"""
Did it work? What an update, a new icon or a new title did to a game's players - measured fairly.

The obvious measure (players 3 days after vs the 3 days before) is wrong three ways:
  1. Day of week.  A Friday update compares Tue-Thu with the next Monday.
  2. Drift.        Most games shrink a little every week anyway (a typical hit halves in ~10 days), so
                   "after vs before" comes out negative on average whether or not anything changed.
  3. The market.   After Halloween everything falls together.
Measured that way the bot once reported "the median update loses 14% of players". That was drift, not updates.

So every change is measured as a matched comparison ("difference in differences"):
  raw    = average players in the 7 days after  /  the 7 days before          (same weekdays on both sides)
  twins  = games of similar size AND similar trend the week before, that did NOT make this kind of change
           within a week either side
  lift   = raw of the game / median raw of its twins - 1                        (what the change added)

A lift of +8% means: this game did 8% better over the following week than similar games that changed nothing.
It is still not proof (studios choose WHEN to update), but drift, weekdays and the market are taken out.

Kinds:
  update   the game was published after at least EFFECT_QUIET_DAYS without a publish (Roblox's "updated" date
           moves on every publish, however small - constant patching can't be measured, a comeback can)
  icon     the icon changed          title    the title changed
"""
import math
import random
from datetime import datetime, timedelta
from statistics import median

import config as C

SCHEMA = """
CREATE TABLE IF NOT EXISTS effects (uid TEXT, day TEXT, kind TEXT, before REAL, raw REAL, twins REAL, lift REAL,
  n_twins INTEGER, PRIMARY KEY (uid, day, kind));
"""
KINDS = {"update": "Updates after a quiet week", "icon": "Icon changes", "title": "Title changes"}


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)


class Panel:
    """Daily players for every game between two dates, loaded once.
    A game's value is its hour-adjusted daily average when every one of its days has 3+ readings, otherwise
    its daily high on every day - never a mix, so a change in how often a game was read can't look like growth."""

    def __init__(self, db, lo, hi):
        raw = {}
        for r in db.execute("SELECT uid, day, peak, sum_ccu, n FROM daily WHERE day>=? AND day<=? AND peak IS NOT NULL", (lo, hi)):
            raw.setdefault(r["uid"], {})[r["day"]] = (r["peak"], r["sum_ccu"], r["n"] or 0)
        self.v = {}
        for uid, ds in raw.items():
            if all(n >= 3 and s for _, s, n in ds.values()):
                self.v[uid] = {d: s / n for d, (_, s, n) in ds.items()}
            else:
                self.v[uid] = {d: float(p) for d, (p, _, _) in ds.items() if p}
        self._weeks = {}

    def _mean(self, ds, start, days=7):
        vals = [ds[d] for d in (_s(start + timedelta(days=i)) for i in range(days)) if d in ds]
        return (sum(vals) / len(vals)) if len(vals) >= C.EFFECT_MIN_DAYS else None

    def weeks(self, day):
        """{uid: (week before, week after, week before that)} around `day`, for every game with enough days."""
        if day not in self._weeks:
            d = _d(day)
            out = {}
            for uid, ds in self.v.items():
                b = self._mean(ds, d - timedelta(days=7))
                a = self._mean(ds, d + timedelta(days=1))
                if b and a:
                    out[uid] = (b, a, self._mean(ds, d - timedelta(days=14)))
            self._weeks[day] = out
            if len(self._weeks) > 40:      # keep memory flat on long catch-ups
                self._weeks.pop(next(iter(self._weeks)))
        return self._weeks[day]


def _near(days, day, span):
    """Did any change in `days` fall within `span` days of `day`?"""
    lo, hi = _s(_d(day) - timedelta(days=span)), _s(_d(day) + timedelta(days=span))
    return any(lo <= x <= hi for x in days)


def measure(panel, uid, day, pool=None, changed=None):
    """{before, raw, twins, lift, n_twins} for one change, or None if the weeks around it aren't complete.
    pool: uids allowed as twins (None = every game); changed: {uid: [days]} of the same kind of change,
    so games that changed around the same time aren't used as "did nothing" twins."""
    wk = panel.weeks(day)
    me = wk.get(uid)
    if not me or me[0] < C.EFFECT_MIN_PLAYERS:
        return None
    before, after, prev = me
    raw = after / before
    trend = math.log(before / prev) if prev else None
    changed = changed or {}
    cand = []
    for v, (b, a, p) in wk.items():
        if v == uid or (pool is not None and v not in pool) or not (0.5 * before <= b <= 2 * before):
            continue
        if v in changed and _near(changed[v], day, 7):
            continue
        cand.append((abs(math.log(b / p) - trend) if (trend is not None and p) else (0.0 if trend is None else None), a / b))
    out = {"before": before, "raw": raw, "twins": None, "lift": None, "n_twins": 0}
    for tol in (C.EFFECT_TREND_TOL, 2 * C.EFFECT_TREND_TOL):
        tw = [r for gap, r in cand if gap is not None and gap <= tol]
        if len(tw) >= C.EFFECT_MIN_TWINS:
            out.update(twins=median(tw), n_twins=len(tw))
            out["lift"] = raw / out["twins"] - 1
            break
    return out


def _median_range(vals, rounds=400, seed=5):
    """90% range for a median, by resampling."""
    if len(vals) < 8:
        return None, None
    rng = random.Random(seed)
    n = len(vals)
    meds = sorted(median(rng.choices(vals, k=n)) for _ in range(rounds))
    return meds[int(0.05 * rounds)], meds[int(0.95 * rounds) - 1]


def summarise(rows):
    """rows: measured changes (dicts with raw/lift). -> {n, raw, twins, lift, lo, hi, up, down, verdict} or None."""
    lifts = [r["lift"] for r in rows if r.get("lift") is not None]
    if len(lifts) < C.EFFECT_MIN_EVENTS:
        return {"n": len(lifts)}
    lo, hi = _median_range(lifts)
    out = {"n": len(lifts), "raw": median(r["raw"] for r in rows if r.get("lift") is not None) - 1,
           "twins": median(r["twins"] for r in rows if r.get("lift") is not None) - 1,
           "lift": median(lifts), "lo": lo, "hi": hi,
           "up": sum(1 for x in lifts if x >= 0.10) / len(lifts), "down": sum(1 for x in lifts if x <= -0.10) / len(lifts)}
    out["verdict"] = ("helps" if lo is not None and lo > 0 else "hurts" if hi is not None and hi < 0 else "no clear effect")
    return out


# ------------------------------------------------------------ the events ---

def publish_events(db, since):
    """Publishes found in the database: Roblox's "updated" date moving to a new day while the bot was watching.
    Returns (events after a quiet spell [(uid, day)], {uid: [all publish days]}, set of uids watched for publishes)."""
    seen = {}
    lo = _s(_d(since) - timedelta(days=C.EFFECT_QUIET_DAYS + 7))
    for r in db.execute("SELECT uid, day, updated FROM daily WHERE updated IS NOT NULL AND updated!='' AND day>=?", (lo,)):
        seen.setdefault(r["uid"], {})[r["day"]] = r["updated"][:10]
    events, allp = [], {}
    for uid, ds in seen.items():
        pubs = sorted(set(ds.values()))
        allp[uid] = pubs
        for i, u in enumerate(pubs):
            if i == 0 or u < since:
                continue          # the first date we ever saw isn't a publish we watched happen
            if (_d(u) - _d(pubs[i - 1])).days < C.EFFECT_QUIET_DAYS:
                continue          # constant patching: no clean "before"
            watched = sum(1 for k in range(1, 8) if _s(_d(u) - timedelta(days=k)) in ds)
            if watched >= 4:      # we were actually watching that quiet week (not a gap in our own tracking)
                events.append((uid, u))
    return events, allp, set(seen)


def update(db, state, today):
    """Measure every change whose week-after is complete and not measured yet. Returns how many were added."""
    ensure(db)
    since = _s(_d(today) - timedelta(days=C.EFFECT_HISTORY_DAYS))
    have = {(r["uid"], r["day"], r["kind"]) for r in db.execute("SELECT uid, day, kind FROM effects")}
    ready = _s(_d(today) - timedelta(days=8))       # the 7 days after must be finished
    jobs = []                                       # (kind, uid, day, pool, changed)
    ev, allp, watched = publish_events(db, since)
    for uid, day in ev:
        if day <= ready and (uid, day, "update") not in have:
            # twins: any similar game not KNOWN to have published that fortnight. (Only ~800 games are watched
            # for publishes; restricting twins to them left most updates with too few to compare against. Some
            # unwatched twins will have updated too, which makes this lift slightly conservative.)
            jobs.append(("update", uid, day, None, allp))
    ch = {"icon": {}, "title": {}}
    for c in state.get("icon_changes") or []:
        if c.get("kind") in ch:
            ch[c["kind"]].setdefault(c["uid"], []).append(c["day"])
    try:
        for r in db.execute("SELECT uid, day FROM renames WHERE day>=?", (since,)):
            ch["title"].setdefault(r["uid"], []).append(r["day"])
    except Exception:
        pass
    icon_pool = set(state.get("icons") or {}) or None
    for kind, pool in (("icon", icon_pool), ("title", None)):
        for uid, days in ch[kind].items():
            for day in set(days):
                if since <= day <= ready and (uid, day, kind) not in have:
                    jobs.append((kind, uid, day, pool, ch[kind]))
    if not jobs:
        return 0
    lo = _s(_d(min(j[2] for j in jobs)) - timedelta(days=15))
    panel = Panel(db, lo, today)
    rows = []
    for kind, uid, day, pool, changed in sorted(jobs, key=lambda j: j[2]):
        m = measure(panel, uid, day, pool, changed)
        if m:
            rows.append((uid, day, kind, m["before"], m["raw"], m["twins"], m["lift"], m["n_twins"]))
        else:
            rows.append((uid, day, kind, None, None, None, None, 0))   # remembered, so it isn't retried every day
    db.executemany("INSERT OR REPLACE INTO effects VALUES(?,?,?,?,?,?,?,?)", rows)
    db.execute("DELETE FROM effects WHERE day < ?", (_s(_d(today) - timedelta(days=C.INSIGHT_KEEP_DAYS)),))
    return len(rows)


def table(db, kind, since=None):
    q = "SELECT e.*, g.name FROM effects e LEFT JOIN games g ON g.uid=e.uid WHERE e.kind=? AND e.lift IS NOT NULL"
    args = [kind]
    if since:
        q += " AND e.day>=?"
        args.append(since)
    return [dict(r) for r in db.execute(q, args)]


def report_lines(db, today):
    """Weekly-report lines: for each kind of change, the typical lift over similar games, with its range."""
    ensure(db)
    out = []
    for kind, label in KINDS.items():
        rows = table(db, kind)
        s = summarise(rows)
        if not s or s.get("lift") is None:
            out.append(f"• {label}: measuring — {s['n'] if s else 0} measured so far (needs {C.EFFECT_MIN_EVENTS})")
            continue
        rng = f" (likely {s['lo'] * 100:+.0f}% to {s['hi'] * 100:+.0f}%)" if s.get("lo") is not None else ""
        icon = {"helps": "✅", "hurts": "🔻", "no clear effect": "▫️"}[s["verdict"]]
        out.append(f"• {icon} **{label}**: typical lift **{s['lift'] * 100:+.0f}%**{rng} vs similar games that changed nothing · "
                   f"{s['up'] * 100:.0f}% beat their twins by 10%+, {s['down'] * 100:.0f}% fell 10%+ behind · {s['n']} measured")
        out.append(f"   ↳ the games themselves went {s['raw'] * 100:+.0f}% week on week while their twins went "
                   f"{s['twins'] * 100:+.0f}% — the naive before/after number is mostly that drift")
        best = sorted(rows, key=lambda r: -r["lift"])[:3]
        if kind == "update" and best and best[0]["lift"] >= 0.25:
            out.append("   ↳ biggest: " + ", ".join(f"{(r['name'] or r['uid'])[:26]} ({r['lift'] * 100:+.0f}%)" for r in best
                                                    if r["lift"] >= 0.25))
    out.append("_Lift = the game's week-on-week change divided by the median change of similar-size, similar-trend games "
               "that made no such change. Correlation still, but weekdays, natural decay and market swings are removed._")
    return out

"""
Weekday hold and LONG-TERM GAMES.

Weekly, for every game with enough players:
  hold       = average players Mon-Wed  /  average players on its two busiest days of Fri-Sun before
  benchmark  = the median hold of all rated games that week (the "typical" weekday dip)
  relative   = hold / benchmark     -> above 1.0 = keeps its crowd better than a typical game

Why "two busiest of Fri-Sun" and not simply Sat+Sun: the weekend isn't Saturday-Sunday everywhere. For a
game with a Middle-Eastern audience Friday-Saturday is the weekend and Sunday is a school day, so judging
it against Sat+Sun made it look like a habit game when it was just in another timezone's week.

Long-term game = a game whose relative hold is RELIABLY above typical: its average over the rated weeks
is above 1.0 by more than week-to-week noise can explain (95% one-sided, using the noise level measured
across all games), with at least LONGTERM_MIN_WEEKS weeks. The old rule ("above typical in 75% of weeks,
2+ weeks") was passed by about one game in five by luck alone, which is why genre shares jumped around
from week to week. By luck alone about 5% of games pass the new rule.

Judged against the median game (not Roblox's total) so past weeks rebuilt from
downloaded history are measured exactly like live weeks. Roblox's own dip is still
recorded and shown for context.

Left out, because the ratio would lie:
  growing   weekdays 1.5x+ the previous week's weekdays (measures growth, not loyalty)
  new       under 14 days old with no previous week
  spike     busiest day > 1.8x the second busiest (an event): only the second busiest counts as the weekend
"""
import math
from datetime import datetime, timedelta
from statistics import median

import config as C

SCHEMA = """
CREATE TABLE IF NOT EXISTS hold_weekly (uid TEXT, week TEXT, hold REAL, rel REAL, flag TEXT,
  weekend INTEGER, weekday INTEGER, PRIMARY KEY (uid, week));
CREATE INDEX IF NOT EXISTS hold_weekly_week ON hold_weekly(week);
"""


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)


# ------------------------------------------------------------ platform ---

def record_platform(state, data):
    """Merge RoWatcher /platform/ccu samples (last 24h) into per-day sum/count/max."""
    plat = state.setdefault("platform", {})
    last = plat.get("_last", "")
    newest = last
    for x in (data or {}).get("history") or []:
        ts = x.get("recordedAt") or x.get("time") or ""
        v = x.get("totalCCU") or x.get("value") or 0
        if not ts or ts <= last or not v:
            continue
        d = plat.setdefault(ts[:10], {"sum": 0, "n": 0, "max": 0})
        d["sum"] += v
        d["n"] += 1
        d["max"] = max(d["max"], v)
        newest = max(newest, ts)
    plat["_last"] = newest
    keep = _s(datetime.utcnow() - timedelta(days=21))
    for k in [k for k in plat if not k.startswith("_") and k < keep]:
        del plat[k]


def _roblox_hold(state, wkend, wkday):
    p = state.get("platform") or {}
    vals = [p.get(d) for d in wkend + wkday]
    if not all(v and v["n"] >= 100 for v in vals):
        return None
    avg = [v["sum"] / v["n"] for v in vals]
    return (sum(avg[2:]) / 2) / (sum(avg[:2]) / 2)


# --------------------------------------------------------------- weeks ---

def week_of(wed):
    """Weekend (Sat, Sun) and weekdays (Tue, Wed) for the week whose Wednesday is `wed`."""
    w = _d(wed)
    return [_s(w - timedelta(days=4)), _s(w - timedelta(days=3))], [_s(w - timedelta(days=1)), wed]


def latest_wed(today):
    y = _d(today) - timedelta(days=1)
    while y.weekday() != 2:
        y -= timedelta(days=1)
    return _s(y)


def compute_week(db, wed, created, robust=None):
    """{uid: {hold, rel, flag, weekend, weekday}}, benchmark — for the week whose Wednesday is `wed`.
    robust=True: Mon-Wed vs the two busiest of Fri-Sun (see module docstring); False: Tue-Wed vs Sat-Sun."""
    robust = C.HOLD_ROBUST if robust is None else robust
    w = _d(wed)
    fri, sat, sun, mon, tue = (_s(w - timedelta(days=k)) for k in (5, 4, 3, 2, 1))
    need = [sat, sun, tue, wed]                      # always required
    wkend_days = [fri, sat, sun] if robust else [sat, sun]
    wkday_days = [mon, tue, wed] if robust else [tue, wed]
    prev = [_s(_d(d) - timedelta(days=7)) for d in wkday_days]
    days = sorted(set(wkend_days + wkday_days + prev))
    rows = {}
    for r in db.execute(f"SELECT uid, day, peak, sum_ccu, n FROM daily WHERE day IN ({','.join('?' * len(days))}) "
                        "AND peak IS NOT NULL", days):
        rows.setdefault(r["uid"], {})[r["day"]] = (r["peak"], (r["sum_ccu"] / r["n"]) if r["n"] else None, r["n"] or 0)
    out = {}
    for uid, ds in rows.items():
        if not all(d in ds for d in need):
            continue
        used = [d for d in wkend_days + wkday_days + prev if d in ds]
        use_avg = all(ds[d][2] >= 2 and ds[d][1] for d in used)
        val = (lambda d: ds[d][1]) if use_avg else (lambda d: ds[d][0])
        we = sorted((val(d) for d in wkend_days if d in ds), reverse=True)
        if we[0] < C.HOLD_MIN_PLAYERS:
            continue
        flag, weekend = "ok", (we[0] + we[1]) / 2
        if we[0] > C.HOLD_SPIKE_RATIO * we[1]:
            weekend, flag = we[1], "spike"
        wd = [val(d) for d in wkday_days if d in ds]
        weekday = sum(wd) / len(wd)
        pv = [val(d) for d in prev if d in ds]
        c = created.get(uid)
        if len(pv) >= 2 and weekday >= C.HOLD_GROWING_RATIO * (sum(pv) / len(pv)):
            flag = "growing"
        elif len(pv) < 2 and c and (_d(wed) - _d(c)).days < 14:
            flag = "new"
        if weekend:
            out[uid] = {"hold": weekday / weekend, "flag": flag, "weekend": weekend, "weekday": weekday}
    judged = [h["hold"] for h in out.values() if h["flag"] in ("ok", "spike")]
    bench = median(judged) if len(judged) >= C.HOLD_MIN_BENCHMARK_GAMES else None
    for h in out.values():
        h["rel"] = (h["hold"] / bench) if (bench and h["flag"] in ("ok", "spike")) else None
    return out, bench


def update(db, state, today):
    """Rebuild the last HOLD_HISTORY_WEEKS weeks, refresh state['hold'] (latest week) and the long-term list."""
    ensure(db)
    created = {r["uid"]: r["created"] for r in db.execute("SELECT uid, created FROM games")}
    wed = latest_wed(today)
    weeks, benches = [], {}
    for i in range(C.HOLD_HISTORY_WEEKS):
        w = _s(_d(wed) - timedelta(days=7 * i))
        res, bench = compute_week(db, w, created)
        if not res:
            continue
        benches[w] = bench
        db.executemany("INSERT OR REPLACE INTO hold_weekly VALUES(?,?,?,?,?,?,?)",
                       [(u, w, round(h["hold"], 4), round(h["rel"], 4) if h["rel"] else None, h["flag"],
                         int(h["weekend"]), int(h["weekday"])) for u, h in res.items()])
        weeks.append(w)
        if i == 0:
            state["hold"] = {u: {"hold": round(h["hold"], 3), "rel": round(h["rel"], 3) if h["rel"] else None,
                                 "flag": h["flag"], "week": w} for u, h in res.items()}
    wkend, wkday = week_of(wed)
    state["hold_meta"] = {"week": wed, "weekend": wkend, "weekday": wkday,
                          "benchmark": round(benches[wed], 3) if benches.get(wed) else None,
                          "roblox": round(_roblox_hold(state, wkend, wkday), 3) if _roblox_hold(state, wkend, wkday) else None,
                          "weeks": len(weeks)}
    state["longterm"] = classify(db, today)
    state["hold_meta"].update(noise_stats(db, today))
    return state["hold_meta"]


# ----------------------------------------------------------- long term ---

def _log_rels(db, today):
    """{uid: [(week, log relative hold, weekend players)]} over the long-term window."""
    since = _s(_d(latest_wed(today)) - timedelta(days=7 * (C.LONGTERM_WINDOW_WEEKS - 1)))
    by = {}
    for r in db.execute("SELECT uid, week, rel, weekend FROM hold_weekly WHERE week>=? AND rel IS NOT NULL AND rel>0", (since,)):
        by.setdefault(r["uid"], []).append((r["week"], math.log(r["rel"]), r["weekend"]))
    return by


def _variances(by):
    """(week-to-week noise variance within a game, real variance between games) of log relative hold."""
    ss, dof, means, inv_n = 0.0, 0, [], []
    for ws in by.values():
        xs = [x for _, x, _ in ws]
        m = sum(xs) / len(xs)
        means.append(m)
        inv_n.append(1 / len(xs))
        if len(xs) >= 2:
            ss += sum((x - m) ** 2 for x in xs)
            dof += len(xs) - 1
    if dof < 30 or len(means) < 30:
        return None, None
    within = ss / dof
    gm = sum(means) / len(means)
    total = sum((m - gm) ** 2 for m in means) / (len(means) - 1)
    between = max(0.0, total - within * (sum(inv_n) / len(inv_n)))
    return within, between


def noise_stats(db, today):
    """How much of one week's relative hold is the game and how much is noise (0-1; 1 = perfectly repeatable)."""
    within, between = _variances(_log_rels(db, today))
    if within is None or (within + between) <= 0:
        return {"reliability": None}
    return {"reliability": round(between / (between + within), 3), "noise_sd": round(math.sqrt(within), 3)}


def classify(db, today):
    """{uid: {"status": "long-term"|"promising", "weeks": n, "good": k, "med": typical rel, "z": evidence}}

    long-term: the game's average log relative hold is above 0 (= typical) by more than LONGTERM_Z standard
    errors, where the standard error uses the week-to-week noise measured across ALL games (a game's own
    2-4 weeks are too few to estimate its noise). "med" is the average pulled towards 1.0 by how little
    data there is (shrinkage), so a 2-week wonder doesn't top the list."""
    by = _log_rels(db, today)
    within, between = _variances(by)
    out = {}
    for uid, ws in by.items():
        xs = [x for _, x, _ in ws]
        n = len(xs)
        m = sum(xs) / n
        good = sum(1 for x in xs if x >= 0)
        players = max(w for _, _, w in ws)
        if within is None:      # not enough games yet to measure the noise: fall back to the simple rule
            z, est = None, m
            is_lt = n >= max(3, C.LONGTERM_MIN_WEEKS) and good == n and m >= math.log(1.05)
        else:
            se = math.sqrt(within / n)
            z = m / se if se else 0.0
            shrink = between / (between + within / n) if (between + within / n) > 0 else 0.0
            est = m * shrink
            is_lt = n >= C.LONGTERM_MIN_WEEKS and z >= C.LONGTERM_Z
        if is_lt:
            out[uid] = {"status": "long-term", "weeks": n, "good": good, "med": round(math.exp(est), 3), "players": players,
                        "z": round(z, 2) if z is not None else None}
        elif math.exp(m) >= C.LONGTERM_PROMISING_REL:
            out[uid] = {"status": "promising", "weeks": n, "good": good, "med": round(math.exp(m), 3), "players": players,
                        "z": round(z, 2) if z is not None else None}
    return out


def _wilson(k, n, z=1.645):
    """90% range for a share k/n (Wilson score interval)."""
    if not n:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def genre_table(db, state):
    """Per genre: games rated, median relative hold, long-term count, best long-term games."""
    lt = state.get("longterm") or {}
    hold = state.get("hold") or {}
    meta = {r["uid"]: (r["genre"] or "Unknown", r["name"] or r["uid"]) for r in db.execute("SELECT uid, genre, name FROM games")}
    since = _s(_d(state.get("hold_meta", {}).get("week", "2000-01-01")) - timedelta(days=7 * (C.LONGTERM_WINDOW_WEEKS - 1)))
    rels = {}
    for r in db.execute("SELECT uid, rel FROM hold_weekly WHERE week>=? AND rel IS NOT NULL", (since,)):
        rels.setdefault(r["uid"], []).append(r["rel"])
    by = {}
    for uid, rs in rels.items():
        if len(rs) < C.LONGTERM_MIN_WEEKS:
            continue        # too few weeks to judge: counting them diluted every genre's share
        g = meta.get(uid, ("Unknown", uid))[0]
        x = by.setdefault(g, {"games": 0, "rels": [], "lt": [], "promising": 0})
        x["games"] += 1
        x["rels"].append(median(rs))
        s = (lt.get(uid) or {}).get("status")
        if s == "long-term":
            x["lt"].append((lt[uid]["players"], meta.get(uid, ("", uid))[1], uid, lt[uid]["med"]))
        elif s == "promising":
            x["promising"] += 1
    rows = []
    tot_g = sum(x["games"] for x in by.values())
    tot_lt = sum(len(x["lt"]) for x in by.values())
    overall = (tot_lt / tot_g) if tot_g else 0.0
    for g, x in by.items():
        if x["games"] < C.GENRE_MIN_GAMES:
            continue
        x["lt"].sort(reverse=True)
        lo, hi = _wilson(len(x["lt"]), x["games"])
        rows.append({"genre": g, "games": x["games"], "median": median(x["rels"]), "lt": len(x["lt"]),
                     "share": len(x["lt"]) / x["games"], "lo": lo, "hi": hi, "overall": overall,
                     "evidence": "above" if lo > overall else ("below" if hi < overall else "unclear"),
                     "promising": x["promising"], "top": x["lt"][:3]})
    rows.sort(key=lambda r: (-r["lo"], -r["median"]))
    return rows


def heat_points(state, gid):
    """(points to add to heat, relative hold or None). Long-term status adds a little extra."""
    h = (state.get("hold") or {}).get(gid)
    rel = (h or {}).get("rel")
    pts = max(-10.0, min(10.0, (rel - 0.95) * 40)) if rel is not None else 0.0
    if ((state.get("longterm") or {}).get(gid) or {}).get("status") == "long-term":
        pts += 5
    return pts, rel


# ------------------------------------------------------------- output ---

def digest_lines(state, fmt, name_of, young_ids, link):
    meta = state.get("hold_meta") or {}
    hold = state.get("hold") or {}
    if not hold or not meta.get("benchmark"):
        return []
    sat = _d(meta["weekend"][0]).strftime("%a %d %b")
    rob = f"; Roblox overall kept {meta['roblox']*100:.0f}%" if meta.get("roblox") else ""
    lines = [f"🔁 **Weekday hold** (Mon–Wed vs its two busiest days of the weekend of {sat}; a typical game kept "
             f"**{meta['benchmark']*100:.0f}%**{rob})"]
    rated = sorted(((h["rel"], uid, h) for uid, h in hold.items() if h.get("rel") and uid in young_ids), reverse=True)
    if rated:
        lines.append("Young games holding best (habit, not hype):")
        for rel, uid, h in rated[:5]:
            lines.append(f"• {name_of(uid)[:38]} — kept {h['hold']*100:.0f}% (**{rel:.2f}×** typical) {link(uid)}")
        worst = [x for x in rated[-3:] if x[0] < 0.8 and x not in rated[:5]]
        if worst:
            lines.append("Weekend-only crowds (likely to fade):")
            for rel, uid, h in sorted(worst):
                lines.append(f"• {name_of(uid)[:38]} — kept {h['hold']*100:.0f}% ({rel:.2f}× typical)")
    return lines


def report_lines(db, state, fmt, name_of, link):
    lt = state.get("longterm") or {}
    meta = state.get("hold_meta") or {}
    rel = meta.get("reliability")
    lines = [f"🏛️ **Long-term games** (weekday hold reliably above a typical game's over {C.LONGTERM_MIN_WEEKS}+ weeks; "
             f"{meta.get('weeks', 0)} weeks of data so far)"]
    if rel is not None:
        lines.append(f"• How repeatable is weekday hold? **{rel * 100:.0f}%** of the difference between games in one week is "
                     f"the game itself; the rest is week-to-week noise. That's why one good week proves little.")
    rows = genre_table(db, state)
    if rows:
        ov = rows[0]["overall"]
        lines.append(f"By genre (share of rated games that are long-term; all genres together: {ov * 100:.0f}%, "
                     f"and ~5% would pass by luck):")
        for r in rows[:12]:
            tops = ", ".join(n[:22] for _, n, _, _ in r["top"]) or "—"
            tag = {"above": " · ✅ reliably above average", "below": " · 🔻 reliably below average", "unclear": ""}[r["evidence"]]
            lines.append(f"• **{r['genre']}** — {r['lt']}/{r['games']} long-term ({r['share']*100:.0f}%, likely "
                         f"{r['lo']*100:.0f}–{r['hi']*100:.0f}%){tag} · median {r['median']:.2f}× · e.g. {tops}")
        if not any(r["evidence"] != "unclear" for r in rows):
            lines.append("_No genre is reliably different from the average yet — treat the order above as noise._")
    else:
        lines.append("• Building up — needs a few weeks of weekday-hold data.")
    young = sorted(((v.get("z") or 0, uid, v) for uid, v in lt.items() if v["status"] == "long-term"
                    and uid in (state.get("_young_ids") or set())), reverse=True)
    if young:
        lines += ["", "🌱🏛️ **Young games that are already long-term** (the ones to study):"]
        for _, uid, v in young[:6]:
            lines.append(f"• {name_of(uid)[:38]} — {v['med']:.2f}× typical over {v['weeks']} weeks "
                         f"({v['good']}/{v['weeks']} above) · {fmt(v['players'])} weekend players {link(uid)}")
    prom = sorted(((v["med"], uid, v) for uid, v in lt.items() if v["status"] == "promising"
                   and uid in (state.get("_young_ids") or set())), reverse=True)
    if prom:
        lines.append("Promising (strong so far, too few weeks to be sure): "
                     + ", ".join(f"{name_of(u)[:24]} ({v['med']:.2f}×, {v['weeks']}wk)" for _, u, v in prom[:6]))
    return lines


def newly_longterm(state, before):
    """uids that became long-term since the previous classification."""
    now = state.get("longterm") or {}
    return [u for u, v in now.items() if v["status"] == "long-term" and (before.get(u) or {}).get("status") != "long-term"]

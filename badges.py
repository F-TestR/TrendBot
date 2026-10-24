"""
Badges: the closest thing to a game's private analytics that Roblox makes public.

For every badge Roblox publishes:
  awardedCount          players who have EVER earned it
  pastDayAwardedCount   players who earned it for the first time in the last day
  winRatePercentage     that past-day count / players who played the game that day  (a fraction, 0-1)

Checked live on Illegal Soccer, Natural Disaster Survival, Grow a Garden and Twisted:
every badge in a game gives the same  past-day count / win rate  (to within rounding).
So for any game with a badge earned by at least ~1% of players:

  DAU (players per day)        = past-day count / win rate
  playtime per player per day  = average players online x 1,440 / DAU     <- Roblox's #1 ranking signal
  sessions per player per day  = visits that day / DAU
  session length               = playtime per player / sessions per player

And when the game has a "welcome / you played" badge (awarded on first join):
  new players per day          = its past-day count
  new-player share             = its win rate          -> returning share = 1 - win rate
  lifetime playtime per player = minutes played per day / new players per day   (steady state)
  funnels                      = other badges' past-day count / new players per day
                                 e.g. "7-day streak": share of new players who ever hit a 7-day streak
                                      "Drive 1,000 miles": share who ever get that far

Benchmarks (GameAnalytics 2026, games with 1M+ monthly players): median game session 9.8 min
(top 5% 16.6, top 1% 21.1); median game 1.56 opens per player per day (top 10% 3.22, top 1% 8.3);
median player 22.4 min/day across all of Roblox.

Caveats: funnels assume steady state (a fast-growing game looks worse, a shrinking one better);
badge names are written by developers, so only parseable ones are used.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from statistics import median

import config as C

UA = {"User-Agent": "roblox-trend-bot/1.6", "Accept": "application/json"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS badge_daily (uid TEXT, badge_id TEXT, day TEXT, name TEXT, awarded INTEGER,
  past_day INTEGER, win_rate REAL, PRIMARY KEY (uid, badge_id, day));
CREATE TABLE IF NOT EXISTS badge_metrics (uid TEXT, day TEXT, dau INTEGER, avg_ccu REAL, visits_day INTEGER,
  minutes_per_dau REAL, sessions_per_dau REAL, new_per_day INTEGER, new_share REAL, unique_players INTEGER,
  lifetime_min REAL, welcome TEXT, first_step TEXT, first_step_share REAL, streaks TEXT, ladder TEXT,
  playtime_reach TEXT, n_badges INTEGER, base TEXT, PRIMARY KEY (uid, day));
CREATE INDEX IF NOT EXISTS badge_metrics_day ON badge_metrics(day);
"""

WELCOME = re.compile(r"\b(welcome|you joined|joined|first join|join(ed)? the game|first time|thanks for playing|"
                     r"thank you for playing|you played|played the game|you came|for playing|visited|visit the game|"
                     r"entered the game|beginner|newcomer|hello)\b", re.I)
NOT_WELCOME = re.compile(r"\b(\d+\s*(days?|hours?|minutes?|times|visits)|streak|again)\b", re.I)
MINUTES = re.compile(r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?|hr|h|m)\b", re.I)
PLAY_CONTEXT = re.compile(r"\b(play|played|playing|playtime|play time|spend|spent|stay|stayed|online|session)\b", re.I)
DAYS = re.compile(r"(\d+)\s*-?\s*(?:days?|day streak|logins?)\b|\bday\s*(\d+)\b", re.I)
RETURN_CONTEXT = re.compile(r"\b(day|days|login|logins|log in|return|returned|come back|came back|streak|daily)\b", re.I)
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?(?:\s*[kKmM]\b)?")


def log(m):
    print(m, file=sys.stderr)


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


class RateLimited(Exception):
    pass


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited("Roblox badges: rate limited")
        raise


def ensure(db):
    db.executescript(SCHEMA)


def fetch_badges(uid):
    out, cursor = [], ""
    for _ in range(C.BADGE_MAX_PAGES):
        q = {"limit": 100, "sortOrder": "Asc"}
        if cursor:
            q["cursor"] = cursor
        d = get_json(f"https://badges.roblox.com/v1/universes/{uid}/badges?" + urllib.parse.urlencode(q))
        out += d.get("data") or []
        cursor = d.get("nextPageCursor")
        if not cursor:
            break
        time.sleep(0.3)
    return out


def normalise(raw):
    rows = []
    for b in raw or []:
        st = b.get("statistics") or {}
        if b.get("enabled") is False:
            continue
        wr = st.get("winRatePercentage")
        rows.append({"id": str(b.get("id")), "name": (b.get("name") or "").strip()[:100],
                     "description": (b.get("description") or "").strip()[:300],
                     "awarded": int(st.get("awardedCount") or 0), "past_day": int(st.get("pastDayAwardedCount") or 0),
                     "win_rate": float(wr) if wr is not None else None})
    if rows and max((r["win_rate"] or 0) for r in rows) > 1.0:  # in case Roblox ever switches to real percentages
        for r in rows:
            if r["win_rate"] is not None:
                r["win_rate"] /= 100
    return rows


# ---------------------------------------------------------------- parsing ---

def _num(txt):
    t = txt.replace(",", "").strip().lower()
    mult = 1000 if t.endswith("k") else (1_000_000 if t.endswith("m") else 1)
    try:
        return float(t.rstrip("km").strip()) * mult
    except ValueError:
        return None


def minutes_of(text):
    if not PLAY_CONTEXT.search(text):
        return None
    m = MINUTES.search(text)
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2).lower()
    mins = n * 60 if unit.startswith("h") else n
    return mins if 1 <= mins <= 1000 * 60 else None


def days_of(text):
    if not RETURN_CONTEXT.search(text) or minutes_of(text):
        return None
    m = DAYS.search(text)
    if not m:
        return None
    n = int(m.group(1) or m.group(2))
    return n if 2 <= n <= 365 else None


def template(name):
    """'Drive 1,000 Miles' -> ('drive # miles', 1000). None if no number."""
    m = NUM.search(name)
    if not m:
        return None, None
    v = _num(m.group(0))
    if v is None or v <= 0:
        return None, None
    return NUM.sub("#", name.lower(), count=1).strip(), v


def estimate_dau(rows):
    """Median of past-day / win rate over the badges with the most precise win rates."""
    est = sorted(((r["win_rate"], r["past_day"] / r["win_rate"]) for r in rows
                  if r["win_rate"] and r["win_rate"] >= C.BADGE_MIN_WIN_RATE and r["past_day"] >= 20), reverse=True)[:5]
    if not est:
        return None, None
    vals = [e for _, e in est]
    dau = median(vals)
    spread = (max(vals) - min(vals)) / dau if len(vals) > 1 and dau else 0.0
    return dau, spread


def find_welcome(rows):
    cands = [r for r in rows if WELCOME.search(f"{r['name']} {r['description']}")
             and not NOT_WELCOME.search(r["name"]) and r["win_rate"]]
    if not cands:
        return None
    w = max(cands, key=lambda r: r["past_day"])
    top = max(r["past_day"] for r in rows)
    # a real join badge is (nearly) the most-earned badge of the day
    return w if w["past_day"] >= 0.8 * top else None


def metrics_from(rows, avg_ccu, visits_day):
    """rows: normalised badges. Returns a metrics dict or None."""
    if not rows:
        return None
    dau, spread = estimate_dau(rows)
    if not dau:
        return None
    m = {"dau": int(dau), "spread": spread, "avg_ccu": avg_ccu, "visits_day": visits_day, "n_badges": len(rows),
         "minutes_per_dau": None, "sessions_per_dau": None, "new_per_day": None, "new_share": None,
         "unique_players": None, "lifetime_min": None, "welcome": None, "first_step": None, "first_step_share": None,
         "streaks": [], "ladder": None, "playtime_reach": [], "base": None}
    if avg_ccu:
        mp = avg_ccu * 1440 / dau
        m["minutes_per_dau"] = mp if 0.5 <= mp <= 600 else None
    if visits_day and visits_day > 0:
        sp = visits_day / dau
        m["sessions_per_dau"] = sp if 0.5 <= sp <= 50 else None
    w = find_welcome(rows)
    base = None
    if w:
        base = w["past_day"]
        m.update(welcome=w["name"], new_per_day=w["past_day"], new_share=w["win_rate"], unique_players=w["awarded"])
        if avg_ccu and base:
            m["lifetime_min"] = avg_ccu * 1440 / base
        m["base"] = "new players"
    else:
        # no join badge: measure funnels against the game's most-earned first-step badge instead
        big = max(r["awarded"] for r in rows)  # skip brand-new event badges: the base must be an old, common badge
        top = max((r for r in rows if r["past_day"] > 0 and r["awarded"] >= 0.3 * big), key=lambda r: r["past_day"], default=None)
        if top:
            w, base = top, top["past_day"]
            m["base"] = f"players who earn \"{top['name'][:30]}\""
    others = [r for r in rows if r is not w and r["past_day"] > 0]
    if base and others and m["welcome"]:
        fs = max(others, key=lambda r: r["past_day"])
        m["first_step"], m["first_step_share"] = fs["name"], min(1.0, fs["past_day"] / base)
    for r in rows:
        if r is w:
            continue
        text = f"{r['name']} {r['description']}"
        mins = minutes_of(text)
        if mins:
            m["playtime_reach"].append((mins, r["win_rate"] or 0, (r["past_day"] / base) if base else None, r["name"]))
            continue
        days = days_of(text)
        if days:
            m["streaks"].append((days, r["win_rate"] or 0, (r["past_day"] / base) if base else None, r["name"]))
    m["playtime_reach"].sort()
    m["streaks"].sort()
    # the game's main numbered ladder ("Drive # Miles", "Level #", "Survived # Disasters"...)
    groups = {}
    for r in rows:
        if r is w:
            continue
        tpl, v = template(r["name"])
        if tpl:
            groups.setdefault(tpl, []).append((v, r["past_day"], r["name"]))
    best = max((g for g in groups.values() if len(g) >= 3), key=lambda g: sum(p for _, p, _ in g), default=None)
    if best and base:
        best.sort()
        m["ladder"] = [(nm, min(1.0, p / base)) for _, p, nm in best]
    return m


# ---------------------------------------------------------------- collect ---

def candidates(state, today):
    pri = {}
    for gid in C.WATCHLIST:
        pri[str(gid)] = 1e12
    young = state.get("_young_ids") or set()
    for gid, r in state["games"].items():
        if r.get("last_seen") != today:
            continue
        p = r.get("last", 0)
        if p < C.BADGE_MIN_PLAYERS and str(gid) not in pri:
            continue
        pri[str(gid)] = max(pri.get(str(gid), 0), p * (3 if gid in young else 1))
    for gid in (state.get("hold") or {}):
        pri[str(gid)] = max(pri.get(str(gid), 0), 1)
    done = state.get("badges_at") or {}
    due = [g for g, _ in sorted(pri.items(), key=lambda kv: -kv[1]) if done.get(g) != today and g.isdigit()]
    return due[:C.BADGE_GAMES_PER_DAY - sum(1 for d in done.values() if d == today)]


def _ccu_visits(db, uid, t):
    """Yesterday's average players online and visits gained that day."""
    yday, d2 = _s(t - timedelta(days=1)), _s(t - timedelta(days=2))
    rows = {r["day"]: r for r in db.execute("SELECT day, peak, low, sum_ccu, n, visits FROM daily WHERE uid=? AND day IN (?, ?)",
                                            (uid, yday, d2))}
    y = rows.get(yday)
    avg = None
    if y and y["n"] and y["n"] >= 3:
        avg = y["sum_ccu"] / y["n"]
    elif y and y["peak"]:
        avg = ((y["peak"] or 0) + (y["low"] or y["peak"] or 0)) / 2 * 0.9
    vis = None
    if y and rows.get(d2) and y["visits"] and rows[d2]["visits"] and y["visits"] > rows[d2]["visits"]:
        vis = y["visits"] - rows[d2]["visits"]
    return avg, vis


def collect(db, state, t):
    ensure(db)
    today = _s(t)
    done = state.setdefault("badges_at", {})
    bstate = state.setdefault("badges", {})
    n = 0
    for uid in candidates(state, today)[:C.BADGE_GAMES_PER_RUN]:
        try:
            rows = normalise(fetch_badges(uid))
        except RateLimited as e:
            log(str(e))
            break
        except Exception as e:
            log(f"badges failed for {uid}: {e}")
            done[uid] = today
            continue
        done[uid] = today
        n += 1
        if rows:
            db.executemany("INSERT OR REPLACE INTO badge_daily VALUES(?,?,?,?,?,?,?)",
                           [(uid, r["id"], today, r["name"], r["awarded"], r["past_day"], r["win_rate"]) for r in rows])
        avg, vis = _ccu_visits(db, uid, t)
        m = metrics_from(rows, avg, vis)
        if not m:
            bstate.pop(uid, None)
            continue
        db.execute("INSERT OR REPLACE INTO badge_metrics VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (uid, today, m["dau"], m["avg_ccu"], m["visits_day"], m["minutes_per_dau"], m["sessions_per_dau"],
                    m["new_per_day"], m["new_share"], m["unique_players"], m["lifetime_min"], m["welcome"],
                    m["first_step"], m["first_step_share"], json.dumps(m["streaks"]), json.dumps(m["ladder"]),
                    json.dumps(m["playtime_reach"]), m["n_badges"], m["base"]))
        streak7 = next((s for s in m["streaks"] if 5 <= s[0] <= 10 and s[2] is not None), None)
        bstate[uid] = {"day": today, "dau": m["dau"], "playtime": round(m["minutes_per_dau"], 1) if m["minutes_per_dau"] else None,
                       "sessions": round(m["sessions_per_dau"], 2) if m["sessions_per_dau"] else None,
                       "returning": round(1 - m["new_share"], 3) if m["new_share"] is not None else None,
                       "new": m["new_per_day"], "lifetime": round(m["lifetime_min"]) if m["lifetime_min"] else None,
                       "first_step": round(m["first_step_share"], 3) if m["first_step_share"] is not None else None,
                       "streak7": (streak7[0], round(streak7[2], 4)) if streak7 else None,
                       "base": m["base"]}
        time.sleep(C.BADGE_PAUSE_SECONDS)
    cut = _s(t - timedelta(days=4))
    for k in [k for k, d in done.items() if d < cut]:
        del done[k]
    for k in [k for k, v in bstate.items() if v.get("day", "") < _s(t - timedelta(days=14))]:
        del bstate[k]
    db.execute("DELETE FROM badge_daily WHERE day < ?", (_s(t - timedelta(days=C.BADGE_KEEP_DAYS)),))
    db.execute("DELETE FROM badge_metrics WHERE day < ?", (_s(t - timedelta(days=C.THEME_KEEP_DAYS)),))
    return n


# ---------------------------------------------------------------- weekly ---

def week_medians(db, wed):
    """uid -> {'playtime': median minutes per player per day, 'returning': median returning share} for the week."""
    lo, hi = _s(_d(wed) - timedelta(days=6)), _s(_d(wed) + timedelta(days=3))  # badges change slowly: allow a few days after
    by = {}
    for r in db.execute("SELECT uid, minutes_per_dau, new_share FROM badge_metrics WHERE day>=? AND day<=?", (lo, hi)):
        x = by.setdefault(r["uid"], {"p": [], "r": []})
        if r["minutes_per_dau"] is not None:
            x["p"].append(r["minutes_per_dau"])
        if r["new_share"] is not None:
            x["r"].append(1 - r["new_share"])
    return {u: {"playtime": median(x["p"]) if x["p"] else None, "returning": median(x["r"]) if x["r"] else None}
            for u, x in by.items()}


def heat_points(state, gid):
    b = (state.get("badges") or {}).get(gid) or {}
    pt = b.get("playtime")
    if not pt:
        return 0.0, None
    allp = sorted(v["playtime"] for v in (state.get("badges") or {}).values() if v.get("playtime"))
    med = allp[len(allp) // 2] if len(allp) >= 10 else C.BADGE_PLAYTIME_REFERENCE
    import math
    return max(-4.0, min(6.0, 4 * math.log2(pt / med))), pt


# ---------------------------------------------------------------- reports ---

def _pct(x, digits=0):
    return f"{x * 100:.{digits}f}%"


def funnel_lines(db, uid, name_of):
    r = db.execute("SELECT * FROM badge_metrics WHERE uid=? ORDER BY day DESC LIMIT 1", (uid,)).fetchone()
    if not r:
        return []
    bits = [f"**{name_of(uid)[:40]}** — {r['dau']:,} players/day"]
    if r["minutes_per_dau"]:
        bits.append(f"~{r['minutes_per_dau']:.0f} min each per day")
    if r["sessions_per_dau"]:
        bits.append(f"{r['sessions_per_dau']:.1f} sessions each")
    if r["new_share"] is not None:
        bits.append(f"{_pct(1 - r['new_share'])} returning")
    out = ["• " + " · ".join(bits)]
    steps = []
    if r["first_step"] and r["first_step_share"] is not None:
        steps.append(f"{_pct(r['first_step_share'])} get \"{r['first_step'][:28]}\"")
    for days, _, share, nm in json.loads(r["streaks"] or "[]"):
        if share is not None and days in (3, 5, 7, 14, 30):
            steps.append(f"{_pct(share, 1)} hit a {days}-day streak")
    lad = json.loads(r["ladder"] or "null")
    if lad:
        steps.append("ladder: " + " → ".join(f"{nm[:22]} {_pct(s, 1)}" for nm, s in lad[:5]))
    if steps:
        out.append(f"  Of {r['base'] or 'new players'}: " + " · ".join(steps))
    return out


def report_lines(db, state, fmt, name_of, link):
    b = state.get("badges") or {}
    lines = ["🏅 **Badges: real players per day, playtime and funnels** (from Roblox's public badge stats)"]
    if not b:
        return lines + ["• Collecting — badges are read for the top tracked games each day."]
    pts = [v["playtime"] for v in b.values() if v.get("playtime")]
    ses = [v["sessions"] for v in b.values() if v.get("sessions")]
    ret = [v["returning"] for v in b.values() if v.get("returning") is not None]
    summ = [f"{len(b)} games measured"]
    if pts:
        summ.append(f"median **{median(pts):.0f} min** played per player per day")
    if ses:
        summ.append(f"{median(ses):.1f} sessions each (GameAnalytics median 1.56, top 10% 3.22)")
    if ret:
        summ.append(f"{_pct(median(ret))} of daily players are returning")
    lines.append("• " + " · ".join(summ))
    young = state.get("_young_ids") or set()
    top = sorted(((v["playtime"], u, v) for u, v in b.items() if v.get("playtime") and u in young and (v.get("dau") or 0) >= 2000),
                 reverse=True)[:6]
    if top:
        lines.append("Young games with the most playtime per player (Roblox's top ranking signal):")
        for pt, u, v in top:
            extra = f", {_pct(v['returning'])} returning" if v.get("returning") is not None else ""
            lines.append(f"• {name_of(u)[:36]} — **{pt:.0f} min/day** · {fmt(v['dau'])} players/day{extra} {link(u)}")
    st = sorted(((v["streak7"][1], u, v) for u, v in b.items() if v.get("streak7") and v.get("base") == "new players"),
                reverse=True)[:5]
    if st:
        lines.append("Best streak retention (share of new players who ever hit a ~7-day streak; GameAnalytics top 1% D7 = 9.1%):")
        for s, u, v in st:
            lines.append(f"• {name_of(u)[:36]} — **{_pct(s, 1)}** reach a {v['streak7'][0]}-day streak")
    hooks = [(v["first_step"], u) for u, v in b.items() if v.get("first_step") is not None and (v.get("new") or 0) >= 500]
    if len(hooks) >= 6:
        hooks.sort()
        lines.append(f"First-step hook (share of new players who earn the game's next badge): median {_pct(median(h for h, _ in hooks))}; "
                     f"weakest: " + ", ".join(f"{name_of(u)[:22]} {_pct(h)}" for h, u in hooks[:3]))
    watch = [str(g) for g in C.WATCHLIST if str(g) in b]
    if watch:
        lines.append("Your watchlist (funnels — study these for your own game):")
        for u in watch[:6]:
            lines += funnel_lines(db, u, name_of)
    return lines


def check():
    try:
        rows = normalise(get_json("https://badges.roblox.com/v1/universes/65241/badges?limit=100&sortOrder=Asc").get("data"))
        dau, _ = estimate_dau(rows)
        if not rows:
            return ["⚪ Roblox badges — reachable, but the test game returned no badges"]
        return [f"✅ Roblox badges — {len(rows)} badges on the test game, ≈{int(dau or 0):,} players yesterday"]
    except Exception as e:
        return [f"❌ Roblox badges — {e}"]

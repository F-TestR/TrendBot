"""
Engagement: how STICKY a game is, measured from public numbers, and proof that it matters.

1. Session length (estimated). Little's law: players online = players joining per minute x minutes
   each stays, so   session minutes ~= average players online x 1,440 / visits that day.
   Benchmarks (GameAnalytics 2026 report, games with 1M+ monthly players): median game session
   9.8 min, top 5% 16.6 min, top 1% 21.1 min.

2. Stickiness score (0-100) per game per week = weighted percentile rank among that week's rated games:
     weekday hold vs a typical game  35%   (do players come back on school days?)
     session length                  25%   (do they stay?)
     level kept                      20%   (this week's players vs its best week of the last 6)
     favourite rate                  10%   (RoWatcher: share of visitors who favourite)
     revenue per player              10%   (RoWatcher's revenue estimate / average players)
   These mirror what Roblox says its recommendation system now rewards: returning players over
   28 days, playtime and session quality, and spend.

3. Backtest: does a high score in week W predict still having players 4 weeks later?

4. Feature mining: words in game descriptions (daily rewards, codes, trading...) that are far more
   common in long-term games than in the rest.

5. Opportunity map: each genre placed by growth (players now vs 3 weeks ago) and stickiness.
"""
import math
import re
from datetime import datetime, timedelta
from statistics import median

import config as C

SCHEMA = """
CREATE TABLE IF NOT EXISTS engage_weekly (uid TEXT, week TEXT, avg_ccu REAL, session_min REAL, level_kept REAL,
  fav_conv REAL, rev_per_ccu REAL, hold_rel REAL, score REAL, PRIMARY KEY (uid, week));
CREATE INDEX IF NOT EXISTS engage_weekly_week ON engage_weekly(week);
"""

WEIGHTS = {"hold_rel": 0.35, "session_min": 0.25, "level_kept": 0.20, "fav_conv": 0.10, "rev_per_ccu": 0.10}
LABELS = {"hold_rel": "weekday hold", "session_min": "session length", "level_kept": "players kept vs best week",
          "fav_conv": "favourite rate", "rev_per_ccu": "revenue per player"}


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)
    cols = {r[1] for r in db.execute("PRAGMA table_info(games)")}
    if "description" not in cols:
        db.execute("ALTER TABLE games ADD COLUMN description TEXT")


def record_description(db, uid, desc):
    if desc:
        db.execute("UPDATE games SET description=? WHERE uid=? AND (description IS NULL OR description='')",
                   (str(desc)[:2500], uid))


# ---------------------------------------------------------- weekly build ---

def _week_days(wed):
    w = _d(wed)
    return [_s(w - timedelta(days=i)) for i in range(6, -1, -1)]  # Thu .. Wed


def build_week(db, wed):
    days = _week_days(wed)
    lo = _s(_d(days[0]) - timedelta(days=1))
    data = {}
    for r in db.execute("""SELECT uid, day, peak, sum_ccu, n, visits, fav_conv, rev_usd FROM daily
                           WHERE day>=? AND day<=? AND peak IS NOT NULL""", (lo, wed)):
        data.setdefault(r["uid"], {})[r["day"]] = dict(r)
    holds = {r["uid"]: r["rel"] for r in db.execute("SELECT uid, rel FROM hold_weekly WHERE week=?", (wed,))}
    out = {}
    for uid, ds in data.items():
        avgs, sessions = [], []
        for d in days:
            r = ds.get(d)
            if not r:
                continue
            avg = (r["sum_ccu"] / r["n"]) if r["n"] and r["n"] >= 2 else None
            if avg:
                avgs.append(avg)
            prev = ds.get(_s(_d(d) - timedelta(days=1)))
            if avg and prev and r["visits"] and prev["visits"] and r["visits"] > prev["visits"]:
                s = avg * 1440 / (r["visits"] - prev["visits"])
                if C.SESSION_MIN_MIN <= s <= C.SESSION_MAX_MIN:
                    sessions.append(s)
        if len(avgs) < 4:
            continue
        a = sum(avgs) / len(avgs)
        if a < C.ENGAGE_MIN_AVG_CCU:
            continue
        fav = [ds[d]["fav_conv"] for d in days if d in ds and ds[d]["fav_conv"] is not None]
        rev = [ds[d]["rev_usd"] for d in days if d in ds and ds[d]["rev_usd"] is not None]
        out[uid] = {"avg_ccu": a, "session_min": median(sessions) if len(sessions) >= 3 else None,
                    "fav_conv": fav[-1] if fav else None,
                    "rev_per_ccu": (rev[-1] / a) if rev and a else None, "hold_rel": holds.get(uid)}
    return out


def _pct_ranks(values):
    """{key: value} -> {key: percentile 0..1}"""
    items = sorted((v, k) for k, v in values.items() if v is not None)
    n = len(items)
    if n < 2:
        return {k: 0.5 for _, k in items}
    return {k: i / (n - 1) for i, (_, k) in enumerate(items)}


def update(db, state, today):
    """Rebuild engagement for the last weeks, score them, keep latest scores in state['stick']."""
    import hold as HOLD
    ensure(db)
    wed0 = HOLD.latest_wed(today)
    weeks = [_s(_d(wed0) - timedelta(days=7 * i)) for i in range(C.HOLD_HISTORY_WEEKS)][::-1]
    history = {}
    for w in weeks:
        wk = build_week(db, w)
        if wk:
            history[w] = wk
    # level kept needs earlier weeks' averages
    for i, w in enumerate(weeks):
        if w not in history:
            continue
        for uid, x in history[w].items():
            prev = [history[p][uid]["avg_ccu"] for p in weeks[max(0, i - 5):i] if p in history and uid in history[p]]
            best = max(prev + [x["avg_ccu"]])
            x["level_kept"] = x["avg_ccu"] / best if prev else None
        ranks = {k: _pct_ranks({u: x[k] for u, x in history[w].items()}) for k in WEIGHTS}
        rows = []
        for uid, x in history[w].items():
            tot = wsum = 0.0
            for k, wt in WEIGHTS.items():
                if uid in ranks[k]:
                    tot += wt * ranks[k][uid]
                    wsum += wt
            have_core = x.get("hold_rel") is not None or x.get("session_min") is not None
            x["score"] = round(100 * tot / wsum, 1) if (wsum >= 0.45 and have_core) else None
            rows.append((uid, w, x["avg_ccu"], x["session_min"], x.get("level_kept"), x["fav_conv"],
                         x["rev_per_ccu"], x["hold_rel"], x["score"]))
        db.executemany("INSERT OR REPLACE INTO engage_weekly VALUES(?,?,?,?,?,?,?,?,?)", rows)
    latest = history.get(wed0) or (history[max(history)] if history else {})
    state["stick"] = {u: {"score": x["score"], "session": round(x["session_min"], 1) if x["session_min"] else None}
                      for u, x in latest.items() if x.get("score") is not None or x.get("session_min")}
    cut = _s(_d(today) - timedelta(days=C.THEME_KEEP_DAYS))
    db.execute("DELETE FROM engage_weekly WHERE week < ?", (cut,))
    return len(latest)


# -------------------------------------------------------------- backtest ---

def _spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    if len(xs) < 5:
        return None
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    vy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return cov / (vx * vy) if vx and vy else None


def backtest(db):
    """Score in week W vs share of players still there 4 weeks later."""
    rows = {}
    for r in db.execute("SELECT uid, week, avg_ccu, score FROM engage_weekly"):
        rows.setdefault(r["uid"], {})[r["week"]] = (r["avg_ccu"], r["score"])
    pairs = []
    for uid, ws in rows.items():
        for w, (a, sc) in ws.items():
            if sc is None or a < C.HOLD_MIN_PLAYERS:
                continue
            later = ws.get(_s(_d(w) + timedelta(days=28)))
            if later:
                pairs.append((sc, later[0] / a))
    if len(pairs) < C.BACKTEST_MIN_PAIRS:
        return {"n": len(pairs)}
    bands = {"70+": [], "40–70": [], "under 40": []}
    for sc, kept in pairs:
        bands["70+" if sc >= 70 else ("40–70" if sc >= 40 else "under 40")].append(kept)
    out = {"n": len(pairs), "rho": _spearman([p[0] for p in pairs], [math.log(max(p[1], 0.01)) for p in pairs]),
           "bands": {}}
    for b, ks in bands.items():
        if ks:
            out["bands"][b] = {"n": len(ks), "median_kept": median(ks), "alive": sum(1 for k in ks if k >= 0.5) / len(ks)}
    return out


# -------------------------------------------------------------- features ---

def feature_report(db, state):
    """Which description features are over-represented in long-term games."""
    lt = state.get("longterm") or {}
    rated = {r["uid"] for r in db.execute("SELECT DISTINCT uid FROM hold_weekly WHERE rel IS NOT NULL")}
    descs = {r["uid"]: (r["description"] or "").lower() for r in db.execute(
        "SELECT uid, description FROM games WHERE description IS NOT NULL AND description != ''")}
    pool = [u for u in rated if u in descs]
    is_lt = {u: (lt.get(u) or {}).get("status") == "long-term" for u in pool}
    n_lt = sum(is_lt.values())
    n_other = len(pool) - n_lt
    if n_lt < 5 or n_other < 5:
        return {"n_lt": n_lt, "n_other": n_other, "rows": []}
    rows = []
    for feat, pats in C.DESCRIPTION_FEATURES.items():
        rx = re.compile("|".join(r"\b" + re.escape(p) + r"\b" for p in pats))
        has = {u for u in pool if rx.search(descs[u])}
        if len(has) < C.FEATURE_MIN_GAMES:
            continue
        a = sum(1 for u in has if is_lt[u]) / n_lt
        b = sum(1 for u in has if not is_lt[u]) / n_other
        lt_rate_with = sum(1 for u in has if is_lt[u]) / len(has)
        lt_rate_without = sum(1 for u in pool if u not in has and is_lt[u]) / max(1, len(pool) - len(has))
        rows.append({"feature": feat, "games": len(has), "in_lt": a, "in_other": b,
                     "lift": (lt_rate_with / lt_rate_without) if lt_rate_without else None})
    rows.sort(key=lambda r: -(r["lift"] or 0))
    return {"n_lt": n_lt, "n_other": n_other, "rows": rows}


# ------------------------------------------------------- opportunity map ---

def opportunity_map(db, state, today):
    """Per genre: growth (players this week vs 3 weeks ago, same games) and median stickiness."""
    import hold as HOLD
    w = HOLD.latest_wed(today)
    w3 = _s(_d(w) - timedelta(days=21))
    now = {r["uid"]: (r["avg_ccu"], r["score"]) for r in db.execute("SELECT uid, avg_ccu, score FROM engage_weekly WHERE week=?", (w,))}
    then = {r["uid"]: r["avg_ccu"] for r in db.execute("SELECT uid, avg_ccu FROM engage_weekly WHERE week=?", (w3,))}
    genre = {r["uid"]: r["genre"] or "Unknown" for r in db.execute("SELECT uid, genre FROM games")}
    by = {}
    for uid, (a, sc) in now.items():
        g = genre.get(uid, "Unknown")
        x = by.setdefault(g, {"now": 0.0, "then": 0.0, "scores": [], "games": 0})
        x["games"] += 1
        if sc is not None:
            x["scores"].append(sc)
        if uid in then:
            x["now"] += a
            x["then"] += then[uid]
    rows = []
    for g, x in by.items():
        if x["games"] < C.GENRE_MIN_GAMES or not x["scores"] or not x["then"]:
            continue
        growth = (x["now"] / x["then"] - 1) * 100
        stick = median(x["scores"])
        q = ("🟢 growing + sticky" if growth >= C.MAP_GROWTH_PCT and stick >= 50 else
             "🟡 growing, not sticky (hype)" if growth >= C.MAP_GROWTH_PCT else
             "🔵 sticky, not growing (steady)" if stick >= 50 else "🔴 shrinking, not sticky")
        rows.append({"genre": g, "growth": growth, "stick": stick, "games": x["games"], "quadrant": q})
    rows.sort(key=lambda r: -(r["growth"] + r["stick"]))
    return rows


def map_chart(rows):
    import charts
    plt = charts._matplotlib()
    if not plt or len(rows) < 3:
        return None
    import io
    fig, ax = plt.subplots(figsize=(9, 6), dpi=110)
    charts._style(ax, fig)
    xs = [r["stick"] for r in rows]
    ys = [max(-60, min(150, r["growth"])) for r in rows]
    ax.axvline(50, color=charts.GRID, linewidth=1.2)
    ax.axhline(C.MAP_GROWTH_PCT, color=charts.GRID, linewidth=1.2)
    for r, x, y in zip(rows, xs, ys):
        good = r["quadrant"].startswith("🟢")
        ax.scatter([x], [y], s=40 + 4 * r["games"], color=charts.PALETTE[1] if good else "#8a8f98", alpha=0.85, zorder=3)
        ax.annotate(r["genre"][:22], (x, y), xytext=(6, 4), textcoords="offset points", color=charts.FG, fontsize=8.5)
    ax.set_xlabel("stickiness (median score of its games, 0–100)", color=charts.FG)
    ax.set_ylabel("growth: players now vs 3 weeks ago (%)", color=charts.FG)
    ax.set_xlim(0, 100)
    ax.text(98, ax.get_ylim()[1] * 0.95, "growing + sticky", ha="right", va="top", color=charts.FG, fontsize=9, fontweight="bold")
    ax.text(2, ax.get_ylim()[1] * 0.95, "hype", ha="left", va="top", color=charts.FG, fontsize=9)
    ax.text(98, ax.get_ylim()[0] * 0.9 if ax.get_ylim()[0] < 0 else 2, "steady", ha="right", color=charts.FG, fontsize=9)
    ax.set_title("Opportunity map by genre — top right = players arriving AND staying", loc="left", color=charts.FG, fontsize=12)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=charts.BG)
    plt.close(fig)
    return buf.getvalue()


# -------------------------------------------------------------- output ---

def heat_points(state, gid):
    s = ((state.get("stick") or {}).get(gid) or {}).get("score")
    return (max(-5.0, min(5.0, (s - 50) / 10)), s) if s is not None else (0.0, None)


def report_lines(db, state, today, fmt, name_of, link):
    lines = ["📏 **Stickiness** (weekday hold 35% · session length 25% · players kept vs best week 20% · "
             "favourite rate 10% · revenue per player 10%)"]
    st = state.get("stick") or {}
    sess = [v["session"] for v in st.values() if v.get("session")]
    if sess:
        lines.append(f"• Estimated session length this week: median game **{median(sess):.1f} min** "
                     f"(GameAnalytics: median 9.8 min, top 5% 16.6, top 1% 21.1 — their sample is bigger games, "
                     f"and ours is an estimate, so compare games with each other first).")
    young = state.get("_young_ids") or set()
    top = sorted(((v["score"], u, v) for u, v in st.items() if v.get("score") is not None and u in young), reverse=True)[:6]
    if top:
        lines.append("Stickiest young games:")
        for sc, u, v in top:
            se = f", ~{v['session']:.0f} min sessions" if v.get("session") else ""
            lines.append(f"• {name_of(u)[:38]} — **{sc:.0f}**/100{se} {link(u)}")
    bt = backtest(db)
    lines += ["", "🧪 **Does stickiness predict survival?** (score in a week vs players 4 weeks later)"]
    if bt.get("bands"):
        for b in ("70+", "40–70", "under 40"):
            x = bt["bands"].get(b)
            if x:
                lines.append(f"• Score {b}: kept a median **{x['median_kept']*100:.0f}%** of players; "
                             f"{x['alive']*100:.0f}% still had half or more ({x['n']} game-weeks)")
        if bt.get("rho") is not None:
            lines.append(f"• Rank correlation {bt['rho']:+.2f} (0 = no link, +1 = perfect) over {bt['n']} game-weeks.")
    else:
        lines.append(f"• Needs more history ({bt.get('n', 0)} game-weeks so far, needs {C.BACKTEST_MIN_PAIRS}).")
    fr = feature_report(db, state)
    lines += ["", "🧩 **What long-term games do differently** (features mentioned in their descriptions)"]
    if fr["rows"]:
        for r in [x for x in fr["rows"] if x["lift"] is not None][:8]:
            lines.append(f"• {r['feature']}: in {r['in_lt']*100:.0f}% of long-term games vs {r['in_other']*100:.0f}% of others "
                         f"→ games mentioning it were **{r['lift']:.1f}×** as likely to be long-term ({r['games']} games)")
        lines.append("_Descriptions are marketing, and this is correlation, not proof — but it's a strong checklist._")
    else:
        lines.append(f"• Needs more rated games ({fr['n_lt']} long-term, {fr['n_other']} others with descriptions).")
    om = opportunity_map(db, state, today)
    lines += ["", "🗺️ **Opportunity map** (growth vs stickiness, by genre — chart attached)"]
    if om:
        for q in ("🟢", "🟡", "🔵", "🔴"):
            gs = [r for r in om if r["quadrant"].startswith(q)]
            if gs:
                lines.append(f"• {gs[0]['quadrant']}: " + ", ".join(f"{r['genre']} ({r['growth']:+.0f}%, {r['stick']:.0f})" for r in gs[:6]))
    else:
        lines.append("• Needs 3+ weeks of history.")
    return lines, om

"""
Weekday hold and LONG-TERM GAMES.

Weekly, for every game with enough players:
  hold       = average players Tue + Wed  /  average players the Saturday + Sunday before
  benchmark  = the median hold of all rated games that week (the "typical" weekday dip)
  relative   = hold / benchmark     -> above 1.0 = keeps its crowd better than a typical game

Long-term game = a game whose relative hold is >= LONGTERM_REL in most of its recent
rated weeks (at least LONGTERM_MIN_WEEKS of them). These are habit games: players come
back on school days, not just when a video sends them on a Saturday.

Judged against the median game (not Roblox's total) so past weeks rebuilt from
downloaded history are measured exactly like live weeks. Roblox's own dip is still
recorded and shown for context.

Left out, because the ratio would lie:
  growing   weekdays 1.5x+ the previous week's weekdays (measures growth, not loyalty)
  new       under 14 days old with no previous week
  spike     Saturday > 1.8x Sunday (an event): only Sunday counts as the weekend
"""
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


def compute_week(db, wed, created):
    wkend, wkday = week_of(wed)
    prev = [_s(_d(d) - timedelta(days=7)) for d in wkday]
    days = wkend + wkday + prev
    rows = {}
    for r in db.execute(f"SELECT uid, day, peak, sum_ccu, n FROM daily WHERE day IN ({','.join('?' * len(days))}) "
                        "AND peak IS NOT NULL", days):
        rows.setdefault(r["uid"], {})[r["day"]] = (r["peak"], (r["sum_ccu"] / r["n"]) if r["n"] else None, r["n"] or 0)
    out = {}
    for uid, ds in rows.items():
        if not all(d in ds for d in wkend + wkday):
            continue
        use_avg = all(ds[d][2] >= 2 and ds[d][1] for d in wkend + wkday + [p for p in prev if p in ds])
        val = (lambda d: ds[d][1]) if use_avg else (lambda d: ds[d][0])
        sat, sun = val(wkend[0]), val(wkend[1])
        if max(sat, sun) < C.HOLD_MIN_PLAYERS:
            continue
        flag, weekend = "ok", (sat + sun) / 2
        if sat > C.HOLD_SPIKE_RATIO * sun:
            weekend, flag = sun, "spike"
        weekday = sum(val(d) for d in wkday) / 2
        pv = [val(d) for d in prev if d in ds]
        c = created.get(uid)
        if len(pv) == 2 and weekday >= C.HOLD_GROWING_RATIO * (sum(pv) / 2):
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
    return state["hold_meta"]


# ----------------------------------------------------------- long term ---

def classify(db, today):
    """{uid: {"status": "long-term"|"promising", "weeks": n, "good": k, "med": median rel}}"""
    since = _s(_d(latest_wed(today)) - timedelta(days=7 * (C.LONGTERM_WINDOW_WEEKS - 1)))
    by = {}
    for r in db.execute("SELECT uid, week, rel, weekend FROM hold_weekly WHERE week>=? AND rel IS NOT NULL", (since,)):
        by.setdefault(r["uid"], []).append((r["week"], r["rel"], r["weekend"]))
    out = {}
    for uid, ws in by.items():
        rels = [r for _, r, _ in ws]
        good = sum(1 for r in rels if r >= C.LONGTERM_REL)
        med = median(rels)
        players = max(w for _, _, w in ws)
        if len(rels) >= C.LONGTERM_MIN_WEEKS and good / len(rels) >= C.LONGTERM_SHARE and med >= C.LONGTERM_REL:
            out[uid] = {"status": "long-term", "weeks": len(rels), "good": good, "med": round(med, 3), "players": players}
        elif len(rels) >= 1 and med >= C.LONGTERM_PROMISING_REL:
            out[uid] = {"status": "promising", "weeks": len(rels), "good": good, "med": round(med, 3), "players": players}
    return out


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
    for g, x in by.items():
        if x["games"] < C.GENRE_MIN_GAMES:
            continue
        x["lt"].sort(reverse=True)
        rows.append({"genre": g, "games": x["games"], "median": median(x["rels"]), "lt": len(x["lt"]),
                     "share": len(x["lt"]) / x["games"], "promising": x["promising"], "top": x["lt"][:3]})
    rows.sort(key=lambda r: (-r["share"], -r["median"]))
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
    lines = [f"🔁 **Weekday hold** (Tue–Wed vs the weekend of {sat}; a typical game kept "
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
    lines = [f"🏛️ **Long-term games** (keep {C.LONGTERM_REL:.1f}×+ the typical weekday hold in most weeks, "
             f"{C.LONGTERM_MIN_WEEKS}+ weeks measured; {meta.get('weeks', 0)} weeks of data so far)"]
    rows = genre_table(db, state)
    if rows:
        lines.append("By genre (share of rated games that are long-term · median hold vs typical):")
        for r in rows[:12]:
            tops = ", ".join(n[:22] for _, n, _, _ in r["top"]) or "—"
            lines.append(f"• **{r['genre']}** — {r['lt']}/{r['games']} long-term ({r['share']*100:.0f}%) · "
                         f"median {r['median']:.2f}× · e.g. {tops}")
    else:
        lines.append("• Building up — needs a couple of weeks of weekday-hold data.")
    young = sorted(((v["players"], uid, v) for uid, v in lt.items() if v["status"] == "long-term"
                    and uid in (state.get("_young_ids") or set())), reverse=True)
    if young:
        lines += ["", "🌱🏛️ **Young games that are already long-term** (the ones to study):"]
        for p, uid, v in young[:6]:
            lines.append(f"• {name_of(uid)[:38]} — {v['good']}/{v['weeks']} weeks above typical, median {v['med']:.2f}× · "
                         f"{fmt(p)} weekend players {link(uid)}")
    prom = sorted(((v["med"], uid, v) for uid, v in lt.items() if v["status"] == "promising"
                   and uid in (state.get("_young_ids") or set())), reverse=True)
    if prom:
        lines.append("Promising (one strong week so far): " + ", ".join(f"{name_of(u)[:24]} ({v['med']:.2f}×)" for _, u, v in prom[:6]))
    return lines


def newly_longterm(state, before):
    """uids that became long-term since the previous classification."""
    now = state.get("longterm") or {}
    return [u for u, v in now.items() if v["status"] == "long-term" and (before.get(u) or {}).get("status") != "long-term"]

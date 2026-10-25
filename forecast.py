"""
Forecasting: how big, how soon, how long.

1. S-CURVE PEAK FORECAST (growth-curve fitting, Bass-style)
   New games spread like new products: slow, then fast, then levelling off. For each rising young game
   the bot fits  players(t) = K / (1 + e^(-r (t - t0)))  to its weekday-adjusted daily players and reads off
   K (likely peak), the date it reaches 90% of K, and a range from all curves that fit nearly as well.
   Before the turning point the peak is uncertain, so the bot says "at least" and shows the range.

2. BREAKOUT START DETECTION (Bayesian online change-point detection, Adams & MacKay 2007)
   Tracks each game's daily growth rate and the probability that its growth just changed regime.
   Fires when a new, faster regime has very probably started in the last 2 days - earlier and with
   fewer false alarms than a fixed "x1.5 vs last week" rule.

3. LIFESPAN (survival analysis, Kaplan-Meier)
   For every game that peaked above SURV_MIN_PEAK: how many days until it fell below half its peak.
   Games still above half are counted properly as "still going" (censored), not ignored. Median
   half-life by genre, mechanic and weekday-hold band; each game gets the estimate for its group.

Each part is back-tested on the bot's own history and the results go in the weekly report.
Pure Python, no extra libraries.
"""
import math
from datetime import datetime, timedelta
from statistics import median

import config as C

SCHEMA = """
CREATE TABLE IF NOT EXISTS fc_preds (day TEXT, uid TEXT, players REAL, peak REAL, lo REAL, hi REAL, peak_day TEXT,
  status TEXT, PRIMARY KEY (day, uid));
CREATE TABLE IF NOT EXISTS cp_fires (day TEXT, uid TEXT, players REAL, prob REAL, growth REAL, PRIMARY KEY (day, uid));
"""


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)


# ------------------------------------------------------------- loading ---

def load_series(db, lo, hi, min_avg=0):
    """{uid: [(day, average players)]} sorted by day."""
    out = {}
    for r in db.execute("SELECT uid, day, peak, sum_ccu, n FROM daily WHERE day>=? AND day<=? AND peak IS NOT NULL",
                        (lo, hi)):
        avg = (r["sum_ccu"] / r["n"]) if r["n"] and r["n"] >= 3 and r["sum_ccu"] else (r["peak"] or 0) * 0.75
        out.setdefault(r["uid"], []).append((r["day"], avg))
    for v in out.values():
        v.sort()
    return {u: v for u, v in out.items() if max(a for _, a in v) >= min_avg}


def weekday_factors(series):
    """Typical players on each weekday vs that game's own weekly average (median across games)."""
    ratios = {i: [] for i in range(7)}
    for v in series.values():
        if len(v) < 14:
            continue
        vals = dict(v)
        for day, a in v[3:-3]:
            win = [vals.get(_s(_d(day) + timedelta(days=k))) for k in range(-3, 4)]
            win = [w for w in win if w]
            if len(win) == 7 and a > 50:
                ratios[_d(day).weekday()].append(a / (sum(win) / 7))
    if sum(len(x) for x in ratios.values()) < 200:
        return [0.95, 0.93, 0.93, 0.95, 1.02, 1.13, 1.12]
    return [median(ratios[i]) if ratios[i] else 1.0 for i in range(7)]


def adjust(v, wf):
    return [(d, a / wf[_d(d).weekday()]) for d, a in v]


# ------------------------------------------------------------ S-curve ---

R_GRID = [0.12 * (1.17 ** i) for i in range(18)]   # 0.12 .. ~1.7 per day


def fit_scurve(ys):
    """ys: adjusted daily players (oldest first). Returns dict or None."""
    pts = [(i, y) for i, y in enumerate(ys) if y and y > 0]
    if len(pts) < 4:
        return None
    n = len(ys)
    ymax = max(y for _, y in pts)
    fits = []
    for r in R_GRID:
        t0 = -3.0
        while t0 <= n + 35:
            f = [1 / (1 + math.exp(-r * (t - t0))) for t, _ in pts]
            sff = sum(x * x for x in f)
            if sff > 0:
                K = sum(y * x for (_, y), x in zip(pts, f)) / sff
                if K >= 0.95 * ymax and K < ymax * 60:
                    err = sum((math.log(y) - math.log(max(K * x, 1e-6))) ** 2 for (_, y), x in zip(pts, f))
                    fits.append((err, K, r, t0))
            t0 += 0.5
    if not fits:
        return None
    fits.sort()
    best = fits[0]
    good = [f for f in fits if f[0] <= best[0] * 1.25 + 0.02]
    ks = sorted(f[1] for f in good)
    err, K, r, t0 = best
    t_last = n - 1
    t90 = t0 + math.log(9) / r
    return {"K": K, "lo": ks[max(0, int(len(ks) * 0.1))], "hi": ks[min(len(ks) - 1, int(len(ks) * 0.9))],
            "r": r, "t0": t0, "days_to_90": max(0.0, t90 - t_last), "past_turn": t_last >= t0,
            "rmse": math.sqrt(err / len(pts))}


def forecast_game(v, wf):
    """v: [(day, avg)] for one game. Returns forecast dict or None."""
    if len(v) < C.FC_MIN_DAYS:
        return None
    adj = adjust(v[-C.FC_WINDOW_DAYS:], wf)
    ys = [a for _, a in adj]
    mx = max(ys)
    last3 = sum(ys[-3:]) / 3
    if mx < C.FC_MIN_PLAYERS:
        return None
    if last3 < 0.8 * mx and ys.index(mx) < len(ys) - 2:
        return {"status": "past peak", "peak": mx, "lo": mx, "hi": mx, "peak_day": adj[ys.index(mx)][0],
                "now": last3}
    if ys[-1] < 1.15 * ys[0] and len(ys) >= 6:
        return {"status": "steady", "peak": mx, "lo": mx, "hi": mx, "peak_day": None, "now": last3}
    f = fit_scurve(ys)
    if not f:
        return None
    last_day = _d(adj[-1][0])
    status = "rising" if f["past_turn"] else "early"
    return {"status": status, "peak": f["K"], "lo": f["lo"], "hi": f["hi"],
            "peak_day": _s(last_day + timedelta(days=round(f["days_to_90"]))), "now": ys[-1], "rmse": f["rmse"]}


def backtest_scurve(series, wf, today):
    """Fit on each rising game's first FC_BACKTEST_DAYS days; compare with its real peak over the next 3 weeks."""
    errs = []
    for uid, v in series.items():
        if len(v) < C.FC_BACKTEST_DAYS + 10:
            continue
        adj = adjust(v, wf)
        start = next((i for i, (_, a) in enumerate(adj) if a >= C.FC_MIN_PLAYERS), None)
        if start is None or start + C.FC_BACKTEST_DAYS + 10 > len(adj):
            continue
        head = [a for _, a in adj[start:start + C.FC_BACKTEST_DAYS]]
        tail = [a for _, a in adj[start + C.FC_BACKTEST_DAYS:start + C.FC_BACKTEST_DAYS + 21]]
        if head[-1] < 1.3 * head[0]:
            continue  # only games that were rising when the forecast would have been made
        f = fit_scurve(head)
        if not f:
            continue
        actual = max(head + tail)
        errs.append(abs(math.log(f["K"] / actual)))
    if len(errs) < C.FC_BACKTEST_MIN:
        return {"n": len(errs)}
    return {"n": len(errs), "median_err": math.exp(median(errs)) - 1,
            "within2x": sum(1 for e in errs if e <= math.log(2)) / len(errs)}


# --------------------------------------------------------- change-points ---

def bocpd(xs, hazard=None, mu0=0.0, kappa0=1.0, alpha0=1.0, beta0=0.02):
    """Bayesian online change-point detection on a sequence (Normal-Gamma model, Student-t predictive).
    Returns (run-length posterior after the last point, per-run-length posterior mean)."""
    h = hazard or (1 / C.CP_EXPECTED_RUN)
    R = [1.0]
    mu, kappa, alpha, beta = [mu0], [kappa0], [alpha0], [beta0]
    for x in xs:
        pred = []
        for m, k, a, b in zip(mu, kappa, alpha, beta):
            scale2 = b * (k + 1) / (a * k)
            nu = 2 * a
            z = (x - m) ** 2 / (nu * scale2)
            logp = (math.lgamma((nu + 1) / 2) - math.lgamma(nu / 2) - 0.5 * math.log(nu * math.pi * scale2)
                    - (nu + 1) / 2 * math.log1p(z))
            pred.append(math.exp(logp))
        growth = [r * p * (1 - h) for r, p in zip(R, pred)]
        cp = sum(r * p * h for r, p in zip(R, pred))
        R = [cp] + growth
        tot = sum(R) or 1e-300
        R = [r / tot for r in R]
        mu_n = [mu0] + [(k * m + x) / (k + 1) for m, k in zip(mu, kappa)]
        kappa_n = [kappa0] + [k + 1 for k in kappa]
        alpha_n = [alpha0] + [a + 0.5 for a in alpha]
        beta_n = [beta0] + [b + k * (x - m) ** 2 / (2 * (k + 1)) for m, k, b in zip(mu, kappa, beta)]
        mu, kappa, alpha, beta = mu_n, kappa_n, alpha_n, beta_n
        if len(R) > 60:  # truncate very long runs
            R, mu, kappa, alpha, beta = R[:60], mu[:60], kappa[:60], alpha[:60], beta[:60]
    return R, mu


def changepoint(v, wf):
    """Has a faster growth regime just started? Returns dict or None."""
    adj = adjust(v[-C.CP_WINDOW_DAYS:], wf)
    ys = [a for _, a in adj]
    if len(ys) < 6 or ys[-1] < C.CP_MIN_PLAYERS:
        return None
    xs = [math.log(max(b, 1) / max(a, 1)) for a, b in zip(ys, ys[1:])]
    R, mu = bocpd(xs)
    p_recent = sum(R[:C.CP_RECENT + 1])
    # growth in the new regime (runs of length <= CP_RECENT) vs the old one
    new_g = sum(R[i] * mu[i] for i in range(min(len(R), C.CP_RECENT + 1))) / (p_recent or 1)
    # mean of the earlier points
    old = xs[:-(C.CP_RECENT + 1)] or [0.0]
    old_g = sum(old) / len(old)
    return {"prob": p_recent, "growth": new_g, "old": old_g, "players": ys[-1],
            "fire": p_recent >= C.CP_MIN_PROB and new_g >= C.CP_MIN_GROWTH and new_g - old_g >= C.CP_MIN_JUMP}


def backtest_cp(series, wf):
    """How often a firing was followed by 2x players within 14 days, vs random young game-days."""
    fired, base = [], []
    cands = [v for v in series.values() if len(v) >= 20 and max(a for _, a in v) >= 2 * C.CP_MIN_PLAYERS]
    cands = cands[:C.CP_BACKTEST_GAMES]
    for v in cands:
        for end in range(8, len(v) - 14, 2):
            seg = v[:end]
            if seg[-1][1] < C.CP_MIN_PLAYERS:
                continue
            fut = max(a for _, a in v[end:end + 14])
            hit = fut >= 2 * seg[-1][1]
            base.append(hit)
            c = changepoint(seg, wf)
            if c and c["fire"]:
                fired.append(hit)
    if len(fired) < 5 or not base:
        return {"n": len(fired)}
    return {"n": len(fired), "hit": sum(fired) / len(fired), "base": sum(base) / len(base)}


# ------------------------------------------------------------- survival ---

def kaplan_meier_median(rows):
    """rows: [(duration_days, event 1/0)]. Median survival (days) or None if more than half survive."""
    if not rows:
        return None
    times = sorted({d for d, _ in rows})
    s = 1.0
    for t in times:
        at_risk = sum(1 for d, _ in rows if d >= t)
        events = sum(1 for d, e in rows if d == t and e)
        if at_risk:
            s *= 1 - events / at_risk
        if s <= 0.5:
            return t
    return None


def survival(db, series, wf, today, groups):
    """Half-life (days from peak until below 50% of peak) per group. groups: uid -> {kind: label}."""
    rows = {}
    for uid, v in series.items():
        adj = adjust(v, wf)
        ys = [a for _, a in adj]
        if max(ys) < C.SURV_MIN_PEAK or len(ys) < 7:
            continue
        i = ys.index(max(ys))
        if i >= len(ys) - 3 or i < 2:
            continue  # peak too recent to judge, or peak before the window
        pk = ys[i]
        event, dur = 0, len(ys) - 1 - i
        for j in range(i + 1, len(ys) - 2):
            if sum(ys[j:j + 3]) / 3 < 0.5 * pk:
                event, dur = 1, j - i
                break
        g = dict(groups.get(uid, {}))
        g["all"] = "all games"
        for kind, label in g.items():
            if label:
                rows.setdefault((kind, label), []).append((dur, event))
    out = {}
    for key, rs in rows.items():
        if len(rs) >= C.SURV_MIN_GROUP:
            med = kaplan_meier_median(rs)
            out[key] = {"n": len(rs), "events": sum(e for _, e in rs), "median": med}
    return out


def lifespan_for(table, g):
    """Best available half-life estimate for a game with group labels g."""
    for kind in ("hold", "mech", "genre", "all"):
        label = g.get(kind) if kind != "all" else "all games"
        x = table.get((kind, label)) if label else None
        if x:
            return x, kind, label
    return None, None, None


# --------------------------------------------------------------- driver ---

def update(db, state, today, young_ids, mechanics_of):
    ensure(db)
    lo = _s(_d(today) - timedelta(days=C.FC_HISTORY_DAYS))
    yday = _s(_d(today) - timedelta(days=1))
    series = load_series(db, lo, yday, min_avg=50)
    wf = weekday_factors(series)
    fc, cp = {}, {}
    for uid in young_ids:
        v = series.get(uid)
        if not v:
            continue
        f = forecast_game(v, wf)
        if f:
            fc[uid] = f
        c = changepoint(v, wf)
        if c:
            cp[uid] = c
    db.executemany("INSERT OR REPLACE INTO fc_preds VALUES(?,?,?,?,?,?,?,?)",
                   [(today, u, f["now"], f["peak"], f["lo"], f["hi"], f.get("peak_day"), f["status"]) for u, f in fc.items()])
    db.executemany("INSERT OR REPLACE INTO cp_fires VALUES(?,?,?,?,?)",
                   [(today, u, c["players"], c["prob"], c["growth"]) for u, c in cp.items() if c["fire"]])
    # groups for lifespans
    meta = {r["uid"]: (r["name"] or "", r["genre"]) for r in db.execute("SELECT uid, name, genre FROM games")}
    holds = {}
    for r in db.execute("SELECT uid, rel FROM hold_weekly WHERE rel IS NOT NULL"):
        holds.setdefault(r["uid"], []).append(r["rel"])
    groups = {}
    for uid in series:
        nm, genre = meta.get(uid, ("", None))
        mechs = mechanics_of(nm) if nm else []
        hv = holds.get(uid)
        band = None
        if hv:
            m = median(hv)
            band = "holds weekday players well" if m >= 1.1 else ("holds them poorly" if m < 0.9 else "average weekday hold")
        groups[uid] = {"genre": genre, "mech": mechs[0] if mechs else None, "hold": band}
    surv = survival(db, series, wf, today, groups)
    life = {}
    for uid in young_ids:
        if uid in groups or uid in fc:
            x, kind, label = lifespan_for(surv, groups.get(uid, {}))
            if x and x["median"] is not None:
                life[uid] = {"days": x["median"], "basis": label}
    state["_fc"] = fc
    state["_cp"] = cp
    state["_life"] = life
    state["fc_meta"] = {"day": today, "wf": [round(x, 3) for x in wf]}
    # back-tests are slower: refresh weekly
    if state.get("fc_bt_day") is None or (_d(today) - _d(state["fc_bt_day"])).days >= 6:
        try:
            state["fc_bt"] = {"scurve": backtest_scurve(series, wf, today), "cp": backtest_cp(series, wf)}
            state["fc_bt_day"] = today
        except Exception as e:
            print(f"forecast backtest failed: {e}")
    state["fc_surv"] = [{"kind": k, "label": l, **v} for (k, l), v in sorted(surv.items(), key=lambda kv: -kv[1]["n"])][:60]
    db.execute("DELETE FROM fc_preds WHERE day < ?", (_s(_d(today) - timedelta(days=60)),))
    db.execute("DELETE FROM cp_fires WHERE day < ?", (_s(_d(today) - timedelta(days=120)),))
    return len(fc), sum(1 for c in cp.values() if c["fire"])


def peak_text(f, fmt):
    if not f:
        return None
    if f["status"] == "past peak":
        return "past its peak"
    if f["status"] == "steady":
        return "steady"
    when = ""
    if f.get("peak_day"):
        when = f" by {_d(f['peak_day']).strftime('%a %d %b')}"
    if f["status"] == "early":
        return f"heading for {fmt(f['lo'])}–{fmt(f['hi'])}{when} (early, wide range)"
    return f"peak ~{fmt(f['peak'])}{when}"


def weekly_lines(state, fmt):
    lines = []
    bt = state.get("fc_bt") or {}
    s = bt.get("scurve") or {}
    if s.get("median_err") is not None:
        lines.append(f"📈 Peak forecasts (made on day {C.FC_BACKTEST_DAYS}): typically off by **{s['median_err'] * 100:.0f}%**; "
                     f"{s['within2x'] * 100:.0f}% within 2× of the real peak ({s['n']} games)")
    c = bt.get("cp") or {}
    if c.get("hit") is not None:
        lines.append(f"🧭 Breakout-start signal: followed by 2× players within 2 weeks **{c['hit'] * 100:.0f}%** of the time "
                     f"vs {c['base'] * 100:.0f}% for any young game ({c['n']} firings)")
    surv = state.get("fc_surv") or []
    allg = next((x for x in surv if x["kind"] == "all"), None)
    if allg and allg["median"] is not None:
        lines.append(f"⏳ A typical hit keeps half its peak players for **{allg['median']} days** ({allg['n']} games)")
    elif allg:
        lines.append(f"⏳ Lifespans: most of the {allg['n']} hits tracked are still above half their peak — "
                     f"half-lives appear as they age")
    for kind, title in (("hold", "By weekday hold"), ("mech", "By mechanic"), ("genre", "By genre")):
        xs = [x for x in surv if x["kind"] == kind and x["median"] is not None]
        xs.sort(key=lambda x: -x["median"])
        if len(xs) >= 2:
            lines.append(f"{title}: " + " · ".join(f"{x['label']} **{x['median']}d**" for x in xs[:4]))
    return lines

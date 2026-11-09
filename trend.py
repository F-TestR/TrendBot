"""
Trend Score: one number (0-100) for "how likely is this young game to take off in the next 2 weeks".

It is a learned combination of every early signal the bot has, so you don't have to weigh them yourself:
  players vs last week · growth just accelerated (change-point) · S-curve forecast headroom ·
  Roblox promotion chance (algorithm mirror) · breakout model · cross-platform heat ·
  YouTube Shorts speed and count · YouTube videos · Roblox home-page sorts it's in ·
  the size of the copy wave it belongs to · weekday hold · playtime per player · size and age

Outcome it predicts ("takes off"): within 14 days the game's daily players are at least DOUBLE today's AND
at least TS_MIN_TARGET (5,000), on TS_SUSTAIN_DAYS or more days. (An earlier version only asked for 2x and
1,000 players on one day. A 400-player game wobbling up to 1,000 counted, a quarter of all snapshots
"took off", and the learned model simply ranked the smallest games first.)

  * Every day the bot saves each young game's signals ("snapshots"). After 14 days it knows the outcome.
  * It starts with a hand-set formula. As outcomes arrive that formula is CALIBRATED against them (a
    2-number curve fitted to what its past scores were actually followed by), so a score of 40 means
    "about 40% of games scored like this took off" - no model training involved, so it can't fool itself.
  * A learned model (logistic regression, challenged by boosted trees) replaces the formula only after it
    passes the honest test in learn.py: trained only on outcomes already known at the time (a 14-day
    purge - the same game appears in many daily snapshots, so an ordinary train/test split would let it
    memorise games), over TS_MIN_DAYS+ different days.
  * Each score comes with the 2-3 signals that pushed it up most, in plain English.
"""
import json
import math
from datetime import datetime, timedelta
from statistics import median

import config as C
import learn as L
import warehouse as W

SCHEMA = """
CREATE TABLE IF NOT EXISTS trend_feats (day TEXT, uid TEXT, players REAL, feats TEXT, score REAL,
  PRIMARY KEY (day, uid));
"""

NAMES = ["growth", "accel", "headroom", "promo", "breakout", "heat", "shorts_speed", "shorts_n", "yt_views",
         "sorts", "abroad", "wave", "studio", "event", "hold", "playtime", "size", "age"]

# starting weights (used until enough real outcomes exist); features are roughly 0..3 each
PRIOR = {"growth": 0.9, "accel": 1.2, "headroom": 0.5, "promo": 2.0, "breakout": 1.5, "heat": 1.5,
         "shorts_speed": 0.5, "shorts_n": 0.4, "yt_views": 0.25, "sorts": 0.5, "abroad": 0.6, "wave": 0.4,
         "studio": 0.4, "event": -0.8, "hold": 0.3,
         "playtime": 0.3, "size": -0.2, "age": -0.4}
PRIOR_BIAS = -3.4


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)


def _sig(z):
    return 1 / (1 + math.exp(-max(-30, min(30, z))))


# ------------------------------------------------------------ features ---

def features(state, db, gid, today, ctx, yts, theme_new):
    """Signals for one game as of today. Returns (feats, info for reasons)."""
    r = state["games"].get(gid) or {}
    players = max(1, r.get("last", 0))
    info = {"players": players}
    ratio, _ = ctx["growth"](r, _s(_d(today) - timedelta(days=1)), state.get("cutoff") or 500, state.get("baseline_day")) if r else (None, None)
    f = {}
    f["growth"] = max(-2.0, min(4.0, math.log2(ratio))) if ratio else 0.0
    info["ratio"] = ratio
    c = (state.get("_cp") or {}).get(gid) or {}
    f["accel"] = (c.get("prob", 0) * max(0, c.get("growth", 0)) * 5) if c else 0.0
    info["cp"] = c.get("fire")
    fc = (state.get("_fc") or {}).get(gid) or {}
    if fc.get("status") in ("rising", "early") and fc.get("peak"):
        f["headroom"] = max(0.0, min(5.0, math.log2(fc["peak"] / players)))
        info["peak"] = fc["peak"]
    else:
        f["headroom"] = 0.0
    pr = ((state.get("_promo") or {}).get(gid) or {}).get("p")
    f["promo"] = pr
    info["promo"] = pr
    pm = (state.get("_preds") or {}).get(gid)
    f["breakout"] = pm
    info["breakout"] = pm
    h = ctx["S"].heat(state, gid, today, state.get("cutoff") or 500, yts) or {}
    f["heat"] = (h.get("score") or 0) / 100
    info["heat"] = h.get("score")
    y = yts.get(gid) or {}
    f["shorts_speed"] = math.log10(1 + y.get("svph", 0)) / 2
    f["shorts_n"] = math.log1p(y.get("sn", 0))
    f["yt_views"] = math.log10(1 + y.get("views", 0)) / 2
    info["svph"], info["sn"], info["ytv"] = y.get("svph", 0), y.get("sn", 0), y.get("views", 0)
    seen = ((state.get("rbx_direct") or {}).get("seen") or {}).get(gid) or {}
    sorts = [s for s in seen.get("sorts", []) if s in C.RBX_CHART_SORTS or s.startswith("trending-in-")]
    f["sorts"] = math.log1p(len(sorts))
    info["sorts"] = sorts
    try:
        import roblox_direct as RD
        ab = RD.abroad(state, gid, today)
    except Exception:
        ab = []
    f["abroad"] = math.log1p(len(ab))
    info["abroad"] = ab
    try:
        g = db.execute("SELECT creator_id FROM games WHERE uid=?", (gid,)).fetchone()
        best = W.creator_best(db, g["creator_id"], gid) if g and g["creator_id"] else 0
    except Exception:
        best = 0
    f["studio"] = math.log10(1 + best) / 2
    info["studio"] = best
    try:
        import events as EV
        evt = EV.event_of(state, r.get("name", ""))
    except Exception:
        evt = None
    f["event"] = 1.0 if evt else 0.0
    info["event"] = evt
    best_w, best_n = None, 0
    for w in ctx["keywords"](r.get("name", "")):
        n = theme_new.get(w, 0)
        if n > best_n:
            best_w, best_n = w, n
    f["wave"] = math.log1p(best_n)
    info["wave"] = (best_w, best_n)
    hr = ((state.get("hold") or {}).get(gid) or {}).get("rel")
    f["hold"] = (hr - 1) * 2 if hr else None
    info["hold"] = hr
    pt = ((state.get("badges") or {}).get(gid) or {}).get("playtime")
    f["playtime"] = math.log(pt / 20) if pt else None
    info["playtime"] = pt
    f["size"] = math.log10(players)
    age = ctx["age_days"](r, today) if r else None
    f["age"] = math.log10((age or 30) + 1)
    info["age"] = age
    return f, info


def reasons(contrib, info, fmt, n=3):
    """Plain-English reasons for the biggest positive contributions."""
    out = []
    for name, v in sorted(contrib.items(), key=lambda kv: -kv[1]):
        if v <= 0.05 or len(out) >= n + 1:
            break
        txt = None
        if name == "growth" and info.get("ratio"):
            txt = f"players ×{info['ratio']:.1f} vs last week"
        elif name == "accel" and info.get("cp"):
            txt = "growth just accelerated"
        elif name == "headroom" and info.get("peak"):
            import forecast as FC
            txt = f"forecast to reach ~{fmt(info['peak'])}" if FC.TRUST["peak"] else \
                f"forecast: {FC.rough(info['peak'], info.get('players') or 0)}"
        elif name == "promo" and info.get("promo"):
            txt = f"Roblox likely to push it ({info['promo'] * 100:.0f}%)"
        elif name == "breakout" and info.get("breakout"):
            txt = "looks like past breakouts"
        elif name == "heat" and info.get("heat"):
            txt = "buzzing across platforms"
        elif name in ("shorts_speed", "shorts_n") and info.get("sn"):
            txt = f"Shorts taking off ({fmt(info['svph'])} views/hour)" if info.get("svph", 0) >= 1000 else f"{info['sn']} new Shorts about it"
        elif name == "yt_views" and info.get("ytv"):
            txt = f"YouTube buzz ({fmt(info['ytv'])} views in 48h)"
        elif name == "sorts" and info.get("sorts"):
            nice = {"up-and-coming": "Up-and-Coming", "top-trending": "Top Trending", "fun-with-friends": "Fun with Friends",
                    "top-revisited": "Top Revisited"}
            names = [nice.get(s, s.replace("trending-in-", "Trending in ").replace("-and-", " & ").replace("-", " ").title())
                     for s in info["sorts"][:2]]
            txt = "on Roblox's " + " + ".join(names)
        elif name == "abroad" and info.get("abroad"):
            txt = f"charting abroad first ({len(info['abroad'])} countries)"
        elif name == "studio" and info.get("studio", 0) >= 5000:
            txt = f"studio has had a hit ({fmt(info['studio'])} peak)"
        elif name == "wave" and info.get("wave", (None, 0))[1]:
            txt = f"part of a wave (\"{info['wave'][0]}\", {info['wave'][1]} new games)"
        elif name == "hold" and info.get("hold"):
            txt = "players come back on weekdays"
        elif name == "playtime" and info.get("playtime"):
            txt = f"{info['playtime']:.0f} min played per player"
        if txt and txt not in out:
            out.append(txt)
    generic = "buzzing across platforms"
    if generic in out and len(out) > 1:  # prefer the specific reasons
        out.remove(generic)
        out.append(generic)
    return out[:n]


# ------------------------------------------------------------- scoring ---

def _apply_iso(cal, p):
    """Calibration: Platt scaling {"a", "b"} on the raw score's log-odds (smooth), capped to 1-97%."""
    if not cal:
        return max(0.01, min(0.97, p))
    if isinstance(cal, dict):
        z = math.log(max(p, 1e-6) / max(1 - p, 1e-6))
        return max(0.01, min(0.97, _sig(cal["a"] * z + cal["b"])))
    for ub, v in cal:  # older isotonic format
        if p <= ub:
            return max(0.01, min(0.97, v))
    return max(0.01, min(0.97, cal[-1][1]))


def platt(scores, labels, iters=2000, lr=0.05):
    """Fit p = sigmoid(a * logit(score) + b) on held-out predictions."""
    zs = [math.log(max(p, 1e-6) / max(1 - p, 1e-6)) for p in scores]
    a, b = 1.0, 0.0
    n = len(zs)
    for _ in range(iters):
        ga = gb = 0.0
        for z, y in zip(zs, labels):
            e = _sig(a * z + b) - y
            ga += e * z
            gb += e
        a -= lr * ga / n
        b -= lr * gb / n
    return {"a": a, "b": b}


def pav(scores, labels):
    """Isotonic regression (pool adjacent violators). Returns [(upper_bound, value)]."""
    pts = sorted(zip(scores, labels))
    blocks = []  # [sum_y, n, max_x]
    for x, y in pts:
        blocks.append([y, 1, x])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            a = blocks.pop()
            blocks[-1][0] += a[0]
            blocks[-1][1] += a[1]
            blocks[-1][2] = a[2]
    return [(b[2], b[0] / b[1]) for b in blocks]


def score_one(model, f):
    """(calibrated probability, contributions) for one feature dict."""
    if model:
        x = {k: (f.get(k) if f.get(k) is not None else model["median"].get(k, 0.0)) for k in model["names"]}
        raw = L.predict(model, x)
        contrib = {k: w * (x[k] - mu) / sd for k, w, mu, sd in zip(model["names"], model["w"], model["mu"], model["sd"])}
        return _apply_iso(model.get("iso"), raw), contrib
    contrib = {k: PRIOR[k] * (f.get(k) or 0.0) for k in NAMES}
    return _sig(PRIOR_BIAS + sum(contrib.values())), contrib


def _daily_value(r):
    return (r["sum_ccu"] / r["n"]) if r["n"] and r["n"] >= 3 else (r["peak"] or 0) * 0.75


def label(db, uid, day, players, target=None, sustain=None):
    """1 = took off: on `sustain`+ of the next 14 days it had at least max(2 x players, target). None = unknown."""
    target = C.TS_MIN_TARGET if target is None else target
    sustain = C.TS_SUSTAIN_DAYS if sustain is None else sustain
    lo, hi = _s(_d(day) + timedelta(days=1)), _s(_d(day) + timedelta(days=14))
    rows = db.execute("SELECT peak, sum_ccu, n FROM daily WHERE uid=? AND day>=? AND day<=? AND peak IS NOT NULL",
                      (uid, lo, hi)).fetchall()
    if len(rows) < 7:
        return None
    vals = sorted((_daily_value(r) for r in rows), reverse=True)
    return 1 if vals[min(sustain, len(vals)) - 1] >= max(2 * players, target) else 0


def labelled(db, today):
    """Every snapshot old enough to know its outcome: [{x, y, day, uid, players, shown}] oldest first."""
    rows = db.execute("SELECT day, uid, players, feats, score FROM trend_feats WHERE day<=?",
                      (_s(_d(today) - timedelta(days=14)),)).fetchall()
    ex = []
    for r in rows:
        y = label(db, r["uid"], r["day"], r["players"])
        if y is not None:
            ex.append({"x": json.loads(r["feats"]), "y": y, "day": r["day"], "uid": r["uid"], "players": r["players"],
                       "shown": r["score"]})
    ex.sort(key=lambda e: e["day"])
    return ex


def prior_score(f):
    """The hand-set starting formula's raw probability for one feature dict."""
    return _sig(PRIOR_BIAS + sum(PRIOR[k] * (f.get(k) or 0.0) for k in NAMES))


def calibrate_prior(db, today, ex=None):
    """Check the starting formula against real outcomes and fit its calibration curve.
    Stores and returns {"n", "pos", "days", "auc", "lo", "hi", "cal": {"a", "b"} or None}."""
    ex = labelled(db, today) if ex is None else ex
    n, pos = len(ex), sum(e["y"] for e in ex)
    out = {"n": n, "pos": pos, "days": len({e["day"] for e in ex}), "cal": None}
    if n >= 50 and 0 < pos < n:
        oof = [(prior_score(e["x"]), e["y"], e["uid"]) for e in ex]
        h = L.honest_metrics(oof)
        if h and h.get("auc") is not None:
            out.update({k: h[k] for k in ("auc", "lo", "hi", "base", "top") if k in h})
        if n >= C.TS_CAL_MIN_EXAMPLES and pos >= C.TS_CAL_MIN_POSITIVES and out["days"] >= C.TS_CAL_MIN_DAYS:
            out["cal"] = platt([o[0] for o in oof], [o[1] for o in oof])
    W.meta_set(db, "trend_prior", out)
    return out


def train(db, today, ex=None):
    """Fit the learned model and run its honest test. It is only USED when status['test_auc'] passes."""
    ex = labelled(db, today) if ex is None else ex
    n, pos = len(ex), sum(e["y"] for e in ex)
    ndays = len({e["day"] for e in ex})
    st = {"day": today, "examples": n, "positives": pos, "days": ndays, "trained": False}
    if n < C.TS_MIN_EXAMPLES or pos < C.TS_MIN_POSITIVES or pos == n or ndays < C.TS_MIN_DAYS:
        st["why"] = (f"needs {C.TS_MIN_EXAMPLES}+ outcomes with {C.TS_MIN_POSITIVES}+ take-offs over {C.TS_MIN_DAYS}+ days "
                     f"(has {n} / {pos} over {ndays} day{'s' if ndays != 1 else ''})")
        W.meta_set(db, "trend_status", st)
        W.meta_set(db, "trend_model", None)
        return st
    med = {k: (median([e["x"][k] for e in ex if e["x"].get(k) is not None]) if any(e["x"].get(k) is not None for e in ex) else 0.0)
           for k in NAMES}
    for e in ex:
        e["x"] = {k: (e["x"].get(k) if e["x"].get(k) is not None else med[k]) for k in NAMES}
    names = [k for k in NAMES if len({round(e["x"][k], 5) for e in ex}) > 1]
    model = L.fit(ex, names=names, iters=400, l2=0.02)
    model = L.attach_champion(model, ex, names, st, horizon=14, iters=400, l2=0.02)
    iso = None
    if model.get("oof") and 0 < sum(b for _, b in model["oof"]) < len(model["oof"]):
        iso = platt([a for a, _ in model["oof"]], [b for _, b in model["oof"]])   # calibrated on honest predictions only
    model["median"] = med
    model["iso"] = iso
    st["trained"] = True
    st["weights"] = dict(zip(model["names"], model["w"]))
    W.meta_set(db, "trend_model", model)
    W.meta_set(db, "trend_status", st)
    return st


def update(db, state, today, ids, ctx):
    """Score today's young games, save their snapshots, retrain. Sets state['_ts'] and state['ts']."""
    ensure(db)
    yday = _s(_d(today) - timedelta(days=1))
    theme_new = {}
    try:
        for r in db.execute("SELECT theme, new7 FROM theme_daily WHERE day=? AND theme LIKE 'w:%'", (yday,)):
            theme_new[r["theme"][2:]] = r["new7"] or 0
    except Exception:
        pass
    yts = ctx["S"].yt_stats(state, ctx["t"])
    prior = {}
    try:
        ex = labelled(db, today)
        prior = calibrate_prior(db, today, ex)
        st = train(db, today, [dict(e, x=dict(e["x"])) for e in ex])
    except Exception as e:
        print(f"trend score training failed: {e}")
        st = W.meta_get(db, "trend_status", {}) or {}
    model = W.meta_get(db, "trend_model")
    # the learned model must pass its honest test AND beat the starting formula it would replace
    trusted = bool(model) and (st.get("test_auc") or 0) >= max(C.MODEL_TRUST_AUC, (prior.get("auc") or 0) + C.GBM_MARGIN)
    cal = prior.get("cal")
    out, rows = {}, []
    yavg = {}
    for r in db.execute("SELECT uid, peak, sum_ccu, n FROM daily WHERE day=?", (yday,)):
        yavg[r["uid"]] = (r["sum_ccu"] / r["n"]) if r["n"] and r["n"] >= 3 else (r["peak"] or 0) * 0.75
    for gid in ids:
        r = state["games"].get(gid)
        if not r or r.get("last", 0) < C.TS_MIN_PLAYERS:
            continue
        f, info = features(state, db, gid, today, ctx, yts, theme_new)
        p, contrib = score_one(model if trusted else None, f)
        if not trusted and cal:
            p = _apply_iso(cal, p)      # starting formula, corrected to what its scores were really followed by
        out[gid] = {"score": round(100 * p), "reasons": reasons(contrib, info, ctx["fmt"]), "players": r.get("last", 0),
                    "event": info.get("event")}
        rows.append((today, gid, float(yavg.get(gid) or r.get("last", 0)), json.dumps(f), p))
    db.executemany("INSERT OR REPLACE INTO trend_feats VALUES(?,?,?,?,?)", rows)
    db.execute("DELETE FROM trend_feats WHERE day < ?", (_s(_d(today) - timedelta(days=C.TS_KEEP_DAYS)),))
    state["_ts"] = out
    state["ts"] = {u: v["score"] for u, v in out.items() if v["score"] >= 20}  # small, kept between runs for alerts
    state["ts_mode"] = "learned" if trusted else ("starting formula, calibrated" if cal else "starting formula")
    return len(out), st


def live_check(db, today):
    """How did the scores the bot actually SHOWED do? Uses snapshots 14-60 days old."""
    ex = [e for e in labelled(db, today) if e["day"] >= _s(_d(today) - timedelta(days=60)) and e["shown"] is not None]
    bands = {"50+": [], "25–49": [], "10–24": [], "under 10": []}
    for e in ex:
        s = 100 * e["shown"]
        bands["50+" if s >= 50 else "25–49" if s >= 25 else "10–24" if s >= 10 else "under 10"].append(e["y"])
    lab = [e["y"] for e in ex]
    if len(ex) < 50 or not (0 < sum(lab) < len(lab)):
        return {"n": len(ex)}
    return {"n": len(ex), "auc": L.auc([e["shown"] for e in ex], lab), "base": sum(lab) / len(lab),
            "bands": {b: (sum(v) / len(v), len(v)) for b, v in bands.items() if v}}


def weekly_lines(db, state, today):
    st = W.meta_get(db, "trend_status", {}) or {}
    pr = W.meta_get(db, "trend_prior", {}) or {}
    mode = state.get("ts_mode") or "starting formula"
    lines = [f"🚀 **Trend Score** — chance a young game at least doubles and passes {C.TS_MIN_TARGET:,} players within 2 weeks · "
             f"now using: **{mode}**"]
    if pr.get("auc") is not None:
        rng = f" (likely {pr['lo']:.2f}–{pr['hi']:.2f})" if pr.get("lo") is not None else ""
        lines.append(f"• Starting formula vs real outcomes: accuracy **{pr['auc']:.2f}**{rng} · its top 10% took off "
                     f"{pr['top'] * 100:.0f}% of the time vs {pr['base'] * 100:.1f}% for all · {pr['n']:,} snapshots over {pr['days']} days")
    elif pr.get("n"):
        lines.append(f"• Starting formula: {pr['n']:,} outcomes so far, {pr.get('pos', 0)} take-offs — too few to score it yet")
    if st.get("trained"):
        lines.append("• Learned model — " + L.honest_line(st, "take-offs"))
        cl = L.champion_line(st)
        if cl:
            lines.append("  " + cl)
        if mode != "learned":
            lines.append("  Not used yet: it has to pass that test and beat the starting formula first.")
    else:
        lines.append(f"• Learned model: not trained yet — {st.get('why', 'collecting outcomes')}")
    lc = live_check(db, today)
    if lc.get("bands"):
        lines.append("• Scores as shown at the time: " + " · ".join(
            f"{b}: {v[0] * 100:.0f}% took off ({v[1]})" for b, v in lc["bands"].items()))
    return lines

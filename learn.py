"""
The learning part: predicts which young games will explode.

How it works, in plain terms:
  1. For every game in the database, find the day it first reached LEARN_ENTRY_CCU
     players (the moment the bot would first notice it). Call that day 0.
  2. Describe the game as it looked at the end of day 1 (its "features"): how many
     players on day 0 and day 1, how fast it grew, visits gained, whether it was
     still climbing late in the day, how old it was, whether its studio has had a
     hit before, how crowded its mechanic is...
  3. Check what happened next (its "label"): did it reach EXPLODE_CCU players
     within LABEL_DAYS days?
  4. Fit a logistic regression (a simple, explainable model) on all past examples,
     test it on the most recent ones it didn't train on, and report how accurate it
     is. Then score today's young games: "X% chance this explodes".

Pure Python, no extra libraries. Retrains once a day.
"""
import math
from datetime import datetime, timedelta

import config as C
import insights as I
import warehouse as W

FEATURES = [
    ("players_d0", "players on the day it was first noticed"),
    ("players_d1", "players the day after"),
    ("growth_d1", "growth from day 0 to day 1"),
    ("visits_d1", "visits gained on day 1"),
    ("visits_missing", "(no visit data)"),
    ("late_climb", "still climbing late on day 1"),
    ("late_missing", "(no hourly data)"),
    ("age", "game age when noticed"),
    ("weekend", "noticed on a weekend"),
    ("studio_best", "studio's best previous game"),
    ("crowd", "copies in the same mechanic in the 2 weeks before"),
    ("mech_hits", "same-mechanic games that exploded in the month before"),
]


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def _log10(v):
    return math.log10(max(v, 1))


# ------------------------------------------------------------- dataset ---

def _game_rows(db):
    games = {r["uid"]: dict(r) for r in db.execute("SELECT * FROM games")}
    daily = {}
    for r in db.execute("SELECT uid, day, peak, visits FROM daily WHERE peak IS NOT NULL ORDER BY day"):
        daily.setdefault(r["uid"], {})[r["day"]] = (r["peak"], r["visits"])
    return games, daily


def _entry(days, created):
    """Day the game first reached the entry level, only if we actually saw it cross."""
    ds = sorted(days)
    for i, d in enumerate(ds):
        if days[d][0] >= C.LEARN_ENTRY_CCU:
            prev_ok = i > 0 and days[ds[i - 1]][0] < C.LEARN_ENTRY_CCU and (_d(d) - _d(ds[i - 1])).days == 1
            new_ok = created is not None and (_d(d) - _d(created)).days <= 2
            return d if (prev_ok or new_ok) else None
    return None


def _late_climb(db, uid, day):
    rows = [r["ccu"] for r in db.execute("SELECT ccu FROM hourly WHERE uid=? AND hour LIKE ? ORDER BY hour",
                                         (uid, day + "%"))]
    if len(rows) < 12:
        return None
    first, last = sum(rows[:6]) / 6, sum(rows[-6:]) / 6
    return math.log2(max(last, 1) / max(first, 1))


def build_examples(db, today, for_prediction=False):
    """Returns list of dicts {uid, t0, x: {feature: value}, y: 0/1/None, players_now}."""
    games, daily = _game_rows(db)
    entries = {}
    for uid, days in daily.items():
        g = games.get(uid) or {}
        created = g.get("created")
        t0 = _entry(days, created)
        if not t0:
            continue
        age = (_d(t0) - _d(created)).days if created else None
        if age is not None and age > C.LEARN_MAX_AGE_DAYS:
            continue
        entries[uid] = (t0, age)

    # crowding + mechanic hit history
    mech_of = {uid: I.mechanics_of((games.get(uid) or {}).get("name") or "") for uid in entries}
    exploded_day = {}
    for uid, days in daily.items():
        for d in sorted(days):
            if days[d][0] >= C.EXPLODE_CCU:
                exploded_day[uid] = d
                break

    out = []
    for uid, (t0, age) in entries.items():
        days = daily[uid]
        d1 = _s(_d(t0) + timedelta(days=1))
        if d1 not in days or d1 >= today:
            continue  # decision day not finished yet
        p0, v0 = days[t0]
        p1, v1 = days[d1]
        if p1 >= C.EXPLODE_CCU:
            continue  # already exploded by decision time: nothing to predict
        # label
        end = _s(_d(t0) + timedelta(days=C.LABEL_DAYS))
        window = [days[d][0] for d in days if t0 <= d <= end]
        hit = max(window) >= C.EXPLODE_CCU
        complete = end < today
        if for_prediction:
            if hit or (_d(today) - _d(d1)).days > C.PREDICT_MAX_DAYS_AFTER:
                continue
            y = None
        else:
            if not hit and not complete:
                continue
            y = 1 if hit else 0
        g = games.get(uid) or {}
        mechs = mech_of.get(uid) or []
        lo = _s(_d(t0) - timedelta(days=14))
        crowd = sum(1 for u, (t, _) in entries.items() if u != uid and lo <= t < t0
                    and set(mech_of.get(u) or []) & set(mechs)) if mechs else 0
        lo30 = _s(_d(t0) - timedelta(days=30))
        mhits = sum(1 for u, d in exploded_day.items() if u != uid and lo30 <= d < t0
                    and set(I.mechanics_of((games.get(u) or {}).get("name") or "")) & set(mechs)) if mechs else 0
        late = _late_climb(db, uid, d1)
        vis = (v1 - v0) if (v0 is not None and v1 is not None and v1 >= v0) else None
        sb = W.creator_best(db, g.get("creator_id"), uid, t0)
        x = {
            "players_d0": _log10(p0), "players_d1": _log10(p1),
            "growth_d1": math.log2(max(p1, 1) / max(p0, 1)),
            "visits_d1": _log10(vis) if vis else 0.0, "visits_missing": 0.0 if vis else 1.0,
            "late_climb": late if late is not None else 0.0, "late_missing": 0.0 if late is not None else 1.0,
            "age": _log10((age or 0) + 1), "weekend": 1.0 if _d(t0).weekday() >= 5 else 0.0,
            "studio_best": _log10(sb), "crowd": math.log1p(crowd), "mech_hits": math.log1p(mhits),
        }
        out.append({"uid": uid, "name": g.get("name") or uid, "t0": t0, "x": x, "y": y,
                    "players": max(days[d][0] for d in days if d >= t0)})
    out.sort(key=lambda e: e["t0"])
    return out


# --------------------------------------------------------------- model ---

def _sigmoid(z):
    return 1 / (1 + math.exp(-max(-30, min(30, z))))


def fit(examples, l2=None, iters=None, lr=0.3, names=None):
    l2 = C.LEARN_L2 if l2 is None else l2
    iters = iters or 600
    names = names or [f for f, _ in FEATURES]
    X = [[e["x"][f] for f in names] for e in examples]
    y = [e["y"] for e in examples]
    n, k = len(X), len(names)
    mu = [sum(r[j] for r in X) / n for j in range(k)]
    sd = [math.sqrt(sum((r[j] - mu[j]) ** 2 for r in X) / n) or 1.0 for j in range(k)]
    Z = [[(r[j] - mu[j]) / sd[j] for j in range(k)] for r in X]
    pos = sum(y) or 1
    neg = (n - sum(y)) or 1
    wpos, wneg = n / (2 * pos), n / (2 * neg)  # balance rare explosions
    w, b = [0.0] * k, 0.0
    for _ in range(iters):
        gw, gb = [0.0] * k, 0.0
        for zi, yi in zip(Z, y):
            p = _sigmoid(b + sum(wj * zj for wj, zj in zip(w, zi)))
            err = (p - yi) * (wpos if yi else wneg)
            gb += err
            for j in range(k):
                gw[j] += err * zi[j]
        b -= lr * gb / n
        for j in range(k):
            w[j] -= lr * (gw[j] / n + l2 * w[j])
    # undo class balancing in the intercept so outputs are real-world probabilities
    prior = pos / n
    b += math.log(prior / (1 - prior)) if 0 < prior < 1 else 0
    return {"names": names, "mu": mu, "sd": sd, "w": w, "b": b, "n": n, "pos": int(sum(y))}


def predict(model, x):
    z = model["b"] + sum(w * (x[f] - m) / s for f, w, m, s in zip(model["names"], model["w"], model["mu"], model["sd"]))
    return _sigmoid(z)


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def train(db, today):
    """Train, evaluate on the newest 25%, then refit on everything. Stores the model in the DB."""
    ex = build_examples(db, today)
    n, pos = len(ex), sum(e["y"] for e in ex)
    status = {"examples": n, "positives": pos, "trained": False, "day": today}
    if n < C.LEARN_MIN_EXAMPLES or pos < C.LEARN_MIN_POSITIVES:
        status["why"] = (f"needs {C.LEARN_MIN_EXAMPLES}+ examples with {C.LEARN_MIN_POSITIVES}+ explosions "
                         f"(has {n} / {pos})")
        W.meta_set(db, "model_status", status)
        return status
    cut = int(n * 0.75)
    tr, te = ex[:cut], ex[cut:]
    if sum(e["y"] for e in tr) >= 3 and 0 < sum(e["y"] for e in te) < len(te):
        m = fit(tr)
        scores = [predict(m, e["x"]) for e in te]
        labels = [e["y"] for e in te]
        status["test_auc"] = auc(scores, labels)
        status["test_n"], status["test_pos"] = len(te), sum(labels)
        k = max(1, len(te) // 10)
        top = sorted(zip(scores, labels), reverse=True)[:k]
        status["test_top10_hit"] = sum(l for _, l in top) / k
        status["base_rate"] = sum(labels) / len(labels)
        flagged = [(s, l) for s, l in zip(scores, labels) if s >= C.PREDICT_ALERT_PROB]
        status["test_flagged"] = len(flagged)
        status["test_flagged_hit"] = (sum(l for _, l in flagged) / len(flagged)) if flagged else None
    model = fit(ex)
    status["trained"] = True
    status["drivers"] = sorted(((f, w) for f, w in zip(model["names"], model["w"])), key=lambda x: -abs(x[1]))[:6]
    W.meta_set(db, "model", model)
    W.meta_set(db, "model_status", status)
    return status


def predictions(db, today):
    model = W.meta_get(db, "model")
    if not model:
        return []
    out = []
    for e in build_examples(db, today, for_prediction=True):
        p = predict(model, e["x"])
        out.append((p, e))
        db.execute("""INSERT INTO predictions(day, uid, prob, players, model) VALUES(?,?,?,?,?)
                      ON CONFLICT(day, uid) DO UPDATE SET prob=excluded.prob, players=excluded.players""",
                   (today, e["uid"], p, e["players"], W.meta_get(db, "model_status", {}).get("day")))
    out.sort(key=lambda x: -x[0])
    return out


# ------------------------------------------------------------ scorecard ---

def _outcome(db, uid, day, players_at):
    end = _s(_d(day) + timedelta(days=C.LABEL_DAYS))
    r = db.execute("SELECT MAX(peak) AS m FROM daily WHERE uid=? AND day>? AND day<=?", (uid, day, end)).fetchone()
    peak = r["m"] or 0
    return peak >= C.EXPLODE_CCU, peak


def scorecard(db, today):
    """How often each kind of alert (and the model) was followed by an explosion."""
    rows = {}
    seen = set()
    for a in db.execute("SELECT * FROM alerts ORDER BY ts"):
        if (a["players"] or 0) >= C.EXPLODE_CCU or (a["kind"], a["uid"]) in seen:
            continue
        seen.add((a["kind"], a["uid"]))
        hit, _ = _outcome(db, a["uid"], a["day"], a["players"])
        done = _s(_d(a["day"]) + timedelta(days=C.LABEL_DAYS)) < today
        r = rows.setdefault(a["kind"], {"hit": 0, "miss": 0, "pending": 0})
        if hit:
            r["hit"] += 1
        elif done:
            r["miss"] += 1
        else:
            r["pending"] += 1
    seen = set()
    for p in db.execute("SELECT * FROM predictions ORDER BY day"):
        if p["uid"] in seen or (p["players"] or 0) >= C.EXPLODE_CCU:
            continue
        seen.add(p["uid"])
        kind = "model ≥ {:.0f}%".format(C.PREDICT_ALERT_PROB * 100) if p["prob"] >= C.PREDICT_ALERT_PROB \
            else "model < {:.0f}%".format(C.PREDICT_ALERT_PROB * 100)
        hit, _ = _outcome(db, p["uid"], p["day"], p["players"])
        done = _s(_d(p["day"]) + timedelta(days=C.LABEL_DAYS)) < today
        r = rows.setdefault(kind, {"hit": 0, "miss": 0, "pending": 0})
        if hit:
            r["hit"] += 1
        elif done:
            r["miss"] += 1
        else:
            r["pending"] += 1
    return rows


LABELS = {"new": "🆕 crossed 2K", "surge": "🚀 surge", "copy": "🧬 copy wave", "heat": "🔥 heat",
          "early": "👀 early warning", "breakout": "💥 breakout", "predict": "🎯 prediction"}


def report_lines(db, today, fmt):
    st = W.meta_get(db, "model_status", {}) or {}
    lines = [f"🧠 **What the model has learned** (explode = {fmt(C.EXPLODE_CCU)}+ players within {C.LABEL_DAYS} days)"]
    if not st.get("trained"):
        lines.append(f"• Still collecting examples — {st.get('why', 'not trained yet')}.")
    else:
        lines.append(f"• Trained on {st['examples']} young games, {st['positives']} of which exploded.")
        if st.get("test_auc") is not None:
            lines.append(f"• Tested on the newest {st['test_n']} games it hadn't seen: ranking accuracy (AUC) "
                         f"**{st['test_auc']:.2f}** (0.5 = coin flip, 1.0 = perfect). Its top 10% picks exploded "
                         f"**{st['test_top10_hit']*100:.0f}%** of the time vs {st['base_rate']*100:.0f}% for a random young game.")
        names = dict(FEATURES)
        drv = ", ".join(f"{names[f]} ({'+' if w > 0 else '−'})" for f, w in st.get("drivers", [])[:4])
        if drv:
            lines.append(f"• Biggest drivers: {drv}")
    sc = scorecard(db, today)
    lines += ["", f"🎯 **Scorecard: how often signals were followed by an explosion**"]
    if sc:
        for kind, r in sorted(sc.items(), key=lambda kv: -(kv[1]["hit"] + kv[1]["miss"])):
            done = r["hit"] + r["miss"]
            rate = f"**{r['hit']}/{done}** ({r['hit']/done*100:.0f}%)" if done else "—"
            lines.append(f"• {LABELS.get(kind, kind)}: {rate}" + (f" · {r['pending']} still in their {C.LABEL_DAYS}-day window" if r["pending"] else ""))
    else:
        lines.append("• Nothing to score yet")
    return lines

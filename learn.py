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

Retrains once a day.

Champion / challenger (every model in the bot uses this, via attach_champion):
  The simple logistic regression is always trained — it explains WHY (the bars and reasons).
  A gradient-boosted tree model (scikit-learn, free) challenges it: trees catch thresholds and
  combinations ("young AND same-mechanic hits AND climbing late") a straight line can't.
  Both are judged by walk-forward testing — train on the past, predict the next slice of time, slide
  forward, repeat — the same way they're used live. The trees only take over when they beat the
  simple model on that test by a clear margin; otherwise nothing changes.
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
            if not complete:
                continue  # wait for the full window either way: early explosions alone inflated the hit rate
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


def _np():
    try:
        import numpy as np
        return np
    except ImportError:
        return None


def fit_matrix(Xa, ya, l2, iters, lr=0.3):
    """Class-balanced, standardised logistic regression on numpy arrays. Returns (w, b, mu, sd) as lists/floats."""
    np = _np()
    n, k = Xa.shape
    mu = Xa.mean(axis=0)
    sd = Xa.std(axis=0)
    sd[sd == 0] = 1.0
    Za = (Xa - mu) / sd
    pos = float(ya.sum()) or 1.0
    neg = float(n - ya.sum()) or 1.0
    cw = np.where(ya > 0, n / (2 * pos), n / (2 * neg))   # balance rare positives
    wa, b = np.zeros(k), 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(b + Za @ wa, -30, 30)))
        err = (p - ya) * cw
        b -= lr * err.sum() / n
        wa -= lr * (Za.T @ err / n + l2 * wa)
    prior = float(ya.sum()) / n
    if 0 < prior < 1:   # undo class balancing in the intercept so outputs are real-world probabilities
        b += math.log(prior / (1 - prior))
    return wa.tolist(), float(b), mu.tolist(), sd.tolist()


def fit(examples, l2=None, iters=None, lr=0.3, names=None):
    l2 = C.LEARN_L2 if l2 is None else l2
    iters = iters or 600
    names = names or [f for f, _ in FEATURES]
    X = [[e["x"][f] for f in names] for e in examples]
    y = [e["y"] for e in examples]
    n, k = len(X), len(names)
    np = _np()
    if np is not None:   # same maths with numpy when it's there (~100x faster); pure Python otherwise
        w, b, mu, sd = fit_matrix(np.array(X, dtype=float).reshape(n, k), np.array(y, dtype=float), l2, iters, lr)
        return {"names": names, "mu": mu, "sd": sd, "w": w, "b": b, "n": n, "pos": int(sum(y))}
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
    prior = sum(y) / n
    b += math.log(prior / (1 - prior)) if 0 < prior < 1 else 0
    return {"names": names, "mu": mu, "sd": sd, "w": w, "b": b, "n": n, "pos": int(sum(y))}


def predict(model, x):
    if model.get("gbm"):
        p = _gbm_predict(model, x)
        if p is not None:
            return p
    z = model["b"] + sum(w * (x[f] - m) / s for f, w, m, s in zip(model["names"], model["w"], model["mu"], model["sd"]))
    return _sigmoid(z)


# ------------------------------------------------------ champion / challenger ---

_GBM_CACHE = {}


def _gbm_new():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=C.GBM_TREES, learning_rate=0.05, max_leaf_nodes=15,
                                          min_samples_leaf=C.GBM_MIN_LEAF, l2_regularization=1.0, random_state=7)


def _matrix(examples, names):
    return [[float(e["x"].get(f) if e["x"].get(f) is not None else float("nan")) for f in names] for e in examples]


def _gbm_predict(model, x):
    try:
        key = model["gbm"][:64] + str(len(model["gbm"]))
        clf = _GBM_CACHE.get(key)
        if clf is None:
            import base64
            import pickle
            clf = _GBM_CACHE[key] = pickle.loads(base64.b64decode(model["gbm"]))
        row = [[float(x.get(f) if x.get(f) is not None else float("nan")) for f in model["gbm_names"]]]
        return float(clf.predict_proba(row)[0][1])
    except Exception:
        return None   # library missing or model unreadable -> the simple model answers


def brier(scores, labels):
    return sum((s - l) ** 2 for s, l in zip(scores, labels)) / len(labels) if labels else None


def auc(scores, labels):
    """Ranking accuracy: chance a random positive is scored above a random negative (ties count half)."""
    np = _np()
    if np is not None and len(scores) >= 64:
        s = np.asarray(scores, dtype=float)
        y = np.asarray(labels) > 0
        npos = int(y.sum())
        nneg = len(y) - npos
        if not npos or not nneg:
            return None
        _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
        avg_rank = np.cumsum(cnt) - (cnt - 1) / 2.0
        r = avg_rank[inv]
        return float((r[y].sum() - npos * (npos + 1) / 2.0) / (npos * nneg))
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


# --------------------------------------------------------- honest testing ---
#
# Every model here predicts something that takes days to find out (7, 14 or 21). Two traps follow:
#   1. LEAKAGE. A game scored on Monday and again on Tuesday has almost the same next-7-days. If Monday is
#      in the training set and Tuesday in the test set, the model is being marked on answers it has seen.
#      So a test block may only be predicted by a model trained on examples whose outcome was ALREADY KNOWN
#      when that block began (their day + the outcome window is before the block). That gap is the "purge".
#   2. NOISE. A model that scores 0.70 against 0.67 on a few hundred predictions has not shown it is
#      better. Accuracy gets a range from resampling whole games (a game's repeated days move together),
#      and a challenger only takes over when it wins in nearly all resamples.

def _day_of(e):
    return e.get("day") or e.get("t0")


def _group_of(e):
    return e.get("uid") or e.get("theme") or e.get("group") or _day_of(e)


def purged_folds(examples, horizon, folds=None, min_train_days=None, test_from=None):
    """[(train, test)] in time order. Each test block is a run of days; its training set is every example
    whose outcome window (day + horizon) had closed before the block started.
    test_from: only days on/after this are ever TESTED on (training may still use earlier ones) - used to
    test only on games the bot watched live, never on downloaded survivors-only history."""
    folds = folds or C.WF_FOLDS
    min_train_days = C.WF_MIN_TRAIN_DAYS if min_train_days is None else min_train_days
    days = sorted({_day_of(e) for e in examples})
    if len(days) < 3:
        return []
    first_test = _s(_d(days[0]) + timedelta(days=horizon + min_train_days))
    if test_from and test_from > first_test:
        first_test = test_from
    tdays = [d for d in days if d >= first_test]
    if len(tdays) < 2:
        return []
    size = max(1, math.ceil(len(tdays) / folds))
    out = []
    for i in range(0, len(tdays), size):
        block = tdays[i:i + size]
        cut = _s(_d(block[0]) - timedelta(days=horizon))
        tr = [e for e in examples if _day_of(e) < cut]
        te = [e for e in examples if block[0] <= _day_of(e) <= block[-1]]
        if te and len({e["y"] for e in tr}) == 2 and sum(e["y"] for e in tr) >= C.WF_MIN_TRAIN_POS:
            out.append((tr, te))
    return out


def _boot_groups(groups, rounds, seed=7):
    """Index arrays for cluster-bootstrap resamples (whole groups drawn with replacement)."""
    np = _np()
    rng = np.random.default_rng(seed)
    idx = {}
    for i, g in enumerate(groups):
        idx.setdefault(g, []).append(i)
    members = [np.array(v) for v in idx.values()]
    for _ in range(rounds):
        pick = rng.integers(0, len(members), len(members))
        yield np.concatenate([members[j] for j in pick])


def honest_metrics(oof, top_share=0.1):
    """oof: [(score, y, group)] from purged walk-forward. AUC with a 90% range, and top-picks hit rate vs base."""
    if not oof:
        return None
    sc, lab, grp = [o[0] for o in oof], [o[1] for o in oof], [o[2] for o in oof]
    n, pos = len(sc), sum(lab)
    if pos < C.HONEST_MIN_POS or pos == n:
        return {"n": n, "pos": pos, "auc": None}
    k = max(1, int(n * top_share))
    top = sorted(zip(sc, lab), key=lambda x: -x[0])[:k]
    out = {"n": n, "pos": pos, "auc": auc(sc, lab), "base": pos / n, "top": sum(l for _, l in top) / k, "top_n": k}
    np = _np()
    if np is not None and len(set(grp)) >= 20:
        s, y = np.asarray(sc, dtype=float), np.asarray(lab)
        vals = []
        for ix in _boot_groups(grp, C.BOOT_ROUNDS):
            a = auc(s[ix], y[ix])
            if a is not None:
                vals.append(a)
        if len(vals) >= 20:
            vals.sort()
            out["lo"], out["hi"] = vals[int(0.05 * len(vals))], vals[min(len(vals) - 1, int(0.95 * len(vals)))]
    return out


def p_better(oof_a, oof_b):
    """How sure are we that model B ranks better than model A on the same test predictions?
    Returns (share of resamples where B wins, mean AUC difference)."""
    np = _np()
    if np is None or not oof_a or len(oof_a) != len(oof_b):
        return None, None
    y = np.asarray([o[1] for o in oof_a])
    a, b = np.asarray([o[0] for o in oof_a], dtype=float), np.asarray([o[0] for o in oof_b], dtype=float)
    wins, diffs = 0, []
    for ix in _boot_groups([o[2] for o in oof_a], C.BOOT_ROUNDS):
        ua, ub = auc(a[ix], y[ix]), auc(b[ix], y[ix])
        if ua is None or ub is None:
            continue
        diffs.append(ub - ua)
        wins += ub > ua
    if not diffs:
        return None, None
    return wins / len(diffs), sum(diffs) / len(diffs)


def walk_forward(examples, names, lr_kw, horizon=0, want_gbm=True, folds=None, test_from=None):
    """Purged, time-ordered test of the simple model (and boosted trees).
    Returns {'oof': {'lr': [(score, y, group)], 'gbm': [...]}, 'folds': n, 'horizon': days}."""
    oof = {"lr": [], "gbm": []}
    have_gbm = False
    if want_gbm:
        try:
            import sklearn  # noqa: F401
            have_gbm = True
        except ImportError:
            pass
    fs = purged_folds(examples, horizon, folds, test_from=test_from)
    for tr, te in fs:
        m = fit(tr, names=names, **lr_kw)
        oof["lr"] += [(predict(m, e["x"]), e["y"], _group_of(e)) for e in te]
        if have_gbm:
            clf = _gbm_new().fit(_matrix(tr, names), [e["y"] for e in tr])
            ps = clf.predict_proba(_matrix(te, names))[:, 1].tolist()
            oof["gbm"] += [(p, e["y"], _group_of(e)) for p, e in zip(ps, te)]
    return {"oof": oof, "folds": len(fs), "horizon": horizon}


def attach_champion(model, examples, names, status, horizon=0, test_from=None, **lr_kw):
    """The honest check and the champion/challenger choice, in one place for every model.

    Runs the purged walk-forward test, stores the champion's honest numbers in status['honest'] (and the
    legacy status['test_auc'] etc. that reports and trust gates read), and — only if boosted trees beat the
    simple model in nearly all resamples — stores the trees in `model` so predict() uses them.
    `examples` must be oldest-first and carry 'day' (or 't0'); 'uid'/'theme' is used to resample by game."""
    n, pos = len(examples), sum(e["y"] for e in examples)
    for k in ("test_auc", "honest", "wf", "champion_why"):
        status.pop(k, None)
    status["champion"] = "simple"
    model.pop("gbm", None)
    want_gbm = n >= C.GBM_MIN_EXAMPLES and pos >= C.GBM_MIN_POSITIVES and pos < n
    try:
        wf = walk_forward(examples, names, lr_kw, horizon, want_gbm, test_from=test_from)
    except Exception as e:
        status["champion_why"] = f"walk-forward failed: {e}"
        return model
    lr, gb = honest_metrics(wf["oof"]["lr"]), honest_metrics(wf["oof"]["gbm"])
    status["wf"] = {"folds": wf["folds"], "horizon": horizon, "test_from": test_from,
                    **{k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                       for k, v in (("lr", lr), ("gbm", gb)) if v}}
    best, kind = lr, "lr"
    if gb and lr and gb.get("auc") is not None and lr.get("auc") is not None:
        pb, diff = p_better(wf["oof"]["lr"], wf["oof"]["gbm"])
        status["wf"]["p_trees_better"], status["wf"]["diff"] = (round(pb, 3) if pb is not None else None,
                                                                round(diff, 4) if diff is not None else None)
        if pb is not None and pb >= C.GBM_MIN_CONFIDENCE and diff >= C.GBM_MARGIN and gb["auc"] >= C.GBM_MIN_AUC:
            import base64
            import pickle
            clf = _gbm_new().fit(_matrix(examples, names), [e["y"] for e in examples])
            model["gbm"] = base64.b64encode(pickle.dumps(clf)).decode()
            model["gbm_names"] = list(names)
            status["champion"] = "boosted trees"
            best, kind = gb, "gbm"
    model["oof"] = [(o[0], o[1]) for o in wf["oof"][kind][-3000:]]
    if best and best.get("auc") is not None:
        status["honest"] = best
        status["test_auc"] = best["auc"]
    elif best:
        status["honest"] = best   # counts only: not enough positives to score
    return model


def honest_line(status, what="positives"):
    """One report line: the honest accuracy with its range, or why there isn't one yet."""
    h = (status or {}).get("honest")
    wf = (status or {}).get("wf") or {}
    if not h:
        tf = wf.get("test_from")
        if tf and wf.get("horizon") is not None:
            first = _s(_d(tf) + timedelta(days=int(wf["horizon"]) + 1))
            return (f"Honest test: not possible yet — it is run only on games the bot watched from the start ({tf} on), and "
                    f"their {wf['horizon']}-day outcomes only began finishing on {first}. It needs {C.HONEST_MIN_POS}+ {what} among them.")
        return (f"Honest test: not possible yet — it needs enough history to train only on outcomes that were "
                f"already known ({wf.get('horizon', '?')}-day outcomes).")
    if h.get("auc") is None:
        return (f"Honest test: too few {what} in the test window to score ({h['pos']} of {h['n']:,}; "
                f"needs {C.HONEST_MIN_POS}+). Treat this model's picks as unproven.")
    rng = f" (likely between {h['lo']:.2f} and {h['hi']:.2f})" if h.get("lo") is not None else ""
    return (f"Honest test: accuracy **{h['auc']:.2f}**{rng} · 0.5 = coin flip · top 10% picks came true "
            f"**{h['top'] * 100:.0f}%** of the time vs {h['base'] * 100:.0f}% for all · {h['n']:,} predictions, "
            f"each made by a model trained only on outcomes already known at the time")


def champion_line(status):
    """One line for reports: which model won the honest test and how sure that is."""
    wf = (status or {}).get("wf") or {}
    lr, gb = wf.get("lr"), wf.get("gbm")
    if not lr or lr.get("auc") is None:
        return None
    if not gb or gb.get("auc") is None:
        return None
    pb = wf.get("p_trees_better")
    sure = f"trees better in {pb * 100:.0f}% of resamples" if pb is not None else "not comparable"
    if status.get("champion") == "boosted trees":
        return f"⚙️ Using **boosted trees**: {gb['auc']:.2f} vs {lr['auc']:.2f} for the simple model ({sure})"
    return (f"⚙️ Simple model kept: {lr['auc']:.2f} vs {gb['auc']:.2f} for boosted trees "
            f"({sure}; they need {C.GBM_MIN_CONFIDENCE * 100:.0f}%+ and a {C.GBM_MARGIN:.2f}+ lead)")


def coef_stability(examples, names, rounds=None, **lr_kw):
    """Are the simple model's weights real or noise? Refit on resampled games and see how much each moves.
    Returns {feature: {"w": weight on all data, "lo", "hi": 90% range, "sign": share of resamples agreeing
    with the sign of w}} — or {} without numpy."""
    np = _np()
    if np is None or len(examples) < 100:
        return {}
    rounds = rounds or C.COEF_BOOT_ROUNDS
    l2 = lr_kw.get("l2", C.LEARN_L2)
    iters = lr_kw.get("iters") or 600
    X = np.array([[e["x"][f] for f in names] for e in examples], dtype=float)
    y = np.array([e["y"] for e in examples], dtype=float)
    w0, _, _, _ = fit_matrix(X, y, l2, iters)
    ws = []
    for ix in _boot_groups([_group_of(e) for e in examples], rounds, seed=11):
        if 0 < y[ix].sum() < len(ix):
            ws.append(fit_matrix(X[ix], y[ix], l2, iters)[0])
    if len(ws) < 10:
        return {}
    W_ = np.array(ws)
    out = {}
    for j, f in enumerate(names):
        col = np.sort(W_[:, j])
        out[f] = {"w": float(w0[j]), "lo": float(col[int(0.05 * len(col))]), "hi": float(col[min(len(col) - 1, int(0.95 * len(col)))]),
                  "sign": float((np.sign(W_[:, j]) == np.sign(w0[j])).mean()) if w0[j] else 0.0}
    return out


def train(db, today):
    """Fit on every finished example, and test honestly (walk-forward, trained only on outcomes already known)."""
    ex = build_examples(db, today)
    n, pos = len(ex), sum(e["y"] for e in ex)
    status = {"examples": n, "positives": pos, "trained": False, "day": today}
    if n < C.LEARN_MIN_EXAMPLES or pos < C.LEARN_MIN_POSITIVES:
        status["why"] = (f"needs {C.LEARN_MIN_EXAMPLES}+ examples with {C.LEARN_MIN_POSITIVES}+ explosions "
                         f"(has {n} / {pos})")
        W.meta_set(db, "model_status", status)
        return status
    model = fit(ex)
    live = W.live_start(db)
    status["live_examples"] = sum(1 for e in ex if live and e["t0"] >= live)
    status["live_positives"] = sum(e["y"] for e in ex if live and e["t0"] >= live)
    # Trained on everything, but TESTED only on games first noticed while the bot was watching: the
    # downloaded history holds survivors only, and a model marked on survivors flatters itself.
    model = attach_champion(model, ex, model["names"], status, horizon=C.LABEL_DAYS, test_from=live)
    h = status.get("honest") or {}
    status["test_n"], status["test_pos"] = h.get("n"), h.get("pos")
    status["test_top10_hit"], status["base_rate"] = h.get("top"), h.get("base", pos / n)
    status["trained"] = True
    status["drivers"] = sorted(((f, w) for f, w in zip(model["names"], model["w"])), key=lambda x: -abs(x[1]))[:6]
    try:
        stab = coef_stability(ex, model["names"])
        status["stable"] = [f for f, v in stab.items() if v["sign"] >= 0.9]
    except Exception:
        status["stable"] = []
    W.meta_set(db, "model", model)
    W.meta_set(db, "model_status", status)
    return status


def trusted(status):
    """A model's predictions are only used (board, alerts, other models) once its honest test passes."""
    return bool(status) and (status.get("test_auc") or 0) >= C.MODEL_TRUST_AUC


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
        r = rows.setdefault(a["kind"], {"hit": 0, "miss": 0, "pending": 0, "early": 0})
        # Only alerts whose 21-day window has ENDED are scored: counting early explosions before the
        # misses are known made every signal look 100% right.
        if done:
            r["hit" if hit else "miss"] += 1
        else:
            r["pending"] += 1
            r["early"] += 1 if hit else 0
    seen = set()
    for p in db.execute("SELECT * FROM predictions ORDER BY day"):
        if p["uid"] in seen or (p["players"] or 0) >= C.EXPLODE_CCU:
            continue
        seen.add(p["uid"])
        kind = "model ≥ {:.0f}%".format(C.PREDICT_ALERT_PROB * 100) if p["prob"] >= C.PREDICT_ALERT_PROB \
            else "model < {:.0f}%".format(C.PREDICT_ALERT_PROB * 100)
        hit, _ = _outcome(db, p["uid"], p["day"], p["players"])
        done = _s(_d(p["day"]) + timedelta(days=C.LABEL_DAYS)) < today
        r = rows.setdefault(kind, {"hit": 0, "miss": 0, "pending": 0, "early": 0})
        if done:
            r["hit" if hit else "miss"] += 1
        else:
            r["pending"] += 1
            r["early"] += 1 if hit else 0
    return rows


LABELS = {"new": "🆕 crossed 2K", "surge": "🚀 surge", "copy": "🧬 copy wave", "heat": "🔥 heat",
          "early": "👀 early warning", "breakout": "💥 breakout", "predict": "🎯 prediction"}


def report_lines(db, today, fmt):
    st = W.meta_get(db, "model_status", {}) or {}
    lines = [f"🧠 **Explosion model** (explode = {fmt(C.EXPLODE_CCU)}+ players within {C.LABEL_DAYS} days of first reaching "
             f"{fmt(C.LEARN_ENTRY_CCU)})"]
    if not st.get("trained"):
        lines.append(f"• Still collecting examples — {st.get('why', 'not trained yet')}.")
    else:
        lines.append(f"• Trained on {st['examples']} young games, {st['positives']} of which exploded "
                     f"({st['positives'] / max(st['examples'], 1) * 100:.0f}%). Only {st.get('live_examples', 0)} of them "
                     f"({st.get('live_positives', 0)} explosions) were first noticed while the bot was watching — the rest come from "
                     f"downloaded history, which only contains games that survived, so the test below uses the watched ones only.")
        lines.append("• " + honest_line(st, "explosions"))
        cl = champion_line(st)
        if cl:
            lines.append("• " + cl)
        if not trusted(st):
            lines.append("• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.")
        names = dict(FEATURES)
        stable = set(st.get("stable") or [])
        drv = ", ".join(f"{names[f]} ({'+' if w > 0 else '−'})" for f, w in st.get("drivers", []) if f in stable)
        lines.append(f"• Drivers that hold up when resampled: {drv}" if drv else
                     "• No driver holds up when the data is resampled yet (too few explosions) — ignore the model's \"reasons\".")
    sc = scorecard(db, today)
    lines += ["", f"🎯 **Scorecard: how often signals were followed by an explosion**"]
    if sc:
        for kind, r in sorted(sc.items(), key=lambda kv: -(kv[1]["hit"] + kv[1]["miss"])):
            done = r["hit"] + r["miss"]
            rate = f"**{r['hit']}/{done}** ({r['hit']/done*100:.0f}%)" if done else "—"
            lines.append(f"• {LABELS.get(kind, kind)}: {rate}" + (f" · {r['pending']} still in their {C.LABEL_DAYS}-day window"
                                                                  + (f" ({r['early']} already exploded)" if r.get("early") else "") if r["pending"] else ""))
        lines.append(f"_Only signals whose {C.LABEL_DAYS} days are up are scored, so early wins don't flatter the rate._")
    else:
        lines.append("• Nothing to score yet")
    return lines

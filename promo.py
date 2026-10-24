"""
Algorithm mirror: learns what Roblox's recommendation algorithm is rewarding RIGHT NOW,
by watching what goes in and what comes out.

We can't see inside Roblox's models (they are trained on every player's private play history),
but we can see both ends:

  IN   public versions of the signals Roblox says it ranks on (June 2026: returning players over
       28 days, playtime per player, early quitting, session quality, spend), plus a few controls:
         playtime per player per day   (badges)          returning-player share   (badges)
         first-step hook               (badges)          sessions per player      (badges)
         weekday hold vs typical game  (hold.py)         session length           (players x 1440 / visits)
         like ratio, favourite rate, revenue per player   (RoWatcher)
         controls: size, momentum, age  (so the model doesn't credit quality for what is just size or growth)

  OUT  two things the algorithm visibly does to a game in the next 7 days:
         chart     the game enters one of Roblox's charts (Trending, Up-and-Coming, Top Revisited...)
         growth    its average players rise 50%+ (most of that lift comes from recommendations)

Two simple logistic models (one per outcome) are trained on every game-day of the last 8 weeks.
All signals are standardised, so each weight reads as "how much one standard step in this signal
raises the odds of being promoted". Comparing this week's weights with a few weeks ago shows when
Roblox changes what it rewards.

The promotion score for a game = the average of its two probabilities, and its "weak spot" is the
quality signal pulling its score down the most.
"""
import math
import random
from datetime import datetime, timedelta
from statistics import median

import config as C
import learn as L
import warehouse as W

SCHEMA = """
CREATE TABLE IF NOT EXISTS promo_preds (day TEXT, uid TEXT, p_chart REAL, p_growth REAL, avg_ccu REAL,
  charted INTEGER, PRIMARY KEY (day, uid));
"""

QUALITY = [
    ("playtime", "playtime per player per day (badges)"),
    ("returning", "returning-player share (badges)"),
    ("first_step", "new players reaching the next badge (badges)"),
    ("sessions", "sessions per player per day (badges)"),
    ("hold", "weekday hold vs a typical game"),
    ("session_len", "session length"),
    ("like_ratio", "like ratio"),
    ("fav_conv", "favourite rate"),
    ("rev_per_player", "revenue per player"),
]
CONTROLS = [
    ("size", "current players (size)"),
    ("momentum", "growth over the last few days"),
    ("age", "game age"),
    ("has_badges", "(has usable badges)"),
]
FEATURES = QUALITY + CONTROLS
NAMES = [f for f, _ in FEATURES]
LABEL = dict(FEATURES)
TARGETS = {"chart": "enters a Roblox chart within 7 days", "growth": "players up 50%+ within 7 days"}


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)


# ------------------------------------------------------------- loading ---

def _load(db, lo, hi):
    """Everything needed for features/labels between lo and hi, in memory."""
    daily = {}
    for r in db.execute("""SELECT uid, day, peak, sum_ccu, n, visits, likes, dislikes, fav_conv, rev_usd, chart_best
                           FROM daily WHERE day>=? AND day<=?""", (lo, hi)):
        avg = (r["sum_ccu"] / r["n"]) if r["n"] and r["sum_ccu"] else (r["peak"] * 0.75 if r["peak"] else None)
        daily.setdefault(r["uid"], {})[r["day"]] = (avg, r["visits"], r["likes"], r["dislikes"], r["fav_conv"],
                                                     r["rev_usd"], r["chart_best"])
    created = {r["uid"]: r["created"] for r in db.execute("SELECT uid, created FROM games")}
    holds = {}
    for r in db.execute("SELECT uid, week, rel FROM hold_weekly WHERE rel IS NOT NULL AND week>=?", (_s(_d(lo) - timedelta(days=14)),)):
        holds.setdefault(r["uid"], []).append((r["week"], r["rel"]))
    badges = {}
    try:
        for r in db.execute("""SELECT uid, day, minutes_per_dau, new_share, first_step_share, sessions_per_dau
                               FROM badge_metrics WHERE day>=?""", (_s(_d(lo) - timedelta(days=4)),)):
            badges.setdefault(r["uid"], []).append((r["day"], r["minutes_per_dau"], r["new_share"], r["first_step_share"],
                                                    r["sessions_per_dau"]))
    except Exception:
        pass
    for v in holds.values():
        v.sort()
    for v in badges.values():
        v.sort()
    return daily, created, holds, badges


def _latest(seq, day, max_age):
    """Last item of a sorted [(day, ...)] list on or before `day`, no older than max_age days."""
    best = None
    for item in seq or []:
        if item[0] <= day:
            best = item
        else:
            break
    if best and (_d(day) - _d(best[0])).days <= max_age:
        return best
    return None


def features(uid, day, data):
    daily, created, holds, badges = data
    ds = daily.get(uid) or {}
    today = ds.get(day)
    if not today or not today[0]:
        return None
    avg = today[0]
    if avg < C.PROMO_MIN_PLAYERS:
        return None
    dd = _d(day)
    def a(k):
        r = ds.get(_s(dd - timedelta(days=k)))
        return r[0] if r and r[0] else None
    recent = [x for x in (a(0), a(1), a(2)) if x]
    before = [x for x in (a(k) for k in range(3, 10)) if x]
    x = {f: None for f in NAMES}
    x["size"] = math.log10(avg + 1)
    x["momentum"] = math.log((sum(recent) / len(recent)) / (sum(before) / len(before))) if recent and before else 0.0
    c = created.get(uid)
    try:
        x["age"] = math.log10(max(1, (dd - _d(c)).days) + 1) if c else None
    except ValueError:
        x["age"] = None
    _, vis, likes, dislikes, fav, rev, _ = today
    prev = ds.get(_s(dd - timedelta(days=1)))
    if vis and prev and prev[1] and vis > prev[1]:
        s = avg * 1440 / (vis - prev[1])
        x["session_len"] = math.log(s) if 0.5 <= s <= 240 else None
    if likes is not None and dislikes is not None and likes + dislikes >= 50:
        x["like_ratio"] = likes / (likes + dislikes)
    x["fav_conv"] = fav
    x["rev_per_player"] = math.log1p(rev / avg) if rev is not None and avg else None
    h = _latest(holds.get(uid), day, 10)
    x["hold"] = h[1] if h else None
    b = _latest(badges.get(uid), day, 4)
    if b:
        _, mpd, new_share, fs, spd = b
        x["playtime"] = math.log(mpd) if mpd else None
        x["returning"] = (1 - new_share) if new_share is not None else None
        x["first_step"] = fs
        x["sessions"] = math.log(spd) if spd else None
    x["has_badges"] = 1.0 if b else 0.0
    return x


def charted_recently(uid, day, data, back=2):
    ds = data[0].get(uid) or {}
    return any((ds.get(_s(_d(day) - timedelta(days=k))) or (None,) * 7)[6] for k in range(0, back + 1))


def labels(uid, day, data):
    ds = data[0].get(uid) or {}
    dd = _d(day)
    fut = [ds.get(_s(dd + timedelta(days=k))) for k in range(1, 8)]
    if sum(1 for f in fut if f and f[0]) < 4:
        return None
    chart = 1 if any(f and f[6] for f in fut) else 0
    past = [ds.get(_s(dd - timedelta(days=k))) for k in range(0, 7)]
    pa = [p[0] for p in past if p and p[0]]
    fa = [f[0] for f in fut if f and f[0]]
    growth = 1 if pa and fa and (sum(fa) / len(fa)) >= C.PROMO_GROWTH_RATIO * (sum(pa) / len(pa)) else 0
    return {"chart": chart, "growth": growth}


# ------------------------------------------------------------ training ---

def _impute(rows, med):
    out = []
    for x in rows:
        out.append({f: (x[f] if x[f] is not None else med[f]) for f in NAMES})
    return out


def build(db, today):
    hi = _s(_d(today) - timedelta(days=8))
    lo = _s(_d(today) - timedelta(days=7 * C.PROMO_HISTORY_WEEKS))
    data = _load(db, _s(_d(lo) - timedelta(days=10)), today)
    rng = random.Random(7)
    ex = {"chart": [], "growth": []}
    day = _d(lo)
    while _s(day) <= hi:
        d = _s(day)
        uids = [u for u, ds in data[0].items() if d in ds]
        rng.shuffle(uids)
        for uid in uids[:C.PROMO_GAMES_PER_DAY]:
            x = features(uid, d, data)
            if not x:
                continue
            y = labels(uid, d, data)
            if not y:
                continue
            ex["growth"].append({"x": x, "y": y["growth"], "day": d})
            if not charted_recently(uid, d, data):  # "enters a chart" only makes sense for games not on one
                ex["chart"].append({"x": x, "y": y["chart"], "day": d})
        day += timedelta(days=C.PROMO_DAY_STEP)
    return ex, data


def _fit_one(examples):
    n, pos = len(examples), sum(e["y"] for e in examples)
    st = {"examples": n, "positives": pos, "trained": False}
    if n < C.PROMO_MIN_EXAMPLES or pos < C.PROMO_MIN_POSITIVES or pos == n:
        st["why"] = f"needs {C.PROMO_MIN_EXAMPLES}+ examples with {C.PROMO_MIN_POSITIVES}+ promotions (has {n} / {pos})"
        return None, st
    examples.sort(key=lambda e: e["day"])
    med = {f: (median([e["x"][f] for e in examples if e["x"][f] is not None])
               if any(e["x"][f] is not None for e in examples) else 0.0) for f in NAMES}
    for e in examples:
        e["x"] = {f: (e["x"][f] if e["x"][f] is not None else med[f]) for f in NAMES}
    usable = [f for f in NAMES if len({round(e["x"][f], 6) for e in examples}) > 1]
    cut = int(n * 0.75)
    tr, te = examples[:cut], examples[cut:]
    if sum(e["y"] for e in tr) >= 5 and 0 < sum(e["y"] for e in te) < len(te):
        m = L.fit(tr, names=usable, iters=C.PROMO_ITERS, l2=C.PROMO_L2)
        sc = [L.predict(m, e["x"]) for e in te]
        lab = [e["y"] for e in te]
        st["test_auc"] = L.auc(sc, lab)
        k = max(1, len(te) // 10)
        st["top10_hit"] = sum(l for _, l in sorted(zip(sc, lab), reverse=True)[:k]) / k
        st["base_rate"] = sum(lab) / len(lab)
    m = L.fit(examples, names=usable, iters=C.PROMO_ITERS, l2=C.PROMO_L2)
    m["median"] = med
    st["trained"] = True
    st["weights"] = {f: w for f, w in zip(m["names"], m["w"])}
    return m, st


def train(db, today):
    ensure(db)
    ex, _ = build(db, today)
    models, status = {}, {"day": today}
    for t in TARGETS:
        m, st = _fit_one(ex[t])
        status[t] = st
        if m:
            models[t] = m
    W.meta_set(db, "promo_models", models)
    W.meta_set(db, "promo_status", status)
    hist = W.meta_get(db, "promo_history", {}) or {}
    hist[today] = {t: status[t].get("weights") for t in TARGETS if status[t].get("trained")}
    for k in sorted(hist)[:-C.PROMO_KEEP_HISTORY]:
        del hist[k]
    W.meta_set(db, "promo_history", hist)
    return status


# ------------------------------------------------------------- scoring ---

def score(db, today, uids):
    """{uid: {"p": promotion score, "chart": p, "growth": p, "weak": (feature, contribution)}}"""
    models = W.meta_get(db, "promo_models", {}) or {}
    if not models:
        return {}
    data = _load(db, _s(_d(today) - timedelta(days=12)), today)
    out = []
    for uid in uids:
        x = features(uid, today, data) or features(uid, _s(_d(today) - timedelta(days=1)), data)
        if not x:
            continue
        res, contrib = {}, {}
        for t, m in models.items():
            xi = {f: (x.get(f) if x.get(f) is not None else m["median"][f]) for f in m["names"]}
            res[t] = L.predict(m, xi)
            for f, w, mu, sd in zip(m["names"], m["w"], m["mu"], m["sd"]):
                if f in dict(QUALITY) and x.get(f) is not None:
                    contrib[f] = contrib.get(f, 0) + w * (x[f] - mu) / sd
        ps = [res[t] for t in res]
        weak = min(contrib.items(), key=lambda kv: kv[1]) if contrib else None
        strong = max(contrib.items(), key=lambda kv: kv[1]) if contrib else None
        out.append((uid, {"p": sum(ps) / len(ps), "chart": res.get("chart"), "growth": res.get("growth"),
                          "weak": weak if weak and weak[1] < 0 else None,
                          "strong": strong if strong and strong[1] > 0 else None,
                          "avg": 10 ** x["size"] - 1, "charted": charted_recently(uid, today, data, 0)}))
    rows = [(today, u, v["chart"], v["growth"], v["avg"], 1 if v["charted"] else 0) for u, v in out]
    db.executemany("INSERT OR REPLACE INTO promo_preds VALUES(?,?,?,?,?,?)", rows)
    db.execute("DELETE FROM promo_preds WHERE day < ?", (_s(_d(today) - timedelta(days=60)),))
    return dict(out)


def scorecard(db, today):
    """How did predictions made 8-35 days ago turn out?"""
    ensure(db)
    lo, hi = _s(_d(today) - timedelta(days=35)), _s(_d(today) - timedelta(days=8))
    preds = db.execute("SELECT * FROM promo_preds WHERE day>=? AND day<=?", (lo, hi)).fetchall()
    if not preds:
        return None
    data = _load(db, _s(_d(lo) - timedelta(days=10)), today)
    res = {}
    for t in TARGETS:
        sc, lab = [], []
        for r in preds:
            p = r["p_chart"] if t == "chart" else r["p_growth"]
            if p is None or (t == "chart" and r["charted"]):
                continue
            y = labels(r["uid"], r["day"], data)
            if y is None:
                continue
            sc.append(p)
            lab.append(y[t])
        if len(sc) >= 50 and 0 < sum(lab) < len(lab):
            k = max(1, len(sc) // 10)
            res[t] = {"n": len(sc), "auc": L.auc(sc, lab), "base": sum(lab) / len(lab),
                      "top10": sum(l for _, l in sorted(zip(sc, lab), reverse=True)[:k]) / k}
    return res


# ------------------------------------------------------------- reports ---

def _bar(w, scale=1.0):
    n = min(8, int(round(abs(w) / scale * 4)))
    return ("🟩" if w > 0 else "🟥") * max(n, 1)


def rewarded(status):
    """Quality signals ranked by average standardised weight across both targets."""
    ws = {}
    for t in TARGETS:
        for f, w in ((status.get(t) or {}).get("weights") or {}).items():
            if f in dict(QUALITY):
                ws.setdefault(f, []).append(w)
    return sorted(((f, sum(v) / len(v)) for f, v in ws.items()), key=lambda x: -x[1])


def shifts(db):
    """Biggest changes in what's rewarded vs ~3 weeks ago."""
    hist = W.meta_get(db, "promo_history", {}) or {}
    days = sorted(hist)
    if len(days) < 2:
        return []
    now = days[-1]
    old = next((d for d in reversed(days[:-1]) if (_d(now) - _d(d)).days >= C.PROMO_SHIFT_DAYS), None)
    if not old:
        return []
    def avgw(h):
        ws = {}
        for t, w in (h or {}).items():
            for f, v in (w or {}).items():
                ws.setdefault(f, []).append(v)
        return {f: sum(v) / len(v) for f, v in ws.items()}
    a, b = avgw(hist[old]), avgw(hist[now])
    out = [(f, a[f], b[f]) for f in b if f in a and f in dict(QUALITY) and abs(b[f] - a[f]) >= C.PROMO_SHIFT_MIN]
    return sorted(out, key=lambda x: -abs(x[2] - x[1])), old


def report_lines(db, today):
    st = W.meta_get(db, "promo_status", {}) or {}
    lines = ["🧠 **Algorithm mirror: what Roblox is rewarding right now**",
             "_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week. "
             "Bars = how much one step up in a signal raises the odds, after allowing for size, momentum and age._"]
    if not any((st.get(t) or {}).get("trained") for t in TARGETS):
        why = "; ".join(f"{t}: {(st.get(t) or {}).get('why', 'not trained')}" for t in TARGETS)
        return lines + [f"• Still learning — {why}."]
    rw = rewarded(st)
    scale = max((abs(w) for _, w in rw), default=1) or 1
    for f, w in rw:
        lines.append(f"{_bar(w, scale)} {LABEL[f]} ({w:+.2f})")
    for t, desc in TARGETS.items():
        s = st.get(t) or {}
        if s.get("test_auc") is not None:
            lines.append(f"• Model for *{desc}*: accuracy {s['test_auc']:.2f} on days it hadn't seen "
                         f"(0.5 = coin flip); its top 10% were promoted {s['top10_hit']*100:.0f}% of the time vs "
                         f"{s['base_rate']*100:.0f}% for all games ({s['examples']} examples).")
    sh = shifts(db)
    if sh and sh[0]:
        moves, old = sh
        lines.append(f"⚠️ **Algorithm change watch** (vs {old}): " + "; ".join(
            f"{LABEL[f]} {'more' if b > a else 'less'} rewarded ({a:+.2f} → {b:+.2f})" for f, a, b in moves[:4]))
    sc = scorecard(db, today)
    if sc:
        for t, r in sc.items():
            lines.append(f"🧪 Live check, {TARGETS[t]}: past predictions scored {r['auc']:.2f}; their top 10% were promoted "
                         f"{r['top10']*100:.0f}% of the time vs {r['base']*100:.0f}% overall ({r['n']} predictions).")
    lines.append("_Correlation from public data, not Roblox's actual model — but it tracks what its outputs reward, "
                 "and the live check shows whether it works._")
    return lines


def digest_lines(scores, name_of, link, young_ids, fmt):
    top = sorted(((v["p"], u, v) for u, v in scores.items() if u in young_ids and not v["charted"]), reverse=True)[:5]
    if not top:
        return []
    lines = ["🧠 **Most likely to be promoted by Roblox next** (algorithm mirror)"]
    for p, u, v in top:
        bits = [f"**{p*100:.0f}%**", f"{fmt(v['avg'])} players"]
        if v.get("strong"):
            bits.append(f"strong: {LABEL[v['strong'][0]].split(' (')[0]}")
        if v.get("weak"):
            bits.append(f"weak spot: {LABEL[v['weak'][0]].split(' (')[0]}")
        lines.append(f"• {name_of(u)[:36]} — " + " · ".join(bits) + f" {link(u)}")
    return lines

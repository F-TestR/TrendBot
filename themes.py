"""
Themes: predicting TRENDS (not single games) before they form, and learning which
indicators actually give early warning.

A "theme" is a word or two-word phrase from game titles ("cat", "chocolate factory"),
or one of RoWatcher's curated trend definitions ("Brainrot", "Pets"...).

Every day the bot works out, for every theme:
  ccu        total players across its games
  games      how many games use it          hits     how many have 2K+ players
  new7       games created in the last 7 days (new7_prev = the 7 days before)
  tiny7      new games still under 1K players (studios testing the idea)
  studios7   different studios behind those new games
  renames7   established games that renamed themselves to include it
  charts     games of this theme in Roblox's algorithm charts
  yt3        Roblox YouTube video titles using it (last 3 days, and the 3 before)
  upstream   whether it is rising on Steam / YouTube trending / Wikipedia / Twitch,
             or is in season

A theme "breaks out" when it goes from at most 1 game with 2K+ players to at least
THEME_BREAKOUT_GAMES such games within LABEL_DAYS days. The model learns, from every
past theme-day, which of the numbers above came before breakouts. The indicator
report tests each signal on its own: how often it was followed by a breakout and
how many days of warning it gave.
"""
import math
import re
from datetime import datetime, timedelta
from statistics import median

import config as C
import learn as L
import upstream as U
import warehouse as W

SCHEMA = """
CREATE TABLE IF NOT EXISTS theme_daily (theme TEXT, day TEXT, ccu INTEGER, games INTEGER, hits INTEGER,
  new7 INTEGER, new7_prev INTEGER, tiny7 INTEGER, studios7 INTEGER, renames7 INTEGER, charts INTEGER,
  yt3 INTEGER, yt3_prev INTEGER, up_steam REAL, up_wiki REAL, up_ytt REAL, up_tw REAL, season REAL,
  PRIMARY KEY (theme, day));
CREATE INDEX IF NOT EXISTS theme_daily_day ON theme_daily(day);
CREATE TABLE IF NOT EXISTS renames (uid TEXT, day TEXT, old TEXT, new TEXT, PRIMARY KEY (uid, day));
CREATE TABLE IF NOT EXISTS theme_preds (day TEXT, theme TEXT, prob REAL, PRIMARY KEY (day, theme));
"""

FEATURES = [
    ("ccu", "players across the theme"),
    ("growth3", "theme growth over 3 days"),
    ("growth7", "theme growth over 7 days"),
    ("games", "number of games"),
    ("new7", "new games this week"),
    ("new_accel", "new games this week vs last week"),
    ("tiny7", "tiny new games (studios testing it)"),
    ("studios7", "different studios making it"),
    ("renames7", "established games renaming to it"),
    ("charts", "in Roblox's algorithm charts"),
    ("yt3", "Roblox YouTube mentions"),
    ("yt_accel", "Roblox YouTube mentions rising"),
    ("up_steam", "rising on Steam"),
    ("up_wiki", "spiking on Wikipedia"),
    ("up_ytt", "rising on YouTube trending"),
    ("up_tw", "new in Twitch's top games"),
    ("season", "in season"),
]

INDICATORS = {
    "copy_burst": ("🧬 copy burst", lambda r, p: r["new7"] >= 3 and r["new7"] >= 2 * (r["new7_prev"] + 1)),
    "tiny_burst": ("🐣 tiny-game burst", lambda r, p: r["tiny7"] >= 4),
    "many_studios": ("🏢 3+ studios at once", lambda r, p: r["studios7"] >= 3),
    "renames": ("✏️ games renaming to it", lambda r, p: r["renames7"] >= 2),
    "growth": ("📈 theme doubled in a week", lambda r, p: p is not None and p["ccu"] > 0 and r["ccu"] >= 2 * p["ccu"]),
    "charts": ("📊 in the algorithm charts", lambda r, p: r["charts"] >= 1),
    "yt_buzz": ("📺 Roblox YouTube buzz", lambda r, p: r["yt3"] >= 3 and r["yt3"] >= 3 * (r["yt3_prev"] + 1)),
    "steam": ("🎮 rising on Steam", lambda r, p: (r["up_steam"] or 0) > 0),
    "wikipedia": ("📚 Wikipedia spike", lambda r, p: (r["up_wiki"] or 0) > 0),
    "yt_trending": ("🔥 YouTube trending", lambda r, p: (r["up_ytt"] or 0) > 0),
    "twitch_top": ("🟣 Twitch top games", lambda r, p: (r["up_tw"] or 0) > 0),
    "season": ("🗓️ in season", lambda r, p: (r["season"] or 0) > 0),
}


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)
    U.ensure(db)


def display(key, state=None):
    if key.startswith("rw:"):
        for tid, name, _ in (state or {}).get("rw_trends", []):
            if tid == key[3:]:
                return name
        return key[3:]
    return key[2:]


def keys_for(name, rw_trends):
    ws = U.words_of(name)
    keys = {("b:" if " " in w else "w:") + w for w in ws}
    low = " " + re.sub(r"[^a-z0-9]+", " ", (name or "").lower()) + " "
    for tid, _, kws in rw_trends:
        if any(" " + k + " " in low for k in kws):
            keys.add("rw:" + tid)
    return keys


# ----------------------------------------------------------- daily build ---

def record_rename(db, uid, day, old, new):
    db.execute("INSERT OR IGNORE INTO renames(uid, day, old, new) VALUES(?,?,?,?)", (uid, day, old[:120], new[:120]))


def compute_days(db, days, rw_trends):
    """Fill theme_daily for the given days (each a finished day)."""
    if not days:
        return 0
    lo = _s(_d(min(days)) - timedelta(days=21))
    hi = max(days)
    games = {r["uid"]: dict(r) for r in db.execute("SELECT uid, name, created, creator_id FROM games")}
    keys = {uid: keys_for(g["name"], rw_trends) for uid, g in games.items()}
    peaks, charts = {}, {}
    for r in db.execute("SELECT uid, day, peak, chart_best FROM daily WHERE day>=? AND day<=?", (lo, hi)):
        if r["peak"]:
            peaks.setdefault(r["uid"], {})[r["day"]] = r["peak"]
        if r["chart_best"]:
            charts.setdefault(r["day"], set()).add(r["uid"])
    renames = {}
    for r in db.execute("SELECT uid, day, old, new FROM renames WHERE day>=?", (lo,)):
        old = keys_for(r["old"], rw_trends)
        for k in keys_for(r["new"], rw_trends) - old:
            renames.setdefault(k, []).append(r["day"])
    ytw, up = {}, {}
    for r in db.execute("SELECT source, day, word, score FROM upstream WHERE day>=? AND day<=?", (lo, hi)):
        if r["source"] == "yt_roblox":
            ytw.setdefault(r["word"], {})[r["day"]] = r["score"]
        else:
            up.setdefault(r["word"], {}).setdefault(r["source"], {})[r["day"]] = r["score"]

    def upscore(k, src, day):
        word = k[2:] if not k.startswith("rw:") else None
        if not word:
            return 0.0
        rows = (up.get(word) or {}).get(src) or {}
        lo7 = _s(_d(day) - timedelta(days=7))
        return max([v for dd, v in rows.items() if lo7 < dd <= day] or [0.0])

    written = 0
    for day in sorted(days):
        agg = {}
        d7, d14 = _s(_d(day) - timedelta(days=7)), _s(_d(day) - timedelta(days=14))
        for uid, ps in peaks.items():
            g = games.get(uid)
            if not g:
                continue
            p = ps.get(day)
            created = g.get("created")
            is_new = created and d7 < created <= day
            was_new = created and d14 < created <= d7
            if not p and not (is_new or was_new):
                continue
            best = max([v for dd, v in ps.items() if dd <= day] or [0])
            if best < C.THEME_MIN_GAME_CCU:
                continue
            for k in keys.get(uid, ()):
                a = agg.setdefault(k, {"ccu": 0, "games": 0, "hits": 0, "new7": 0, "new7_prev": 0,
                                       "tiny7": 0, "studios": set(), "charts": 0})
                if p:
                    a["ccu"] += p
                    a["games"] += 1
                    if p >= C.THEME_HIT_CCU:
                        a["hits"] += 1
                    if uid in charts.get(day, ()):
                        a["charts"] += 1
                if is_new:
                    a["new7"] += 1
                    if best < 1000:
                        a["tiny7"] += 1
                    if g.get("creator_id"):
                        a["studios"].add(g["creator_id"])
                elif was_new:
                    a["new7_prev"] += 1
        rows = []
        for k, a in agg.items():
            single = a["games"] <= 1 and a["new7"] == 0
            if single or (a["ccu"] < C.THEME_MIN_CCU and a["new7"] == 0):
                continue
            yw = ytw.get(k[2:] if not k.startswith("rw:") else "", {})
            yt3 = sum(v for dd, v in yw.items() if _s(_d(day) - timedelta(days=3)) < dd <= day)
            yt3p = sum(v for dd, v in yw.items() if _s(_d(day) - timedelta(days=6)) < dd <= _s(_d(day) - timedelta(days=3)))
            rn = sum(1 for dd in renames.get(k, []) if d7 < dd <= day)
            rows.append((k, day, a["ccu"], a["games"], a["hits"], a["new7"], a["new7_prev"], a["tiny7"],
                         len(a["studios"]), rn, a["charts"], int(yt3), int(yt3p),
                         upscore(k, "steam", day), upscore(k, "wikipedia", day), upscore(k, "yt_trending", day),
                         upscore(k, "twitch_top", day), upscore(k, "season", day)))
        db.executemany("""INSERT OR REPLACE INTO theme_daily VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
        written += len(rows)
    return written


def update(db, state, today):
    """Compute any missing finished days (first time: as far back as the database goes)."""
    ensure(db)
    yday = _s(_d(today) - timedelta(days=1))
    have = {r["day"] for r in db.execute("SELECT DISTINCT day FROM theme_daily")}
    first = db.execute("SELECT MIN(day) AS m FROM daily WHERE peak IS NOT NULL").fetchone()["m"]
    if not first:
        return 0
    start = max(_d(first) + timedelta(days=7), _d(today) - timedelta(days=C.THEME_HISTORY_DAYS))
    days, d = [], start
    while _s(d) <= yday:
        if _s(d) not in have or _s(d) >= _s(_d(yday) - timedelta(days=2)):  # refresh last few days
            days.append(_s(d))
        d += timedelta(days=1)
    n = compute_days(db, days, state.get("rw_trends", []))
    cut = _s(_d(today) - timedelta(days=C.THEME_KEEP_DAYS))
    db.execute("DELETE FROM theme_daily WHERE day < ?", (cut,))
    db.execute("DELETE FROM renames WHERE day < ?", (cut,))
    db.execute("DELETE FROM theme_preds WHERE day < ?", (cut,))
    return n


def record_roblox_youtube_words(db, state, day):
    """Words used in Roblox YouTube video titles published on `day` (feature yt3)."""
    from sources import src_state
    U.ensure(db)
    counts = {}
    for r in src_state(state)["videos"].values():
        if (r.get("p") or "")[:10] == day:
            for w in U.words_of(r.get("t", "")):
                counts[w] = counts.get(w, 0) + 1
    for w, n in counts.items():
        U.put(db, "yt_roblox", day, w, float(n))


# ---------------------------------------------------------- learning ---

def _load(db, since=None):
    rows = {}
    q = "SELECT * FROM theme_daily" + (" WHERE day>=?" if since else "")
    for r in db.execute(q, (since,) if since else ()):
        rows.setdefault(r["theme"], {})[r["day"]] = dict(r)
    return rows


def _features(r, hist, day):
    def prev(n):
        return hist.get(_s(_d(day) - timedelta(days=n)))
    p3, p7 = prev(3), prev(7)
    lg = lambda v: math.log10(max(v or 0, 1))
    return {
        "ccu": lg(r["ccu"]),
        "growth3": math.log2(max(r["ccu"], 1) / max((p3 or {}).get("ccu", 0) or 0, max(r["ccu"] / 8, 1))) if p3 else 0.0,
        "growth7": math.log2(max(r["ccu"], 1) / max((p7 or {}).get("ccu", 0) or 0, max(r["ccu"] / 16, 1))) if p7 else 0.0,
        "games": math.log1p(r["games"]), "new7": math.log1p(r["new7"]),
        "new_accel": math.log1p(r["new7"]) - math.log1p(r["new7_prev"]),
        "tiny7": math.log1p(r["tiny7"]), "studios7": math.log1p(r["studios7"]),
        "renames7": math.log1p(r["renames7"]), "charts": math.log1p(r["charts"]),
        "yt3": math.log1p(r["yt3"]), "yt_accel": math.log1p(r["yt3"]) - math.log1p(r["yt3_prev"]),
        "up_steam": float(r["up_steam"] or 0), "up_wiki": float(r["up_wiki"] or 0),
        "up_ytt": min(3.0, math.log1p(r["up_ytt"] or 0)), "up_tw": float(r["up_tw"] or 0),
        "season": float(r["season"] or 0),
    }


def breakout_day(hist):
    """First day a theme reached THEME_BREAKOUT_GAMES hits after having <= 1."""
    was_small = False
    for day in sorted(hist):
        h = hist[day]["hits"]
        if h <= 1:
            was_small = True
        elif h >= C.THEME_BREAKOUT_GAMES and was_small:
            return day
    return None


def examples(db, today, predict_only=False):
    data = _load(db, _s(_d(today) - timedelta(days=C.THEME_KEEP_DAYS)))
    out = []
    for k, hist in data.items():
        bday = breakout_day(hist)
        ds = sorted(hist)
        for i, day in enumerate(ds):
            r = hist[day]
            if r["hits"] > 1 or (bday and day >= bday):
                if bday and day >= bday:
                    break
                continue
            end = _s(_d(day) + timedelta(days=C.LABEL_DAYS))
            if predict_only:
                if day != ds[-1] or day < _s(_d(today) - timedelta(days=2)):
                    continue
                y = None
            else:
                if i % 3 and not (bday and _d(bday) - _d(day) <= timedelta(days=C.LABEL_DAYS)):
                    continue  # thin out non-event days so one theme doesn't dominate
                hit = bool(bday and day < bday <= end)
                if not hit and end >= today:
                    continue
                y = 1 if hit else 0
            out.append({"theme": k, "day": day, "x": _features(r, hist, day), "y": y, "row": r})
    out.sort(key=lambda e: e["day"])
    return out


def train(db, today):
    names = [f for f, _ in FEATURES]
    ex = examples(db, today)
    n, pos = len(ex), sum(e["y"] for e in ex)
    st = {"examples": n, "positives": pos, "trained": False, "day": today}
    if n < C.THEME_MIN_EXAMPLES or pos < C.THEME_MIN_POSITIVES:
        st["why"] = f"needs {C.THEME_MIN_EXAMPLES}+ theme-days with {C.THEME_MIN_POSITIVES}+ breakouts (has {n} / {pos})"
        W.meta_set(db, "theme_model_status", st)
        return st
    cut = int(n * 0.75)
    tr, te = ex[:cut], ex[cut:]
    if sum(e["y"] for e in tr) >= 3 and 0 < sum(e["y"] for e in te) < len(te):
        m = L.fit(tr, names=names)
        sc = [L.predict(m, e["x"]) for e in te]
        lab = [e["y"] for e in te]
        st["test_auc"] = L.auc(sc, lab)
        st["test_n"], st["test_pos"], st["base_rate"] = len(te), sum(lab), sum(lab) / len(lab)
        k = max(1, len(te) // 20)
        st["test_top5_hit"] = sum(l for _, l in sorted(zip(sc, lab), reverse=True)[:k]) / k
    model = L.fit(ex, names=names)
    st["trained"] = True
    st["drivers"] = sorted(zip(model["names"], model["w"]), key=lambda x: -abs(x[1]))[:6]
    W.meta_set(db, "theme_model", model)
    W.meta_set(db, "theme_model_status", st)
    return st


def firing(r, prev):
    return [k for k, (_, rule) in INDICATORS.items() if rule(r, prev)]


def predict(db, today):
    """[(prob or None, rule_score, theme, row, firing_indicators)] for small themes, best first."""
    model = W.meta_get(db, "theme_model")
    data = _load(db, _s(_d(today) - timedelta(days=10)))
    out = []
    for e in examples(db, today, predict_only=True):
        hist = data.get(e["theme"], {})
        prev = hist.get(_s(_d(e["day"]) - timedelta(days=7)))
        fired = firing(e["row"], prev)
        p = L.predict(model, e["x"]) if model else None
        if p is not None:
            db.execute("INSERT OR REPLACE INTO theme_preds(day, theme, prob) VALUES(?,?,?)", (today, e["theme"], p))
        out.append((p, len(fired), e["theme"], e["row"], fired))
    out.sort(key=lambda x: (-(x[0] if x[0] is not None else -1), -x[1], -x[3]["new7"]))
    # prefer the single word over a phrase that covers the same new games ("cactus" over "cactus clicker")
    words = {}
    last = max((e[3]["day"] for e in out), default=None)
    if last:
        for r in db.execute("SELECT * FROM theme_daily WHERE day=? AND theme LIKE 'w:%'", (last,)):
            words[r["theme"]] = dict(r)
    keep = []
    for item in out:
        k, r = item[2], item[3]
        if k.startswith("b:"):
            parts = k[2:].split()
            # skip if a single word already covers it, or that word is already a big trend
            if any(("w:" + w) in words and (words["w:" + w]["new7"] >= r["new7"]
                                            or words["w:" + w]["hits"] > C.THEME_ALERT_MAX_HITS) for w in parts):
                continue
        keep.append(item)
    return keep


# --------------------------------------------------------- indicators ---

def indicator_report(db, today):
    """For each indicator: how often it was followed by a breakout, and how much warning it gave."""
    data = _load(db, _s(_d(today) - timedelta(days=C.THEME_KEEP_DAYS)))
    stats = {k: {"fired": 0, "hit": 0, "miss": 0, "leads": []} for k in INDICATORS}
    breakouts = {}
    for k, hist in data.items():
        b = breakout_day(hist)
        if b:
            breakouts[k] = b
    caught = {k: 0 for k in INDICATORS}
    for theme, hist in data.items():
        b = breakouts.get(theme)
        last_fire = {}
        for day in sorted(hist):
            if b and day >= b:
                break
            r = hist[day]
            if r["hits"] > 1:
                continue
            prev = hist.get(_s(_d(day) - timedelta(days=7)))
            for ind in firing(r, prev):
                lf = last_fire.get(ind)
                if lf and (_d(day) - _d(lf)).days < 14:
                    continue
                last_fire[ind] = day
                s = stats[ind]
                s["fired"] += 1
                end = _s(_d(day) + timedelta(days=C.LABEL_DAYS))
                if b and day < b <= end:
                    s["hit"] += 1
                    s["leads"].append((_d(b) - _d(day)).days)
                elif end < today:
                    s["miss"] += 1
        if b:
            for ind in INDICATORS:
                lo = _s(_d(b) - timedelta(days=C.LABEL_DAYS))
                if any(lo <= d < b and ind in firing(hist[d], hist.get(_s(_d(d) - timedelta(days=7))))
                       for d in hist if d < b):
                    caught[ind] += 1
    total_b = len(breakouts)
    # base rate: share of small-theme days followed by a breakout
    ex = examples(db, today)
    base = (sum(e["y"] for e in ex) / len(ex)) if ex else None
    rows = []
    for k, s in stats.items():
        done = s["hit"] + s["miss"]
        prec = s["hit"] / done if done else None
        rows.append({"key": k, "label": INDICATORS[k][0], "fired": s["fired"], "hit": s["hit"], "done": done,
                     "precision": prec, "lift": (prec / base) if (prec is not None and base) else None,
                     "lead": median(s["leads"]) if s["leads"] else None,
                     "recall": (caught[k] / total_b) if total_b else None})
    rows.sort(key=lambda r: -((r["lift"] or 0) * min(r["done"], 20)))
    return rows, total_b, base


def report_lines(db, today, fmt):
    st = W.meta_get(db, "theme_model_status", {}) or {}
    lines = [f"🌱 **Theme model** (a theme \"breaks out\" when {C.THEME_BREAKOUT_GAMES}+ of its games pass "
             f"{fmt(C.THEME_HIT_CCU)} players within {C.LABEL_DAYS} days)"]
    if not st.get("trained"):
        lines.append(f"• Still collecting — {st.get('why', 'not trained yet')}.")
    else:
        lines.append(f"• Trained on {st['examples']:,} theme-days, {st['positives']} of which led to a breakout.")
        if st.get("test_auc") is not None:
            lines.append(f"• On the newest data it hadn't seen: AUC **{st['test_auc']:.2f}**; its top 5% picks broke out "
                         f"**{st['test_top5_hit']*100:.0f}%** of the time vs {st['base_rate']*100:.1f}% on average.")
        names = dict(FEATURES)
        lines.append("• Biggest drivers: " + ", ".join(f"{names[f]} ({'+' if w > 0 else '−'})" for f, w in st.get("drivers", [])[:5]))
    rows, nb, base = indicator_report(db, today)
    lines += ["", f"🔬 **Which indicators actually work** ({nb} theme breakouts tracked so far)"]
    useful = [r for r in rows if r["done"]]
    if useful:
        for r in useful[:12]:
            lift = f" · **{r['lift']:.1f}×** better than chance" if r["lift"] else ""
            lead = f" · ~{r['lead']:.0f} days' warning" if r["lead"] is not None else ""
            rec = f" · caught {r['recall']*100:.0f}% of breakouts" if r["recall"] is not None else ""
            lines.append(f"• {r['label']}: followed by a breakout {r['hit']}/{r['done']} times{lift}{lead}{rec}")
        idle = [r["label"] for r in rows if not r["done"]]
        if idle:
            lines.append("• Not enough data yet: " + ", ".join(idle))
    else:
        lines.append("• Measuring — results appear as indicator firings reach the end of their 3-week window.")
    return lines


# ------------------------------------------------------------- alerts ---

def top_games(db, theme, rw_trends, day, n=3):
    rows = db.execute("""SELECT g.uid, g.name, d.peak FROM daily d JOIN games g ON g.uid=d.uid
                         WHERE d.day=? AND d.peak IS NOT NULL ORDER BY d.peak DESC""", (day,)).fetchall()
    out = []
    for r in rows:
        if theme in keys_for(r["name"], rw_trends):
            out.append((r["peak"], r["name"], r["uid"]))
            if len(out) >= n:
                break
    return out


def bridges(db, state, today):
    """Outside-Roblox words that just started appearing in brand-new Roblox games."""
    lo14 = _s(_d(today) - timedelta(days=14))
    up = {}
    for r in db.execute("""SELECT word, source, MAX(score) AS s, MAX(detail) AS detail FROM upstream
                           WHERE day>=? AND source IN ('steam','wikipedia','yt_trending','twitch_top')
                           GROUP BY word, source""", (lo14,)):
        if len(r["word"]) >= 4 and r["word"] not in C.THEME_GENERIC:
            up.setdefault(r["word"], []).append((r["source"], r["detail"]))
    if not up:
        return []
    yday = _s(_d(today) - timedelta(days=1))
    old = _s(_d(today) - timedelta(days=21))
    out = []
    for word, srcs in up.items():
        key = ("b:" if " " in word else "w:") + word
        now = db.execute("SELECT * FROM theme_daily WHERE theme=? AND day=?", (key, yday)).fetchone()
        if not now or now["new7"] < 1:
            continue
        before = db.execute("SELECT MAX(games) AS g FROM theme_daily WHERE theme=? AND day<=?", (key, old)).fetchone()
        if before and (before["g"] or 0) > 1:
            continue  # already a Roblox word before the outside signal
        out.append((word, srcs, dict(now)))
    return out

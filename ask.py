"""
Ask the bot: answers plain-English questions from the bot's own database, posted to Discord.

No AI service (so no tokens): the question is matched to one of these kinds, by keywords:
  game      "how is Wash the Car doing?"  "tell me about be a pirate"        -> one game in detail
  compare   "Wash the Car vs Clean Everything"  "compare X and Y"          -> two games side by side
  theme     "is chocolate trending?"  "cleaning games"  "theme pirate"     -> a title word / theme
  mechanic  "how are tycoon games doing?"  "horror"                        -> a mechanic or genre
  top       "what's rising?"  "top games"  "what should I watch?"          -> today's board
  longterm  "long term games"  "what lasts?"                               -> long-term list and genres
  algorithm "what is roblox rewarding?"  "algorithm"                       -> the algorithm mirror
  coming    "what's coming up?"                                            -> forward calendar
  help      anything else, with suggestions

Game names are matched loosely (typos, missing emoji and brackets are fine).
"""
import difflib
import json
import math
import re
from datetime import datetime, timedelta
from statistics import median

import config as C

STOP = {"how", "is", "are", "the", "a", "an", "doing", "about", "tell", "me", "what", "whats", "what's", "game", "games",
        "of", "on", "in", "for", "and", "to", "do", "does", "it", "its", "it's", "right", "now", "today", "this", "week",
        "show", "give", "info", "stats", "please", "roblox", "any", "there", "be", "will", "going", "doing?", "trend",
        "trending", "theme", "with", "my", "our", "can", "you", "i", "should", "look", "at", "like", "much", "many"}

KINDS = [
    ("algorithm", r"\b(algorithm|rewarding|reward|promot|recommend)"),
    ("longterm", r"\b(long[ -]?term|lasting|lasts|sticky|stickiest|habit)"),
    ("coming", r"\b(coming up|upcoming|calendar|release|releases|next month|halloween|christmas)\b"),
    ("top", r"\b(rising|top|best|hot|hottest|watch list|to watch|breakouts?|what'?s new|new games|biggest)\b"),
]


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def norm(name):
    t = re.sub(r"\[.*?\]|\(.*?\)", " ", (name or "").lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _pct(x):
    return f"{x * 100:.0f}%"


# ------------------------------------------------------------- matching ---

def find_games(state, db, text, n=3):
    """Loose name match over every game the bot knows. Returns [(score, uid, name)]."""
    q = norm(text)
    qw = [w for w in q.split() if w not in STOP]
    if not qw:
        return []
    qs = " ".join(qw)
    names = {u: r.get("name") or u for u, r in state["games"].items()}
    for r in db.execute("SELECT uid, name FROM games WHERE name IS NOT NULL"):
        names.setdefault(r["uid"], r["name"])
    players = {u: r.get("last", 0) for u, r in state["games"].items()}
    out = []
    for uid, name in names.items():
        nn = norm(name)
        if not nn:
            continue
        nw = set(nn.split())
        overlap = sum(1 for w in qw if w in nw) / len(qw)
        if overlap == 0 and not any(difflib.get_close_matches(w, list(nw), 1, 0.85) for w in qw):
            continue
        ratio = difflib.SequenceMatcher(None, qs, nn).ratio()
        sc = 0.6 * overlap + 0.4 * ratio + 0.05 * math.log10(players.get(uid, 0) + 10)
        if qs == nn:
            sc += 1
        out.append((sc, uid, name))
    out.sort(reverse=True)
    return out[:n]


def classify(q, state, db):
    ql = q.lower().strip()
    if not ql or ql in ("help", "?"):
        return "help", None
    for sep in (" vs ", " versus ", " or "):
        if sep in ql:
            a, b = ql.split(sep, 1)
            a = re.sub(r"^(compare|which is better|is)\s+", "", a)
            return "compare", (a, b.rstrip("?"))
    m = re.match(r"compare (.+?) (?:and|with|to) (.+)", ql)
    if m:
        return "compare", (m.group(1), m.group(2).rstrip("?"))
    for kind, rx in KINDS:
        if re.search(rx, ql):
            return kind, None
    words = [w for w in norm(ql).split() if w not in STOP]
    for mech, kws in C.MECHANICS.items():
        if any(w in kws or w.rstrip("s") in kws for w in words) and len(words) <= 2 and \
                re.search(r"\b(games?|genre|mechanic|type)\b", ql):
            return "mechanic", mech
    genres = {r["genre"] for r in db.execute("SELECT DISTINCT genre FROM games WHERE genre IS NOT NULL")}
    for g in genres:
        if norm(g) and norm(g) in norm(ql) and re.search(r"\b(games?|genre)\b", ql):
            return "genre", g
    if re.search(r"\b(trending|theme|trend|games)\b", ql) and len(words) <= 2:
        return "theme", " ".join(words)
    hits = find_games(state, db, ql)
    if hits and hits[0][0] >= 0.55:
        return "game", hits
    if len(words) <= 2 and words:
        return "theme", " ".join(words)
    return ("game", hits) if hits else ("help", None)


# -------------------------------------------------------------- answers ---

def game_card(db, state, uid, ctx, compact=False):
    S, fmt, today = ctx["S"], ctx["fmt"], ctx["today"]
    r = state["games"].get(uid) or {}
    g = db.execute("SELECT * FROM games WHERE uid=?", (uid,)).fetchone()
    name = r.get("name") or (g["name"] if g else uid)
    url = ctx["link"](uid, state).strip("<>")
    days = db.execute("SELECT day, peak, sum_ccu, n FROM daily WHERE uid=? AND day>=? ORDER BY day",
                      (uid, _s(_d(today) - timedelta(days=15)))).fetchall()
    avg = [(d["day"], (d["sum_ccu"] / d["n"]) if d["n"] and d["n"] >= 3 else (d["peak"] or 0) * 0.75) for d in days]
    lines = []
    now = r.get("last") or (avg[-1][1] if avg else 0)
    head = [f"**{fmt(now)}** playing"]
    age = ctx["age_days"](r, today) if r else None
    if age is not None:
        head.append(f"{age} days old")
    if g and g["genre"]:
        head.append(g["genre"])
    mech = ctx["I"].mechanics_of(name)
    if mech:
        head.append(mech[0])
    lines.append(" · ".join(head))
    if len(avg) >= 8:
        a = dict(avg)
        y = avg[-1][0]
        wk = a.get(_s(_d(y) - timedelta(days=7)))
        if wk:
            lines.append(f"📊 {_d(y).strftime('%a')} {fmt(avg[-1][1])} avg vs {fmt(wk)} a week before (**{(avg[-1][1] / wk - 1) * 100:+.0f}%**)")
        spark = "▁▂▃▄▅▆▇█"
        vals = [v for _, v in avg[-14:]]
        lo, hi = min(vals), max(vals)
        lines.append("Last 14 days: `" + "".join(spark[min(7, int((v - lo) / ((hi - lo) or 1) * 7.99))] for v in vals) + "`")
    h = (state.get("hold") or {}).get(uid) or {}
    lt = ((state.get("longterm") or {}).get(uid) or {}).get("status")
    st = ((state.get("stick") or {}).get(uid) or {}).get("score")
    q = []
    if h.get("rel"):
        q.append(f"weekday hold **{h['rel']:.2f}×** typical")
    elif h.get("flag") == "growing":
        q.append("weekday hold: still growing")
    if st is not None:
        q.append(f"stickiness **{st:.0f}**/100")
    if lt:
        q.append("🏛️ long-term" if lt == "long-term" else "promising")
    if q:
        lines.append("🔁 " + " · ".join(q))
    b = (state.get("badges") or {}).get(uid) or {}
    if b.get("dau"):
        bits = [f"{fmt(b['dau'])} players/day"]
        if b.get("playtime"):
            bits.append(f"~{b['playtime']:.0f} min each")
        if b.get("returning") is not None:
            bits.append(f"{_pct(b['returning'])} returning")
        if b.get("streak7"):
            bits.append(f"{b['streak7'][1] * 100:.1f}% reach a {b['streak7'][0]}-day streak")
        lines.append("⏱ " + " · ".join(bits))
    try:
        f = ctx["FC"]
        series = f.load_series(db, _s(_d(today) - timedelta(days=30)), _s(_d(today) - timedelta(days=1)))
        v = series.get(uid)
        wf = (state.get("fc_meta") or {}).get("wf") or [1] * 7
        if v:
            fc = f.forecast_game(v, wf)
            pt = f.peak_text(fc, fmt) if fc else None
            cp = f.changepoint(v, wf)
            if pt:
                lines.append(f"📈 Forecast: {pt}" + (" · 🧭 breakout just started" if cp and cp["fire"] else ""))
        surv = {(x["kind"], x["label"]): x for x in state.get("fc_surv") or []}
        for kind, label in (("mech", mech[0] if mech else None), ("genre", g["genre"] if g else None), ("all", "all games")):
            x = surv.get((kind, label))
            if x and x.get("median") is not None:
                lines.append(f"⏳ {label} hits usually keep half their peak players ~{x['median']} days")
                break
    except Exception:
        pass
    try:
        ps = ctx["P"].score(db, today, [uid]).get(uid)
        if ps:
            bits = [f"🧠 Promotion chance next 7 days: **{_pct(ps['p'])}**"]
            if ps.get("weak"):
                bits.append(f"weak spot: {ctx['P'].LABEL[ps['weak'][0]].split(' (')[0]}")
            lines.append(" · ".join(bits))
    except Exception:
        pass
    pm = (state.get("_preds") or {}).get(uid)
    if pm is None:
        row = db.execute("SELECT prob FROM predictions WHERE uid=? ORDER BY day DESC LIMIT 1", (uid,)).fetchone()
        pm = row["prob"] if row else None
    if pm is not None:
        lines.append(f"🎯 Breakout chance: {_pct(min(pm, 0.95))}")
    if compact:
        return name, url, lines
    return {"title": f"🔎 {name[:80]}", "url": url, "description": "\n".join(lines)[:4000], "color": 0x5865F2}


def theme_answer(db, state, word, ctx):
    fmt, today = ctx["fmt"], ctx["today"]
    w = norm(word)
    key = ("b:" if " " in w else "w:") + w
    rows = db.execute("SELECT * FROM theme_daily WHERE theme=? AND day>=? ORDER BY day",
                      (key, _s(_d(today) - timedelta(days=15)))).fetchall()
    if not rows and w.endswith("s"):
        key = key[:-1]
        rows = db.execute("SELECT * FROM theme_daily WHERE theme=? AND day>=? ORDER BY day",
                          (key, _s(_d(today) - timedelta(days=15)))).fetchall()
        w = w[:-1]
    lines = []
    if rows:
        last = rows[-1]
        wk = next((r for r in rows if r["day"] == _s(_d(last["day"]) - timedelta(days=7))), None)
        chg = f" ({(last['ccu'] / wk['ccu'] - 1) * 100:+.0f}% vs a week before)" if wk and wk["ccu"] else ""
        lines.append(f"**{last['games']}** games with \"{w}\" in the title · **{fmt(last['ccu'])}** players{chg}")
        lines.append(f"🆕 {last['new7']} new this week (vs {last['new7_prev']} the week before) · "
                     f"{last['studios7']} studios · {last['hits']} with {fmt(C.THEME_HIT_CCU)}+ players")
        verdict = ("🔥 **Trending up** — new copies arriving and players growing" if last["new7"] > last["new7_prev"] and chg.startswith(" (+")
                   else "📈 Players growing, but few new copies yet" if chg.startswith(" (+")
                   else "🧬 Copies arriving, players not growing yet" if last["new7"] > last["new7_prev"]
                   else "▫️ Not trending right now")
        lines.append(verdict)
    else:
        lines.append(f"No games with \"{w}\" in the title in the bot's database.")
    tops = []
    for r in db.execute("""SELECT g.uid, g.name, d.peak FROM daily d JOIN games g ON g.uid=d.uid
                           WHERE d.day=? AND d.peak IS NOT NULL ORDER BY d.peak DESC""", (_s(_d(today) - timedelta(days=1)),)):
        if re.search(r"\b" + re.escape(w), norm(r["name"])):
            tops.append(r)
            if len(tops) >= 6:
                break
    if tops:
        lines.append("Top games: " + ", ".join(f"[{t['name'][:28]}]({ctx['link'](t['uid'], state).strip('<>')}) {fmt(t['peak'])}"
                                              for t in tops))
    return {"title": f"🌱 Theme: \"{w}\"", "description": "\n".join(lines)[:4000], "color": 0x2ECC71}


def mechanic_answer(state, mech, ctx):
    fmt = ctx["fmt"]
    tab = ctx["I"].mechanic_table(state, ctx["today"])
    r = next((x for x in tab if x["mech"] == mech), None)
    if not r:
        return {"title": f"🧭 {mech}", "description": "No data yet.", "color": 0x1ABC9C}
    chg = f"{r['chg']:+.0f}%" if r["chg"] is not None else "—"
    lines = [f"{r['label']} · **{fmt(r['now'])}** average players this week ({chg} vs last)",
             f"{r['games']} games · {r['new']} new this week · {r['hits']} new hits",
             "Top: " + ", ".join(f"{n[:26]} ({fmt(p)})" for p, n, _ in r["top"])]
    return {"title": f"🧭 {mech}", "description": "\n".join(lines), "color": 0x1ABC9C}


def genre_answer(db, state, genre, ctx):
    fmt, today = ctx["fmt"], ctx["today"]
    rows = db.execute("""SELECT g.uid, g.name, d.peak FROM daily d JOIN games g ON g.uid=d.uid
                         WHERE d.day=? AND g.genre=? ORDER BY d.peak DESC LIMIT 8""",
                      (_s(_d(today) - timedelta(days=1)), genre)).fetchall()
    lines = [f"Top {genre} games yesterday:"] + [f"• [{r['name'][:36]}]({ctx['link'](r['uid'], state).strip('<>')}) — {fmt(r['peak'])}" for r in rows]
    try:
        gt = {x["genre"]: x for x in ctx["HOLD"].genre_table(db, state)}
        x = gt.get(genre)
        if x:
            lines.append(f"🏛️ {_pct(x['share'])} of its games are long-term (median hold {x['median']:.2f}× typical)")
    except Exception:
        pass
    return {"title": f"🎮 Genre: {genre}", "description": "\n".join(lines), "color": 0x1ABC9C}


def help_card(hint=None):
    ex = ["`how is Wash the Car doing`", "`Be a Pirate vs Pilfering Pirates`", "`is chocolate trending`",
          "`tycoon games`", "`what's rising`", "`long term games`", "`what is roblox rewarding`", "`what's coming up`"]
    d = (f"I couldn't match \"{hint}\" to a game or theme.\n\n" if hint else "") + "Try:\n" + "\n".join("• " + e for e in ex)
    return {"title": "❓ Ask the trend bot", "description": d, "color": 0x95A5A6}


def answer(db, state, question, ctx):
    """Returns (content line, [cards])."""
    kind, arg = classify(question, state, db)
    q = f"**Q:** {question[:200]}"
    if kind == "game":
        if not arg:
            return q, [help_card(question)]
        best = arg[0]
        cards = [game_card(db, state, best[1], ctx)]
        others = [n for s, u, n in arg[1:] if s >= 0.5]
        if others:
            cards[0]["footer"] = {"text": "Did you mean: " + " · ".join(o[:30] for o in others)}
        return q, cards
    if kind == "compare":
        cards = []
        for part in arg:
            hits = find_games(state, db, part, 1)
            if hits:
                name, url, lines = game_card(db, state, hits[0][1], ctx, compact=True)
                cards.append({"title": f"🔎 {name[:80]}", "url": url, "description": "\n".join(lines)[:2000], "color": 0x5865F2})
            else:
                cards.append(theme_answer(db, state, part, ctx))
        return q, cards
    if kind == "theme":
        return q, [theme_answer(db, state, arg, ctx)]
    if kind == "mechanic":
        return q, [mechanic_answer(state, arg, ctx)]
    if kind == "genre":
        return q, [genre_answer(db, state, arg, ctx)]
    if kind == "top":
        try:  # refresh forecasts and promotion scores so the board has every signal
            young = {g for g, r in state["games"].items() if ctx["pctx"]["is_young"](r, ctx["today"])}
            ctx["FC"].update(db, state, ctx["today"], young, ctx["I"].mechanics_of)
            state["_promo"] = ctx["P"].score(db, ctx["today"], list(young))
        except Exception:
            pass
        rows = ctx["PR"].watch_board(state, ctx["today"], state.get("cutoff") or 500, ctx["t"], ctx["pctx"], limit=10)
        lines = [ctx["PR"].board_line(x, ctx["pctx"], state) for x in rows] or ["Nothing stands out yet."]
        return q, [{"title": "🎮 Games to watch right now", "description": "\n".join(lines),
                    "footer": {"text": ctx["PR"].LEGEND}, "color": 0xED4245}]
    if kind == "longterm":
        cards = [c for c in ctx["PR"].weekly_cards(db, state, ctx["today"], ctx["pctx"], []) if c and "Long-term" in c["title"]]
        return q, cards or [help_card()]
    if kind == "algorithm":
        cards = [c for c in ctx["PR"].weekly_cards(db, state, ctx["today"], ctx["pctx"], []) if c and "algorithm" in c["title"]]
        return q, cards or [help_card()]
    if kind == "coming":
        ups = ctx["FUT"].upcoming(db, ctx["today"])
        lines = [f"🔮 **{u['name'][:40]}** · {ctx['PR']._when(u)} · {ctx['PR']._status(u)}" for u in ups[:10]] or ["Nothing on the calendar."]
        return q, [{"title": "🔮 Coming up", "description": "\n".join(lines), "color": 0xE91E63}]
    return q, [help_card()]

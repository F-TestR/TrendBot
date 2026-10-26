"""
Presentation: turns everything the bot knows into short, scannable Discord cards.

Daily digest  = 5 cards: Today in 30 seconds · Games to watch · Trends · Coming up · Watchlist
Weekly report = 7 cards: The week in 6 lines · Mechanics · Long-term · Algorithm · Engagement ·
                What lasting games share · Model check — plus the full-length report attached as a file.

Rules: one line per item, the name is the link, numbers before words, at most 4 signal tags per
line, a legend in the footer. Detail lives in the dashboard and the attached full report.
"""
import json
import math
from datetime import datetime, timedelta
from statistics import median

import config as C
import discord_out as DO

BLUE, RED, GREEN, PINK, AMBER, PURPLE, TEAL = 0x5865F2, 0xED4245, 0x2ECC71, 0xE91E63, 0xFAA61A, 0x8E7CC3, 0x1ABC9C
LEGEND = ("Trend Score = chance (%) its players double within 2 weeks, combining every signal · "
          "reasons = what pushed it up most")
LEGEND_TAGS = ("×N growth vs same day last week · 🧭 breakout just started · 📈 forecast peak · 🧠 promotion chance · "
               "🔥 heat · 🎯 breakout chance · ⏱ playtime/player/day")


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def _pct(x, digits=None):
    if digits is None:
        digits = 1 if 0 < abs(x) < 0.095 else 0
    return f"{x * 100:.{digits}f}%"


def name_link(name, url, n=34):
    nm = (name or "?").replace("[", "(").replace("]", ")")
    nm = nm[:n - 1] + "…" if len(nm) > n else nm
    return f"[{nm}]({url})" if url else nm


def card(title, lines, color=BLUE, footer=None, max_lines=10, more=None, optional=False):
    lines = [l for l in lines if l is not None]
    if optional and not lines:
        return None
    extra = len(lines) - max_lines
    body = lines[:max_lines]
    if extra > 0:
        body.append(f"_…and {extra} more{(' — ' + more) if more else ''}_")
    desc = "\n".join(body).strip() or "_Nothing yet._"
    e = {"title": title[:256], "description": desc[:4000], "color": color}
    if footer:
        e["footer"] = {"text": footer[:2048]}
    return e


def _size(e):
    return len(e.get("title", "")) + len(e.get("description", "")) + len((e.get("footer") or {}).get("text", ""))


def post_cards(url, cards, content="", files=None, dry_run=False, label="digest"):
    """Up to 10 cards and ~5,800 characters per message; files go with the last message."""
    cards = [c for c in cards if c]
    if dry_run or not url:
        print(f"----- [{label}] -----" + (f"\n{content}" if content else ""))
        for c in cards:
            print(f"\n## {c['title']}\n{c['description']}" + (f"\n[{c['footer']['text']}]" if c.get("footer") else ""))
        if files:
            print(f"(+ attached: {', '.join(f[0] for f in files)})")
        return
    batches, cur, size = [], [], 0
    for c in cards:
        n = _size(c)
        if cur and (len(cur) >= 10 or size + n > 5800):
            batches.append(cur)
            cur, size = [], 0
        cur.append(c)
        size += n
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches):
        last = i == len(batches) - 1
        DO.send(url, {"content": content if i == 0 else "", "embeds": b, "allowed_mentions": {"parse": []}},
                files if last else None)


# --------------------------------------------------------------- the board ---

def watch_board(state, today, cutoff, t, ctx, limit=8):
    """One ranked list of young games, merging growth, heat, breakout model, promotion model and badges."""
    S, games = ctx["S"], state["games"]
    yday = _s(_d(today) - timedelta(days=1))
    yts = S.yt_stats(state, t)
    preds = state.get("_preds") or {}
    promo = state.get("_promo") or {}
    badges = state.get("badges") or {}
    tsd = state.get("_ts") or {}
    ids = set(S.candidate_games(state, today, 400)) | set(yts) | set(preds) | \
        {u for u, v in promo.items() if v.get("p", 0) >= 0.2} | set(tsd)
    rows = []
    for gid in ids:
        r = games.get(gid)
        if r is None or not ctx["is_young"](r, today):
            continue
        players = S.players_now(state, gid)
        if players < C.BOARD_MIN_PLAYERS:
            continue
        ratio, _ = ctx["growth"](r, yday, cutoff, state.get("baseline_day"))
        h = S.heat(state, gid, today, cutoff, yts) or {"score": 0}
        pm, pr = preds.get(gid), (promo.get(gid) or {}).get("p")
        pt = (badges.get(gid) or {}).get("playtime")
        fc = (state.get("_fc") or {}).get(gid) or {}
        cpf = ((state.get("_cp") or {}).get(gid) or {}).get("fire")
        fpeak = fc.get("peak") if fc.get("status") in ("rising", "early") and fc.get("peak", 0) >= 1.5 * max(players, 1) else None
        new = r["first_seen"] in (today, yday) and not ctx["is_base"](state, r)
        y = yts.get(gid) or {}
        score = (h["score"] + 35 * (pr or 0) + 35 * (pm or 0) + (min(ratio, 5) * 6 if ratio and ratio >= 1.3 else 0)
                 + (8 if new else 0) + (12 if cpf else 0) + (min(10, 4 * math.log2(fpeak / max(players, 1))) if fpeak else 0))
        tags = []
        if ratio and ratio >= 1.3:
            tags.append(f"**×{ratio:.1f}**")
        if cpf:
            tags.append("🧭")
        if fpeak:
            tags.append(f"📈{ctx['fmt'](fpeak)}")
        if pr is not None and pr >= 0.15:
            tags.append(f"🧠{pr * 100:.0f}%")
        if h["score"] >= 25:
            tags.append(f"🔥{h['score']}")
        if pm is not None and pm >= 0.1:
            tags.append(f"🎯{min(pm, 0.95) * 100:.0f}%")
        if pt:
            tags.append(f"⏱{pt:.0f}m")
        if y.get("views", 0) >= 100_000:
            tags.append(f"📺{ctx['fmt'](y['views'])}")
        if new:
            tags.append("🆕")
        tsv = tsd.get(gid)
        if tsv:
            score = tsv["score"] * 1000 + score  # the Trend Score leads; the old score only breaks ties
        rows.append({"gid": gid, "name": r["name"], "players": players, "score": score, "tags": tags[:5],
                     "ts": tsv["score"] if tsv else None, "why": tsv["reasons"] if tsv else [],
                     "fc": fc or None, "cp": bool(cpf), "life": ((state.get("_life") or {}).get(gid) or {}).get("days"),
                     "ratio": ratio, "heat": h["score"], "promo": pr, "model": pm, "playtime": pt, "new": new,
                     "age": ctx["age_days"](r, today)})
    rows.sort(key=lambda x: -x["score"])
    return rows[:limit]


def board_line(x, ctx, state):
    url = ctx["link"](x["gid"], state).strip("<>")
    age = f" · {x['age']}d old" if x.get("age") is not None else ""
    if x.get("ts") is not None:
        why = (" · " + " · ".join(x["why"][:2])) if x.get("why") else ""
        return f"**{x['ts']}** · **{name_link(x['name'], url)}** — {ctx['fmt'](x['players'])} playing{age}{why}"
    tags = (" · " + " ".join(x["tags"])) if x["tags"] else ""
    return f"**{name_link(x['name'], url)}** — {ctx['fmt'](x['players'])} playing{age}{tags}"


# ---------------------------------------------------------------- digest ---

def digest_cards(db, state, today, cutoff, t, ctx):
    S, T, FUT, fmt = ctx["S"], ctx["T"], ctx["FUT"], ctx["fmt"]
    games = state["games"]
    yday = _s(_d(today) - timedelta(days=1))
    lk = lambda gid: ctx["link"](gid, state).strip("<>")
    nm = lambda gid: S.game_name(state, gid)
    board = watch_board(state, today, cutoff, t, ctx, limit=12)

    # --- headline picks (one per category, no repeats)
    used, head = set(), []
    def pick(rows, key, minimum):
        for x in sorted(rows, key=lambda x: -(x[key] or 0)):
            if (x[key] or 0) >= minimum and x["gid"] not in used:
                used.add(x["gid"])
                return x
        return None
    allb = watch_board(state, today, cutoff, t, ctx, limit=60)
    x = pick(allb, "ts", 50)
    if x:
        why = f" ({', '.join(x['why'][:2])})" if x.get("why") else ""
        head.append(f"🚀 **Highest Trend Score:** {name_link(x['name'], lk(x['gid']))} — **{x['ts']}**{why}")
    x = pick(allb, "ratio", 1.5)
    if x:
        head.append(f"🚀 **Biggest riser:** {name_link(x['name'], lk(x['gid']))} — ×{x['ratio']:.1f} to {fmt(x['players'])}")
    x = pick(allb, "promo", 0.2)
    if x:
        head.append(f"🧠 **Roblox likely to push next:** {name_link(x['name'], lk(x['gid']))} — {_pct(x['promo'])}")
    fcs = [x for x in allb if x.get("fc") and x["fc"].get("status") == "rising" and x["fc"]["peak"] >= 2 * max(x["players"], 1)]
    if fcs:
        x = max(fcs, key=lambda x: x["fc"]["peak"])
        if x["gid"] not in used:
            used.add(x["gid"])
            when = f" by {_d(x['fc']['peak_day']).strftime('%a')}" if x["fc"].get("peak_day") else ""
            head.append(f"📈 **Biggest forecast:** {name_link(x['name'], lk(x['gid']))} — {fmt(x['players'])} now, "
                        f"on track for ~{fmt(x['fc']['peak'])}{when}")
    x = pick(allb, "heat", 30)
    if x:
        head.append(f"🔥 **Hottest across platforms:** {name_link(x['name'], lk(x['gid']))} — heat {x['heat']}")
    x = pick(allb, "playtime", 1)
    if x and x["playtime"] >= C.BOARD_PLAYTIME_HEADLINE:
        head.append(f"⏱ **Most playtime per player:** {name_link(x['name'], lk(x['gid']))} — {x['playtime']:.0f} min/day")
    th = state.get("_themes") or []
    # only show the theme model's % once it has passed its test on unseen data; until then show signal counts
    ts = ctx["W"].meta_get(db, "theme_model_status", {}) or {}
    if not (ts.get("test_auc") or 0) >= C.MODEL_TRUST_AUC:
        th = [(None, sc, k, r, f) for p, sc, k, r, f in th]
        th.sort(key=lambda x: (-x[1], -x[3]["new7"]))
    th = [(min(p, 0.95) if p is not None else None, sc, k, r, f) for p, sc, k, r, f in th]
    if th:
        p, sc, k, r, fired = th[0]
        pct = _pct(p) if p is not None else f"{sc} signal{'s' if sc != 1 else ''}"
        head.append(f"🌱 **Theme to watch:** \"{T.display(k, state)}\" — {pct}, {r['new7']} new games this week")
    ups = []
    try:
        ups = FUT.upcoming(db, today)
    except Exception:
        pass
    if ups:
        u = next((u for u in ups if u["roblox"] and u["roblox"]["new7"]), ups[0])
        when = _when(u)
        head.append(f"🔮 **Coming up:** {u['name'][:40]} ({when}) — {_status(u)}")
    drops = _watch_rows(state, today, ctx)
    falling = [w for w in drops if w["pct"] is not None and w["pct"] <= -C.WATCH_DROP_PCT]
    if falling:
        w = min(falling, key=lambda w: w["pct"])
        head.append(f"⚠️ **Watchlist falling:** {w['label']} {w['pct']:+.0f}% week on week")
    if not head:
        head.append("Quiet day — nothing crossed the alert thresholds. Full tables are in the dashboard.")
    dbs = state.get("_dbstats") or {}
    c1 = card(f"📊 Daily digest · {_d(today).strftime('%a %d %b')}", head, BLUE,
              footer=f"{len(games):,} games tracked · {dbs.get('daily', 0):,} game-days stored · "
                     f"comparing {_d(yday).strftime('%A')} with the same kind of day last week")

    # --- games to watch
    has_ts = any(x.get("ts") is not None for x in board)
    mode = state.get("ts_mode") or "starting formula"
    c2 = card("🎮 Games to watch · ranked by Trend Score" if has_ts else "🎮 Games to watch",
              [board_line(x, ctx, state) for x in board[:C.BOARD_ROWS]], RED,
              footer=(LEGEND + f" · {mode}") if has_ts else LEGEND_TAGS, max_lines=C.BOARD_ROWS)
    if not board:
        c2["description"] = "_Builds up over the first week — growth needs a week of history to compare against._"

    # --- trends
    tl = []
    for p, sc, k, r, fired in th[:4]:
        pct = f"**{_pct(p)}**" if p is not None else f"{sc} signal{'s' if sc != 1 else ''}"
        tl.append(f"🌱 \"{T.display(k, state)}\" · {pct} · {r['games']} games, {r['new7']} new · {fmt(r['ccu'])} players")
    for kw, rs in _copy_clusters(state, today, ctx)[:3]:
        tl.append(f"🧬 \"{kw}\" in {len(rs)} new titles: " + ", ".join(x["name"][:20] for x in rs[:3]))
    brs = state.get("_bridges") or []
    if brs:
        tl.append("🌉 Reaching Roblox from outside: " + ", ".join(f"\"{w}\" ({row['new7']})" for w, _, row in brs[:4]))
    try:
        sw, _ = S.rising_title_words(state, t, shorts=True)
        if sw:
            tl.append("🎬 Rising in YouTube Shorts: " + ", ".join(f"\"{g}\"" for n, p, g in sw[:5]))
        words, have_prev = S.rising_title_words(state, t, shorts=False)
        if words:
            tl.append("🗣️ Rising in YouTube video titles: " + ", ".join(f"\"{g}\"" for n, p, g in words[:5]))
    except Exception:
        pass
    c3 = card("🌱 Trends", tl, GREEN, footer="🌱 theme model chance · 🧬 copy wave · 🌉 outside-Roblox word now in new games",
              max_lines=9, optional=True)

    # --- coming up & outside roblox
    cl = []
    for u in ups[:C.FUTURE_DIGEST_ITEMS]:
        cl.append(f"🔮 **{u['name'][:38]}** · {_when(u)} · {_status(u)}")
    ust = state.get("upstream", {})
    if ust.get("steam_rising"):
        cl.append("🎮 Steam climbers: " + ", ".join(x["name"][:24] for x in ust["steam_rising"][:3]))
    if ust.get("wiki_spikes"):
        cl.append("📚 Wikipedia spikes: " + ", ".join(w[:24] for w in ust["wiki_spikes"][:3]))
    if ust.get("tw_top_new"):
        cl.append("🟣 New on Twitch: " + ", ".join(w[:24] for w in ust["tw_top_new"][:3]))
    c4 = card("🔮 Coming up & outside Roblox", cl, PINK,
              footer="✨ not on Roblox yet = first-mover chance · 🌉 already appearing in new Roblox games", max_lines=10,
              optional=True)

    # --- watchlist
    wl = []
    for w in drops:
        if w["now"] is None:
            wl.append(f"▫️ {w['label']} · not in the top list yesterday")
            continue
        arrow = "🔺" if (w["pct"] or 0) >= 5 else ("🔻" if (w["pct"] or 0) <= -5 else "▫️")
        bits = [fmt(w["now"])]
        if w["pct"] is not None:
            bits.append(f"{w['pct']:+.0f}%")
        b = (state.get("badges") or {}).get(w["gid"]) or {}
        if b.get("playtime"):
            bits.append(f"⏱{b['playtime']:.0f}m")
        if b.get("returning") is not None:
            bits.append(f"↩{_pct(b['returning'])}")
        wl.append(f"{arrow} **{name_link(w['label'], lk(w['gid']))}** · " + " · ".join(bits))
    yu = state["requests"].get(yday, 0)
    c5 = card("👀 Watchlist", wl, AMBER, max_lines=12,
              footer=f"vs same day last week · ↩ returning players · RoWatcher {yu}/1,000 requests yesterday · "
                     f"full tables in dashboard.html") if wl else None
    state["_head"] = head
    state["_board"] = board
    return [c1, c2, c3, c4, c5]


def _when(u):
    if u["days"] is None:
        return "date tbc"
    if u["days"] <= 0:
        return "out now"
    return f"in {u['days']} day{'s' if u['days'] != 1 else ''}"


def _status(u):
    rb = u["roblox"]
    if rb and rb["new7"]:
        return f"🌉 {rb['new7']} new Roblox game{'s' if rb['new7'] != 1 else ''} already"
    if rb and rb["games"]:
        return f"{rb['games']} older Roblox games"
    return "✨ not on Roblox yet"


def _watch_rows(state, today, ctx):
    games = state["games"]
    yday = _s(_d(today) - timedelta(days=1))
    prev = _s(_d(yday) - timedelta(days=7))
    out = []
    for gid, label in C.WATCHLIST.items():
        r = games.get(gid)
        now = (r or {}).get("days", {}).get(yday)
        p = (r or {}).get("days", {}).get(prev)
        out.append({"gid": gid, "label": label, "now": now, "pct": ((now / p - 1) * 100) if now and p else None})
    return out


def _copy_clusters(state, today, ctx):
    games = state["games"]
    week_ago = _d(today) - timedelta(days=7)
    by_kw = {}
    for gid, r in games.items():
        if not ctx["is_base"](state, r) and _d(r["first_seen"]) >= week_ago:
            for kw in ctx["keywords"](r["name"]):
                by_kw.setdefault(kw, []).append(r)
    out, seen = [], set()
    for kw, rs in sorted(by_kw.items(), key=lambda x: -len(x[1])):
        key = frozenset(id(r) for r in rs)
        if len(rs) >= 3 and key not in seen:
            seen.add(key)
            out.append((kw, rs))
    return out


# ---------------------------------------------------------------- weekly ---

def _bar(w, scale):
    n = max(1, min(6, int(round(abs(w) / (scale or 1) * 6))))
    return ("🟩" if w > 0 else "🟥") * n


def weekly_cards(db, state, today, ctx, table):
    S, I, L, T, HOLD, E, BD, P, fmt = (ctx[k] for k in ("S", "I", "L", "T", "HOLD", "E", "BD", "P", "fmt"))
    lk = lambda gid: ctx["link"](gid, state).strip("<>")
    nm = lambda gid: S.game_name(state, gid)
    young = {g for g, r in state["games"].items() if ctx["is_young"](r, today)}
    head = []

    # mechanics
    rows = [r for r in table if r["chg"] is not None]
    if rows:
        up = max(rows, key=lambda r: r["chg"])
        dn = min(rows, key=lambda r: r["chg"])
        gaps = [r for r in table if r["label"].startswith("🟢")]
        head.append(f"🧭 **Demand:** {up['mech']} {up['chg']:+.0f}% · {dn['mech']} {dn['chg']:+.0f}%"
                    + (f" · best opening: **{gaps[0]['mech']}**" if gaps else ""))
    ml = []
    for r in sorted(table, key=lambda r: (not r["label"].startswith("🟢"), -abs(r["chg"] or 0)))[:6]:
        chg = f"{r['chg']:+.0f}%" if r["chg"] is not None else "—"
        ml.append(f"{(r['label'].split() or ['▫️'])[0]} **{r['mech']}** · {fmt(r['now'])} ({chg}) · {r['new']} new"
                  + (f" · {r['hits']} hit{'s' if r['hits'] != 1 else ''}" if r["hits"] else ""))
    life = I.ins_state(state)["life"]
    wk = _s(_d(today) - timedelta(days=7))
    brk = sorted([(g, r) for g, r in life.items() if r["broke"] >= wk and not r.get("pre")], key=lambda x: -x[1]["peak"])
    if brk:
        ml.append(f"💥 {len(brk)} breakout{'s' if len(brk) != 1 else ''}: " +
                  ", ".join(name_link(r["name"], lk(g), 22) for g, r in brk[:3]))
    c_mech = card("🧭 Mechanics: biggest moves", ml, TEAL,
                  footer="🟢 open gap · 🟡 growing but crowding · 🔴 saturating · avg players this week (vs last) · all mechanics in the dashboard")

    # long-term
    lt = state.get("longterm") or {}
    ll = []
    try:
        gt = HOLD.genre_table(db, state)
    except Exception:
        gt = []
    if gt:
        g0 = gt[0]
        head.append(f"🏛️ **Most long-term genre:** {g0['genre']} — {_pct(g0['share'])} of its games hold players on weekdays")
    for r in gt[:5]:
        ll.append(f"**{r['genre']}** · {_pct(r['share'])} long-term ({r['lt']}/{r['games']}) · hold {r['median']:.2f}×")
    ylt = sorted(((v["players"], u, v) for u, v in lt.items() if v["status"] == "long-term" and u in young), reverse=True)[:3]
    if ylt:
        ll.append("Young games already long-term: " + ", ".join(name_link(nm(u), lk(u), 24) for _, u, _ in ylt))
    st = state.get("stick") or {}
    sy = sorted(((v["score"], u) for u, v in st.items() if v.get("score") is not None and u in young), reverse=True)[:3]
    if sy:
        ll.append("Stickiest young games: " + ", ".join(f"{name_link(nm(u), lk(u), 22)} ({s:.0f})" for s, u in sy))
        head.append(f"📏 **Stickiest young game:** {name_link(nm(sy[0][1]), lk(sy[0][1]))} — {sy[0][0]:.0f}/100")
    c_lt = card("🏛️ Long-term games", ll, PURPLE,
                footer="long-term = holds its weekend crowd on Tue–Wed better than a typical game, most weeks")

    # algorithm
    pst = ctx["W"].meta_get(db, "promo_status", {}) or {}
    rw = P.rewarded(pst)
    al = []
    if rw:
        scale = max(abs(w) for _, w in rw)
        for f, w in rw[:6]:
            al.append(f"{_bar(w, scale)} {P.LABEL[f].split(' (')[0]}")
        top2 = [P.LABEL[f].split(" (")[0] for f, w in rw[:2] if w > 0]
        if top2:
            head.append(f"🧠 **Roblox is rewarding:** {' and '.join(top2)}")
        accs = [f"{t} {(pst.get(t) or {}).get('test_auc'):.2f}" for t in P.TARGETS if (pst.get(t) or {}).get("test_auc") is not None]
        if accs:
            al.append(f"Accuracy on unseen days: {' · '.join(accs)} (0.5 = coin flip)")
        sh = P.shifts(db)
        if sh and sh[0]:
            moves, old = sh
            msg = "; ".join(f"{P.LABEL[f].split(' (')[0]} {'↑' if b > a else '↓'}" for f, a, b in moves[:3])
            al.append(f"⚠️ **Changed since {old[5:]}:** {msg}")
            head.append(f"⚠️ **Algorithm change:** {msg}")
    else:
        why = "; ".join(f"{(pst.get(t) or {}).get('why', 'not trained')}" for t in P.TARGETS) or "not trained yet"
        al.append(f"_Still learning — {why}._")
    c_al = card("🧠 What Roblox's algorithm is rewarding", al, BLUE,
                footer="learned from which games Roblox charted or grew 50%+ the next week · bars = relative weight")

    # engagement (badges)
    b = state.get("badges") or {}
    el = []
    pts = [v["playtime"] for v in b.values() if v.get("playtime")]
    if pts:
        rets = [v["returning"] for v in b.values() if v.get("returning") is not None]
        el.append(f"Typical game: **{median(pts):.0f} min** per player per day"
                  + (f" · {_pct(median(rets))} returning" if rets else "") + f" ({len(b)} games measured)")
    tp = sorted(((v["playtime"], u, v) for u, v in b.items() if v.get("playtime") and u in young and (v.get("dau") or 0) >= 2000),
                reverse=True)[:4]
    for p, u, v in tp:
        el.append(f"⏱ {name_link(nm(u), lk(u))} · **{p:.0f} min** · {fmt(v['dau'])}/day"
                  + (f" · ↩{_pct(v['returning'])}" if v.get("returning") is not None else ""))
    if tp:
        head.append(f"⏱ **Most playtime (young):** {name_link(nm(tp[0][1]), lk(tp[0][1]))} — {tp[0][0]:.0f} min/player/day")
    sk = sorted(((v["streak7"][1], u) for u, v in b.items() if v.get("streak7") and v.get("base") == "new players"), reverse=True)[:3]
    if sk:
        el.append("🔁 Best 7-day streak retention: " + ", ".join(f"{name_link(nm(u), lk(u), 22)} {_pct(s, 1)}" for s, u in sk))
    c_en = card("⏱ Engagement (from badges)", el, AMBER, optional=True,
                footer="players/day from badge win rates · ↩ returning players · streak = share of new players reaching it")

    # what lasting games share + survival check
    sl = []
    try:
        fr = E.feature_report(db, state)
        for r in [x for x in fr["rows"] if x["lift"]][:5]:
            sl.append(f"{'✅' if r['lift'] >= 1.2 else '▫️'} {r['feature']} · **{r['lift']:.1f}×** as likely to be long-term")
        bt = E.backtest(db)
        if bt.get("bands"):
            hi, lo = bt["bands"].get("70+"), bt["bands"].get("under 40")
            if hi and lo and abs(hi["median_kept"] - lo["median_kept"]) >= 0.05:
                sl.append(f"🧪 Stickiness 70+ kept {_pct(hi['median_kept'])} of players 4 weeks later vs {_pct(lo['median_kept'])} for under 40")
    except Exception:
        pass
    c_sh = card("🧩 What lasting games have in common", sl, GREEN, footer="from game descriptions · correlation, not proof",
                optional=True)

    # model check
    ck = []
    ms = ctx["W"].meta_get(db, "model_status", {}) or {}
    if ms.get("test_auc") is not None:
        ck.append(f"🎯 Breakout model: accuracy **{ms['test_auc']:.2f}** · top picks hit {_pct(ms['test_top10_hit'])} vs {_pct(ms['base_rate'])} average")
    ts = ctx["W"].meta_get(db, "theme_model_status", {}) or {}
    if ts.get("test_auc") is not None:
        ck.append(f"🌱 Theme model: accuracy **{ts['test_auc']:.2f}** · top picks hit {_pct(ts['test_top5_hit'])} vs {_pct(ts['base_rate'], 1)}")
    try:
        sc = P.scorecard(db, today) or {}
        for t, r in sc.items():
            ck.append(f"🧠 Promotion ({t}) live check: **{r['auc']:.2f}** · top picks {_pct(r['top10'])} vs {_pct(r['base'])}")
    except Exception:
        pass
    try:
        irows, nb, _ = T.indicator_report(db, today)
        good = [r for r in irows if r["done"] and r.get("lift")]
        good.sort(key=lambda r: -r["lift"])
        for r in good[:3]:
            lead = f", ~{r['lead']:.0f} days' warning" if r["lead"] is not None else ""
            ck.append(f"🔬 {r['label']}: **{r['lift']:.1f}×** better than chance{lead}")
    except Exception:
        pass
    try:
        ck = ctx["TS"].weekly_lines(db, state, today) + ck
    except Exception:
        pass
    if ms.get("test_auc") is not None:
        head.append(f"🎯 **Model check:** breakout model accuracy {ms['test_auc']:.2f} (0.5 = coin flip)")
    if not ck:
        ck.append("_Models are still collecting examples — accuracy appears once they've been tested on unseen data._")
    c_ck = card("🔬 Are the predictions working?", ck, RED, footer="accuracy = AUC on data the model never saw · 0.5 coin flip, 1.0 perfect")

    fl = ctx["FC"].weekly_lines(state, fmt)
    c_fc = card("📈 Forecasts & how long hits last", fl, TEAL, optional=True,
                footer="peak = S-curve fitted to each game's rise · start signal = Bayesian change-point detection · "
                       "lifespan = Kaplan-Meier half-life (days until below half the peak)")
    if not head:
        head.append("Still building history — most sections fill in over the first 2–3 weeks.")
    c0 = card(f"🗓️ Weekly report · week to {_d(today).strftime('%a %d %b')}", head[:7], BLUE,
              footer="full-length report attached (weekly_report.md) · tables in the dashboard")
    mo = state.get("_money") or []
    c_mo = None
    if mo:
        M = ctx["MO"]
        gl = sorted(M.groups(mo, "genre"), key=lambda g: -g["per_player"])[:5]
        ml = [f"**{len(mo):,} games** (400+ players) · typical **{M.usd(median(r['monthly'] for r in mo))}/month**"]
        ml += [f"💰 **{g['group']}** — {M.usd(g['median'])} typical · {M.usd(g['top25'])} top-quartile · "
               f"**{M.usd(g['per_player'])}**/player" for g in gl]
        small = sorted([r for r in mo if r["ccu"] < 5000], key=lambda r: -r["monthly"])[:3]
        if small:
            ml.append("Top earners under 5K players: " + ", ".join(
                f"{name_link(r['name'], lk(r['uid']), 22)} {M.usd(r['monthly'])}" for r in small))
        c_mo = card("💰 What earns the most", ml, AMBER,
                    footer="RoWatcher revenue estimates, last 7 days · $/player = monthly $ per concurrent player · "
                           "full tables: reports/money.md")
        g0 = gl[0] if gl else None
        if g0:
            head.append(f"💰 **Best-earning genre per player:** {g0['group']} — {M.usd(g0['per_player'])}/player/month")
        c0["description"] = "\n".join(head[:8])
    return [c0, c_mech, c_al, c_lt, c_en, c_sh, c_fc, c_mo, c_ck]

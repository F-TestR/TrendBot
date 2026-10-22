"""A single self-contained dashboard.html, attached to the daily digest."""
import html
from datetime import datetime, timedelta

import config as C
import insights as I
import sources as S

HOOKS = {}  # bot.py fills in: fmt, is_young, age_days, growth


def _e(s):
    return html.escape(str(s), quote=True)


def spark(days, today, n=14, w=120, h=30):
    ds = [(datetime.strptime(today, "%Y-%m-%d") - timedelta(days=n - 1 - i)).strftime("%Y-%m-%d") for i in range(n)]
    vals = [days.get(d) for d in ds]
    known = [v for v in vals if v]
    if len(known) < 2:
        return '<span class="muted">—</span>'
    lo, hi = min(known), max(known)
    rng = (hi - lo) or 1
    pts = []
    for i, v in enumerate(vals):
        if v:
            x = i * (w - 4) / (n - 1) + 2
            y = h - 3 - (v - lo) / rng * (h - 6)
            pts.append(f"{x:.1f},{y:.1f}")
    up = known[-1] >= known[0]
    color = "var(--up)" if up else "var(--down)"
    last = pts[-1].split(",")
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
            f'<polyline fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" points="{" ".join(pts)}"/>'
            f'<circle cx="{last[0]}" cy="{last[1]}" r="2.4" fill="{color}"/></svg>')


def _num(v, fmt):
    return f'<td data-v="{v if v is not None else -1}">{fmt(v) if v else "—"}</td>'


def build(state, today, cutoff):
    fmt, is_young, age_days, growth = HOOKS["fmt"], HOOKS["is_young"], HOOKS["age_days"], HOOKS["growth"]
    games = state["games"]
    t = datetime.strptime(today, "%Y-%m-%d")
    from datetime import timezone
    yts = S.yt_stats(state, t.replace(hour=23, tzinfo=timezone.utc))
    yday = (t - timedelta(days=1)).strftime("%Y-%m-%d")

    # --- rows: young games with heat, plus watchlist
    ids = set(S.candidate_games(state, today, 400)) | set(yts) | set(C.WATCHLIST)
    rows = []
    for gid in ids:
        r = games.get(gid)
        h = S.heat(state, gid, today, cutoff, yts) or {"score": 0, "signals": [], "parts": {}}
        if r is None and not h["parts"]:
            continue
        name = S.game_name(state, gid)
        ratio = None
        if r:
            ratio, _ = growth(r, yday, cutoff, state.get("baseline_day"))
        p = h["parts"]
        y = p.get("yt") or {}
        tw = p.get("twitch")
        comm = p.get("group") or p.get("discord")
        rows.append({
            "gid": gid, "name": name, "watch": gid in C.WATCHLIST,
            "young": bool(r and is_young(r, today)) or r is None,
            "players": S.players_now(state, gid), "days": (r or {}).get("days", {}),
            "ratio": ratio, "heat": h["score"], "signals": h["signals"],
            "yt_n": y.get("n"), "yt_v": y.get("views"), "tw": tw[0] if tw else None,
            "comm": comm[1] if comm and comm[1] is not None else None,
            "likes": p.get("likes"), "age": age_days(r, today) if r else None,
            "model": (state.get("_preds") or {}).get(gid),
            "mech": ", ".join(I.mechanics_of(name)) or "",
            "link": (S.roblox_link(state, gid) or f"<https://rowatcher.com/games/{gid}>").strip("<>"),
        })
    rows.sort(key=lambda x: (-x["heat"], -x["players"]))
    hot = [x for x in rows if x["young"]][:60]
    watch = [x for x in rows if x["watch"]]

    def table(rs, tid):
        out = [f'<table id="{tid}" class="sortable"><thead><tr>'
               '<th data-t="s">Game</th><th>Players</th><th class="nosort">Last 14 days</th><th>Growth</th>'
               '<th>Heat</th><th>Model</th><th>YouTube 48h</th><th>Twitch</th><th>Community</th><th>👍</th><th>Age</th>'
               '<th data-t="s">Type</th></tr></thead><tbody>']
        for x in rs:
            ratio_s = f"{x['ratio']:.1f}×" if x["ratio"] else "—"
            comm_s = f"{x['comm']:+.1f}%" if x["comm"] is not None else "—"
            likes_s = f"{x['likes'] * 100:.0f}%" if x["likes"] else "—"
            model_s = f"{x['model'] * 100:.0f}%" if x["model"] is not None else "—"
            sig = "".join(f'<span class="tag">{_e(s)}</span>' for s in x["signals"])
            heat_cls = "hot" if x["heat"] >= C.HEAT_ALERT_SCORE else ("warm" if x["heat"] >= 30 else "")
            out.append(
                f'<tr><td data-v="{_e(x["name"].lower())}"><a href="{_e(x["link"])}" target="_blank" rel="noopener">{_e(x["name"][:48])}</a>'
                f'{" <span class=star>★</span>" if x["watch"] else ""}</td>'
                + _num(x["players"], fmt)
                + f'<td>{spark(x["days"], today)}</td>'
                + f'<td data-v="{x["ratio"] or -1}">{ratio_s}</td>'
                + f'<td data-v="{x["heat"]}"><span class="heat {heat_cls}">{x["heat"]}</span> {sig}</td>'
                + f'<td data-v="{x["model"] if x["model"] is not None else -1}">{model_s}</td>'
                + f'<td data-v="{x["yt_v"] or -1}">{(str(x["yt_n"]) + " · " + fmt(x["yt_v"]) + " views") if x["yt_n"] else "—"}</td>'
                + _num(x["tw"], fmt)
                + f'<td data-v="{x["comm"] if x["comm"] is not None else -999}">{comm_s}</td>'
                + f'<td data-v="{x["likes"] or -1}">{likes_s}</td>'
                + f'<td data-v="{x["age"] if x["age"] is not None else 99999}">{(str(x["age"]) + "d") if x["age"] is not None else "—"}</td>'
                + f'<td data-v="{_e(x["mech"])}">{_e(x["mech"]) or "—"}</td></tr>')
        out.append("</tbody></table>")
        return "".join(out)

    # --- mechanics
    mt = I.mechanic_table(state, today)
    def _chg(m):
        return f"{m['chg']:+.0f}%" if m["chg"] is not None else "—"
    mech_rows = "".join(
        f'<tr><td data-v="{_e(m["mech"])}">{_e(m["label"])} <b>{_e(m["mech"])}</b></td>'
        f'<td data-v="{m["now"]}">{fmt(m["now"])}</td>'
        f'<td data-v="{m["chg"] if m["chg"] is not None else -999}">{_chg(m)}</td>'
        f'<td data-v="{m["games"]}">{m["games"]}</td><td data-v="{m["new"]}">{m["new"]}</td><td data-v="{m["hits"]}">{m["hits"]}</td>'
        f'<td>{_e(", ".join(n[:24] for _, n, _ in m["top"]))}</td></tr>' for m in mt)

    # --- lifecycle
    life = I.ins_state(state)["life"]
    lrows = []
    for gid, r in sorted(life.items(), key=lambda kv: kv[1]["broke"], reverse=True)[:80]:
        days_to_peak = (datetime.strptime(r["peak_day"], "%Y-%m-%d") - datetime.strptime(r["broke"], "%Y-%m-%d")).days
        lrows.append(f'<tr><td data-v="{_e(r["name"].lower())}">{_e(r["name"])}</td><td data-v="{r["broke"]}">{"before tracking" if r.get("pre") else r["broke"][5:]}</td>'
                     f'<td data-v="{r["age"] if r.get("age") is not None else 99999}">{(str(r["age"]) + "d") if r.get("age") is not None else "—"}</td>'
                     f'<td data-v="{r["peak"]}">{fmt(r["peak"])}</td><td data-v="{days_to_peak}">{days_to_peak}d</td>'
                     f'<td>{_e(I.life_status(r, today))}</td><td>{_e(", ".join(r["mech"]))}</td></tr>')

    # --- updates
    urows = []
    for e in sorted(I.ins_state(state)["updates"], key=lambda e: e["date"], reverse=True)[:80]:
        cells = "".join(f'<td data-v="{e.get(k, -999)}" class="{"up" if e.get(k, 0) > 0 else ("down" if e.get(k, 0) < 0 else "")}">'
                        f'{(str(e[k]) if e[k] <= 0 else "+" + str(e[k])) + "%" if k in e else "…"}</td>' for k in ("d1", "d3", "d7"))
        urows.append(f'<tr><td data-v="{_e(e["name"].lower())}">{_e(e["name"])}</td><td data-v="{e["date"]}">{e["date"][5:]}</td>'
                     f'<td data-v="{e.get("before") or -1}">{fmt(e["before"]) if e.get("before") else "—"}</td>{cells}</tr>')

    # --- themes
    import themes as T
    trows = []
    for p, sc, k, r, fired in (state.get("_themes") or [])[:60]:
        prob = f"{p*100:.0f}%" if p is not None else "—"
        sig = "".join(f'<span class="tag">{_e(T.INDICATORS[i][0])}</span>' for i in fired)
        trows.append(f'<tr><td data-v="{_e(T.display(k, state).lower())}"><b>{_e(T.display(k, state))}</b></td>'
                     f'<td data-v="{p if p is not None else -1}">{prob}</td><td data-v="{sc}">{sc}</td>'
                     f'<td data-v="{r["ccu"]}">{fmt(r["ccu"])}</td><td data-v="{r["games"]}">{r["games"]}</td>'
                     f'<td data-v="{r["new7"]}">{r["new7"]}</td><td data-v="{r["studios7"]}">{r["studios7"]}</td>'
                     f'<td data-v="{r["hits"]}">{r["hits"]}</td><td>{sig or "—"}</td></tr>')
    brs = state.get("_bridges") or []
    bridge_html = ""
    if brs:
        bridge_html = '<p class="note"><b>🌉 Outside trends already reaching Roblox:</b> ' + ", ".join(
            f'"{_e(w)}" ({row["new7"]} new games)' for w, _, row in brs[:10]) + "</p>"

    reqs = state["requests"].get(yday, 0)
    yt_units = S.src_state(state)["yt_units"].get(yday, 0)
    tw_total = S.src_state(state)["tw_total"].get(yday) or S.src_state(state)["tw_total"].get(today)
    stats = [("Games tracked", fmt(len(games))), ("Breakouts logged", str(len(life))),
             ("Updates measured", str(len(I.ins_state(state)["updates"]))),
             ("Roblox on Twitch (peak)", fmt(tw_total) if tw_total else "—")]
    stat_html = "".join(f'<div class="stat"><div class="sv">{_e(v)}</div><div class="sl">{_e(k)}</div></div>' for k, v in stats)

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Roblox Trend Dashboard</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--fg:#1d2026;--muted:#6b7280;--line:#e5e7eb;--up:#16a34a;--down:#dc2626;--accent:#5865F2;--hot:#dc2626;--warm:#d97706}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1e1f22;--card:#2b2d31;--fg:#e3e5e8;--muted:#9aa0a6;--line:#3f4147;--up:#3ba55d;--down:#ed4245;--accent:#7983f5;--hot:#ed4245;--warm:#faa61a}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
header{{padding:20px 16px 8px;max-width:1300px;margin:auto}}h1{{font-size:20px;margin:0 0 4px}}.muted{{color:var(--muted)}}
main{{max-width:1300px;margin:auto;padding:0 16px 40px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}}
.stat{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}.sv{{font-size:22px;font-weight:700}}.sl{{color:var(--muted);font-size:12px}}
nav{{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}}nav button{{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:6px 14px;cursor:pointer;font:inherit}}
nav button.on{{background:var(--accent);color:#fff;border-color:var(--accent)}}
section{{display:none}}section.on{{display:block}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:auto}}
input[type=search]{{width:100%;max-width:340px;padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit;margin:4px 0 10px}}
table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap;vertical-align:middle}}
th{{position:sticky;top:0;background:var(--card);font-size:12px;color:var(--muted);cursor:pointer;user-select:none}}th.nosort{{cursor:default}}
td a{{color:var(--fg);text-decoration:none;font-weight:600}}td a:hover{{color:var(--accent)}}
.tag{{display:inline-block;font-size:11px;padding:1px 6px;border-radius:999px;background:var(--line);margin-left:3px}}
.heat{{display:inline-block;min-width:30px;text-align:center;font-weight:700;border-radius:6px;padding:1px 6px;background:var(--line)}}
.heat.hot{{background:var(--hot);color:#fff}}.heat.warm{{background:var(--warm);color:#fff}}.star{{color:#f5b700}}
td.up{{color:var(--up);font-weight:600}}td.down{{color:var(--down);font-weight:600}}
p.note{{color:var(--muted);font-size:12.5px;margin:8px 2px}}
</style></head><body>
<header><h1>Roblox Trend Dashboard</h1><div class="muted">Updated {_e(datetime.strptime(today, "%Y-%m-%d").strftime("%A %d %B %Y"))} · open fresh copies from each day's digest</div>
<div class="stats">{stat_html}</div></header>
<main>
<nav><button class="on" data-s="hot">🔥 Hot young games</button><button data-s="watch">★ Watchlist</button>
<button data-s="themes">🌱 Themes</button><button data-s="mech">🧭 Mechanics</button><button data-s="life">💥 Breakouts</button><button data-s="upd">🛠️ Updates</button></nav>
<section id="hot" class="on"><input type="search" placeholder="Filter games or types…" data-for="t-hot">
<div class="card">{table(hot, "t-hot")}</div><p class="note">Model = the learned chance of reaching the "exploded" level (see weekly report for its accuracy). Heat combines player growth vs last week, YouTube videos/views (48h), Twitch viewers, Roblox group / Discord growth (~2 days) and likes. Click a column to sort.</p></section>
<section id="watch"><div class="card">{table(watch, "t-watch")}</div></section>
<section id="themes"><input type="search" placeholder="Filter themes…" data-for="t-themes">
<div class="card"><table id="t-themes" class="sortable"><thead><tr><th data-t="s">Theme</th><th>Model</th><th>Signals</th><th>Players</th><th>Games</th><th>New this week</th><th>Studios</th><th>2K+ games</th><th class="nosort">Indicators firing</th></tr></thead><tbody>{"".join(trows) or '<tr><td colspan=9 class=muted>No theme data yet.</td></tr>'}</tbody></table></div>
<p class="note">A theme is a word or phrase shared by game titles. "Model" = learned chance that {C.THEME_BREAKOUT_GAMES}+ of its games pass {fmt(C.THEME_HIT_CCU)} players within {C.LABEL_DAYS} days. See the weekly report for which indicators have proven useful.</p>{bridge_html}</section>
<section id="mech"><div class="card"><table class="sortable"><thead><tr><th data-t="s">Mechanic</th><th>Avg players (7d)</th><th>vs last week</th><th>Games</th><th>New this week</th><th>New hits</th><th class="nosort">Top games</th></tr></thead><tbody>{mech_rows}</tbody></table></div>
<p class="note">🟢 open gap = demand up 10%+ with few new games · 🟡 growing but crowding · 🔴 saturating = demand falling while copies keep arriving.</p></section>
<section id="life"><div class="card"><table class="sortable"><thead><tr><th data-t="s">Game</th><th>Broke out</th><th>Age then</th><th>Peak</th><th>Days to peak</th><th class="nosort">Now</th><th class="nosort">Type</th></tr></thead><tbody>{"".join(lrows) or '<tr><td colspan=7 class=muted>No breakouts logged yet.</td></tr>'}</tbody></table></div></section>
<section id="upd"><div class="card"><table class="sortable"><thead><tr><th data-t="s">Game</th><th>Updated</th><th>Players before</th><th>Day 1</th><th>Day 3</th><th>Day 7</th></tr></thead><tbody>{"".join(urows) or '<tr><td colspan=6 class=muted>No updates measured yet.</td></tr>'}</tbody></table></div></section>
</main>
<script>
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('nav button,section').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById(b.dataset.s).classList.add('on')}});
document.querySelectorAll('input[data-for]').forEach(i=>i.oninput=()=>{{const q=i.value.toLowerCase();document.querySelectorAll('#'+i.dataset.for+' tbody tr').forEach(r=>r.style.display=r.textContent.toLowerCase().includes(q)?'':'none')}});
document.querySelectorAll('table.sortable th:not(.nosort)').forEach(th=>th.onclick=()=>{{const tb=th.closest('table').tBodies[0],i=[...th.parentNode.children].indexOf(th),s=th.dataset.t==='s',dir=th.dataset.d=th.dataset.d==='a'?'d':'a';
[...tb.rows].sort((a,b)=>{{let x=a.cells[i]?.dataset.v??'',y=b.cells[i]?.dataset.v??'';if(!s){{x=parseFloat(x);y=parseFloat(y)}}return (x>y?1:x<y?-1:0)*(dir==='a'?1:-1)}}).forEach(r=>tb.appendChild(r))}});
</script></body></html>"""

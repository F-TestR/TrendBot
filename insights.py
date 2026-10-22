"""
Insights: turning the raw numbers into decisions.

  * Mechanics  - groups games by what you do in them (tycoon, anomaly, find-the...)
                 and tracks demand vs. how crowded each one is getting.
  * Updates    - spots when a game publishes an update and measures what it did
                 to players 1, 3 and 7 days later.
  * Lifecycle  - every young game that breaks out gets a record: age when it broke
                 out, how long it took to peak, and how fast it fell after.

All of it uses data the bot already collects, so it costs no extra API calls.
"""
import re
from datetime import datetime, timedelta, timezone
from statistics import median

import config as C

HOOKS = {}  # bot.py fills in: fmt, is_young, age_days, link


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ins_state(state):
    s = state.setdefault("ins", {})
    s.setdefault("last_updated", {})
    s.setdefault("updates", [])
    s.setdefault("life", {})
    return s


# --------------------------------------------------------------- mechanics ---

_WORD = re.compile(r"[a-z]+")


def mechanics_of(name):
    words = set(_WORD.findall(re.sub(r"\[.*?\]|\(.*?\)", " ", name.lower())))
    out = []
    for mech, kws in C.MECHANICS.items():
        for kw in kws:
            if " " in kw:
                if kw in name.lower():
                    out.append(mech)
                    break
            elif kw in words or kw + "s" in words or kw + "es" in words:
                out.append(mech)
                break
    return out


def _avg_high(days, start, end):
    """Average daily high over [start, end] inclusive, missing days = 0 (below the top list)."""
    n = (end - start).days + 1
    tot = 0
    for i in range(n):
        tot += days.get(_s(start + timedelta(days=i)), 0)
    return tot / n


def mechanic_table(state, today):
    """One row per mechanic: demand this week vs last, new games, hits, label."""
    games = state["games"]
    y = _d(today) - timedelta(days=1)
    this_start, last_end, last_start = y - timedelta(days=6), y - timedelta(days=7), y - timedelta(days=13)
    have_last_week = state.get("baseline_day") and _d(state["baseline_day"]) <= last_start
    week_ago = _d(today) - timedelta(days=7)
    rows = {m: {"now": 0.0, "prev": 0.0, "games": 0, "new": 0, "hits": 0, "top": []} for m in C.MECHANICS}
    for gid, r in games.items():
        mechs = mechanics_of(r["name"])
        if not mechs:
            continue
        now = _avg_high(r["days"], this_start, y)
        prev = _avg_high(r["days"], last_start, last_end)
        is_new = r["first_seen"] != state.get("baseline_day") and _d(r["first_seen"]) >= week_ago
        peak = max([v for d, v in r["days"].items() if _d(d) >= this_start] or [0])
        for m in mechs:
            row = rows[m]
            row["now"] += now
            row["prev"] += prev
            if now > 0:
                row["games"] += 1
            if is_new:
                row["new"] += 1
                if peak >= C.HIT_PLAYERS:
                    row["hits"] += 1
            row["top"].append((now, r["name"], gid))
    out = []
    for m, row in rows.items():
        if row["now"] <= 0:
            continue
        chg = ((row["now"] / row["prev"] - 1) * 100) if (have_last_week and row["prev"] > 0) else None
        if chg is None:
            label = "⚪ need 2 weeks of data"
        elif chg >= 10 and row["new"] <= C.GAP_MAX_NEW_GAMES:
            label = "🟢 open gap"
        elif chg >= 10:
            label = "🟡 growing but crowding"
        elif chg <= -10 and row["new"] >= C.GAP_MAX_NEW_GAMES:
            label = "🔴 saturating"
        elif chg <= -10:
            label = "🔻 cooling"
        else:
            label = "▫️ steady"
        row["top"].sort(reverse=True)
        out.append({"mech": m, "now": row["now"], "chg": chg, "games": row["games"], "new": row["new"],
                    "hits": row["hits"], "label": label, "top": row["top"][:3]})
    if have_last_week:
        out.sort(key=lambda x: -(x["chg"] if x["chg"] is not None else -999))
    else:
        out.sort(key=lambda x: -x["now"])
    return out


# ----------------------------------------------------------------- updates ---

def track_updates(state, today):
    """Detect new updates (Roblox 'updated' date changed). Returns list of new events."""
    from sources import src_state
    ins = ins_state(state)
    rbx = src_state(state)["rbx"]
    games = state["games"]
    new_events = []
    for gid, r in rbx.items():
        upd = r.get("updated")
        if not upd:
            continue
        prev = ins["last_updated"].get(gid)
        ins["last_updated"][gid] = upd
        if prev is None or upd <= prev:
            continue
        g = games.get(gid)
        players = (g or {}).get("last") or r.get("playing", 0)
        if players < C.UPDATE_MIN_PLAYERS or not g:
            continue
        ud = _d(upd)
        before = [g["days"][_s(ud - timedelta(days=k))] for k in (1, 2, 3) if _s(ud - timedelta(days=k)) in g["days"]]
        ev = {"gid": gid, "name": g["name"][:50], "date": upd, "seen": today,
              "before": round(sum(before) / len(before)) if before else None}
        ins["updates"].append(ev)
        new_events.append(ev)
    # fill in outcomes once each day is complete
    for ev in ins["updates"]:
        g = games.get(ev["gid"])
        if not g or not ev.get("before"):
            continue
        for k in (1, 3, 7):
            key = f"d{k}"
            day = _s(_d(ev["date"]) + timedelta(days=k))
            if key not in ev and day < today and day in g["days"]:
                ev[key] = round((g["days"][day] / ev["before"] - 1) * 100)
    cutoff = _s(_d(today) - timedelta(days=C.INSIGHT_KEEP_DAYS))
    ins["updates"] = [e for e in ins["updates"] if e["date"] >= cutoff][-C.MAX_UPDATE_EVENTS:]
    # forget update dates for games no longer tracked
    for gid in [g for g in ins["last_updated"] if g not in rbx]:
        del ins["last_updated"][gid]
    return new_events


def update_lines(state, today, days=7, limit=8):
    fmt = HOOKS["fmt"]
    since = _s(_d(today) - timedelta(days=days))
    evs = [e for e in ins_state(state)["updates"] if e["date"] >= since]
    evs.sort(key=lambda e: e["date"], reverse=True)
    out = []
    for e in evs[:limit]:
        res = []
        for k in (1, 3, 7):
            if f"d{k}" in e:
                res.append(f"day {k}: {e[f'd{k}']:+d}%")
        before = f"from {fmt(e['before'])}" if e.get("before") else "no 'before' data"
        out.append(f"• {e['name'][:35]} — updated {e['date'][5:]} ({before})"
                   + (" → " + ", ".join(res) if res else " → measuring…"))
    return out


# --------------------------------------------------------------- lifecycle ---

def track_lifecycle(state, today):
    """Record young games crossing the breakout threshold, and follow them. Returns new breakouts."""
    is_young, age_days = HOOKS["is_young"], HOOKS["age_days"]
    life = ins_state(state)["life"]
    new = []
    for gid, r in state["games"].items():
        high = r["days"].get(today)
        if not high:
            continue
        rec = life.get(gid)
        if rec is None:
            if high >= C.BREAKOUT_PLAYERS and is_young(r, today):
                # games already big when the bot started: kept for reference, left out of the stats
                pre = r["first_seen"] == state.get("baseline_day") and min(r["days"]) == state.get("baseline_day") \
                    and r["days"][min(r["days"])] >= C.BREAKOUT_PLAYERS
                a = age_days(r, today)
                rec = life[gid] = {"name": r["name"][:50], "mech": mechanics_of(r["name"]),
                                   "age": a, "broke": today, "peak": high, "peak_day": today}
                if pre:
                    rec["pre"] = True
                else:
                    new.append(gid)
            else:
                continue
        rec["name"] = r["name"][:50]
        if high > rec["peak"]:
            rec["peak"], rec["peak_day"] = high, today
        rec["last"], rec["last_day"] = high, today
    # games that fell out of the top list: mark them faded
    for gid, rec in life.items():
        if gid not in state["games"] or state["games"][gid].get("last_seen") != today:
            rec.setdefault("gone", today)
        else:
            rec.pop("gone", None)
    cutoff = _s(_d(today) - timedelta(days=C.INSIGHT_KEEP_DAYS))
    for gid in [g for g, r in life.items() if r["broke"] < cutoff]:
        del life[gid]
    return new


def life_status(rec, today):
    days_since_peak = (_d(today) - _d(rec["peak_day"])).days
    cur = rec.get("last", rec["peak"]) if not rec.get("gone") else 0
    if days_since_peak <= 1 and not rec.get("gone"):
        return "📈 still climbing"
    if cur >= 0.7 * rec["peak"]:
        return "➡️ holding near peak"
    if cur >= 0.3 * rec["peak"]:
        return "📉 cooling"
    return "💀 faded"


def lifecycle_summary(state, today):
    """Per mechanic: breakouts, median age at breakout, median days to peak (finished ones)."""
    life = ins_state(state)["life"]
    by = {}
    for gid, r in life.items():
        if r.get("pre"):
            continue
        for m in (r["mech"] or ["Other"]):
            by.setdefault(m, []).append(r)
    out = []
    for m, rs in by.items():
        ages = [r["age"] for r in rs if r.get("age") is not None]
        done = [r for r in rs if (_d(today) - _d(r["peak_day"])).days >= 3]
        to_peak = [(_d(r["peak_day"]) - _d(r["broke"])).days for r in done]
        out.append({"mech": m, "n": len(rs), "age": median(ages) if ages else None,
                    "to_peak": median(to_peak) if to_peak else None, "done": len(done)})
    out.sort(key=lambda x: -x["n"])
    return out


# ------------------------------------------------------------ weekly report ---

def weekly_report(state, today):
    fmt, link = HOOKS["fmt"], HOOKS["link"]
    lines = [f"**📅 Weekly opportunity report** · week to {_d(today).strftime('%a %d %b')}",
             "_Demand = average daily players across all games of that type (this week vs last week)._", ""]
    table = mechanic_table(state, today)
    lines.append("🧭 **Mechanics: demand vs how crowded**")
    if table:
        for r in table:
            chg = f"{r['chg']:+.0f}%" if r["chg"] is not None else "—"
            tops = ", ".join(n[:22] for _, n, _ in r["top"])
            lines.append(f"• {r['label']} **{r['mech']}** — {fmt(r['now'])} avg players ({chg}) · "
                         f"{r['new']} new game{'s' if r['new'] != 1 else ''} this week, {r['hits']} hit {fmt(C.HIT_PLAYERS)}+ · top: {tops}")
    else:
        lines.append("• Not enough data yet")

    gaps = [r for r in table if r["label"].startswith("🟢")]
    lines += ["", "💡 **Best openings right now:** " +
              (", ".join(f"{r['mech']} ({r['chg']:+.0f}% demand, only {r['new']} new)" for r in gaps[:3])
               if gaps else "none clear-cut this week")]

    # Breakouts
    life = ins_state(state)["life"]
    week_ago = _s(_d(today) - timedelta(days=7))
    recent = sorted([(g, r) for g, r in life.items() if r["broke"] >= week_ago and not r.get("pre")],
                    key=lambda x: -x[1]["peak"])
    lines += ["", f"💥 **Breakouts this week** (young games crossing {fmt(C.BREAKOUT_PLAYERS)} players)"]
    if recent:
        for gid, r in recent[:8]:
            age = f"{r['age']}d old" if r.get("age") is not None else "age ?"
            lines.append(f"• {r['name'][:35]} — {age} when it broke out, peak {fmt(r['peak'])} "
                         f"· {life_status(r, today)} {link(gid, state)}")
    else:
        lines.append("• None this week")

    summ = [s for s in lifecycle_summary(state, today) if s["n"] >= 2]
    lines += ["", "⏳ **How long trends last** (all breakouts tracked so far)"]
    if summ:
        for s in summ[:8]:
            age = f"broke out at ~{s['age']:.0f} days old" if s["age"] is not None else ""
            tp = (f"peaked ~{s['to_peak']:.0f} days later" if s["to_peak"] is not None else "none peaked yet")
            lines.append(f"• **{s['mech']}** — {s['n']} breakouts, {age}, {tp}")
        lines.append("_Tip: if a type usually peaks ~10 days after breaking out, a copy needs to ship well inside that window._")
    else:
        lines.append("• Builds up over the coming weeks")

    # Updates
    evs = [e for e in ins_state(state)["updates"] if "d3" in e]
    lines += ["", "🛠️ **What updates did** (players 3 days after an update vs the days before)"]
    if evs:
        d3 = [e["d3"] for e in evs]
        ups = sum(1 for v in d3 if v >= 10)
        lines.append(f"• {len(evs)} update{'s' if len(evs) != 1 else ''} measured · median change {median(d3):+.0f}% · "
                     f"{ups} of {len(evs)} gave a 10%+ boost")
        best = [e for e in sorted(evs, key=lambda e: -e["d3"]) if e["d3"] > 0][:3]
        if best:
            lines.append("• Biggest boosts: " + ", ".join(f"{e['name'][:25]} ({e['d3']:+d}%)" for e in best))
    else:
        lines.append("• Measuring — results appear 3 days after the first updates are spotted")
    return "\n".join(lines), table

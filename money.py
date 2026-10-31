"""
Money: which games (and which kinds of games) earn the most.

Source: RoWatcher's revenue estimate for every game in its top 2,000 (refreshed every scan). It is an
estimate from RoWatcher's own model, not Roblox's real payouts, but it is consistent across games, so
comparisons are fair. Revenue below is what the bot recorded over the last 7 complete days:

  monthly revenue   = average daily estimate x 30.4
  $ per player      = monthly revenue / average concurrent players (what each "seat" of CCU earns a month)
  $ per 1K daily    = monthly revenue / (daily players from badges / 1,000), when badge data exists

Grouped by genre, sub-genre, mechanic, size band and age band, with medians (typical game) and the
top-quartile game (what a good one in that group makes).
"""
import csv
import io
from datetime import datetime, timedelta
from statistics import median

import benchmarks as BM
import config as C

SIZE_BANDS = [(400, 1000, "400–1K"), (1000, 5000, "1K–5K"), (5000, 20000, "5K–20K"),
              (20000, 100000, "20K–100K"), (100000, 10 ** 9, "100K+")]
AGE_BANDS = [(0, 30, "under 1 month"), (30, 90, "1–3 months"), (90, 365, "3–12 months"),
             (365, 1095, "1–3 years"), (1095, 10 ** 6, "3+ years")]


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def band(v, bands):
    for lo, hi, name in bands:
        if lo <= v < hi:
            return name
    return None


def q75(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * 0.75))] if xs else None


def table(db, state, today, mechanics_of):
    """One row per game with enough data."""
    end = _s(_d(today) - timedelta(days=1))
    start = _s(_d(today) - timedelta(days=C.MONEY_DAYS))
    rows = {}
    for r in db.execute("""SELECT uid, day, peak, sum_ccu, n, rev_usd FROM daily
                           WHERE day>=? AND day<=? AND rev_usd IS NOT NULL""", (start, end)):
        avg = (r["sum_ccu"] / r["n"]) if r["n"] and r["n"] >= 2 else (r["peak"] or 0) * 0.75
        x = rows.setdefault(r["uid"], {"rev": [], "ccu": []})
        x["rev"].append(r["rev_usd"])
        x["ccu"].append(avg)
    meta = {r["uid"]: r for r in db.execute("SELECT uid, name, genre, subgenre, created FROM games")}
    badges = state.get("badges") or {}
    out = []
    for uid, x in rows.items():
        if len(x["rev"]) < C.MONEY_MIN_DAYS:
            continue
        ccu = sum(x["ccu"]) / len(x["ccu"])
        if ccu < C.MONEY_MIN_CCU:
            continue
        daily = sum(x["rev"]) / len(x["rev"])
        m = meta.get(uid)
        name = (m["name"] if m else None) or (state["games"].get(uid) or {}).get("name") or uid
        age = None
        if m and m["created"]:
            try:
                age = (_d(today) - _d(m["created"][:10])).days
            except ValueError:
                age = None
        dau = (badges.get(uid) or {}).get("dau")
        monthly = daily * 30.4
        rc = BM.reality_check(monthly, dau) if dau else None
        out.append({"uid": uid, "name": name, "genre": (m["genre"] if m else None) or "Unknown",
                    "subgenre": (m["subgenre"] if m else None) or "", "mech": (mechanics_of(name) or ["Other"])[0],
                    "ccu": ccu, "monthly": monthly, "per_player": monthly / ccu if ccu else 0,
                    "per_1k_daily": (monthly / (dau / 1000)) if dau else None, "age": age,
                    "mon_pct": rc["pct"] if rc and not rc["suspect"] else None,
                    "suspect": (monthly / ccu if ccu else 0) > C.MONEY_SUSPECT_PER_PLAYER or bool(rc and rc["suspect"]),
                    "size": band(ccu, SIZE_BANDS), "age_band": band(age, AGE_BANDS) if age is not None else "unknown"})
    out.sort(key=lambda r: -r["monthly"])
    return out


def groups(rows, key):
    by = {}
    for r in rows:
        k = r.get(key)
        if k:
            by.setdefault(k, []).append(r)
    res = []
    for k, rs in by.items():
        if len(rs) < C.MONEY_MIN_GROUP:
            continue
        res.append({"group": k, "n": len(rs), "median": median(r["monthly"] for r in rs),
                    "top25": q75([r["monthly"] for r in rs]), "per_player": median(r["per_player"] for r in rs),
                    "total": sum(r["monthly"] for r in rs),
                    "top": sorted(rs, key=lambda r: -r["monthly"])[:3]})
    return res


def usd(v):
    if v is None:
        return "—"
    if v >= 1e6:
        return f"${v / 1e6:.1f}M"
    if v >= 1e3:
        return f"${v / 1e3:.0f}K" if v >= 1e4 else f"${v / 1e3:.1f}K"
    if v < 10:
        return f"${v:.2f}"
    return f"${v:.0f}"


def report_lines(rows, fmt, link=None, n_top=8, bench=True):
    if not rows:
        return ["Not enough revenue data yet — it builds up over the first week."]
    lk = (lambda r: f"[{r['name'][:30]}]({link(r['uid'])})") if link else (lambda r: r["name"][:30])
    lines = [f"**{len(rows):,} games** with 400+ players · median **{usd(median(r['monthly'] for r in rows))}/month** · "
             f"median **{usd(median(r['per_player'] for r in rows))}** per concurrent player per month"]
    lines.append("")
    lines.append("**By genre** (typical game · a top-quartile game · $ per player):")
    for g in sorted(groups(rows, "genre"), key=lambda g: -g["per_player"])[:8]:
        lines.append(f"• **{g['group']}** — {usd(g['median'])} · {usd(g['top25'])} · **{usd(g['per_player'])}**/player ({g['n']})")
    lines.append("")
    lines.append("**By mechanic** ($ per player, best first):")
    for g in sorted(groups(rows, "mech"), key=lambda g: -g["per_player"])[:8]:
        if g["group"] == "Other":
            continue
        lines.append(f"• **{g['group']}** — {usd(g['median'])} typical · **{usd(g['per_player'])}**/player ({g['n']})")
    lines.append("")
    lines.append("**By size** (concurrent players):")
    order = [b[2] for b in SIZE_BANDS]
    for g in sorted(groups(rows, "size"), key=lambda g: order.index(g["group"])):
        lines.append(f"• **{g['group']}** — {usd(g['median'])} typical · {usd(g['top25'])} top-quartile · {usd(g['per_player'])}/player ({g['n']})")
    lines.append("")
    eff = sorted([r for r in rows if r["ccu"] >= 1000 and not r.get("suspect")], key=lambda r: -r["per_player"])[:n_top]
    if eff:
        lines.append("**Best earners per player** (1K+ players):")
        for r in eff:
            lines.append(f"• {lk(r)} — **{usd(r['per_player'])}**/player · {usd(r['monthly'])}/month · {fmt(r['ccu'])} players · {r['genre']}")
    mon = sorted([r for r in rows if r.get("mon_pct") and r["ccu"] >= 1000], key=lambda r: -r["per_1k_daily"])[:n_top]
    if mon:
        lines.append("")
        lines.append("**Best monetisers per daily player** (vs Roblox's own benchmarks):")
        for r in mon:
            lines.append(f"• {lk(r)} — **{usd(r['per_1k_daily'])}** per 1K daily players/month · {BM.tier(r['mon_pct'])} · {r['genre']} · {r['mech']}")
    small = sorted([r for r in rows if r["ccu"] < 5000 and not r.get("suspect")], key=lambda r: -r["monthly"])[:n_top]
    if small:
        lines.append("")
        lines.append("**Top earners under 5K players** (realistic for a small studio):")
        for r in small:
            lines.append(f"• {lk(r)} — **{usd(r['monthly'])}/month** · {fmt(r['ccu'])} players · {r['genre']} · {r['mech']}")
    if bench:
        lines.append("")
        lines += BM.report_lines()
    return lines


def to_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["universe_id", "name", "genre", "subgenre", "mechanic", "avg_players_7d", "monthly_revenue_usd",
                "usd_per_player_month", "usd_per_1k_daily_players", "monetisation_percentile", "estimate_suspect", "age_days", "size_band", "age_band"])
    for r in rows:
        w.writerow([r["uid"], r["name"], r["genre"], r["subgenre"], r["mech"], round(r["ccu"]), round(r["monthly"]),
                    round(r["per_player"], 2), round(r["per_1k_daily"], 2) if r["per_1k_daily"] else "", r.get("mon_pct") or "", "yes" if r.get("suspect") else "",
                    r["age"] if r["age"] is not None else "", r["size"], r["age_band"]])
    return buf.getvalue()


def markdown(rows, fmt):
    """Full report as Markdown (for the reports branch)."""
    out = [f"# Roblox earnings report", "",
           "Estimated from RoWatcher's revenue model over the last 7 days; games with 400+ concurrent players.", ""]
    out += [l.replace("• ", "- ") for l in report_lines(rows, fmt, None, n_top=15)]
    out += ["", "## All groups", ""]
    for key, title in (("genre", "Genre"), ("subgenre", "Sub-genre"), ("mech", "Mechanic"), ("size", "Size"), ("age_band", "Age")):
        gs = sorted(groups(rows, key), key=lambda g: -g["per_player"])
        if not gs:
            continue
        out += [f"### {title}", "", "| Group | Games | Typical $/month | Top-quartile $/month | $ per player/month | Total $/month | Top games |",
                "|---|---|---|---|---|---|---|"]
        for g in gs:
            out.append(f"| {g['group']} | {g['n']} | {usd(g['median'])} | {usd(g['top25'])} | {usd(g['per_player'])} | {usd(g['total'])} | "
                       + ", ".join(r["name"][:24].replace("|", "/") for r in g["top"]) + " |")
        out.append("")
    out += ["## Top 50 earners", "", "| Game | Genre | Players | $/month | $ per player |", "|---|---|---|---|---|"]
    for r in rows[:50]:
        out.append(f"| {r['name'][:40].replace('|', '/')} | {r['genre']} | {fmt(r['ccu'])} | {usd(r['monthly'])} | {usd(r['per_player'])} |")
    return "\n".join(out)

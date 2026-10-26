"""
Real Roblox benchmarks — what "good" looks like inside Creator Hub — and a reality check on earnings.

Source: Creator Hub screenshots of a top game (Fisch, Feb 2025) shared by the owner. Creator Hub shows
each metric against Roblox's own benchmark: the 50th and 90th percentile of comparable experiences.

  metric                         50th      90th
  average session time           13.5 min  25.8 min
  day-1 retention                10.55%    14.78%
  day-7 retention                 2.21%     5.93%
  payer conversion (per day)      0.88%     2.37%
  revenue per paying user (R$)    181       506.8
  qualified play-through rate     1.15%     1.67%

Treating each metric as log-normal through those two points reproduces Creator Hub's own percentile
for Fisch on every metric (session 87th vs 84th shown, D1 88th vs 88th, D7 92nd vs 94th, conversion
83rd vs 78th, ARPPU 86th vs 86th), so the bot can turn any estimate into "top X%" the same way.

Revenue identity (checked on Fisch: 4.33M daily players x 1.82% x R$433.7 = R$34.2M vs R$33.7M shown):

  Robux per day = daily players x payer conversion x revenue per paying user

So a typical game earns ~R$1.6 per daily player per day and a top-10% monetiser ~R$12. Fisch earned
~R$6.7 (R$29M a day over 72 hours) = ~$780 a month per 1K daily players at the DevEx rate; RoWatcher
estimates Fisch today at $725 per 1K daily players — within ~7%, so RoWatcher's model is trustworthy
for this kind of game. The bot uses the same identity to grade every game's earnings per player.

Other things the screenshots show (used in reports, not formulas):
  * revenue mix of a top game: developer products ~78%, game passes ~18%, private servers ~5%;
    premium engagement payouts add another ~11% on top
  * weekend days earn ~2-3x a weekday (players only ~1.4x) and update days with a new limited
    bundle spike hardest, so earnings must be averaged over a full week (the bot does)
  * best-selling passes: 2x XP (R$199), "sell / appraise / spawn anywhere" convenience (R$299-499),
    luck (R$399), emote pack (R$99); developer-product bundles at R$799-1,499
"""
import math

DEVEX_USD = 0.0038        # USD per Robux at the Developer Exchange rate

BENCH = {
    "session_min": (13.5, 25.8),
    "d1": (0.1055, 0.1478),
    "d7": (0.0221, 0.0593),
    "conversion": (0.0088, 0.0237),
    "arppu": (181.0, 506.8),
    "qptr": (0.0115, 0.0167),
}
Z90 = 1.2815516

LABEL = {"session_min": "session length", "d1": "day-1 retention", "d7": "day-7 retention",
         "conversion": "payer conversion", "arppu": "revenue per paying player", "qptr": "play-through rate",
         "monetisation": "earnings per player"}


def _params(metric):
    p50, p90 = BENCH[metric]
    return math.log(p50), (math.log(p90) - math.log(p50)) / Z90


def _phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def percentile(metric, value):
    """Where a value sits among Roblox games (0-100), Creator Hub style."""
    if value is None or value <= 0:
        return None
    if metric == "monetisation":          # Robux per daily player per day = conversion x ARPPU
        m1, s1 = _params("conversion")
        m2, s2 = _params("arppu")
        mu, sd = m1 + m2, math.sqrt(s1 * s1 + s2 * s2)
    else:
        mu, sd = _params(metric)
    return max(1, min(99, round(_phi((math.log(value) - mu) / sd) * 100)))


def robux_per_dau(monthly_usd, dau):
    """Daily Robux per daily player implied by a monthly USD estimate."""
    if not monthly_usd or not dau:
        return None
    return monthly_usd / 30.4 / DEVEX_USD / dau


def monthly_band(dau):
    """What a game with this many daily players earns a month: typical vs top-10% monetiser (USD)."""
    if not dau:
        return None
    k = dau * 30.4 * DEVEX_USD
    typ = BENCH["conversion"][0] * BENCH["arppu"][0]
    top = BENCH["conversion"][1] * BENCH["arppu"][1]
    return {"typical": k * typ, "top10": k * top}


def tier(p):
    if p is None:
        return ""
    if p >= 90:
        return f"top {100 - p}%"
    if p >= 50:
        return f"{p}th percentile"
    return f"bottom {p}%"


def reality_check(monthly_usd, dau):
    """{'pct', 'rpd', 'suspect'} — how the revenue estimate compares with real Roblox monetisation."""
    rpd = robux_per_dau(monthly_usd, dau)
    if rpd is None:
        return None
    p = percentile("monetisation", rpd)
    return {"pct": p, "rpd": rpd, "suspect": rpd > 60 or rpd < 0.05}


def report_lines():
    """Static 'what real games look like' notes for the money report."""
    b = monthly_band(1000)
    return [
        "**What real Roblox numbers look like** (Creator Hub benchmarks, checked on a top game's real dashboard):",
        f"• Per 1K daily players: typical game **${b['typical']:.0f}/month**, top-10% monetiser **${b['top10']:,.0f}/month** "
        "(daily players × payer conversion 0.9–2.4% × R$181–507 per payer)",
        "• Good benchmarks: session 13.5 min typical / 25.8 top-10% · day-1 retention 10.6% / 14.8% · day-7 2.2% / 5.9%",
        "• A top game's money: ~78% developer products (bundles, currency packs), ~18% passes, ~5% private servers, "
        "plus ~11% extra from premium playtime payouts",
        "• Weekends earn 2–3× a weekday; update days with a new limited bundle spike hardest",
    ]

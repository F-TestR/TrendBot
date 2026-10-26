"""
Game passes: what games sell and at what price (public Roblox data, no key).

A few games per run (top earners first, each about once a week): number of passes for sale, their
prices in Robux and names. Combined with the earnings table this answers "what do the best earners
sell, how many passes, at what price points" by genre and mechanic.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from statistics import median

import config as C

UA = {"User-Agent": "Mozilla/5.0 (compatible; roblox-trend-bot/1.8)", "Accept": "application/json"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS passes (uid TEXT PRIMARY KEY, day TEXT, n INTEGER, prices TEXT, names TEXT);
"""
KINDS = [("VIP", r"\bvip\b"), ("2x / multiplier", r"\b(2x|x2|3x|double|triple|multiplier|boost)\b"),
         ("auto / skip", r"\b(auto|skip|instant|faster|speed)\b"), ("extra slots / storage", r"\b(slot|storage|backpack|inventory|capacity)\b"),
         ("luck", r"\b(luck|lucky)\b"), ("cosmetic / trail", r"\b(trail|skin|cosmetic|title|tag|chat|color|colour|aura)\b"),
         ("admin / commands", r"\b(admin|command|cmds?)\b"), ("teleport / unlock area", r"\b(teleport|tp|unlock|area|world)\b"),
         ("do-it-anywhere convenience", r"\b(anywhere|remote|portable|everywhere)\b"),
         ("emotes / radio / social", r"\b(emotes?|radio|boombox|music|dance)\b"),
         ("supporter / donation", r"\b(supporter|donat\w*|tip)\b")]


def log(m):
    print(m, file=sys.stderr)


def ensure(db):
    db.executescript(SCHEMA)


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def _price(it):
    for k in ("price", "priceInRobux"):
        if isinstance(it.get(k), (int, float)) and it[k]:
            return int(it[k])
    pi = it.get("priceInformation") or {}
    v = pi.get("defaultPriceInRobux") or pi.get("priceInRobux")
    return int(v) if isinstance(v, (int, float)) and v else None


def fetch(uid):
    """[(name, price)] for passes currently for sale."""
    urls = [f"https://apis.roblox.com/game-passes/v1/universes/{uid}/game-passes?" + urllib.parse.urlencode({"passView": "Full", "pageSize": 100}),
            f"https://games.roblox.com/v1/games/{uid}/game-passes?" + urllib.parse.urlencode({"limit": 100, "sortOrder": "Asc"})]
    last = None
    for u in urls:
        try:
            d = get_json(u)
        except Exception as e:
            last = e
            continue
        items = d.get("gamePasses") or d.get("data") or []
        out = []
        for it in items:
            if it.get("isForSale") is False:
                continue
            p = _price(it)
            if p:
                out.append(((it.get("displayName") or it.get("name") or "")[:60], p))
        return out
    raise last or RuntimeError("no game-pass endpoint answered")


def collect(db, state, money_rows, today):
    """Refresh a few games' passes (top earners first)."""
    ensure(db)
    done = {r["uid"]: r["day"] for r in db.execute("SELECT uid, day FROM passes")}
    cut = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=C.PASSES_REFRESH_DAYS)).strftime("%Y-%m-%d")
    todo = [r["uid"] for r in money_rows if done.get(r["uid"], "") < cut][:C.PASSES_GAMES_PER_RUN]
    n = 0
    for uid in todo:
        try:
            ps = fetch(uid)
        except Exception as e:
            log(f"game passes failed for {uid}: {e}")
            db.execute("INSERT OR REPLACE INTO passes VALUES(?,?,?,?,?)", (uid, today, None, "[]", "[]"))
            continue
        db.execute("INSERT OR REPLACE INTO passes VALUES(?,?,?,?,?)",
                   (uid, today, len(ps), json.dumps([p for _, p in ps]), json.dumps([nm for nm, _ in ps])))
        n += 1
        time.sleep(0.3)
    return n


def load(db):
    ensure(db)
    return {r["uid"]: {"n": r["n"], "prices": json.loads(r["prices"] or "[]"), "names": json.loads(r["names"] or "[]")}
            for r in db.execute("SELECT * FROM passes WHERE n IS NOT NULL")}


def summary(rows, ps, key=None):
    """Pass stats for a set of money rows (optionally grouped by key)."""
    def stats(rs):
        have = [ps[r["uid"]] for r in rs if r["uid"] in ps]
        if len(have) < 4:
            return None
        prices = [p for x in have for p in x["prices"]]
        kinds = {}
        for x in have:
            names = " ".join(x["names"]).lower()
            for k, rx in KINDS:
                if re.search(rx, names):
                    kinds[k] = kinds.get(k, 0) + 1
        return {"games": len(have), "median_n": median(x["n"] for x in have),
                "median_price": median(prices) if prices else None,
                "points": sorted({p: prices.count(p) for p in prices}.items(), key=lambda kv: -kv[1])[:5],
                "kinds": sorted(((k, v / len(have)) for k, v in kinds.items()), key=lambda kv: -kv[1])[:5]}
    if not key:
        return stats(rows)
    by = {}
    for r in rows:
        by.setdefault(r.get(key), []).append(r)
    return {k: s for k, s in ((k, stats(v)) for k, v in by.items()) if s}


def lines(rows, ps):
    """Short text: what top earners sell vs everyone else."""
    if not rows or not ps:
        return []
    top = sorted(rows, key=lambda r: -r["per_player"])[:max(20, len(rows) // 10)]
    rest = [r for r in rows if r not in top]
    a, b = summary(top, ps), summary(rest, ps)
    if not a:
        return []
    out = [f"🎟️ Best earners per player sell **{a['median_n']:.0f}** passes (others: {b['median_n']:.0f})" if b else
           f"🎟️ Best earners per player sell **{a['median_n']:.0f}** passes",
           "Most common prices: " + ", ".join(f"R${p}" for p, _ in a["points"][:5])]
    if a["kinds"]:
        out.append("What they sell: " + ", ".join(f"{k} ({v * 100:.0f}%)" for k, v in a["kinds"][:4]))
    out.append("Passes are only ~1/5 of a top game's money — developer products (bundles R$799–1,499, currency packs) "
               "make ~3/4 but aren't public")
    return out


def markdown_section(rows, ps):
    if not ps:
        return ""
    out = ["", "## What games sell (game passes)", ""]
    out += ["- " + l for l in lines(rows, ps)]
    g = summary(rows, ps, "genre")
    if g:
        out += ["", "| Genre | Games checked | Typical passes | Typical price | Common prices | Most common kinds |", "|---|---|---|---|---|---|"]
        for k, s in sorted(g.items(), key=lambda kv: -kv[1]["games"]):
            out.append(f"| {k} | {s['games']} | {s['median_n']:.0f} | R${s['median_price']:.0f} | "
                       + ", ".join(f"R${p}" for p, _ in s["points"][:4]) + " | "
                       + ", ".join(f"{kk} {v * 100:.0f}%" for kk, v in s["kinds"][:3]) + " |")
    return "\n".join(out)

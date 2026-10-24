"""
The forward calendar: things we KNOW are coming, so you can build before the wave.

Sources (all free):
  * Steam      - games in Steam's "Coming Soon" list, with their release dates
  * Films / TV - upcoming films and this week's trending films and shows (TMDB, free key;
                 optional - set TMDB_API_KEY). This product uses the TMDB API but is not
                 endorsed or certified by TMDB.
  * Dates      - holidays and events you list in config.FUTURE_EVENTS (add Roblox events,
                 game launches or anything else you hear about)

Every day the bot:
  1. refreshes the list of upcoming things (next FUTURE_HORIZON_DAYS days, plus the last 14 days),
  2. checks whether each one's distinctive words already appear in brand-new Roblox games,
  3. alerts 🔮 when an upcoming thing STARTS appearing in Roblox ("first copies are arriving"),
  4. writes the words into the outside-signals table (source "future") so the theme model and
     the indicator league table can measure whether upcoming releases really lead Roblox trends.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import config as C
import upstream as U

SCHEMA = """
CREATE TABLE IF NOT EXISTS future (source TEXT, key TEXT, name TEXT, date TEXT, score REAL, detail TEXT,
  words TEXT, first_seen TEXT, last_seen TEXT, PRIMARY KEY (source, key));
"""


def log(m):
    print(m, file=sys.stderr)


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def ensure(db):
    db.executescript(SCHEMA)


def distinctive_words(name):
    ws = [w for w in U.words_of(name, bigrams=True) if len(w) >= 4 and w not in C.THEME_GENERIC]
    return sorted(set(ws))[:8]


def _put(db, source, key, name, date, score, detail, today):
    words = distinctive_words(name)
    if not words:
        return
    db.execute("""INSERT INTO future(source, key, name, date, score, detail, words, first_seen, last_seen)
                  VALUES(?,?,?,?,?,?,?,?,?)
                  ON CONFLICT(source, key) DO UPDATE SET name=excluded.name, date=COALESCE(excluded.date, date),
                    score=excluded.score, detail=excluded.detail, words=excluded.words, last_seen=excluded.last_seen""",
               (source, str(key), name[:120], date, score, detail[:160], json.dumps(words), today, today))


# ------------------------------------------------------------------ steam ---

def _steam_date(txt):
    """Steam gives dates like '14 Nov, 2026', 'Nov 14, 2026', 'Q4 2026', 'Coming soon'. Returns YYYY-MM-DD or None."""
    for fmt in ("%d %b, %Y", "%b %d, %Y", "%d %B, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(txt.strip(), fmt).strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            pass
    return None


def collect_steam(db, fst, today):
    d = U.get_json("https://store.steampowered.com/api/featuredcategories?cc=us&l=english")
    items = ((d.get("coming_soon") or {}).get("items") or []) + ((d.get("new_releases") or {}).get("items") or [])[:10]
    cache = fst.setdefault("steam_dates", {})
    n = lookups = 0
    seen = set()
    for i, it in enumerate(items):
        appid, name = str(it.get("id")), it.get("name") or ""
        if not name or appid in seen:
            continue
        seen.add(appid)
        if appid not in cache and lookups < 20:
            lookups += 1
            try:
                info = U.get_json(f"https://store.steampowered.com/api/appdetails?appids={appid}&filters=release_date")
                rd = ((info.get(appid) or {}).get("data") or {}).get("release_date") or {}
                cache[appid] = _steam_date(rd.get("date", "")) or ""
            except Exception as e:
                log(f"steam date lookup failed for {appid}: {e}")
                continue
        date = cache.get(appid) or None
        _put(db, "steam", appid, name, date, 1.0 + (len(items) - i) / max(len(items), 1),
             f"Steam: {name}" + (f" (out {date})" if date else " (coming soon)"), today)
        n += 1
    return n


# ------------------------------------------------------------------- tmdb ---

def collect_tmdb(db, key, today):
    n = 0
    base = "https://api.themoviedb.org/3/"
    def get(path, **params):
        return U.get_json(base + path + "?" + urllib.parse.urlencode(dict(params, api_key=key)))
    for page in (1, 2):
        d = get("movie/upcoming", region=C.TMDB_REGION, page=page)
        for m in d.get("results") or []:
            pop = m.get("popularity") or 0
            if pop < C.TMDB_MIN_POPULARITY:
                continue
            _put(db, "film", f"m{m.get('id')}", m.get("title") or "", m.get("release_date") or None,
                 min(5.0, pop / 50), f"Film: {m.get('title')} ({m.get('release_date') or 'date tbc'})", today)
            n += 1
    d = get("trending/all/week")
    for m in d.get("results") or []:
        if m.get("media_type") not in ("movie", "tv"):
            continue
        name = m.get("title") or m.get("name") or ""
        date = m.get("release_date") or m.get("first_air_date") or None
        kind = "Film" if m.get("media_type") == "movie" else "Show"
        _put(db, "trending", f"{m.get('media_type')}{m.get('id')}", name, date, min(5.0, (m.get("popularity") or 0) / 50),
             f"Trending {kind.lower()} this week: {name}", today)
        n += 1
    return n


# ------------------------------------------------------------------ fixed ---

def collect_fixed(db, today):
    n = 0
    for date, name, words in C.FUTURE_EVENTS:
        db.execute("""INSERT INTO future(source, key, name, date, score, detail, words, first_seen, last_seen)
                      VALUES('event', ?, ?, ?, 2.0, ?, ?, ?, ?)
                      ON CONFLICT(source, key) DO UPDATE SET date=excluded.date, words=excluded.words, last_seen=excluded.last_seen""",
                   (f"{date}:{name}", name, date, f"Event: {name}", json.dumps([w.lower() for w in words]), today, today))
        n += 1
    return n


# ----------------------------------------------------------------- driver ---

def collect_all(db, state, t, env):
    ensure(db)
    U.ensure(db)
    fst = state.setdefault("future", {})
    today = _s(t)
    if fst.get("last") == today:
        return []
    ran = []
    for name, fn in (("steam", lambda: collect_steam(db, fst, today)),
                     ("films", (lambda: collect_tmdb(db, env["TMDB_API_KEY"], today)) if env.get("TMDB_API_KEY") else None),
                     ("events", lambda: collect_fixed(db, today))):
        if fn is None:
            continue
        try:
            ran.append(f"{name}:{fn()}")
        except Exception as e:
            log(f"future {name} failed: {e}")
    # feed upcoming things (next horizon days, or released in the last 14) into the outside-signals table
    lo, hi = _s(t - timedelta(days=14)), _s(t + timedelta(days=C.FUTURE_HORIZON_DAYS))
    for r in db.execute("SELECT * FROM future WHERE last_seen >= ?", (_s(t - timedelta(days=7)),)):
        if r["date"] and not (lo <= r["date"] <= hi):
            continue
        for w in json.loads(r["words"] or "[]"):
            U.put(db, "future", today, w, float(r["score"] or 1), r["detail"] or r["name"])
    db.execute("DELETE FROM future WHERE last_seen < ?", (_s(t - timedelta(days=60)),))
    fst["last"] = today
    return ran


def upcoming(db, today):
    """Upcoming things with their Roblox status, soonest-most-important first."""
    ensure(db)
    t = _d(today)
    lo, hi = _s(t - timedelta(days=14)), _s(t + timedelta(days=C.FUTURE_HORIZON_DAYS))
    yday = _s(t - timedelta(days=1))
    out = []
    for r in db.execute("SELECT * FROM future WHERE last_seen >= ?", (_s(t - timedelta(days=7)),)):
        if r["date"] and not (lo <= r["date"] <= hi):
            continue
        words = json.loads(r["words"] or "[]")
        best = None
        for w in words:
            key = ("b:" if " " in w else "w:") + w
            row = db.execute("SELECT games, new7, ccu FROM theme_daily WHERE theme=? AND day=?", (key, yday)).fetchone()
            if row and (best is None or row["new7"] > best["new7"] or (row["new7"] == best["new7"] and row["games"] > best["games"])):
                best = {"word": w, "games": row["games"], "new7": row["new7"], "ccu": row["ccu"]}
        days = (_d(r["date"]) - t).days if r["date"] else None
        out.append({"source": r["source"], "name": r["name"], "date": r["date"], "days": days, "score": r["score"] or 1,
                    "detail": r["detail"], "roblox": best})
    def rank(x):
        soon = 1.0 if x["days"] is None else max(0.2, 1 - abs(x["days"]) / (C.FUTURE_HORIZON_DAYS + 14))
        return -(x["score"] * soon)
    out.sort(key=rank)
    return out


def alerts_for(db, state, today):
    """Upcoming things whose words just started appearing in brand-new Roblox games."""
    out = []
    for x in upcoming(db, today):
        rb = x["roblox"]
        if rb and rb["new7"] >= C.FUTURE_ALERT_NEW_GAMES:
            out.append(x)
    return out


def digest_lines(db, today, fmt):
    ups = upcoming(db, today)
    if not ups:
        return []
    lines = [f"🔮 **Coming up** (next {C.FUTURE_HORIZON_DAYS} days — build before the wave)"]
    for x in ups[:C.FUTURE_DIGEST_ITEMS]:
        when = ("out now" if x["days"] is not None and x["days"] <= 0 else
                f"in {x['days']} day{'s' if x['days'] != 1 else ''}" if x["days"] is not None else "date tbc")
        rb = x["roblox"]
        if rb and rb["new7"]:
            status = f"🌉 already {rb['new7']} new Roblox game{'s' if rb['new7'] != 1 else ''} using \"{rb['word']}\""
        elif rb and rb["games"]:
            status = f"{rb['games']} older Roblox games use \"{rb['word']}\""
        else:
            status = "✨ not on Roblox yet — first-mover chance"
        lines.append(f"• {x['detail']} · {when} · {status}")
    return lines


def check(env):
    out = []
    try:
        d = U.get_json("https://store.steampowered.com/api/featuredcategories?cc=us&l=english")
        items = (d.get("coming_soon") or {}).get("items") or []
        out.append(f"✅ Steam coming soon — {len(items)} games, e.g. {items[0]['name'] if items else '—'}")
    except Exception as e:
        out.append(f"❌ Steam coming soon — {e}")
    key = env.get("TMDB_API_KEY")
    if not key:
        out.append("⚪ Films & shows (TMDB) — no TMDB_API_KEY secret yet (optional, see SETUP.md)")
    else:
        try:
            d = U.get_json("https://api.themoviedb.org/3/movie/upcoming?" + urllib.parse.urlencode(
                {"api_key": key, "region": C.TMDB_REGION}))
            r = (d.get("results") or [{}])[0]
            out.append(f"✅ Films & shows (TMDB) — e.g. {r.get('title', '?')} ({r.get('release_date', '?')})")
        except Exception as e:
            out.append(f"❌ Films & shows (TMDB) — {e}")
    return out

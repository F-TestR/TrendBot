"""
Outside-Roblox signals: things that often become Roblox trends a few weeks later.

  * Steam      - games climbing Steam's most-played chart (Roblox versions often follow)
  * YouTube    - words rising in YouTube's general trending videos (memes, shows, characters)
  * Wikipedia  - articles newly spiking into Wikipedia's daily top 1,000
  * Twitch     - games newly entering Twitch's top 100 categories
  * Calendar   - seasonal themes you list in config.SEASONS

Each collector boils its source down to WORDS with a score for that day, stored in
the database table `upstream(source, day, word, score, detail)`. themes.py then checks
whether those words start appearing in new Roblox games - and the indicator report
measures which sources actually had predictive value.

All free. Failures are quiet: a broken source never stops the bot.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import config as C

UA = {"User-Agent": "roblox-trend-bot/1.3 (personal project; https://github.com/"
                    + os.environ.get("GITHUB_REPOSITORY", "unknown") + ")", "Accept": "application/json"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS upstream (source TEXT, day TEXT, word TEXT, score REAL, detail TEXT,
  PRIMARY KEY (source, day, word));
CREATE INDEX IF NOT EXISTS upstream_word ON upstream(word);
"""


def log(m):
    print(m, file=sys.stderr)


def get_json(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers=dict(UA, **(headers or {})))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def words_of(text, bigrams=True):
    t = re.sub(r"\[.*?\]|\(.*?\)", " ", (text or "").lower())
    t = re.sub(r"[^a-z0-9]+", " ", t)
    ws = [w for w in t.split() if len(w) >= 3 and not w.isdigit()]
    stop = C.THEME_STOPWORDS
    out = {w for w in ws if w not in stop}
    if bigrams:
        for a, b in zip(ws, ws[1:]):
            if a not in stop and b not in stop:
                out.add(a + " " + b)
    return out


def ensure(db):
    db.executescript(SCHEMA)


def put(db, source, day, word, score, detail=""):
    db.execute("""INSERT INTO upstream(source, day, word, score, detail) VALUES(?,?,?,?,?)
                  ON CONFLICT(source, day, word) DO UPDATE SET score=MAX(score, excluded.score),
                    detail=COALESCE(excluded.detail, detail)""", (source, day, word, score, detail[:120]))


# ------------------------------------------------------------------ steam ---

def collect_steam(db, ust, today):
    d = get_json("https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/")
    ranks = (d.get("response") or {}).get("ranks") or []
    names = ust.setdefault("steam_names", {})
    lookups = 0
    rising = []
    for r in ranks:
        appid = str(r.get("appid"))
        rank, last = r.get("rank") or 999, r.get("last_week_rank")
        new_entry = last in (None, -1, 0)
        climbed = (not new_entry) and (last - rank >= C.STEAM_RANK_CLIMB)
        if not (new_entry or climbed):
            continue
        if appid not in names and lookups < 15:
            lookups += 1
            try:
                info = get_json(f"https://store.steampowered.com/api/appdetails?appids={appid}&filters=basic")
                names[appid] = ((info.get(appid) or {}).get("data") or {}).get("name") or ""
            except Exception as e:
                log(f"steam name lookup failed for {appid}: {e}")
                continue
        name = names.get(appid) or ""
        if not name:
            continue
        rising.append((rank, name, "new to top 100" if new_entry else f"up {last - rank} places"))
    for rank, name, why in rising:
        score = 1.0 + (100 - min(rank, 100)) / 100
        full = " ".join(sorted(words_of(name, bigrams=False), key=name.lower().find))
        detail = f"Steam #{rank} {name} ({why})"
        for w in words_of(name):
            put(db, "steam", today, w, score, detail)
        if full:
            put(db, "steam", today, full, score + 0.5, detail)
    ust["steam_rising"] = [{"rank": r, "name": n, "why": w} for r, n, w in rising[:15]]
    return len(rising)


# ---------------------------------------------------------------- youtube ---

def collect_yt_trending(db, ust, today, key, units_cb):
    counts = {}
    titles = []
    for region in C.YT_TRENDING_REGIONS:
        for cat in ("", "20"):  # all, gaming
            params = {"part": "snippet", "chart": "mostPopular", "regionCode": region, "maxResults": 50, "key": key}
            if cat:
                params["videoCategoryId"] = cat
            try:
                units_cb(1)
                d = get_json("https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(params))
            except Exception as e:
                log(f"youtube trending {region}/{cat or 'all'} failed: {e}")
                continue
            for it in d.get("items", []):
                import html
                t = html.unescape((it.get("snippet") or {}).get("title", ""))
                titles.append(t)
                for w in words_of(t):
                    counts[w] = counts.get(w, 0) + 1
    hist = ust.setdefault("ytt_hist", {})
    hist[today] = {w: max(c, (hist.get(today) or {}).get(w, 0)) for w, c in counts.items()}
    keep = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=8)).strftime("%Y-%m-%d")
    for d in [d for d in hist if d < keep]:
        del hist[d]
    prev_days = [d for d in hist if d < today]
    rising = []
    for w, c in counts.items():
        prev = max([hist[d].get(w, 0) for d in prev_days] or [0])
        if c >= 2 and c >= 2 * (prev + 1):
            put(db, "yt_trending", today, w, float(c), "YouTube trending")
            rising.append((c, w))
    rising.sort(reverse=True)
    ust["ytt_rising"] = [w for _, w in rising[:15]]
    return len(rising)


# -------------------------------------------------------------- wikipedia ---

def collect_wikipedia(db, ust, today):
    y = datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/"
           f"{y:%Y}/{y:%m}/{y:%d}")
    d = get_json(url)
    arts = ((d.get("items") or [{}])[0].get("articles")) or []
    titles = {}
    for a in arts:
        t = a.get("article", "")
        if ":" in t or t in ("Main_Page",):
            continue
        titles[t] = a.get("views", 0)
    hist = ust.setdefault("wiki_hist", {})
    seen_before = set()
    for day, ts in hist.items():
        seen_before |= set(ts)
    hist[today] = list(titles)[:1000]
    keep = (y - timedelta(days=8)).strftime("%Y-%m-%d")
    for k in [k for k in hist if k < keep]:
        del hist[k]
    if len(hist) < 3:
        return 0  # need a few days of history to know what's "new"
    spikes = [(v, t) for t, v in titles.items() if t not in seen_before]
    spikes.sort(reverse=True)
    for v, t in spikes[:200]:
        name = t.replace("_", " ")
        for w in words_of(name):
            put(db, "wikipedia", today, w, min(3.0, v / 100000), f"Wikipedia: {name}")
    ust["wiki_spikes"] = [t.replace("_", " ") for _, t in spikes[:15]]
    return len(spikes)


# ----------------------------------------------------------------- twitch ---

def collect_twitch_top(db, ust, today, cid, secret):
    from sources import twitch_get, twitch_token
    tok = twitch_token(cid, secret)
    d = twitch_get("games/top", cid, tok, {"first": 100})
    now = [g.get("name", "") for g in d.get("data", [])]
    hist = ust.setdefault("tw_top_hist", {})
    old = set()
    for day, names in hist.items():
        if day < today:
            old |= set(names)
    hist[today] = now
    keep = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=8)).strftime("%Y-%m-%d")
    for k in [k for k in hist if k < keep]:
        del hist[k]
    if len(hist) < 2:
        return 0
    new = [(i + 1, n) for i, n in enumerate(now) if n not in old and n.lower() != "roblox"]
    for rank, n in new:
        for w in words_of(n):
            put(db, "twitch_top", today, w, 1.0 + (100 - rank) / 100, f"Twitch top #{rank}: {n}")
    ust["tw_top_new"] = [n for _, n in new[:15]]
    return len(new)


# --------------------------------------------------------------- calendar ---

def collect_calendar(db, today):
    d = datetime.strptime(today, "%Y-%m-%d")
    nxt = (d.replace(day=1) + timedelta(days=32)).month
    n = 0
    for month, ws in C.SEASONS.items():
        if month in (d.month, nxt):
            for w in ws:
                put(db, "season", today, w.lower(), 1.0, f"season (month {month})")
                n += 1
    return n


# ----------------------------------------------------------------- driver ---

def collect_all(db, state, t, env, units_cb):
    """Once a day (Steam, Wikipedia, calendar) / with YouTube & Twitch timers. Never raises."""
    ensure(db)
    ust = state.setdefault("upstream", {})
    today = t.strftime("%Y-%m-%d")
    ran = []
    jobs = [
        ("steam", lambda: collect_steam(db, ust, today), "daily"),
        ("wikipedia", lambda: collect_wikipedia(db, ust, today), "daily"),
        ("calendar", lambda: collect_calendar(db, today), "daily"),
    ]
    if env.get("YOUTUBE_API_KEY"):
        jobs.append(("yt_trending", lambda: collect_yt_trending(db, ust, today, env["YOUTUBE_API_KEY"], units_cb), "6h"))
    if env.get("TWITCH_CLIENT_ID") and env.get("TWITCH_CLIENT_SECRET"):
        jobs.append(("twitch_top", lambda: collect_twitch_top(db, ust, today, env["TWITCH_CLIENT_ID"],
                                                              env["TWITCH_CLIENT_SECRET"]), "6h"))
    last = ust.setdefault("last", {})
    for name, fn, every in jobs:
        prev = last.get(name)
        if every == "daily" and prev and prev[:10] == today:
            continue
        if every == "6h" and prev and (t - datetime.fromisoformat(prev)) < timedelta(hours=6):
            continue
        try:
            n = fn()
            ran.append(f"{name}:{n}")
        except Exception as e:
            log(f"upstream {name} failed: {e}")
        last[name] = t.isoformat()
    cut = (t - timedelta(days=C.UPSTREAM_KEEP_DAYS)).strftime("%Y-%m-%d")
    db.execute("DELETE FROM upstream WHERE day < ?", (cut,))
    return ran


def check(env):
    out = []
    try:
        d = get_json("https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/")
        ranks = (d.get("response") or {}).get("ranks") or []
        top = ranks[0] if ranks else {}
        info = get_json(f"https://store.steampowered.com/api/appdetails?appids={top.get('appid')}&filters=basic")
        name = ((info.get(str(top.get("appid"))) or {}).get("data") or {}).get("name", "?")
        out.append(f"✅ Steam charts — {len(ranks)} games, #1 is {name}")
    except Exception as e:
        out.append(f"❌ Steam charts — {e}")
    try:
        y = datetime.utcnow() - timedelta(days=2)
        d = get_json("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/"
                     f"{y:%Y}/{y:%m}/{y:%d}")
        arts = d["items"][0]["articles"]
        out.append(f"✅ Wikipedia top pages — {len(arts)} articles")
    except Exception as e:
        out.append(f"❌ Wikipedia top pages — {e}")
    key = env.get("YOUTUBE_API_KEY")
    if key:
        try:
            d = get_json("https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(
                {"part": "snippet", "chart": "mostPopular", "regionCode": "US", "maxResults": 1, "key": key}))
            out.append(f"✅ YouTube trending — e.g. \"{d['items'][0]['snippet']['title'][:50]}\"")
        except Exception as e:
            out.append(f"❌ YouTube trending — {e}")
    if env.get("TWITCH_CLIENT_ID") and env.get("TWITCH_CLIENT_SECRET"):
        try:
            from sources import twitch_get, twitch_token
            tok = twitch_token(env["TWITCH_CLIENT_ID"], env["TWITCH_CLIENT_SECRET"])
            d = twitch_get("games/top", env["TWITCH_CLIENT_ID"], tok, {"first": 3})
            out.append(f"✅ Twitch top games — #1 {d['data'][0]['name']}")
        except Exception as e:
            out.append(f"❌ Twitch top games — {e}")
    return out

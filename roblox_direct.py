"""
Roblox direct: free data straight from Roblox, so the bot isn't limited by RoWatcher's 2,000-game cap.

Three parts:
  1. DISCOVER (hourly)  Roblox's own home-page sorts (Top Trending, Up-and-Coming, Fun with Friends,
                        Top Revisited, Top Rated, every "Trending in <genre>"...), on computer and phone.
                        These are the games Roblox's algorithm is pushing right now - about 1,500 games.
  2. SEARCH  (daily)    Roblox search for the words that matter right now (rising themes, copy-wave words,
                        your watch words). Finds tiny new copies - games with 20-500 players.
  3. TRACK   (each run) Live players / visits / favourites for every game the bot cares about that wasn't
                        in RoWatcher's list this run (young games, watchlist, everything just discovered),
                        50 games per request.

All public endpoints, no key, a few dozen requests per run.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta

import config as C

UA = {"User-Agent": "Mozilla/5.0 (compatible; roblox-trend-bot/1.7)", "Accept": "application/json"}
EXPLORE = "https://apis.roblox.com/explore-api/v1/get-sorts"
SEARCH = "https://apis.roblox.com/search-api/omni-search"
GAMES = "https://games.roblox.com/v1/games"


def log(m):
    print(m, file=sys.stderr)


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def rstate(state):
    s = state.setdefault("rbx_direct", {})
    s.setdefault("session", str(uuid.uuid4()))
    s.setdefault("seen", {})        # uid -> {"name", "players", "up", "down", "genre", "place", "sorts", "day"}
    s.setdefault("searched", {})    # word -> day
    return s


# ------------------------------------------------------------- discover ---

def discover(state, t):
    """Roblox home-page sorts. Returns {uid: info} and remembers sort membership."""
    rs = rstate(state)
    if rs.get("sorts_at") and (t - datetime.fromisoformat(rs["sorts_at"])) < timedelta(minutes=C.RBX_SORTS_EVERY_MIN - 2):
        return {}
    found, ranks = {}, {}
    for device in C.RBX_DEVICES:
        tok = ""
        for _ in range(10):
            q = {"sessionId": rs["session"], "device": device, "country": "all"}
            if tok:
                q["sortsPageToken"] = tok
            try:
                d = get_json(EXPLORE + "?" + urllib.parse.urlencode(q))
            except Exception as e:
                log(f"roblox sorts failed ({device}): {e}")
                break
            for srt in d.get("sorts") or []:
                sid = srt.get("sortId") or ""
                if sid in C.RBX_SKIP_SORTS:
                    continue
                for rank, g in enumerate(srt.get("games") or [], 1):
                    uid = str(g.get("universeId") or "")
                    if not uid:
                        continue
                    f = found.setdefault(uid, {"name": g.get("name") or uid, "players": int(g.get("playerCount") or 0),
                                               "up": g.get("totalUpVotes"), "down": g.get("totalDownVotes"),
                                               "genre": g.get("genreL1"), "place": g.get("rootPlaceId"), "sorts": []})
                    if sid not in f["sorts"]:
                        f["sorts"].append(sid)
                    if sid in C.RBX_CHART_SORTS:
                        ranks[uid] = min(ranks.get(uid, 999), rank)
            tok = d.get("nextSortsPageToken")
            if not tok:
                break
            time.sleep(0.3)
    if found:
        rs["sorts_at"] = t.isoformat()
        rs["chart_rank"] = ranks
        day = _s(t)
        for uid, f in found.items():
            rs["seen"][uid] = dict(f, day=day)
    return found


# ------------------------------------------------------------ countries ---

def countries(state, t):
    """Top Trending / Up-and-Coming per country (first page only: 1 request per country).
    Remembers each game's best rank per country for the last few days, so the bot can see
    games climbing abroad before they show up in the worldwide lists."""
    rs = rstate(state)
    if rs.get("cc_at") and (t - datetime.fromisoformat(rs["cc_at"])) < timedelta(minutes=C.RBX_COUNTRY_EVERY_MIN - 2):
        return {}
    day = _s(t)
    cc = rs.setdefault("cc", {})  # uid -> {country: [best rank today, day]}
    found = {}
    ok = 0
    for country in C.RBX_COUNTRIES:
        try:
            d = get_json(EXPLORE + "?" + urllib.parse.urlencode(
                {"sessionId": rs["session"], "device": "phone", "country": country}))
        except Exception as e:
            log(f"roblox sorts failed ({country}): {e}")
            continue
        ok += 1
        for srt in d.get("sorts") or []:
            if srt.get("sortId") not in ("top-trending", "up-and-coming"):
                continue
            for rank, g in enumerate(srt.get("games") or [], 1):
                uid = str(g.get("universeId") or "")
                if not uid:
                    continue
                e = cc.setdefault(uid, {})
                prev = e.get(country)
                if not prev or prev[1] != day or rank < prev[0]:
                    e[country] = [rank, day]
                found.setdefault(uid, {"name": g.get("name") or uid, "players": int(g.get("playerCount") or 0),
                                       "up": g.get("totalUpVotes"), "down": g.get("totalDownVotes"),
                                       "genre": g.get("genreL1"), "place": g.get("rootPlaceId"), "sorts": []})
        time.sleep(0.25)
    if ok:
        rs["cc_at"] = t.isoformat()
        old = _s(t - timedelta(days=3))
        for uid in list(cc):
            cc[uid] = {k: v for k, v in cc[uid].items() if v[1] >= old}
            if not cc[uid]:
                del cc[uid]
        for uid, f in found.items():
            rs["seen"][uid] = dict(rs["seen"].get(uid, {}), **{k: v for k, v in f.items() if k != "sorts"}, day=day)
    return found


def abroad(state, uid, today):
    """Countries where the game is in Top Trending / Up-and-Coming today but it isn't in the worldwide lists.
    Returns [(country, rank)] best first."""
    rs = rstate(state)
    e = rs.get("cc", {}).get(uid) or {}
    world = set(((rs.get("seen") or {}).get(uid) or {}).get("sorts") or []) & {"top-trending", "up-and-coming"}
    if world:
        return []
    return sorted(((c, v[0]) for c, v in e.items() if v[1] == today and c not in C.RBX_HOME_COUNTRIES), key=lambda x: x[1])


# --------------------------------------------------------------- search ---

def search_words(state, today, extra=()):
    """Words worth searching today: rising themes, copy-wave words, config watch words."""
    words = list(C.RBX_SEARCH_WORDS) + list(extra)
    for p, sc, k, r, fired in (state.get("_themes") or [])[:15]:
        if k.startswith(("w:", "b:")):
            words.append(k[2:])
    rs = rstate(state)
    out, seen = [], set()
    for w in words:
        w = w.strip().lower()
        if len(w) < 3 or w in seen or rs["searched"].get(w) == today:
            continue
        seen.add(w)
        out.append(w)
    return out


def search(state, t, words):
    rs = rstate(state)
    today = _s(t)
    found = {}
    for w in words[:C.RBX_SEARCH_WORDS_PER_RUN]:
        tok = ""
        for _ in range(C.RBX_SEARCH_PAGES):
            q = {"searchQuery": w, "sessionId": rs["session"], "pageType": "all"}
            if tok:
                q["pageToken"] = tok
            try:
                d = get_json(SEARCH + "?" + urllib.parse.urlencode(q))
            except Exception as e:
                log(f"roblox search failed for {w!r}: {e}")
                break
            for grp in d.get("searchResults") or []:
                for c in grp.get("contents") or []:
                    if c.get("contentType") != "Game":
                        continue
                    uid = str(c.get("universeId") or "")
                    players = int(c.get("playerCount") or 0)
                    if not uid or players < C.RBX_MIN_PLAYERS:
                        continue
                    found[uid] = {"name": c.get("name") or uid, "players": players, "up": c.get("totalUpVotes"),
                                  "down": c.get("totalDownVotes"), "place": c.get("rootPlaceId"),
                                  "creator": c.get("creatorName"), "creator_id": c.get("creatorId"),
                                  "description": c.get("description"), "sorts": [], "search": w}
            tok = d.get("nextPageToken")
            if not tok:
                break
            time.sleep(0.3)
        rs["searched"][w] = today
    for uid, f in found.items():
        rs["seen"][uid] = dict(rs["seen"].get(uid, {}), **f, day=today)
    cut = _s(t - timedelta(days=3))
    rs["searched"] = {w: d for w, d in rs["searched"].items() if d >= cut}
    return found


# ---------------------------------------------------------------- track ---

def track(state, t, have_ids, is_young):
    """Live numbers from Roblox for games the bot follows that RoWatcher didn't return this run."""
    rs = rstate(state)
    today = _s(t)
    games = state["games"]
    cut = _s(t - timedelta(days=C.RBX_TRACK_DAYS))
    want = {}
    for uid, f in rs["seen"].items():  # just discovered
        if f.get("day", "") >= _s(t - timedelta(days=1)):
            want[uid] = 3 + f.get("players", 0) / 1e6
    for uid, r in games.items():       # followed: young games and watchlist seen recently
        if (r.get("last_seen", "") >= cut and is_young(r, today)) or uid in C.WATCHLIST:
            want[uid] = max(want.get(uid, 0), 2 if uid in C.WATCHLIST else 1)
    ids = [u for u, _ in sorted(want.items(), key=lambda kv: -kv[1]) if u not in have_ids and u.isdigit()]
    ids = ids[:C.RBX_TRACK_MAX]
    out = []
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        try:
            d = get_json(GAMES + "?universeIds=" + ",".join(batch))
        except urllib.error.HTTPError as e:
            log(f"roblox games batch failed: {e}")
            if e.code == 429:
                break
            continue
        except Exception as e:
            log(f"roblox games batch failed: {e}")
            continue
        for g in d.get("data") or []:
            raw = to_raw(g, rs["seen"].get(str(g.get("id"))) or {})
            if raw:
                out.append(raw)
        time.sleep(0.25)
    # forget discoveries that never mattered
    old = _s(t - timedelta(days=C.RBX_TRACK_DAYS))
    rs["seen"] = {u: f for u, f in rs["seen"].items() if f.get("day", "") >= old}
    return out


def to_raw(g, seen):
    """Roblox game info -> the same shape as a RoWatcher list entry, so the rest of the bot treats it the same."""
    uid = g.get("id")
    if not uid:
        return None
    cr = g.get("creator") or {}
    raw = {"universeId": uid, "name": g.get("name") or seen.get("name") or str(uid), "playing": int(g.get("playing") or 0),
           "visits": g.get("visits"), "favorites": g.get("favoritedCount"),
           "robloxCreatedAt": g.get("created"), "rootPlaceId": g.get("rootPlaceId") or seen.get("place"),
           "creatorId": cr.get("id"), "creatorName": cr.get("name"), "creatorType": cr.get("type"),
           "genre": g.get("genre_l1") or seen.get("genre") or g.get("genre"), "subgenre": g.get("genre_l2"),
           "description": g.get("description") or seen.get("description"), "_src": "roblox"}
    if seen.get("up") is not None and seen.get("down") is not None:
        raw["likes"], raw["dislikes"] = seen["up"], seen["down"]
    return raw


# -------------------------------------------------------------- driver ---

def collect(state, t, have_ids, is_young):
    """Run discovery/search as due, then track. Returns (raw games, chart list for the warehouse, summary)."""
    rs = rstate(state)
    found = {}
    try:
        found.update(discover(state, t))
    except Exception as e:
        log(f"roblox discover failed: {e}")
    try:
        found.update(countries(state, t))
    except Exception as e:
        log(f"roblox country sorts failed: {e}")
    try:
        words = search_words(state, _s(t))
        if words:
            found.update(search(state, t, words))
    except Exception as e:
        log(f"roblox search failed: {e}")
    raws = []
    try:
        raws = track(state, t, have_ids, is_young)
    except Exception as e:
        log(f"roblox track failed: {e}")
    chart = []
    if found and rs.get("chart_rank"):
        chart = [{"universeId": int(u)} for u, _ in sorted(rs["chart_rank"].items(), key=lambda kv: kv[1])]
    return raws, chart, f"{len(found)} discovered, {len(raws)} tracked"


def check():
    try:
        d = get_json(GAMES + "?universeIds=65241")
        g = (d.get("data") or [{}])[0]
        out = [f"✅ Roblox game info — {g.get('name', '?')}: {g.get('playing', 0):,} playing"]
    except Exception as e:
        out = [f"❌ Roblox game info — {e}"]
    try:
        d = get_json(EXPLORE + "?" + urllib.parse.urlencode({"sessionId": str(uuid.uuid4()), "device": "computer", "country": "all"}))
        n = sum(len(s.get("games") or []) for s in d.get("sorts") or [])
        out.append(f"✅ Roblox home-page sorts — {len(d.get('sorts') or [])} sorts, {n} games on the first page")
    except Exception as e:
        out.append(f"❌ Roblox home-page sorts — {e}")
    try:
        d = get_json(SEARCH + "?" + urllib.parse.urlencode({"searchQuery": "obby", "sessionId": str(uuid.uuid4()), "pageType": "all"}))
        n = sum(1 for g in d.get("searchResults") or [] for c in g.get("contents") or [] if c.get("contentType") == "Game")
        out.append(f"✅ Roblox search — {n} games for \"obby\"")
    except Exception as e:
        out.append(f"❌ Roblox search — {e}")
    return out

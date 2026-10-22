"""
Extra data sources for the trend bot (stage 1):

  * YouTube  - recent Roblox videos, which games they feature, how many views
  * Roblox   - Roblox's own public game data: likes/dislikes, favourites, last update
  * Community - member counts of each game's Roblox group (automatic) and of any
                Discord servers you list in config.DISCORD_INVITES

Each collector runs on its own timer (see config.py) and fails quietly: if one
source is down, the rest of the bot carries on as normal.
"""
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import config as C

# bot.py fills these in at start-up (is_young, growth, fmt) to avoid a circular import
HOOKS = {}

UA = {"User-Agent": "roblox-trend-bot/1.1", "Accept": "application/json"}


# ---------------------------------------------------------------- helpers ---

def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def src_state(state):
    s = state.setdefault("src", {})
    for k in ("last", "yt_units", "videos", "place_map", "rbx", "social", "dc", "grp", "tw", "tw_total"):
        s.setdefault(k, {})
    return s


def due(src, name, t, every_min):
    last = src["last"].get(name)
    if not last:
        return True
    return (t - datetime.fromisoformat(last)) >= timedelta(minutes=every_min - 2)


def mark(src, name, t):
    src["last"][name] = t.isoformat()


def norm(s):
    """Normalise a game name or video title for matching."""
    s = s.lower()
    s = re.sub(r"\[.*?\]|\(.*?\)|【.*?】|\{.*?\}", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    words = s.split()
    while words and words[0] in C.NAME_EDGE_WORDS:
        words.pop(0)
    while words and words[-1] in C.NAME_EDGE_WORDS:
        words.pop()
    return " ".join(words)


def log(msg):
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------- youtube ---

GAME_LINK = re.compile(r"roblox\.com/(?:[a-z]{2}/)?games/(\d+)", re.I)


def place_to_universe(src, place_id):
    m = src["place_map"]
    if place_id in m:
        return m[place_id]
    try:
        d = get_json(f"https://apis.roblox.com/universes/v1/places/{place_id}/universe")
        uid = str(d.get("universeId") or "") or None
    except Exception as e:
        log(f"place lookup failed for {place_id}: {e}")
        return None  # don't cache failures; try again later
    m[place_id] = uid
    return uid


def name_index(state):
    """normalised game name -> universe id (highest-player game wins on duplicates)."""
    idx = {}
    cands = []
    for gid, r in state["games"].items():
        cands.append((r["name"], gid, r.get("last", 0)))
    for gid, r in src_state(state)["rbx"].items():
        if r.get("name"):
            cands.append((r["name"], gid, r.get("playing", 0)))
    best = {}
    for name, gid, players in cands:
        n = norm(name)
        if len(n) < C.YT_MIN_NAME_CHARS or n in C.YT_GENERIC_NAMES:
            continue
        if n not in best or players > best[n][1]:
            best[n] = (gid, players)
    for n, (gid, _) in best.items():
        idx[n] = gid
    return idx


def match_title(title, idx):
    t = " " + norm(title) + " "
    hits = [n for n in idx if " " + n + " " in t]
    # drop names contained in a longer matched name ("sell fries" inside "sell fries 2")
    hits = [h for h in hits if not any(h != o and h in o for o in hits)]
    return [idx[h] for h in hits]


def collect_youtube(state, t, key):
    src = src_state(state)
    today = t.strftime("%Y-%m-%d")
    used = src["yt_units"].get(today, 0)

    def yt(path, params, cost):
        nonlocal used
        if used + cost > C.YT_DAILY_UNIT_CAP:
            raise RuntimeError("YouTube daily quota cap reached")
        params = dict(params, key=key)
        url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
        used += cost
        src["yt_units"][today] = used
        return get_json(url)

    after = (t - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = set()
    for q in C.YT_QUERIES:
        try:
            d = yt("search", {"part": "snippet", "type": "video", "order": "viewCount", "q": q,
                              "publishedAfter": after, "maxResults": 50, "relevanceLanguage": "en"}, 100)
        except RuntimeError as e:
            log(str(e))
            break
        for it in d.get("items", []):
            vid = (it.get("id") or {}).get("videoId")
            if vid:
                found.add(vid)

    videos = src["videos"]
    cutoff = t - timedelta(days=4)
    refresh = set(found) | {v for v, r in videos.items()
                            if datetime.fromisoformat(r["p"].replace("Z", "+00:00")) >= cutoff}
    refresh = list(refresh)
    idx = name_index(state)
    lookups = 0
    for i in range(0, len(refresh), 50):
        batch = refresh[i:i + 50]
        try:
            d = yt("videos", {"part": "snippet,statistics", "id": ",".join(batch), "maxResults": 50}, 1)
        except RuntimeError as e:
            log(str(e))
            break
        for it in d.get("items", []):
            vid = it["id"]
            sn, st = it.get("snippet", {}), it.get("statistics", {})
            views = int(st.get("viewCount", 0) or 0)
            rec = videos.get(vid)
            if rec is None:
                title = sn.get("title", "")
                desc = sn.get("description", "")
                uids = []
                for pid in dict.fromkeys(GAME_LINK.findall(desc + " " + title)):
                    if lookups >= C.YT_MAX_PLACE_LOOKUPS_PER_RUN and pid not in src["place_map"]:
                        continue
                    if pid not in src["place_map"]:
                        lookups += 1
                    u = place_to_universe(src, pid)
                    if u and u not in uids:
                        uids.append(u)
                linked = bool(uids)
                if not uids:
                    uids = match_title(title, idx)
                rec = videos[vid] = {"t": title[:120], "c": sn.get("channelTitle", "")[:40],
                                     "p": sn.get("publishedAt", t.isoformat()), "u": uids[:3],
                                     "l": linked, "v0": views, "t0": t.isoformat()}
            rec["v"] = views
            rec["t1"] = t.isoformat()

    # forget videos older than 5 days
    old = t - timedelta(days=5)
    for vid in [v for v, r in videos.items()
                if datetime.fromisoformat(r["p"].replace("Z", "+00:00")) < old]:
        del videos[vid]
    src["yt_units"] = {d: n for d, n in src["yt_units"].items() if d >= (t - timedelta(days=7)).strftime("%Y-%m-%d")}


def yt_stats(state, t, hours=48):
    """universe id -> {"n": videos, "views": total views, "top": (views, title, vid)}"""
    out = {}
    since = t - timedelta(hours=hours)
    for vid, r in src_state(state)["videos"].items():
        if datetime.fromisoformat(r["p"].replace("Z", "+00:00")) < since:
            continue
        for u in r.get("u", []):
            s = out.setdefault(u, {"n": 0, "views": 0, "top": (0, "", "")})
            s["n"] += 1
            s["views"] += r.get("v", 0)
            if r.get("v", 0) > s["top"][0]:
                s["top"] = (r.get("v", 0), r["t"], vid)
    return out


def rising_title_words(state, t):
    """Words/phrases appearing in many more Roblox video titles in the last 48h than the 48h before."""
    now_c, prev_c = {}, {}
    for r in src_state(state)["videos"].values():
        age = (t - datetime.fromisoformat(r["p"].replace("Z", "+00:00"))).total_seconds() / 3600
        bucket = now_c if age <= 48 else (prev_c if age <= 96 else None)
        if bucket is None:
            continue
        words = [w for w in norm(r["t"]).split() if len(w) >= 3 and not any(ch.isdigit() for ch in w)]
        grams = {w for w in words if w not in C.YT_TITLE_STOPWORDS}
        for a, b in zip(words, words[1:]):
            if a not in C.YT_TITLE_STOPWORDS and b not in C.YT_TITLE_STOPWORDS:
                grams.add(a + " " + b)
        for g in grams:
            bucket[g] = bucket.get(g, 0) + 1
    have_prev = bool(prev_c)
    out = []
    for g, n in now_c.items():
        p = prev_c.get(g, 0)
        if n >= C.YT_RISING_MIN_VIDEOS and (not have_prev or n >= 3 * (p + 1)):
            out.append((n, p, g))
    out.sort(reverse=True)
    # keep a phrase over its single words when counts are similar
    keep = []
    for n, p, g in out:
        if " " not in g and any(g in k.split() and kn >= n - 1 for kn, _, k in keep):
            continue
        keep.append((n, p, g))
    return keep[:8], have_prev


# ----------------------------------------------------------------- twitch ---

def twitch_token(cid, secret):
    body = urllib.parse.urlencode({"client_id": cid, "client_secret": secret,
                                   "grant_type": "client_credentials"}).encode()
    req = urllib.request.Request("https://id.twitch.tv/oauth2/token", data=body, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())["access_token"]


def twitch_get(path, cid, token, params):
    url = "https://api.twitch.tv/helix/" + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=dict(UA, **{"Client-Id": cid, "Authorization": f"Bearer {token}"}))
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def collect_twitch(state, t, cid, secret):
    src = src_state(state)
    today = t.strftime("%Y-%m-%d")
    token = twitch_token(cid, secret)
    gid_tw = src.get("tw_game_id")
    if not gid_tw:
        d = twitch_get("games", cid, token, {"name": "Roblox"})
        gid_tw = src["tw_game_id"] = d["data"][0]["id"]
    idx = name_index(state)
    per_game, total, streams, cursor = {}, 0, 0, None
    for _ in range(C.TWITCH_PAGES):
        params = {"game_id": gid_tw, "first": 100}
        if cursor:
            params["after"] = cursor
        d = twitch_get("streams", cid, token, params)
        for st in d.get("data", []):
            v = st.get("viewer_count", 0)
            total += v
            streams += 1
            for u in match_title(st.get("title", ""), idx):
                g = per_game.setdefault(u, {"v": 0, "s": 0})
                g["v"] += v
                g["s"] += 1
        cursor = (d.get("pagination") or {}).get("cursor")
        if not cursor:
            break
    tw = src["tw"]
    for u, g in per_game.items():
        day = tw.setdefault(u, {}).setdefault(today, {"v": 0, "s": 0})
        day["v"], day["s"] = max(day["v"], g["v"]), max(day["s"], g["s"])
    src["tw_total"][today] = max(src["tw_total"].get(today, 0), total)
    keep = (t - timedelta(days=C.KEEP_DAYS)).strftime("%Y-%m-%d")
    for u in list(tw):
        tw[u] = {d: v for d, v in tw[u].items() if d >= keep}
        if not tw[u]:
            del tw[u]
    src["tw_total"] = {d: v for d, v in src["tw_total"].items() if d >= keep}


def twitch_stats(state, gid):
    """(peak viewers today/latest day, growth ratio vs ~2 days before or None, streams)"""
    days = src_state(state)["tw"].get(gid) or {}
    if not days:
        return None, None, 0
    latest = max(days)
    now = days[latest]
    ref = (datetime.strptime(latest, "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
    older = [d for d in days if d <= ref]
    ratio = None
    if older and days[max(older)]["v"]:
        ratio = now["v"] / days[max(older)]["v"]
    return now["v"], ratio, now["s"]


def top_twitch(state, today, n=5):
    tw = src_state(state)["tw"]
    rows = [(d[today]["v"], d[today]["s"], g) for g, d in tw.items() if today in d]
    return sorted(rows, reverse=True)[:n]


# ----------------------------------------------------------------- roblox ---

def candidate_games(state, today, limit):
    """Games worth enriching: watchlist, young games in the top list, YouTube-linked games."""
    is_young = HOOKS["is_young"]
    pri = {}
    for gid in C.WATCHLIST:
        pri[gid] = 1e12
    for gid, r in state["games"].items():
        if r.get("last_seen") == today and r.get("last", 0) >= C.ENRICH_MIN_PLAYERS and is_young(r, today):
            pri[gid] = max(pri.get(gid, 0), r["last"])
    for vid, r in src_state(state)["videos"].items():
        for u in r.get("u", []):
            pri[u] = max(pri.get(u, 0), 1e9 + r.get("v", 0))
    return [g for g, _ in sorted(pri.items(), key=lambda kv: -kv[1])][:limit]


def collect_roblox(state, t):
    src = src_state(state)
    today = t.strftime("%Y-%m-%d")
    ids = [i for i in candidate_games(state, today, C.ROBLOX_MAX_GAMES) if i.isdigit()]
    rbx = src["rbx"]
    for i in range(0, len(ids), 50):
        batch = ",".join(ids[i:i + 50])
        try:
            d = get_json(f"https://games.roblox.com/v1/games?universeIds={batch}")
            for g in d.get("data", []):
                r = rbx.setdefault(str(g["id"]), {})
                cr = g.get("creator") or {}
                r.update({"name": g.get("name"), "place": g.get("rootPlaceId"),
                          "playing": g.get("playing", 0), "visits": g.get("visits", 0),
                          "updated": (g.get("updated") or "")[:10], "seen": today,
                          "group": cr.get("id") if cr.get("type") == "Group" else None})
                m = INVITE.search(g.get("description") or "")
                if m:
                    r["invite"] = m.group(1)
                fav = g.get("favoritedCount")
                if fav is not None:
                    r.setdefault("fav_days", {})[today] = fav
        except Exception as e:
            log(f"roblox games lookup failed: {e}")
        try:
            d = get_json(f"https://games.roblox.com/v1/games/votes?universeIds={batch}")
            for g in d.get("data", []):
                r = rbx.setdefault(str(g["id"]), {})
                r["up"], r["down"] = g.get("upVotes", 0), g.get("downVotes", 0)
        except Exception as e:
            log(f"roblox votes lookup failed: {e}")
        time.sleep(0.5)
    keep = (t - timedelta(days=C.KEEP_DAYS)).strftime("%Y-%m-%d")
    for gid in list(rbx):
        r = rbx[gid]
        if r.get("seen", today) < keep:
            del rbx[gid]
            continue
        if "fav_days" in r:
            r["fav_days"] = {d: v for d, v in r["fav_days"].items() if d >= keep}


def like_ratio(state, gid):
    r = src_state(state)["rbx"].get(gid) or {}
    up, down = r.get("up", 0) or 0, r.get("down", 0) or 0
    if up + down < 100:
        return None
    return up / (up + down)


def game_icons(gids):
    """universe id -> icon image URL (public thumbnails API, one call)."""
    ids = [g for g in dict.fromkeys(gids) if g and str(g).isdigit()][:100]
    if not ids:
        return {}
    try:
        d = get_json("https://thumbnails.roblox.com/v1/games/icons?" + urllib.parse.urlencode(
            {"universeIds": ",".join(ids), "size": "150x150", "format": "Png", "isCircular": "false"}))
        return {str(x["targetId"]): x["imageUrl"] for x in d.get("data", []) if x.get("imageUrl")}
    except Exception as e:
        log(f"icon lookup failed: {e}")
        return {}


def roblox_link(state, gid):
    place = (src_state(state)["rbx"].get(gid) or {}).get("place")
    return f"<https://www.roblox.com/games/{place}>" if place else None


# ---------------------------------------------------------------- discord ---

INVITE = re.compile(r"(?:discord\.gg|discord(?:app)?\.com/invite)/([A-Za-z0-9-]+)", re.I)


def collect_community(state, t):
    """Roblox group member counts (automatic) + Discord member counts (invites you list)."""
    src = src_state(state)
    today = t.strftime("%Y-%m-%d")
    rbx, grp, dc = src["rbx"], src["grp"], src["dc"]
    ids = [i for i in candidate_games(state, today, C.COMMUNITY_MAX_GAMES) if i.isdigit()]

    # Roblox groups (public, no key). Several games can share one group.
    groups = []
    for gid in ids:
        g = (rbx.get(gid) or {}).get("group")
        if g and str(g) not in groups:
            groups.append(str(g))
    for g in groups[:C.GROUP_LOOKUPS_PER_RUN]:
        try:
            d = get_json(f"https://groups.roblox.com/v1/groups/{g}")
            n = d.get("memberCount")
            if n:
                grp.setdefault(g, {})[today] = n
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log("Roblox groups rate limit hit; stopping this run")
                break
            log(f"group {g} failed: {e}")
        except Exception as e:
            log(f"group {g} failed: {e}")
        time.sleep(0.5)

    # Discord: invites from config (plus any found in a game's description)
    invites = dict(C.DISCORD_INVITES)
    for gid in ids:
        inv = (rbx.get(gid) or {}).get("invite")
        if inv and gid not in invites:
            invites[gid] = inv
    for gid, code in list(invites.items())[:C.DISCORD_MAX_GAMES]:
        code = INVITE.search(code).group(1) if INVITE.search(code) else code
        try:
            d = get_json(f"https://discord.com/api/v10/invites/{code}?with_counts=true")
            n = d.get("approximate_member_count")
            if n:
                dc.setdefault(gid, {})[today] = n
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log("Discord rate limit hit; stopping member lookups this run")
                break
            log(f"discord invite {code} for {gid} failed ({e.code}) — is the invite still valid?")
        except Exception as e:
            log(f"discord invite {code} failed: {e}")
        time.sleep(1.2)

    keep = (t - timedelta(days=C.KEEP_DAYS)).strftime("%Y-%m-%d")
    for store in (dc, grp):
        for k in list(store):
            store[k] = {d: v for d, v in store[k].items() if d >= keep}
            if not store[k]:
                del store[k]


def _growth_of(days):
    """(latest value, % growth vs ~2 days earlier) from a {day: count} dict."""
    if not days:
        return None, None
    latest = max(days)
    now = days[latest]
    ref = datetime.strptime(latest, "%Y-%m-%d") - timedelta(days=2)
    older = [d for d in days if datetime.strptime(d, "%Y-%m-%d") <= ref]
    if not older:
        return now, None
    prev = days[max(older)]
    return now, ((now / prev - 1) * 100 if prev else None)


def group_growth(state, gid):
    g = (src_state(state)["rbx"].get(gid) or {}).get("group")
    if not g:
        return None, None
    return _growth_of(src_state(state)["grp"].get(str(g)) or {})


def discord_growth(state, gid, today=None):
    """(members now, % growth vs ~2 days earlier) or (members, None)."""
    return _growth_of(src_state(state)["dc"].get(gid) or {})


def fav_growth(state, gid):
    days = (src_state(state)["rbx"].get(gid) or {}).get("fav_days") or {}
    ds = sorted(days)
    if len(ds) < 3:
        return None
    a, b = days[ds[-3]], days[ds[-1]]
    return (b / a - 1) * 100 if a else None


# ------------------------------------------------------------------- heat ---

def heat(state, gid, today, cutoff, yts):
    """Combine every source into one 0-100 score. Returns dict or None."""
    growth = HOOKS["growth"]
    r = state["games"].get(gid)
    parts, signals = {}, []
    score = 0.0

    # Players (RoWatcher): today's high vs same kind of day last week
    ratio = None
    if r:
        ratio, _ = growth(r, today, cutoff, state.get("baseline_day"))
        if not ratio:
            yday = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            ratio, _ = growth(r, yday, cutoff, state.get("baseline_day"))
    if ratio:
        parts["players"] = ratio
        score += max(0, min(40, 25 * math.log2(ratio)))
        if ratio >= 1.5:
            signals.append("players")

    # YouTube: videos in the last 48h and their views
    y = yts.get(gid)
    if y:
        parts["yt"] = y
        score += min(20, 5 * y["n"]) + max(0, min(15, 5 * math.log10(max(y["views"], 1) / 10000)))
        if y["n"] >= C.YT_SIGNAL_MIN_VIDEOS or y["views"] >= C.YT_SIGNAL_MIN_VIEWS:
            signals.append("youtube")

    # Community: Roblox group and/or Discord growth over ~2 days
    best = None
    for key, (members, pct) in (("group", group_growth(state, gid)), ("discord", discord_growth(state, gid))):
        if members:
            parts[key] = (members, pct)
            if pct is not None and (best is None or pct > best[1]):
                best = (members, pct)
    if best:
        score += max(0, min(20, best[1] * 2))
        if best[1] >= C.COMMUNITY_SIGNAL_PCT and best[0] >= 500:
            signals.append("community")

    # Twitch: viewers on streams featuring the game
    tv, tratio, ts = twitch_stats(state, gid)
    if tv:
        parts["twitch"] = (tv, tratio, ts)
        score += max(0, min(10, 4 * math.log10(max(tv, 1) / 10)))
        if tv >= C.TWITCH_SIGNAL_VIEWERS and tratio is not None and tratio >= C.TWITCH_SIGNAL_GROWTH:
            signals.append("twitch")

    # Favourites growth (Roblox) - a small bonus
    fg = fav_growth(state, gid)
    if fg is not None:
        parts["fav"] = fg
        score += max(0, min(10, fg))

    # Quality: like ratio
    lr = like_ratio(state, gid)
    if lr is not None:
        parts["likes"] = lr
        score += 5 if lr >= 0.9 else (-10 if lr < 0.7 else 0)

    if not parts:
        return None
    return {"score": max(0, min(100, round(score))), "signals": signals, "parts": parts}


def heat_line(state, gid, h, name=None):
    fmt = HOOKS["fmt"]
    p = h["parts"]
    bits = [f"**heat {h['score']}**"]
    if "players" in p:
        bits.append(f"players {p['players']:.1f}×")
    if "yt" in p:
        bits.append(f"YouTube {p['yt']['n']} vid{'s' if p['yt']['n'] != 1 else ''} / {fmt(p['yt']['views'])} views")
    for key, label in (("group", "group"), ("discord", "Discord")):
        if key in p:
            m, pct = p[key]
            bits.append(f"{label} {fmt(m)}" + (f" ({pct:+.0f}%)" if pct is not None else ""))
    if "twitch" in p:
        tv, tr, ts = p["twitch"]
        bits.append(f"Twitch {fmt(tv)} viewers" + (f" ({tr:.1f}×)" if tr else ""))
    if "likes" in p:
        bits.append(f"👍 {p['likes']*100:.0f}%")
    name = name or game_name(state, gid)
    link = roblox_link(state, gid) or f"<https://rowatcher.com/games/{gid}>"
    return f"{name[:40]} — " + " · ".join(bits) + f" {link}"


def game_name(state, gid):
    r = state["games"].get(gid) or src_state(state)["rbx"].get(gid) or {}
    return r.get("name") or C.WATCHLIST.get(gid) or gid


def players_now(state, gid):
    r = state["games"].get(gid)
    if r and r.get("last_seen"):
        return r.get("last", 0)
    return (src_state(state)["rbx"].get(gid) or {}).get("playing", 0)


# ---------------------------------------------------------------- driver ---

def collect_all(state, t, env):
    """Run each collector that is due. Never raises."""
    src = src_state(state)
    yt_key = env.get("YOUTUBE_API_KEY")
    tw_id, tw_secret = env.get("TWITCH_CLIENT_ID"), env.get("TWITCH_CLIENT_SECRET")
    jobs = [
        ("twitch", C.TWITCH_EVERY_MIN,
         (lambda: collect_twitch(state, t, tw_id, tw_secret)) if (tw_id and tw_secret) else None),
        ("youtube", C.YT_EVERY_MIN, (lambda: collect_youtube(state, t, yt_key)) if yt_key else None),
        ("roblox", C.ROBLOX_EVERY_MIN, lambda: collect_roblox(state, t)),
        ("community", C.COMMUNITY_EVERY_MIN, lambda: collect_community(state, t)),
    ]
    ran = []
    for name, every, fn in jobs:
        if fn is None or not due(src, name, t, every):
            continue
        try:
            fn()
            ran.append(name)
        except Exception as e:
            log(f"{name} collector failed: {e}")
        mark(src, name, t)
    return ran


def check_sources(env):
    """Tiny live test of every source. Returns a list of result lines."""
    out = []
    try:
        d = get_json("https://games.roblox.com/v1/games?universeIds=10155360168")
        g = d["data"][0]
        out.append(f"✅ Roblox games data — {g['name']}: {g['playing']:,} playing, {g.get('favoritedCount', 0):,} favourites")
    except Exception as e:
        out.append(f"❌ Roblox games data — {e}")
    try:
        d = get_json("https://games.roblox.com/v1/games/votes?universeIds=10155360168")
        g = d["data"][0]
        out.append(f"✅ Roblox likes — 👍 {g['upVotes']:,} / 👎 {g['downVotes']:,}")
    except Exception as e:
        out.append(f"❌ Roblox likes — {e}")
    try:
        d = get_json("https://games.roblox.com/v1/games?universeIds=10155360168")
        cr = d["data"][0].get("creator") or {}
        if cr.get("type") == "Group":
            g = get_json(f"https://groups.roblox.com/v1/groups/{cr['id']}")
            out.append(f"✅ Roblox group members — {g.get('name', cr.get('name'))}: {g.get('memberCount', 0):,} members")
        else:
            out.append("⚪ Roblox group members — test game isn't group-owned, can't check")
    except Exception as e:
        out.append(f"❌ Roblox group members — {e}")
    if C.DISCORD_INVITES:
        gid, code = next(iter(C.DISCORD_INVITES.items()))
        code = INVITE.search(code).group(1) if INVITE.search(code) else code
        try:
            d = get_json(f"https://discord.com/api/v10/invites/{code}?with_counts=true")
            out.append(f"✅ Discord member counts — {C.WATCHLIST.get(gid, gid)}: {d.get('approximate_member_count', 0):,} members")
        except Exception as e:
            out.append(f"❌ Discord member counts — invite '{code}': {e} (is the invite still valid?)")
    else:
        out.append("⚪ Discord member counts — no invites added to DISCORD_INVITES in config.py yet (optional)")
    icons = game_icons(["10155360168"])
    out.append("✅ Roblox game icons (for alert cards)" if icons else "❌ Roblox game icons — cards will show without pictures")
    try:
        d = get_json("https://apis.roblox.com/universes/v1/places/4924922222/universe")
        out.append(f"✅ Roblox place → game lookup — {d.get('universeId')}")
    except Exception as e:
        out.append(f"❌ Roblox place → game lookup — {e}")
    cid, secret = env.get("TWITCH_CLIENT_ID"), env.get("TWITCH_CLIENT_SECRET")
    if not (cid and secret):
        out.append("⚪ Twitch — no TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET secrets yet (optional, see SETUP.md)")
    else:
        try:
            tok = twitch_token(cid, secret)
            g = twitch_get("games", cid, tok, {"name": "Roblox"})["data"][0]["id"]
            d = twitch_get("streams", cid, tok, {"game_id": g, "first": 1})
            top = d["data"][0] if d.get("data") else {}
            out.append(f"✅ Twitch — top Roblox stream now: {top.get('viewer_count', 0):,} viewers, "
                       f"\"{(top.get('title') or '')[:50]}\"")
        except urllib.error.HTTPError as e:
            out.append(f"❌ Twitch — HTTP {e.code}: {e.read()[:150].decode(errors='ignore')}")
        except Exception as e:
            out.append(f"❌ Twitch — {e}")
    key = env.get("YOUTUBE_API_KEY")
    if not key:
        out.append("⚪ YouTube — no YOUTUBE_API_KEY secret yet (see SETUP.md)")
    else:
        try:
            d = get_json("https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(
                {"part": "snippet", "type": "video", "q": "roblox", "maxResults": 1, "key": key}))
            title = d["items"][0]["snippet"]["title"] if d.get("items") else "(no results)"
            out.append(f"✅ YouTube — e.g. \"{title[:60]}\"")
        except urllib.error.HTTPError as e:
            out.append(f"❌ YouTube — HTTP {e.code}: {e.read()[:150].decode(errors='ignore')}")
        except Exception as e:
            out.append(f"❌ YouTube — {e}")
    return out

"""Simulated Roblox, RoWatcher, YouTube and Discord for end-to-end tests of the trend bot (no network)."""
import io, json, math, random, sys, os, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

BOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BOT)
import config as C

rng = random.Random(11)
START = datetime(2026, 9, 24, tzinfo=timezone.utc)
NOW = [START]
CAP = [2000]

THEMES = ["Tycoon", "Obby", "Simulator", "Tower Defense", "Roleplay", "Anomaly", "Horror", "Pet", "Brainrot", "Tornado",
          "Car", "Fishing", "Mining", "Escape", "Battles", "Clicker", "Farm", "Cooking", "Survival", "Racing"]
ADJ = ["Super", "Mega", "Ultimate", "Tiny", "Crazy", "Epic", "Lucky", "Sneaky", "Wild", "Silly", "Golden", "Frozen"]
FEATS = ["Daily rewards and login streaks!", "Use codes for free coins!", "Trade with friends.", "Collect pets!",
         "Limited time event!", "Rebirth for multipliers.", "Join the group for rewards.", "Play with friends for a boost."]
GENRES = ["Simulation", "Roleplay", "Obby & Platformer", "Survival", "Shooter", "RPG", "Strategy", "Action"]


class G:
    pass


games = []
def mk(uid, name, base, created, kind="est", **kw):
    g = G(); g.uid = str(uid); g.name = name; g.base = base; g.created = created; g.kind = kind
    g.q = rng.gauss(0, 1); g.habit = 0.55 + 0.35 / (1 + math.exp(-g.q)) ; g.genre = rng.choice(GENRES)
    g.mpd = math.exp(3.0 + 0.4 * g.q); g.sess = math.exp(rng.gauss(0.6, 0.3)); g.new = max(0.08, min(0.8, 0.45 - 0.15 * g.q))
    g.like = 1 / (1 + math.exp(-(1.2 + 0.7 * g.q))); g.visits = int(base * 3000 * rng.uniform(5, 50)); g.fav = 0.002 + 0.002 * max(0, g.q)
    g.desc = " ".join(rng.sample(FEATS, 2) + (["Daily rewards!"] if g.q > 0.8 else []))
    g.welcome = rng.random() < 0.6; g.hasb = rng.random() < 0.75
    for k, v in kw.items(): setattr(g, k, v)
    games.append(g); return g

for uid, label in C.WATCHLIST.items():
    mk(uid, label, rng.uniform(3000, 40000), "2026-09-0%d" % rng.randint(1, 9), kind="young", t0=-25, peak=rng.uniform(8000, 60000), rise=6)
for i in range(int(os.environ.get('SIM_ESTABLISHED', 2600))):
    created = (START - timedelta(days=rng.randint(90, 2500))).strftime("%Y-%m-%d")
    mk(9000000 + i, f"{rng.choice(ADJ)} {rng.choice(THEMES)} {rng.choice(['World','Island','Legends','Factory','Life','Story','Rush','2'])}",
       10 ** rng.uniform(2.1, 4.9), created)
# young games: launched during or just before the sim, some break out
for i in range(int(os.environ.get('SIM_YOUNG', 260))):
    t0 = rng.randint(-40, 22)
    theme = "Chocolate" if (i % 9 == 0 and t0 > 8) else rng.choice(THEMES)
    created = (START + timedelta(days=t0)).strftime("%Y-%m-%d")
    hit = rng.random() < (0.35 if theme == "Chocolate" else 0.12)
    peak = 10 ** rng.uniform(3.6, 4.9) if hit else 10 ** rng.uniform(2.0, 3.3)
    mk(11000000 + i, f"{theme} {rng.choice(['Factory','Tycoon','Simulator','Obby','Battles','Rush','Life'])} {rng.choice(['','2','!','[NEW]'])}".strip(),
       peak, created, kind="young", t0=t0, peak=peak, rise=rng.uniform(3, 10), hit=hit)


def ccu(g, t):
    day = (t - START).total_seconds() / 86400
    hour = t.hour + t.minute / 60
    diurnal = 0.65 + 0.35 * math.cos((hour - 19) / 24 * 2 * math.pi)
    weekend = 1.35 if t.weekday() >= 5 else (1.0 if g.habit > 0.75 else 0.9)
    if g.kind == "est":
        lvl = g.base * math.exp(0.01 * math.sin(day / 5 + g.q))
    else:
        age = day - g.t0
        if age < 0:
            return 0
        lvl = g.peak / (1 + math.exp(-(age - g.rise) / 1.6))
        if age > g.rise + 6:
            lvl *= math.exp(-(age - g.rise - 6) * (0.02 if g.habit > 0.75 else 0.06))
    wk = weekend if g.habit > 0.7 else weekend * (1.1 if t.weekday() >= 5 else 0.8)
    return max(0, int(lvl * diurnal * wk * math.exp(rng.gauss(0, 0.03))))


def gdict(g, t):
    p = ccu(g, t)
    g.visits += int(p * 1440 / max(1, g.mpd / g.sess) / 6)
    return {"universeId": int(g.uid), "name": g.name, "playing": p, "visits": g.visits, "favorites": int(g.visits * g.fav),
            "likes": int(g.visits * 0.002 * g.like), "dislikes": int(g.visits * 0.002 * (1 - g.like)),
            "robloxCreatedAt": g.created + "T00:00:00Z", "rootPlaceId": int(g.uid) * 3, "creatorId": int(g.uid) % 997,
            "creatorType": "Group", "creatorName": f"Studio {int(g.uid) % 997}", "genre": g.genre,
            "breakoutScore": 50 + 10 * g.q, "favConversion": g.fav, "algoReach": 0.5,
            "revenueEstimate": {"expected": {"dailyUsd": p * 0.12 * (1 + 0.3 * g.q)}}, "description": g.desc,
            "firstSeen": g.created}


def respond(url):
    t = NOW[0]
    u = urllib.parse.urlparse(url); q = dict(urllib.parse.parse_qsl(u.query)); path = u.path
    host = u.netloc
    if "rowatcher" in host:
        path = path.split("/v1", 1)[-1] if "/v1" in path else path
        if path == "/games":
            page, size = int(q.get("page", 1)), int(q.get("pageSize", 100))
            if page * size > CAP[0]:
                raise urllib.error.HTTPError(url, 403, "Forbidden", {}, io.BytesIO(b'{"success":false,"error":{"code":"ANON_LIMIT","limit":2000}}'))
            ranked = sorted((g for g in games if ccu(g, t) > 0), key=lambda g: -ccu(g, t))
            return {"data": [gdict(g, t) for g in ranked[(page - 1) * size: page * size]]}
        if path.startswith("/games/") and path.endswith("/history"):
            uid = path.split("/")[2]; g = next((x for x in games if x.uid == uid), None)
            if not g: return {"data": []}
            pts = []; tt = t - timedelta(days=60)
            vis = max(0, g.visits - 10**7)
            while tt < t:
                p = ccu(g, tt); vis += int(p * 1440 / max(1, g.mpd / g.sess) / 4)
                if p: pts.append({"time": tt.strftime("%Y-%m-%dT%H:%M:%SZ"), "playing": p, "visits": vis})
                tt += timedelta(hours=6)
            return {"data": pts}
        if path.startswith("/games/"):
            uid = path.split("/")[2]; g = next((x for x in games if x.uid == uid), None)
            return {"data": gdict(g, t) if g else {}}
        if path == "/charts":
            young = [g for g in games if g.kind == "young" and ccu(g, t) > 0]
            def mom(g):
                return ccu(g, t) / max(50, ccu(g, t - timedelta(days=2)))
            pushed = sorted(young, key=lambda g: -(mom(g) * (1 + 0.5 * g.q)))[:40]
            return {"data": [gdict(g, t) for g in pushed]}
        if path == "/trends":
            return {"data": [{"_id": "t1", "name": "Chocolate games", "keywords": ["chocolate"]}]}
        if path == "/platform/ccu":
            return {"data": {"history": [{"recordedAt": (t - timedelta(minutes=5 * k)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                           "totalCCU": int(15e6 * (1.35 if t.weekday() >= 5 else 1))} for k in range(288)]}}
        return {"data": []}
    if host == "apis.roblox.com" and "get-sorts" in path:
        young = [g for g in games if g.kind == "young" and ccu(g, t) > 0]
        def mom(g):
            return ccu(g, t) / max(30, ccu(g, t - timedelta(days=2)))
        up = sorted(young, key=lambda g: -(mom(g) * (1 + 0.5 * g.q)))[:90]
        top = sorted(games, key=lambda g: -ccu(g, t))[:90]
        def gl(lst):
            return [{"universeId": int(g.uid), "rootPlaceId": int(g.uid) * 3, "name": g.name, "playerCount": ccu(g, t),
                     "totalUpVotes": int(g.visits * 0.002 * g.like), "totalDownVotes": int(g.visits * 0.002 * (1 - g.like)),
                     "genreL1": g.genre} for g in lst]
        if q.get("sortsPageToken"):
            return {"sorts": [{"sortId": "trending-in-simulation", "games": gl(up[40:80])}], "nextSortsPageToken": None}
        return {"sorts": [{"sortId": "filters_v5", "games": []}, {"sortId": "top-trending", "games": gl(top)},
                          {"sortId": "up-and-coming", "games": gl(up)}], "nextSortsPageToken": "p2"}
    if host == "apis.roblox.com" and "omni-search" in path:
        w = q.get("searchQuery", "").lower()
        hits = [g for g in games if w in g.name.lower() and ccu(g, t) > 0][:30]
        if q.get("pageToken"):
            return {"searchResults": [], "nextPageToken": None}
        return {"searchResults": [{"contentGroupType": "Game", "contents": [{"universeId": int(g.uid), "name": g.name,
                 "playerCount": ccu(g, t), "totalUpVotes": 10, "totalDownVotes": 1, "rootPlaceId": int(g.uid) * 3,
                 "contentType": "Game", "description": g.desc}]} for g in hits], "nextPageToken": None}
    if host == "games.roblox.com" and path == "/v1/games":
        ids = q.get("universeIds", "").split(",")
        out = []
        for g in games:
            if g.uid in ids:
                out.append({"id": int(g.uid), "rootPlaceId": int(g.uid) * 3, "name": g.name, "description": g.desc,
                            "creator": {"id": int(g.uid) % 997, "name": "Studio", "type": "Group"}, "playing": ccu(g, t),
                            "visits": g.visits, "created": g.created + "T00:00:00Z", "genre_l1": g.genre,
                            "favoritedCount": int(g.visits * g.fav)})
        return {"data": out}
    if host == "www.googleapis.com" and "/youtube/v3/search" in path:
        hot = sorted([g for g in games if g.kind == "young" and ccu(g, t) > 0],
                     key=lambda g: -(ccu(g, t + timedelta(days=3)) / max(30, ccu(g, t))))[:25]
        short = q.get("videoDuration") == "short"
        items = [{"id": {"videoId": f"{'s' if short else 'v'}{g.uid}{t:%m%d%H}"}} for g in hot[:15 if short else 8]]
        return {"items": items}
    if host == "www.googleapis.com" and "/youtube/v3/videos" in path:
        out = []
        for vid in q.get("id", "").split(","):
            uid = vid[1:-6]
            g = next((x for x in games if x.uid == uid), None)
            if not g:
                continue
            short = vid.startswith("s")
            tag = "#" + g.name.lower().replace(" ", "").replace("!", "").replace("[new]", "")
            growth = ccu(g, t + timedelta(days=3)) / max(30, ccu(g, t))
            out.append({"id": vid, "snippet": {"title": (f"this game is crazy {tag} #roblox" if short else f"I played {g.name} for 24 hours"),
                        "description": "", "channelTitle": "Chan", "channelId": "c" + uid[-3:],
                        "publishedAt": (t - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")},
                        "statistics": {"viewCount": str(int(2000 * growth * (5 if short else 1)))},
                        "contentDetails": {"duration": "PT0M45S" if short else "PT12M3S"}})
        return {"items": out}
    if host == "www.googleapis.com" and "/youtube/v3/channels" in path:
        return {"items": [{"id": c, "statistics": {"subscriberCount": "50000"}} for c in q.get("id", "").split(",")]}
    if host == "apis.roblox.com" and "/game-passes/" in path:
        uid = path.split("/universes/")[1].split("/")[0]
        g = next((x for x in games if x.uid == uid), None)
        r = random.Random(int(uid))
        names = ["VIP", "2x Cash", "Auto Collect", "Extra Storage", "Lucky Boost", "Rainbow Trail", "Admin Commands", "Teleport"]
        k = r.randint(1, 8) + (3 if g and g.q > 0.5 else 0)
        return {"gamePasses": [{"name": names[i % 8], "displayName": names[i % 8], "price": r.choice([49, 99, 149, 199, 299, 499, 799]),
                                "isForSale": True} for i in range(k)]}
    if host == "thumbnails.roblox.com":
        ids = q.get("universeIds", "").split(",")
        day = (t - START).days
        return {"data": [{"targetId": int(u), "imageUrl": f"https://tr.rbxcdn.com/icon/{u}/{(day // 9) if int(u) % 7 == 0 else 0}.png"}
                         for u in ids if u]}
    if "badges.roblox.com" in host:
        uid = path.split("/universes/")[1].split("/")[0]; g = next((x for x in games if x.uid == uid), None)
        if not g or not g.hasb: return {"data": [], "nextPageCursor": None}
        avg = max(1, ccu(g, t)) * 0.8; dau = avg * 1440 / g.mpd; rows = []
        def b(name, desc, share):
            rows.append({"id": len(rows) + 1, "name": name, "description": desc, "enabled": True,
                         "statistics": {"awardedCount": int(dau * 50 * share + 1), "pastDayAwardedCount": int(dau * share),
                                        "winRatePercentage": round(share, 3)}})
        if g.welcome: b("Welcome!", "You joined the game", g.new)
        b("First Steps", "Do your first thing", g.new * 0.6)
        for lv, f in ((10, .3), (50, .08), (100, .02)): b(f"Level {lv}", "", g.new * f)
        b("7 Day Streak", "Log in 7 days in a row", g.new * 0.03 * (1 + g.q if g.q > -1 else 0.1))
        return {"data": rows, "nextPageCursor": None}
    raise urllib.error.HTTPError(url, 404, "not simulated", {}, io.BytesIO(b"{}"))


class FakeResp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): return False


SENT = []
def _png(seed):
    try:
        from PIL import Image
    except ImportError:
        return b""
    r = random.Random(seed)
    im = Image.new("L", (32, 32))
    im.putdata([r.randint(0, 255) for _ in range(32 * 32)])
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def fake_urlopen(req, timeout=None, **kw):
    url = req.full_url if hasattr(req, "full_url") else req
    if "tr.rbxcdn.com/icon/" in url:
        uid = url.split("/icon/")[1].split("/")[0]
        n = int(uid)
        seed = (11000000 + (n % 5)) if (n % 11 == 0 and n >= 11000000) else n  # some young games copy a hit's icon
        return FakeResp(_png(seed))
    if "discord.com" in url:
        SENT.append(req.data); return FakeResp(b"{}")
    return FakeResp(json.dumps(respond(url)).encode())


urllib.request.urlopen = fake_urlopen

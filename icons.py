"""
Icons and titles: what changing them does, and copies that hide behind different names.

Once a day, for up to ICON_TRACK_MAX games (young games, the board, the watchlist and top earners):
  * the icon's address changes when the icon changes -> logged as an icon change
  * a small perceptual fingerprint of the icon (difference hash, 64 bits) is kept
Three days after an icon or title change the bot compares players before and after, so the weekly
report can say what icon and title changes typically do.
New young games whose icon fingerprint is very close to a big game's icon (from another studio) are
flagged as icon copies — that catches copy waves even when the titles differ.
"""
import io
import json
import sys
import urllib.request
from datetime import datetime, timedelta
from statistics import median

import config as C


def log(m):
    print(m, file=sys.stderr)


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def dhash(png):
    """64-bit difference hash of an image (needs Pillow). Returns int or None."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        im = Image.open(io.BytesIO(png)).convert("L").resize((9, 8))
        px = list(im.getdata())
        bits = 0
        for row in range(8):
            for col in range(8):
                bits = (bits << 1) | (1 if px[row * 9 + col] > px[row * 9 + col + 1] else 0)
        return bits
    except Exception:
        return None


def distance(a, b):
    return bin(a ^ b).count("1")


def _download(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as r:
        return r.read()


def avg_players(db, uid, lo, hi):
    rows = db.execute("SELECT peak, sum_ccu, n FROM daily WHERE uid=? AND day>=? AND day<=?", (uid, lo, hi)).fetchall()
    vals = [(r["sum_ccu"] / r["n"]) if r["n"] and r["n"] >= 3 else (r["peak"] or 0) * 0.75 for r in rows]
    return sum(vals) / len(vals) if vals else None


def update(db, state, today, ids, icon_lookup, big_ids):
    """ids: games to check today. icon_lookup(list) -> {uid: url}. big_ids: established hits to compare copies against."""
    ic = state.setdefault("icons", {})
    if state.get("icons_day") == today:
        return 0, 0
    ids = [u for u in dict.fromkeys(ids) if u][:C.ICON_TRACK_MAX]
    want = ids + [u for u in big_ids if u not in ic][:100]
    urls = {}
    for i in range(0, len(want), 100):
        urls.update(icon_lookup(want[i:i + 100]))
    changes = state.setdefault("icon_changes", [])
    nch = 0
    hashed = 0
    for uid, url in urls.items():
        prev = ic.get(uid)
        h = prev.get("h") if prev else None
        if not prev or prev.get("u") != url:
            if prev and prev.get("u"):
                changes.append({"uid": uid, "day": today, "kind": "icon",
                                "before": avg_players(db, uid, _s(_d(today) - timedelta(days=3)), _s(_d(today) - timedelta(days=1)))})
                nch += 1
            if hashed < C.ICON_TRACK_MAX:
                try:
                    h = dhash(_download(url))
                    hashed += 1
                except Exception as e:
                    log(f"icon download failed for {uid}: {e}")
        ic[uid] = {"u": url, "h": h, "d": today}
    # title changes (renames are already logged by the theme module)
    try:
        for r in db.execute("SELECT uid, day FROM renames WHERE day=?", (today,)):
            changes.append({"uid": r["uid"], "day": today, "kind": "title",
                            "before": avg_players(db, r["uid"], _s(_d(today) - timedelta(days=3)), _s(_d(today) - timedelta(days=1)))})
    except Exception:
        pass
    # effect after 3 days
    for c in changes:
        if "after" not in c and (_d(today) - _d(c["day"])).days >= 4:
            c["after"] = avg_players(db, c["uid"], _s(_d(c["day"]) + timedelta(days=1)), _s(_d(c["day"]) + timedelta(days=3)))
    cut = _s(_d(today) - timedelta(days=120))
    state["icon_changes"] = [c for c in changes if c["day"] >= cut][-2000:]
    # icon copies: new young games vs established hits from other studios
    copies = state.setdefault("icon_copies", {})
    creators = {r["uid"]: r["creator_id"] for r in db.execute("SELECT uid, creator_id FROM games")}
    bigs = [(u, ic[u]["h"]) for u in big_ids if u in ic and ic[u].get("h") is not None]
    ncp = 0
    for uid in ids:
        x = ic.get(uid)
        if not x or x.get("h") is None or uid in copies or uid in big_ids:
            continue
        best = None
        for bu, bh in bigs:
            if bu == uid or (creators.get(bu) and creators.get(bu) == creators.get(uid)):
                continue
            dist = distance(x["h"], bh)
            if dist <= C.ICON_COPY_DISTANCE and (best is None or dist < best[1]):
                best = (bu, dist)
        if best:
            copies[uid] = [best[0], best[1], today]
            ncp += 1
    old = _s(_d(today) - timedelta(days=30))
    state["icon_copies"] = {u: v for u, v in copies.items() if v[2] >= old}
    for u in [u for u, v in ic.items() if v.get("d", "") < _s(_d(today) - timedelta(days=30))]:
        del ic[u]
    state["icons_day"] = today
    return nch, ncp


def effects(state):
    """Median % change in players 3 days after icon / title changes."""
    out = {}
    for kind in ("icon", "title"):
        ch = [c for c in state.get("icon_changes") or [] if c["kind"] == kind and c.get("after") and c.get("before")]
        if len(ch) >= 8:
            d = [(c["after"] / c["before"] - 1) * 100 for c in ch]
            out[kind] = {"n": len(ch), "median": median(d), "up": sum(1 for x in d if x >= 10) / len(d)}
    return out

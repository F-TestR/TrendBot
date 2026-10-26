"""
Roblox platform events (The Hollow, The Hunt, The Games...): games taking part get a temporary boost
from the event, not from real demand. The bot spots them two ways:

  1. known event names in config.RBX_EVENTS appearing in a game's title tag, e.g. "[THE HOLLOW] Clean Crew"
  2. any new bracket tag that suddenly appears in many games at once (EVENT_MIN_GAMES+ within a few days)
     and isn't an ordinary word like UPDATE / NEW / FREE / a holiday emoji

Games with an event tag are marked: their surges are labelled "boosted by a Roblox event", the Trend Score
treats the boost with caution, and the digest says so.
"""
import re
from datetime import datetime, timedelta

import config as C

TAG = re.compile(r"[\[\(]([^\]\)]{3,40})[\]\)]")
ORDINARY = re.compile(r"^\W*(upd(ate)?\s*\d*|new|free|beta|alpha|release|event|x\d+|\d+x|sale|halloween|christmas|"
                      r"winter|summer|spooky|part\s*\d+|w\d+|season\s*\d+|testing|test|new map|new stages|vip|ugc)\W*$", re.I)


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def tags_of(name):
    out = []
    for m in TAG.findall(name or ""):
        t = re.sub(r"[^a-z0-9 ]+", " ", m.lower())
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) >= 3 and not ORDINARY.match(t):
            out.append(t)
    return out


def update(state, today):
    """Find event tags; returns {tag: number of games}. Stores state['events'] = {tag: first_day}."""
    ev = state.setdefault("events", {})
    counts = {}
    for gid, r in state["games"].items():
        if r.get("last_seen") != today:
            continue
        for t in tags_of(r.get("name")):
            counts[t] = counts.get(t, 0) + 1
    seen = state.setdefault("tag_seen", {})
    for t, n in counts.items():
        seen.setdefault(t, today)
    for known in C.RBX_EVENTS:
        for t, n in counts.items():
            if known in t:
                ev.setdefault(t, today)
    cut = _s(datetime.strptime(today, "%Y-%m-%d") - timedelta(days=C.EVENT_NEW_DAYS))
    for t, n in counts.items():
        if n >= C.EVENT_MIN_GAMES and seen.get(t, today) >= cut:
            ev.setdefault(t, today)
    old = _s(datetime.strptime(today, "%Y-%m-%d") - timedelta(days=45))
    for t in [t for t, d in ev.items() if d < old and counts.get(t, 0) == 0]:
        del ev[t]
    for t in [t for t, d in seen.items() if d < old and counts.get(t, 0) == 0]:
        del seen[t]
    return {t: counts.get(t, 0) for t in ev}


def event_of(state, name):
    """The event tag in a game's title, if it's taking part in a Roblox event."""
    ev = state.get("events") or {}
    for t in tags_of(name):
        if t in ev:
            return t
    return None

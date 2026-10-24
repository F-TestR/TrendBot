#!/usr/bin/env python3
"""
Roblox trend bot.

Every run: pulls the top games by live players from RoWatcher's official API,
remembers each game's daily high, and posts to Discord when something looks
like a trend starting. Once a day it posts a digest.

It also reads YouTube, Roblox's own public game data and Discord server sizes
and Twitch (see sources.py) and combines everything into a single "heat" score
per game. insights.py turns the history into a weekly opportunity report.

No AI involved, so it costs no tokens. Uses only the Python standard library.

Usage:
  python bot.py                 # one run (what GitHub Actions does)
  python bot.py --loop 20       # keep running every 20 minutes (for a PC)
  python bot.py --dry-run       # print messages instead of posting them
  python bot.py --test-webhooks # post a hello message to both channels
  python bot.py --digest-now    # force today's digest
  python bot.py --check-sources # test YouTube / Roblox / Twitch / Discord access and post the result
  python bot.py --weekly-now    # post the weekly opportunity report now
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import charts
import config as C
import present as PR
import promo as P
import badges as BD
import future as FUT
import engage as E
import hold as HOLD
import dashboard as DB
import discord_out as DO
import insights as I
import learn as L
import sources as S
import themes as T
import upstream as U
import warehouse as W

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.environ.get("STATE_PATH", os.path.join(HERE, "state", "state.json"))


# ------------------------------------------------------------------ setup ---

def load_dotenv():
    """Read KEY=VALUE lines from a local .env file (for running on a PC)."""
    path = os.path.join(HERE, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def now_utc():
    return datetime.now(timezone.utc)


def day_str(dt):
    return dt.strftime("%Y-%m-%d")


def parse_day(s):
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def is_weekend(day):
    return parse_day(day).weekday() >= 5


# ------------------------------------------------------------------ state ---

def empty_state():
    return {"games": {}, "alerts": {}, "requests": {}, "last_digest": None, "baseline_day": None}


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return empty_state()


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, separators=(",", ":"))
    os.replace(tmp, STATE_PATH)


# -------------------------------------------------------------------- api ---

class BudgetExceeded(Exception):
    pass


class RoWatcher:
    def __init__(self, api_key, state, today):
        self.key = api_key
        self.state = state
        self.today = today

    def _count(self):
        return self.state["requests"].get(self.today, 0)

    def get(self, path, params=None):
        if self._count() >= C.DAILY_REQUEST_CAP:
            raise BudgetExceeded(f"daily cap of {C.DAILY_REQUEST_CAP} requests reached")
        url = C.API_BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.key}",
            "Accept": "application/json",
            "User-Agent": "roblox-trend-bot/1.0",
        })
        self.state["requests"][self.today] = self._count() + 1
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise BudgetExceeded("RoWatcher rate limit hit (429)")
            raise


def pick(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return None


def normalise_game(g):
    gid = pick(g, "universeId", "id", "_id", "slug")
    created = pick(g, "robloxCreatedAt", "createdAt", "created")
    return {
        "id": str(gid),
        "name": str(pick(g, "name") or gid),
        "playing": int(pick(g, "playing") or 0),
        "created": str(created)[:10] if created else None,
    }


# ---------------------------------------------------------------- discord ---

def post_discord(url, text, dry_run=False, label="", files=None):
    DO.post_text(url, text, dry_run, label, files)


def link(gid, state=None):
    if state is not None:
        rl = S.roblox_link(state, gid)
        if rl:
            return rl
    return f"<https://rowatcher.com/games/{gid}>"


def fmt(n):
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)


# ---------------------------------------------------------------- signals ---

def baseline_high(days, ref_day):
    """Average daily high on the same kind of day (weekday vs weekend) 5-9 days before ref_day."""
    ref = parse_day(ref_day)
    vals = []
    for back in range(5, 10):
        d = day_str(ref - timedelta(days=back))
        if d in days and is_weekend(d) == is_weekend(ref_day):
            vals.append(days[d])
    return (sum(vals) / len(vals)) if vals else None


def age_days(game, today):
    if not game.get("created"):
        return None
    try:
        return (parse_day(today) - parse_day(game["created"])).days
    except ValueError:
        return None


def is_young(game, today):
    a = age_days(game, today)
    if a is not None:
        return a <= C.YOUNG_GAME_DAYS
    # unknown creation date: treat as young if we first saw it in the last 14 days
    return (parse_day(today) - parse_day(game["first_seen"])).days <= 14


def keywords(name):
    name = re.sub(r"\[.*?\]|\(.*?\)", " ", name.lower())
    words = re.findall(r"[a-z]{3,}", name)
    return {w for w in words if w not in C.STOPWORDS}


def growth(game, day, cutoff, baseline_day=None):
    """Ratio of day's high to the same-type baseline. If the game only entered the
    top list after the bot started (so it was below the cutoff a week ago), use the
    cutoff as a generous stand-in baseline. Games already in the list on the bot's
    first day just lack history, so they get no ratio until a week has passed."""
    high = game["days"].get(day)
    if not high:
        return None, None
    base = baseline_high(game["days"], day)
    if base is None:
        entered_later = baseline_day is not None and game["first_seen"] > baseline_day and not game.get("base")
        if entered_later and parse_day(game["first_seen"]) > parse_day(day) - timedelta(days=5):
            base = cutoff  # it was below the top list last week
        else:
            return None, None
    if not base:
        return None, None
    return high / base, base


def is_base(state, r):
    """True for games that were already there when the bot (or deep scanning) started."""
    return bool(r.get("base")) or r["first_seen"] == state.get("baseline_day")


def cooled(state, key, today, days=C.ALERT_COOLDOWN_DAYS):
    last = state["alerts"].get(key)
    return last is None or (parse_day(today) - parse_day(last)).days >= days


# -------------------------------------------------------------------- run ---

def run_once(dry_run=False, force_digest=False, force_weekly=False):
    load_dotenv()
    api_key = os.environ.get("ROWATCHER_API_KEY")
    alerts_url = os.environ.get("DISCORD_ALERTS_WEBHOOK")
    digest_url = os.environ.get("DISCORD_DIGEST_WEBHOOK")
    if not api_key:
        sys.exit("ROWATCHER_API_KEY is not set. See SETUP.md.")

    state = load_state()
    t = now_utc()
    today = day_str(t)
    api = RoWatcher(api_key, state, today)

    restored = W.restore_if_missing()
    if restored:
        print(restored)
    db = W.connect()
    T.ensure(db)
    HOLD.ensure(db)
    E.ensure(db)
    BD.ensure(db)
    P.ensure(db)

    def paced():
        """Optional calls only while we're under the day's pro-rata budget."""
        mins = t.hour * 60 + t.minute + 20
        return state["requests"].get(today, 0) < C.DAILY_REQUEST_CAP * min(1.0, mins / 1440)

    # 1. Pull the game lists: top 300 every run, deeper pages in rotation, very deep once a day
    pages = list(range(1, C.CORE_PAGES + 1))
    deep = list(range(C.CORE_PAGES + 1, C.DEEP_LAST_PAGE + 1))
    ptr = state.get("deep_ptr", 0) % max(len(deep), 1)
    rotation = [deep[(ptr + i) % len(deep)] for i in range(min(C.DEEP_PAGES_PER_RUN, len(deep)))]
    first_run = not state["games"]
    upgrading = "deep_ptr" not in state
    if first_run or upgrading:
        rotation = deep  # build the full picture on the very first (deep) run
    discovery = []
    if state.get("last_discovery") != today and t.hour >= 2 and not first_run:
        discovery = list(range(C.DISCOVERY_FIRST_PAGE, C.DISCOVERY_LAST_PAGE + 1))

    top, raw_seen = [], 0
    fetched_deepest = None
    def fetch(page):
        nonlocal raw_seen, fetched_deepest
        resp = api.get("/games", {"sort": "playing", "page": page, "pageSize": C.PAGE_SIZE})
        data = resp.get("data") or []
        for g in data:
            ng = normalise_game(g)
            ng["raw"] = g
            top.append(ng)
        raw_seen += len(data)
        if page == C.DEEP_LAST_PAGE and data:
            fetched_deepest = min(normalise_game(g)["playing"] for g in data)
        return len(data)
    try:
        for page in pages:
            if fetch(page) < C.PAGE_SIZE:
                break
        done = 0
        for page in rotation:
            if not (first_run or upgrading) and not paced():
                break
            fetch(page)
            done += 1
        state["deep_ptr"] = ptr + done
        if discovery and paced():
            for page in discovery:
                if fetch(page) < C.PAGE_SIZE:
                    break
            state["last_discovery"] = today
    except BudgetExceeded as e:
        print(f"Stopping fetch: {e}")
    if not top:
        print("No games fetched this run.")
        save_state(state)
        db.commit()
        return

    if first_run:
        state["baseline_day"] = today
    if fetched_deepest:
        state["cutoff"] = fetched_deepest
    cutoff = state.get("cutoff") or min(g["playing"] for g in top)

    games = state["games"]
    new_ids, crossed = [], []
    for g in top:
        rec = games.get(g["id"])
        is_new = rec is None
        if is_new:
            rec = games[g["id"]] = {"name": g["name"], "first_seen": today,
                                    "created": g["created"], "days": {}}
            if first_run or upgrading:
                # already there when the bot started (or first deep run): not "new",
                # so it can't trigger new-game, copy-wave or riser alerts
                rec["base"] = True
            else:
                new_ids.append(g["id"])
        prev_max = max(rec["days"].values() or [0])
        if not is_new and rec.get("name") and rec["name"] != g["name"]:
            try:
                T.record_rename(db, g["id"], today, rec["name"], g["name"])
            except Exception as e:
                print(f"rename log failed: {e}", file=sys.stderr)
        rec["name"] = g["name"]
        rec["last"] = g["playing"]
        rec["last_seen"] = today
        if g["created"]:
            rec["created"] = g["created"]
        if g["raw"].get("creatorId"):
            rec["creator"] = str(g["raw"].get("creatorId"))
        rec["days"][today] = max(rec["days"].get(today, 0), g["playing"])
        if g["playing"] >= C.MIN_PLAYERS_NEW_ENTRY and not rec.get("crossed"):
            rec["crossed"] = today
            if not first_run and (prev_max < C.MIN_PLAYERS_NEW_ENTRY):
                crossed.append(g["id"])
        try:
            W.record_snapshot(db, g["raw"], t, ", ".join(I.mechanics_of(g["name"])))
            E.record_description(db, g["id"], g["raw"].get("description"))
        except Exception as e:
            print(f"db write failed for {g['id']}: {e}", file=sys.stderr)

    # 2. Look up creation dates for promising games that lack one (rare: the list usually has it)
    lookups = 0
    for gid in sorted(set(new_ids) | set(crossed), key=lambda i: -games[i]["last"]):
        rec = games[gid]
        if rec.get("created") or rec.get("detail_checked") or rec["last"] < C.MIN_PLAYERS_NEW_ENTRY:
            continue
        if lookups >= C.MAX_DETAIL_LOOKUPS_PER_RUN:
            break
        try:
            d = api.get(f"/games/{urllib.parse.quote(gid)}")
            info = normalise_game((d or {}).get("data") or {})
            if info["created"]:
                rec["created"] = info["created"]
        except BudgetExceeded:
            break
        except Exception as e:
            print(f"detail lookup failed for {gid}: {e}")
        rec["detail_checked"] = True
        lookups += 1

    # 2b. Roblox's algorithm charts (hourly)
    charted_now = []
    if (not state.get("charts_at") or (t - datetime.fromisoformat(state["charts_at"])) >= timedelta(minutes=C.CHARTS_EVERY_MIN - 2)) \
            and (first_run or paced()):
        try:
            ch = (api.get("/charts") or {}).get("data") or []
            W.record_chart(db, ch, t)
            prev = set(state.get("charted", []))
            now_ids = [str(g.get("universeId")) for g in ch if g.get("universeId")]
            charted_now = [u for u in now_ids if u not in prev] if prev else []
            state["charted"] = sorted(set(now_ids) | {u for u in prev if games.get(u, {}).get("last_seen") == today})[-300:]
            state["chart_rank"] = {u: i + 1 for i, u in enumerate(now_ids)}
            state["charts_at"] = t.isoformat()
        except BudgetExceeded:
            pass
        except Exception as e:
            print(f"charts failed: {e}", file=sys.stderr)

    # 2b1. Roblox-wide player counts (for the weekday-hold comparison), every 6 hours
    if (not state.get("platform_at") or (t - datetime.fromisoformat(state["platform_at"])) >= timedelta(hours=C.PLATFORM_EVERY_HOURS - 0.1)) \
            and (first_run or paced()):
        try:
            HOLD.record_platform(state, (api.get("/platform/ccu", {"range": "24h"}) or {}).get("data"))
            state["platform_at"] = t.isoformat()
        except BudgetExceeded:
            pass
        except Exception as e:
            print(f"platform ccu failed: {e}", file=sys.stderr)

    # 2b2. RoWatcher's curated trend list (weekly, 1 request) - extra ready-made themes
    if (not state.get("rw_trends_at") or (t - datetime.fromisoformat(state["rw_trends_at"])).days >= C.RW_TRENDS_EVERY_DAYS) \
            and paced():
        try:
            tr = (api.get("/trends", {"limit": 500}) or {}).get("data") or []
            state["rw_trends"] = [(str(x.get("id")), x.get("name") or str(x.get("id")),
                                   [re.sub(r"[^a-z0-9]+", " ", k.lower()).strip() for k in (x.get("keywords") or []) if k])
                                  for x in tr if x.get("id")]
            state["rw_trends_at"] = t.isoformat()
        except BudgetExceeded:
            pass
        except Exception as e:
            print(f"trends failed: {e}", file=sys.stderr)

    # 2b3. Outside-Roblox signals (Steam, Wikipedia daily; YouTube trending, Twitch top every 6h)
    def yt_units(n):
        u = S.src_state(state)["yt_units"]
        if u.get(today, 0) + n > C.YT_DAILY_UNIT_CAP:
            raise RuntimeError("YouTube daily quota cap reached")
        u[today] = u.get(today, 0) + n
    try:
        up_ran = U.collect_all(db, state, t, os.environ, yt_units)
        if up_ran:
            print("outside sources: " + ", ".join(up_ran))
    except Exception as e:
        print(f"outside sources failed: {e}", file=sys.stderr)

    # 2b4. Forward calendar: Steam coming soon, upcoming/trending films and shows, your dates (daily)
    try:
        fr = FUT.collect_all(db, state, t, os.environ)
        if fr:
            print("forward calendar: " + ", ".join(fr))
    except Exception as e:
        print(f"forward calendar failed: {e}", file=sys.stderr)

    # 2b5. Roblox badges: players per day, playtime per player, returning share, funnels (~10 games a run)
    if not first_run:
        try:
            state["_young_ids"] = {gid for gid, r in games.items() if is_young(r, today)}
            nb = BD.collect(db, state, t)
            state.pop("_young_ids", None)
            if nb:
                print(f"badges: {nb} games read")
        except Exception as e:
            state.pop("_young_ids", None)
            print(f"badges failed: {e}", file=sys.stderr)

    # 2c. Backfill past history for young games (teaches the model faster)
    if not first_run:
        since = day_str(t - timedelta(days=C.BACKFILL_MAX_AGE_DAYS))
        # alternate: one game that exploded, one that didn't, so the model sees both kinds
        want_hit = (state.get("bf_flip", 0) % 2 == 0)
        state["bf_flip"] = state.get("bf_flip", 0) + 1
        cands = db.execute("""SELECT g.uid, g.created, MAX(d.peak) AS pk FROM games g JOIN daily d ON d.uid=g.uid
                              WHERE g.created >= ? AND g.uid NOT IN (SELECT uid FROM backfill)
                              GROUP BY g.uid ORDER BY ((MAX(d.peak) >= ?) = ?) DESC, RANDOM() LIMIT ?""",
                           (since, C.EXPLODE_CCU, 1 if want_hit else 0, C.BACKFILL_PER_RUN)).fetchall()
        for c in cands:
            if not paced():
                break
            try:
                frm = max(c["created"], since) + "T00:00:00Z"
                h = api.get(f"/games/{c['uid']}/history", {"from": frm})
                n = W.record_history(db, c["uid"], (h or {}).get("data") or [], c["created"])
                db.execute("INSERT OR REPLACE INTO backfill(uid, ts, points, status) VALUES(?,?,?,?)",
                           (c["uid"], t.isoformat(), n, "ok"))
            except BudgetExceeded:
                break
            except Exception as e:
                print(f"backfill failed for {c['uid']}: {e}", file=sys.stderr)
                db.execute("INSERT OR REPLACE INTO backfill(uid, ts, points, status) VALUES(?,?,?,?)",
                           (c["uid"], t.isoformat(), 0, "error"))
        # older games: about 8 weeks of history each, so long-term ratings start straight away
        olds = db.execute("""SELECT g.uid, g.created, MAX(d.peak) AS pk FROM games g JOIN daily d ON d.uid=g.uid
                             WHERE (g.created IS NULL OR g.created < ?) AND g.uid NOT IN (SELECT uid FROM backfill)
                             GROUP BY g.uid HAVING MAX(d.peak) >= ? ORDER BY MAX(d.peak) DESC LIMIT ?""",
                          (since, C.BACKFILL_ESTABLISHED_MIN_PLAYERS, C.BACKFILL_ESTABLISHED_PER_RUN)).fetchall()
        for c in olds:
            if not paced():
                break
            try:
                frm = day_str(t - timedelta(days=7 * C.HOLD_HISTORY_WEEKS + 7)) + "T00:00:00Z"
                h = api.get(f"/games/{c['uid']}/history", {"from": frm})
                n = W.record_history(db, c["uid"], (h or {}).get("data") or [], c["created"] or "2000-01-01")
                db.execute("INSERT OR REPLACE INTO backfill(uid, ts, points, status) VALUES(?,?,?,?)",
                           (c["uid"], t.isoformat(), n, "ok-old"))
            except BudgetExceeded:
                break
            except Exception as e:
                print(f"backfill failed for {c['uid']}: {e}", file=sys.stderr)
                db.execute("INSERT OR REPLACE INTO backfill(uid, ts, points, status) VALUES(?,?,?,?)",
                           (c["uid"], t.isoformat(), 0, "error"))
    db.commit()

    alerts = []  # each: {kind, gid, title, desc, url, fields, ping, text}

    def add(kind, gid, title, desc, fields=(), ping=False, extra_text=""):
        url = link(gid, state).strip("<>") if gid else None
        alerts.append({"kind": kind, "gid": gid, "title": title, "desc": desc, "url": url,
                       "fields": list(fields), "ping": ping,
                       "text": f"**{title}** — {desc}{extra_text}" + (f" {link(gid, state)}" if gid else "")})

    # 3a. Young games crossing 2K players for the first time
    for gid in crossed:
        rec = games[gid]
        if is_young(rec, today) and cooled(state, "new:" + gid, today, 9999):
            a = age_days(rec, today)
            add("new", gid, f"🆕 Just crossed {fmt(C.MIN_PLAYERS_NEW_ENTRY)} players: {rec['name'][:80]}",
                f"{fmt(rec['last'])} playing right now.",
                [("Players", fmt(rec["last"])), ("Age", f"{a} days" if a is not None else "unknown"),
                 ("Type", ", ".join(I.mechanics_of(rec["name"])) or "—")] + studio_field(db, gid))
            state["alerts"]["new:" + gid] = today

    # 3a2. Young games that just appeared in Roblox's algorithm charts
    for gid in charted_now:
        rec = games.get(gid)
        if rec and is_young(rec, today) and rec.get("last", 0) < C.EARLY_WARNING_MAX_PLAYERS * 4 and cooled(state, "chart:" + gid, today, 14):
            add("chart", gid, f"📈 Entered Roblox's algorithm charts: {rec['name'][:70]}",
                f"Now #{state['chart_rank'].get(gid)} in the charts with {fmt(rec['last'])} playing — Roblox is pushing it.",
                [("Players", fmt(rec["last"])), ("Age", f"{age_days(rec, today)} days" if age_days(rec, today) is not None else "unknown")]
                + studio_field(db, gid))
            state["alerts"]["chart:" + gid] = today

    # 3b. Weekday-to-weekday surges in young games
    for gid, rec in games.items():
        if rec.get("last_seen") != today or not is_young(rec, today):
            continue
        ratio, base = growth(rec, today, cutoff, state.get("baseline_day"))
        high = rec["days"].get(today, 0)
        if ratio and ratio >= C.SURGE_MULTIPLIER and high >= C.SURGE_MIN_PLAYERS and cooled(state, "surge:" + gid, today):
            kind = "weekend" if is_weekend(today) else "weekday"
            a = age_days(rec, today)
            add("surge", gid, f"🚀 Surging: {rec['name'][:80]}",
                f"Today's high **{fmt(high)}** vs {fmt(base)} on {kind}s last week (**{ratio:.1f}×**).",
                [("Today's high", fmt(high)), ("Growth", f"{ratio:.1f}×"), ("Age", f"{a} days" if a is not None else "unknown")],
                ping=ratio >= C.PING_SURGE_MULTIPLIER)
            state["alerts"]["surge:" + gid] = today

    # 3c. Copy waves: 3+ games new to the list in 7 days sharing a title word
    week_ago = parse_day(today) - timedelta(days=7)
    recent = [(gid, r) for gid, r in games.items()
              if not is_base(state, r) and parse_day(r["first_seen"]) >= week_ago
              and max(r["days"].values() or [0]) >= C.COPY_WAVE_MIN_PLAYERS]
    by_kw = {}
    for gid, r in recent:
        for kw in keywords(r["name"]):
            by_kw.setdefault(kw, []).append((gid, r))
    seen_sets = set()
    for kw, items in sorted(by_kw.items(), key=lambda kv: -len(kv[1])):
        ids = frozenset(gid for gid, _ in items)
        if ids in seen_sets:
            continue  # same games as another keyword (e.g. "eat" + "everything")
        seen_sets.add(ids)
        if len(items) >= C.COPY_WAVE_MIN_GAMES and cooled(state, "copy:" + kw, today, 7):
            ranked = sorted(items, key=lambda x: -x[1]["last"])
            names = "\n".join(f"• {r['name'][:45]} — {fmt(r['last'])}" for _, r in ranked[:6])
            lead = ranked[0][0]
            add("copy", lead, f"🧬 Copy wave forming: \"{kw}\"",
                f"{len(items)} new games this week share this word:\n{names}",
                ping=len(items) >= C.PING_COPY_WAVE_GAMES)
            alerts[-1]["url"] = None
            state["alerts"]["copy:" + kw] = today

    # 3d. Extra sources (YouTube / Roblox / Twitch / community) and cross-platform heat
    ran = S.collect_all(state, t, os.environ)
    if ran:
        print("sources checked: " + ", ".join(ran))
    yts = S.yt_stats(state, t)
    for gid in set(S.candidate_games(state, today, 400)) | set(yts):
        rec = games.get(gid)
        if rec is not None and not is_young(rec, today) and gid not in C.WATCHLIST:
            continue
        h = S.heat(state, gid, today, cutoff, yts)
        if (h and len(h["signals"]) >= 2 and h["score"] >= C.HEAT_ALERT_SCORE
                and cooled(state, "heat:" + gid, today)):
            add("heat", gid, f"🔥 Heating up on {len(h['signals'])} platforms: {S.game_name(state, gid)[:70]}",
                f"Rising on **{', '.join(h['signals'])}** · heat score **{h['score']}**/100",
                heat_fields(state, gid, h) + studio_field(db, gid),
                ping=h["score"] >= C.PING_HEAT_SCORE and len(h["signals"]) >= 3,
                extra_text=" · " + S.heat_line(state, gid, h).split(" — ", 1)[-1].rsplit(" <", 1)[0])
            state["alerts"]["heat:" + gid] = today
    for gid, y in yts.items():
        name = S.game_name(state, gid)
        players = S.players_now(state, gid)
        if name == gid or players >= C.EARLY_WARNING_MAX_PLAYERS:
            continue
        if (y["n"] >= C.EARLY_WARNING_VIDEOS or y["views"] >= C.EARLY_WARNING_VIEWS or y.get("big", 0) >= 1) \
                and cooled(state, "early:" + gid, today, 7):
            views, title, vid = y["top"]
            add("early", gid, f"👀 Early warning: {name[:80]}",
                f"Hot on YouTube while still small on Roblox.\nTop video: [{title[:80]}](https://youtu.be/{vid}) ({fmt(views)} views)",
                [("Playing now", fmt(players)), ("YouTube 48h", f"{y['n']} videos"), ("Views 48h", fmt(y["views"]))]
                + ([("Big creators", f"{y['big']} video{'s' if y['big'] != 1 else ''} from 1M+ sub channels")] if y.get("big") else [])
                + studio_field(db, gid),
                ping=y["views"] >= C.PING_EARLY_VIEWS or y.get("big", 0) >= 2,
                extra_text=f" · top video <https://youtu.be/{vid}>")
            state["alerts"]["early:" + gid] = today

    # 3e. Insights: updates and breakouts
    for ev in I.track_updates(state, today):
        if ev["gid"] in C.WATCHLIST:
            add("update", ev["gid"], f"🛠️ Watchlist game updated: {ev['name']}",
                f"Published an update on {ev['date']}. Players before: "
                f"{fmt(ev['before']) if ev.get('before') else 'unknown'}. Results show in the digest after 1, 3 and 7 days.")
    already = {a["gid"] for a in alerts}
    for gid in I.track_lifecycle(state, today):
        if gid in already:
            continue
        r = I.ins_state(state)["life"][gid]
        add("breakout", gid, f"💥 Breakout: {r['name']}",
            f"A young game just crossed **{fmt(C.BREAKOUT_PLAYERS)}** players. Now logged in lifecycle tracking.",
            [("Players", fmt(r["peak"])), ("Age", f"{r['age']} days" if r.get("age") is not None else "unknown"),
             ("Type", ", ".join(r["mech"]) or "—")])

    # 3f. Learning: once a day (with the digest) retrain and score today's young games
    digest_due = force_digest or (state.get("last_digest") != today and t.hour >= C.DIGEST_HOUR_UTC and not first_run)
    preds = []
    if digest_due or force_weekly:
        try:
            status = L.train(db, today)
            print(f"model: {status.get('examples')} examples, {status.get('positives')} explosions, trained={status.get('trained')}")
            preds = L.predictions(db, today)
            db.commit()
        except Exception as e:
            print(f"learning failed: {e}", file=sys.stderr)
        state["_preds"] = {e["uid"]: p for p, e in preds}

        # Themes: rebuild yesterday's theme numbers, retrain, score small themes, spot bridges
        tpreds, brs = [], []
        try:
            yday_s = day_str(t - timedelta(days=1))
            T.record_roblox_youtube_words(db, state, yday_s)
            n = T.update(db, state, today)
            tst = T.train(db, today)
            print(f"themes: {n} rows, model {tst.get('examples')} examples / {tst.get('positives')} breakouts, trained={tst.get('trained')}")
            tpreds = T.predict(db, today)
            brs = T.bridges(db, state, today)
            db.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"themes failed: {e}", file=sys.stderr)
        state["_themes"] = [(p, sc, k, dict(r), f) for p, sc, k, r, f in tpreds[:40]]
        state["_bridges"] = [(w, srcs, row) for w, srcs, row in brs]
        rw = state.get("rw_trends", [])
        for p, sc, k, r, fired in tpreds[:30]:
            trusted = (tst.get("test_auc") or 0) >= C.MODEL_TRUST_AUC if isinstance(tst, dict) else False
            if not trusted:
                p = None  # the model hasn't proven itself on unseen data yet: use the simple signal rule
            strong = (p is not None and p >= C.THEME_ALERT_PROB) or (p is None and sc >= 3 and r["new7"] >= 3)
            if not strong or r["hits"] > C.THEME_ALERT_MAX_HITS or not cooled(state, "theme:" + k, today, 14):
                continue
            tops = T.top_games(db, k, rw, day_str(t - timedelta(days=1)))
            lead = tops[0][2] if tops else None
            labels = ", ".join(T.INDICATORS[i][0] for i in fired) or "—"
            add("theme", lead, f"🌱 Emerging theme: \"{T.display(k, state)}\"",
                (f"Model: **{p*100:.0f}%** chance that {C.THEME_BREAKOUT_GAMES}+ games of this theme pass "
                 f"{fmt(C.THEME_HIT_CCU)} players within {C.LABEL_DAYS} days." if p is not None else
                 "Several early indicators are firing at once (the theme model is still learning).")
                + "\n" + "\n".join(f"• {nm[:45]} — {fmt(pk)}" for pk, nm, _ in tops),
                [("Games", str(r["games"])), ("New this week", f"{r['new7']} (from {r['studios7']} studios)"),
                 ("With 2K+ players", str(r["hits"])), ("Signals", labels)],
                ping=p is not None and p >= 0.6)
            alerts[-1]["url"] = None
            state["alerts"]["theme:" + k] = today
        for w, srcs, row in brs:
            if not cooled(state, "bridge:" + w, today, 30):
                continue
            where = "; ".join(sorted({d for _, d in srcs if d}))[:300]
            tops = T.top_games(db, ("b:" if " " in w else "w:") + w, rw, day_str(t - timedelta(days=1)))
            add("bridge", tops[0][2] if tops else None, f"🌉 Outside trend reaching Roblox: \"{w}\"",
                f"Rising outside Roblox ({where}) and now in {row['new7']} brand-new Roblox game"
                f"{'s' if row['new7'] != 1 else ''} this week.\n"
                + "\n".join(f"• {nm[:45]} — {fmt(pk)}" for pk, nm, _ in tops),
                [("New Roblox games", str(row["new7"])), ("Total players", fmt(row["ccu"]))], ping=row["new7"] >= 3)
            alerts[-1]["url"] = None
            state["alerts"]["bridge:" + w] = today
        try:
            for x in FUT.alerts_for(db, state, today):
                key = "future:" + x["name"].lower()[:60]
                if not cooled(state, key, today, 21):
                    continue
                rb = x["roblox"]
                tops = T.top_games(db, ("b:" if " " in rb["word"] else "w:") + rb["word"], rw, day_str(t - timedelta(days=1)))
                when = ("out now" if x["days"] is not None and x["days"] <= 0 else
                        f"in {x['days']} days" if x["days"] is not None else "date tbc")
                add("future", tops[0][2] if tops else None, f"🔮 First Roblox copies of something coming: {x['name'][:60]}",
                    f"{x['detail']} ({when}) — and {rb['new7']} brand-new Roblox game{'s' if rb['new7'] != 1 else ''} "
                    f"already use \"{rb['word']}\". The wave may be starting; early movers win.\n"
                    + "\n".join(f"• {nm[:45]} — {fmt(pk)}" for pk, nm, _ in tops),
                    [("New Roblox games", str(rb["new7"])), ("Release", x["date"] or "tbc")], ping=rb["new7"] >= 3)
                alerts[-1]["url"] = None
                state["alerts"][key] = today
        except Exception as e:
            print(f"future alerts failed: {e}", file=sys.stderr)
        for p, e in preds:
            gid = e["uid"]
            if p >= C.PREDICT_ALERT_PROB and S.players_now(state, gid) < C.PREDICT_ALERT_MAX_PLAYERS \
                    and cooled(state, "predict:" + gid, today, 14):
                add("predict", gid, f"🎯 Model predicts a breakout: {e['name'][:70]}",
                    f"**{p*100:.0f}%** chance of reaching {fmt(C.EXPLODE_CCU)}+ players within {C.LABEL_DAYS} days of being noticed "
                    f"(noticed {e['t0'][5:]}).",
                    [("Playing now", fmt(S.players_now(state, gid))), ("Type", ", ".join(I.mechanics_of(e["name"])) or "—")]
                    + studio_field(db, gid), ping=p >= 0.7)
                state["alerts"]["predict:" + gid] = today

    # 3g. Weekday hold + long-term games (once a day, with the digest)
    if digest_due or force_weekly:
        try:
            before = dict(state.get("longterm") or {})
            m = HOLD.update(db, state, today)
            db.commit()
            ne = E.update(db, state, today)
            db.commit()
            print(f"stickiness: {ne} games scored")
            try:
                pst = P.train(db, today)
                print("algorithm mirror: " + ", ".join(
                    f"{k} {(pst.get(k) or {}).get('examples')} ex / {(pst.get(k) or {}).get('positives')} promoted, "
                    f"trained={(pst.get(k) or {}).get('trained')}" for k in P.TARGETS))
                ids = [g for g, r in games.items() if r.get("last_seen") == today and r.get("last", 0) >= C.PROMO_MIN_PLAYERS]
                state["_promo"] = P.score(db, today, ids)
                db.commit()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"algorithm mirror failed: {e}", file=sys.stderr)
            lt = state.get("longterm") or {}
            print(f"weekday hold: typical {m.get('benchmark')}, Roblox {m.get('roblox')}, {len(state.get('hold', {}))} rated, "
                  f"{sum(1 for v in lt.values() if v['status'] == 'long-term')} long-term games")
            if before:  # not on the very first rating, or every long-term game would alert at once
                for gid in HOLD.newly_longterm(state, before):
                    rec = games.get(gid)
                    if rec and is_young(rec, today) and cooled(state, "longterm:" + gid, today, 60):
                        v = lt[gid]
                        add("longterm", gid, f"🏛️ New long-term game: {rec['name'][:70]}",
                            f"Kept its weekend crowd better than a typical game in {v['good']} of {v['weeks']} weeks "
                            f"(median **{v['med']:.2f}×**). Young games that do this tend to last.",
                            [("Weekend players", fmt(v["players"])), ("Age", f"{age_days(rec, today)} days" if age_days(rec, today) is not None else "unknown")]
                            + studio_field(db, gid))
                        state["alerts"]["longterm:" + gid] = today
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"weekday hold failed: {e}", file=sys.stderr)

    for a in alerts:
        if a.get("gid") and a["kind"] not in ("theme", "bridge", "future"):
            try:
                W.record_alert(db, t, a["gid"], a["kind"], S.players_now(state, a["gid"]))
            except Exception as e:
                print(f"couldn't log alert: {e}", file=sys.stderr)
    db.commit()

    if alerts:
        header = f"**Trend alert** · {t.strftime('%a %d %b %H:%M')} UTC"
        icons = S.game_icons([a["gid"] for a in alerts if a.get("gid")]) if (C.RICH_CARDS and not dry_run) else {}
        DO.post_alerts(alerts_url, alerts, header, icons, dry_run)

    # 4. Daily digest (+ charts and dashboard), weekly report on the chosen day
    if digest_due:
        try:
            W.record_sources_day(db, day_str(t - timedelta(days=1)), sources_day(state, day_str(t - timedelta(days=1))))
            W.prune(db, today)
            db.commit()
        except Exception as e:
            print(f"daily source write failed: {e}", file=sys.stderr)
        state["_dbstats"] = W.stats(db)
        cards = None
        if C.DIGEST_STYLE == "cards":
            try:
                cards = PR.digest_cards(db, state, today, cutoff, t, present_ctx())
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"digest cards failed, sending text instead: {e}", file=sys.stderr)
        files = digest_files(state, today, cutoff)
        state.pop("_head", None)
        state.pop("_board", None)
        posted = False
        if cards:
            PR.post_cards(digest_url, cards, files=files, dry_run=dry_run, label="digest")
            posted = True
        if not posted:
            post_discord(digest_url, build_digest(state, today, cutoff, t), dry_run, "digest", files)
        state["last_digest"] = today
        try:
            state["backup"] = W.backup(db)
        except Exception as e:
            state["backup"] = f"failed: {e}"
        print("backup: " + state["backup"])
    if force_weekly or (state.get("last_weekly") != today and t.weekday() == C.WEEKLY_REPORT_WEEKDAY
                        and t.hour >= C.DIGEST_HOUR_UTC and not first_run):
        text, table = I.weekly_report(state, today)
        files = []
        text += "\n\n" + "\n".join(L.report_lines(db, today, fmt))
        try:
            state["_young_ids"] = {gid for gid, r in games.items() if is_young(r, today)}
            text += "\n\n" + "\n".join(HOLD.report_lines(db, state, fmt, lambda u: S.game_name(state, u), lambda u: link(u, state)))
            state.pop("_young_ids", None)
        except Exception as e:
            print(f"long-term report failed: {e}", file=sys.stderr)
        try:
            state["_young_ids"] = {gid for gid, r in games.items() if is_young(r, today)}
            el, om = E.report_lines(db, state, today, fmt, lambda u: S.game_name(state, u), lambda u: link(u, state))
            el += [""] + BD.report_lines(db, state, fmt, lambda u: S.game_name(state, u), lambda u: link(u, state))
            el += [""] + P.report_lines(db, today)
            state.pop("_young_ids", None)
            text += "\n\n" + "\n".join(el)
            png = E.map_chart(om) if C.DIGEST_CHARTS else None
            if png:
                files.append(("opportunity_map.png", png, "image/png"))
        except Exception as e:
            print(f"stickiness report failed: {e}", file=sys.stderr)
        try:
            text += "\n\n" + "\n".join(T.report_lines(db, today, fmt))
        except Exception as e:
            print(f"theme report failed: {e}", file=sys.stderr)
        rows = [r for r in table if r["chg"] is not None]
        if C.DIGEST_CHARTS and rows:
            png = charts.bar_chart([r["mech"] for r in rows], [r["chg"] for r in rows],
                                   "Demand change by mechanic (this week vs last)")
            if png:
                files.append(("mechanics.png", png, "image/png"))
        posted = False
        if C.DIGEST_STYLE == "cards":
            try:
                cards = PR.weekly_cards(db, state, today, present_ctx(), table)
                full = ("# Weekly report — full version\n\n" + text).encode("utf-8")
                PR.post_cards(digest_url, cards, files=files + [("weekly_report.md", full, "text/markdown")],
                              dry_run=dry_run, label="weekly")
                posted = True
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"weekly cards failed, sending text instead: {e}", file=sys.stderr)
        if not posted:
            post_discord(digest_url, text, dry_run, "weekly", files)
        state["last_weekly"] = today

    db.commit()
    db.close()
    state.pop("_preds", None)
    state.pop("_promo", None)
    state.pop("_themes", None)
    state.pop("_bridges", None)
    state.pop("_dbstats", None)

    # 5. Tidy up
    keep_from = parse_day(today) - timedelta(days=C.KEEP_DAYS)
    for gid in list(games):
        r = games[gid]
        r["days"] = {d: v for d, v in r["days"].items() if parse_day(d) >= keep_from}
        if parse_day(r.get("last_seen", r["first_seen"])) < keep_from:
            del games[gid]
    state["requests"] = {d: n for d, n in state["requests"].items() if parse_day(d) >= keep_from}
    state["alerts"] = {k: d for k, d in state["alerts"].items()
                       if k.startswith("new:") or parse_day(d) >= keep_from}
    save_state(state)
    print(f"{today}: {len(top)} games, {len(new_ids)} new, {len(alerts)} alerts, "
          f"{state['requests'].get(today, 0)} API requests today")


def studio_field(db, gid):
    try:
        g = db.execute("SELECT creator_id, creator_name FROM games WHERE uid=?", (gid,)).fetchone()
        if not g or not g["creator_id"]:
            return []
        best = W.creator_best(db, g["creator_id"], gid)
        name = (g["creator_name"] or "unknown")[:40]
        if best >= C.HIT_PLAYERS:
            return [("Studio", f"🏆 {name} · their best other game peaked at {fmt(best)}")]
        return [("Studio", name)]
    except Exception:
        return []


def sources_day(state, day):
    """Per-game YouTube / Twitch / community numbers for a finished day (for the database)."""
    src = S.src_state(state)
    rows = {}
    for vid, r in src["videos"].items():
        if (r.get("p") or "")[:10] != day:
            continue
        big = 1 if (src.get("channels", {}).get(r.get("ch") or "", 0) or 0) >= C.YT_BIG_CHANNEL_SUBS else 0
        for u in r.get("u", []):
            x = rows.setdefault(u, {"yt_n": 0, "yt_views": 0, "yt_big": 0})
            x["yt_n"] += 1
            x["yt_views"] += r.get("v", 0)
            x["yt_big"] += big
    for u, days in src["tw"].items():
        if day in days:
            rows.setdefault(u, {})["tw_v"] = days[day]["v"]
    for u, r in src["rbx"].items():
        g = r.get("group")
        if g and day in (src["grp"].get(str(g)) or {}):
            rows.setdefault(u, {})["grp"] = src["grp"][str(g)][day]
        if r.get("updated"):
            rows.setdefault(u, {})["updated"] = r["updated"]
    for u, days in src["dc"].items():
        if day in days:
            rows.setdefault(u, {})["dc"] = days[day]
    return rows


def heat_fields(state, gid, h):
    p = h["parts"]
    f = [("Playing", fmt(S.players_now(state, gid)))]
    if "players" in p:
        f.append(("Players vs last week", f"{p['players']:.1f}×"))
    if "yt" in p:
        f.append(("YouTube 48h", f"{p['yt']['n']} videos · {fmt(p['yt']['views'])} views"
                  + (f" · {p['yt']['big']} from 1M+ channels" if p['yt'].get('big') else "")))
    if "twitch" in p:
        tv, tr, ts = p["twitch"]
        f.append(("Twitch", f"{fmt(tv)} viewers" + (f" ({tr:.1f}×)" if tr else "")))
    for key, label in (("group", "Roblox group"), ("discord", "Discord")):
        if key in p:
            m, pct = p[key]
            f.append((label, fmt(m) + (f" ({pct:+.0f}%)" if pct is not None else "")))
    if "hold" in p:
        f.append(("Weekday hold", f"{p['hold']:.2f}× typical"))
    if "playtime" in p:
        b = (state.get("badges") or {}).get(gid) or {}
        f.append(("Playtime", f"~{p['playtime']:.0f} min/player/day · {fmt(b['dau'])} players/day" if b.get("dau") else f"~{p['playtime']:.0f} min/player/day"))
    if "likes" in p:
        f.append(("Likes", f"{p['likes']*100:.0f}%"))
    return f


def digest_files(state, today, cutoff):
    files = []
    games = state["games"]
    yday = day_str(parse_day(today) - timedelta(days=1))
    if C.DIGEST_CHARTS:
        try:
            risers = []
            for gid, r in games.items():
                if is_young(r, today):
                    ratio, _ = growth(r, yday, cutoff, state.get("baseline_day"))
                    if ratio and ratio >= 1.5 and r["days"].get(yday, 0) >= 1000:
                        risers.append((ratio * min(r["days"][yday], 50000), r))
            risers.sort(key=lambda x: -x[0])
            if risers:
                png = charts.line_chart([(r["name"], r["days"]) for _, r in risers[:6]], "Top risers — daily peak players")
                if png:
                    files.append(("risers.png", png, "image/png"))
            watch = [(label, games[gid]["days"]) for gid, label in C.WATCHLIST.items() if gid in games]
            if watch:
                png = charts.line_chart(watch, "Watchlist — daily peak players")
                if png:
                    files.append(("watchlist.png", png, "image/png"))
        except Exception as e:
            print(f"charts failed: {e}", file=sys.stderr)
    if C.DASHBOARD:
        try:
            files.append(("dashboard.html", DB.build(state, today, cutoff).encode("utf-8"), "text/html"))
        except Exception as e:
            print(f"dashboard failed: {e}", file=sys.stderr)
    return files


def build_digest(state, today, cutoff, t=None):
    t = t or now_utc()
    games = state["games"]
    yday = day_str(parse_day(today) - timedelta(days=1))
    lines = [f"**Daily trend digest** · {parse_day(today).strftime('%a %d %b %Y')}",
             f"_Comparing {parse_day(yday).strftime('%A')}'s high with the same kind of day last week._", ""]

    # Top risers among young games (yesterday = a complete day)
    risers = []
    for gid, r in games.items():
        if not is_young(r, today):
            continue
        ratio, base = growth(r, yday, cutoff, state.get("baseline_day"))
        high = r["days"].get(yday, 0)
        if ratio and ratio >= 1.5 and high >= 1000:
            risers.append((ratio, high, base, gid, r))
    risers.sort(key=lambda x: -(x[0] * min(x[1], 50000)))
    lines.append("🚀 **Top risers (games under 60 days old)**")
    if risers:
        for ratio, high, base, gid, r in risers[:10]:
            a = age_days(r, today)
            lines.append(f"• {r['name'][:40]} — {fmt(high)} ({ratio:.1f}× vs {fmt(base)})"
                         f"{f', {a}d old' if a is not None else ''} {link(gid, state)}")
    else:
        lines.append("• Not enough history yet — risers appear after about a week of data.")

    # New entries in the last day
    new = [(gid, r) for gid, r in games.items()
           if r["first_seen"] in (today, yday) and not is_base(state, r)
           and r.get("last", 0) >= 1000]
    lines += ["", "🆕 **New in the top list (last 24h, 1K+ players)**"]
    if new:
        for gid, r in sorted(new, key=lambda x: -x[1]["last"])[:10]:
            lines.append(f"• {r['name'][:40]} — {fmt(r['last'])} {link(gid, state)}")
    else:
        lines.append("• None")

    # Copy clusters
    week_ago = parse_day(today) - timedelta(days=7)
    by_kw = {}
    for gid, r in games.items():
        if not is_base(state, r) and parse_day(r["first_seen"]) >= week_ago:
            for kw in keywords(r["name"]):
                by_kw.setdefault(kw, []).append(r)
    clusters, seen_sets = [], set()
    for kw, rs in sorted(by_kw.items(), key=lambda x: -len(x[1])):
        key = frozenset(id(r) for r in rs)
        if len(rs) >= 2 and key not in seen_sets:
            seen_sets.add(key)
            clusters.append((kw, rs))
    clusters = clusters[:6]
    lines += ["", "🧬 **Title words shared by new games this week**"]
    if clusters:
        for kw, rs in clusters:
            lines.append(f"• \"{kw}\" — {len(rs)} games: " + ", ".join(r["name"][:25] for r in rs[:4]))
    else:
        lines.append("• None yet")

    # Cross-platform heat
    yts = S.yt_stats(state, t)
    heats = []
    for gid in set(S.candidate_games(state, today, 400)) | set(yts):
        rec = games.get(gid)
        if rec is not None and not is_young(rec, today):
            continue
        h = S.heat(state, gid, today, cutoff, yts)
        if h and h["score"] >= 20:
            heats.append((h["score"], gid, h))
    heats.sort(key=lambda x: -x[0])
    lines += ["", "🔥 **Cross-platform heat (young games)**"]
    if heats:
        for _, gid, h in heats[:8]:
            lines.append("• " + S.heat_line(state, gid, h))
    else:
        lines.append("• Building up data — this fills in over the first few days.")

    # YouTube
    if S.src_state(state)["videos"]:
        hot = sorted(yts.items(), key=lambda kv: -kv[1]["views"])[:6]
        lines += ["", "📺 **Most-watched Roblox games on YouTube (last 48h)**"]
        if hot:
            for gid, y in hot:
                lines.append(f"• {S.game_name(state, gid)[:40]} — {y['n']} vid{'s' if y['n'] != 1 else ''}, "
                             f"{fmt(y['views'])} views · {fmt(S.players_now(state, gid))} playing {link(gid, state)}")
        else:
            lines.append("• No videos matched to games yet")
        words, have_prev = S.rising_title_words(state, t)
        lines += ["", "🗣️ **Rising words in Roblox video titles**" + ("" if have_prev else " _(no earlier data to compare yet)_")]
        if words:
            lines.append("• " + " · ".join(f"\"{g}\" ({n} videos{f', was {p}' if have_prev else ''})" for n, p, g in words))
        else:
            lines.append("• Nothing standing out")
    else:
        lines += ["", "📺 _YouTube not connected yet — add a YOUTUBE_API_KEY secret (see SETUP.md)._"]

    # Model predictions
    preds = state.get("_preds") or {}
    lines += ["", f"🎯 **Model: chance of reaching {fmt(C.EXPLODE_CCU)}+ players** (young games noticed in the last few days)"]
    if preds:
        for gid, p in sorted(preds.items(), key=lambda kv: -kv[1])[:8]:
            lines.append(f"• {S.game_name(state, gid)[:40]} — **{p*100:.0f}%** · {fmt(S.players_now(state, gid))} playing {link(gid, state)}")
    else:
        lines.append("• Still learning — predictions start once enough past breakouts are in the database (see the weekly report).")

    # Themes
    th = state.get("_themes") or []
    lines += ["", "🌱 **Themes to watch** (small themes that could become trends)"]
    if th:
        for p, sc, k, r, fired in th[:7]:
            pct = f"**{p*100:.0f}%**" if p is not None else f"{sc} signal{'s' if sc != 1 else ''}"
            sig = (" · " + ", ".join(T.INDICATORS[i][0] for i in fired[:3])) if fired else ""
            lines.append(f"• \"{T.display(k, state)}\" — {pct} · {r['games']} games, {r['new7']} new this week, "
                         f"{fmt(r['ccu'])} players{sig}")
    else:
        lines.append("• Building theme history — appears after the first full day of data.")

    # Outside Roblox
    ust = state.get("upstream", {})
    outside = []
    if ust.get("steam_rising"):
        outside.append("🎮 Steam climbers: " + ", ".join(f"{x['name']} (#{x['rank']})" for x in ust["steam_rising"][:5]))
    if ust.get("ytt_rising"):
        outside.append("🔥 Rising on YouTube trending: " + ", ".join(f"\"{w}\"" for w in ust["ytt_rising"][:8]))
    if ust.get("tw_top_new"):
        outside.append("🟣 New in Twitch's top games: " + ", ".join(ust["tw_top_new"][:5]))
    if ust.get("wiki_spikes"):
        outside.append("📚 New on Wikipedia's top pages: " + ", ".join(ust["wiki_spikes"][:6]))
    brs = state.get("_bridges") or []
    if brs:
        outside.append("🌉 **Already reaching Roblox:** " + ", ".join(f"\"{w}\" ({row['new7']} new games)" for w, _, row in brs[:6]))
    if outside:
        lines += ["", "🌍 **Outside Roblox** (things that often become Roblox trends a few weeks later)"] + ["• " + o for o in outside]
    try:
        _db = W.connect()
        fl = FUT.digest_lines(_db, today, fmt)
        _db.close()
        if fl:
            lines += [""] + fl
    except Exception as e:
        print(f"forward calendar digest failed: {e}", file=sys.stderr)

    # Twitch
    tw = S.top_twitch(state, yday) or S.top_twitch(state, today)
    if tw:
        lines += ["", "🎮 **Most-streamed Roblox games on Twitch (peak viewers)**"]
        for v, n, gid in tw:
            lines.append(f"• {S.game_name(state, gid)[:40]} — {fmt(v)} viewers across {n} stream{'s' if n != 1 else ''}")

    # Weekday hold
    young_ids = {gid for gid, r in games.items() if is_young(r, today)} | set(C.WATCHLIST)
    hl = HOLD.digest_lines(state, fmt, lambda u: S.game_name(state, u), young_ids, lambda u: link(u, state))
    if hl:
        lines += [""] + hl

    # Algorithm mirror
    if state.get("_promo"):
        pl = P.digest_lines(state["_promo"], lambda u: S.game_name(state, u), lambda u: link(u, state), young_ids, fmt)
        if pl:
            lines += [""] + pl

    # Updates and their effect
    ul = I.update_lines(state, today)
    if ul:
        lines += ["", "🛠️ **Recent updates and what they did to players**"] + ul

    # Watchlist
    lines += ["", "👀 **Watchlist** (yesterday's high vs same day last week)"]
    drops = []
    for gid, label in C.WATCHLIST.items():
        r = games.get(gid)
        if not r or yday not in r["days"]:
            lines.append(f"• {label} — not in the top list yesterday")
            continue
        prev_day = day_str(parse_day(yday) - timedelta(days=7))
        now_h, prev_h = r["days"][yday], r["days"].get(prev_day)
        if prev_h:
            pct = (now_h / prev_h - 1) * 100
            arrow = "🔺" if pct >= 5 else ("🔻" if pct <= -5 else "▫️")
            lines.append(f"• {arrow} {label} — {fmt(now_h)} ({pct:+.0f}%){extras(state, gid, today)}")
            if pct <= -C.WATCH_DROP_PCT:
                drops.append(label)
        else:
            lines.append(f"• {label} — {fmt(now_h)} (no data from a week ago yet){extras(state, gid, today)}")
    if drops:
        lines += ["", "⚠️ **Falling week over week:** " + ", ".join(drops)]

    dbs = state.get("_dbstats") or {}
    if dbs:
        lines += ["", f"_🗄️ Database: {dbs.get('games', 0):,} games · {dbs.get('daily', 0):,} game-days · "
                      f"{dbs.get('backfill', 0):,} histories downloaded · {dbs.get('mb', 0)} MB · last backup: {state.get('backup', 'not yet')}_"]
    yt_units = S.src_state(state)["yt_units"].get(yday, 0)
    lines += ["", "📎 _Charts and **dashboard.html** attached — open the dashboard in your browser for sortable tables._"
              if (C.DASHBOARD or C.DIGEST_CHARTS) else ""]
    lines += ["", f"_RoWatcher requests yesterday: {state['requests'].get(yday, 0)} / 1,000"
                  + (f" · YouTube quota: {yt_units:,} / 10,000_" if yt_units else "_")]
    return "\n".join(lines)


def present_ctx():
    return {"S": S, "T": T, "FUT": FUT, "I": I, "L": L, "HOLD": HOLD, "E": E, "BD": BD, "P": P, "W": W,
            "link": link, "fmt": fmt, "is_young": is_young, "growth": growth, "age_days": age_days,
            "is_base": is_base, "keywords": keywords}


def extras(state, gid, today):
    bits = []
    lr = S.like_ratio(state, gid)
    if lr is not None:
        bits.append(f"👍 {lr*100:.0f}%")
    for label, (m, pct) in (("group", S.group_growth(state, gid)), ("Discord", S.discord_growth(state, gid))):
        if m:
            bits.append(f"{label} {fmt(m)}" + (f" {pct:+.0f}%" if pct is not None else ""))
    upd = (S.src_state(state)["rbx"].get(gid) or {}).get("updated")
    if upd:
        bits.append(f"updated {upd[5:]}")
    return (" · " + " · ".join(bits)) if bits else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", type=float, help="run every N minutes (for a PC)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--digest-now", action="store_true")
    ap.add_argument("--test-webhooks", action="store_true")
    ap.add_argument("--check-sources", action="store_true")
    ap.add_argument("--weekly-now", action="store_true")
    a = ap.parse_args()

    if a.check_sources:
        load_dotenv()
        lines = S.check_sources(os.environ) + U.check(os.environ) + FUT.check(os.environ) + BD.check()
        post_discord(os.environ.get("DISCORD_ALERTS_WEBHOOK"), "**Source check**\n" + "\n".join(lines), a.dry_run, "alerts")
        return

    if a.test_webhooks:
        load_dotenv()
        post_discord(os.environ.get("DISCORD_ALERTS_WEBHOOK"), "✅ Trend bot connected — urgent alerts will appear here.", a.dry_run, "alerts")
        post_discord(os.environ.get("DISCORD_DIGEST_WEBHOOK"), "✅ Trend bot connected — the daily digest will appear here.", a.dry_run, "digest")
        return

    if a.loop:
        while True:
            try:
                run_once(a.dry_run, a.digest_now, a.weekly_now)
            except Exception as e:
                print(f"run failed: {e}", file=sys.stderr)
            time.sleep(a.loop * 60)
    else:
        run_once(a.dry_run, a.digest_now, a.weekly_now)


S.HOOKS.update(is_young=is_young, growth=growth, fmt=fmt)
I.HOOKS.update(is_young=is_young, age_days=age_days, fmt=fmt, link=lambda gid, state: link(gid, state))
DB.HOOKS.update(is_young=is_young, age_days=age_days, fmt=fmt, growth=growth)

if __name__ == "__main__":
    main()

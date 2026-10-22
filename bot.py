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
import dashboard as DB
import discord_out as DO
import insights as I
import sources as S

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
        entered_later = baseline_day is not None and game["first_seen"] > baseline_day
        if entered_later and parse_day(game["first_seen"]) > parse_day(day) - timedelta(days=5):
            base = cutoff  # it was below the top list last week
        else:
            return None, None
    if not base:
        return None, None
    return high / base, base


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

    # 1. Pull the top games
    top = []
    try:
        for page in range(1, C.TOP_PAGES + 1):
            resp = api.get("/games", {"sort": "playing", "page": page, "pageSize": C.PAGE_SIZE})
            data = resp.get("data") or []
            top += [normalise_game(g) for g in data]
            if len(data) < C.PAGE_SIZE:
                break
    except BudgetExceeded as e:
        print(f"Stopping fetch: {e}")
    if not top:
        print("No games fetched this run.")
        save_state(state)
        return

    first_run = not state["games"]
    if first_run:
        state["baseline_day"] = today
    cutoff = min(g["playing"] for g in top)

    games = state["games"]
    new_ids = []
    for g in top:
        rec = games.get(g["id"])
        if rec is None:
            rec = games[g["id"]] = {"name": g["name"], "first_seen": today,
                                    "created": g["created"], "days": {}}
            if not first_run:
                new_ids.append(g["id"])
        rec["name"] = g["name"]
        rec["last"] = g["playing"]
        rec["last_seen"] = today
        if g["created"]:
            rec["created"] = g["created"]
        rec["days"][today] = max(rec["days"].get(today, 0), g["playing"])

    # 2. Look up creation dates for promising new games (a few calls only)
    lookups = 0
    for gid in sorted(new_ids, key=lambda i: -games[i]["last"]):
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

    alerts = []  # each: {kind, gid, title, desc, url, fields, ping, text}

    def add(kind, gid, title, desc, fields=(), ping=False, extra_text=""):
        url = link(gid, state).strip("<>") if gid else None
        alerts.append({"kind": kind, "gid": gid, "title": title, "desc": desc, "url": url,
                       "fields": list(fields), "ping": ping,
                       "text": f"**{title}** — {desc}{extra_text}" + (f" {link(gid, state)}" if gid else "")})

    # 3a. Brand-new games entering the top list
    for gid in new_ids:
        rec = games[gid]
        if rec["last"] >= C.MIN_PLAYERS_NEW_ENTRY and is_young(rec, today) and cooled(state, "new:" + gid, today, 9999):
            a = age_days(rec, today)
            add("new", gid, f"🆕 New in the top {len(top)}: {rec['name'][:80]}",
                f"{fmt(rec['last'])} playing right now.",
                [("Players", fmt(rec["last"])), ("Age", f"{a} days" if a is not None else "unknown"),
                 ("Type", ", ".join(I.mechanics_of(rec["name"])) or "—")])
            state["alerts"]["new:" + gid] = today

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
              if r["first_seen"] != state.get("baseline_day") and parse_day(r["first_seen"]) >= week_ago]
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
                heat_fields(state, gid, h),
                ping=h["score"] >= C.PING_HEAT_SCORE and len(h["signals"]) >= 3,
                extra_text=" · " + S.heat_line(state, gid, h).split(" — ", 1)[-1].rsplit(" <", 1)[0])
            state["alerts"]["heat:" + gid] = today
    for gid, y in yts.items():
        name = S.game_name(state, gid)
        players = S.players_now(state, gid)
        if name == gid or players >= C.EARLY_WARNING_MAX_PLAYERS:
            continue
        if (y["n"] >= C.EARLY_WARNING_VIDEOS or y["views"] >= C.EARLY_WARNING_VIEWS) and cooled(state, "early:" + gid, today, 7):
            views, title, vid = y["top"]
            add("early", gid, f"👀 Early warning: {name[:80]}",
                f"Hot on YouTube while still small on Roblox.\nTop video: [{title[:80]}](https://youtu.be/{vid}) ({fmt(views)} views)",
                [("Playing now", fmt(players)), ("YouTube 48h", f"{y['n']} videos"), ("Views 48h", fmt(y["views"]))],
                ping=y["views"] >= C.PING_EARLY_VIEWS,
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

    if alerts:
        header = f"**Trend alert** · {t.strftime('%a %d %b %H:%M')} UTC"
        icons = S.game_icons([a["gid"] for a in alerts if a.get("gid")]) if (C.RICH_CARDS and not dry_run) else {}
        DO.post_alerts(alerts_url, alerts, header, icons, dry_run)

    # 4. Daily digest (+ charts and dashboard), weekly report on the chosen day
    if force_digest or (state.get("last_digest") != today and t.hour >= C.DIGEST_HOUR_UTC and not first_run):
        files = digest_files(state, today, cutoff)
        post_discord(digest_url, build_digest(state, today, cutoff, t), dry_run, "digest", files)
        state["last_digest"] = today
    if force_weekly or (state.get("last_weekly") != today and t.weekday() == C.WEEKLY_REPORT_WEEKDAY
                        and t.hour >= C.DIGEST_HOUR_UTC and not first_run):
        text, table = I.weekly_report(state, today)
        files = []
        rows = [r for r in table if r["chg"] is not None]
        if C.DIGEST_CHARTS and rows:
            png = charts.bar_chart([r["mech"] for r in rows], [r["chg"] for r in rows],
                                   "Demand change by mechanic (this week vs last)")
            if png:
                files.append(("mechanics.png", png, "image/png"))
        post_discord(digest_url, text, dry_run, "weekly", files)
        state["last_weekly"] = today

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


def heat_fields(state, gid, h):
    p = h["parts"]
    f = [("Playing", fmt(S.players_now(state, gid)))]
    if "players" in p:
        f.append(("Players vs last week", f"{p['players']:.1f}×"))
    if "yt" in p:
        f.append(("YouTube 48h", f"{p['yt']['n']} videos · {fmt(p['yt']['views'])} views"))
    if "twitch" in p:
        tv, tr, ts = p["twitch"]
        f.append(("Twitch", f"{fmt(tv)} viewers" + (f" ({tr:.1f}×)" if tr else "")))
    for key, label in (("group", "Roblox group"), ("discord", "Discord")):
        if key in p:
            m, pct = p[key]
            f.append((label, fmt(m) + (f" ({pct:+.0f}%)" if pct is not None else "")))
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
           if r["first_seen"] in (today, yday) and r["first_seen"] != state.get("baseline_day")
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
        if r["first_seen"] != state.get("baseline_day") and parse_day(r["first_seen"]) >= week_ago:
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

    # Twitch
    tw = S.top_twitch(state, yday) or S.top_twitch(state, today)
    if tw:
        lines += ["", "🎮 **Most-streamed Roblox games on Twitch (peak viewers)**"]
        for v, n, gid in tw:
            lines.append(f"• {S.game_name(state, gid)[:40]} — {fmt(v)} viewers across {n} stream{'s' if n != 1 else ''}")

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

    yt_units = S.src_state(state)["yt_units"].get(yday, 0)
    lines += ["", "📎 _Charts and **dashboard.html** attached — open the dashboard in your browser for sortable tables._"
              if (C.DASHBOARD or C.DIGEST_CHARTS) else ""]
    lines += ["", f"_RoWatcher requests yesterday: {state['requests'].get(yday, 0)} / 1,000"
                  + (f" · YouTube quota: {yt_units:,} / 10,000_" if yt_units else "_")]
    return "\n".join(lines)


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
        lines = S.check_sources(os.environ)
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

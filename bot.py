#!/usr/bin/env python3
"""
Roblox trend bot.

Every run: pulls the top games by live players from RoWatcher's official API,
remembers each game's daily high, and posts to Discord when something looks
like a trend starting. Once a day it posts a digest.

No AI involved, so it costs no tokens. Uses only the Python standard library.

Usage:
  python bot.py                 # one run (what GitHub Actions does)
  python bot.py --loop 20       # keep running every 20 minutes (for a PC)
  python bot.py --dry-run       # print messages instead of posting them
  python bot.py --test-webhooks # post a hello message to both channels
  python bot.py --digest-now    # force today's digest
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

import config as C

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

def post_discord(url, text, dry_run=False, label=""):
    chunks, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > 1900:
            chunks.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        chunks.append(cur)
    for chunk in chunks:
        if dry_run or not url:
            print(f"----- [{label or 'discord'}] -----\n{chunk}")
            continue
        body = json.dumps({"content": chunk, "allowed_mentions": {"parse": []}}).encode()
        for attempt in range(3):
            req = urllib.request.Request(url, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "roblox-trend-bot/1.0"})
            try:
                urllib.request.urlopen(req, timeout=20).read()
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 2.0
                    try:
                        wait = float(json.loads(e.read().decode()).get("retry_after", 2))
                    except Exception:
                        pass
                    time.sleep(min(wait, 10))
                    continue
                print(f"Discord error {e.code}: {e.read()[:200]}", file=sys.stderr)
                break
            except (urllib.error.URLError, OSError) as e:
                print(f"Couldn't reach Discord ({e}); will try again next run.", file=sys.stderr)
                if attempt == 2:
                    break
                time.sleep(2)
        time.sleep(0.5)


def link(gid):
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

def run_once(dry_run=False, force_digest=False):
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

    alerts = []

    # 3a. Brand-new games entering the top list
    for gid in new_ids:
        rec = games[gid]
        if rec["last"] >= C.MIN_PLAYERS_NEW_ENTRY and is_young(rec, today) and cooled(state, "new:" + gid, today, 9999):
            a = age_days(rec, today)
            age = f"{a} days old" if a is not None else "age unknown"
            alerts.append(f"🆕 **New in the top {len(top)}:** {rec['name']} — {fmt(rec['last'])} playing ({age}) {link(gid)}")
            state["alerts"]["new:" + gid] = today

    # 3b. Weekday-to-weekday surges in young games
    for gid, rec in games.items():
        if rec.get("last_seen") != today or not is_young(rec, today):
            continue
        ratio, base = growth(rec, today, cutoff, state.get("baseline_day"))
        high = rec["days"].get(today, 0)
        if ratio and ratio >= C.SURGE_MULTIPLIER and high >= C.SURGE_MIN_PLAYERS and cooled(state, "surge:" + gid, today):
            kind = "weekend" if is_weekend(today) else "weekday"
            alerts.append(f"🚀 **Surging:** {rec['name']} — today's high {fmt(high)} vs {fmt(base)} on {kind}s last week "
                          f"(**{ratio:.1f}×**) {link(gid)}")
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
            names = ", ".join(f"{r['name'][:30]} ({fmt(r['last'])})" for _, r in sorted(items, key=lambda x: -x[1]["last"])[:5])
            alerts.append(f"🧬 **Copy wave forming — \"{kw}\":** {len(items)} new games this week: {names}")
            state["alerts"]["copy:" + kw] = today

    if alerts:
        header = f"**Trend alert** · {t.strftime('%a %d %b %H:%M')} UTC"
        post_discord(alerts_url, header + "\n" + "\n".join(alerts), dry_run, "alerts")

    # 4. Daily digest
    if force_digest or (state.get("last_digest") != today and t.hour >= C.DIGEST_HOUR_UTC and not first_run):
        post_discord(digest_url, build_digest(state, today, cutoff), dry_run, "digest")
        state["last_digest"] = today

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


def build_digest(state, today, cutoff):
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
                         f"{f', {a}d old' if a is not None else ''} {link(gid)}")
    else:
        lines.append("• Not enough history yet — risers appear after about a week of data.")

    # New entries in the last day
    new = [(gid, r) for gid, r in games.items()
           if r["first_seen"] in (today, yday) and r["first_seen"] != state.get("baseline_day")
           and r.get("last", 0) >= 1000]
    lines += ["", "🆕 **New in the top list (last 24h, 1K+ players)**"]
    if new:
        for gid, r in sorted(new, key=lambda x: -x[1]["last"])[:10]:
            lines.append(f"• {r['name'][:40]} — {fmt(r['last'])} {link(gid)}")
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
            lines.append(f"• {arrow} {label} — {fmt(now_h)} ({pct:+.0f}%)")
            if pct <= -C.WATCH_DROP_PCT:
                drops.append(label)
        else:
            lines.append(f"• {label} — {fmt(now_h)} (no data from a week ago yet)")
    if drops:
        lines += ["", "⚠️ **Falling week over week:** " + ", ".join(drops)]

    lines += ["", f"_API requests used yesterday: {state['requests'].get(yday, 0)} / 1,000_"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", type=float, help="run every N minutes (for a PC)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--digest-now", action="store_true")
    ap.add_argument("--test-webhooks", action="store_true")
    a = ap.parse_args()

    if a.test_webhooks:
        load_dotenv()
        post_discord(os.environ.get("DISCORD_ALERTS_WEBHOOK"), "✅ Trend bot connected — urgent alerts will appear here.", a.dry_run, "alerts")
        post_discord(os.environ.get("DISCORD_DIGEST_WEBHOOK"), "✅ Trend bot connected — the daily digest will appear here.", a.dry_run, "digest")
        return

    if a.loop:
        while True:
            try:
                run_once(a.dry_run, a.digest_now)
            except Exception as e:
                print(f"run failed: {e}", file=sys.stderr)
            time.sleep(a.loop * 60)
    else:
        run_once(a.dry_run, a.digest_now)


if __name__ == "__main__":
    main()

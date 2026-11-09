"""
Small, fast checks of the parts the simulation can't easily reach: the alert budget, the circuit breaker,
message splitting, HTML escaping, the event-tag rule, the Wikipedia source and the backup size guard.

    python tests/test_units.py          # a few seconds, no network
"""
import json
import os
import random
import sys
import tempfile
import urllib.error
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="trendbot-unit-")
os.environ.update(STATE_PATH=os.path.join(TMP, "state.json"), DB_PATH=os.path.join(TMP, "trendbot.db"))
sys.path.insert(0, os.path.dirname(HERE))

import bot  # noqa: E402
import config as C  # noqa: E402
import dashboard as DASH  # noqa: E402
import discord_out as DO  # noqa: E402
import events as EV  # noqa: E402
import net as NET  # noqa: E402
import upstream as U  # noqa: E402
import warehouse as W  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


# ---- alert budget: three days of ~120 alerts a day at 30 runs a day ------------------------------------------------
random.seed(3)
prec = dict(bot.KIND_PRIOR)
state = {"alerts": {}, "ts": {}, "ts_mode": "starting formula"}
kinds = ["new"] * 40 + ["surge"] * 25 + ["abroad"] * 25 + ["copy"] * 10 + ["breakout"] * 12 + ["early"] * 8 + ["chart"] * 5 + ["heat"] * 2
t0 = datetime(2026, 11, 10, 0, 7, tzinfo=timezone.utc)
gid, sent, by_hour = 0, {}, []
_print, bot.print = print, lambda *a, **k: None
for day in range(3):
    for run in range(30):
        now = t0 + timedelta(days=day, minutes=48 * run)
        today = now.strftime("%Y-%m-%d")
        alerts = []
        for k in random.sample(kinds, 4):
            gid += 1
            key = f"{k}:{gid}"
            state["ts"][str(gid)] = random.randint(5, 70)
            alerts.append({"kind": k, "gid": str(gid), "title": f"{k} {gid}", "desc": "d", "url": None, "fields": [],
                           "ping": False, "keys": [[key, state["alerts"].get(key)]], "text": "t"})
            state["alerts"][key] = today
        out = bot.apply_budget(alerts, state, today, now, prec)
        for a in out:
            sent[a["kind"]] = sent.get(a["kind"], 0) + 1
            by_hour.append(now.hour)
del bot.print
check("budget: never more than the daily budget", all(n <= C.ALERT_DAILY_BUDGET for n in state["alert_count"].values()),
      str(state["alert_count"]))
check("budget: the cards go to the alert types that are right most often",
      sent.get("chart", 0) + sent.get("heat", 0) + sent.get("breakout", 0) >= 0.8 * sum(sent.values()) and not sent.get("new"),
      str(sent))
check("budget: cards are spread through the day, not spent by mid-morning",
      sum(1 for h in by_hour if h >= 12) >= len(by_hour) // 3, str(sorted(by_hour)))
shown = {f"{a['kind']}:{a['gid']}" for a in state["alert_queue"]}
dropped = [o[1] for v in state["overflow"].values() for o in v]
check("budget: an alert that was never shown gets its cooldown back",
      dropped and not any(f"{x.split()[0]}:{x.split()[1]}" in state["alerts"] for x in dropped))
try:
    json.dumps(state)
    check("budget: everything it keeps can be saved", True)
except TypeError as e:
    check("budget: everything it keeps can be saved", False, str(e))
ping = [{"kind": "surge", "gid": f"p{i}", "title": f"ping {i}", "desc": "d", "url": None, "fields": [], "ping": True,
         "keys": [], "text": "t"} for i in range(C.PING_DAILY_CAP + 4)]
pst, got_pings = {"alerts": {}, "ts": {}}, []
for hour in (0, 6, 12, 18, 23):
    for a in ping:
        a["ping"] = True
    batch = [dict(a, gid=f"{a['gid']}h{hour}") for a in ping]
    out = bot.apply_budget(batch, pst, "2026-11-20", datetime(2026, 11, 20, hour, 7, tzinfo=timezone.utc), prec)
    got_pings.append(sum(1 for a in out if a["ping"]))
check("budget: pings are capped per day and spread through it",
      sum(got_pings) == C.PING_DAILY_CAP and got_pings[0] <= 2 and sum(got_pings[2:]) >= 2, str(got_pings))

# ---- circuit breaker ------------------------------------------------------------------------------------------------
NET.begin()
url = "https://slow.example/api"
for _ in range(C.BREAKER_FAILS):
    try:
        with NET.call(url):
            raise TimeoutError("timed out")
    except TimeoutError:
        pass
try:
    with NET.call(url):
        pass
    check("breaker: a host that keeps failing is skipped", False)
except NET.Skipped:
    check("breaker: a host that keeps failing is skipped", True)
try:
    with NET.call("https://fine.example/x"):
        pass
    check("breaker: other hosts are unaffected", True)
except NET.Skipped:
    check("breaker: other hosts are unaffected", False)
NET.begin(3.0)
check("quota: a run after an hour's gap does three runs' worth", NET.quota(10) == 30 and NET.quota(1) == 3)
NET.begin(99)
check("quota: capped", NET.quota(10) == int(10 * C.RUN_SCALE_MAX))
NET.begin()

# ---- Discord text splitting ----------------------------------------------------------------------------------------
got = []
DO.send = lambda url, payload, files=None: (got.append(payload["content"]), True)[1]
DO.post_text("https://discord.example/hook", "short line\n" + "x" * 4500 + "\nlast line")
check("discord: no message over 2,000 characters, nothing lost",
      all(len(c) <= 2000 for c in got) and sum(c.count("x") for c in got) == 4500 and "last line" in got[-1],
      str([len(c) for c in got]))
DO.send = lambda url, payload, files=None: False
check("discord: a refused message is reported, not assumed sent", DO.post_text("https://discord.example/hook", "hello") is False)
al = [{"kind": "new", "title": "t", "desc": "d", "text": "x", "gid": None}]
check("discord: undelivered alerts are handed back", DO.post_alerts("https://discord.example/hook", al, "h", {}) == [])

# ---- dashboard escaping --------------------------------------------------------------------------------------------
h = DASH._md('**b** [a](https://x"onmouseover="alert(1)) <script>')
check("dashboard: a crafted game name can't add attributes or tags", '"onmouseover' not in h and "<script>" not in h, h)

# ---- event tags ----------------------------------------------------------------------------------------------------
st = {"games": {str(i): {"name": f"[FPS] Shooter {i}", "last_seen": "2026-10-01"} for i in range(20)}}
EV.update(st, "2026-10-01")
for i in range(20):
    st["games"][str(i)]["last_seen"] = "2026-10-05"
for i in range(20, 40):
    st["games"][str(i)] = {"name": f"[THE HUNT] Game {i}", "last_seen": "2026-10-05"}
for i in range(40, 55):
    st["games"][str(i)] = {"name": f"[MOON FEST] Game {i}", "last_seen": "2026-10-05"}
ev = EV.update(st, "2026-10-05")
check("events: a tag that was always there is not an event", "fps" not in ev, str(ev))
check("events: a known event and a new tag in many games are", "the hunt" in ev and "moon fest" in ev, str(ev))

# ---- Wikipedia: not published yet -> retried, older day filled in ----------------------------------------------------
db = W.connect()
U.ensure(db)
calls = []


def fake(url, headers=None, timeout=25):
    calls.append(url)
    if url.endswith("2026/11/08"):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    return {"items": [{"articles": [{"article": "Some_Page", "views": 1000}]}]}


U.get_json = fake
ust = {}
try:
    U.collect_wikipedia(db, ust, "2026-11-09")
    check("wikipedia: 'not published yet' asks for a retry", False)
except U.NotReady:
    check("wikipedia: 'not published yet' asks for a retry", "2026-11-07" in ust["wiki_hist"] and "2026-11-08" not in ust["wiki_hist"])
t = datetime(2026, 11, 9, 0, 7, tzinfo=timezone.utc)
state = {"upstream": ust}
U.collect_all(db, state, t, {}, lambda n: None)
check("wikipedia: a failed day is not marked done", "wikipedia" not in state["upstream"]["last"] and "wikipedia" in state["upstream"]["fail"])
check("wikipedia: no retry storm", not NET.may_try(state["upstream"]["fail"], "wikipedia", t + timedelta(minutes=30))
      and NET.may_try(state["upstream"]["fail"], "wikipedia", t + timedelta(minutes=C.DAILY_JOB_RETRY_MIN + 1)))

# ---- backup size guard ---------------------------------------------------------------------------------------------
rel = {"assets": [{"name": "b.enc", "size": 30_000_000, "id": 1}]}
check("backup: a backup half the size of the last one doesn't replace it", bool(W._shrunk(db, rel, "b.enc", 2_000_000)))
check("backup: a normal one does", W._shrunk(db, rel, "b.enc", 31_000_000) is None)
check("backup: a first backup does", W._shrunk(db, {"assets": []}, "b.enc", 2_000_000) is None)
calls = []


def fake_gh(method, url, token, data=None, ctype="application/json", accept="application/vnd.github+json"):
    calls.append(method + " " + url.rsplit("/", 1)[-1].split("?name=")[-1])
    return {"id": 99}


real_gh, W._gh = W._gh, fake_gh
W._put_asset("o/r", "t", {"id": 5, "assets": [{"name": "b.enc", "id": 1}]}, "b.enc", b"x", "application/octet-stream")
check("backup: the new copy is uploaded before the old one is removed", calls == ["POST b.enc.new", "DELETE 1", "PATCH 99"], str(calls))
calls.clear()
W._put_asset("o/r", "t", {"id": 5, "assets": [{"name": "b.enc.new", "id": 7}]}, "b.enc", b"x", "application/octet-stream")
check("backup: a half-finished replace is completed, not deleted", calls[0] == "PATCH 7" and "DELETE 7" in calls and calls[-1] == "PATCH 99", str(calls))
W._gh = real_gh
db.close()

# ---- restore: a backup that can't be read stops the run ------------------------------------------------------------
os.environ.update(GITHUB_REPOSITORY="o/r", GITHUB_TOKEN="t")
keep_path, W.DB_PATH = W.DB_PATH, os.path.join(TMP, "missing", "trendbot.db")


def no_release(repo, token, create=False):
    raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)


real_release, W._release = W._release, no_release
check("restore: no backup at all is a normal first run", W.restore_if_missing() is None)
W._release = lambda repo, token, create=False: {"id": 5, "assets": [{"name": W.ENC_ASSET, "id": 1, "size": 10}]}
os.environ.pop("BACKUP_PASSWORD", None)
try:
    W.restore_if_missing()
    check("restore: a backup that can't be read stops the run", False)
except W.RestoreFailed:
    check("restore: a backup that can't be read stops the run", not os.path.exists(W.DB_PATH))
W._release, W.DB_PATH = real_release, keep_path
for k in ("GITHUB_REPOSITORY", "GITHUB_TOKEN"):
    os.environ.pop(k, None)

print()
if fails:
    print(f"FAILED: {len(fails)} check(s): " + "; ".join(fails))
    sys.exit(1)
print("OK")

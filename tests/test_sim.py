"""
End-to-end test: runs the whole bot against a simulated Roblox for a couple of weeks (no network, no Discord)
and checks that every part ran without errors and produced its outputs.

    python tests/test_sim.py            # ~2-3 minutes
    SIM_DAYS=29 python tests/test_sim.py  # the full month used during development
"""
import io
import json
import os
import shutil
import sys
import tempfile
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="trendbot-test-")
os.environ.setdefault("SIM_ESTABLISHED", "1200")
os.environ.setdefault("SIM_YOUNG", "160")
os.environ.update(ROWATCHER_API_KEY="x", DISCORD_ALERTS_WEBHOOK="https://discord.com/api/webhooks/1/a",
                  DISCORD_DIGEST_WEBHOOK="https://discord.com/api/webhooks/2/b", YOUTUBE_API_KEY="fake",
                  STATE_PATH=os.path.join(TMP, "state.json"), DB_PATH=os.path.join(TMP, "trendbot.db"))
for k in ("TWITCH_CLIENT_ID", "TMDB_API_KEY", "GITHUB_TOKEN", "GITHUB_REPOSITORY", "BACKUP_PASSWORD"):
    os.environ.pop(k, None)
sys.path.insert(0, HERE)
import sim_world as world  # noqa: E402  (patches network access)
import bot  # noqa: E402
import present as PR  # noqa: E402
import discord_out as DO  # noqa: E402
import badges as BD  # noqa: E402

BD.time.sleep = lambda s: None
DO.time.sleep = lambda s: None
CAP = {"digest": [], "weekly": [], "ask": []}


def cap(url, cards, content="", files=None, dry_run=False, label="digest"):
    CAP.setdefault(label, []).append({"cards": cards, "files": [f[0] for f in (files or [])]})


PR.post_cards = cap
bot.now_utc = lambda: world.NOW[0]

days = int(os.environ.get("SIM_DAYS", 12))
errors = io.StringIO()
out = io.StringIO()
crashes = 0
with redirect_stdout(out), redirect_stderr(errors):
    while world.NOW[0] < world.START + timedelta(days=days):
        try:
            bot.run_once()
        except Exception:
            crashes += 1
            traceback.print_exc()
        world.NOW[0] += timedelta(hours=3)
    for q in ("how is cat battles doing", "is chocolate trending", "which genres earn the most", "what's rising",
              "is there an influx of games surrounding the sea/boats/ pirates?"):
        try:
            bot.run_ask(q)
        except Exception:
            crashes += 1
            traceback.print_exc()

err = [l for l in errors.getvalue().splitlines() if l.strip() and "not simulated" not in l]
bad = [l for l in err if "Traceback" in l or "failed" in l or "Error" in l]
problems = []
if crashes:
    problems.append(f"{crashes} run(s) crashed")
if bad:
    problems.append("errors logged:\n  " + "\n  ".join(sorted(set(bad))[:30]))
if len(CAP["digest"]) < days - 2:
    problems.append(f"only {len(CAP['digest'])} digests for {days} days")
if not CAP["weekly"]:
    problems.append("no weekly report")
if len(CAP.get("ask", [])) < 5:
    problems.append("ask answers missing")
elif not any("Theme" in (c or {}).get("title", "") for c in CAP["ask"][-1]["cards"]):
    problems.append("sea/boats/pirates question wasn't answered as a theme: " + str([c["title"] for c in CAP["ask"][-1]["cards"]]))
elif os.environ.get("VERBOSE"):
    print(CAP["ask"][-1]["cards"][0]["description"])
titles = [c["title"] for d in CAP["digest"][-1:] for c in d["cards"] if c]
for need in ("Daily digest", "Games to watch"):
    if not any(need in t for t in titles):
        problems.append(f"digest card missing: {need}")
if os.environ.get("VERBOSE"):
    keys = ("game passes:", "icons:", "roblox events", "alert budget", "trend score:", "forecasts:", "money:", "roblox direct:", "badges:")
    seen = {}
    for l in out.getvalue().splitlines():
        for k in keys:
            if l.startswith(k):
                seen[k] = l
    print("\n".join(seen.values()))
    print("\n".join(err[-15:]))
print(f"{days} simulated days · {len(CAP['digest'])} digests · {len(CAP['weekly'])} weekly · {len(CAP.get('ask', []))} answers")
shutil.rmtree(TMP, ignore_errors=True)
if problems:
    print("FAILED:\n- " + "\n- ".join(problems))
    sys.exit(1)
print("OK")

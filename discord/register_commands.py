"""
Registers the bot's slash commands with Discord (run once, and again if commands change).
Runs on GitHub: Actions -> "Discord commands" -> Run workflow.
Needs secrets DISCORD_APP_ID and DISCORD_BOT_TOKEN (optional DISCORD_GUILD_ID: commands appear instantly in that server).
"""
import json
import os
import sys
import urllib.error
import urllib.request

S, I = 3, 3  # option types: string
COMMANDS = [
    {"name": "ask", "description": "Ask the trend bot anything about Roblox games, themes or earnings",
     "options": [{"type": S, "name": "question", "description": "e.g. how is Wash the Car doing", "required": True}]},
    {"name": "game", "description": "Everything the bot knows about one game",
     "options": [{"type": S, "name": "name", "description": "Game name (rough is fine)", "required": True}]},
    {"name": "compare", "description": "Two games side by side",
     "options": [{"type": S, "name": "first", "description": "First game", "required": True},
                 {"type": S, "name": "second", "description": "Second game", "required": True}]},
    {"name": "theme", "description": "Is a theme (title word) trending?",
     "options": [{"type": S, "name": "word", "description": "e.g. chocolate, pirate, wash", "required": True}]},
    {"name": "top", "description": "Games to watch right now, ranked by Trend Score"},
    {"name": "money", "description": "What earns the most (optionally for one genre or mechanic)",
     "options": [{"type": S, "name": "topic", "description": "e.g. tycoon, simulation, pets", "required": False}]},
    {"name": "longterm", "description": "Long-term games and the genres that hold players"},
    {"name": "algorithm", "description": "What Roblox's algorithm is rewarding right now"},
    {"name": "coming", "description": "Upcoming releases and dates, and whether they're on Roblox yet"},
]


def main():
    app, token, guild = os.environ.get("DISCORD_APP_ID"), os.environ.get("DISCORD_BOT_TOKEN"), os.environ.get("DISCORD_GUILD_ID")
    if not (app and token):
        sys.exit("Set the DISCORD_APP_ID and DISCORD_BOT_TOKEN secrets first (see SETUP.md).")
    url = (f"https://discord.com/api/v10/applications/{app}/guilds/{guild}/commands" if guild
           else f"https://discord.com/api/v10/applications/{app}/commands")
    req = urllib.request.Request(url, data=json.dumps(COMMANDS).encode(), method="PUT", headers={
        "Authorization": f"Bot {token}", "Content-Type": "application/json", "User-Agent": "trendbot (github, 1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            got = json.loads(r.read().decode())
        print(f"Registered {len(got)} commands" + (f" in server {guild}" if guild else " (global)") + ": "
              + ", ".join("/" + c["name"] for c in got))
    except urllib.error.HTTPError as e:
        sys.exit(f"Discord refused ({e.code}): {e.read().decode()[:500]}")


if __name__ == "__main__":
    main()

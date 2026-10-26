# Roblox Trend Bot

A free, self-running bot that watches Roblox and the wider internet, learns from what happens next, and
tells you in Discord which games and themes are about to take off. It runs on GitHub Actions every
20 minutes, keeps its own database, uses no AI service (no tokens) and stays inside every free allowance.

---

## What you get

### In Discord

| Channel | What arrives |
|---|---|
| **#alerts** | One card per game when something big happens: 🚀 high **Trend Score**, 🌍 climbing abroad first, 🏆 a proven studio launched something, 🧭 breakout just started, 🆕 crossed 2K players, 📈 entered Roblox's charts, 🔥 heating up across platforms, 👀 big on YouTube while still small. Several signals about the same game in one run are merged into one card. Theme alerts: 🌱 emerging theme, 🌉 outside trend reaching Roblox, 🔮 first copies of something upcoming. Plus a one-line notice if the bot ever fails. Capped at about 12 cards a day (pings and watchlist always get through); anything else is listed under "Also flagged" in the digest. |
| **#daily-digest** (about 08:00 UK) | Five short cards: **📊 Today in 30 seconds** · **🎮 Games to watch** (ranked by Trend Score, with plain-English reasons) · **🌱 Trends** (themes, copy waves, rising words in YouTube Shorts and videos) · **🔮 Coming up** · **👀 Watchlist** — plus charts and the **dashboard.html** file. |
| **Sundays** | **🗓️ The week in a few lines**, then cards for mechanics, what Roblox's algorithm rewards, long-term games, engagement, what lasting games share, forecasts & lifespans, **💰 what earns the most**, and whether the predictions are working. The full-length report is attached. |

### The Trend Score (the one number to watch)
Every young game gets a **Trend Score from 0 to 100**: the chance its players at least double within two
weeks. It combines every signal below, learns their weights from what actually happened, and is
calibrated (a score of 70 means about 70% of games scored like that took off). Until it has enough real
outcomes it uses a sensible starting formula, and the Sunday report says which mode it's in and how
accurate it has been.

### The signals behind it
- **Players** — every game in RoWatcher's top 2,000 every 20–60 minutes, plus Roblox's own data for smaller and newer games (home-page sorts like Up-and-Coming, Roblox search, live player counts). Daily averages are corrected for the time of day each game was read.
- **Abroad first** — Roblox's Top Trending / Up-and-Coming in 15 countries (Brazil, the Philippines, Indonesia, Mexico…): games charting abroad before the worldwide lists.
- **Proven studios** — a new game from a studio whose other game was a hit.
- **Roblox events** — games taking part in platform events (e.g. "[THE HOLLOW]") are flagged, so event boosts aren't mistaken for real demand.
- **Growth just accelerated** — Bayesian change-point detection on each game's growth.
- **Forecast headroom** — an S-curve fitted to each rise: likely peak and when.
- **Roblox promotion chance** — the *algorithm mirror* learns which signals Roblox is rewarding right now (and warns when that changes).
- **Breakout model** — how much the game looks like past breakouts.
- **YouTube Shorts** — how fast Shorts about the game are being watched (the fastest signal for what kids are into), in English, Portuguese, Spanish and Indonesian, plus YouTube videos and big-creator coverage. *TikTok and Instagram Reels have no free public access, so Shorts is the short-video source.*
- **Copy waves** — new games sharing title words, studios piling in, tiny-game bursts, and **icon copies** (new games whose icon is nearly identical to a hit's).
- **Quality** — weekday hold, playtime per player, returning players and funnels (from public badge stats), likes, favourites.
- **Outside Roblox** — Steam, Wikipedia, YouTube trending, Twitch, upcoming films/shows/games and holidays.

Every model and signal is **scored against what happened**, and the Sunday report shows the results.

### Ask the bot
In Discord with **slash commands** (`/game`, `/theme`, `/top`, `/money`, `/ask`… — step 8), or on
GitHub → **Actions → Roblox trend bot → Run workflow** → type in **"Ask the bot a question"** → **Run workflow**.
The answer appears in #daily-digest a minute later (works from the GitHub phone app). Examples:
`how is Wash the Car doing` · `Be a Pirate vs Pilfering Pirates` · `is chocolate trending` · `tycoon games` ·
`which genres earn the most` · `tycoon money` · `what's rising` · `long term games` · `what is roblox rewarding` · `what's coming up`

### The dashboard
A **live web page** (once you switch on GitHub Pages — step 7) at `https://<your-username>.github.io/<repo>/`, updated every morning; also attached to each digest as **dashboard.html**. Tabs: ⭐ Overview · 🔥 Hot young games · ★ Watchlist ·
🏛️ Long-term · 🧠 Algorithm · 🔎 Search (every game seen in 30 days) · 💰 Money · 🌱 Themes · 🧭 Mechanics · 💥 Breakouts · 🛠️ Updates.
Every column sorts; every table filters.

### Reports branch
Each day the bot also writes readable files to the repo's **`reports`** branch (switch the branch picker on
GitHub): `digest.md`, `board.csv`, `money.md`, `money.csv`, and on Sundays `weekly.md`. Open the CSVs in a
spreadsheet, or hand them to Claude to answer anything about the bot's data.

---

## Setup

### 1. RoWatcher key
Log in at <https://rowatcher.com>, open <https://rowatcher.com/docs/api> and generate an API key.

### 2. GitHub
1. Create a repository (public is fine — secrets stay secret) and upload every file, including `.github/workflows/trendbot.yml`.
2. **Settings → Secrets and variables → Actions → New repository secret**, add:

   | Secret | Value | Needed? |
   |---|---|---|
   | `ROWATCHER_API_KEY` | your RoWatcher key | required |
   | `DISCORD_ALERTS_WEBHOOK` | webhook URL of your alerts channel | required |
   | `DISCORD_DIGEST_WEBHOOK` | webhook URL of your digest channel | required |
   | `YOUTUBE_API_KEY` | free YouTube Data API key (step 3) | strongly recommended (Shorts + videos) |
   | `BACKUP_PASSWORD` | any long random password you keep somewhere safe | recommended (step 4) |
   | `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET` | free Twitch app (step 5) | optional |
   | `TMDB_API_KEY` | free TMDB key (step 6) | optional |

3. **Actions → Roblox trend bot → Run workflow** with **"Just post a hello"** ticked → both channels get ✅. Then run once with nothing ticked; after that it runs by itself.

### 3. YouTube (free, 5 minutes)
<https://console.cloud.google.com> → new project → enable **YouTube Data API v3** → **Credentials → Create credentials → API key** → (optional) restrict it to that API → save as `YOUTUBE_API_KEY`. The bot uses up to 9,000 of the 10,000 free daily units and stops itself before the limit.

### 4. Encrypted backups (recommended)
The bot's memory lives in GitHub's Actions cache, which is deleted if unused for 7 days. With a
`BACKUP_PASSWORD` secret, the bot saves an **encrypted** copy (database + memory) to the repo's Releases page
every day and restores itself automatically if the cache is ever lost. Without the password, the file is
unreadable, so it's safe in a public repo. Keep the password somewhere safe; without it the backup can't be opened.

### 5. Twitch (optional)
Turn on two-factor at <https://www.twitch.tv/settings/security>, register an app at <https://dev.twitch.tv/console/apps>
(redirect `http://localhost`, category Analytics Tool, client type Confidential), copy the Client ID and a new secret.

### 6. Films & shows (optional)
Free account at <https://www.themoviedb.org/signup> → <https://www.themoviedb.org/settings/api> → request a Developer
API key → save the short **API Key** as `TMDB_API_KEY`. (This product uses the TMDB API but is not endorsed or certified by TMDB.)

### 7. Live dashboard (GitHub Pages, 1 minute)
Repo **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `reports` / `(root)` → Save**.
After the next daily digest the dashboard is live at `https://<your-username>.github.io/<repo>/` (the link is also in the digest).
Note: like the repo itself, the page is public.

### 8. Discord slash commands (optional, free, about 15 minutes)
Ask the bot from Discord: `/game Wash the Car`, `/compare`, `/theme chocolate`, `/top`, `/money`, `/longterm`,
`/algorithm`, `/coming`, or `/ask` anything. Discord shows "Trend bot is thinking…" and the answer replaces it
about a minute later (the bot wakes up on GitHub to answer). How it works: Discord → a tiny free
**Cloudflare Worker** (`discord/worker.js`) → starts the bot's GitHub workflow → the bot edits the reply.

**a) Discord app** — <https://discord.com/developers/applications> → **New Application** (e.g. "Trend Bot").
- **General Information:** copy the **Application ID** and the **Public Key**.
- **Bot:** **Reset Token** → copy the token (only used once, to register the commands).
- **Installation:** under *Guild Install* make sure **applications.commands** is ticked, copy the **Install Link**,
  open it and add the app to your server.
- Your server's ID: Discord → User Settings → Advanced → Developer Mode on → right-click your server → **Copy Server ID**.
  Your own user ID: right-click your name → **Copy User ID**.

**b) GitHub secrets** (Settings → Secrets and variables → Actions): `DISCORD_APP_ID`, `DISCORD_BOT_TOKEN`,
`DISCORD_GUILD_ID` (your server ID). Then **Actions → Discord commands → Run workflow** — the log should say
"Registered 9 commands".

**c) A GitHub token for the worker** — <https://github.com/settings/personal-access-tokens/new> → name "trendbot discord",
expiry up to a year → **Repository access: Only select repositories → TrendBot** → **Permissions → Actions: Read and write** →
**Generate token** → copy it.

**d) Cloudflare Worker** — free account at <https://dash.cloudflare.com/sign-up> → **Workers & Pages → Create → Create Worker** →
name it `trendbot-discord` → **Deploy** → **Edit code** → replace everything with the contents of `discord/worker.js` → **Deploy**.
Then the worker's **Settings → Variables and Secrets → Add** (type *Secret*):

| Name | Value |
|---|---|
| `DISCORD_PUBLIC_KEY` | the Public Key from (a) |
| `GITHUB_TOKEN` | the token from (c) |
| `GITHUB_REPO` | `F-TestR/TrendBot` |
| `ALLOWED_USERS` | your Discord user ID (so only you can use it; leave out to allow everyone in the server) |

Copy the worker's address (like `https://trendbot-discord.<you>.workers.dev`).

**e) Connect them** — back in the Discord app's **General Information → Interactions Endpoint URL**, paste the worker address → **Save**
(Discord checks it straight away; if it refuses, re-check `DISCORD_PUBLIC_KEY`). Type `/top` in your server.

### 9. Check everything
**Run workflow** with **"Test all data sources"** ticked → #alerts gets a ✅/❌ line per source.

---

## What to expect
- **Day 1:** memory builds; alerts start; first digest next morning.
- **Week 1:** week-on-week growth, weekday hold, stickiness, badges, earnings, game passes and icon tracking fill in.
- **Weeks 2–3:** the breakout, theme, algorithm-mirror and Trend Score models start passing their accuracy tests; their percentages appear only once they score at least 0.6 on data they never saw (0.5 = coin flip).
- **Month 2+:** lifespans, indicator lead times and the Trend Score's live check become solid.

## Tuning
Everything is in `config.py`, grouped by section: the **watchlist** (`WATCHLIST`), alert thresholds, ping levels
(`PING_USER_ID` to be @mentioned), YouTube and Shorts searches (`YT_QUERIES`, `YT_SHORTS_QUERIES`), Roblox search
words (`RBX_SEARCH_WORDS`), mechanic groups (`MECHANICS`), dates to watch (`FUTURE_EVENTS`), Trend Score alert
level (`TS_ALERT`), and switches for cards, charts, the dashboard and reports.

## Tests
Every code change runs the **Tests** workflow: the whole bot against a simulated Roblox for two weeks
(no network, no Discord). If it fails, the change is broken — the scheduled bot isn't affected until it's fixed.

## Limits worth knowing
- RoWatcher's free API serves its top 2,000 games; smaller games come from Roblox directly.
- Revenue figures are RoWatcher's estimates, not real payouts — good for comparing, not for exact amounts.
- Badge-based numbers need games with common badges (about two thirds of games).
- TikTok and Reels can't be read for free; YouTube Shorts covers short video.

## If something breaks
The bot posts the error to #alerts (once a day per error). If a webhook ever leaks: Discord → channel settings →
Integrations → Webhooks → delete, create a new one, update the secret.

## Running on a PC instead
Install Python 3, copy `env.example` to `.env` and fill it in, then `python bot.py --loop 20`
(also `--test-webhooks`, `--check-sources`, `--digest-now`, `--weekly-now`, `--ask "question"`).

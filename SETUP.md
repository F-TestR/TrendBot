# Roblox Trend Bot

A free, self-running bot that watches Roblox and the wider internet, learns from what happens next, and
tells you in Discord which games and themes are about to take off. It runs on GitHub Actions every
20 minutes, keeps its own database, uses no AI service (no tokens) and stays inside every free allowance.

---

## What you get

### In Discord

| Channel | What arrives |
|---|---|
| **#alerts** | One card per game when something big happens: 🚀 high **Trend Score**, 🧭 breakout just started, 🆕 crossed 2K players, 📈 entered Roblox's charts, 🔥 heating up across platforms, 👀 big on YouTube while still small. Several signals about the same game in one run are merged into one card. Theme alerts: 🌱 emerging theme, 🌉 outside trend reaching Roblox, 🔮 first copies of something upcoming. Plus a one-line notice if the bot ever fails. |
| **#daily-digest** (about 08:00 UK) | Five short cards: **📊 Today in 30 seconds** · **🎮 Games to watch** (ranked by Trend Score, with plain-English reasons) · **🌱 Trends** (themes, copy waves, rising words in YouTube Shorts and videos) · **🔮 Coming up** · **👀 Watchlist** — plus charts and the **dashboard.html** file. |
| **Sundays** | **🗓️ The week in a few lines**, then cards for mechanics, what Roblox's algorithm rewards, long-term games, engagement, what lasting games share, forecasts & lifespans, **💰 what earns the most**, and whether the predictions are working. The full-length report is attached. |

### The Trend Score (the one number to watch)
Every young game gets a **Trend Score from 0 to 100**: the chance its players at least double within two
weeks. It combines every signal below, learns their weights from what actually happened, and is
calibrated (a score of 70 means about 70% of games scored like that took off). Until it has enough real
outcomes it uses a sensible starting formula, and the Sunday report says which mode it's in and how
accurate it has been.

### The signals behind it
- **Players** — every game in RoWatcher's top 2,000 every 20–60 minutes, plus Roblox's own data for smaller and newer games (home-page sorts like Up-and-Coming, Roblox search, live player counts).
- **Growth just accelerated** — Bayesian change-point detection on each game's growth.
- **Forecast headroom** — an S-curve fitted to each rise: likely peak and when.
- **Roblox promotion chance** — the *algorithm mirror* learns which signals Roblox is rewarding right now (and warns when that changes).
- **Breakout model** — how much the game looks like past breakouts.
- **YouTube Shorts** — how fast Shorts about the game are being watched (the fastest signal for what kids are into), plus YouTube videos and big-creator coverage. *TikTok and Instagram Reels have no free public access, so Shorts is the short-video source.*
- **Copy waves** — new games sharing title words, studios piling in, tiny-game bursts.
- **Quality** — weekday hold, playtime per player, returning players and funnels (from public badge stats), likes, favourites.
- **Outside Roblox** — Steam, Wikipedia, YouTube trending, Twitch, upcoming films/shows/games and holidays.

Every model and signal is **scored against what happened**, and the Sunday report shows the results.

### Ask the bot
GitHub → **Actions → Roblox trend bot → Run workflow** → type in **"Ask the bot a question"** → **Run workflow**.
The answer appears in #daily-digest a minute later (works from the GitHub phone app). Examples:
`how is Wash the Car doing` · `Be a Pirate vs Pilfering Pirates` · `is chocolate trending` · `tycoon games` ·
`which genres earn the most` · `tycoon money` · `what's rising` · `long term games` · `what is roblox rewarding` · `what's coming up`

### The dashboard
Open **dashboard.html** from any digest in your browser. Tabs: ⭐ Overview · 🔥 Hot young games · ★ Watchlist ·
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

### 7. Check everything
**Run workflow** with **"Test all data sources"** ticked → #alerts gets a ✅/❌ line per source.

---

## What to expect
- **Day 1:** memory builds; alerts start; first digest next morning.
- **Week 1:** week-on-week growth, weekday hold, stickiness, badges and earnings fill in.
- **Weeks 2–3:** the breakout, theme, algorithm-mirror and Trend Score models start passing their accuracy tests; their percentages appear only once they score at least 0.6 on data they never saw (0.5 = coin flip).
- **Month 2+:** lifespans, indicator lead times and the Trend Score's live check become solid.

## Tuning
Everything is in `config.py`, grouped by section: the **watchlist** (`WATCHLIST`), alert thresholds, ping levels
(`PING_USER_ID` to be @mentioned), YouTube and Shorts searches (`YT_QUERIES`, `YT_SHORTS_QUERIES`), Roblox search
words (`RBX_SEARCH_WORDS`), mechanic groups (`MECHANICS`), dates to watch (`FUTURE_EVENTS`), Trend Score alert
level (`TS_ALERT`), and switches for cards, charts, the dashboard and reports.

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

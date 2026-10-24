# Roblox Trend Bot — setup

The bot checks RoWatcher every 20 minutes and posts to your Discord:

- **#alerts** (instant): a new game entering the top 1,000, a young game surging 3×+ against last week, or 3+ copies of something appearing in a week.
- **#daily-digest** (once a day, about 08:00 UK): top risers, new games, title words shared by new games, and your watchlist up or down.

It also reads **YouTube**, **Twitch**, **Roblox's own public game data** (likes, favourites, update dates) and **community size** (each game's Roblox group members, plus any Discord servers you list), and combines them into one **heat score** per game:

- 🔥 **Heating up** alert: a young game rising on 2+ platforms at once (e.g. players, YouTube and community growth).
- 👀 **Early warning** alert: a game getting lots of YouTube videos while it still has under 5K players.
- 💥 **Breakout** alert: a young game crossing 10K players (it's then followed for its whole lifecycle).
- 🛠️ **Update** alert: a watchlist game publishes an update; the digest then reports what it did to players after 1, 3 and 7 days.
- Alerts arrive as **cards** with the game's icon and a one-click link, and can **@mention you** on the biggest signals.
- The **daily digest** gains a heat table, YouTube and Twitch sections, update results, **charts** of player curves and a **dashboard.html** file you open in your browser (sortable tables of every tracked game).
- Every **Sunday** a **weekly opportunity report** groups games by mechanic (tycoon, anomaly, find-the, battles…) and labels each one 🟢 open gap / 🟡 crowding / 🔴 saturating, plus breakouts and how long trends last.

Roblox data needs no key. YouTube needs one free key (Step 3). Twitch (Step 5), @mentions (Step 6) and Discord tracking (see Tuning) are optional.

It also keeps its **own database** and **learns**:

- It scans the top ~3,000 games (down to ~350 players) through the day, and once a day goes down to ~150 players to catch tiny new games.
- It downloads the **past player history** of young games (about 2 months back) so it can learn from real breakouts straight away.
- Every day it retrains a small **prediction model**: "how likely is this young game to reach 25K+ players within 3 weeks?" 🎯 alerts fire when a still-small game scores 50%+.
- Every alert and prediction is logged and **scored** later, so the weekly report shows how often each signal was actually right.
- 📈 alerts when a young game enters Roblox's **algorithm charts**, and 🏆 **proven studio** tags on games from studios that have had hits before.

**Trend prediction (themes):** besides single games, it tracks **themes** — words and phrases shared by game titles ("cat", "chocolate", "anomaly") plus RoWatcher's curated trend list — and learns which ones are about to become trends:

- 🌱 **Emerging theme** alert: a small theme the model thinks will soon have 3+ games over 2K players (before that, when several early signals fire at once: copy bursts, many studios, tiny-game bursts, renames…).
- 🌉 **Outside trend reaching Roblox** alert: something rising on **Steam**, **YouTube trending**, **Wikipedia** or **Twitch** that has just started appearing in brand-new Roblox games.
- The digest gets **🌱 Themes to watch** and **🌍 Outside Roblox**; the dashboard gets a **Themes** tab.
- The Sunday report gets **🔬 Which indicators actually work**: for every signal, how often it was followed by a breakout, how much better than chance, and how many days' warning it gave. The theme model weights signals by what actually worked.
- Seasonal themes (Halloween, Christmas, summer…) are in `config.py` → `SEASONS`; add your own.

**Long-term games:** every week the bot measures how well each game keeps its weekend crowd on Tuesday–Wednesday compared with a typical game. Games that hold at least as well in most weeks are labelled 🏛️ **long-term** (habit games, not hype). The Sunday report ranks genres by how many of their games are long-term, a 🏛️ alert fires when a young game earns the label, the heat score rewards good hold, and the dashboard has a **Long-term** tab. It downloads ~8 weeks of history for established games in the background, so ratings appear within days.

**Stickiness:** each week the bot also estimates every game's **session length** (from players online and daily visits), and combines weekday hold, session length, players kept vs its best recent week, favourite rate and revenue per player into a **stickiness score (0–100)**. The Sunday report tests whether the score predicts which games still have players 4 weeks later, lists the **description features** (daily rewards, codes, trading…) most common in long-term games, and attaches an **opportunity map** placing each genre by growth vs stickiness.

It uses no AI service, so it costs no tokens. It stays inside RoWatcher's free API allowance (1,000 requests a day): it paces itself through the day, uses about 750–900, and never goes past 950.

---

## Step 1 — Get a RoWatcher API key (2 minutes)

1. Go to <https://rowatcher.com>, log in (create a free account if needed).
2. Open <https://rowatcher.com/docs/api> and generate an API key (a long string of letters and numbers).
3. Keep it private, like a password.

## Step 2 — Run it on GitHub (recommended: works when your PC is off)

1. Create a free account at <https://github.com> if you don't have one.
2. Click **New repository** → name it `trend-bot`.
   - **Public** = no limit on how often it runs (your keys stay secret either way).
   - **Private** = fine too, but edit `.github/workflows/trendbot.yml` and change `"7,27,47 * * * *"` to `"7,37 * * * *"` (every 30 min) so it stays within GitHub's free monthly minutes.
3. Upload every file from this folder, **including the `.github` folder**. (On the repo page: **Add file → Upload files**, then drag the folder contents in. If the `.github` folder doesn't upload by dragging, create the file manually: **Add file → Create new file**, name it `.github/workflows/trendbot.yml`, and paste its contents.)
4. Add your three secrets: repo **Settings → Secrets and variables → Actions → New repository secret**:

   | Name | Value |
   |---|---|
   | `ROWATCHER_API_KEY` | your RoWatcher API key |
   | `DISCORD_ALERTS_WEBHOOK` | your **alerts** channel webhook URL |
   | `DISCORD_DIGEST_WEBHOOK` | your **daily digest** channel webhook URL |

5. Test it: **Actions** tab → **Roblox trend bot** → **Run workflow** → tick **"Just post a hello"** → **Run**. You should get a ✅ message in both Discord channels.
6. Then click **Run workflow** once more with nothing ticked to start it. From then on it runs by itself.

Note: GitHub sometimes starts scheduled runs 5–15 minutes late when it's busy. That's normal.

## Step 3 — Add YouTube (free, about 5 minutes)

1. Go to <https://console.cloud.google.com> and sign in with any Google account.
2. Top bar → project picker → **New project** → name it `trend-bot` → **Create**, then make sure it's selected.
3. Search the top bar for **YouTube Data API v3** → open it → **Enable**.
4. Left menu → **Credentials** → **Create credentials → API key**. Copy the key.
5. (Recommended) Click the key → **API restrictions → Restrict key** → tick **YouTube Data API v3** → **Save**.
6. In GitHub, add a fourth secret: name `YOUTUBE_API_KEY`, value = that key.

No card is needed. The bot uses about half of YouTube's free daily allowance and stops itself before the limit.

## Step 4 — Check every source works

**Actions → Roblox trend bot → Run workflow** → tick **"Test YouTube / Roblox / Twitch / Discord access"** → **Run**.
Your #alerts channel gets a ✅ / ❌ line for each source (including Steam, Wikipedia, YouTube trending and Twitch top games). If anything shows ❌, screenshot it and send it over.

## Step 5 — Add Twitch (optional, free, about 5 minutes)

1. Twitch needs two-factor login switched on first: <https://www.twitch.tv/settings/security> → **Two-Factor Authentication**.
2. Go to <https://dev.twitch.tv/console/apps> → **Register Your Application**.
   - Name: anything unique, e.g. `trend-bot-yourname`
   - OAuth Redirect URLs: `http://localhost`
   - Category: **Analytics Tool** · Client Type: **Confidential**
3. Click **Create**, then **Manage** on your new app. Copy the **Client ID**, then click **New Secret** and copy that too.
4. Add two GitHub secrets: `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET`.
5. Run the source check again (Step 4): Twitch should show ✅.

## Step 6 — Get @mentioned on big signals (optional)

1. Discord → **User Settings → Advanced** → turn on **Developer Mode**.
2. Right-click your own name (in any member list or message) → **Copy User ID**.
3. In GitHub, open `config.py` → ✏️ → set `PING_USER_ID = "your number here"` → **Commit changes**.

You'll be pinged only for: heat 80+ on 3+ platforms, a 5×+ surge, 1M+ YouTube views on a small game, or a copy wave of 5+ games. Change these in `config.py` (`PING_*`).

## The dashboard

Each daily digest has a **dashboard.html** attached. Click it in Discord → download → open it in your browser. Tabs: 🔥 hot young games (heat, 14-day curve, YouTube, Twitch, community, likes), ★ watchlist, 🧭 mechanics, 💥 breakouts and 🛠️ updates. Click any column to sort; type in the box to filter.

## Alternative — run it on your PC instead of GitHub

1. Install Python 3 from <https://python.org> (tick "Add Python to PATH").
2. Copy `.env.example` to `.env` in the same folder and paste in your values (YouTube is optional).
3. Open a terminal in the folder and run:
   - `python bot.py --test-webhooks` — posts a hello to both channels.
   - `python bot.py --check-sources` — tests YouTube / Roblox / Twitch / Discord access.
   - `python bot.py --digest-now` / `--weekly-now` — post the digest or weekly report straight away.
   - `python bot.py --loop 20` — runs every 20 minutes while the window stays open.

## The database and backups

The database (`trendbot.db`) lives in GitHub's Actions cache next to the bot's memory, so nothing extra is needed.

- **Private repo:** it's also backed up once a day to your repo's **Releases** page (a release called "Trend bot database backup" — don't delete it). If the cache is ever cleared, the bot restores itself from there.
- **Public repo:** the backup is skipped, because anyone could download it. The cache alone is normally fine, but if you want the safety net, make the repo private (Settings → General → Danger Zone → Change visibility) and change the schedule to every 30 minutes as described in Step 2.

## What to expect

- **Day 1:** the bot builds its memory. New-game alerts start after the first run; the digest starts the next morning.
- **Day 1–2:** YouTube and Roblox data start straight away; group/Discord growth needs 2 days of counts; "rising title words" needs 2 days to compare.
- **After about a week:** weekday-vs-last-week comparisons kick in properly, so surge alerts, the risers list and the players part of the heat score become reliable.
- **First few days:** the bot downloads past histories in the background; the weekly report shows how many examples the model has.
- **Usually within the first week:** the model has enough finished examples (60+, including 8+ explosions) to train, and 🎯 predictions start. Its accuracy is reported every Sunday — trust it more as the "AUC" and scorecard numbers climb.
- **After two weeks:** the weekly report can compare mechanics week over week, so the 🟢 / 🟡 / 🔴 labels switch on.
- **Over the following months:** breakouts and update results pile up (kept for 6 months), so "how long trends last" and "what updates do" get more trustworthy.

## Tuning

Everything lives in `config.py`: thresholds (e.g. surge = 3×), the watchlist of games you care about (add any game's universe ID from its RoWatcher link), the digest time, the YouTube search terms (`YT_QUERIES`), and the heat alert levels (`HEAT_ALERT_SCORE`, `EARLY_WARNING_*`), the **mechanic groups** (`MECHANICS` — add your own words or groups), the weekly report day, what counts as "exploded" for the model (`EXPLODE_CCU`, `LABEL_DAYS`), when 🎯 alerts fire (`PREDICT_ALERT_PROB`), and on/off switches for cards, charts and the dashboard (`RICH_CARDS`, `DIGEST_CHARTS`, `DASHBOARD`).

**Tracking a game's Discord server (optional):** Roblox hides games' Discord links from bots, so add the ones you care about to `DISCORD_INVITES` in `config.py`, e.g. `"10767380385": "https://discord.gg/abc123",` (game's universe ID, then its invite link). Find the invite on the game's Roblox page or in YouTube video descriptions. Use an invite that never expires.

## If a webhook URL ever leaks

Discord → channel settings → Integrations → Webhooks → delete it, make a new one, and update the secret.

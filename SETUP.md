# Roblox Trend Bot — setup

The bot checks RoWatcher every 20 minutes and posts to your Discord:

- **#alerts** (instant): a new game entering the top 1,000, a young game surging 3×+ against last week, or 3+ copies of something appearing in a week.
- **#daily-digest** (once a day, about 08:00 UK): top risers, new games, title words shared by new games, and your watchlist up or down.

It uses no AI, so it costs no tokens. It stays inside RoWatcher's free API allowance (1,000 requests a day; the bot uses about 720 and stops itself at 950).

---

## Step 1 — Get a RoWatcher API key (2 minutes)

1. Go to <https://rowatcher.com>, log in (create a free account if needed).
2. Open <https://rowatcher.com/docs/api> and generate an API key. It starts with `rw_`.
3. Keep it private, like a password.

## Step 2a — Run it on GitHub (recommended: works when your PC is off)

1. Create a free account at <https://github.com> if you don't have one.
2. Click **New repository** → name it `trend-bot`.
   - **Public** = no limit on how often it runs (your keys stay secret either way).
   - **Private** = fine too, but edit `.github/workflows/trendbot.yml` and change `*/20` to `*/30` so it stays within GitHub's free monthly minutes.
3. Upload every file from this folder, **including the `.github` folder**. (On the repo page: **Add file → Upload files**, then drag the folder contents in. If the `.github` folder doesn't upload by dragging, create the file manually: **Add file → Create new file**, name it `.github/workflows/trendbot.yml`, and paste its contents.)
4. Add your three secrets: repo **Settings → Secrets and variables → Actions → New repository secret**:

   | Name | Value |
   |---|---|
   | `ROWATCHER_API_KEY` | your `rw_…` key |
   | `DISCORD_ALERTS_WEBHOOK` | your **alerts** channel webhook URL |
   | `DISCORD_DIGEST_WEBHOOK` | your **daily digest** channel webhook URL |

5. Test it: **Actions** tab → **Roblox trend bot** → **Run workflow** → tick **"Just post a hello"** → **Run**. You should get a ✅ message in both Discord channels.
6. Then click **Run workflow** once more with nothing ticked to start it. From then on it runs by itself.

Note: GitHub sometimes starts scheduled runs 5–15 minutes late when it's busy. That's normal.

## Step 2b — Or run it on your PC

1. Install Python 3 from <https://python.org> (tick "Add Python to PATH").
2. Copy `.env.example` to `.env` in the same folder and paste in your three values.
3. Open a terminal in the folder and run:
   - `python bot.py --test-webhooks` — posts a hello to both channels.
   - `python bot.py --loop 20` — runs every 20 minutes while the window stays open.

## What to expect

- **Day 1:** the bot builds its memory. New-game alerts start after the first run; the digest starts the next morning.
- **After about a week:** weekday-vs-last-week comparisons kick in properly, so surge alerts and the risers list become reliable.

## Tuning

Everything lives in `config.py`: thresholds (e.g. surge = 3×), the watchlist of games you care about (add any game's universe ID from its RoWatcher link), and the digest time.

## If a webhook URL ever leaks

Discord → channel settings → Integrations → Webhooks → delete it, make a new one, and update the secret.

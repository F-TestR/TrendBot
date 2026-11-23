# Model check

_Model check · 2026-11-23_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩🟩🟩🟩 session length (+0.27)
🟥🟥🟥 revenue per player (-0.19) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
🟥🟥🟥🟥 favourite rate (-0.25)
▫️ Unclear this week (direction flips when resampled, or measured for too few games): new players reaching the next badge, weekday hold vs a typical game, sessions per player per day, playtime per player per day, like ratio
• Model for *enters a Roblox chart within 7 days* (3,243 game-days): Honest test: accuracy **0.75** (likely between 0.68 and 0.81) · 0.5 = coin flip · top 10% picks came true **12%** of the time vs 4% for all · 1,331 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.75 vs 0.80 for boosted trees (trees better in 87% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (4,555 game-days): Honest test: accuracy **0.86** (likely between 0.83 and 0.89) · 0.5 = coin flip · top 10% picks came true **45%** of the time vs 9% for all · 2,449 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.86 vs 0.83 for the simple model (trees better in 100% of resamples)
⚠️ **Algorithm change watch** (vs 2026-11-02): favourite rate less rewarded (+0.04 → -0.25)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.67; their top 10% were promoted 16% of the time vs 6% overall (47,539 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.80; their top 10% were promoted 36% of the time vs 8% overall (55,045 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.75–0.81) · its top 10% took off 23% of the time vs 7.2% for all · 8,787 snapshots over 15 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 8787 / 629 over 15 days)
• Scores as shown at the time: 50+: 22% took off (750) · 25–49: 21% took off (683) · 10–24: 14% took off (867) · under 10: 3% took off (6487)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 595 young games, 20 of which exploded (3%). Only 181 of them (3 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (3 of 181; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **30/409** (7%) · 715 still in their 21-day window (37 already exploded)
• abroad: **23/229** (10%) · 475 still in their 21-day window (43 already exploded)
• 🚀 surge: **31/209** (15%) · 489 still in their 21-day window (37 already exploded)
• 💥 breakout: **24/111** (22%) · 144 still in their 21-day window (34 already exploded)
• model < 50%: **0/84** (0%) · 412 still in their 21-day window (4 already exploded)
• 🧬 copy wave: **5/73** (7%) · 402 still in their 21-day window (28 already exploded)
• 👀 early warning: **3/67** (4%) · 96 still in their 21-day window (6 already exploded)
• chart: **22/44** (50%) · 74 still in their 21-day window (34 already exploded)
• longterm: **2/15** (13%) · 59 still in their 21-day window (4 already exploded)
• 🔥 heat: **3/9** (33%) · 24 still in their 21-day window (7 already exploded)
• 🎯 prediction: **0/5** (0%) · 4 still in their 21-day window (1 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• model ≥ 50%: **1/4** (25%) · 4 still in their 21-day window (1 already exploded)
• studio: **1/3** (33%) · 49 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Trained on 1,892 calm theme-days from 1,094 themes; 56 (3.0%) were followed by a breakout.
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• Biggest drivers: number of games (+), theme growth over 7 days (+), players across the theme (+), an upcoming release or event (−), YouTube Shorts mentions rising (+)

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• Too few firings to judge (under 8): 📊 in the algorithm charts (0/1)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **182%**; 40% within 2× of the real peak (128 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 14% for any young game (100 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1516 games that peaked while the bot was watching; 1001 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: holds weekday players well **11d** (258) · average weekday hold **11d** (184) · holds them poorly **4d** (57)
By mechanic: Battles / army **8d** (61) · Roleplay / life **8d** (59) · Vehicles / riding **8d** (53) · Sports **8d** (41)
By genre: Action **10d** (108) · Puzzle **10d** (20) · Obby & Platformer **9d** (100) · Party & Casual **9d** (74)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **5,074** games (5,418 tried)
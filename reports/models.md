# Model check

_Model check · 2026-11-26_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
• No quality signal is reliably rewarded or penalised in this window.
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, like ratio, sessions per player per day, playtime per player per day, new players reaching the next badge, weekday hold vs a typical game, revenue per player, favourite rate
• Model for *enters a Roblox chart within 7 days* (3,639 game-days): Honest test: accuracy **0.79** (likely between 0.74 and 0.82) · 0.5 = coin flip · top 10% picks came true **17%** of the time vs 5% for all · 1,805 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.79 vs 0.77 for boosted trees (trees better in 32% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (4,550 game-days): Honest test: accuracy **0.87** (likely between 0.85 and 0.90) · 0.5 = coin flip · top 10% picks came true **55%** of the time vs 10% for all · 2,493 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.87 vs 0.87 for boosted trees (trees better in 50% of resamples; they need 90%+ and a 0.01+ lead)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.68; their top 10% were promoted 17% of the time vs 7% overall (53,471 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.81; their top 10% were promoted 37% of the time vs 8% overall (61,958 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.76–0.81) · its top 10% took off 23% of the time vs 7.3% for all · 10,760 snapshots over 18 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 10760 / 789 over 18 days)
• Scores as shown at the time: 50+: 23% took off (982) · 25–49: 21% took off (863) · 10–24: 13% took off (1105) · under 10: 3% took off (7810)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 634 young games, 21 of which exploded (3%). Only 220 of them (4 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (4 of 220; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), copies in the same mechanic in the 2 weeks before (−), players the day after (+), game age when noticed (−), (no hourly data) (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **39/473** (8%) · 739 still in their 21-day window (32 already exploded)
• abroad: **35/294** (12%) · 481 still in their 21-day window (33 already exploded)
• 🚀 surge: **38/252** (15%) · 499 still in their 21-day window (34 already exploded)
• 💥 breakout: **26/115** (23%) · 149 still in their 21-day window (34 already exploded)
• 🧬 copy wave: **11/104** (11%) · 425 still in their 21-day window (26 already exploded)
• model < 50%: **0/97** (0%) · 437 still in their 21-day window (4 already exploded)
• 👀 early warning: **4/81** (5%) · 88 still in their 21-day window (5 already exploded)
• chart: **27/54** (50%) · 76 still in their 21-day window (31 already exploded)
• longterm: **2/19** (11%) · 69 still in their 21-day window (4 already exploded)
• 🔥 heat: **3/11** (27%) · 25 still in their 21-day window (7 already exploded)
• studio: **2/9** (22%) · 47 still in their 21-day window
• 🎯 prediction: **0/8** (0%) · 1 still in their 21-day window (1 already exploded)
• update: **4/7** (57%) · 1 still in their 21-day window (1 already exploded)
• model ≥ 50%: **1/6** (17%) · 2 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Trained on 3,917 calm theme-days from 1,360 themes; 105 (2.7%) were followed by a breakout.
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• Biggest drivers: number of games (+), theme growth over 7 days (+), players across the theme (+), new games this week vs last week (−), in season (−)

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• Too few firings to judge (under 8): 📊 in the algorithm charts (0/1)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **153%**; 44% within 2× of the real peak (197 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 13% for any young game (122 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1586 games that peaked while the bot was watching; 1122 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (205) · holds weekday players well **11d** (270) · holds them poorly **3d** (70)
By mechanic: Battles / army **9d** (66) · Roleplay / life **8d** (64) · Vehicles / riding **8d** (54) · Sports **8d** (41)
By genre: Social **30d** (28) · Action **10d** (116) · Shooter **10d** (56) · RPG **10d** (50)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **5,211** games (5,605 tried)
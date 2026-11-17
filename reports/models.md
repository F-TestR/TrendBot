# Model check

_Model check · 2026-11-17_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥🟥 favourite rate (-0.17)
🟥🟥🟥🟥 revenue per player (-0.24) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, new players reaching the next badge, like ratio, playtime per player per day, weekday hold vs a typical game, sessions per player per day
• Model for *enters a Roblox chart within 7 days* (2,435 game-days): Honest test: accuracy **0.83** (likely between 0.74 and 0.90) · 0.5 = coin flip · top 10% picks came true **19%** of the time vs 3% for all · 581 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.83 vs 0.74 for the simple model (trees better in 90% of resamples)
• Model for *players up 50%+ within 7 days* (4,834 game-days): Honest test: accuracy **0.85** (likely between 0.82 and 0.87) · 0.5 = coin flip · top 10% picks came true **40%** of the time vs 9% for all · 2,621 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.85 vs 0.64 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.66; their top 10% were promoted 18% of the time vs 7% overall (35,166 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.79; their top 10% were promoted 34% of the time vs 8% overall (40,687 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.73–0.80) · its top 10% took off 23% of the time vs 7.0% for all · 5,083 snapshots over 9 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 5083 / 358 over 9 days)
• Scores as shown at the time: 50+: 22% took off (449) · 25–49: 23% took off (383) · 10–24: 11% took off (483) · under 10: 3% took off (3768)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 491 young games, 18 of which exploded (4%). Only 77 of them (1 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (1 of 77; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **10/213** (5%) · 721 still in their 21-day window (48 already exploded)
• abroad: **5/82** (6%) · 501 still in their 21-day window (52 already exploded)
• 💥 breakout: **9/51** (18%) · 168 still in their 21-day window (41 already exploded)
• 🚀 surge: **5/46** (11%) · 521 still in their 21-day window (54 already exploded)
• 👀 early warning: **1/37** (3%) · 110 still in their 21-day window (5 already exploded)
• 🧬 copy wave: **1/24** (4%) · 331 still in their 21-day window (27 already exploded)
• chart: **8/21** (38%) · 74 still in their 21-day window (40 already exploded)
• longterm: **0/5** (0%) · 51 still in their 21-day window (4 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• 🔥 heat: **0/1** (0%) · 30 still in their 21-day window (8 already exploded)
• studio: — · 37 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window (1 already exploded)
• model < 50%: — · 380 still in their 21-day window (2 already exploded)
• model ≥ 50%: — · 7 still in their 21-day window (2 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20).

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **115%**; 45% within 2× of the real peak (76 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **11%** of the time vs 17% for any young game (64 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1225 games that peaked while the bot was watching; 755 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **12d** (146) · holds weekday players well **11d** (225) · holds them poorly **5d** (45)
By mechanic: Sports **9d** (37) · RNG / gacha / luck **9d** (36) · Roleplay / life **8d** (54) · Battles / army **8d** (50)
By genre: Roleplay & Avatar Sim **10d** (59) · RPG **10d** (33) · Obby & Platformer **9d** (85) · Action **9d** (83)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **4,764** games (5,047 tried)
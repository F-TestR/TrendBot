# Model check

_Model check · 2026-11-24_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥🟥 favourite rate (-0.25)
🟥🟥🟥🟥 revenue per player (-0.35) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, sessions per player per day, like ratio, new players reaching the next badge, weekday hold vs a typical game, playtime per player per day
• Model for *enters a Roblox chart within 7 days* (3,342 game-days): Honest test: accuracy **0.76** (likely between 0.70 and 0.82) · 0.5 = coin flip · top 10% picks came true **17%** of the time vs 4% for all · 1,498 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.76 vs 0.68 for the simple model (trees better in 97% of resamples)
• Model for *players up 50%+ within 7 days* (4,536 game-days): Honest test: accuracy **0.88** (likely between 0.86 and 0.90) · 0.5 = coin flip · top 10% picks came true **52%** of the time vs 9% for all · 2,444 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.88 vs 0.84 for the simple model (trees better in 98% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.67; their top 10% were promoted 16% of the time vs 6% overall (49,570 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.81; their top 10% were promoted 36% of the time vs 8% overall (57,399 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.75–0.81) · its top 10% took off 24% of the time vs 7.3% for all · 9,456 snapshots over 16 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 9456 / 689 over 16 days)
• Scores as shown at the time: 50+: 23% took off (817) · 25–49: 21% took off (737) · 10–24: 14% took off (959) · under 10: 3% took off (6943)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 608 young games, 20 of which exploded (3%). Only 194 of them (3 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (3 of 194; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **33/422** (8%) · 728 still in their 21-day window (34 already exploded)
• abroad: **26/242** (11%) · 481 still in their 21-day window (40 already exploded)
• 🚀 surge: **32/224** (14%) · 487 still in their 21-day window (36 already exploded)
• 💥 breakout: **24/111** (22%) · 146 still in their 21-day window (34 already exploded)
• model < 50%: **0/88** (0%) · 420 still in their 21-day window (4 already exploded)
• 🧬 copy wave: **7/85** (8%) · 413 still in their 21-day window (26 already exploded)
• 👀 early warning: **4/72** (6%) · 92 still in their 21-day window (5 already exploded)
• chart: **25/47** (53%) · 73 still in their 21-day window (31 already exploded)
• longterm: **2/17** (12%) · 57 still in their 21-day window (4 already exploded)
• 🔥 heat: **3/11** (27%) · 22 still in their 21-day window (7 already exploded)
• studio: **2/7** (29%) · 45 still in their 21-day window
• 🎯 prediction: **0/6** (0%) · 3 still in their 21-day window (1 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• model ≥ 50%: **1/4** (25%) · 4 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Trained on 2,827 calm theme-days from 1,187 themes; 81 (2.9%) were followed by a breakout.
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• Biggest drivers: number of games (+), theme growth over 7 days (+), players across the theme (+), an upcoming release or event (−), tiny new games (studios testing it) (−)

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• Too few firings to judge (under 8): 📊 in the algorithm charts (0/1)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **153%**; 44% within 2× of the real peak (197 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 13% for any young game (122 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1544 games that peaked while the bot was watching; 1051 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **12d** (186) · holds weekday players well **10d** (263) · holds them poorly **3d** (62)
By mechanic: Roleplay / life **8d** (61) · Battles / army **8d** (60) · Vehicles / riding **8d** (56) · RNG / gacha / luck **8d** (44)
By genre: Social **30d** (26) · Action **10d** (113) · Obby & Platformer **9d** (106) · Party & Casual **9d** (76)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **5,115** games (5,484 tried)
# Model check

_Model check · 2026-11-21_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩🟩 like ratio (+0.15)
🟥🟥🟥🟥 revenue per player (-0.36) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, sessions per player per day, weekday hold vs a typical game, new players reaching the next badge, playtime per player per day, favourite rate
• Model for *enters a Roblox chart within 7 days* (2,973 game-days): Honest test: accuracy **0.74** (likely between 0.67 and 0.80) · 0.5 = coin flip · top 10% picks came true **12%** of the time vs 4% for all · 1,131 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.74 vs 0.76 for boosted trees (trees better in 74% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (4,667 game-days): Honest test: accuracy **0.89** (likely between 0.87 and 0.91) · 0.5 = coin flip · top 10% picks came true **53%** of the time vs 9% for all · 2,513 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.89 vs 0.77 for the simple model (trees better in 100% of resamples)
⚠️ **Algorithm change watch** (vs 2026-10-31): revenue per player less rewarded (+0.00 → -0.36)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.68; their top 10% were promoted 18% of the time vs 7% overall (43,344 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.80; their top 10% were promoted 36% of the time vs 8% overall (50,173 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.74–0.82) · its top 10% took off 25% of the time vs 7.3% for all · 7,526 snapshots over 13 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 7526 / 549 over 13 days)
• Scores as shown at the time: 50+: 23% took off (637) · 25–49: 22% took off (573) · 10–24: 14% took off (726) · under 10: 3% took off (5590)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 569 young games, 19 of which exploded (3%). Only 155 of them (2 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (2 of 155; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), copies in the same mechanic in the 2 weeks before (−), game age when noticed (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **24/332** (7%) · 756 still in their 21-day window (40 already exploded)
• abroad: **17/185** (9%) · 492 still in their 21-day window (46 already exploded)
• 🚀 surge: **25/156** (16%) · 513 still in their 21-day window (40 already exploded)
• 💥 breakout: **18/84** (21%) · 158 still in their 21-day window (37 already exploded)
• model < 50%: **0/65** (0%) · 395 still in their 21-day window (4 already exploded)
• 👀 early warning: **2/56** (4%) · 102 still in their 21-day window (6 already exploded)
• 🧬 copy wave: **4/54** (7%) · 399 still in their 21-day window (29 already exploded)
• chart: **18/39** (46%) · 75 still in their 21-day window (36 already exploded)
• longterm: **2/13** (15%) · 61 still in their 21-day window (2 already exploded)
• 🔥 heat: **1/6** (17%) · 27 still in their 21-day window (9 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• model ≥ 50%: **1/4** (25%) · 4 still in their 21-day window (1 already exploded)
• 🎯 prediction: **0/3** (0%) · 6 still in their 21-day window (1 already exploded)
• studio: **0/2** (0%) · 46 still in their 21-day window (2 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Trained on 999 calm theme-days from 999 themes; 33 (3.3%) were followed by a breakout.
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• Biggest drivers: theme growth over 3 days (+), number of games (+), players across the theme (+), Roblox YouTube mentions rising (−), rising on YouTube trending (−)

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• Too few firings to judge (under 8): 📊 in the algorithm charts (0/1)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **182%**; 40% within 2× of the real peak (128 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 14% for any young game (100 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1445 games that peaked while the bot was watching; 919 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: holds weekday players well **11d** (252) · average weekday hold **11d** (180) · holds them poorly **5d** (56)
By mechanic: Roleplay / life **9d** (54) · Battles / army **8d** (60) · Vehicles / riding **8d** (51) · Sports **8d** (40)
By genre: Action **10d** (107) · RPG **10d** (44) · Obby & Platformer **9d** (93) · Party & Casual **9d** (73)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **4,997** games (5,325 tried)
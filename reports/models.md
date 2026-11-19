# Model check

_Model check · 2026-11-19_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩 session length (+0.19)
🟥🟥 favourite rate (-0.27)
🟥🟥🟥🟥 revenue per player (-0.56) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): like ratio, sessions per player per day, playtime per player per day, new players reaching the next badge, weekday hold vs a typical game
• Model for *enters a Roblox chart within 7 days* (2,724 game-days): Honest test: accuracy **0.84** (likely between 0.78 and 0.90) · 0.5 = coin flip · top 10% picks came true **27%** of the time vs 5% for all · 841 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.84 vs 0.82 for boosted trees (trees better in 32% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (4,785 game-days): Honest test: accuracy **0.86** (likely between 0.83 and 0.88) · 0.5 = coin flip · top 10% picks came true **49%** of the time vs 10% for all · 2,556 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.86 vs 0.73 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.67; their top 10% were promoted 18% of the time vs 7% overall (39,246 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.79; their top 10% were promoted 35% of the time vs 8% overall (45,419 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.75–0.82) · its top 10% took off 24% of the time vs 7.1% for all · 6,291 snapshots over 11 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 6291 / 447 over 11 days)
• Scores as shown at the time: 50+: 22% took off (554) · 25–49: 23% took off (489) · 10–24: 12% took off (588) · under 10: 3% took off (4660)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 520 young games, 19 of which exploded (4%). Only 106 of them (2 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (2 of 106; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **17/270** (6%) · 749 still in their 21-day window (43 already exploded)
• abroad: **10/151** (7%) · 492 still in their 21-day window (48 already exploded)
• 🚀 surge: **17/111** (15%) · 508 still in their 21-day window (44 already exploded)
• 💥 breakout: **12/63** (19%) · 167 still in their 21-day window (39 already exploded)
• 👀 early warning: **1/48** (2%) · 103 still in their 21-day window (5 already exploded)
• 🧬 copy wave: **3/41** (7%) · 364 still in their 21-day window (27 already exploded)
• chart: **13/28** (46%) · 78 still in their 21-day window (37 already exploded)
• longterm: **0/6** (0%) · 68 still in their 21-day window (4 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• 🔥 heat: **0/4** (0%) · 28 still in their 21-day window (8 already exploded)
• studio: **0/1** (0%) · 42 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window (1 already exploded)
• model < 50%: — · 418 still in their 21-day window (2 already exploded)
• model ≥ 50%: — · 7 still in their 21-day window (2 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20).

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **182%**; 40% within 2× of the real peak (128 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 14% for any young game (100 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1359 games that peaked while the bot was watching; 837 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **12d** (173) · holds weekday players well **11d** (232) · holds them poorly **5d** (56)
By mechanic: Tower defense **10d** (17) · Sports **9d** (37) · Roleplay / life **8d** (54) · Battles / army **8d** (54)
By genre: Action **10d** (99) · RPG **10d** (39) · Obby & Platformer **9d** (89) · Roleplay & Avatar Sim **9d** (65)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **4,896** games (5,207 tried)
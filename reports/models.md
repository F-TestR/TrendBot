# Model check

_Model check · 2026-11-18_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩🟩🟩 session length (+0.23)
🟥🟥🟥 favourite rate (-0.19)
🟥🟥🟥🟥 revenue per player (-0.27) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): playtime per player per day, like ratio, weekday hold vs a typical game, sessions per player per day, new players reaching the next badge
• Model for *enters a Roblox chart within 7 days* (2,508 game-days): Honest test: accuracy **0.82** (likely between 0.76 and 0.88) · 0.5 = coin flip · top 10% picks came true **27%** of the time vs 5% for all · 679 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.82 vs 0.78 for the simple model (trees better in 92% of resamples)
• Model for *players up 50%+ within 7 days* (4,756 game-days): Honest test: accuracy **0.85** (likely between 0.82 and 0.87) · 0.5 = coin flip · top 10% picks came true **41%** of the time vs 8% for all · 2,536 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.85 vs 0.64 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.67; their top 10% were promoted 18% of the time vs 7% overall (37,201 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.80; their top 10% were promoted 34% of the time vs 8% overall (43,047 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.73–0.81) · its top 10% took off 23% of the time vs 7.0% for all · 5,682 snapshots over 10 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 5682 / 400 over 10 days)
• Scores as shown at the time: 50+: 21% took off (500) · 25–49: 23% took off (443) · 10–24: 12% took off (533) · under 10: 3% took off (4206)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 505 young games, 19 of which exploded (4%). Only 91 of them (2 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (2 of 91; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **14/247** (6%) · 733 still in their 21-day window (45 already exploded)
• abroad: **9/118** (8%) · 500 still in their 21-day window (49 already exploded)
• 🚀 surge: **14/96** (15%) · 502 still in their 21-day window (46 already exploded)
• 💥 breakout: **10/58** (17%) · 166 still in their 21-day window (41 already exploded)
• 👀 early warning: **1/42** (2%) · 106 still in their 21-day window (5 already exploded)
• 🧬 copy wave: **1/31** (3%) · 351 still in their 21-day window (28 already exploded)
• chart: **11/24** (46%) · 77 still in their 21-day window (38 already exploded)
• longterm: **0/5** (0%) · 51 still in their 21-day window (4 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• 🔥 heat: **0/4** (0%) · 27 still in their 21-day window (8 already exploded)
• studio: — · 41 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window (1 already exploded)
• model < 50%: — · 396 still in their 21-day window (2 already exploded)
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
⏳ A typical hit keeps half its peak players for **8 days** (1272 games that peaked while the bot was watching; 792 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **12d** (153) · holds weekday players well **10d** (222) · holds them poorly **6d** (49)
By mechanic: Sports **9d** (37) · RNG / gacha / luck **9d** (36) · Roleplay / life **8d** (53) · Battles / army **8d** (52)
By genre: RPG **10d** (38) · Action **9d** (91) · Obby & Platformer **9d** (87) · Party & Casual **9d** (63)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **4,834** games (5,131 tried)
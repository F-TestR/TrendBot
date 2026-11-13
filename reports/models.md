# Model check

_Model check · 2026-11-13_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥🟥🟥 revenue per player (-0.42) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): like ratio, session length, sessions per player per day, playtime per player per day, weekday hold vs a typical game, new players reaching the next badge, favourite rate
• Model for *enters a Roblox chart within 7 days* (1,868 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (4,873 game-days): Honest test: accuracy **0.82** (likely between 0.79 and 0.85) · 0.5 = coin flip · top 10% picks came true **44%** of the time vs 10% for all · 2,407 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.82 vs 0.51 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.65; their top 10% were promoted 17% of the time vs 7% overall (26,721 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.79; their top 10% were promoted 32% of the time vs 7% overall (30,850 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.73–0.81) · its top 10% took off 28% of the time vs 8.1% for all · 2,708 snapshots over 5 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 2708 / 219 over 5 days)
• Scores as shown at the time: 50+: 28% took off (218) · 25–49: 24% took off (205) · 10–24: 13% took off (256) · under 10: 4% took off (2029)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 422 young games, 17 of which exploded (4%). Only 11 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: not possible yet — it is run only on games the bot watched from the start (2026-10-22 on), and their 21-day outcomes only began finishing on 2026-11-13. It needs 10+ explosions among them.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), players the day after (+), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), visits gained on day 1 (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **1/37** (3%) · 712 still in their 21-day window (40 already exploded)
• 👀 early warning: **1/7** (14%) · 121 still in their 21-day window (4 already exploded)
• chart: **2/4** (50%) · 83 still in their 21-day window (32 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 447 still in their 21-day window (42 already exploded)
• 💥 breakout: — · 174 still in their 21-day window (36 already exploded)
• 🧬 copy wave: — · 235 still in their 21-day window (17 already exploded)
• longterm: — · 56 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 24 still in their 21-day window (5 already exploded)
• abroad: — · 488 still in their 21-day window (42 already exploded)
• studio: — · 24 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 259 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
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
⏳ A typical hit keeps half its peak players for **9 days** (1148 games that peaked while the bot was watching; 613 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **15d** (163) · holds weekday players well **12d** (222) · holds them poorly **3d** (35)
By mechanic: Roleplay / life **10d** (51) · Tycoon / sell stuff **9d** (33) · Sports **9d** (32) · RNG / gacha / luck **9d** (30)
By genre: Obby & Platformer **16d** (82) · Shooter **14d** (35) · Action **12d** (82) · Roleplay & Avatar Sim **11d** (66)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **3,823** games (4,030 tried)
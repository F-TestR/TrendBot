# Model check

_Model check · 2026-11-15_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥 weekday hold vs a typical game (-0.13) — games that keep a steady crowd all week rarely jump 50% in a week, so this mostly means "already settled", not that Roblox punishes retention
🟥🟥🟥 favourite rate (-0.23)
🟥🟥🟥🟥 revenue per player (-0.31) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, like ratio, playtime per player per day, sessions per player per day, new players reaching the next badge
• Model for *enters a Roblox chart within 7 days* (2,150 game-days): Honest test: accuracy **0.72** (likely between 0.58 and 0.86) · 0.5 = coin flip · top 10% picks came true **20%** of the time vs 5% for all · 300 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.72 vs 0.66 for boosted trees (trees better in 24% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (4,939 game-days): Honest test: accuracy **0.82** (likely between 0.79 and 0.85) · 0.5 = coin flip · top 10% picks came true **46%** of the time vs 9% for all · 2,501 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.82 vs 0.63 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.65; their top 10% were promoted 17% of the time vs 7% overall (30,830 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (35,648 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.73–0.81) · its top 10% took off 25% of the time vs 7.4% for all · 3,882 snapshots over 7 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 3882 / 286 over 7 days)
• Scores as shown at the time: 50+: 24% took off (329) · 25–49: 23% took off (291) · 10–24: 12% took off (358) · under 10: 3% took off (2904)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 475 young games, 17 of which exploded (4%). Only 61 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (0 of 61; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), visits gained on day 1 (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **5/145** (3%) · 735 still in their 21-day window (50 already exploded)
• 💥 breakout: **6/44** (14%) · 167 still in their 21-day window (40 already exploded)
• 👀 early warning: **1/20** (5%) · 116 still in their 21-day window (4 already exploded)
• chart: **4/14** (29%) · 79 still in their 21-day window (42 already exploded)
• 🚀 surge: **1/14** (7%) · 516 still in their 21-day window (55 already exploded)
• 🧬 copy wave: **0/9** (0%) · 285 still in their 21-day window (25 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• longterm: **0/2** (0%) · 54 still in their 21-day window (4 already exploded)
• 🔥 heat: — · 27 still in their 21-day window (8 already exploded)
• abroad: — · 537 still in their 21-day window (55 already exploded)
• studio: — · 31 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window (1 already exploded)
• model < 50%: — · 318 still in their 21-day window (2 already exploded)
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
⏳ A typical hit keeps half its peak players for **8 days** (1207 games that peaked while the bot was watching; 684 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (148) · holds weekday players well **12d** (218) · holds them poorly **8d** (43)
By mechanic: Vehicles / riding **9d** (39) · Sports **9d** (38) · RNG / gacha / luck **9d** (33) · Steal / brainrot **8d** (60)
By genre: Shooter **14d** (41) · Action **10d** (84) · Obby & Platformer **10d** (78) · Roleplay & Avatar Sim **10d** (61)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **4,381** games (4,623 tried)
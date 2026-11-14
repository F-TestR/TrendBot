# Model check

_Model check · 2026-11-14_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩🟩🟩 session length (+0.27)
🟥🟥🟥🟥 revenue per player (-0.32) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): like ratio, playtime per player per day, weekday hold vs a typical game, sessions per player per day, new players reaching the next badge, favourite rate
• Model for *enters a Roblox chart within 7 days* (2,001 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (4,930 game-days): Honest test: accuracy **0.82** (likely between 0.80 and 0.85) · 0.5 = coin flip · top 10% picks came true **41%** of the time vs 9% for all · 2,436 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.82 vs 0.51 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.65; their top 10% were promoted 17% of the time vs 7% overall (28,745 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 32% of the time vs 8% overall (33,226 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.72–0.81) · its top 10% took off 26% of the time vs 7.6% for all · 3,282 snapshots over 6 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 3282 / 250 over 6 days)
• Scores as shown at the time: 50+: 25% took off (284) · 25–49: 23% took off (252) · 10–24: 13% took off (306) · under 10: 3% took off (2440)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 447 young games, 17 of which exploded (4%). Only 33 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (0 of 33; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), players the day after (+), (no hourly data) (+), visits gained on day 1 (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **3/78** (4%) · 717 still in their 21-day window (41 already exploded)
• 👀 early warning: **1/14** (7%) · 116 still in their 21-day window (4 already exploded)
• chart: **4/12** (33%) · 80 still in their 21-day window (34 already exploded)
• 💥 breakout: **1/8** (12%) · 178 still in their 21-day window (38 already exploded)
• 🚀 surge: **0/6** (0%) · 477 still in their 21-day window (45 already exploded)
• update: **2/4** (50%) · 4 still in their 21-day window (3 already exploded)
• 🧬 copy wave: **0/1** (0%) · 267 still in their 21-day window (18 already exploded)
• longterm: — · 56 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 26 still in their 21-day window (7 already exploded)
• abroad: — · 511 still in their 21-day window (45 already exploded)
• studio: — · 27 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 292 still in their 21-day window
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
⏳ A typical hit keeps half its peak players for **8 days** (1141 games that peaked while the bot was watching; 643 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **15d** (157) · holds weekday players well **12d** (209) · holds them poorly **5d** (35)
By mechanic: Sports **10d** (34) · Roleplay / life **9d** (52) · Vehicles / riding **9d** (34) · RNG / gacha / luck **9d** (29)
By genre: Shooter **14d** (36) · Obby & Platformer **12d** (76) · Action **11d** (77) · Roleplay & Avatar Sim **11d** (66)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **4,102** games (4,326 tried)
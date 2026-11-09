# Model check

_Model check · 2026-11-09_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥 favourite rate (-0.16)
🟥🟥🟥 weekday hold vs a typical game (-0.25) — games that keep a steady crowd all week rarely jump 50% in a week, so this mostly means "already settled", not that Roblox punishes retention
🟥🟥🟥🟥 revenue per player (-0.35) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): like ratio, session length, sessions per player per day, playtime per player per day, new players reaching the next badge
• Model for *enters a Roblox chart within 7 days* (1,284 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (5,182 game-days): Honest test: accuracy **0.80** (likely between 0.77 and 0.83) · 0.5 = coin flip · top 10% picks came true **44%** of the time vs 11% for all · 2,532 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.57 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (18,550 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (21,343 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula**
• Starting formula vs real outcomes: accuracy **0.66** (likely 0.58–0.74) · its top 10% took off 16% of the time vs 6.8% for all · 501 snapshots over 1 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 501 / 34 over 1 day)
• Scores as shown at the time: 50+: 36% took off (14) · 25–49: 6% took off (17) · 10–24: 14% took off (51) · under 10: 5% took off (419)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 257 young games, 12 of which exploded (5%). Only 0 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: not possible yet — it is run only on games the bot watched from the start (2026-10-22 on), and their 21-day outcomes only began finishing on 2026-11-13. It needs 10+ explosions among them.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), studio's best previous game (−), visits gained on day 1 (−), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: — · 641 still in their 21-day window (35 already exploded)
• chart: — · 69 still in their 21-day window (28 already exploded)
• 👀 early warning: — · 108 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 356 still in their 21-day window (36 already exploded)
• 💥 breakout: — · 161 still in their 21-day window (29 already exploded)
• 🧬 copy wave: — · 166 still in their 21-day window (14 already exploded)
• longterm: — · 50 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 18 still in their 21-day window (5 already exploded)
• abroad: — · 405 still in their 21-day window (36 already exploded)
• studio: — · 15 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 161 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20).

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **74%**; 54% within 2× of the real peak (573 games)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **18%** of the time vs 22% for any young game (208 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **11 days** (926 games; 399 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (117) · holds weekday players well **12d** (187) · holds them poorly **8d** (25)
By mechanic: Care / baby / pets **13d** (15) · Anime / fighting style **12d** (23) · Roleplay / life **11d** (44) · Sports **10d** (30)
By genre: RPG **12d** (35) · Roleplay & Avatar Sim **11d** (53) · Party & Casual **11d** (49) · Strategy **11d** (25)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **2,435** games (2,529 tried)
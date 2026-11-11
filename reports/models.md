# Model check

_Model check · 2026-11-11_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥 weekday hold vs a typical game (-0.24) — games that keep a steady crowd all week rarely jump 50% in a week, so this mostly means "already settled", not that Roblox punishes retention
🟥🟥🟥🟥 revenue per player (-0.47) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, like ratio, sessions per player per day, new players reaching the next badge, playtime per player per day, favourite rate
• Model for *enters a Roblox chart within 7 days* (1,623 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (5,125 game-days): Honest test: accuracy **0.79** (likely between 0.76 and 0.82) · 0.5 = coin flip · top 10% picks came true **41%** of the time vs 9% for all · 2,494 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.79 vs 0.59 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.64; their top 10% were promoted 16% of the time vs 7% overall (22,644 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 32% of the time vs 7% overall (26,091 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula**
• Starting formula vs real outcomes: accuracy **0.74** (likely 0.70–0.80) · its top 10% took off 32% of the time vs 8.7% for all · 1,567 snapshots over 3 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 1567 / 137 over 3 days)
• Scores as shown at the time: 50+: 38% took off (81) · 25–49: 24% took off (102) · 10–24: 16% took off (148) · under 10: 5% took off (1236)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 331 young games, 13 of which exploded (4%). Only 0 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: not possible yet — it is run only on games the bot watched from the start (2026-10-22 on), and their 21-day outcomes only began finishing on 2026-11-13. It needs 10+ explosions among them.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), studio's best previous game (−), copies in the same mechanic in the 2 weeks before (−), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: — · 686 still in their 21-day window (36 already exploded)
• chart: — · 79 still in their 21-day window (30 already exploded)
• 👀 early warning: — · 119 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 398 still in their 21-day window (37 already exploded)
• 💥 breakout: — · 167 still in their 21-day window (32 already exploded)
• 🧬 copy wave: — · 195 still in their 21-day window (14 already exploded)
• longterm: — · 50 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 21 still in their 21-day window (5 already exploded)
• abroad: — · 446 still in their 21-day window (37 already exploded)
• studio: — · 19 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 190 still in their 21-day window
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
⏳ A typical hit keeps half its peak players for **9 days** (1030 games; 507 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (141) · holds weekday players well **10d** (196) · holds them poorly **6d** (29)
By mechanic: Roleplay / life **10d** (44) · Sports **10d** (32) · Vehicles / riding **9d** (30) · RNG / gacha / luck **9d** (24)
By genre: All **12d** (10) · Roleplay & Avatar Sim **11d** (55) · Sports & Racing **11d** (48) · Party & Casual **10d** (59)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **3,084** games (3,213 tried)
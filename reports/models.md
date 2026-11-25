# Model check

_Model check · 2026-11-25_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
• No quality signal is reliably rewarded or penalised in this window.
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, like ratio, playtime per player per day, sessions per player per day, weekday hold vs a typical game, new players reaching the next badge, favourite rate, revenue per player
• Model for *enters a Roblox chart within 7 days* (3,539 game-days): Honest test: accuracy **0.73** (likely between 0.67 and 0.80) · 0.5 = coin flip · top 10% picks came true **18%** of the time vs 5% for all · 1,704 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.73 vs 0.74 for boosted trees (trees better in 64% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (4,539 game-days): Honest test: accuracy **0.88** (likely between 0.85 and 0.90) · 0.5 = coin flip · top 10% picks came true **55%** of the time vs 10% for all · 2,491 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.88 vs 0.88 for boosted trees (trees better in 58% of resamples; they need 90%+ and a 0.01+ lead)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.67; their top 10% were promoted 17% of the time vs 6% overall (51,519 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.81; their top 10% were promoted 37% of the time vs 8% overall (59,675 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.76–0.81) · its top 10% took off 24% of the time vs 7.4% for all · 10,106 snapshots over 17 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 10106 / 744 over 17 days)
• Scores as shown at the time: 50+: 23% took off (893) · 25–49: 22% took off (798) · 10–24: 13% took off (1039) · under 10: 3% took off (7376)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 619 young games, 20 of which exploded (3%). Only 205 of them (3 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (3 of 205; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), players the day after (+), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **36/453** (8%) · 714 still in their 21-day window (32 already exploded)
• abroad: **34/284** (12%) · 460 still in their 21-day window (33 already exploded)
• 🚀 surge: **36/242** (15%) · 483 still in their 21-day window (33 already exploded)
• 💥 breakout: **24/112** (21%) · 147 still in their 21-day window (35 already exploded)
• 🧬 copy wave: **8/94** (9%) · 409 still in their 21-day window (26 already exploded)
• model < 50%: **0/91** (0%) · 431 still in their 21-day window (4 already exploded)
• 👀 early warning: **4/75** (5%) · 91 still in their 21-day window (5 already exploded)
• chart: **26/52** (50%) · 73 still in their 21-day window (31 already exploded)
• longterm: **2/18** (11%) · 56 still in their 21-day window (4 already exploded)
• 🔥 heat: **3/11** (27%) · 24 still in their 21-day window (7 already exploded)
• studio: **2/8** (25%) · 47 still in their 21-day window
• update: **4/7** (57%) · 1 still in their 21-day window (1 already exploded)
• 🎯 prediction: **0/7** (0%) · 2 still in their 21-day window (1 already exploded)
• model ≥ 50%: **1/5** (20%) · 3 still in their 21-day window (1 already exploded)
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
⏳ A typical hit keeps half its peak players for **8 days** (1576 games that peaked while the bot was watching; 1088 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **12d** (197) · holds weekday players well **10d** (269) · holds them poorly **3d** (68)
By mechanic: Disasters / survival **9d** (25) · Battles / army **8d** (66) · Roleplay / life **8d** (61) · Vehicles / riding **8d** (54)
By genre: Social **30d** (27) · Action **10d** (114) · Obby & Platformer **9d** (106) · Party & Casual **9d** (76)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **5,154** games (5,532 tried)
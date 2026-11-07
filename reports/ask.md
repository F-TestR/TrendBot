# Latest question

**Q:** how accurate is the bot

## 🎯 How accurate is the bot (1/2)

_Model check · 2026-11-07_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week. Bars = how much one step up in a signal raises the odds, after allowing for size, momentum and age._
🟩🟩 like ratio (+0.09)
🟩 session length (+0.07)
🟩 playtime per player per day (badges) (+0.03)
🟩 new players reaching the next badge (badges) (+0.03)
🟥 weekday hold vs a typical game (-0.00)
🟥 returning-player share (badges) (-0.01)
🟥 sessions per player per day (badges) (-0.04)
🟥 favourite rate (-0.07)
🟥🟥🟥🟥 revenue per player (-0.22)
- Model for *enters a Roblox chart within 7 days*: accuracy 0.84 on days it hadn't seen (0.5 = coin flip); its top 10% were promoted 37% of the time vs 7% for all games (5219 examples).
  ⚙️ Simple model kept: walk-forward accuracy 0.64 vs 0.64 for boosted trees (trees must win by 0.01+)
- Model for *players up 50%+ within 7 days*: accuracy 0.83 on days it hadn't seen (0.5 = coin flip); its top 10% were promoted 37% of the time vs 8% for all games (5412 examples).
  ⚙️ Using **boosted trees**: walk-forward accuracy **0.83** vs 0.81 for the simple model (2,706 predictions tested in time order)
🧪 Live check, enters a Roblox chart within 7 days: past predictions scored 0.65; their top 10% were promoted 15% of the time vs 7% overall (14490 predictions).
🧪 Live check, players up 50%+ within 7 days: past predictions scored 0.78; their top 10% were promoted 35% of the time vs 8% overall (16622 predictions).
_Correlation from public data, not Roblox's actual model — but it tracks what its outputs reward, and the live check shows whether it works._

**⭐ Trend Score**
🚀 Trend Score: using its starting formula — needs 400+ outcomes with 30+ take-offs (has 0 / 0)

**💥 Explosion model + alert scorecard**
🧠 **What the model has learned** (explode = 25.0K+ players within 21 days)
- Trained on 175 young games, 11 of which exploded.
- Tested on the newest 44 games it hadn't seen: ranking accuracy (AUC) **0.67** (0.5 = coin flip, 1.0 = perfect). Its top 10% picks exploded **25%** of the time vs 7% for a random young game.
- Biggest drivers: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), players the day after (+)

🎯 **Scorecard: how often signals were followed by an explosion**
- 🆕 crossed 2K: — · 566 still in their 21-day window (28 already exploded)
- chart: — · 59 still in their 21-day window (25 already exploded)
- 👀 early warning: — · 95 still in their 21-day window (2 already exploded)
- update: — · 7 still in their 21-day window (4 already exploded)
- 🚀 surge: — · 309 still in their 21-day window (29 already exploded)
- 💥 breakout: — · 149 still in their 21-day window (22 already exploded)
- 🧬 copy wave: — · 140 still in their 21-day window (12 already exploded)
- longterm: — · 45 still in their 21-day window (3 already exploded)
- 🔥 heat: — · 15 still in their 21-day window (4 already exploded)
- abroad: — · 351 still in their 21-day window (30 already exploded)
- studio: — · 9 still in their 21-day window
- 🎯 prediction: — · 8 still in their 21-day window
- model < 50%: — · 124 still in their 21-day window
- model ≥ 50%: — · 6 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a theme "breaks out" when 3+ of its games under 45 days old pass 2.0K players within 21 days)
- Trained on 4,588 theme-days, 1588 of which led to a breakout.
- On the newest data it hadn't seen: AUC **0.77**; its top 5% picks broke out **95%** of the time vs 50.3% on average.

## 🎯 How accurate is the bot (2/2)

- ⚙️ Simple model kept: walk-forward accuracy 0.77 vs 0.76 for boosted trees (trees must win by 0.01+)
- Biggest drivers: number of games (+), new games this week vs last week (−), theme growth over 7 days (+), new games this week (+), different studios making it (+)

🔬 **Which indicators actually work** (184 theme breakouts tracked so far)
- 📈 theme doubled in a week: followed by a breakout 23/57 times · **1.2×** better than chance · ~8 days' warning · caught 48% of breakouts
- 📊 in the algorithm charts: followed by a breakout 6/6 times · **2.9×** better than chance · ~4 days' warning · caught 41% of breakouts
- 📺 Roblox YouTube buzz: followed by a breakout 1/1 times · **2.9×** better than chance · ~12 days' warning · caught 6% of breakouts
- 🔥 YouTube trending: followed by a breakout 1/1 times · **2.9×** better than chance · ~5 days' warning · caught 9% of breakouts
- Not enough data yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 🎮 rising on Steam, 📚 Wikipedia spike, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **74%**; 54% within 2× of the real peak (573 games)
   ↳ not accurate enough to quote numbers yet (needs 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **18%** of the time vs 22% for any young game (208 firings) · **alerts paused** until it beats that
⏳ A typical hit keeps half its peak players for **11 days** (1589 games)
By weekday hold: holds weekday players well **23d** · average weekday hold **17d** · holds them poorly **7d**
By mechanic: Merge / clicker **15d** · Roleplay / life **14d** · Anime / fighting style **12d** · Battles / army **11d**
By genre: Shooter **33d** · Social **33d** · Action **23d** · Obby & Platformer **21d**

**📏 Stickiness weights**
weekday hold 64% · players kept vs best week 31% · session length 5% — learned from 1,934 game-weeks

📥 Past histories downloaded: **1,762** games (1,826 tried)

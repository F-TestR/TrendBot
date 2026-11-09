# Model check

_Model check · 2026-11-09_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week. Bars = how much one step up in a signal raises the odds, after allowing for size, momentum and age._
🟩🟩🟩🟩 session length (+0.18)
🟩 playtime per player per day (badges) (+0.04)
🟩 like ratio (+0.02)
🟩 new players reaching the next badge (badges) (+0.01)
🟩 favourite rate (+0.00)
🟥 sessions per player per day (badges) (-0.05)
🟥 weekday hold vs a typical game (-0.05)
🟥🟥🟥 revenue per player (-0.15)
• Model for *enters a Roblox chart within 7 days*: accuracy 0.65 on days it hadn't seen (0.5 = coin flip); its top 10% were promoted 17% of the time vs 5% for all games (4978 examples).
  ⚙️ Simple model kept: walk-forward accuracy 0.72 vs 0.67 for boosted trees (trees must win by 0.01+)
• Model for *players up 50%+ within 7 days*: accuracy 0.82 on days it hadn't seen (0.5 = coin flip); its top 10% were promoted 45% of the time vs 9% for all games (5195 examples).
  ⚙️ Using **boosted trees**: walk-forward accuracy **0.84** vs 0.73 for the simple model (2,598 predictions tested in time order)
🧪 Live check, enters a Roblox chart within 7 days: past predictions scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (18501 predictions).
🧪 Live check, players up 50%+ within 7 days: past predictions scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (21294 predictions).
_Correlation from public data, not Roblox's actual model — but it tracks what its outputs reward, and the live check shows whether it works._

**⭐ Trend Score**
🚀 Trend Score (learned): accuracy **0.71** on unseen days · games scored 50+ took off 40% of the time vs 25% overall
⚙️ Using **boosted trees**: walk-forward accuracy **0.70** vs 0.67 for the simple model (268 predictions tested in time order)
Live check: scored 70+: 100% took off (2) · scored 40–69: 22% took off (18) · scored under 40: 15% took off (516)

**💥 Explosion model + alert scorecard**
🧠 **What the model has learned** (explode = 25.0K+ players within 21 days)
• Trained on 248 young games, 12 of which exploded.
• Tested on the newest 62 games it hadn't seen: ranking accuracy (AUC) **1.00** (0.5 = coin flip, 1.0 = perfect). Its top 10% picks exploded **33%** of the time vs 3% for a random young game.
• Biggest drivers: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), studio's best previous game (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: — · 619 still in their 21-day window (35 already exploded)
• chart: — · 66 still in their 21-day window (28 already exploded)
• 👀 early warning: — · 104 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 342 still in their 21-day window (36 already exploded)
• 💥 breakout: — · 158 still in their 21-day window (29 already exploded)
• 🧬 copy wave: — · 164 still in their 21-day window (14 already exploded)
• longterm: — · 45 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 18 still in their 21-day window (5 already exploded)
• abroad: — · 388 still in their 21-day window (36 already exploded)
• studio: — · 13 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 153 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a theme "breaks out" when 3+ of its games under 45 days old pass 2.0K players within 21 days)
• Trained on 4,928 theme-days, 1763 of which led to a breakout.
• On the newest data it hadn't seen: AUC **0.76**; its top 5% picks broke out **98%** of the time vs 50.2% on average.
• ⚙️ Simple model kept: walk-forward accuracy 0.77 vs 0.76 for boosted trees (trees must win by 0.01+)
• Biggest drivers: number of games (+), new games this week vs last week (−), theme growth over 7 days (+), players across the theme (−), new games this week (+)

🔬 **Which indicators actually work** (195 theme breakouts tracked so far)
• 📊 in the algorithm charts: followed by a breakout 7/7 times · **2.8×** better than chance · ~4 days' warning · caught 44% of breakouts
• 📈 theme doubled in a week: followed by a breakout 23/70 times · **0.9×** better than chance · ~8 days' warning · caught 49% of breakouts
• 🔥 YouTube trending: followed by a breakout 2/2 times · **2.8×** better than chance · ~10 days' warning · caught 9% of breakouts
• 📺 Roblox YouTube buzz: followed by a breakout 1/1 times · **2.8×** better than chance · ~12 days' warning · caught 6% of breakouts
• Not enough data yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 🎮 rising on Steam, 📚 Wikipedia spike, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **74%**; 54% within 2× of the real peak (573 games)
   ↳ not accurate enough to quote numbers yet (needs 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **18%** of the time vs 22% for any young game (208 firings) · **alerts paused** until it beats that
⏳ A typical hit keeps half its peak players for **10 days** (1668 games)
By weekday hold: holds weekday players well **23d** · average weekday hold **15d** · holds them poorly **6d**
By mechanic: Roleplay / life **14d** · Anime / fighting style **12d** · Eat / grow big **11d** · Sports **10d**
By genre: Social **33d** · Shooter **31d** · Obby & Platformer **19d** · Action **16d**

**📏 Stickiness weights**
weekday hold 61% · players kept vs best week 30% · session length 9% — learned from 2,562 game-weeks

📥 Past histories downloaded: **2,289** games (2,376 tried)
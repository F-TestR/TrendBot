# Model check

_Model check · 2026-11-08_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week. Bars = how much one step up in a signal raises the odds, after allowing for size, momentum and age._
🟩🟩🟩 session length (+0.08)
🟩 like ratio (+0.01)
🟥 new players reaching the next badge (badges) (-0.00)
🟥 playtime per player per day (badges) (-0.02)
🟥 weekday hold vs a typical game (-0.03)
🟥🟥 sessions per player per day (badges) (-0.04)
🟥🟥🟥 favourite rate (-0.09)
🟥🟥🟥🟥 revenue per player (-0.11)
• Model for *enters a Roblox chart within 7 days*: accuracy 0.68 on days it hadn't seen (0.5 = coin flip); its top 10% were promoted 11% of the time vs 6% for all games (5078 examples).
  ⚙️ Simple model kept: walk-forward accuracy 0.73 vs 0.67 for boosted trees (trees must win by 0.01+)
• Model for *players up 50%+ within 7 days*: accuracy 0.78 on days it hadn't seen (0.5 = coin flip); its top 10% were promoted 44% of the time vs 10% for all games (5267 examples).
  ⚙️ Using **boosted trees**: walk-forward accuracy **0.82** vs 0.75 for the simple model (2,634 predictions tested in time order)
🧪 Live check, enters a Roblox chart within 7 days: past predictions scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (16500 predictions).
🧪 Live check, players up 50%+ within 7 days: past predictions scored 0.78; their top 10% were promoted 34% of the time vs 8% overall (18967 predictions).
_Correlation from public data, not Roblox's actual model — but it tracks what its outputs reward, and the live check shows whether it works._

**⭐ Trend Score**
🚀 Trend Score: using its starting formula — needs 400+ outcomes with 30+ take-offs (has 0 / 0)

**💥 Explosion model + alert scorecard**
🧠 **What the model has learned** (explode = 25.0K+ players within 21 days)
• Trained on 218 young games, 11 of which exploded.
• Tested on the newest 55 games it hadn't seen: ranking accuracy (AUC) **0.99** (0.5 = coin flip, 1.0 = perfect). Its top 10% picks exploded **40%** of the time vs 4% for a random young game.
• Biggest drivers: same-mechanic games that exploded in the month before (+), copies in the same mechanic in the 2 weeks before (−), game age when noticed (−), studio's best previous game (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: — · 597 still in their 21-day window (32 already exploded)
• chart: — · 62 still in their 21-day window (27 already exploded)
• 👀 early warning: — · 100 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 323 still in their 21-day window (33 already exploded)
• 💥 breakout: — · 153 still in their 21-day window (26 already exploded)
• 🧬 copy wave: — · 153 still in their 21-day window (14 already exploded)
• longterm: — · 45 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 15 still in their 21-day window (5 already exploded)
• abroad: — · 372 still in their 21-day window (34 already exploded)
• studio: — · 10 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 139 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a theme "breaks out" when 3+ of its games under 45 days old pass 2.0K players within 21 days)
• Trained on 4,742 theme-days, 1672 of which led to a breakout.
• On the newest data it hadn't seen: AUC **0.77**; its top 5% picks broke out **97%** of the time vs 50.8% on average.
• ⚙️ Simple model kept: walk-forward accuracy 0.77 vs 0.76 for boosted trees (trees must win by 0.01+)
• Biggest drivers: number of games (+), new games this week vs last week (−), theme growth over 7 days (+), new games this week (+), different studios making it (+)

🔬 **Which indicators actually work** (192 theme breakouts tracked so far)
• 📈 theme doubled in a week: followed by a breakout 23/65 times · **1.0×** better than chance · ~8 days' warning · caught 50% of breakouts
• 📊 in the algorithm charts: followed by a breakout 7/7 times · **2.8×** better than chance · ~4 days' warning · caught 43% of breakouts
• 🔥 YouTube trending: followed by a breakout 2/2 times · **2.8×** better than chance · ~10 days' warning · caught 9% of breakouts
• 📺 Roblox YouTube buzz: followed by a breakout 1/1 times · **2.8×** better than chance · ~12 days' warning · caught 6% of breakouts
• Not enough data yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 🎮 rising on Steam, 📚 Wikipedia spike, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **74%**; 54% within 2× of the real peak (573 games)
   ↳ not accurate enough to quote numbers yet (needs 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **18%** of the time vs 22% for any young game (208 firings) · **alerts paused** until it beats that
⏳ A typical hit keeps half its peak players for **10 days** (1621 games)
By weekday hold: holds weekday players well **23d** · average weekday hold **15d** · holds them poorly **6d**
By mechanic: Battles / army **16d** · Roleplay / life **14d** · Anime / fighting style **12d** · Disasters / survival **11d**
By genre: Shooter **33d** · Social **33d** · Obby & Platformer **21d** · Action **16d**

**📏 Stickiness weights**
weekday hold 66% · players kept vs best week 29% · session length 5% — learned from 2,239 game-weeks

📥 Past histories downloaded: **1,985** games (2,057 tried)
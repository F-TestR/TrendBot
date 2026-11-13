# Diagnostics · 2026-11-13

_generated 2026-11-13T18:15:49Z · models retrained in memory only_

## Tables and coverage

- games: 8,613
- daily: 210,061
- hourly: 1,074,032
- alerts: 3,373
- predictions: 711
- backfill: 4,147
- trend_feats: 12,975
- promo_preds: 55,618
- theme_daily: 50,905
- theme_preds: 22,062
- hold_weekly: 12,460
- engage_weekly: 16,884
- fc_preds: 18,099
- cp_fires: 114
- renames: 4,420
- effects: 3,368
- upstream: 92,073
- database file: 164 MB
- daily covers 2026-07-26 → 2026-11-13 (111 days)

game-days per day, last 21 days (live / backfill / other):
- 2026-10-23: 6,030 / 300 / 22 · most readings of one game that day (≈ runs): 294
- 2026-10-24: 6,084 / 326 / 28 · most readings of one game that day (≈ runs): 295
- 2026-10-25: 6,081 / 362 / 18 · most readings of one game that day (≈ runs): 294
- 2026-10-26: 2,836 / 1,142 / 39 · most readings of one game that day (≈ runs): 301
- 2026-10-27: 2,888 / 1,111 / 39 · most readings of one game that day (≈ runs): 295
- 2026-10-28: 2,764 / 1,130 / 41 · most readings of one game that day (≈ runs): 304
- 2026-10-29: 2,790 / 1,149 / 49 · most readings of one game that day (≈ runs): 295
- 2026-10-30: 2,824 / 1,123 / 55 · most readings of one game that day (≈ runs): 295
- 2026-10-31: 2,796 / 1,144 / 64 · most readings of one game that day (≈ runs): 295
- 2026-11-01: 2,769 / 1,175 / 70 · most readings of one game that day (≈ runs): 295
- 2026-11-02: 2,797 / 1,143 / 101 · most readings of one game that day (≈ runs): 295
- 2026-11-03: 2,790 / 1,191 / 113 · most readings of one game that day (≈ runs): 98
- 2026-11-04: 2,848 / 1,160 / 117 · most readings of one game that day (≈ runs): 161
- 2026-11-05: 2,823 / 1,157 / 136 · most readings of one game that day (≈ runs): 307
- 2026-11-06: 2,825 / 1,083 / 143 · most readings of one game that day (≈ runs): 304
- 2026-11-07: 2,712 / 989 / 165 · most readings of one game that day (≈ runs): 306
- 2026-11-08: 2,721 / 888 / 197 · most readings of one game that day (≈ runs): 305
- 2026-11-09: 2,911 / 763 / 208 · most readings of one game that day (≈ runs): 299
- 2026-11-10: 3,131 / 643 / 219 · most readings of one game that day (≈ runs): 301
- 2026-11-11: 3,093 / 439 / 239 · most readings of one game that day (≈ runs): 301
- 2026-11-12: 3,159 / 212 / 196 · most readings of one game that day (≈ runs): 301
- 2026-11-13: 3,211 / 48 / 0 · most readings of one game that day (≈ runs): 195
- alerts: 2026-10-22 → 2026-11-13 (23 distinct)
- trend_feats: 2026-10-26 → 2026-11-13 (19 distinct)
- promo_preds: 2026-10-24 → 2026-11-13 (21 distinct)
- theme_daily: 2026-08-25 → 2026-11-12 (80 distinct)
- hold_weekly: 2026-09-02 → 2026-11-11 (11 distinct)
- engage_weekly: 2026-09-02 → 2026-11-11 (11 distinct)

state.json: 6.1 MB · biggest keys:
- games: 3.07 MB
- src: 1.33 MB
- rbx_direct: 0.74 MB
- icon_changes: 0.22 MB
- upstream: 0.21 MB
- hold: 0.17 MB
- icons: 0.14 MB
- ins: 0.13 MB
- stick: 0.13 MB
- alert_queue: 0.11 MB
- alerts: 0.08 MB
- rw_trends: 0.07 MB

_0.1s_

## How often games are really read

readings per game on 2026-11-12 (10th / 25th / median / 75th / 90th percentile), by the game's daily high:
- <500: 428 games · 2 / 8 / 19 / 22 / 23 · 11% have under 3 readings
- 500–2K: 1,649 games · 3 / 8 / 17 / 21 / 23 · 8% have under 3 readings
- 2K–10K: 888 games · 19 / 20 / 23 / 23 / 23 · 0% have under 3 readings
- 10K+: 194 games · 23 / 23 / 23 / 23 / 23 · 1% have under 3 readings

hour-adjusted daily average ÷ daily high (games with 8+ readings) — the code assumes 0.75 when a day has under 3 readings:
- <500: median 0.64 (321 games)
- 500–2K: median 0.73 (1255 games)
- 2K–10K: median 0.69 (878 games)
- 10K+: median 0.71 (192 games)

_0.0s_

## Alerts, updates, breakouts

alerts by kind: total · first day · last day · last 7 days
- surge: 872 · 2026-10-23 · 2026-11-13 · 422
- new: 772 · 2026-10-22 · 2026-11-13 · 280
- abroad: 723 · 2026-10-26 · 2026-11-13 · 359
- copy: 340 · 2026-10-23 · 2026-11-13 · 186
- early: 190 · 2026-10-22 · 2026-11-13 · 87
- breakout: 184 · 2026-10-23 · 2026-11-13 · 65
- chart: 90 · 2026-10-22 · 2026-11-13 · 33
- update: 63 · 2026-10-22 · 2026-11-13 · 34
- longterm: 57 · 2026-10-24 · 2026-11-12 · 11
- heat: 48 · 2026-10-25 · 2026-11-13 · 25
- studio: 25 · 2026-10-28 · 2026-11-13 · 16
- predict: 9 · 2026-10-30 · 2026-11-08 · 1

update events kept in memory: 400 (cap 400) · with a day-3 result: 3 · dates 2026-11-01 → 2026-11-13
icon/title changes in memory: 1993 · kinds: {"icon": 660, "title": 1333}
breakouts logged: 205 · days from breakout to peak, all: 0 / 0 / 1 / 4 / 8 · only those 14+ days old (92): 0 / 0 / 1 / 7 / 9

_0.0s_

## Plumbing: runs, alert cards, sources, backup

last full run: 2026-11-13T17:50:30.498996+00:00 · RoWatcher requests by day: {"2026-11-10": 950, "2026-11-11": 915, "2026-11-12": 939, "2026-11-13": 705}
alert cards by day: {"2026-11-10": 17, "2026-11-11": 14, "2026-11-12": 13, "2026-11-13": 12} · pings: {"2026-11-10": 6, "2026-11-11": 6, "2026-11-12": 6, "2026-11-13": 6}
alerts waiting for a slot: 128 · strongest: 0.61 🚀 Trend Score 52: [BETA] My Career - Be ; 0.46 📈 Entered Roblox's algorithm charts: Jum; 0.38 🚀 Trend Score 46: Ragdoll Soccer; 0.38 🚀 Trend Score 46: [UPD] Blood Lab; 0.35 🚀 Trend Score 40: Bobby's Daycare [HORRO
yesterday's alert priorities: 306 alerts · top 12th = 0.648 · 0.055 / 0.08 / 0.12 / 0.273 / 0.399

alert type → chance it's followed by an explosion (starting guess → now, matured alerts behind it):
- chart: 0.350 → 0.375 (4 matured)
- predict: 0.350 → 0.350 (0 matured)
- trend: 0.300 → 0.300 (0 matured)
- heat: 0.250 → 0.250 (0 matured)
- studio: 0.200 → 0.200 (0 matured)
- cp: 0.200 → 0.200 (0 matured)
- theme: 0.200 → 0.200 (0 matured)
- breakout: 0.180 → 0.180 (0 matured)
- bridge: 0.150 → 0.150 (0 matured)
- future: 0.150 → 0.150 (0 matured)
- longterm: 0.120 → 0.120 (0 matured)
- surge: 0.100 → 0.100 (0 matured)
- abroad: 0.090 → 0.090 (0 matured)
- copy: 0.080 → 0.080 (0 matured)
- early: 0.040 → 0.067 (7 matured)
- update: 0.050 → 0.050 (0 matured)
- new: 0.055 → 0.037 (37 matured)

outside sources last worked: {"steam": "2026-11-13T00:05:05.465585+00:00", "wikipedia": "2026-11-13T04:22:13.598779+00:00", "calendar": "2026-11-13T00:05:05.465585+00:00", "yt_trending": "2026-11-13T12:39:51.425625+00:00"}
outside sources failing today: {} · Wikipedia days held: ['2026-11-08', '2026-11-09', '2026-11-10', '2026-11-11', '2026-11-12']
backfill by status: {"error:1": 59, "error:2": 77, "error:3": 83, "ok": 3096, "ok-old": 818, "ok2": 14}
worldwide trending lists last read: 2026-11-13T16:53:31.632579+00:00 · games in them: 139 · theme words saved for search: ['zero', 'real', 'rob', 'chase', 'adventures', 'mine', 'voice', 'pass', 'fighter', 'dead', 'toilet', 'blood', 'monkey', 'night', 'cozy']
title tags currently treated as Roblox events: {"the hollow": "2026-10-26"}
backup: encrypted backup saved (45.6 MB)

_0.0s_

## Digest and weekly cards, built from today's data (not posted)

daily digest: 5 cards built — 📊 Daily digest · Fri 13 Nov · 🎮 Games to watch · 🌱 Trends · 🔮 Coming up & outside Roblox · 👀 Watchlist

weekly report: 9 cards built — 🗓️ Weekly report · week to Fri 13 Nov · 🧭 Mechanics: biggest moves · 🧠 What Roblox's algorithm is rewarding · 🏛️ Long-term games · ⏱ Engagement (from badges) · 🧩 What lasting games have in common · 📈 Forecasts & how long hits last · 🛠️ Do updates, icons and titles help? · 🔬 Are the predictions working?

**📊 Daily digest · Fri 13 Nov**
🚀 **Biggest riser:** [Ragdoll Soccer](https://www.roblox.com/games/106931373443671) — ×58.9 to 48.9K
🔥 **Hottest across platforms:** [Throw Food For Animals](https://www.roblox.com/games/120219252362013) — heat 77
⏱ **Most playtime per player:** [Project Soul's (Undertale RPG)](https://rowatcher.com/games/10768613071) — 104 min/day
🔮 **Coming up:** A Dog's Perfect Christmas (out 9 days ago) — 🌉 1 new Roblox game already
⚠️ **Watchlist falling:** Eat Everything In A Grocery Store -76% week on week
📥 **Also flagged** (didn't make the day's 12 alert cards; strongest first): 🚀 Trend Score 99: [🎃] Dead Signal; 🚀 Trend Score 97: [ATTACHMENTS] Ragdoll Realism; 🚀 Trend Score 97: Build a Bridge; 🚀 Trend Score 97: [🌍] World War Sandbox; 🚀 Trend Score 95: Volley Bomb (+75 more)
🎃 **After Halloween:** 10% of games still carry Halloween tags. The event is over, so week-on-week falls right now are mostly that event unwinding, not games failing

**🎮 Games to watch**
**[Impossible Hill Climb](https://www.roblox.com/games/100981917200669)** — 13.5K playing · 19d old · **×6.2** 🔥69
**[Run a Motel ! (EXPAND)](https://www.roblox.com/games/82046305882496)** — 7.4K playing · 26d old · **×4.8** 🔥69
**[ SF BIKE (NEW BIKES) ](https://www.roblox.com/games/133214978843288)** — 14.1K playing · 32d old · **×10.7** 🔥67
**[(UPD) Malam Sama Kembar](https://www.roblox.com/games/95525762235977)** — 665 playing · 14d old · **×4.6** 🔥67 ⏱33m 📺115.6K
**[Unstable SMP FFA (JAVA PVP!)](https://www.roblox.com/games/76870565041704)** — 43.9K playing · 23d old · **×8.5** 🔥63
**[Sweep The Moon 🌕](https://www.roblox.com/games/109576450376407)** — 35.5K playing · 21d old · **×5.4** 🔥61 ⏱94m
**[Jump for Cases🎲](https://www.roblox.com/games/93545804988403)** — 13.9K playing · 52d old · **×8.3** 🔥58 ⏱68m
**[(🐟) Net a Fish!](https://www.roblox.com/games/93898234979111)** — 29.7K playing · 29d old · **×5.0** 🔥58

**🗓️ Weekly report · week to Fri 13 Nov**
🎃 **After Halloween:** 10% of games still carry Halloween tags. The event is over, so week-on-week falls right now are mostly that event unwinding, not games failing
🧭 **Demand:** Disasters / survival +20% · Anomaly / night shift -27%
🏛️ **Most long-term genre:** Social — 68% of its games reliably hold players on weekdays (all genres: 14%)
📏 **Stickiest young game:** [Roll Pets to Fight](https://rowatcher.com/games/10770739222) — 90/100
⏱ **Most playtime (young):** [ABOVE (💀RUINS)](https://www.roblox.com/games/124357835578554) — 152 min/player/day

**🧭 Mechanics: biggest moves**
🔴 **Anomaly / night shift** · 302.4K (-27%) · 9 new · 1 hit
🔴 **Care / baby / pets** · 491.7K (-25%) · 10 new · 1 hit
🔴 **Find / search** · 32.9K (-24%) · 2 new
🟡 **Disasters / survival** · 288.1K (+20%) · 22 new · 1 hit
🔴 **Anime / fighting style** · 923.3K (-17%) · 20 new · 3 hits
🔴 **Eat / grow big** · 73.6K (-17%) · 8 new · 1 hit
💥 72 breakouts: [Hyper Realistic Ragdo…](https://www.roblox.com/games/101277003916102), [Sweep The Moon 🌕](https://www.roblox.com/games/109576450376407), [Ragdoll Soccer](https://www.roblox.com/games/106931373443671)

**🧠 What Roblox's algorithm is rewarding**
🟥🟥🟥🟥🟥🟥 revenue per player — _fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation_
🧪 enters a Roblox chart within 7 days: predictions the bot made scored **0.65** · top 10% came true 16% vs 6.8% overall
🧪 players up 50%+ within 7 days: predictions the bot made scored **0.79** · top 10% came true 32% vs 7.5% overall

**🏛️ Long-term games**
Weekday hold is 75% the game, 25% week-to-week noise — so one good week proves little
**Social** · 68% long-term (17/25, likely 52%–81%) ✅
**RPG** · 27% long-term (12/44, likely 18%–39%) ✅
**Sports & Racing** · 26% long-term (12/46, likely 17%–38%) ✅
**Puzzle** · 25% long-term (5/20, likely 13%–43%)
**Simulation** · 14% long-term (86/608, likely 12%–17%)
Young games already long-term: [Free Fire Zone (Max)](https://www.roblox.com/games/99610146753435), [🚨(QUADS) Bike Universe](https://www.roblox.com/games/98628861455414), [Ragdoll Engine ⚙️](https://www.roblox.com/games/112332082095944)
Stickiest young games: [Roll Pets to Fight](https://rowatcher.com/games/10770739222) (90), [(⛩️RAIDS) Anime Auto …](https://rowatcher.com/games/10770014246) (90), [(👽) Steal a PC ](https://www.roblox.com/games/135402322419238) (88)

**⏱ Engagement (from badges)**
Typical game: **51 min** per player per day (313 games measured)
⏱ [ABOVE (💀RUINS)](https://www.roblox.com/games/124357835578554) · **152 min** · 35.0K/day
⏱ [Project Soul's (Undertale RPG)](https://rowatcher.com/games/10768613071) · **104 min** · 34.1K/day
⏱ [Escape The Matrix](https://www.roblox.com/games/90088244419227) · **104 min** · 51.1K/day
⏱ [+1 Assassin Leveling](https://www.roblox.com/games/120731410233153) · **104 min** · 75.8K/day

**🧩 What lasting games have in common**
✅ leaderboards · **2.3×** as likely to be long-term (likely 1.5–3.5×, 103 games)
✅ codes · **1.6×** as likely to be long-term (likely 1.1–2.4×, 192 games)
🧪 Stickiness can't be checked against survival until 2026-11-25 (needs games watched from the start, 4 weeks on)

**📈 Forecasts & how long hits last**
📈 Peak forecasts (made on day 5): typically off by **115%**; 45% within 2× of the real peak (76 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **11%** of the time vs 17% for any young game (64 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **9 days** (1148 games that peaked while the bot was watching; 613 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **15d** (163) · holds weekday players well **12d** (222) · holds them poorly **3d** (35)
By mechanic: Roleplay / life **10d** (51) · Tycoon / sell stuff **9d** (33) · Sports **9d** (32) · RNG / gacha / luck **9d** (30)
By genre: Obby & Platformer **16d** (82) · Shooter **14d** (35) · Action **12d** (82) · Roleplay & Avatar Sim **11d** (66)

**🛠️ Do updates, icons and titles help?**
▫️ **Updates after a quiet week**: -6% (likely -11% to +2%) vs similar games that changed nothing · 25% beat them by 10%+ (57 measured)
✅ **Icon changes**: +8% (likely +3% to +12%) vs similar games that changed nothing · 46% beat them by 10%+ (215 measured)
▫️ **Title changes**: +0% (likely -1% to +2%) vs similar games that changed nothing · 38% beat them by 10%+ (1672 measured)
🖼️ 7 young games use an icon nearly identical to a hit from another studio (last 30 days)

**🔬 Are the predictions working?**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.73–0.81) · its top 10% took off 28% of the time vs 8.1% for all · 2,708 snapshots over 5 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 2708 / 219 over 5 days)
🎯 Explosion model: not provable yet (too few finished explosions among games watched live) — its picks aren't used
🌱 Theme model: still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20)

_5.5s_

## Trend Score

snapshots old enough to score: 3,032 over 5 days (2026-10-26 → 2026-10-30)

take-off rate by size at the time of the snapshot (took off / snapshots):
| definition | <500 | 500–2K | 2K–10K | 10K+ | all |
|---|---|---|---|---|---|
| old (2× and 1,000, one day) | 59/147 (40.1%) | 294/1378 (21.3%) | 162/986 (16.4%) | 22/208 (10.6%) | 537/2719 (19.7%) |
| 2× and 5,000, one day | 9/147 (6.1%) | 79/1378 (5.7%) | 153/986 (15.5%) | 22/208 (10.6%) | 263/2719 (9.7%) |
| NEW (2× and 5,000, two days) | 8/147 (5.4%) | 63/1378 (4.6%) | 130/986 (13.2%) | 18/208 (8.7%) | 219/2719 (8.1%) |
| 2× and 2,000, two days | 26/147 (17.7%) | 195/1378 (14.2%) | 136/986 (13.8%) | 18/208 (8.7%) | 375/2719 (13.8%) |

starting formula vs the NEW outcome: {"n": 2719, "pos": 219, "auc": 0.774, "base": 0.081, "top": 0.28, "top_n": 271, "lo": 0.731, "hi": 0.818}
scores as shown at the time vs the NEW outcome: AUC 0.774
- shown 50–100: 60/218 took off (28%)
- shown 25–50: 49/205 took off (24%)
- shown 10–25: 34/256 took off (13%)
- shown 0–10: 76/2040 took off (4%)
starting-formula raw scores (10/25/50/75/90th pct): 0.00743 / 0.012 / 0.025 / 0.0997 / 0.435
calibration of the starting formula: {"n": 2719, "pos": 219, "days": 5, "cal": {"a": 0.46441372320222274, "b": -1.3007475489645004}, "auc": 0.774, "lo": 0.731, "hi": 0.818, "base": 0.081, "top": 0.28}
learned model status: {"day": "2026-11-13", "examples": 2719, "positives": 219, "days": 5, "trained": false, "why": "needs 2000+ outcomes with 60+ take-offs over 21+ days (has 2719 / 219 over 5 days)"}

_3.4s_

## Weekday hold: old vs new definition

**OLD: Tue–Wed vs Sat–Sun** — games rated: 2,840 · weeks rated per game: 1 / 1 / 3 / 6 / 8 · week-to-week rank correlation: 0.494 (7,118 pairs) · share of one week's spread that is the game itself: 0.734 · noise sd 0.228 · old-rule 'long-term': 579 of 2061 with 2+ weeks (28%)
**NEW: Mon–Wed vs two busiest of Fri–Sun** — games rated: 2,893 · weeks rated per game: 1 / 1 / 3 / 6 / 8 · week-to-week rank correlation: 0.502 (7,148 pairs) · share of one week's spread that is the game itself: 0.752 · noise sd 0.214 · old-rule 'long-term': 586 of 2084 with 2+ weeks (28%)

games the OLD measure flattered most (old ÷ new relative hold):
- Hide ur Secret Base — ×3.91 (2 weeks)
- Fat And Skinny [ 2 Player Obby ] — ×2.44 (2 weeks)
- SUNYI [HORROR] — ×2.22 (2 weeks)
- Where is Sara? 🔦😨 — ×2.21 (2 weeks)
- [🎃] Shoot For Eggs — ×1.69 (2 weeks)
- British Railway — ×1.54 (2 weeks)
- [🎲] The Game Of Life — ×1.51 (2 weeks)
- Sarab — ×1.48 (5 weeks)
- [UPD🎃] Climb for Eggs! — ×1.47 (3 weeks)
- الشايب [رعب] — ×1.45 (2 weeks)
- [⚔️] Steal a Nito — ×1.45 (2 weeks)
- [UP] Keyboard Slide +1 Speed — ×1.43 (7 weeks)

after the new rule: hold_meta {"week": "2026-11-11", "weekend": ["2026-11-07", "2026-11-08"], "weekday": ["2026-11-10", "2026-11-11"], "benchmark": 0.638, "roblox": 0.669, "weeks": 8, "reliability": 0.752, "noise_sd": 0.214} · long-term 213 · promising 327
- [🌎W10] Throw a Coin — 1.593× over 8 weeks (z 6.42) · 3.8K
- [🍂] Anime Dice — 1.578× over 8 weeks (z 6.29) · 78.2K
- TANPANAMA — 1.549× over 8 weeks (z 6.03) · 4.3K
- [UPD 12] Defeat Anime RNG  — 1.527× over 8 weeks (z 5.83) · 6.4K
- [EVENT🎃] Noob Incremental — 1.49× over 8 weeks (z 5.5) · 5.5K
- Forest Market — 1.471× over 8 weeks (z 5.32) · 3.7K
- [UPD] Anime RNG Defense — 1.462× over 8 weeks (z 5.23) · 3.0K
- Free Fire Zone (Max) — 1.655× over 4 weeks (z 5.1) · 9.6K
- Collect All Pets! — 1.435× over 8 weeks (z 4.98) · 3.4K
- Sol's RNG [ Halloween Event 🎃] — 1.428× over 8 weeks (z 4.91) · 43.1K
- [🌙UPD] Fish It! 🐟 — 1.417× over 8 weeks (z 4.81) · 92.8K
- Bee Swarm Simulator — 1.417× over 8 weeks (z 4.8) · 33.9K

_2.7s_

## What changes do (matched comparison)

games watched for publishes: 969 · publish days seen: 2,921 · publishes after a quiet week: 114
naive measure (day+3 vs the 3 days before), every publish: median -18.2% over 1,439 · by weekday of the publish: Mon -42% (216), Tue -31% (253), Wed +14% (178), Thu +20% (110), Fri -14% (119), Sat -15% (337), Sun -22% (226)
measured now: 0 changes
- icon: 362 events · 321 with complete weeks · 215 with enough twins
- title: 2917 events · 1863 with complete weeks · 1672 with enough twins
- update: 89 events · 85 with complete weeks · 57 with enough twins
• ▫️ **Updates after a quiet week**: typical lift **-6%** (likely -11% to +2%) vs similar games that changed nothing · 25% beat their twins by 10%+, 40% fell 10%+ behind · 57 measured
   ↳ the games themselves went -23% week on week while their twins went -16% — the naive before/after number is mostly that drift
   ↳ biggest: [MARS] Clean the Moon! (+172%), MOUSE 🐭 (+169%), 🎃 [Pokemon Brick Bronze] P (+131%)
• ✅ **Icon changes**: typical lift **+8%** (likely +3% to +12%) vs similar games that changed nothing · 46% beat their twins by 10%+, 36% fell 10%+ behind · 215 measured
   ↳ the games themselves went -23% week on week while their twins went -26% — the naive before/after number is mostly that drift
• ▫️ **Title changes**: typical lift **+0%** (likely -1% to +2%) vs similar games that changed nothing · 38% beat their twins by 10%+, 36% fell 10%+ behind · 1672 measured
   ↳ the games themselves went -12% week on week while their twins went -11% — the naive before/after number is mostly that drift
_Lift = the game's week-on-week change divided by the median change of similar-size, similar-trend games that made no such change. Correlation still, but weekdays, natural decay and market swings are removed._

_1.0s_

## Themes

themes: 3,077 · calm candidate days: 33,892 · breakouts: 146 in 146 themes · history starts 2026-08-25
themes that broke out (count · name · most games): 1× wars (26); 1× walls escape (3); 1× walls (8); 1× voxel (9); 1× verity (32); 1× together (17); 1× throw (12); 1× thai (8); 1× tesla (4); 1× survival (43); 1× steal eggs (9); 1× steal egg (18); 1× showdown (12); 1× sell (18); 1× scooter (10); 1× say (3); 1× save (16); 1× sandbox (23); 1× roadster (4); 1× ride (46); 1× realistic (23); 1× ragdoll physics (7); 1× punch (8); 1× prison (69); 1× playground (20)

model status: {"examples": 0, "positives": 0, "trained": false, "day": "2026-11-13", "themes": 0, "base_rate": null, "why": "needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20)"}

top themes it would show today:
- zero — model None · 4 signals · 8 games, 2 hits, 0 young hits, 0 new
- real — model None · 4 signals · 4 games, 2 hits, 1 young hits, 0 new
- rob — model None · 4 signals · 8 games, 2 hits, 0 young hits, 0 new
- chase — model None · 3 signals · 2 games, 1 hits, 1 young hits, 0 new
- adventures — model None · 3 signals · 4 games, 2 hits, 0 young hits, 0 new
- mine — model None · 3 signals · 10 games, 1 hits, 0 young hits, 0 new
- voice — model None · 3 signals · 9 games, 2 hits, 0 young hits, 0 new
- pass — model None · 3 signals · 5 games, 1 hits, 1 young hits, 0 new
- fighter — model None · 3 signals · 5 games, 1 hits, 1 young hits, 0 new
- dead — model None · 3 signals · 14 games, 1 hits, 0 young hits, 0 new
- toilet — model None · 3 signals · 6 games, 2 hits, 0 young hits, 0 new
- blood — model None · 3 signals · 3 games, 1 hits, 1 young hits, 0 new

🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20).

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

_3.3s_

## Algorithm mirror

**chart**: 1,836 game-days over 13 days (2026-10-24 → 2026-11-05) · 90 positive (4.9%) · games: 1,367
**growth**: 4,915 game-days over 28 days (2026-10-09 → 2026-11-05) · 516 positive (10.5%) · games: 2,539

chart: coverage {"playtime": 0.025, "returning": 0.0, "first_step": 0.009, "sessions": 0.024, "hold": 0.538, "session_len": 0.974, "like_ratio": 0.874, "fav_conv": 0.826, "rev_per_player": 0.818, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
chart: stability {"playtime": {"w": -0.182, "lo": -0.365, "hi": 0.027, "sign": 0.933}, "first_step": {"w": 0.004, "lo": -0.13, "hi": 0.232, "sign": 0.517}, "sessions": {"w": 0.174, "lo": 0.001, "hi": 0.336, "sign": 0.95}, "hold": {"w": 0.066, "lo": -0.129, "hi": 0.193, "sign": 0.767}, "session_len": {"w": 0.23, "lo": 0.055, "hi": 0.476, "sign": 0.967}, "like_ratio": {"w": 0.394, "lo": 0.187, "hi": 0.679, "sign": 1.0}, "fav_conv": {"w": -0.364, "lo": -0.625, "hi": -0.192, "sign": 1.0}, "rev_per_player": {"w": -0.375, "lo": -0.554, "hi": -0.213, "sign": 1.0}, "size": {"w": 0.812, "lo": 0.636, "hi": 1.068, "sign": 1.0}, "momentum": {"w": 0.189, "lo": 0.01, "hi": 0.458, "sign": 0.95}, "age": {"w": -0.279, "lo": -0.462, "hi": -0.035, "sign": 0.983}, "has_badges": {"w": 0.142, "lo": 0.004, "hi": 0.234, "sign": 0.967}}
chart: wf {"folds": 0, "horizon": 8, "test_from": null}

growth: coverage {"playtime": 0.062, "returning": 0.0, "first_step": 0.024, "sessions": 0.06, "hold": 0.54, "session_len": 0.962, "like_ratio": 0.903, "fav_conv": 0.858, "rev_per_player": 0.848, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
growth: stability {"playtime": {"w": -0.171, "lo": -0.336, "hi": 0.0, "sign": 0.95}, "first_step": {"w": 0.014, "lo": -0.055, "hi": 0.116, "sign": 0.683}, "sessions": {"w": 0.094, "lo": -0.06, "hi": 0.305, "sign": 0.867}, "hold": {"w": -0.013, "lo": -0.122, "hi": 0.087, "sign": 0.767}, "session_len": {"w": 0.019, "lo": -0.128, "hi": 0.143, "sign": 0.55}, "like_ratio": {"w": 0.136, "lo": 0.047, "hi": 0.275, "sign": 1.0}, "fav_conv": {"w": -0.047, "lo": -0.137, "hi": 0.047, "sign": 0.667}, "rev_per_player": {"w": -0.324, "lo": -0.518, "hi": -0.079, "sign": 1.0}, "size": {"w": -0.301, "lo": -0.439, "hi": -0.176, "sign": 1.0}, "momentum": {"w": 0.857, "lo": 0.782, "hi": 1.028, "sign": 1.0}, "age": {"w": -0.472, "lo": -0.635, "hi": -0.325, "sign": 1.0}, "has_badges": {"w": 0.057, "lo": -0.143, "hi": 0.212, "sign": 0.633}}
growth: wf {"folds": 4, "horizon": 8, "test_from": null, "lr": {"n": 2389, "pos": 229, "auc": 0.469, "base": 0.0959, "top": 0.0504, "top_n": 238, "lo": 0.4383, "hi": 0.5055}, "gbm": {"n": 2389, "pos": 229, "auc": 0.8064, "base": 0.0959, "top": 0.4202, "top_n": 238, "lo": 0.7798, "hi": 0.8358}, "p_trees_better": 1.0, "diff": 0.3389}
- chart, 0-day purge: simple 0.756 · trees 0.788 · n 1191 · folds 4
- chart, 8-day purge: simple None · trees None · n None · folds 0
- growth, 0-day purge: simple 0.729 · trees 0.812 · n 3929 · folds 4
- growth, 8-day purge: simple 0.469 · trees 0.806 · n 2389 · folds 4

🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩🟩🟩 like ratio (+0.27)
🟥🟥🟥🟥 revenue per player (-0.35) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): sessions per player per day, session length, weekday hold vs a typical game, new players reaching the next badge, playtime per player per day, favourite rate
• Model for *enters a Roblox chart within 7 days* (1,836 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (4,915 game-days): Honest test: accuracy **0.81** (likely between 0.78 and 0.84) · 0.5 = coin flip · top 10% picks came true **42%** of the time vs 10% for all · 2,389 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.81 vs 0.47 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.65; their top 10% were promoted 16% of the time vs 7% overall (26,754 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.79; their top 10% were promoted 32% of the time vs 7% overall (30,883 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

_13.3s_

## Explosion model

examples: 425 · exploded: 17 · first noticed on a backfilled day (before the bot watched): 416 (17 exploded) vs live: 9 (0 exploded)
first-noticed dates: 2026-08-08 → 2026-10-22 · by month: {"2026-08": [34, 1], "2026-09": [107, 6], "2026-10": [284, 10]}
log10(peak after ÷ players the day after noticing): 0.0532 / 0.174 / 0.451 / 0.779 / 1.13
status: {"examples": 425, "positives": 17, "trained": true, "day": "2026-11-13", "live_examples": 11, "live_positives": 0, "champion": "simple", "wf": {"folds": 0, "horizon": 21, "test_from": "2026-10-22"}, "test_n": null, "test_pos": null, "test_top10_hit": null, "base_rate": 0.04, "stable": ["players_d0", "players_d1", "growth_d1", "visits_d1", "late_missing", "age", "crowd", "mech_hits"]}

🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 425 young games, 17 of which exploded (4%). Only 11 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: not possible yet — it is run only on games the bot watched from the start (2026-10-22 on), and their 21-day outcomes only began finishing on 2026-11-13. It needs 10+ explosions among them.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), players the day after (+), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), visits gained on day 1 (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **1/37** (3%) · 734 still in their 21-day window (42 already exploded)
• 👀 early warning: **1/7** (14%) · 122 still in their 21-day window (4 already exploded)
• chart: **2/4** (50%) · 86 still in their 21-day window (35 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 465 still in their 21-day window (44 already exploded)
• 💥 breakout: — · 184 still in their 21-day window (38 already exploded)
• 🧬 copy wave: — · 241 still in their 21-day window (18 already exploded)
• longterm: — · 56 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 25 still in their 21-day window (6 already exploded)
• abroad: — · 499 still in their 21-day window (44 already exploded)
• studio: — · 25 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 259 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

_3.4s_

## Stickiness and lasting features

games scored: 2725 · weights {"hold_rel": 0.3, "playtime": 0.2, "session_min": 0.15, "level_kept": 0.15, "fav_conv": 0.1, "rev_per_ccu": 0.1} · per-signal rank correlation with players kept 4 weeks later: {} · n 0 · honest cross-check null
description features: 213 long-term vs 1327 others · checked 16
- leaderboards: lift 2.38 (1.55–3.64) · 103 games · reliable: True
- codes: lift 1.62 (1.08–2.44) · 192 games · reliable: True
- pets / collecting: lift 1.37 (0.95–1.97) · 330 games · reliable: False
- offline / idle earnings: lift 1.32 (0.76–2.29) · 112 games · reliable: False
- quests / missions: lift 1.27 (0.67–2.37) · 87 games · reliable: False
- trading: lift 1.41 (0.67–2.99) · 52 games · reliable: False
- group rewards: lift 0.94 (0.6–1.47) · 259 games · reliable: False
- limited events: lift 1.06 (0.56–2.0) · 103 games · reliable: False
- daily rewards / streaks: lift 1.41 (0.54–3.68) · 31 games · reliable: False
- rebirth / prestige: lift 1.09 (0.54–2.21) · 80 games · reliable: False
- base building / decorating: lift 0.83 (0.52–1.3) · 280 games · reliable: False
- PvP: lift 1.03 (0.51–2.1) · 84 games · reliable: False

_2.5s_

## Money: top earners under 5K players

games with earnings: 2,677 · $/player/month percentiles: 1.68 / 9.61 / 23.8 / 60.7 · flagged as suspect: 29
- The Hollow — $680,595/month · 970 players · $702/player · suspect: True
- [🎵] +1 Stone Skipping — $298,469/month · 4437 players · $67/player · suspect: True
- [🎃]+1 Loot To Forge — $254,600/month · 3293 players · $77/player · suspect: True
- [🍲] Karinderya! — $243,089/month · 4276 players · $57/player · suspect: False
- Paint to Get Rich 🎨 — $238,148/month · 4520 players · $53/player · suspect: False
- Sarab — $224,992/month · 3488 players · $65/player · suspect: True
- Build a Keyboard! — $192,294/month · 4994 players · $39/player · suspect: False
- Build An Ant Empire — $187,750/month · 1761 players · $107/player · suspect: True

_0.2s_

## Badge streaks

games with badge data: 313 · with a 7-day streak badge: 14
- [GAMEMODES!] Illegal Soccer: [7, 0.1607] · base: players who earn "First Tackle"
- 7 Days Cat-Sitting: [10, 0.001] · base: players who earn "Haunted House"
- Firefighting Sim 🚒: [7, 0.035] · base: players who earn "First Alarm"
- [UPD🌀] UNDERTALE Fight!: [7, 0.0005] · base: players who earn "PLAY UNDERTALE FIGHT!"
- Pet Store Tycoon: [7, 0.0981] · base: new players
- Punch Out Of Prison: [7, 0.0016] · base: new players
- The Block: [5, 0.0] · base: players who earn "Best Audience Award"
- Become the Potato!: [7, 0.0] · base: new players
- [UPD 2] Crack THE Geode!: [7, 0.0003] · base: new players
- Draw an aquarium: [7, 0.0] · base: players who earn "My First Fish"
- Untitled Symbiote Suit Game [VENOM]: [7, 0.0] · base: players who earn "Bonded"
- Clean The Bugs 🐜: [7, 0.0] · base: new players
- Sleepover (Story) 🤫: [7, 0.0] · base: new players
- 🤡 Class Clowns: [7, 0.0] · base: new players

_0.0s_

## Model check as the bot would now print it

_Model check · 2026-11-13_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟩🟩🟩 like ratio (+0.27)
🟥🟥🟥🟥 revenue per player (-0.35) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): sessions per player per day, session length, weekday hold vs a typical game, new players reaching the next badge, playtime per player per day, favourite rate
• Model for *enters a Roblox chart within 7 days* (1,836 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (4,915 game-days): Honest test: accuracy **0.81** (likely between 0.78 and 0.84) · 0.5 = coin flip · top 10% picks came true **42%** of the time vs 10% for all · 2,389 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.81 vs 0.47 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.65; their top 10% were promoted 16% of the time vs 7% overall (26,754 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.79; their top 10% were promoted 32% of the time vs 7% overall (30,883 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.77** (likely 0.73–0.82) · its top 10% took off 28% of the time vs 8.1% for all · 2,719 snapshots over 5 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 2719 / 219 over 5 days)
• Scores as shown at the time: 50+: 28% took off (218) · 25–49: 24% took off (205) · 10–24: 13% took off (256) · under 10: 4% took off (2040)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 425 young games, 17 of which exploded (4%). Only 11 of them (0 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: not possible yet — it is run only on games the bot watched from the start (2026-10-22 on), and their 21-day outcomes only began finishing on 2026-11-13. It needs 10+ explosions among them.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), players the day after (+), copies in the same mechanic in the 2 weeks before (−), (no hourly data) (+), visits gained on day 1 (−)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **1/37** (3%) · 734 still in their 21-day window (42 already exploded)
• 👀 early warning: **1/7** (14%) · 122 still in their 21-day window (4 already exploded)
• chart: **2/4** (50%) · 86 still in their 21-day window (35 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 465 still in their 21-day window (44 already exploded)
• 💥 breakout: — · 184 still in their 21-day window (38 already exploded)
• 🧬 copy wave: — · 241 still in their 21-day window (18 already exploded)
• longterm: — · 56 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 25 still in their 21-day window (6 already exploded)
• abroad: — · 499 still in their 21-day window (44 already exploded)
• studio: — · 25 still in their 21-day window (2 already exploded)
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

📥 Past histories downloaded: **3,928** games (4,147 tried)

_4.4s_
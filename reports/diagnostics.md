# Diagnostics · 2026-11-28

_generated 2026-11-28T01:50:24Z · models retrained in memory only_

## Tables and coverage

- games: 9,727
- daily: 302,107
- hourly: 1,378,354
- alerts: 7,396
- predictions: 2,195
- backfill: 5,692
- trend_feats: 25,752
- promo_preds: 91,895
- theme_daily: 72,965
- theme_preds: 30,875
- hold_weekly: 18,623
- engage_weekly: 25,026
- fc_preds: 38,725
- cp_fires: 299
- renames: 7,340
- effects: 6,465
- upstream: 159,275
- database file: 225 MB
- daily covers 2026-07-26 → 2026-11-27 (125 days)

game-days per day, last 21 days (live / backfill / other):
- 2026-11-07: 2,712 / 1,489 / 120 · most readings of one game that day (≈ runs): 306
- 2026-11-08: 2,721 / 1,414 / 150 · most readings of one game that day (≈ runs): 305
- 2026-11-09: 2,911 / 1,348 / 158 · most readings of one game that day (≈ runs): 313
- 2026-11-10: 3,131 / 1,229 / 169 · most readings of one game that day (≈ runs): 303
- 2026-11-11: 3,093 / 1,049 / 188 · most readings of one game that day (≈ runs): 302
- 2026-11-12: 3,159 / 807 / 172 · most readings of one game that day (≈ runs): 302
- 2026-11-13: 3,277 / 719 / 207 · most readings of one game that day (≈ runs): 275
- 2026-11-14: 3,028 / 663 / 199 · most readings of one game that day (≈ runs): 295
- 2026-11-15: 3,124 / 563 / 171 · most readings of one game that day (≈ runs): 303
- 2026-11-16: 3,107 / 489 / 176 · most readings of one game that day (≈ runs): 289
- 2026-11-17: 3,208 / 392 / 193 · most readings of one game that day (≈ runs): 294
- 2026-11-18: 3,126 / 341 / 174 · most readings of one game that day (≈ runs): 293
- 2026-11-19: 3,358 / 247 / 182 · most readings of one game that day (≈ runs): 291
- 2026-11-20: 3,112 / 229 / 192 · most readings of one game that day (≈ runs): 294
- 2026-11-21: 2,936 / 180 / 206 · most readings of one game that day (≈ runs): 294
- 2026-11-22: 2,887 / 139 / 219 · most readings of one game that day (≈ runs): 294
- 2026-11-23: 2,921 / 92 / 232 · most readings of one game that day (≈ runs): 291
- 2026-11-24: 2,798 / 76 / 218 · most readings of one game that day (≈ runs): 295
- 2026-11-25: 2,929 / 20 / 214 · most readings of one game that day (≈ runs): 294
- 2026-11-26: 2,882 / 20 / 219 · most readings of one game that day (≈ runs): 296
- 2026-11-27: 2,880 / 5 / 0 · most readings of one game that day (≈ runs): 278
- alerts: 2026-10-22 → 2026-11-27 (37 distinct)
- trend_feats: 2026-10-26 → 2026-11-27 (33 distinct)
- promo_preds: 2026-10-24 → 2026-11-27 (35 distinct)
- theme_daily: 2026-08-25 → 2026-11-26 (94 distinct)
- hold_weekly: 2026-09-02 → 2026-11-25 (13 distinct)
- engage_weekly: 2026-09-02 → 2026-11-25 (13 distinct)

state.json: 5.6 MB · biggest keys:
- games: 2.47 MB
- rbx_direct: 1.05 MB
- src: 1.00 MB
- upstream: 0.28 MB
- icon_changes: 0.21 MB
- icons: 0.16 MB
- hold: 0.16 MB
- ins: 0.15 MB
- stick: 0.12 MB
- alert_queue: 0.09 MB
- alerts: 0.08 MB
- rw_trends: 0.08 MB

_0.1s_

## How often games are really read

readings per game on 2026-11-27 (10th / 25th / median / 75th / 90th percentile), by the game's daily high:
- <500: 370 games · 1 / 2 / 3 / 3 / 3 · 28% have under 3 readings
- 500–2K: 1,301 games · 1 / 2 / 3 / 3 / 3 · 42% have under 3 readings
- 2K–10K: 984 games · 3 / 3 / 3 / 3 / 3 · 4% have under 3 readings
- 10K+: 225 games · 3 / 3 / 3 / 3 / 3 · 0% have under 3 readings

hour-adjusted daily average ÷ daily high (games with 8+ readings) — the code assumes 0.75 when a day has under 3 readings:
- <500: —
- 500–2K: —
- 2K–10K: —
- 10K+: —

_0.0s_

## Alerts, updates, breakouts

alerts by kind: total · first day · last day · last 7 days
- abroad: 1935 · 2026-10-26 · 2026-11-27 · 572
- surge: 1780 · 2026-10-23 · 2026-11-27 · 351
- copy: 1272 · 2026-10-23 · 2026-11-27 · 367
- new: 1254 · 2026-10-22 · 2026-11-27 · 180
- early: 397 · 2026-10-22 · 2026-11-27 · 84
- breakout: 271 · 2026-10-23 · 2026-11-27 · 30
- chart: 134 · 2026-10-22 · 2026-11-27 · 23
- update: 110 · 2026-10-22 · 2026-11-27 · 22
- longterm: 89 · 2026-10-24 · 2026-11-26 · 14
- heat: 86 · 2026-10-25 · 2026-11-27 · 13
- studio: 59 · 2026-10-28 · 2026-11-27 · 14
- predict: 9 · 2026-10-30 · 2026-11-08 · 0

update events kept in memory: 400 (cap 400) · with a day-3 result: 2 · dates 2026-11-22 → 2026-11-27
icon/title changes in memory: 2000 · kinds: {"icon": 352, "title": 1648}
breakouts logged: 317 · days from breakout to peak, all: 0 / 0 / 1 / 6 / 8 · only those 14+ days old (232): 0 / 0 / 1 / 7 / 9

_0.0s_

## Plumbing: runs, alert cards, sources, backup

last full run: 2026-11-27T22:38:46.330137+00:00 · RoWatcher requests by day: {"2026-11-24": 111, "2026-11-25": 171, "2026-11-26": 168, "2026-11-27": 169}
alert cards by day: {"2026-11-24": 12, "2026-11-25": 12, "2026-11-26": 12, "2026-11-27": 15} · pings: {"2026-11-24": 6, "2026-11-25": 6, "2026-11-26": 6, "2026-11-27": 6}
alerts waiting for a slot: 112 · strongest: 0.38 🏆 Proven studio launched: Crocodile Play; 0.38 🔥 Heating up on 2 platforms: Homeless Si; 0.34 🚀 Trend Score 39: Throw Brains For Zombi; 0.34 🚀 Trend Score 38: Ragdoll Samurai; 0.33 🆕 Just crossed 2.0K players: mymy clicke
yesterday's alert priorities: 263 alerts · top 12th = 0.3801 · 0.0824 / 0.104 / 0.153 / 0.22 / 0.31

alert type → chance it's followed by an explosion (starting guess → now, matured alerts behind it):
- chart: 0.350 → 0.468 (57 matured)
- trend: 0.300 → 0.300 (0 matured)
- heat: 0.250 → 0.258 (11 matured)
- predict: 0.350 → 0.250 (8 matured)
- breakout: 0.180 → 0.220 (119 matured)
- studio: 0.200 → 0.207 (9 matured)
- cp: 0.200 → 0.200 (0 matured)
- theme: 0.200 → 0.200 (0 matured)
- update: 0.050 → 0.185 (7 matured)
- surge: 0.100 → 0.153 (268 matured)
- bridge: 0.150 → 0.150 (0 matured)
- future: 0.150 → 0.150 (0 matured)
- abroad: 0.090 → 0.119 (315 matured)
- copy: 0.080 → 0.104 (120 matured)
- longterm: 0.120 → 0.083 (45 matured)
- new: 0.055 → 0.082 (491 matured)
- early: 0.040 → 0.055 (86 matured)

outside sources last worked: {"steam": "2026-11-27T04:21:16.818700+00:00", "wikipedia": "2026-11-27T04:21:16.818700+00:00", "calendar": "2026-11-27T04:21:16.818700+00:00", "yt_trending": "2026-11-27T22:38:46.330137+00:00"}
outside sources failing today: {} · Wikipedia days held: ['2026-11-18', '2026-11-19', '2026-11-20', '2026-11-21', '2026-11-22', '2026-11-23', '2026-11-24', '2026-11-25', '2026-11-26']
backfill by status: {"error:1": 27, "error:2": 20, "error:3": 361, "ok": 3238, "ok-old": 1437, "ok2": 609}
worldwide trending lists last read: 2026-11-27T22:38:46.330137+00:00 · games in them: 134 · theme words saved for search: ['rebirth', 'bridge', 'team', 'cart', 'guess', 'anomaly', 'zombies', 'project', 'backrooms', 'dig']
title tags currently treated as Roblox events: {"the hollow": "2026-10-26", "thanksgiving": "2026-11-24"}
backup: encrypted backup saved (62.5 MB)

_0.0s_

## Digest and weekly cards, built from today's data (not posted)

daily digest: 5 cards built — 📊 Daily digest · Sat 28 Nov · 🎮 Games to watch · 🌱 Trends · 🔮 Coming up & outside Roblox · 👀 Watchlist

weekly report: 9 cards built — 🗓️ Weekly report · week to Sat 28 Nov · 🧭 Mechanics: biggest moves · 🧠 What Roblox's algorithm is rewarding · 🏛️ Long-term games · ⏱ Engagement (from badges) · 🧩 What lasting games have in common · 📈 Forecasts & how long hits last · 🛠️ Do updates, icons and titles help? · 🔬 Are the predictions working?

**📊 Daily digest · Sat 28 Nov**
🚀 **Biggest riser:** [The Great Build](https://www.roblox.com/games/98487757108234) — ×39.4 to 24.0K
🔥 **Hottest across platforms:** [Homeless Simulator](https://www.roblox.com/games/118697556586883) — heat 80
⏱ **Most playtime per player:** [(🏦HEISTS) Criminal Simulator 💰](https://www.roblox.com/games/83048653078891) — 87 min/day
🔮 **Coming up:** Blade Runner 2099 (out 4 days ago) — ✨ not on Roblox yet
⚠️ **Watchlist falling:** Kukirin Life -63% week on week
📥 **Also flagged** (didn't make the day's 12 alert cards; strongest first): 🚀 Trend Score 58: RUN FROM THE DOGS!!; 📈 Entered Roblox's algorithm charts: [🏴‍☠️] Throw a Friend for Monsters; 📈 Entered Roblox's algorithm charts: 🌎 In This World; 🚀 Surging: [W5🌏]+1 Solo Hunter Evolution⚔️; 🚀 Surging:  RO-CAM [1MILLIONVISITS] (+35 more)

**🎮 Games to watch**
**[Homeless Simulator](https://www.roblox.com/games/118697556586883)** — 1.7K playing · 32d old · **×5.3** 🔥80 📺113.0K
**[The Great Build](https://www.roblox.com/games/98487757108234)** — 24.0K playing · 4d old · **×39.4** 🔥72 ⏱19m 📺122.2K
**[🌎 In This World](https://www.roblox.com/games/98272441761103)** — 21.3K playing · 24d old · **×3.5** 🔥60 ⏱38m
**[(🦃)She Is Listening.(HORROR)](https://www.roblox.com/games/121518208893583)** — 6.7K playing · 25d old · **×2.3** 🔥59
**[(🏦HEISTS) Criminal Simulator 💰](https://www.roblox.com/games/83048653078891)** — 26.0K playing · 51d old · **×1.3** 🔥56 ⏱87m 📺185.2K
**[Ruby Says! (HORROR)](https://www.roblox.com/games/72746078378649)** — 2.3K playing · 14d old · **×3.0** 🔥40
**[Throw a Seed](https://www.roblox.com/games/129081220403721)** — 34.4K playing · 21d old · **×2.1** 🔥42
**[Climb Scary Stairs](https://www.roblox.com/games/134591419708043)** — 1.7K playing · 20d old · **×2.2** 🔥41

**🗓️ Weekly report · week to Sat 28 Nov**
🧭 **Demand:** Horror +14% · Steal / brainrot -37%
🏛️ **Most long-term genre:** Social — 74% of its games reliably hold players on weekdays (all genres: 15%)
📏 **Stickiest young game:** [(🧑‍🍳) Giant Fish Chef](https://www.roblox.com/games/132508477538687) — 99/100
🧠 **Roblox is reliably rewarding:** session length and like ratio
⏱ **Most playtime (young):** [ABOVE (🐴)](https://www.roblox.com/games/124357835578554) — 153 min/player/day

**🧭 Mechanics: biggest moves**
🔴 **Steal / brainrot** · 1.2M (-37%) · 9 new · 1 hit
🔴 **Vehicles / riding** · 342.2K (-34%) · 21 new · 1 hit
🔴 **RNG / gacha / luck** · 1.3M (-32%) · 20 new
🔴 **Anomaly / night shift** · 242.6K (-26%) · 3 new · 1 hit
🔴 **Tower defense** · 147.8K (-19%) · 5 new
🔴 **Merge / clicker** · 112.7K (-19%) · 4 new · 1 hit
💥 46 breakouts: [The Great Build](https://www.roblox.com/games/98487757108234), [Crash Engine](https://www.roblox.com/games/81268852194868), [(🐟) Fish For Sea Anim…](https://www.roblox.com/games/90296841634441)

**🧠 What Roblox's algorithm is rewarding**
🟩🟩 session length
🟩🟩 like ratio
🟥🟥 weekday hold vs a typical game — _games that keep a steady crowd all week rarely jump 50% in a week, so this mostly means "already settled", not that Roblox punishes retention_
🟥🟥🟥🟥🟥🟥 revenue per player — _fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation_
🧪 enters a Roblox chart within 7 days: predictions the bot made scored **0.68** · top 10% came true 18% vs 6.5% overall
🧪 players up 50%+ within 7 days: predictions the bot made scored **0.81** · top 10% came true 39% vs 8.1% overall

**🏛️ Long-term games**
Weekday hold is 78% the game, 22% week-to-week noise — so one good week proves little
**Social** · 74% long-term (26/35, likely 61%–84%) ✅
**Sports & Racing** · 27% long-term (17/64, likely 19%–36%) ✅
**RPG** · 25% long-term (15/59, likely 17%–36%) ✅
**Simulation** · 15% long-term (115/750, likely 13%–18%)
**Shooter** · 16% long-term (12/73, likely 11%–25%)
Young games already long-term: [Teach Your Granny How T…](https://www.roblox.com/games/93799361852148), [(⚔️) 1.8 KIT PVP](https://www.roblox.com/games/72393956865647), [(🏁) Steal A Scooter](https://www.roblox.com/games/107344344488571)
Stickiest young games: [(🧑‍🍳) Giant Fish Chef](https://www.roblox.com/games/132508477538687) (99), [Homeless Simulator](https://www.roblox.com/games/118697556586883) (98), [(SCYTHE FIN) +1 Levia…](https://www.roblox.com/games/73435402573922) (98)

**⏱ Engagement (from badges)**
Typical game: **48 min** per player per day (287 games measured)
⏱ [ABOVE (🐴)](https://www.roblox.com/games/124357835578554) · **153 min** · 39.5K/day
⏱ [(⭐UPD) My KPOP Shop!](https://www.roblox.com/games/128223803884544) · **124 min** · 94.8K/day
⏱ [(NOW) Clean the Moon!](https://www.roblox.com/games/76678170614451) · **123 min** · 72.5K/day
⏱ [UNDERTALE: Project Soul's (SOON)](https://rowatcher.com/games/10768613071) · **114 min** · 56.9K/day

**🧩 What lasting games have in common**
✅ leaderboards · **1.8×** as likely to be long-term (likely 1.2–2.8×, 138 games)
✅ pets / collecting · **1.4×** as likely to be long-term (likely 1.0–1.9×, 436 games)
🧪 Stickiness can't be checked against survival until 2026-11-25 (needs games watched from the start, 4 weeks on)

**📈 Forecasts & how long hits last**
📈 Peak forecasts (made on day 5): typically off by **153%**; 44% within 2× of the real peak (197 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 13% for any young game (122 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1632 games that peaked while the bot was watching; 1145 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (215) · holds weekday players well **11d** (275) · holds them poorly **5d** (73)
By mechanic: Battles / army **9d** (68) · Roleplay / life **8d** (65) · Vehicles / riding **8d** (54) · Sports **8d** (39)
By genre: Social **31d** (27) · Action **10d** (126) · Shooter **10d** (57) · Party & Casual **9d** (78)

**🛠️ Do updates, icons and titles help?**
▫️ **Updates after a quiet week**: -4% (likely -9% to +2%) vs similar games that changed nothing · 26% beat them by 10%+ (117 measured)
✅ **Icon changes**: +8% (likely +2% to +12%) vs similar games that changed nothing · 47% beat them by 10%+ (340 measured)
✅ **Title changes**: +2% (likely +1% to +3%) vs similar games that changed nothing · 40% beat them by 10%+ (3374 measured)
🖼️ 8 young games use an icon nearly identical to a hit from another studio (last 30 days)

**🔬 Are the predictions working?**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.79** (likely 0.76–0.81) · its top 10% took off 23% of the time vs 7.4% for all · 11,433 snapshots over 19 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 11433 / 844 over 19 days)
🎯 Explosion model: not provable yet (too few finished explosions among games watched live) — its picks aren't used
🌱 Theme model: not provable yet (too few finished breakouts among games watched live) — its picks aren't used

_7.9s_

## Trend Score

snapshots old enough to score: 13,845 over 20 days (2026-10-26 → 2026-11-14)

take-off rate by size at the time of the snapshot (took off / snapshots):
| definition | <500 | 500–2K | 2K–10K | 10K+ | all |
|---|---|---|---|---|---|
| old (2× and 1,000, one day) | 240/630 (38.1%) | 1396/5997 (23.3%) | 632/4503 (14.0%) | 81/990 (8.2%) | 2349/12120 (19.4%) |
| 2× and 5,000, one day | 26/630 (4.1%) | 403/5997 (6.7%) | 612/4503 (13.6%) | 81/990 (8.2%) | 1122/12120 (9.3%) |
| NEW (2× and 5,000, two days) | 20/630 (3.2%) | 328/5997 (5.5%) | 478/4503 (10.6%) | 62/990 (6.3%) | 888/12120 (7.3%) |
| 2× and 2,000, two days | 95/630 (15.1%) | 923/5997 (15.4%) | 503/4503 (11.2%) | 62/990 (6.3%) | 1583/12120 (13.1%) |

starting formula vs the NEW outcome: {"n": 12120, "pos": 888, "auc": 0.783, "base": 0.073, "top": 0.231, "top_n": 1212, "lo": 0.758, "hi": 0.808}
scores as shown at the time vs the NEW outcome: AUC 0.781
- shown 50–100: 226/986 took off (23%)
- shown 25–50: 207/953 took off (22%)
- shown 10–25: 184/1378 took off (13%)
- shown 0–10: 271/8803 took off (3%)
starting-formula raw scores (10/25/50/75/90th pct): 0.0057 / 0.0108 / 0.026 / 0.127 / 0.474
calibration of the starting formula: {"n": 12120, "pos": 888, "days": 20, "cal": {"a": 0.4444970845084585, "b": -1.5143093187746572}, "auc": 0.783, "lo": 0.758, "hi": 0.808, "base": 0.073, "top": 0.231}
learned model status: {"day": "2026-11-28", "examples": 12120, "positives": 888, "days": 20, "trained": false, "why": "needs 2000+ outcomes with 60+ take-offs over 21+ days (has 12120 / 888 over 20 days)"}

_12.2s_

## Weekday hold: old vs new definition

**OLD: Tue–Wed vs Sat–Sun** — games rated: 3,412 · weeks rated per game: 1 / 1 / 3 / 7 / 8 · week-to-week rank correlation: 0.491 (9,264 pairs) · share of one week's spread that is the game itself: 0.721 · noise sd 0.218 · old-rule 'long-term': 665 of 2500 with 2+ weeks (27%)
**NEW: Mon–Wed vs two busiest of Fri–Sun** — games rated: 3,462 · weeks rated per game: 1 / 1 / 3 / 7 / 8 · week-to-week rank correlation: 0.502 (9,354 pairs) · share of one week's spread that is the game itself: 0.783 · noise sd 0.203 · old-rule 'long-term': 706 of 2537 with 2+ weeks (28%)

games the OLD measure flattered most (old ÷ new relative hold):
- وين فهد رعب😨 — ×2.21 (2 weeks)
- Napoleonic Wars — ×2.04 (3 weeks)
- Malam Bersama Kaka [HOROR] — ×1.90 (3 weeks)
- 100 Player Floor Is LAVA! 🔥 — ×1.85 (2 weeks)
- Save an Egg — ×1.84 (3 weeks)
- [🎵 Maestro🎶] Mermaid Isle 🌊 — ×1.78 (2 weeks)
- Defend Your Base From Scary Worm — ×1.76 (4 weeks)
- [UPD!] Super Head Soccer 🎃 — ×1.71 (2 weeks)
- [🎃] Shoot For Eggs — ×1.68 (2 weeks)
- +1 Car Vs Platforms — ×1.57 (3 weeks)
- [TRENDING🎶] Dance Troll Tower 2 — ×1.48 (2 weeks)
- [⚔️] Steal a Nito — ×1.45 (2 weeks)

after the new rule: hold_meta {"week": "2026-11-25", "weekend": ["2026-11-21", "2026-11-22"], "weekday": ["2026-11-24", "2026-11-25"], "benchmark": 0.715, "roblox": 0.711, "weeks": 8, "reliability": 0.783, "noise_sd": 0.203} · long-term 290 · promising 313
- [EVENT🦃] Noob Incremental — 1.522× over 8 weeks (z 6.04) · 5.5K
- [UPD 14] Defeat Anime RNG  — 1.514× over 8 weeks (z 5.96) · 6.6K
- 🦃 [TURKEY] Pet Simulator 99! 🍁 — 1.525× over 7 weeks (z 5.71) · 73.7K
- TANPANAMA — 1.484× over 8 weeks (z 5.68) · 4.6K
- [PAINT MAGIC!] Clover Retribution — 1.499× over 7 weeks (z 5.48) · 2.6K
- Teach Your Granny How To Drive! 🎙️ — 1.683× over 4 weeks (z 5.47) · 5.6K
- Forest Market — 1.463× over 8 weeks (z 5.47) · 4.0K
- [⚔️] 1.8 KIT PVP — 1.663× over 4 weeks (z 5.35) · 8.6K
- [🌎W12] Throw a Coin — 1.448× over 8 weeks (z 5.33) · 2.9K
- 🤠 Tap Simulator REBORN — 1.52× over 6 weeks (z 5.27) · 49.4K
- Sol's RNG [ Part 2 🎃 ] — 1.425× over 8 weeks (z 5.1) · 41.4K
- [ Content deleted ] — 1.552× over 5 weeks (z 5.1) · 9.6K

_2.0s_

## What changes do (matched comparison)

games watched for publishes: 1301 · publish days seen: 5,628 · publishes after a quiet week: 218
naive measure (day+3 vs the 3 days before), every publish: median -16.8% over 3,479 · by weekday of the publish: Mon -40% (518), Tue -24% (566), Wed +11% (429), Thu +23% (374), Fri -13% (408), Sat -17% (677), Sun -26% (507)
measured now: 267 changes
- icon: 571 events · 512 with complete weeks · 357 with enough twins
- title: 5979 events · 3925 with complete weeks · 3525 with enough twins
- update: 182 events · 160 with complete weeks · 121 with enough twins
• ▫️ **Updates after a quiet week**: typical lift **-3%** (likely -9% to +2%) vs similar games that changed nothing · 27% beat their twins by 10%+, 40% fell 10%+ behind · 121 measured
   ↳ the games themselves went -23% week on week while their twins went -14% — the naive before/after number is mostly that drift
   ↳ biggest: [RAMEN🍜] Create Slime Mart (+263%), Save the Krusty Krab 🍔 (+213%), [NOW] Clean the Moon! (+172%)
• ✅ **Icon changes**: typical lift **+8%** (likely +3% to +11%) vs similar games that changed nothing · 47% beat their twins by 10%+, 37% fell 10%+ behind · 357 measured
   ↳ the games themselves went -21% week on week while their twins went -25% — the naive before/after number is mostly that drift
• ✅ **Title changes**: typical lift **+2%** (likely +1% to +3%) vs similar games that changed nothing · 39% beat their twins by 10%+, 34% fell 10%+ behind · 3525 measured
   ↳ the games themselves went -13% week on week while their twins went -12% — the naive before/after number is mostly that drift
_Lift = the game's week-on-week change divided by the median change of similar-size, similar-trend games that made no such change. Correlation still, but weekdays, natural decay and market swings are removed._

_2.5s_

## Themes

themes: 3,359 · calm candidate days: 48,811 · breakouts: 190 in 189 themes · history starts 2026-08-25
themes that broke out (count · name · most games): 2× baby (15); 1× wars (26); 1× walls escape (3); 1× walls (8); 1× voxel (12); 1× verity (32); 1× untitled (18); 1× town (14); 1× together (17); 1× throw food (8); 1× throw (22); 1× thai (10); 1× tesla (4); 1× survival (43); 1× studio (11); 1× striker (4); 1× steal eggs (9); 1× steal egg (18); 1× smash (9); 1× showdown (12); 1× shoot (7); 1× shadow (4); 1× sell (18); 1× scooter (10); 1× say (3)

model status: {"examples": 5032, "positives": 124, "trained": true, "day": "2026-11-28", "themes": 1492, "base_rate": 0.0246422893481717, "champion": "simple", "wf": {"folds": 0, "horizon": 21, "test_from": null}}
- simple model, test with a 0-day purge: {"n": 2205, "pos": 43, "auc": 0.692, "base": 0.02, "top": 0.055, "top_n": 220, "lo": 0.587, "hi": 0.792} (folds 2)
- simple model, test with a 21-day purge: {} (folds 0)

top themes it would show today:
- bridge — model 0.364 · 1 signals · 13 games, 2 hits, 1 young hits, 0 new
- rebirth — model 0.345 · 2 signals · 4 games, 2 hits, 1 young hits, 1 new
- Mining — model 0.315 · 1 signals · 14 games, 2 hits, 1 young hits, 0 new
- project — model 0.308 · 1 signals · 13 games, 1 hits, 0 young hits, 0 new
- Backrooms & Liminal Spaces — model 0.307 · 2 signals · 10 games, 2 hits, 0 young hits, 0 new
- guess — model 0.295 · 2 signals · 14 games, 0 hits, 0 young hits, 0 new
- anomaly — model 0.288 · 2 signals · 14 games, 2 hits, 1 young hits, 0 new
- backrooms — model 0.243 · 1 signals · 10 games, 2 hits, 0 young hits, 0 new
- cart — model 0.233 · 2 signals · 9 games, 1 hits, 1 young hits, 0 new
- team — model 0.233 · 2 signals · 7 games, 2 hits, 0 young hits, 0 new
- Anime Blade Combat System — model 0.225 · 1 signals · 14 games, 2 hits, 0 young hits, 0 new
- Object Repair & Fixing Maintenance — model 0.209 · 1 signals · 12 games, 1 hits, 0 young hits, 0 new

🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Trained on 5,032 calm theme-days from 1,492 themes; 124 (2.5%) were followed by a breakout.
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• Biggest drivers: number of games (+), theme growth over 7 days (+), players across the theme (+), new games this week vs last week (−), YouTube Shorts mentions (+)

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• Too few firings to judge (under 8): 📊 in the algorithm charts (0/1)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

_5.6s_

## Algorithm mirror

**chart**: 3,955 game-days over 28 days (2026-10-24 → 2026-11-20) · 164 positive (4.1%) · games: 2,378
**growth**: 4,631 game-days over 28 days (2026-10-24 → 2026-11-20) · 411 positive (8.9%) · games: 2,707

chart: coverage {"playtime": 0.029, "returning": 0.0, "first_step": 0.016, "sessions": 0.029, "hold": 0.617, "session_len": 0.97, "like_ratio": 0.882, "fav_conv": 0.828, "rev_per_player": 0.823, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
chart: stability {"playtime": {"w": -0.027, "lo": -0.1, "hi": 0.09, "sign": 0.517}, "first_step": {"w": 0.137, "lo": 0.034, "hi": 0.334, "sign": 1.0}, "sessions": {"w": 0.108, "lo": -0.004, "hi": 0.238, "sign": 0.9}, "hold": {"w": -0.152, "lo": -0.319, "hi": 0.047, "sign": 0.917}, "session_len": {"w": 0.213, "lo": 0.051, "hi": 0.31, "sign": 0.983}, "like_ratio": {"w": 0.098, "lo": -0.014, "hi": 0.307, "sign": 0.933}, "fav_conv": {"w": -0.3, "lo": -0.531, "hi": -0.128, "sign": 1.0}, "rev_per_player": {"w": -0.229, "lo": -0.399, "hi": -0.06, "sign": 0.967}, "size": {"w": 0.661, "lo": 0.529, "hi": 0.841, "sign": 1.0}, "momentum": {"w": 0.401, "lo": 0.307, "hi": 0.576, "sign": 1.0}, "age": {"w": -0.331, "lo": -0.474, "hi": -0.136, "sign": 1.0}, "has_badges": {"w": 0.039, "lo": -0.144, "hi": 0.174, "sign": 0.583}}
chart: wf {"folds": 4, "horizon": 8, "test_from": null, "lr": {"n": 2103, "pos": 85, "auc": 0.6885, "base": 0.0404, "top": 0.119, "top_n": 210, "lo": 0.6365, "hi": 0.742}, "gbm": {"n": 2103, "pos": 85, "auc": 0.8024, "base": 0.0404, "top": 0.1905, "top_n": 210, "lo": 0.758, "hi": 0.8485}, "p_trees_better": 1.0, "diff": 0.1112}

growth: coverage {"playtime": 0.07, "returning": 0.0, "first_step": 0.034, "sessions": 0.069, "hold": 0.624, "session_len": 0.974, "like_ratio": 0.899, "fav_conv": 0.845, "rev_per_player": 0.839, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
growth: stability {"playtime": {"w": -0.111, "lo": -0.211, "hi": -0.039, "sign": 1.0}, "first_step": {"w": 0.02, "lo": -0.107, "hi": 0.203, "sign": 0.6}, "sessions": {"w": -0.007, "lo": -0.068, "hi": 0.067, "sign": 0.65}, "hold": {"w": 0.029, "lo": -0.073, "hi": 0.105, "sign": 0.633}, "session_len": {"w": 0.021, "lo": -0.068, "hi": 0.158, "sign": 0.667}, "like_ratio": {"w": -0.007, "lo": -0.067, "hi": 0.096, "sign": 0.467}, "fav_conv": {"w": -0.067, "lo": -0.143, "hi": 0.02, "sign": 0.917}, "rev_per_player": {"w": -0.36, "lo": -0.524, "hi": -0.17, "sign": 1.0}, "size": {"w": -0.312, "lo": -0.462, "hi": -0.156, "sign": 1.0}, "momentum": {"w": 0.944, "lo": 0.868, "hi": 1.05, "sign": 1.0}, "age": {"w": -0.536, "lo": -0.698, "hi": -0.416, "sign": 1.0}, "has_badges": {"w": -0.052, "lo": -0.212, "hi": 0.078, "sign": 0.833}}
growth: wf {"folds": 4, "horizon": 8, "test_from": null, "lr": {"n": 2479, "pos": 245, "auc": 0.8457, "base": 0.0988, "top": 0.498, "top_n": 247, "lo": 0.8203, "hi": 0.8695}, "gbm": {"n": 2479, "pos": 245, "auc": 0.8617, "base": 0.0988, "top": 0.5628, "top_n": 247, "lo": 0.8327, "hi": 0.8868}, "p_trees_better": 0.88, "diff": 0.0164}
- chart, 0-day purge: simple 0.723 · trees 0.827 · n 3267 · folds 4
- chart, 8-day purge: simple 0.688 · trees 0.802 · n 2103 · folds 4
- growth, 0-day purge: simple 0.846 · trees 0.872 · n 3845 · folds 4
- growth, 8-day purge: simple 0.846 · trees 0.862 · n 2479 · folds 4

🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥 favourite rate (-0.18)
🟥🟥🟥🟥 revenue per player (-0.29) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, new players reaching the next badge, sessions per player per day, like ratio, weekday hold vs a typical game, playtime per player per day
• Model for *enters a Roblox chart within 7 days* (3,955 game-days): Honest test: accuracy **0.80** (likely between 0.76 and 0.85) · 0.5 = coin flip · top 10% picks came true **19%** of the time vs 4% for all · 2,103 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.69 for the simple model (trees better in 100% of resamples)
• Model for *players up 50%+ within 7 days* (4,631 game-days): Honest test: accuracy **0.85** (likely between 0.82 and 0.87) · 0.5 = coin flip · top 10% picks came true **50%** of the time vs 10% for all · 2,479 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.85 vs 0.86 for boosted trees (trees better in 88% of resamples; they need 90%+ and a 0.01+ lead)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.68; their top 10% were promoted 18% of the time vs 7% overall (57,301 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.81; their top 10% were promoted 39% of the time vs 8% overall (66,473 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

_16.3s_

## Explosion model

examples: 672 · exploded: 23 · first noticed on a backfilled day (before the bot watched): 481 (17 exploded) vs live: 191 (6 exploded)
first-noticed dates: 2026-08-08 → 2026-11-06 · by month: {"2026-08": [34, 1], "2026-09": [107, 6], "2026-10": [439, 13], "2026-11": [92, 3]}
log10(peak after ÷ players the day after noticing): 0.0307 / 0.147 / 0.4 / 0.744 / 1.04
status: {"examples": 672, "positives": 23, "trained": true, "day": "2026-11-28", "live_examples": 258, "live_positives": 6, "champion": "simple", "wf": {"folds": 4, "horizon": 21, "test_from": "2026-10-22", "lr": {"n": 258, "pos": 6, "auc": null}}, "honest": {"n": 258, "pos": 6, "auc": null}, "test_n": 258, "test_pos": 6, "test_top10_hit": null, "base_rate": 0.03422619047619048, "stable": ["players_d1", "growth_d1", "visits_d1", "late_climb", "late_missing", "age", "weekend", "crowd", "mech_hits"]}

🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 672 young games, 23 of which exploded (3%). Only 258 of them (6 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (6 of 258; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), copies in the same mechanic in the 2 weeks before (−), players the day after (+), game age when noticed (−), growth from day 0 to day 1 (+), (no hourly data) (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **44/528** (8%) · 723 still in their 21-day window (32 already exploded)
• abroad: **40/340** (12%) · 466 still in their 21-day window (32 already exploded)
• 🚀 surge: **43/284** (15%) · 498 still in their 21-day window (34 already exploded)
• 💥 breakout: **35/134** (26%) · 137 still in their 21-day window (26 already exploded)
• 🧬 copy wave: **14/128** (11%) · 421 still in their 21-day window (27 already exploded)
• model < 50%: **0/112** (0%) · 452 still in their 21-day window (6 already exploded)
• 👀 early warning: **5/92** (5%) · 79 still in their 21-day window (4 already exploded)
• chart: **30/58** (52%) · 76 still in their 21-day window (33 already exploded)
• longterm: **3/45** (7%) · 43 still in their 21-day window (3 already exploded)
• 🔥 heat: **6/14** (43%) · 24 still in their 21-day window (4 already exploded)
• studio: **2/9** (22%) · 49 still in their 21-day window (1 already exploded)
• 🎯 prediction: **0/8** (0%) · 1 still in their 21-day window (1 already exploded)
• update: **4/7** (57%) · 1 still in their 21-day window (1 already exploded)
• model ≥ 50%: **1/6** (17%) · 2 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

_4.2s_

## Stickiness and lasting features

games scored: 2477 · weights {"hold_rel": 0.555, "playtime": 0.2341, "session_min": 0.0775, "level_kept": 0.1333, "fav_conv": 0.0, "rev_per_ccu": 0.0} · per-signal rank correlation with players kept 4 weeks later: {"hold_rel": 0.358, "playtime": 0.151, "session_min": 0.05, "level_kept": 0.086, "fav_conv": -0.255, "rev_per_ccu": -0.027} · n 1588 · honest cross-check null
description features: 290 long-term vs 1648 others · checked 16
- leaderboards: lift 1.85 (1.24–2.75) · 138 games · reliable: True
- pets / collecting: lift 1.38 (1.02–1.87) · 436 games · reliable: True
- codes: lift 1.42 (0.99–2.04) · 248 games · reliable: False
- PvP: lift 1.24 (0.72–2.13) · 109 games · reliable: False
- base building / decorating: lift 0.99 (0.69–1.42) · 357 games · reliable: False
- offline / idle earnings: lift 1.1 (0.65–1.85) · 135 games · reliable: False
- group rewards: lift 0.89 (0.6–1.33) · 302 games · reliable: False
- quests / missions: lift 1.01 (0.56–1.82) · 113 games · reliable: False
- rebirth / prestige: lift 1.02 (0.55–1.92) · 98 games · reliable: False
- roleplay: lift 0.95 (0.53–1.7) · 126 games · reliable: False
- trading: lift 1.12 (0.52–2.38) · 60 games · reliable: False
- limited events: lift 0.92 (0.52–1.63) · 137 games · reliable: False

_2.6s_

## Money: top earners under 5K players

games with earnings: 2,462 · $/player/month percentiles: 1.87 / 9.75 / 23.9 / 62.9 · flagged as suspect: 29
- [❄️] Kukirin Life [Testing] — $327,480/month · 3763 players · $87/player · suspect: True
- Bug Evolution [🦃] — $277,641/month · 3885 players · $71/player · suspect: True
- +1 Spider Arm🕷️ — $270,954/month · 3233 players · $84/player · suspect: True
- [🌎W13] +1 Anime Eyes — $243,740/month · 2550 players · $96/player · suspect: True
- Realistic Ragdoll Engine 🩸 — $231,406/month · 3640 players · $64/player · suspect: True
- 🧸 My Small Business — $213,584/month · 2616 players · $82/player · suspect: True
- [🎄ROLEPLAY CITY] Build a REAL House — $201,282/month · 4933 players · $41/player · suspect: False
- [🐉W5] +1 Sukuna Evolution — $187,355/month · 2435 players · $77/player · suspect: True

_0.2s_

## Badge streaks

games with badge data: 287 · with a 7-day streak badge: 16
- Illegal Soccer: [7, 0.1369] · base: players who earn "First Tackle"
- 7 Days Cat-Sitting: [10, 0.0006] · base: players who earn "Haunted House"
- Save the Krusty Krab 🍔: [5, 0.0] · base: players who earn "Join the Krew"
- Firefighting Sim 🚒: [7, 0.0312] · base: players who earn "First Alarm"
- Punch Out Of Prison: [7, 0.0019] · base: new players
- Draw an aquarium: [7, 0.0] · base: players who earn "My First Fish"
- Untitled Symbiote Suit Game [VENOM]: [7, 0.0] · base: players who earn "Bonded"
- Clean The Bugs 🐜: [7, 0.0005] · base: new players
- [XMAS🎄] Sleepover (Story) 🤫: [7, 0.0002] · base: new players
- 🤡 Class Clowns: [7, 0.0001] · base: new players
- Ragdoll Craft Sandbox: [7, 0.0056] · base: new players
- ⚡ +1 Heart Per Kill: [7, 0.0062] · base: new players
- Fake Sick!: [10, 0.0535] · base: players who earn "First Day Off"
- The Block: [5, 0.0] · base: players who earn "Best Audience Award"
- [⭐UPD] My KPOP Shop!: [7, 0.0005] · base: players who earn "First Sale"

_0.0s_

## Model check as the bot would now print it

_Model check · 2026-11-28_

**🧠 Algorithm mirror**
🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥 favourite rate (-0.18)
🟥🟥🟥🟥 revenue per player (-0.29) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, new players reaching the next badge, sessions per player per day, like ratio, weekday hold vs a typical game, playtime per player per day
• Model for *enters a Roblox chart within 7 days* (3,955 game-days): Honest test: accuracy **0.80** (likely between 0.76 and 0.85) · 0.5 = coin flip · top 10% picks came true **19%** of the time vs 4% for all · 2,103 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.69 for the simple model (trees better in 100% of resamples)
• Model for *players up 50%+ within 7 days* (4,631 game-days): Honest test: accuracy **0.85** (likely between 0.82 and 0.87) · 0.5 = coin flip · top 10% picks came true **50%** of the time vs 10% for all · 2,479 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.85 vs 0.86 for boosted trees (trees better in 88% of resamples; they need 90%+ and a 0.01+ lead)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.68; their top 10% were promoted 18% of the time vs 7% overall (57,301 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.81; their top 10% were promoted 39% of the time vs 8% overall (66,473 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula, calibrated**
• Starting formula vs real outcomes: accuracy **0.78** (likely 0.76–0.81) · its top 10% took off 23% of the time vs 7.3% for all · 12,120 snapshots over 20 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 12120 / 888 over 20 days)
• Scores as shown at the time: 50+: 23% took off (986) · 25–49: 22% took off (953) · 10–24: 13% took off (1378) · under 10: 3% took off (8803)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 672 young games, 23 of which exploded (3%). Only 258 of them (6 explosions) were first noticed while the bot was watching — the rest come from downloaded history, which only contains games that survived, so the test below uses the watched ones only.
• Honest test: too few explosions in the test window to score (6 of 258; needs 10+). Treat this model's picks as unproven.
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), copies in the same mechanic in the 2 weeks before (−), players the day after (+), game age when noticed (−), growth from day 0 to day 1 (+), (no hourly data) (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: **44/528** (8%) · 723 still in their 21-day window (32 already exploded)
• abroad: **40/340** (12%) · 466 still in their 21-day window (32 already exploded)
• 🚀 surge: **43/284** (15%) · 498 still in their 21-day window (34 already exploded)
• 💥 breakout: **35/134** (26%) · 137 still in their 21-day window (26 already exploded)
• 🧬 copy wave: **14/128** (11%) · 421 still in their 21-day window (27 already exploded)
• model < 50%: **0/112** (0%) · 452 still in their 21-day window (6 already exploded)
• 👀 early warning: **5/92** (5%) · 79 still in their 21-day window (4 already exploded)
• chart: **30/58** (52%) · 76 still in their 21-day window (33 already exploded)
• longterm: **3/45** (7%) · 43 still in their 21-day window (3 already exploded)
• 🔥 heat: **6/14** (43%) · 24 still in their 21-day window (4 already exploded)
• studio: **2/9** (22%) · 49 still in their 21-day window (1 already exploded)
• 🎯 prediction: **0/8** (0%) · 1 still in their 21-day window (1 already exploded)
• update: **4/7** (57%) · 1 still in their 21-day window (1 already exploded)
• model ≥ 50%: **1/6** (17%) · 2 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Trained on 5,032 calm theme-days from 1,492 themes; 124 (2.5%) were followed by a breakout.
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• Biggest drivers: number of games (+), theme growth over 7 days (+), players across the theme (+), new games this week vs last week (−), YouTube Shorts mentions (+)

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• Too few firings to judge (under 8): 📊 in the algorithm charts (0/1)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **153%**; 44% within 2× of the real peak (197 games — only rises the bot watched from their start are checked)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **8%** of the time vs 13% for any young game (122 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **8 days** (1632 games that peaked while the bot was watching; 1145 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (215) · holds weekday players well **11d** (275) · holds them poorly **5d** (73)
By mechanic: Battles / army **9d** (68) · Roleplay / life **8d** (65) · Vehicles / riding **8d** (54) · Sports **8d** (39)
By genre: Social **31d** (27) · Action **10d** (126) · Shooter **10d** (57) · Party & Casual **9d** (78)

**📏 Stickiness weights**
weekday hold 56% · playtime per player 23% · players kept vs best week 13% · session length 8% — learned from 1,588 game-weeks

📥 Past histories downloaded: **5,284** games (5,692 tried)

_7.1s_
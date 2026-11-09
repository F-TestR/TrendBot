# Diagnostics · 2026-11-09

_generated 2026-11-09T21:48:07Z · models retrained in memory only_

## Tables and coverage

- games: 8,137
- daily: 156,196
- hourly: 716,110
- alerts: 2,455
- predictions: 408
- backfill: 2,529
- trend_feats: 9,736
- promo_preds: 45,358
- theme_daily: 44,256
- theme_preds: 22,062
- hold_weekly: 9,209
- engage_weekly: 12,194
- fc_preds: 13,315
- cp_fires: 84
- renames: 3,811
- effects: 2,579
- upstream: 70,679
- database file: 118 MB
- daily covers 2026-07-26 → 2026-11-09 (107 days)

game-days per day, last 21 days (live / backfill / other):
- 2026-10-19: 0 / 1,883 / 0 · most readings of one game that day (≈ runs): 1033
- 2026-10-20: 0 / 1,927 / 0 · most readings of one game that day (≈ runs): 1035
- 2026-10-21: 0 / 1,965 / 0 · most readings of one game that day (≈ runs): 1006
- 2026-10-22: 6,046 / 177 / 15 · most readings of one game that day (≈ runs): 293
- 2026-10-23: 6,030 / 176 / 23 · most readings of one game that day (≈ runs): 294
- 2026-10-24: 6,084 / 187 / 29 · most readings of one game that day (≈ runs): 295
- 2026-10-25: 6,081 / 209 / 18 · most readings of one game that day (≈ runs): 294
- 2026-10-26: 2,836 / 672 / 42 · most readings of one game that day (≈ runs): 295
- 2026-10-27: 2,888 / 636 / 43 · most readings of one game that day (≈ runs): 295
- 2026-10-28: 2,764 / 632 / 47 · most readings of one game that day (≈ runs): 295
- 2026-10-29: 2,790 / 623 / 59 · most readings of one game that day (≈ runs): 295
- 2026-10-30: 2,824 / 598 / 66 · most readings of one game that day (≈ runs): 295
- 2026-10-31: 2,796 / 600 / 77 · most readings of one game that day (≈ runs): 295
- 2026-11-01: 2,769 / 603 / 85 · most readings of one game that day (≈ runs): 295
- 2026-11-02: 2,797 / 557 / 118 · most readings of one game that day (≈ runs): 295
- 2026-11-03: 2,790 / 571 / 134 · most readings of one game that day (≈ runs): 98
- 2026-11-04: 2,848 / 534 / 141 · most readings of one game that day (≈ runs): 161
- 2026-11-05: 2,823 / 522 / 161 · most readings of one game that day (≈ runs): 294
- 2026-11-06: 2,825 / 449 / 173 · most readings of one game that day (≈ runs): 294
- 2026-11-07: 2,712 / 331 / 196 · most readings of one game that day (≈ runs): 294
- 2026-11-08: 2,721 / 201 / 232 · most readings of one game that day (≈ runs): 295
- 2026-11-09: 2,725 / 81 / 9 · most readings of one game that day (≈ runs): 270
- alerts: 2026-10-22 → 2026-11-09 (19 distinct)
- trend_feats: 2026-10-26 → 2026-11-09 (15 distinct)
- promo_preds: 2026-10-24 → 2026-11-09 (17 distinct)
- theme_daily: 2026-08-25 → 2026-11-08 (76 distinct)
- hold_weekly: 2026-09-02 → 2026-11-04 (10 distinct)
- engage_weekly: 2026-09-02 → 2026-11-04 (10 distinct)

state.json: 5.5 MB · biggest keys:
- games: 2.92 MB
- src: 1.31 MB
- rbx_direct: 0.57 MB
- hold: 0.16 MB
- icon_changes: 0.14 MB
- upstream: 0.14 MB
- icons: 0.13 MB
- ins: 0.13 MB
- stick: 0.13 MB
- rw_trends: 0.07 MB
- alerts: 0.07 MB
- badges: 0.06 MB

_0.1s_

## How often games are really read

readings per game on 2026-11-08 (10th / 25th / median / 75th / 90th percentile), by the game's daily high:
- <500: 95 games · 1 / 1 / 2 / 6 / 8 · 52% have under 3 readings
- 500–2K: 1,241 games · 1 / 4 / 7 / 10 / 27 · 17% have under 3 readings
- 2K–10K: 1,108 games · 8 / 9 / 14 / 30 / 30 · 0% have under 3 readings
- 10K+: 277 games · 30 / 30 / 30 / 30 / 30 · 0% have under 3 readings

hour-adjusted daily average ÷ daily high (games with 8+ readings) — the code assumes 0.75 when a day has under 3 readings:
- <500: median 0.81 (10 games)
- 500–2K: median 0.77 (569 games)
- 2K–10K: median 0.75 (1023 games)
- 10K+: median 0.74 (276 games)

_0.0s_

## Alerts, updates, breakouts

alerts by kind: total · first day · last day · last 7 days
- new: 642 · 2026-10-22 · 2026-11-09 · 232
- surge: 600 · 2026-10-23 · 2026-11-09 · 282
- abroad: 486 · 2026-10-26 · 2026-11-09 · 253
- copy: 210 · 2026-10-23 · 2026-11-09 · 118
- breakout: 161 · 2026-10-23 · 2026-11-09 · 50
- early: 135 · 2026-10-22 · 2026-11-09 · 65
- chart: 69 · 2026-10-22 · 2026-11-09 · 25
- longterm: 51 · 2026-10-24 · 2026-11-09 · 35
- update: 43 · 2026-10-22 · 2026-11-08 · 22
- heat: 34 · 2026-10-25 · 2026-11-09 · 16
- studio: 15 · 2026-10-28 · 2026-11-09 · 12
- predict: 9 · 2026-10-30 · 2026-11-08 · 4

update events kept in memory: 400 (cap 400) · with a day-3 result: 31 · dates 2026-11-03 → 2026-11-09
icon/title changes in memory: 1328 · kinds: {"icon": 584, "title": 744}
breakouts logged: 179 · days from breakout to peak, all: 0 / 0 / 1 / 4 / 8 · only those 14+ days old (55): 0 / 0 / 0 / 5 / 8

_0.0s_

## Plumbing: runs, alert cards, sources, backup

last full run: 2026-11-09T21:45:06.656573+00:00 · RoWatcher requests by day: {"2026-11-06": 533, "2026-11-07": 592, "2026-11-08": 592, "2026-11-09": 421}
alert cards by day: {"2026-11-06": 37, "2026-11-07": 32, "2026-11-08": 39, "2026-11-09": 40} · pings: {"2026-11-09": 6}
alerts waiting for a slot: 34 · strongest: 0.60 🚀 Trend Score 83: Project Soul's [Undert; 0.59 🚀 Trend Score 82: [DISCO] Pok Pok; 0.59 🚀 Trend Score 81: Ship The Cargo 🚢; 0.39 🚀 Trend Score 79: Ragdoll Wars!; 0.38 🚀 Trend Score 77: Ragdoll Verity Sandbox
yesterday's alert priorities: 0 alerts · top 12th = — · —

alert type → chance it's followed by an explosion (starting guess → now, matured alerts behind it):
- predict: 0.350 → 0.350 (0 matured)
- chart: 0.350 → 0.350 (0 matured)
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
- new: 0.055 → 0.055 (0 matured)
- update: 0.050 → 0.050 (0 matured)
- early: 0.040 → 0.040 (0 matured)

outside sources last worked: {"steam": "2026-11-09T01:01:49.189491+00:00", "wikipedia": "2026-11-09T01:01:49.189491+00:00", "calendar": "2026-11-09T01:01:49.189491+00:00", "yt_trending": "2026-11-09T17:41:36.169371+00:00"}
outside sources failing today: {} · Wikipedia days held: ['2026-10-22']
backfill by status: {"error": 91, "error:1": 3, "ok": 1723, "ok-old": 712}
worldwide trending lists last read: 2026-11-09T21:32:34.320859+00:00 · games in them: 140 · theme words saved for search: ['zero', 'ship', 'deep', 'hotel', 'monster', 'heaven', 'cozy', 'among', 'pack', 'west', 'flying', 'hospital', 'voice', 'pass', 'fighter']
title tags currently treated as Roblox events: {"the hollow": "2026-10-26"}
backup: encrypted backup saved (33.9 MB)

_0.0s_

## Digest and weekly cards, built from today's data (not posted)

daily digest: 5 cards built — 📊 Daily digest · Mon 09 Nov · 🎮 Games to watch · 🌱 Trends · 🔮 Coming up & outside Roblox · 👀 Watchlist

weekly report: 9 cards built — 🗓️ Weekly report · week to Mon 09 Nov · 🧭 Mechanics: biggest moves · 🧠 What Roblox's algorithm is rewarding · 🏛️ Long-term games · ⏱ Engagement (from badges) · 🧩 What lasting games have in common · 📈 Forecasts & how long hits last · 🛠️ Do updates, icons and titles help? · 🔬 Are the predictions working?

**📊 Daily digest · Mon 09 Nov**
🚀 **Biggest riser:** [(NEW QUEST & MODIFFICATION) Onthe…](https://www.roblox.com/games/110534393529784) — ×64.5 to 1.4K
🔥 **Hottest across platforms:** [Throw Food For Animals](https://www.roblox.com/games/120219252362013) — heat 70
⏱ **Most playtime per player:** [(⚡) Steal a Superpower!](https://www.roblox.com/games/74183246285569) — 82 min/day
🔮 **Coming up:** Lucky Debt (out 8 days ago) — 🌉 1 new Roblox game already
⚠️ **Watchlist falling:** Eat Everything In A Grocery Store -61% week on week
📥 **Also flagged** (didn't make the day's 12 alert cards; strongest first): 🚀 Surging: Chop and Steal an Egg; 🌍 Climbing abroad first: (CHAPTER 2) Left 4 Death; 🌍 Climbing abroad first: Ice Cream Shop [Anomaly] 🍦; 🌍 Climbing abroad first: [✈️UPD] Be a Pilot! ; 🌍 Climbing abroad first: Bloody Ragdoll Physics 🩸 (+170 more)
🎃 **After Halloween:** 12% of games still carry Halloween tags. The event is over, so week-on-week falls right now are mostly that event unwinding, not games failing

**🎮 Games to watch**
**[Compliment](https://rowatcher.com/games/10772422537)** — 1.9K playing · 18d old · **×8.1** 🔥67 📺901.0K
**[Low Range: Offroad 4x4 (EARLY ACC…](https://www.roblox.com/games/88131802740480)** — 7.1K playing · 31d old · **×5.8** 🔥59
**[(⚡) Steal a Superpower!](https://www.roblox.com/games/74183246285569)** — 15.3K playing · 30d old · **×55.5** 🔥59 ⏱82m
**[WRECKED (Realistic Crashes)](https://www.roblox.com/games/77843690602580)** — 5.9K playing · 14d old · **×30.8** 🔥55
**[(🐟) Net a Fish!](https://www.roblox.com/games/93898234979111)** — 14.4K playing · 25d old · **×6.8** 🔥55
**[Untitled Symbiote Suit Game (VENO…](https://www.roblox.com/games/87483534479816)** — 8.3K playing · 15d old · **×37.5** 🔥55
**[Ragdoll Physics 🩸](https://www.roblox.com/games/121868512253414)** — 32.5K playing · 28d old · **×10.1** 🔥55
**[Makeup Salon💄](https://www.roblox.com/games/126608757616138)** — 2.8K playing · 35d old · **×5.9** 🔥54

**🗓️ Weekly report · week to Mon 09 Nov**
🎃 **After Halloween:** 12% of games still carry Halloween tags. The event is over, so week-on-week falls right now are mostly that event unwinding, not games failing
🧭 **Demand:** Disasters / survival +10% · Anomaly / night shift -33%
🏛️ **Most long-term genre:** Social — 60% of its games reliably hold players on weekdays (all genres: 17%)
📏 **Stickiest young game:** [Steal A Balut](https://www.roblox.com/games/90773083590844) — 92/100
⏱ **Most playtime (young):** [Oregon Trail (new!)](https://www.roblox.com/games/124172969655058) — 163 min/player/day

**🧭 Mechanics: biggest moves**
🔴 **Anomaly / night shift** · 309.2K (-33%) · 2 new
🔴 **Eat / grow big** · 79.6K (-24%) · 7 new · 1 hit
🔴 **Horror** · 71.4K (-22%) · 2 new · 2 hits
🔴 **Care / baby / pets** · 542.8K (-21%) · 7 new
🔻 **Fashion / makeup** · 123.4K (-14%) · 0 new
🔴 **Obby / parkour** · 178.2K (-13%) · 13 new · 4 hits
💥 59 breakouts: [Steal A Balut](https://www.roblox.com/games/90773083590844), [Survive Your Ideas](https://www.roblox.com/games/77900175935766), [Ragdoll Physics 🩸](https://www.roblox.com/games/121868512253414)

**🧠 What Roblox's algorithm is rewarding**
🟥🟥🟥 favourite rate
🟥🟥🟥🟥 weekday hold vs a typical game — _games that keep a steady crowd all week rarely jump 50% in a week, so this mostly means "already settled", not that Roblox punishes retention_
🟥🟥🟥🟥🟥🟥 revenue per player — _fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation_
🧪 enters a Roblox chart within 7 days: predictions the bot made scored **0.64** · top 10% came true 14% vs 7.0% overall
🧪 players up 50%+ within 7 days: predictions the bot made scored **0.78** · top 10% came true 33% vs 7.8% overall

**🏛️ Long-term games**
Weekday hold is 72% the game, 28% week-to-week noise — so one good week proves little
**Social** · 60% long-term (6/10, likely 35%–81%) ✅
**RPG** · 35% long-term (12/34, likely 23%–49%) ✅
**Simulation** · 18% long-term (69/375, likely 15%–22%)
**Obby & Platformer** · 19% long-term (11/58, likely 12%–29%)
**Sports & Racing** · 21% long-term (6/29, likely 11%–35%)
Young games already long-term: [Free Fire Zone (Max)](https://www.roblox.com/games/99610146753435), [(⚔️UPD) +1 Venom Evolut…](https://www.roblox.com/games/116448925875915), [Pixel Lineage (Dawn Upd…](https://www.roblox.com/games/126256942507957)
Stickiest young games: [Steal A Balut](https://www.roblox.com/games/90773083590844) (92), [Club Legacy Soccer Ma…](https://www.roblox.com/games/119363206449928) (91), [(🫧CH3) 1M Clicks To E…](https://www.roblox.com/games/138666683767450) (91)

**⏱ Engagement (from badges)**
Typical game: **54 min** per player per day (292 games measured)
⏱ [Oregon Trail (new!)](https://www.roblox.com/games/124172969655058) · **163 min** · 46.1K/day
⏱ [(🥷NINJA) Anime Legacy Simulator](https://www.roblox.com/games/106198175232796) · **145 min** · 50.1K/day
⏱ [Chop A Forest](https://www.roblox.com/games/103363457515322) · **118 min** · 105.7K/day
⏱ [(🎃)+1 Assassin Leveling](https://www.roblox.com/games/120731410233153) · **115 min** · 101.0K/day

**🧩 What lasting games have in common**
✅ leaderboards · **2.0×** as likely to be long-term (likely 1.2–3.3×, 69 games)
🧪 Stickiness can't be checked against survival until 2026-11-25 (needs games watched from the start, 4 weeks on)

**📈 Forecasts & how long hits last**
📈 Peak forecasts (made on day 5): typically off by **74%**; 54% within 2× of the real peak (573 games)
   ↳ not proven enough to quote numbers (needs 30+ games with 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **18%** of the time vs 22% for any young game (208 firings) · **alerts paused** until it beats that by 1.3× over 20+ firings
⏳ A typical hit keeps half its peak players for **11 days** (926 games; 399 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: average weekday hold **13d** (117) · holds weekday players well **12d** (187) · holds them poorly **8d** (25)
By mechanic: Care / baby / pets **13d** (15) · Anime / fighting style **12d** (23) · Roleplay / life **11d** (44) · Sports **10d** (30)
By genre: RPG **12d** (35) · Roleplay & Avatar Sim **11d** (53) · Party & Casual **11d** (49) · Strategy **11d** (25)

**🛠️ Do updates, icons and titles help?**
▫️ Updates after a quiet week: measuring (18 so far)
▫️ **Icon changes**: +7% (likely -3% to +15%) vs similar games that changed nothing · 47% beat them by 10%+ (136 measured)
▫️ **Title changes**: +1% (likely -1% to +2%) vs similar games that changed nothing · 38% beat them by 10%+ (1260 measured)
🖼️ 6 young games use an icon nearly identical to a hit from another studio (last 30 days)

**🔬 Are the predictions working?**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **starting formula**
• Starting formula vs real outcomes: accuracy **0.66** (likely 0.58–0.74) · its top 10% took off 16% of the time vs 6.8% for all · 501 snapshots over 1 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 501 / 34 over 1 day)
🎯 Explosion model: not provable yet (too few finished explosions among games watched live) — its picks aren't used
🌱 Theme model: still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20)

_5.0s_

## Trend Score

snapshots old enough to score: 585 over 1 days (2026-10-26 → 2026-10-26)

take-off rate by size at the time of the snapshot (took off / snapshots):
| definition | <500 | 500–2K | 2K–10K | 10K+ | all |
|---|---|---|---|---|---|
| old (2× and 1,000, one day) | 11/19 (57.9%) | 47/218 (21.6%) | 21/213 (9.9%) | 2/51 (3.9%) | 81/501 (16.2%) |
| 2× and 5,000, one day | 1/19 (5.3%) | 17/218 (7.8%) | 19/213 (8.9%) | 2/51 (3.9%) | 39/501 (7.8%) |
| NEW (2× and 5,000, two days) | 1/19 (5.3%) | 14/218 (6.4%) | 17/213 (8.0%) | 2/51 (3.9%) | 34/501 (6.8%) |
| 2× and 2,000, two days | 4/19 (21.1%) | 35/218 (16.1%) | 18/213 (8.5%) | 2/51 (3.9%) | 59/501 (11.8%) |

starting formula vs the NEW outcome: {"n": 501, "pos": 34, "auc": 0.663, "base": 0.068, "top": 0.16, "top_n": 50, "lo": 0.578, "hi": 0.74}
scores as shown at the time vs the NEW outcome: AUC 0.663
- shown 50–100: 5/14 took off (36%)
- shown 25–50: 1/17 took off (6%)
- shown 10–25: 7/51 took off (14%)
- shown 0–10: 21/419 took off (5%)
starting-formula raw scores (10/25/50/75/90th pct): 0.0105 / 0.0143 / 0.0244 / 0.0532 / 0.166
calibration of the starting formula: {"n": 501, "pos": 34, "days": 1, "cal": null, "auc": 0.663, "lo": 0.578, "hi": 0.74, "base": 0.068, "top": 0.16}
learned model status: {"day": "2026-11-09", "examples": 501, "positives": 34, "days": 1, "trained": false, "why": "needs 2000+ outcomes with 60+ take-offs over 21+ days (has 501 / 34 over 1 day)"}

_0.3s_

## Weekday hold: old vs new definition

**OLD: Tue–Wed vs Sat–Sun** — games rated: 2,381 · weeks rated per game: 1 / 1 / 2 / 6 / 8 · week-to-week rank correlation: 0.522 (5,345 pairs) · share of one week's spread that is the game itself: 0.651 · noise sd 0.238 · old-rule 'long-term': 505 of 1683 with 2+ weeks (30%)
**NEW: Mon–Wed vs two busiest of Fri–Sun** — games rated: 2,408 · weeks rated per game: 1 / 1 / 2 / 6 / 8 · week-to-week rank correlation: 0.524 (5,377 pairs) · share of one week's spread that is the game itself: 0.719 · noise sd 0.209 · old-rule 'long-term': 506 of 1692 with 2+ weeks (30%)

games the OLD measure flattered most (old ÷ new relative hold):
- Hide ur Secret Base — ×3.91 (2 weeks)
- Fat And Skinny [ 2 Player Obby ] — ×2.44 (2 weeks)
- SUNYI [HORROR] — ×2.21 (2 weeks)
- Where Is Fahd? — ×2.21 (2 weeks)
- Kopdes Shift Anomalies (Update) — ×2.02 (2 weeks)
- UNTITLED RPG GAME — ×2.01 (2 weeks)
- [KR] Bell or Die! 🔔 — ×1.73 (2 weeks)
- [🎃] Shoot For Eggs — ×1.68 (2 weeks)
- Escooter Life [🎃] — ×1.57 (2 weeks)
- [⚔️] BEYBLADE X-BATTLES [Beta13.1] — ×1.52 (2 weeks)
- [🎲] The Game Of Life — ×1.51 (2 weeks)
- Draw a Pancake! 🥞 — ×1.50 (2 weeks)

after the new rule: hold_meta {"week": "2026-11-04", "weekend": ["2026-10-31", "2026-11-01"], "weekday": ["2026-11-03", "2026-11-04"], "benchmark": 0.696, "roblox": 0.673, "weeks": 8, "reliability": 0.719, "noise_sd": 0.209} · long-term 152 · promising 340
- [🌎W10] Throw a Coin — 1.551× over 8 weeks (z 6.24) · 5.7K
- TANPANAMA — 1.532× over 8 weeks (z 6.07) · 4.3K
- [🍂] Anime Dice — 1.563× over 7 weeks (z 5.98) · 78.2K
- [EVENT🎃] Noob Incremental — 1.518× over 8 weeks (z 5.93) · 5.5K
- Free Fire Zone (Max) — 1.812× over 3 weeks (z 5.58) · 9.6K
- [UPD] Anime RNG Defense — 1.478× over 8 weeks (z 5.55) · 3.3K
- [UPD 12] Defeat Anime RNG  — 1.499× over 7 weeks (z 5.42) · 6.0K
- Forest Market — 1.462× over 8 weeks (z 5.4) · 3.7K
- [🎃Part 2] 🔩 Resource Incremental — 1.432× over 8 weeks (z 5.1) · 1.9K
- Sol's RNG [ Halloween Event 🎃] — 1.423× over 8 weeks (z 5.02) · 44.4K
- Bee Swarm Simulator — 1.401× over 8 weeks (z 4.8) · 33.9K
- [⚔️UPD] +1 Venom Evolution — 1.66× over 3 weeks (z 4.75) · 38.6K

_1.7s_

## What changes do (matched comparison)

games watched for publishes: 862 · publish days seen: 2,270 · publishes after a quiet week: 99
naive measure (day+3 vs the 3 days before), every publish: median -12.5% over 951 · by weekday of the publish: Mon -43% (88), Tue -29% (137), Wed +13% (178), Thu +20% (110), Fri -13% (111), Sat -14% (170), Sun -23% (157)
measured now: 0 changes
- icon: 235 events · 205 with complete weeks · 136 with enough twins
- title: 2318 events · 1412 with complete weeks · 1260 with enough twins
- update: 26 events · 24 with complete weeks · 18 with enough twins
• Updates after a quiet week: measuring — 18 measured so far (needs 20)
• ▫️ **Icon changes**: typical lift **+7%** (likely -3% to +15%) vs similar games that changed nothing · 47% beat their twins by 10%+, 40% fell 10%+ behind · 136 measured
   ↳ the games themselves went -20% week on week while their twins went -25% — the naive before/after number is mostly that drift
• ▫️ **Title changes**: typical lift **+1%** (likely -1% to +2%) vs similar games that changed nothing · 38% beat their twins by 10%+, 36% fell 10%+ behind · 1260 measured
   ↳ the games themselves went -11% week on week while their twins went -10% — the naive before/after number is mostly that drift
_Lift = the game's week-on-week change divided by the median change of similar-size, similar-trend games that made no such change. Correlation still, but weekdays, natural decay and market swings are removed._

_0.8s_

## Themes

themes: 2,981 · calm candidate days: 29,092 · breakouts: 133 in 133 themes · history starts 2026-08-25
themes that broke out (count · name · most games): 1× walls escape (3); 1× walls (8); 1× verity (32); 1× together (17); 1× throw (12); 1× thai (7); 1× tesla (3); 1× survival (43); 1× steal eggs (8); 1× steal egg (14); 1× scooter (10); 1× say (3); 1× save (16); 1× sandbox (23); 1× roadster (4); 1× ride (46); 1× realistic (23); 1× ragdoll physics (6); 1× punch (8); 1× prison (69); 1× playground (20); 1× pixel (15); 1× physics (16); 1× pets (16); 1× makeup (12)

model status: {"examples": 0, "positives": 0, "trained": false, "day": "2026-11-09", "themes": 0, "base_rate": null, "why": "needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20)"}

top themes it would show today:
- zero — model None · 5 signals · 6 games, 2 hits, 0 young hits, 0 new
- ship — model None · 4 signals · 2 games, 1 hits, 1 young hits, 0 new
- deep — model None · 3 signals · 2 games, 2 hits, 0 young hits, 0 new
- hotel — model None · 3 signals · 3 games, 2 hits, 1 young hits, 0 new
- monster — model None · 3 signals · 6 games, 2 hits, 1 young hits, 0 new
- heaven — model None · 3 signals · 4 games, 1 hits, 1 young hits, 0 new
- cozy — model None · 3 signals · 3 games, 2 hits, 1 young hits, 0 new
- among — model None · 2 signals · 2 games, 0 hits, 0 young hits, 0 new
- pack — model None · 2 signals · 2 games, 1 hits, 0 young hits, 0 new
- west — model None · 2 signals · 2 games, 1 hits, 0 young hits, 0 new
- flying — model None · 2 signals · 2 games, 1 hits, 1 young hits, 0 new
- hospital — model None · 2 signals · 5 games, 2 hits, 0 young hits, 0 new

🌱 **Theme model** (a small theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days; established themes with more than 2 hits aren't candidates)
• Still collecting — needs 200+ calm theme-days with 8+ breakouts from days the bot watched live (has 0 / 0; the first live days finish their 21-day window on 2026-11-20).

🔬 **Which indicators actually work** (0 theme breakouts tracked so far)
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📈 theme doubled in a week, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

_3.6s_

## Algorithm mirror

**chart**: 1,284 game-days over 9 days (2026-10-24 → 2026-11-01) · 67 positive (5.2%) · games: 1,044
**growth**: 5,182 game-days over 28 days (2026-10-05 → 2026-11-01) · 593 positive (11.4%) · games: 2,190

chart: coverage {"playtime": 0.02, "returning": 0.0, "first_step": 0.008, "sessions": 0.019, "hold": 0.481, "session_len": 0.963, "like_ratio": 0.925, "fav_conv": 0.879, "rev_per_player": 0.871, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
chart: stability {"playtime": {"w": 0.098, "lo": -0.114, "hi": 0.331, "sign": 0.7}, "first_step": {"w": -0.059, "lo": -0.174, "hi": 0.141, "sign": 0.767}, "sessions": {"w": 0.034, "lo": -0.112, "hi": 0.287, "sign": 0.6}, "hold": {"w": -0.27, "lo": -0.418, "hi": -0.075, "sign": 1.0}, "session_len": {"w": 0.251, "lo": 0.048, "hi": 0.5, "sign": 0.983}, "like_ratio": {"w": 0.285, "lo": 0.026, "hi": 0.69, "sign": 0.983}, "fav_conv": {"w": -0.241, "lo": -0.61, "hi": 0.016, "sign": 0.933}, "rev_per_player": {"w": -0.375, "lo": -0.662, "hi": -0.126, "sign": 1.0}, "size": {"w": 0.774, "lo": 0.613, "hi": 1.094, "sign": 1.0}, "momentum": {"w": 0.452, "lo": 0.28, "hi": 0.711, "sign": 1.0}, "age": {"w": -0.311, "lo": -0.578, "hi": -0.024, "sign": 0.983}, "has_badges": {"w": 0.235, "lo": 0.035, "hi": 0.386, "sign": 0.967}}
chart: wf {"folds": 0, "horizon": 8, "test_from": null}

growth: coverage {"playtime": 0.057, "returning": 0.0, "first_step": 0.025, "sessions": 0.056, "hold": 0.484, "session_len": 0.942, "like_ratio": 0.944, "fav_conv": 0.903, "rev_per_player": 0.896, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
growth: stability {"playtime": {"w": -0.139, "lo": -0.288, "hi": 0.023, "sign": 0.917}, "first_step": {"w": 0.002, "lo": -0.083, "hi": 0.084, "sign": 0.5}, "sessions": {"w": 0.111, "lo": -0.055, "hi": 0.347, "sign": 0.867}, "hold": {"w": -0.222, "lo": -0.502, "hi": -0.064, "sign": 0.983}, "session_len": {"w": 0.008, "lo": -0.155, "hi": 0.162, "sign": 0.45}, "like_ratio": {"w": -0.018, "lo": -0.123, "hi": 0.12, "sign": 0.617}, "fav_conv": {"w": -0.071, "lo": -0.223, "hi": 0.015, "sign": 0.9}, "rev_per_player": {"w": -0.324, "lo": -0.52, "hi": -0.188, "sign": 1.0}, "size": {"w": -0.437, "lo": -0.676, "hi": -0.265, "sign": 1.0}, "momentum": {"w": 0.911, "lo": 0.796, "hi": 1.023, "sign": 1.0}, "age": {"w": -0.298, "lo": -0.448, "hi": -0.142, "sign": 1.0}, "has_badges": {"w": 0.067, "lo": -0.217, "hi": 0.224, "sign": 0.667}}
growth: wf {"folds": 4, "horizon": 8, "test_from": null, "lr": {"n": 2532, "pos": 272, "auc": 0.575, "base": 0.1074, "top": 0.1383, "top_n": 253, "lo": 0.5453, "hi": 0.6011}, "gbm": {"n": 2532, "pos": 272, "auc": 0.7982, "base": 0.1074, "top": 0.4387, "top_n": 253, "lo": 0.7667, "hi": 0.8255}, "p_trees_better": 1.0, "diff": 0.2239}
- chart, 0-day purge: simple 0.836 · trees 0.867 · n 624 · folds 4
- chart, 8-day purge: simple None · trees None · n None · folds 0
- growth, 0-day purge: simple 0.728 · trees 0.822 · n 4168 · folds 4
- growth, 8-day purge: simple 0.575 · trees 0.798 · n 2532 · folds 4

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

_14.6s_

## Explosion model

examples: 257 · exploded: 12 · first noticed on a backfilled day (before the bot watched): 257 (12 exploded) vs live: 0 (0 exploded)
first-noticed dates: 2026-08-08 → 2026-10-18 · by month: {"2026-08": [20, 1], "2026-09": [72, 3], "2026-10": [165, 8]}
log10(peak after ÷ players the day after noticing): 0.0675 / 0.203 / 0.456 / 0.763 / 1.13
status: {"examples": 257, "positives": 12, "trained": true, "day": "2026-11-09", "live_examples": 0, "live_positives": 0, "champion": "simple", "wf": {"folds": 0, "horizon": 21, "test_from": "2026-10-22"}, "test_n": null, "test_pos": null, "test_top10_hit": null, "base_rate": 0.04669260700389105, "stable": ["players_d1", "growth_d1", "visits_d1", "age", "studio_best", "crowd", "mech_hits"]}

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

_3.1s_

## Stickiness and lasting features

games scored: 2606 · weights {"hold_rel": 0.3, "playtime": 0.2, "session_min": 0.15, "level_kept": 0.15, "fav_conv": 0.1, "rev_per_ccu": 0.1} · per-signal rank correlation with players kept 4 weeks later: {} · n 0 · honest cross-check null
description features: 152 long-term vs 761 others · checked 16
- leaderboards: lift 1.96 (1.17–3.27) · 69 games · reliable: True
- offline / idle earnings: lift 1.72 (1.0–2.97) · 70 games · reliable: False
- codes: lift 1.41 (0.85–2.32) · 112 games · reliable: False
- pets / collecting: lift 1.25 (0.82–1.9) · 219 games · reliable: False
- group rewards: lift 1.1 (0.67–1.82) · 144 games · reliable: False
- trading: lift 1.39 (0.61–3.18) · 35 games · reliable: False
- daily rewards / streaks: lift 1.6 (0.58–4.38) · 19 games · reliable: False
- quests / missions: lift 1.11 (0.53–2.3) · 60 games · reliable: False
- rebirth / prestige: lift 1.13 (0.51–2.52) · 48 games · reliable: False
- limited events: lift 0.93 (0.43–2.03) · 64 games · reliable: False
- base building / decorating: lift 0.74 (0.43–1.28) · 170 games · reliable: False
- PvP: lift 0.82 (0.32–2.06) · 51 games · reliable: False

_2.0s_

## Money: top earners under 5K players

games with earnings: 2,625 · $/player/month percentiles: 1.53 / 9.49 / 23 / 66.1 · flagged as suspect: 37
- [🎃]+1 Loot To Forge — $337,455/month · 3666 players · $92/player · suspect: True
- Sarab — $266,779/month · 4923 players · $54/player · suspect: False
- Build An Ant Empire — $237,725/month · 2752 players · $86/player · suspect: True
- [UPD 6] Anime Zero — $217,045/month · 1563 players · $139/player · suspect: True
- Bunker vs Verity — $193,301/month · 4574 players · $42/player · suspect: False
- [⚔️] Search For The Needle — $188,120/month · 2756 players · $68/player · suspect: True
- Steal Animal Egg — $181,926/month · 643 players · $283/player · suspect: True
- [🐎BIZARRE] Anime Breaker — $181,556/month · 4907 players · $37/player · suspect: False

_0.2s_

## Badge streaks

games with badge data: 292 · with a 7-day streak badge: 9
- [GAMEMODES!] Illegal Soccer: [7, 0.1182] · base: players who earn "First Tackle"
- 7 Days Cat-Sitting: [10, 0.0006] · base: players who earn "Haunted House"
- Firefighting Sim 🚒: [7, 0.0226] · base: players who earn "First Alarm"
- [UPD🌀] UNDERTALE Fight!: [7, 0.0005] · base: players who earn "PLAY UNDERTALE FIGHT!"
- Pet Store Tycoon: [7, 0.0981] · base: new players
- Punch Out Of Prison: [7, 0.0009] · base: new players
- The Block: [5, 0.0] · base: players who earn "Best Audience Award"
- Become the Potato!: [7, 0.0] · base: new players
- [UPD 2] Crack THE Geode!: [7, 0.0003] · base: new players

_0.0s_

## Model check as the bot would now print it

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

_3.8s_
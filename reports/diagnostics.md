# Diagnostics · 2026-11-09

_generated 2026-11-09T21:34:30Z · models retrained in memory only_

## Tables and coverage

- games: 8,137
- daily: 156,041
- hourly: 715,241
- alerts: 2,449
- predictions: 400
- backfill: 2,518
- trend_feats: 9,643
- promo_preds: 45,031
- theme_daily: 44,215
- theme_preds: 22,062
- hold_weekly: 8,834
- engage_weekly: 11,845
- fc_preds: 13,308
- cp_fires: 83
- renames: 3,807
- effects: 0
- upstream: 69,834
- database file: 118 MB
- daily covers 2026-07-26 → 2026-11-09 (107 days)

game-days per day, last 21 days (live / backfill / other):
- 2026-10-19: 0 / 1,878 / 0 · most readings of one game that day (≈ runs): 1033
- 2026-10-20: 0 / 1,921 / 0 · most readings of one game that day (≈ runs): 1035
- 2026-10-21: 0 / 1,959 / 0 · most readings of one game that day (≈ runs): 1006
- 2026-10-22: 6,046 / 176 / 15 · most readings of one game that day (≈ runs): 293
- 2026-10-23: 6,030 / 174 / 23 · most readings of one game that day (≈ runs): 294
- 2026-10-24: 6,084 / 185 / 29 · most readings of one game that day (≈ runs): 295
- 2026-10-25: 6,081 / 207 / 18 · most readings of one game that day (≈ runs): 294
- 2026-10-26: 2,836 / 670 / 42 · most readings of one game that day (≈ runs): 295
- 2026-10-27: 2,888 / 633 / 43 · most readings of one game that day (≈ runs): 295
- 2026-10-28: 2,764 / 630 / 47 · most readings of one game that day (≈ runs): 295
- 2026-10-29: 2,790 / 622 / 59 · most readings of one game that day (≈ runs): 295
- 2026-10-30: 2,824 / 597 / 66 · most readings of one game that day (≈ runs): 295
- 2026-10-31: 2,796 / 599 / 77 · most readings of one game that day (≈ runs): 295
- 2026-11-01: 2,769 / 601 / 85 · most readings of one game that day (≈ runs): 295
- 2026-11-02: 2,797 / 556 / 118 · most readings of one game that day (≈ runs): 295
- 2026-11-03: 2,790 / 570 / 134 · most readings of one game that day (≈ runs): 98
- 2026-11-04: 2,848 / 532 / 141 · most readings of one game that day (≈ runs): 161
- 2026-11-05: 2,823 / 520 / 161 · most readings of one game that day (≈ runs): 294
- 2026-11-06: 2,825 / 447 / 173 · most readings of one game that day (≈ runs): 294
- 2026-11-07: 2,712 / 329 / 196 · most readings of one game that day (≈ runs): 294
- 2026-11-08: 2,721 / 199 / 222 · most readings of one game that day (≈ runs): 295
- 2026-11-09: 2,725 / 79 / 9 · most readings of one game that day (≈ runs): 266
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
- longterm: 0.07 MB

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
- new: 641 · 2026-10-22 · 2026-11-09 · 231
- surge: 600 · 2026-10-23 · 2026-11-09 · 282
- abroad: 486 · 2026-10-26 · 2026-11-09 · 253
- copy: 210 · 2026-10-23 · 2026-11-09 · 118
- breakout: 161 · 2026-10-23 · 2026-11-09 · 50
- early: 135 · 2026-10-22 · 2026-11-09 · 65
- chart: 69 · 2026-10-22 · 2026-11-09 · 25
- longterm: 46 · 2026-10-24 · 2026-11-05 · 30
- update: 43 · 2026-10-22 · 2026-11-08 · 22
- heat: 34 · 2026-10-25 · 2026-11-09 · 16
- studio: 15 · 2026-10-28 · 2026-11-09 · 12
- predict: 9 · 2026-10-30 · 2026-11-08 · 4

update events kept in memory: 400 (cap 400) · with a day-3 result: 31 · dates 2026-11-03 → 2026-11-09
icon/title changes in memory: 1328 · kinds: {"icon": 584, "title": 744}
breakouts logged: 179 · days from breakout to peak, all: 0 / 0 / 1 / 4 / 8 · only those 14+ days old (55): 0 / 0 / 0 / 5 / 8

_0.0s_

## Plumbing: runs, alert cards, sources, backup

last full run: 2026-11-09T21:32:34.320859+00:00 · RoWatcher requests by day: {"2026-11-06": 533, "2026-11-07": 592, "2026-11-08": 592, "2026-11-09": 402}
alert cards by day: {"2026-11-06": 37, "2026-11-07": 32, "2026-11-08": 39, "2026-11-09": 38} · pings: {"2026-11-09": 4}
alerts waiting for a slot: 13 · strongest: 0.35 📈 Entered Roblox's algorithm charts: [GO; 0.31 🆕 Just crossed 2.0K players: 🧟 ZOMBIE MO; 0.28 🌍 Climbing abroad first: 🎨 Draw the Othe; 0.20 🌍 Climbing abroad first: [😈DEVIL UNIONS]; 0.16 🆕 Just crossed 2.0K players: Build and S
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
backfill by status: {"error": 91, "error:1": 1, "ok": 1717, "ok-old": 709}
worldwide trending lists last read: 2026-11-09T21:32:34.320859+00:00 · games in them: 140 · theme words saved for search: []
title tags currently treated as Roblox events: {"the hollow": "2026-10-26"}
backup: encrypted backup saved (33.0 MB)

_0.0s_

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

_0.2s_

## Weekday hold: old vs new definition

**OLD: Tue–Wed vs Sat–Sun** — games rated: 2,381 · weeks rated per game: 1 / 1 / 2 / 6 / 8 · week-to-week rank correlation: 0.521 (5,337 pairs) · share of one week's spread that is the game itself: 0.651 · noise sd 0.238 · old-rule 'long-term': 504 of 1682 with 2+ weeks (30%)
**NEW: Mon–Wed vs two busiest of Fri–Sun** — games rated: 2,408 · weeks rated per game: 1 / 1 / 2 / 6 / 8 · week-to-week rank correlation: 0.524 (5,370 pairs) · share of one week's spread that is the game itself: 0.719 · noise sd 0.209 · old-rule 'long-term': 506 of 1691 with 2+ weeks (30%)

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

after the new rule: hold_meta {"week": "2026-11-04", "weekend": ["2026-10-31", "2026-11-01"], "weekday": ["2026-11-03", "2026-11-04"], "benchmark": 0.696, "roblox": 0.673, "weeks": 8, "reliability": 0.719, "noise_sd": 0.209} · long-term 152 · promising 341
- [🌎W10] Throw a Coin — 1.551× over 8 weeks (z 6.23) · 5.7K
- TANPANAMA — 1.532× over 8 weeks (z 6.06) · 4.3K
- [🍂] Anime Dice — 1.563× over 7 weeks (z 5.98) · 78.2K
- [EVENT🎃] Noob Incremental — 1.518× over 8 weeks (z 5.93) · 5.5K
- Free Fire Zone (Max) — 1.812× over 3 weeks (z 5.57) · 9.6K
- [UPD] Anime RNG Defense — 1.478× over 8 weeks (z 5.55) · 3.3K
- [UPD 12] Defeat Anime RNG  — 1.499× over 7 weeks (z 5.42) · 6.0K
- Forest Market — 1.461× over 8 weeks (z 5.39) · 3.7K
- [🎃Part 2] 🔩 Resource Incremental — 1.431× over 8 weeks (z 5.09) · 1.9K
- Sol's RNG [ Halloween Event 🎃] — 1.423× over 8 weeks (z 5.01) · 44.4K
- Bee Swarm Simulator — 1.401× over 8 weeks (z 4.79) · 33.9K
- [⚔️UPD] +1 Venom Evolution — 1.66× over 3 weeks (z 4.75) · 38.6K

_0.9s_

## What changes do (matched comparison)

games watched for publishes: 834 · publish days seen: 2,191 · publishes after a quiet week: 96
naive measure (day+3 vs the 3 days before), every publish: median -12.5% over 951 · by weekday of the publish: Mon -43% (88), Tue -29% (137), Wed +13% (178), Thu +20% (110), Fri -13% (111), Sat -14% (170), Sun -23% (157)
measured now: 2579 changes
- icon: 235 events · 205 with complete weeks · 136 with enough twins
- title: 2318 events · 1410 with complete weeks · 1258 with enough twins
- update: 26 events · 24 with complete weeks · 18 with enough twins
• Updates after a quiet week: measuring — 18 measured so far (needs 20)
• ▫️ **Icon changes**: typical lift **+7%** (likely -3% to +15%) vs similar games that changed nothing · 47% beat their twins by 10%+, 40% fell 10%+ behind · 136 measured
   ↳ the games themselves went -20% week on week while their twins went -25% — the naive before/after number is mostly that drift
• ▫️ **Title changes**: typical lift **+1%** (likely -1% to +3%) vs similar games that changed nothing · 38% beat their twins by 10%+, 36% fell 10%+ behind · 1258 measured
   ↳ the games themselves went -11% week on week while their twins went -10% — the naive before/after number is mostly that drift
_Lift = the game's week-on-week change divided by the median change of similar-size, similar-trend games that made no such change. Correlation still, but weekdays, natural decay and market swings are removed._

_8.2s_

## Themes

themes: 2,980 · calm candidate days: 29,055 · breakouts: 133 in 133 themes · history starts 2026-08-25
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

_2.4s_

## Algorithm mirror

**chart**: 1,302 game-days over 9 days (2026-10-24 → 2026-11-01) · 46 positive (3.5%) · games: 1,051
**growth**: 5,178 game-days over 28 days (2026-10-05 → 2026-11-01) · 613 positive (11.8%) · games: 2,225

chart: coverage {"playtime": 0.019, "returning": 0.0, "first_step": 0.01, "sessions": 0.019, "hold": 0.486, "session_len": 0.975, "like_ratio": 0.938, "fav_conv": 0.889, "rev_per_player": 0.886, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
chart: stability {"playtime": {"w": -0.019, "lo": -0.17, "hi": 0.151, "sign": 0.467}, "first_step": {"w": 0.17, "lo": 0.04, "hi": 0.331, "sign": 1.0}, "sessions": {"w": 0.1, "lo": -0.161, "hi": 0.322, "sign": 0.783}, "hold": {"w": -0.196, "lo": -0.389, "hi": -0.051, "sign": 0.983}, "session_len": {"w": 0.471, "lo": 0.29, "hi": 0.79, "sign": 1.0}, "like_ratio": {"w": 0.353, "lo": 0.125, "hi": 0.625, "sign": 0.983}, "fav_conv": {"w": -0.159, "lo": -0.846, "hi": 0.107, "sign": 0.85}, "rev_per_player": {"w": -0.56, "lo": -0.787, "hi": -0.213, "sign": 1.0}, "size": {"w": 0.811, "lo": 0.538, "hi": 1.21, "sign": 1.0}, "momentum": {"w": 0.321, "lo": 0.165, "hi": 0.634, "sign": 1.0}, "age": {"w": -0.247, "lo": -0.603, "hi": 0.049, "sign": 0.917}, "has_badges": {"w": -0.025, "lo": -0.34, "hi": 0.103, "sign": 0.783}}
chart: wf {"folds": 0, "horizon": 8, "test_from": null}

growth: coverage {"playtime": 0.054, "returning": 0.0, "first_step": 0.021, "sessions": 0.054, "hold": 0.487, "session_len": 0.946, "like_ratio": 0.953, "fav_conv": 0.908, "rev_per_player": 0.901, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
growth: stability {"playtime": {"w": -0.19, "lo": -0.287, "hi": -0.075, "sign": 1.0}, "first_step": {"w": -0.027, "lo": -0.107, "hi": 0.054, "sign": 0.667}, "sessions": {"w": -0.065, "lo": -0.173, "hi": 0.107, "sign": 0.817}, "hold": {"w": -0.174, "lo": -0.34, "hi": -0.008, "sign": 0.967}, "session_len": {"w": 0.111, "lo": -0.02, "hi": 0.233, "sign": 0.867}, "like_ratio": {"w": 0.066, "lo": -0.07, "hi": 0.185, "sign": 0.717}, "fav_conv": {"w": 0.091, "lo": -0.027, "hi": 0.202, "sign": 0.85}, "rev_per_player": {"w": -0.252, "lo": -0.426, "hi": -0.047, "sign": 0.983}, "size": {"w": -0.34, "lo": -0.526, "hi": -0.247, "sign": 1.0}, "momentum": {"w": 0.794, "lo": 0.672, "hi": 0.958, "sign": 1.0}, "age": {"w": -0.361, "lo": -0.534, "hi": -0.168, "sign": 1.0}, "has_badges": {"w": -0.086, "lo": -0.264, "hi": 0.066, "sign": 0.85}}
growth: wf {"folds": 4, "horizon": 8, "test_from": null, "lr": {"n": 2553, "pos": 291, "auc": 0.4746, "base": 0.114, "top": 0.1176, "top_n": 255, "lo": 0.4443, "hi": 0.5023}, "gbm": {"n": 2553, "pos": 291, "auc": 0.7974, "base": 0.114, "top": 0.4549, "top_n": 255, "lo": 0.7739, "hi": 0.8252}, "p_trees_better": 1.0, "diff": 0.3253}
- chart, 0-day purge: simple 0.794 · trees 0.781 · n 625 · folds 4
- chart, 8-day purge: simple None · trees None · n None · folds 0
- growth, 0-day purge: simple 0.663 · trees 0.837 · n 4179 · folds 4
- growth, 8-day purge: simple 0.475 · trees 0.797 · n 2553 · folds 4

🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
🟥🟥 weekday hold vs a typical game (-0.18)
🟥🟥🟥🟥 revenue per player (-0.41) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, like ratio, new players reaching the next badge, sessions per player per day, favourite rate, playtime per player per day
• Model for *enters a Roblox chart within 7 days* (1,302 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (5,178 game-days): Honest test: accuracy **0.80** (likely between 0.77 and 0.83) · 0.5 = coin flip · top 10% picks came true **45%** of the time vs 11% for all · 2,553 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.47 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (18,548 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (21,341 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

_8.2s_

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
• 🆕 crossed 2K: — · 640 still in their 21-day window (35 already exploded)
• chart: — · 69 still in their 21-day window (28 already exploded)
• 👀 early warning: — · 108 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 356 still in their 21-day window (36 already exploded)
• 💥 breakout: — · 161 still in their 21-day window (29 already exploded)
• 🧬 copy wave: — · 166 still in their 21-day window (14 already exploded)
• longterm: — · 45 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 18 still in their 21-day window (5 already exploded)
• abroad: — · 405 still in their 21-day window (36 already exploded)
• studio: — · 15 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 153 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

_1.8s_

## Stickiness and lasting features

games scored: 2605 · weights {"hold_rel": 0.3, "playtime": 0.2, "session_min": 0.15, "level_kept": 0.15, "fav_conv": 0.1, "rev_per_ccu": 0.1} · per-signal rank correlation with players kept 4 weeks later: {} · n 0 · honest cross-check null
description features: 152 long-term vs 759 others · checked 16
- leaderboards: lift 1.96 (1.17–3.27) · 69 games · reliable: True
- offline / idle earnings: lift 1.72 (1.0–2.96) · 70 games · reliable: False
- codes: lift 1.4 (0.85–2.32) · 112 games · reliable: False
- pets / collecting: lift 1.25 (0.82–1.89) · 219 games · reliable: False
- group rewards: lift 1.11 (0.67–1.83) · 143 games · reliable: False
- trading: lift 1.39 (0.61–3.17) · 35 games · reliable: False
- daily rewards / streaks: lift 1.6 (0.58–4.37) · 19 games · reliable: False
- quests / missions: lift 1.11 (0.53–2.29) · 60 games · reliable: False
- rebirth / prestige: lift 1.13 (0.51–2.51) · 48 games · reliable: False
- limited events: lift 0.93 (0.43–2.02) · 64 games · reliable: False
- base building / decorating: lift 0.74 (0.42–1.28) · 170 games · reliable: False
- PvP: lift 0.81 (0.32–2.05) · 51 games · reliable: False

_1.2s_

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

_0.1s_

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
🟥🟥 weekday hold vs a typical game (-0.18)
🟥🟥🟥🟥 revenue per player (-0.41) — fast-growing games are full of new players who haven't paid yet, so this mostly means "is growing", not that Roblox punishes monetisation
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, like ratio, new players reaching the next badge, sessions per player per day, favourite rate, playtime per player per day
• Model for *enters a Roblox chart within 7 days* (1,302 game-days): Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (8-day outcomes).
• Model for *players up 50%+ within 7 days* (5,178 game-days): Honest test: accuracy **0.80** (likely between 0.77 and 0.83) · 0.5 = coin flip · top 10% picks came true **45%** of the time vs 11% for all · 2,553 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.47 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (18,548 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (21,341 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **learned**
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
• 🆕 crossed 2K: — · 640 still in their 21-day window (35 already exploded)
• chart: — · 69 still in their 21-day window (28 already exploded)
• 👀 early warning: — · 108 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 356 still in their 21-day window (36 already exploded)
• 💥 breakout: — · 161 still in their 21-day window (29 already exploded)
• 🧬 copy wave: — · 166 still in their 21-day window (14 already exploded)
• longterm: — · 45 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 18 still in their 21-day window (5 already exploded)
• abroad: — · 405 still in their 21-day window (36 already exploded)
• studio: — · 15 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 153 still in their 21-day window
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
⏳ A typical hit keeps half its peak players for **10 days** (1668 games; 1083 have dropped below half so far)
By weekday hold in the weeks BEFORE the peak: holds weekday players well **23d** (422) · average weekday hold **15d** (528) · holds them poorly **6d** (543)
By mechanic: Roleplay / life **14d** (79) · Anime / fighting style **12d** (39) · Eat / grow big **11d** (14) · Sports **10d** (46)
By genre: Social **33d** (19) · Shooter **31d** (57) · Obby & Platformer **19d** (116) · Action **16d** (123)

**📏 Stickiness weights**
weekday hold 30% · playtime per player 20% · session length 15% · players kept vs best week 15% · favourite rate 10% · revenue per player 10% — starting weights (0 of 300 game-weeks needed to learn)

📥 Past histories downloaded: **2,426** games (2,518 tried)

_2.3s_
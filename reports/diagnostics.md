# Diagnostics · 2026-11-09

_generated 2026-11-09T20:49:15Z · models retrained in memory only_

## Tables and coverage

- games: 8,126
- daily: 155,668
- hourly: 713,511
- alerts: 2,432
- predictions: 400
- backfill: 2,508
- trend_feats: 9,643
- promo_preds: 45,031
- theme_daily: 44,215
- theme_preds: 22,062
- hold_weekly: 8,834
- engage_weekly: 11,845
- fc_preds: 13,308
- cp_fires: 83
- renames: 3,794
- effects: 0
- upstream: 69,778
- database file: 118 MB
- daily covers 2026-07-26 → 2026-11-09 (107 days)

game-days per day, last 21 days (live / backfill / other):
- 2026-10-19: 0 / 1,872 / 0 · most readings of one game that day (≈ runs): 1033
- 2026-10-20: 0 / 1,915 / 0 · most readings of one game that day (≈ runs): 1035
- 2026-10-21: 0 / 1,953 / 0 · most readings of one game that day (≈ runs): 1006
- 2026-10-22: 6,046 / 175 / 15 · most readings of one game that day (≈ runs): 293
- 2026-10-23: 6,030 / 174 / 23 · most readings of one game that day (≈ runs): 294
- 2026-10-24: 6,084 / 184 / 29 · most readings of one game that day (≈ runs): 295
- 2026-10-25: 6,081 / 206 / 18 · most readings of one game that day (≈ runs): 294
- 2026-10-26: 2,836 / 666 / 42 · most readings of one game that day (≈ runs): 295
- 2026-10-27: 2,888 / 629 / 43 · most readings of one game that day (≈ runs): 295
- 2026-10-28: 2,764 / 626 / 47 · most readings of one game that day (≈ runs): 295
- 2026-10-29: 2,790 / 620 / 59 · most readings of one game that day (≈ runs): 295
- 2026-10-30: 2,824 / 594 / 66 · most readings of one game that day (≈ runs): 295
- 2026-10-31: 2,796 / 597 / 77 · most readings of one game that day (≈ runs): 295
- 2026-11-01: 2,769 / 599 / 85 · most readings of one game that day (≈ runs): 295
- 2026-11-02: 2,797 / 553 / 118 · most readings of one game that day (≈ runs): 295
- 2026-11-03: 2,790 / 566 / 134 · most readings of one game that day (≈ runs): 98
- 2026-11-04: 2,848 / 528 / 141 · most readings of one game that day (≈ runs): 161
- 2026-11-05: 2,823 / 517 / 161 · most readings of one game that day (≈ runs): 294
- 2026-11-06: 2,825 / 444 / 173 · most readings of one game that day (≈ runs): 294
- 2026-11-07: 2,712 / 326 / 196 · most readings of one game that day (≈ runs): 294
- 2026-11-08: 2,721 / 196 / 222 · most readings of one game that day (≈ runs): 295
- 2026-11-09: 2,687 / 77 / 9 · most readings of one game that day (≈ runs): 254
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
- 500–2K: 1,242 games · 1 / 4 / 7 / 10 / 27 · 17% have under 3 readings
- 2K–10K: 1,107 games · 8 / 9 / 14 / 30 / 30 · 0% have under 3 readings
- 10K+: 277 games · 30 / 30 / 30 / 30 / 30 · 0% have under 3 readings

hour-adjusted daily average ÷ daily high (games with 8+ readings) — the code assumes 0.75 when a day has under 3 readings:
- <500: median 0.81 (10 games)
- 500–2K: median 0.77 (569 games)
- 2K–10K: median 0.75 (1023 games)
- 10K+: median 0.74 (276 games)

_0.0s_

## Alerts, updates, breakouts

alerts by kind: total · first day · last day · last 7 days
- new: 639 · 2026-10-22 · 2026-11-09 · 229
- surge: 599 · 2026-10-23 · 2026-11-09 · 281
- abroad: 474 · 2026-10-26 · 2026-11-09 · 241
- copy: 209 · 2026-10-23 · 2026-11-09 · 117
- breakout: 161 · 2026-10-23 · 2026-11-09 · 50
- early: 135 · 2026-10-22 · 2026-11-09 · 65
- chart: 68 · 2026-10-22 · 2026-11-09 · 24
- longterm: 46 · 2026-10-24 · 2026-11-05 · 30
- update: 43 · 2026-10-22 · 2026-11-08 · 22
- heat: 34 · 2026-10-25 · 2026-11-09 · 16
- studio: 15 · 2026-10-28 · 2026-11-09 · 12
- predict: 9 · 2026-10-30 · 2026-11-08 · 4

update events kept in memory: 400 (cap 400) · with a day-3 result: 31 · dates 2026-11-03 → 2026-11-09
icon/title changes in memory: 1328 · kinds: {"icon": 584, "title": 744}
breakouts logged: 179 · days from breakout to peak, all: 0 / 0 / 1 / 4 / 8 · only those 14+ days old (55): 0 / 0 / 0 / 5 / 8

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

_0.3s_

## Weekday hold: old vs new definition

**OLD: Tue–Wed vs Sat–Sun** — games rated: 2,382 · weeks rated per game: 1 / 1 / 2 / 6 / 8 · week-to-week rank correlation: 0.521 (5,326 pairs) · share of one week's spread that is the game itself: 0.651 · noise sd 0.238 · old-rule 'long-term': 503 of 1682 with 2+ weeks (30%)
**NEW: Mon–Wed vs two busiest of Fri–Sun** — games rated: 2,409 · weeks rated per game: 1 / 1 / 2 / 6 / 8 · week-to-week rank correlation: 0.523 (5,359 pairs) · share of one week's spread that is the game itself: 0.719 · noise sd 0.209 · old-rule 'long-term': 504 of 1691 with 2+ weeks (30%)

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

after the new rule: hold_meta {"week": "2026-11-04", "weekend": ["2026-10-31", "2026-11-01"], "weekday": ["2026-11-03", "2026-11-04"], "benchmark": 0.696, "roblox": 0.673, "weeks": 8, "reliability": 0.719, "noise_sd": 0.209} · long-term 151 · promising 343
- [🌎W10] Throw a Coin — 1.551× over 8 weeks (z 6.23) · 5.7K
- TANPANAMA — 1.532× over 8 weeks (z 6.06) · 4.3K
- [🍂] Anime Dice — 1.563× over 7 weeks (z 5.97) · 78.2K
- [EVENT🎃] Noob Incremental — 1.518× over 8 weeks (z 5.93) · 5.5K
- Free Fire Zone (Max) — 1.812× over 3 weeks (z 5.57) · 9.6K
- [UPD] Anime RNG Defense — 1.478× over 8 weeks (z 5.55) · 3.3K
- [UPD 12] Defeat Anime RNG  — 1.499× over 7 weeks (z 5.42) · 6.0K
- Forest Market — 1.462× over 8 weeks (z 5.39) · 3.7K
- [🎃Part 2] 🔩 Resource Incremental — 1.432× over 8 weeks (z 5.09) · 1.9K
- Sol's RNG [ Halloween Event 🎃] — 1.423× over 8 weeks (z 5.01) · 44.4K
- Bee Swarm Simulator — 1.401× over 8 weeks (z 4.79) · 33.9K
- [⚔️UPD] +1 Venom Evolution — 1.66× over 3 weeks (z 4.75) · 38.6K

_1.4s_

## What changes do (matched comparison)

games watched for publishes: 834 · publish days seen: 2,191 · publishes after a quiet week: 96
naive measure (day+3 vs the 3 days before), every publish: median -12.5% over 951 · by weekday of the publish: Mon -43% (88), Tue -29% (137), Wed +13% (178), Thu +20% (110), Fri -13% (111), Sat -14% (170), Sun -23% (157)
measured now: 2579 changes
- icon: 235 events · 205 with complete weeks · 136 with enough twins
- title: 2318 events · 1409 with complete weeks · 1257 with enough twins
- update: 26 events · 24 with complete weeks · 9 with enough twins
• Updates after a quiet week: measuring — 9 measured so far (needs 20)
• ▫️ **Icon changes**: typical lift **+7%** (likely -3% to +15%) vs similar games that changed nothing · 47% beat their twins by 10%+, 40% fell 10%+ behind · 136 measured
   ↳ the games themselves went -20% week on week while their twins went -25% — the naive before/after number is mostly that drift
• ▫️ **Title changes**: typical lift **+0%** (likely -1% to +2%) vs similar games that changed nothing · 38% beat their twins by 10%+, 36% fell 10%+ behind · 1257 measured
   ↳ the games themselves went -11% week on week while their twins went -10% — the naive before/after number is mostly that drift
_Lift = the game's week-on-week change divided by the median change of similar-size, similar-trend games that made no such change. Correlation still, but weekdays, natural decay and market swings are removed._

_12.7s_

## Themes

themes: 2,980 · calm candidate days: 35,941 · breakouts: 189 in 188 themes · history starts 2026-08-25
themes that broke out (count · name · most games): 2× escape (237); 1× walls escape (3); 1× walls (8); 1× verity (32); 1× tower (386); 1× together (17); 1× throw (12); 1× thai (7); 1× test (32); 1× tesla (3); 1× survive (75); 1× survival (43); 1× steal eggs (8); 1× steal egg (14); 1× soccer (51); 1× scooter (10); 1× say (3); 1× save (16); 1× sandbox (23); 1× run (75); 1× roadster (4); 1× rivals (9); 1× ride (46); 1× realistic (23); 1× ragdoll physics (6)

model status: {"examples": 4243, "positives": 780, "trained": true, "day": "2026-11-09", "themes": 479, "base_rate": 0.18383219420221542, "champion": "simple", "wf": {"folds": 4, "horizon": 21, "lr": {"n": 1388, "pos": 351, "auc": 0.7302, "base": 0.2529, "top": 0.6232, "top_n": 138, "lo": 0.6771, "hi": 0.7785}, "gbm": {"n": 1388, "pos": 351, "auc": 0.6826, "base": 0.2529, "top": 0.6667, "top_n": 138, "lo": 0.6347, "hi": 0.7297}, "p_trees_better": 0.01, "diff": -0.0467}, "honest": {"n": 1388, "pos": 351, "auc": 0.7301510768241722, "base": 0.25288184438040345, "top": 0.6231884057971014, "top_n": 138, "lo": 0.6771385120585702, "hi": 0.7785484984859639}, "test_auc": 0.7301510768241722}
- simple model, test with a 0-day purge: {"n": 3755, "pos": 738, "auc": 0.768, "base": 0.197, "top": 0.659, "top_n": 375, "lo": 0.73, "hi": 0.8} (folds 4)
- simple model, test with a 21-day purge: {"n": 1388, "pos": 351, "auc": 0.73, "base": 0.253, "top": 0.623, "top_n": 138, "lo": 0.677, "hi": 0.779} (folds 4)

top themes it would show today:
- school — model 0.966 · 1 signals · 18 games, 7 hits, 1 young hits, 0 new
- rng — model 0.958 · 1 signals · 19 games, 6 hits, 1 young hits, 1 new
- Base Defense & Tower Building — model 0.943 · 1 signals · 27 games, 13 hits, 1 young hits, 0 new
- Fishing — model 0.939 · 2 signals · 26 games, 12 hits, 1 young hits, 0 new
- Riddle & Deduction Mystery Games — model 0.925 · 1 signals · 25 games, 10 hits, 0 young hits, 0 new
- Tower Defense — model 0.92 · 1 signals · 23 games, 10 hits, 1 young hits, 0 new
- city — model 0.912 · 2 signals · 21 games, 9 hits, 1 young hits, 0 new
- speed — model 0.894 · 1 signals · 20 games, 10 hits, 1 young hits, 0 new
- Mukbang & Eating ASMR — model 0.888 · 1 signals · 19 games, 9 hits, 0 young hits, 0 new
- Keycap Collection & Customization — model 0.881 · 1 signals · 19 games, 9 hits, 1 young hits, 0 new
- keyboard — model 0.881 · 1 signals · 19 games, 9 hits, 1 young hits, 0 new
- Brainrot — model 0.878 · 1 signals · 20 games, 7 hits, 1 young hits, 0 new

🌱 **Theme model** (a theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days)
• Trained on 4,243 calm theme-days from 479 themes; 780 (18.4%) were followed by a breakout.
• Honest test: accuracy **0.73** (likely between 0.68 and 0.78) · 0.5 = coin flip · top 10% picks came true **62%** of the time vs 25% for all · 1,388 predictions, each made by a model trained only on outcomes already known at the time
• ⚙️ Simple model kept: 0.73 vs 0.68 for boosted trees (trees better in 1% of resamples; they need 90%+ and a 0.01+ lead)
• Biggest drivers: number of games (+), new games this week vs last week (−), players across the theme (−), tiny new games (studios testing it) (+), new games this week (+)

🔬 **Which indicators actually work** (189 theme breakouts tracked so far; 18.5% of calm theme-days are followed by one)
• 📈 theme doubled in a week: followed by a breakout 29/146 times · **1.1×** chance · ~11 days' warning · caught 37% of breakouts
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

_6.9s_

## Algorithm mirror

**chart**: 4,960 game-days over 28 days (2026-10-05 → 2026-11-01) · 305 positive (6.1%) · games: 2,141
**growth**: 5,204 game-days over 28 days (2026-10-05 → 2026-11-01) · 598 positive (11.5%) · games: 2,210

chart: coverage {"playtime": 0.004, "returning": 0.0, "first_step": 0.002, "sessions": 0.004, "hold": 0.58, "session_len": 0.966, "like_ratio": 0.288, "fav_conv": 0.277, "rev_per_player": 0.274, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
chart: stability {"playtime": {"w": -0.078, "lo": -0.166, "hi": 0.016, "sign": 0.917}, "first_step": {"w": -0.019, "lo": -0.053, "hi": 0.048, "sign": 0.8}, "sessions": {"w": -0.034, "lo": -0.126, "hi": 0.025, "sign": 0.85}, "hold": {"w": 0.024, "lo": -0.108, "hi": 0.078, "sign": 0.75}, "session_len": {"w": 0.217, "lo": 0.127, "hi": 0.354, "sign": 1.0}, "like_ratio": {"w": 0.001, "lo": -0.111, "hi": 0.112, "sign": 0.467}, "fav_conv": {"w": -0.057, "lo": -0.19, "hi": 0.01, "sign": 0.867}, "rev_per_player": {"w": -0.098, "lo": -0.261, "hi": 0.053, "sign": 0.833}, "size": {"w": 0.9, "lo": 0.773, "hi": 1.028, "sign": 1.0}, "momentum": {"w": 0.169, "lo": 0.079, "hi": 0.291, "sign": 0.983}, "age": {"w": -0.088, "lo": -0.172, "hi": 0.067, "sign": 0.85}, "has_badges": {"w": 0.054, "lo": -0.081, "hi": 0.118, "sign": 0.667}}
chart: wf {"folds": 2, "horizon": 8, "lr": {"n": 1108, "pos": 49, "auc": 0.6079, "base": 0.0442, "top": 0.0909, "top_n": 110, "lo": 0.5415, "hi": 0.6808}, "gbm": {"n": 1108, "pos": 49, "auc": 0.5815, "base": 0.0442, "top": 0.0727, "top_n": 110, "lo": 0.5228, "hi": 0.6402}, "p_trees_better": 0.3, "diff": -0.0261}

growth: coverage {"playtime": 0.018, "returning": 0.0, "first_step": 0.007, "sessions": 0.017, "hold": 0.584, "session_len": 0.967, "like_ratio": 0.321, "fav_conv": 0.308, "rev_per_player": 0.305, "size": 1.0, "momentum": 1.0, "age": 1.0, "has_badges": 1.0}
growth: stability {"playtime": {"w": -0.01, "lo": -0.103, "hi": 0.087, "sign": 0.6}, "first_step": {"w": 0.007, "lo": -0.06, "hi": 0.06, "sign": 0.6}, "sessions": {"w": 0.053, "lo": -0.019, "hi": 0.126, "sign": 0.867}, "hold": {"w": -0.047, "lo": -0.135, "hi": 0.034, "sign": 0.833}, "session_len": {"w": 0.004, "lo": -0.082, "hi": 0.107, "sign": 0.617}, "like_ratio": {"w": 0.002, "lo": -0.089, "hi": 0.114, "sign": 0.483}, "fav_conv": {"w": -0.059, "lo": -0.14, "hi": 0.005, "sign": 0.95}, "rev_per_player": {"w": -0.074, "lo": -0.154, "hi": 0.088, "sign": 0.7}, "size": {"w": -0.295, "lo": -0.398, "hi": -0.176, "sign": 1.0}, "momentum": {"w": 1.099, "lo": 1.017, "hi": 1.234, "sign": 1.0}, "age": {"w": -0.356, "lo": -0.458, "hi": -0.248, "sign": 1.0}, "has_badges": {"w": 0.028, "lo": -0.113, "hi": 0.115, "sign": 0.533}}
growth: wf {"folds": 4, "horizon": 8, "lr": {"n": 2565, "pos": 276, "auc": 0.5538, "base": 0.1076, "top": 0.1094, "top_n": 256, "lo": 0.5243, "hi": 0.5821}, "gbm": {"n": 2565, "pos": 276, "auc": 0.8048, "base": 0.1076, "top": 0.4648, "top_n": 256, "lo": 0.7727, "hi": 0.8345}, "p_trees_better": 1.0, "diff": 0.2513}
- chart, 0-day purge: simple 0.557 · trees 0.525 · n 2741 · folds 3
- chart, 8-day purge: simple 0.608 · trees 0.581 · n 1108 · folds 2
- growth, 0-day purge: simple 0.705 · trees 0.833 · n 4203 · folds 4
- growth, 8-day purge: simple 0.554 · trees 0.805 · n 2565 · folds 4

🧠 **Algorithm mirror: what Roblox is rewarding right now**
_Learned from which games Roblox promoted (chart entries, 50%+ growth) in the following week, after allowing for size, momentum and age. Only signals that keep their direction when the model is refitted on resampled games are listed as findings._
• No quality signal is reliably rewarded or penalised in this window.
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, sessions per player per day, like ratio, new players reaching the next badge, weekday hold vs a typical game, playtime per player per day, favourite rate, revenue per player
• Model for *enters a Roblox chart within 7 days* (4,960 game-days): Honest test: accuracy **0.61** (likely between 0.54 and 0.68) · 0.5 = coin flip · top 10% picks came true **9%** of the time vs 4% for all · 1,108 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.61 vs 0.58 for boosted trees (trees better in 30% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (5,204 game-days): Honest test: accuracy **0.80** (likely between 0.77 and 0.83) · 0.5 = coin flip · top 10% picks came true **46%** of the time vs 11% for all · 2,565 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.55 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (18,545 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (21,338 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

_14.4s_

## Explosion model

examples: 254 · exploded: 12 · first noticed on a backfilled day (before the bot watched): 254 (12 exploded) vs live: 0 (0 exploded)
first-noticed dates: 2026-08-08 → 2026-10-18 · by month: {"2026-08": [19, 1], "2026-09": [72, 3], "2026-10": [163, 8]}
log10(peak after ÷ players the day after noticing): 0.0675 / 0.203 / 0.477 / 0.763 / 1.13
status: {"examples": 254, "positives": 12, "trained": true, "day": "2026-11-09", "champion": "simple", "wf": {"folds": 0, "horizon": 21}, "test_n": null, "test_pos": null, "test_top10_hit": null, "base_rate": 0.047244094488188976, "stable": ["players_d1", "growth_d1", "age", "weekend", "studio_best", "crowd", "mech_hits"]}

🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 254 young games, 12 of which exploded (5%).
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), studio's best previous game (−), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: — · 638 still in their 21-day window (35 already exploded)
• chart: — · 68 still in their 21-day window (28 already exploded)
• 👀 early warning: — · 108 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 355 still in their 21-day window (36 already exploded)
• 💥 breakout: — · 161 still in their 21-day window (29 already exploded)
• 🧬 copy wave: — · 165 still in their 21-day window (14 already exploded)
• longterm: — · 45 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 18 still in their 21-day window (5 already exploded)
• abroad: — · 402 still in their 21-day window (36 already exploded)
• studio: — · 15 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 153 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

_2.7s_

## Stickiness and lasting features

games scored: 2605 · weights {"hold_rel": 0.6083, "playtime": 0.0, "session_min": 0.0623, "level_kept": 0.3294, "fav_conv": 0.0, "rev_per_ccu": 0.0} · per-signal rank correlation with players kept 4 weeks later: {"hold_rel": 0.205, "session_min": 0.021, "level_kept": 0.111} · n 2907 · honest cross-check {"rho": 0.191, "n": 2726, "weeks": 6}
description features: 151 long-term vs 758 others · checked 16
- leaderboards: lift 1.97 (1.42–2.73) · 69 games · reliable: True
- offline / idle earnings: lift 1.73 (1.22–2.44) · 70 games · reliable: True
- codes: lift 1.41 (1.03–1.94) · 112 games · reliable: True
- pets / collecting: lift 1.25 (0.96–1.64) · 219 games · reliable: False
- daily rewards / streaks: lift 1.6 (0.84–3.05) · 19 games · reliable: False
- trading: lift 1.4 (0.83–2.36) · 35 games · reliable: False
- group rewards: lift 1.11 (0.81–1.54) · 143 games · reliable: False
- quests / missions: lift 1.11 (0.7–1.77) · 60 games · reliable: False
- rebirth / prestige: lift 1.14 (0.68–1.89) · 48 games · reliable: False
- limited events: lift 0.94 (0.57–1.54) · 64 games · reliable: False
- base building / decorating: lift 0.74 (0.52–1.05) · 170 games · reliable: False
- PvP: lift 0.82 (0.45–1.48) · 51 games · reliable: False

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

games with badge data: 289 · with a 7-day streak badge: 9
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
• No quality signal is reliably rewarded or penalised in this window.
▫️ Unclear this week (direction flips when resampled, or measured for too few games): session length, sessions per player per day, like ratio, new players reaching the next badge, weekday hold vs a typical game, playtime per player per day, favourite rate, revenue per player
• Model for *enters a Roblox chart within 7 days* (4,960 game-days): Honest test: accuracy **0.61** (likely between 0.54 and 0.68) · 0.5 = coin flip · top 10% picks came true **9%** of the time vs 4% for all · 1,108 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Simple model kept: 0.61 vs 0.58 for boosted trees (trees better in 30% of resamples; they need 90%+ and a 0.01+ lead)
• Model for *players up 50%+ within 7 days* (5,204 game-days): Honest test: accuracy **0.80** (likely between 0.77 and 0.83) · 0.5 = coin flip · top 10% picks came true **46%** of the time vs 11% for all · 2,565 predictions, each made by a model trained only on outcomes already known at the time
  ⚙️ Using **boosted trees**: 0.80 vs 0.55 for the simple model (trees better in 100% of resamples)
🧪 Live check, enters a Roblox chart within 7 days: predictions the bot actually made scored 0.64; their top 10% were promoted 14% of the time vs 7% overall (18,545 predictions).
🧪 Live check, players up 50%+ within 7 days: predictions the bot actually made scored 0.78; their top 10% were promoted 33% of the time vs 8% overall (21,338 predictions).
_Correlation from public data, not Roblox's actual model. The live check is the number to trust: it scores predictions made before the outcome existed._

**⭐ Trend Score**
🚀 **Trend Score** — chance a young game at least doubles and passes 5,000 players within 2 weeks · now using: **learned**
• Starting formula vs real outcomes: accuracy **0.66** (likely 0.58–0.74) · its top 10% took off 16% of the time vs 6.8% for all · 501 snapshots over 1 days
• Learned model: not trained yet — needs 2000+ outcomes with 60+ take-offs over 21+ days (has 501 / 34 over 1 day)
• Scores as shown at the time: 50+: 36% took off (14) · 25–49: 6% took off (17) · 10–24: 14% took off (51) · under 10: 5% took off (419)

**💥 Explosion model + alert scorecard**
🧠 **Explosion model** (explode = 25.0K+ players within 21 days of first reaching 600)
• Trained on 254 young games, 12 of which exploded (5%).
• Honest test: not possible yet — it needs enough history to train only on outcomes that were already known (21-day outcomes).
• **Not used yet**: its picks stay off the board and out of alerts until it passes that test.
• Drivers that hold up when resampled: same-mechanic games that exploded in the month before (+), game age when noticed (−), copies in the same mechanic in the 2 weeks before (−), studio's best previous game (−), growth from day 0 to day 1 (+)

🎯 **Scorecard: how often signals were followed by an explosion**
• 🆕 crossed 2K: — · 638 still in their 21-day window (35 already exploded)
• chart: — · 68 still in their 21-day window (28 already exploded)
• 👀 early warning: — · 108 still in their 21-day window (4 already exploded)
• update: — · 8 still in their 21-day window (4 already exploded)
• 🚀 surge: — · 355 still in their 21-day window (36 already exploded)
• 💥 breakout: — · 161 still in their 21-day window (29 already exploded)
• 🧬 copy wave: — · 165 still in their 21-day window (14 already exploded)
• longterm: — · 45 still in their 21-day window (3 already exploded)
• 🔥 heat: — · 18 still in their 21-day window (5 already exploded)
• abroad: — · 402 still in their 21-day window (36 already exploded)
• studio: — · 15 still in their 21-day window (2 already exploded)
• 🎯 prediction: — · 9 still in their 21-day window
• model < 50%: — · 153 still in their 21-day window
• model ≥ 50%: — · 7 still in their 21-day window (1 already exploded)
_Only signals whose 21 days are up are scored, so early wins don't flatter the rate._

**🌱 Theme model**
🌱 **Theme model** (a theme "breaks out" when, after 21+ calm days, 3+ of its games under 45 days old pass 2.0K players within 21 days)
• Trained on 4,243 calm theme-days from 479 themes; 780 (18.4%) were followed by a breakout.
• Honest test: accuracy **0.73** (likely between 0.68 and 0.78) · 0.5 = coin flip · top 10% picks came true **62%** of the time vs 25% for all · 1,388 predictions, each made by a model trained only on outcomes already known at the time
• ⚙️ Simple model kept: 0.73 vs 0.68 for boosted trees (trees better in 1% of resamples; they need 90%+ and a 0.01+ lead)
• Biggest drivers: number of games (+), new games this week vs last week (−), players across the theme (−), tiny new games (studios testing it) (+), new games this week (+)

🔬 **Which indicators actually work** (189 theme breakouts tracked so far; 18.5% of calm theme-days are followed by one)
• 📈 theme doubled in a week: followed by a breakout 29/146 times · **1.1×** chance · ~11 days' warning · caught 37% of breakouts
• No finished firings yet: 🧬 copy burst, 🐣 tiny-game burst, 🏢 3+ studios at once, ✏️ games renaming to it, 📊 in the algorithm charts, 📺 Roblox YouTube buzz, 🎮 rising on Steam, 📚 Wikipedia spike, 🔥 YouTube trending, 🟣 Twitch top games, 🗓️ in season, 🔮 upcoming release/event, 🎬 YouTube Shorts buzz

**📈 Forecasts**
📈 Peak forecasts (made on day 5): typically off by **74%**; 54% within 2× of the real peak (573 games)
   ↳ not accurate enough to quote numbers yet (needs 60% within 2×): the bot says "big rise ahead / more growth / near its peak" instead
🧭 Breakout-start signal: followed by 2× players within 2 weeks **18%** of the time vs 22% for any young game (208 firings) · **alerts paused** until it beats that
⏳ A typical hit keeps half its peak players for **10 days** (1668 games)
By weekday hold: holds weekday players well **23d** · average weekday hold **15d** · holds them poorly **6d**
By mechanic: Roleplay / life **14d** · Anime / fighting style **12d** · Eat / grow big **11d** · Sports **10d**
By genre: Social **33d** · Shooter **31d** · Obby & Platformer **19d** · Action **16d**

**📏 Stickiness weights**
weekday hold 61% · players kept vs best week 33% · session length 6% — learned from 2,907 game-weeks

📥 Past histories downloaded: **2,416** games (2,508 tried)

_4.2s_
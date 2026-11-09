"""
Diagnostics: one page of facts about the bot's own data and models, published as reports/diagnostics.md.

Run it by asking the bot the single word  diagnose  (workflow "question" input, or /ask diagnose).
It reads the bot's memory, retrains every model IN MEMORY with the current code (nothing is saved, nothing
is posted to Discord) and writes down what it finds: how often games are really sampled, whether each
definition behaves, how each model does on the honest test, and how much an ordinary (leaky) test would
have flattered it. It exists so problems can be found from real numbers instead of guesses.
"""
import json
import math
import os
import time
import traceback
from datetime import datetime, timedelta
from statistics import median

import config as C


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _s(dt):
    return dt.strftime("%Y-%m-%d")


def _q(vals, qs=(0.1, 0.25, 0.5, 0.75, 0.9)):
    v = sorted(vals)
    if not v:
        return "—"
    return " / ".join(f"{v[min(len(v) - 1, int(q * len(v)))]:.3g}" for q in qs)


def _bucket(p):
    return "<500" if p < 500 else "500–2K" if p < 2000 else "2K–10K" if p < 10000 else "10K+"


BUCKETS = ["<500", "500–2K", "2K–10K", "10K+"]


def section(out, title, fn):
    t = time.time()
    out.append(f"\n## {title}\n")
    try:
        fn(out)
    except Exception as e:
        out.append(f"**FAILED:** `{e.__class__.__name__}: {e}`\n```\n{traceback.format_exc()[-1500:]}\n```")
    out.append(f"\n_{time.time() - t:.1f}s_")


def report(db, state, today, fmt):
    import ask as ASK
    import effects as EF
    import engage as E
    import hold as HOLD
    import insights as I
    import learn as L
    import promo as P
    import themes as T
    import trend as TS
    import warehouse as W

    out = [f"# Diagnostics · {today}", "", f"_generated {datetime.utcnow().isoformat()[:19]}Z · models retrained in memory only_"]
    yday = _s(_d(today) - timedelta(days=1))

    # ------------------------------------------------------------------ tables
    def tables(o):
        for t in ("games", "daily", "hourly", "alerts", "predictions", "backfill", "trend_feats", "promo_preds", "theme_daily",
                  "theme_preds", "hold_weekly", "engage_weekly", "fc_preds", "cp_fires", "renames", "effects", "upstream"):
            try:
                n = db.execute(f"SELECT COUNT(*) c FROM {t}").fetchone()["c"]
                o.append(f"- {t}: {n:,}")
            except Exception as e:
                o.append(f"- {t}: missing ({e})")
        o.append(f"- database file: {os.path.getsize(W.DB_PATH) / 1e6:.0f} MB")
        r = db.execute("SELECT MIN(day) a, MAX(day) b, COUNT(DISTINCT day) n FROM daily").fetchone()
        o.append(f"- daily covers {r['a']} → {r['b']} ({r['n']} days)")
        o.append("\ngame-days per day, last 21 days (live / backfill / other):")
        for r in db.execute("""SELECT day, SUM(src='live') l, SUM(src='backfill') b, SUM(src IS NULL OR src NOT IN ('live','backfill')) x,
                               MAX(n) mx FROM daily WHERE day>=? GROUP BY day ORDER BY day""", (_s(_d(today) - timedelta(days=21)),)):
            o.append(f"- {r['day']}: {r['l'] or 0:,} / {r['b'] or 0:,} / {r['x'] or 0:,} · most readings of one game that day (≈ runs): {r['mx']}")
        for t, col in (("alerts", "day"), ("trend_feats", "day"), ("promo_preds", "day"), ("theme_daily", "day"), ("hold_weekly", "week"),
                       ("engage_weekly", "week")):
            try:
                r = db.execute(f"SELECT MIN({col}) a, MAX({col}) b, COUNT(DISTINCT {col}) n FROM {t}").fetchone()
                o.append(f"- {t}: {r['a']} → {r['b']} ({r['n']} distinct)")
            except Exception:
                pass
        sp = os.environ.get("STATE_PATH")
        if sp and os.path.exists(sp):
            o.append(f"\nstate.json: {os.path.getsize(sp) / 1e6:.1f} MB · biggest keys:")
            sizes = sorted(((len(json.dumps(v)), k) for k, v in state.items()), reverse=True)[:12]
            o += [f"- {k}: {n / 1e6:.2f} MB" for n, k in sizes]
    section(out, "Tables and coverage", tables)

    # ---------------------------------------------------------------- sampling
    def sampling(o):
        rows = db.execute("SELECT peak, sum_ccu, n FROM daily WHERE day=? AND src='live' AND peak IS NOT NULL", (yday,)).fetchall()
        by = {b: [] for b in BUCKETS}
        ratio = {b: [] for b in BUCKETS}
        for r in rows:
            b = _bucket(r["peak"])
            by[b].append(r["n"] or 0)
            if (r["n"] or 0) >= 8 and r["peak"]:
                ratio[b].append((r["sum_ccu"] / r["n"]) / r["peak"])
        o.append(f"readings per game on {yday} (10th / 25th / median / 75th / 90th percentile), by the game's daily high:")
        for b in BUCKETS:
            v = by[b]
            o.append(f"- {b}: {len(v):,} games · {_q(v)} · {sum(1 for x in v if x < 3) / max(len(v), 1) * 100:.0f}% have under 3 readings")
        o.append("\nhour-adjusted daily average ÷ daily high (games with 8+ readings) — the code assumes 0.75 when a day has under 3 readings:")
        for b in BUCKETS:
            o.append(f"- {b}: median {median(ratio[b]):.2f} ({len(ratio[b])} games)" if ratio[b] else f"- {b}: —")
    section(out, "How often games are really read", sampling)

    # ------------------------------------------------------------------ alerts
    def alerts(o):
        o.append("alerts by kind: total · first day · last day · last 7 days")
        wk = _s(_d(today) - timedelta(days=7))
        for r in db.execute("""SELECT kind, COUNT(*) c, MIN(day) a, MAX(day) b, SUM(day>=?) w FROM alerts GROUP BY kind ORDER BY c DESC""", (wk,)):
            o.append(f"- {r['kind']}: {r['c']} · {r['a']} · {r['b']} · {r['w']}")
        ups = (state.get("ins") or {}).get("updates") or []
        o.append(f"\nupdate events kept in memory: {len(ups)} (cap {C.MAX_UPDATE_EVENTS}) · with a day-3 result: "
                 f"{sum(1 for e in ups if 'd3' in e)} · dates {min((e['date'] for e in ups), default='—')} → {max((e['date'] for e in ups), default='—')}")
        ic = state.get("icon_changes") or []
        o.append(f"icon/title changes in memory: {len(ic)} · kinds: " + json.dumps({k: sum(1 for c in ic if c.get('kind') == k) for k in ('icon', 'title')}))
        life = (state.get("ins") or {}).get("life") or {}
        lag = [(_d(r["peak_day"]) - _d(r["broke"])).days for r in life.values() if not r.get("pre")]
        old = [(_d(r["peak_day"]) - _d(r["broke"])).days for r in life.values()
               if not r.get("pre") and (_d(today) - _d(r["broke"])).days >= C.LIFE_MATURE_DAYS]
        o.append(f"breakouts logged: {len(lag)} · days from breakout to peak, all: {_q(lag)} · only those {C.LIFE_MATURE_DAYS}+ days old "
                 f"({len(old)}): {_q(old)}")
    section(out, "Alerts, updates, breakouts", alerts)

    # --------------------------------------------------------------- trend score
    def trend(o):
        rows = db.execute("SELECT day, uid, players, feats, score FROM trend_feats WHERE day<=?", (_s(_d(today) - timedelta(days=14)),)).fetchall()
        days = sorted({r["day"] for r in rows})
        o.append(f"snapshots old enough to score: {len(rows):,} over {len(days)} days ({days[0] if days else '—'} → {days[-1] if days else '—'})")
        defs = {"old (2× and 1,000, one day)": (1000, 1), "2× and 5,000, one day": (5000, 1), "NEW (2× and 5,000, two days)": (5000, 2),
                "2× and 2,000, two days": (2000, 2)}
        res = {k: {b: [0, 0] for b in BUCKETS} for k in defs}
        prior, shown, ynew = [], [], []
        for r in rows:
            b = _bucket(r["players"] or 0)
            for k, (tg, su) in defs.items():
                y = TS.label(db, r["uid"], r["day"], r["players"], tg, su)
                if y is None:
                    continue
                res[k][b][0] += 1
                res[k][b][1] += y
                if k.startswith("NEW"):
                    prior.append((TS.prior_score(json.loads(r["feats"])), y, r["uid"]))
                    shown.append(r["score"])
                    ynew.append(y)
        o.append("\ntake-off rate by size at the time of the snapshot (took off / snapshots):")
        o.append("| definition | " + " | ".join(BUCKETS) + " | all |")
        o.append("|---|" + "---|" * (len(BUCKETS) + 1))
        for k in defs:
            cells = [f"{res[k][b][1]}/{res[k][b][0]} ({res[k][b][1] / max(res[k][b][0], 1) * 100:.1f}%)" for b in BUCKETS]
            tn, tp = sum(res[k][b][0] for b in BUCKETS), sum(res[k][b][1] for b in BUCKETS)
            o.append(f"| {k} | " + " | ".join(cells) + f" | {tp}/{tn} ({tp / max(tn, 1) * 100:.1f}%) |")
        h = L.honest_metrics(prior)
        o.append(f"\nstarting formula vs the NEW outcome: {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in (h or {}).items()})}")
        if ynew and 0 < sum(ynew) < len(ynew):
            o.append(f"scores as shown at the time vs the NEW outcome: AUC {L.auc(shown, ynew):.3f}")
            for lo, hi in ((0.5, 1.01), (0.25, 0.5), (0.1, 0.25), (0, 0.1)):
                v = [y for s, y in zip(shown, ynew) if lo <= (s or 0) < hi]
                o.append(f"- shown {lo * 100:.0f}–{min(hi, 1) * 100:.0f}: {sum(v)}/{len(v)} took off" + (f" ({sum(v) / len(v) * 100:.0f}%)" if v else ""))
            ps = sorted(p for p, _, _ in prior)
            o.append(f"starting-formula raw scores (10/25/50/75/90th pct): {_q(ps)}")
        pr = TS.calibrate_prior(db, today)
        o.append(f"calibration of the starting formula: {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in pr.items()})}")
        st = TS.train(db, today)
        o.append(f"learned model status: {json.dumps({k: v for k, v in st.items() if k not in ('weights',)}, default=str)[:900]}")
    section(out, "Trend Score", trend)

    # --------------------------------------------------------------------- hold
    def hold(o):
        created = {r["uid"]: r["created"] for r in db.execute("SELECT uid, created FROM games")}
        names = {r["uid"]: r["name"] for r in db.execute("SELECT uid, name FROM games")}
        wed = HOLD.latest_wed(today)
        weeks = [_s(_d(wed) - timedelta(days=7 * i)) for i in range(C.HOLD_HISTORY_WEEKS)][::-1]
        for robust in (False, True):
            rel = {}
            for w in weeks:
                res, bench = HOLD.compute_week(db, w, created, robust=robust)
                for u, hh in res.items():
                    if hh.get("rel"):
                        rel.setdefault(u, {})[w] = hh["rel"]
            by = {u: [(w, math.log(v), 0) for w, v in ws.items()] for u, ws in rel.items()}
            within, between = HOLD._variances(by)
            pairs = [(ws[a], ws[b]) for ws in rel.values() for a, b in zip(weeks, weeks[1:]) if a in ws and b in ws]
            rho = E._spearman([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 20 else None
            nweeks = [len(ws) for ws in rel.values()]
            # old rule: >=1.0 in >=75% of weeks, 2+ weeks, median >= 1.0
            old_lt = sum(1 for ws in rel.values() if len(ws) >= 2 and sum(1 for v in ws.values() if v >= 1) / len(ws) >= 0.75
                         and median(ws.values()) >= 1)
            o.append(f"**{'NEW: Mon–Wed vs two busiest of Fri–Sun' if robust else 'OLD: Tue–Wed vs Sat–Sun'}** — games rated: {len(rel):,} · "
                     f"weeks rated per game: {_q(nweeks)} · week-to-week rank correlation: {rho if rho is None else round(rho, 3)} "
                     f"({len(pairs):,} pairs) · share of one week's spread that is the game itself: "
                     f"{'—' if within is None else round(between / (between + within), 3)} · noise sd {'—' if within is None else round(math.sqrt(within), 3)} "
                     f"· old-rule 'long-term': {old_lt} of {sum(1 for n in nweeks if n >= 2)} with 2+ weeks "
                     f"({old_lt / max(1, sum(1 for n in nweeks if n >= 2)) * 100:.0f}%)")
            if robust:
                new_rel = rel
            else:
                old_rel = rel
        diffs = []
        for u in new_rel:
            if u in old_rel:
                common = [w for w in new_rel[u] if w in old_rel[u]]
                if len(common) >= 2:
                    diffs.append((median(old_rel[u][w] for w in common) / median(new_rel[u][w] for w in common), u, len(common)))
        diffs.sort(reverse=True)
        o.append("\ngames the OLD measure flattered most (old ÷ new relative hold):")
        o += [f"- {names.get(u, u)[:40]} — ×{r:.2f} ({n} weeks)" for r, u, n in diffs[:12]]
        m = HOLD.update(db, state, today)
        lt = state.get("longterm") or {}
        o.append(f"\nafter the new rule: hold_meta {json.dumps(m)} · long-term {sum(1 for v in lt.values() if v['status'] == 'long-term')} · "
                 f"promising {sum(1 for v in lt.values() if v['status'] == 'promising')}")
        top = sorted(((v.get("z") or 0, u, v) for u, v in lt.items() if v["status"] == "long-term"), reverse=True)[:12]
        o += [f"- {names.get(u, u)[:40]} — {v['med']}× over {v['weeks']} weeks (z {v.get('z')}) · {fmt(v['players'])}" for _, u, v in top]
    section(out, "Weekday hold: old vs new definition", hold)

    # ------------------------------------------------------------------ effects
    def effects(o):
        ev, allp, watched = EF.publish_events(db, _s(_d(today) - timedelta(days=C.EFFECT_HISTORY_DAYS)))
        o.append(f"games watched for publishes: {len(watched)} · publish days seen: {sum(len(v) for v in allp.values()):,} · "
                 f"publishes after a quiet week: {len(ev)}")
        # the naive number, for comparison: players on day+3 vs the mean of the 3 days before
        peaks = {}
        for r in db.execute("SELECT uid, day, peak FROM daily WHERE peak IS NOT NULL AND day>=?", (_s(_d(today) - timedelta(days=C.EFFECT_HISTORY_DAYS + 20)),)):
            peaks.setdefault(r["uid"], {})[r["day"]] = r["peak"]
        naive, bywd = [], {}
        for uid, days in allp.items():
            for dday in days[1:]:
                ds = peaks.get(uid) or {}
                bef = [ds.get(_s(_d(dday) - timedelta(days=k))) for k in (1, 2, 3)]
                aft = ds.get(_s(_d(dday) + timedelta(days=3)))
                if all(bef) and aft and sum(bef) / 3 >= C.UPDATE_MIN_PLAYERS:
                    v = aft / (sum(bef) / 3) - 1
                    naive.append(v)
                    bywd.setdefault(_d(dday).strftime("%a"), []).append(v)
        if naive:
            o.append(f"naive measure (day+3 vs the 3 days before), every publish: median {median(naive) * 100:+.1f}% over {len(naive):,} · by weekday of the publish: "
                     + ", ".join(f"{k} {median(v) * 100:+.0f}% ({len(v)})" for k, v in sorted(bywd.items(), key=lambda kv: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].index(kv[0]))))
        n = EF.update(db, state, today)
        o.append(f"measured now: {n} changes")
        for r in db.execute("SELECT kind, COUNT(*) c, SUM(lift IS NOT NULL) m, SUM(raw IS NOT NULL) w FROM effects GROUP BY kind"):
            o.append(f"- {r['kind']}: {r['c']} events · {r['w']} with complete weeks · {r['m']} with enough twins")
        o += EF.report_lines(db, today)
    section(out, "What changes do (matched comparison)", effects)

    # ------------------------------------------------------------------- themes
    def themes(o):
        data = T._load(db, _s(_d(today) - timedelta(days=C.THEME_KEEP_DAYS)))
        start = T._start(data)
        nb, ncand, hot_never = 0, 0, 0
        per = []
        for k, hist in data.items():
            cands, bks = T.timeline(hist, start)
            nb += len(bks)
            ncand += len(cands)
            if bks:
                per.append((len(bks), T.display(k, state), max(h.get("games") or 0 for h in hist.values())))
        o.append(f"themes: {len(data):,} · calm candidate days: {ncand:,} · breakouts: {nb} in {len(per)} themes · history starts {_s(start) if start else '—'}")
        per.sort(reverse=True)
        o.append("themes that broke out (count · name · most games): " + "; ".join(f"{n}× {nm} ({g})" for n, nm, g in per[:25]))
        st = T.train(db, today)
        o.append(f"\nmodel status: {json.dumps({k: v for k, v in st.items() if k != 'drivers'}, default=str)[:900]}")
        ex = T.examples(db, today)
        if len(ex) >= 200 and 0 < sum(e['y'] for e in ex) < len(ex):
            names = [f for f, _ in T.FEATURES]
            for hz in (0, C.LABEL_DAYS):
                wf = L.walk_forward(ex, names, {}, hz, want_gbm=False)
                h = L.honest_metrics(wf["oof"]["lr"])
                o.append(f"- simple model, test with a {hz}-day purge: {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in (h or {}).items()})} (folds {wf['folds']})")
        o.append("\ntop themes it would show today:")
        for p, sc, k, r, fired in T.predict(db, today)[:12]:
            o.append(f"- {T.display(k, state)} — model {None if p is None else round(p, 3)} · {sc} signals · {r['games']} games, {r['hits']} hits, "
                     f"{r.get('yhits')} young hits, {r['new7']} new")
        o += [""] + T.report_lines(db, today, fmt)
    section(out, "Themes", themes)

    # -------------------------------------------------------------------- promo
    def promo(o):
        ex, _ = P.build(db, today)
        for t in P.TARGETS:
            e = ex[t]
            wk = {}
            for x in e:
                w = x["day"][:10]
                wk.setdefault(w, [0, 0])
                wk[w][0] += 1
                wk[w][1] += x["y"]
            days = sorted(wk)
            o.append(f"**{t}**: {len(e):,} game-days over {len(days)} days ({days[0] if days else '—'} → {days[-1] if days else '—'}) · "
                     f"{sum(x['y'] for x in e)} positive ({sum(x['y'] for x in e) / max(len(e), 1) * 100:.1f}%) · games: {len({x['uid'] for x in e}):,}")
        st = P.train(db, today)
        for t in P.TARGETS:
            s = st.get(t) or {}
            o.append(f"\n{t}: coverage {json.dumps(s.get('coverage'))}")
            o.append(f"{t}: stability " + json.dumps({f: {k: round(v, 3) for k, v in d.items()} for f, d in (s.get('stability') or {}).items()}))
            o.append(f"{t}: wf {json.dumps(s.get('wf'))}")
        # how much did the ordinary (unpurged) test flatter it?
        ex2, _ = P.build(db, today)
        from statistics import median as med_
        for t in P.TARGETS:
            e = sorted(ex2[t], key=lambda x: x["day"])
            m = {f: (med_([x["x"][f] for x in e if x["x"][f] is not None]) if any(x["x"][f] is not None for x in e) else 0.0) for f in P.NAMES}
            for x in e:
                x["x"] = {f: (x["x"][f] if x["x"][f] is not None else m[f]) for f in P.NAMES}
            usable = [f for f in P.NAMES if len({round(x["x"][f], 6) for x in e}) > 1]
            for hz in (0, C.PROMO_HORIZON_DAYS):
                wf = L.walk_forward(e, usable, {"iters": C.PROMO_ITERS, "l2": C.PROMO_L2}, hz, want_gbm=True)
                hl, hg = L.honest_metrics(wf["oof"]["lr"]), L.honest_metrics(wf["oof"]["gbm"])
                o.append(f"- {t}, {hz}-day purge: simple {None if not hl else round(hl.get('auc') or 0, 3)} · trees "
                         f"{None if not hg else round(hg.get('auc') or 0, 3)} · n {hl and hl.get('n')} · folds {wf['folds']}")
        o += [""] + P.report_lines(db, today)
    section(out, "Algorithm mirror", promo)

    # ---------------------------------------------------------------- explosion
    def explosion(o):
        ex = L.build_examples(db, today)
        src = {r["uid"] + r["day"]: r["src"] for r in db.execute("SELECT uid, day, src FROM daily WHERE src IS NOT NULL")}
        bf = sum(1 for e in ex if src.get(e["uid"] + e["t0"]) == "backfill")
        o.append(f"examples: {len(ex)} · exploded: {sum(e['y'] for e in ex)} · first noticed on a backfilled day (before the bot watched): {bf} "
                 f"({sum(e['y'] for e in ex if src.get(e['uid'] + e['t0']) == 'backfill')} exploded) vs live: {len(ex) - bf} "
                 f"({sum(e['y'] for e in ex if src.get(e['uid'] + e['t0']) != 'backfill')} exploded)")
        if ex:
            o.append(f"first-noticed dates: {ex[0]['t0']} → {ex[-1]['t0']} · by month: "
                     + json.dumps({m: [sum(1 for e in ex if e['t0'][:7] == m), sum(e['y'] for e in ex if e['t0'][:7] == m)]
                                   for m in sorted({e['t0'][:7] for e in ex})}))
            ratios = [math.log10(max(e["players"], 1)) - e["x"]["players_d1"] for e in ex]
            o.append(f"log10(peak after ÷ players the day after noticing): {_q(ratios)}")
        st = L.train(db, today)
        o.append(f"status: {json.dumps({k: v for k, v in st.items() if k != 'drivers'}, default=str)[:900]}")
        o += [""] + L.report_lines(db, today, fmt)
    section(out, "Explosion model", explosion)

    # --------------------------------------------------------------- stickiness
    def stick(o):
        n = E.update(db, state, today)
        sw = W.meta_get(db, "stick_weights") or {}
        o.append(f"games scored: {n} · weights {json.dumps(sw.get('weights'))} · per-signal rank correlation with players kept 4 weeks later: "
                 f"{json.dumps(sw.get('rho'))} · n {sw.get('n')} · honest cross-check {json.dumps(sw.get('cv'))}")
        fr = E.feature_report(db, state)
        o.append(f"description features: {fr['n_lt']} long-term vs {fr['n_other']} others · checked {fr.get('checked')}")
        for r in fr["rows"][:12]:
            o.append(f"- {r['feature']}: lift {None if r['lift'] is None else round(r['lift'], 2)} "
                     f"({None if r['lo'] is None else round(r['lo'], 2)}–{None if r['hi'] is None else round(r['hi'], 2)}) · {r['games']} games · reliable: {r['sig']}")
    section(out, "Stickiness and lasting features", stick)

    # -------------------------------------------------------------------- money
    def money(o):
        import money as MO
        rows = MO.table(db, state, today, I.mechanics_of)
        pp = [r["per_player"] for r in rows]
        o.append(f"games with earnings: {len(rows):,} · $/player/month percentiles: {_q(pp, (0.1, 0.5, 0.9, 0.99))} · flagged as suspect: {sum(1 for r in rows if r.get('suspect'))}")
        small = sorted([r for r in rows if r["ccu"] < 5000], key=lambda r: -r["monthly"])[:8]
        o += [f"- {r['name'][:36]} — ${r['monthly']:,.0f}/month · {r['ccu']:.0f} players · ${r['per_player']:.0f}/player · suspect: {bool(r.get('suspect'))}" for r in small]
    section(out, "Money: top earners under 5K players", money)

    # ------------------------------------------------------------------- badges
    def badges(o):
        b = state.get("badges") or {}
        names = {r["uid"]: r["name"] for r in db.execute("SELECT uid, name FROM games")}
        sk = [(v["streak7"], names.get(u, u), v.get("base")) for u, v in b.items() if v.get("streak7")]
        o.append(f"games with badge data: {len(b)} · with a 7-day streak badge: {len(sk)}")
        o += [f"- {nm[:36]}: {s} · base: {base}" for s, nm, base in sk[:15]]
    section(out, "Badge streaks", badges)

    # ------------------------------------------------------------- model report
    def models(o):
        o += ASK.models_lines(db, state, today, fmt)
    section(out, "Model check as the bot would now print it", models)
    return "\n".join(out)

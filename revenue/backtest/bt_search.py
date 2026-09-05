"""Broad search over revenue-based strategies (~100 variants), ranked by Sharpe, with
multiple-testing awareness (split-sample validation + noise-max-Sharpe benchmark) and a
1x/2x/3x leverage overlay.  Reuses the sanitised panel from bt_engine and the holders-revenue /
volume loaders from bt_capture / bt_longhold (imported lazily so missing data degrades gracefully).
"""
import json, os, math, itertools, sys
import numpy as np, pandas as pd
import bt_engine as B

idx, PX, REV, eligible, ret, ew, start = B.idx, B.PX, B.REV, B.eligible, B.ret, B.ew, B.start
sl = slice(start, None); COST = B.COST
rev7 = REV.rolling(7).sum(); rev30 = REV.rolling(30).sum(); rev90 = REV.rolling(90).sum()
prior8 = rev7.shift(7).rolling(49).mean()
T_days = int((idx[-1] - start).days)

# ---- optional panels ----
try:
    import bt_capture as C
    HREV, hrev7, capture, has_cap = C.HREV, C.hrev7, C.capture, C.has_cap
    HAVE_H = True
except Exception as e:
    HAVE_H = False; print("holders revenue unavailable:", e)
try:
    import bt_longhold as L
    tradable = L.tradable(); MC_H = L.MC_H
    HAVE_V = True
except Exception as e:
    HAVE_V = False; print("volume/mcap gate unavailable:", e)
    mcap_now = json.load(open("bt_mcap_now.json"))
    gecko_of = {}
    for e_ in B.U:
        key = e_["symbol"] or e_["name"]
        if key not in REV.columns: key = key + "_" + e_["gecko"]
        if key in REV.columns: gecko_of[key] = e_["gecko"]
    mc_now = pd.Series({c: mcap_now.get(g) for c, g in gecko_of.items()}, dtype="float").reindex(REV.columns)
    MC_H = PX.mul(mc_now / PX.ffill().iloc[-1], axis=1); tradable = MC_H >= 10e6

rev_yield = (rev30 * 365 / 30) / MC_H
mom30 = rev30 / rev30.shift(30) - 1
wow = rev7 / rev7.shift(7) - 1
accel = wow - wow.shift(7)
px30 = PX / PX.shift(30) - 1
def xrank(df): return df.where(eligible).rank(axis=1, pct=True)

# ---------- generic event simulator ----------
def sim_event(entry, exit_, elig=None, max_pos=10, prio=None, size=None, hold=None, cooldown=0, stop=None):
    elig = eligible if elig is None else (eligible & elig)
    ent = (entry & elig).fillna(False); cols = list(PX.columns); T = len(idx)
    entA = ent.values; exA = None if exit_ is None else exit_.fillna(False).values
    pxA = PX.values; eligA = elig.fillna(False).values
    prioA = (prio if prio is not None else (rev7 / prior8)).fillna(0).values
    sizeA = None if size is None else size.fillna(0).values
    cash = 1.0; pos = {}; equity = np.zeros(T); expo = np.zeros(T); trades = []; last_exit = {}
    pend_in, pend_out = [], []
    for t in range(T):
        for c in pend_out:
            if c in pos and not np.isnan(pxA[t, c]):
                p = pos.pop(c); val = p["units"] * pxA[t, c] * (1 - COST); cash += val
                trades.append(val / p["cost"] - 1); last_exit[c] = t
        for c in pend_in:
            if c not in pos and len(pos) < max_pos and not np.isnan(pxA[t, c]):
                mv = cash + sum(pp["units"] * pxA[t, k] for k, pp in pos.items() if not np.isnan(pxA[t, k]))
                mult = 1.0 if sizeA is None else float(np.clip(sizeA[t - 1, c], 0.25, 2.0))
                alloc = min(cash, mult * mv / max_pos)
                if alloc <= 0: continue
                pos[c] = {"units": alloc * (1 - COST) / pxA[t, c], "t": t, "cost": alloc, "peak": pxA[t, c]}; cash -= alloc
        pend_in, pend_out = [], []
        mv = cash + sum(p["units"] * pxA[t, c] for c, p in pos.items() if not np.isnan(pxA[t, c]))
        equity[t] = mv; expo[t] = (mv - cash) / mv if mv > 0 else 0
        for c, p in list(pos.items()):
            if not np.isnan(pxA[t, c]): p["peak"] = max(p["peak"], pxA[t, c])
            leave = (exA is not None and exA[t, c]) or (not eligA[t, c])
            if hold is not None and t - p["t"] >= hold: leave = True
            if stop is not None and pxA[t, c] < p["peak"] * (1 - stop): leave = True
            if leave: pend_out.append(c)
        cands = [c for c in range(len(cols)) if entA[t, c] and c not in pos and c not in pend_out and (t - last_exit.get(c, -9999)) > cooldown]
        cands.sort(key=lambda c: -prioA[t, c])
        pend_in = cands[: max(0, max_pos - len(pos))]
    eq = pd.Series(equity, idx)[sl]; eq = eq / eq.iloc[0]
    return eq, pd.Series(expo, idx)[sl], trades

# ---------- generic weekly rank simulator ----------
def sim_rank(score, top=0.2, reb=7, bottom=False, min_names=5):
    cols = PX.columns; T = len(idx); sc = score.where(eligible); retA = ret.fillna(0)
    w = pd.Series(0.0, index=cols); eq = np.ones(T); expo = np.zeros(T)
    for t in range(1, T):
        eq[t] = eq[t - 1] * (1 + float((w * retA.iloc[t]).sum()))
        if w.sum() > 0: w = w * (1 + retA.iloc[t]); w = w / w.sum() * min(1.0, w.sum())
        if (t - 1) % reb == 0 and idx[t] >= start:
            s = sc.iloc[t - 1].dropna()
            if len(s) >= min_names:
                k = max(min_names, int(round(len(s) * top)))
                pick = (s.nsmallest(k) if bottom else s.nlargest(k)).index
                new = pd.Series(0.0, index=cols); new[pick] = 1.0 / k
                eq[t] *= (1 - COST * float((new - w).abs().sum())); w = new
        expo[t] = float(w.sum())
    e = pd.Series(eq, idx)[sl]; return e / e.iloc[0], pd.Series(expo, idx)[sl], []

# ---------- strategy catalogue ----------
S = []  # (family, label, callable)
def add(fam, label, fn): S.append((fam, label, fn))
def brk(series, K, N):
    pr = series.shift(7).rolling(49).mean(); return (series >= series.rolling(N).max()) & (series / pr >= K) & (pr > 0)
def slow(series, w=28): return series < series.shift(1).rolling(w).mean()
def twodown(series): return (series < series.shift(7)) & (series.shift(7) < series.shift(14))

# A. revenue breakout grid (K x N x exit) -> 45
for K, N in itertools.product((1.5, 2.0, 3.0), (28, 56, 90)):
    e = brk(rev7, K, N)
    add("A breakout", f"brk K{K} N{N} exit=slow4wk", lambda e=e: sim_event(e, slow(rev7)))
    add("A breakout", f"brk K{K} N{N} exit=2down", lambda e=e: sim_event(e, twodown(rev7)))
    for h in (14, 28, 56):
        add("A breakout", f"brk K{K} N{N} exit=hold{h}", lambda e=e, h=h: sim_event(e, None, hold=h))
# A2. breakout + stops / cooldown / ratio cap / trend filter -> 8
e = brk(rev7, 2.0, 56)
add("A2 breakout+", "brk K2 N56 slow + 25% trailing stop", lambda: sim_event(e, slow(rev7), stop=0.25))
add("A2 breakout+", "brk K2 N56 slow + 15% trailing stop", lambda: sim_event(e, slow(rev7), stop=0.15))
add("A2 breakout+", "brk K2 N56 slow + 14d re-entry cooldown", lambda: sim_event(e, slow(rev7), cooldown=14))
add("A2 breakout+", "brk K2 N56 slow + ratio cap <=5x", lambda: sim_event(e & (rev7 / prior8 <= 5), slow(rev7)))
add("A2 breakout+", "brk K2 N56 slow + uptrend filter (rev30 > rev30 60d ago)", lambda: sim_event(e & (rev30 > rev30.shift(60)), slow(rev7)))
add("A2 breakout+", "brk K2 N56 slow + cheap filter (rev yield above median)", lambda: sim_event(e & (xrank(rev_yield) >= 0.5), slow(rev7)))
add("A2 breakout+", "brk K2 N56 slow + tradability gate", lambda: sim_event(e, slow(rev7), elig=tradable))
add("A2 breakout+", "brk K2 N56 slow, 5 slots (concentrated)", lambda: sim_event(e, slow(rev7), max_pos=5))
add("A2 breakout+", "brk K2 N56 slow, 20 slots (diversified)", lambda: sim_event(e, slow(rev7), max_pos=20))
add("A2 breakout+", "brk K2 N56 slow, size by sqrt(rev30 rank)", lambda: sim_event(e, slow(rev7), size=xrank(rev30).pow(0.5) * 1.5))
add("A2 breakout+", "brk K2 N56 slow, size by breakout ratio", lambda: sim_event(e, slow(rev7), size=(rev7 / prior8 / 2).clip(0.5, 2)))
# B/C. holders revenue -> ~10
if HAVE_H:
    for K, N in itertools.product((1.5, 2.0), (28, 56)):
        eh = brk(hrev7, K, N)
        add("B holders-rev breakout", f"HOLDERS brk K{K} N{N} exit=slow", lambda eh=eh: sim_event(eh, slow(hrev7)))
        add("B holders-rev breakout", f"HOLDERS brk K{K} N{N} exit=hold28", lambda eh=eh: sim_event(eh, None, hold=28))
    add("C capture-filtered", "brk K2 N56 slow, capture>0 only", lambda: sim_event(e, slow(rev7), elig=has_cap))
    add("C capture-filtered", "brk K2 N56 slow, capture>=25% only", lambda: sim_event(e, slow(rev7), elig=(capture >= 0.25)))
    add("C capture-filtered", "brk K2 N56 slow, capture>=50% only", lambda: sim_event(e, slow(rev7), elig=(capture >= 0.5)))
    add("C capture-filtered", "brk K2 N56 slow, no-capture names only", lambda: sim_event(e, slow(rev7), elig=~has_cap))
    add("C capture-filtered", "brk K2 N56 slow, prioritise+size by capture", lambda: sim_event(e, slow(rev7), prio=capture, size=0.5 + capture.clip(upper=1)))
# D. weekly rank portfolios -> 16
scores = {"rev mom30": mom30, "rev WoW": wow, "rev accel": accel, "rev yield": rev_yield, "value+growth": (xrank(mom30) + xrank(rev_yield)) / 2,
          "divergence": xrank(mom30) - xrank(px30), "rev level (biggest earners)": rev30, "rev 90d growth": rev90 / rev90.shift(90) - 1}
for nm, sc in scores.items():
    for top in (0.1, 0.2):
        add("D weekly rank", f"RANK {nm} top{int(top*100)}%", lambda sc=sc, top=top: sim_rank(sc, top))
add("D weekly rank", "RANK L/S rev mom30 top20% - bottom20%", lambda: (lambda a, b: ((1 + (a[0].pct_change().fillna(0) - b[0].pct_change().fillna(0))).cumprod(), a[1], []))(sim_rank(mom30, 0.2), sim_rank(mom30, 0.2, bottom=True)))
# E. long holds -> 12
first_cross = (rev30 >= 1e6) & (rev30.shift(1) < 1e6) & (rev30.cummax().shift(1) < 1e6) & (mom30 > 0.5)
ramp3 = (rev30 > rev30.shift(30)) & (rev30.shift(30) > rev30.shift(60)) & (rev30.shift(60) > rev30.shift(90)) & (rev30 >= 1e6)
rank_ = rev30.where(eligible).rank(axis=1, ascending=False); climber = (rank_ <= 50) & (rank_.shift(60) - rank_ >= 20)
peak90 = rev30.rolling(90).max()
for en_nm, en in (("first$1M", first_cross), ("ramp3", ramp3), ("climber", climber), ("any", first_cross | ramp3 | climber)):
    for th in (0.4, 0.5, 0.6):
        add("E long-hold", f"HOLD {en_nm} exit rev30<{int((1-th)*100)}% of 90d peak", lambda en=en, th=th: sim_event(en, rev30 < (1 - th) * peak90, elig=tradable, max_pos=15, prio=mom30))
    add("E long-hold", f"HOLD {en_nm} exit MoM<-30%", lambda en=en: sim_event(en, mom30 < -0.3, elig=tradable, max_pos=15, prio=mom30))
# F. combos -> 6
add("F combo", "brk K1.5 N28 slow AND capture>0 AND uptrend", lambda: sim_event(brk(rev7, 1.5, 28) & (rev30 > rev30.shift(60)) & (has_cap if HAVE_H else True), slow(rev7)))
add("F combo", "brk K2 N56 hold28 + cooldown14 + cap5x", lambda: sim_event(e & (rev7 / prior8 <= 5), None, hold=28, cooldown=14))
add("F combo", "brk K2 N56 slow + tradable + uptrend + cooldown14", lambda: sim_event(e & (rev30 > rev30.shift(60)), slow(rev7), elig=tradable, cooldown=14))
add("F combo", "brk K3 N90 hold56 (rare, big moves)", lambda: sim_event(brk(rev7, 3.0, 90), None, hold=56))
add("F combo", "brk K2 N56, exit slow OR MoM<-30%", lambda: sim_event(e, slow(rev7) | (mom30 < -0.3)))
add("F combo", "HOLD any + brk overlay (enter on either)", lambda: sim_event((first_cross | ramp3 | climber) | e, (rev30 < 0.5 * peak90) & slow(rev7), elig=tradable, max_pos=15))

print("strategies in catalogue:", len(S), flush=True)

# ---------- evaluate ----------
def sharpe(r): v = r.std() * math.sqrt(365); return float(r.mean() * 365 / v) if v > 0 else float("nan")
def mdd(eq): return float((eq / eq.cummax() - 1).min())
mid = start + (idx[-1] - start) / 2
rows, curves = [], {}
for i, (fam, label, fn) in enumerate(S):
    try:
        eq, expo, trades = fn()
    except Exception as ex:
        print("FAILED", label, ex); continue
    r = eq.pct_change().dropna()
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    rows.append({"family": fam, "label": label, "total": float(eq.iloc[-1] - 1), "cagr": float(eq.iloc[-1] ** (1 / yrs) - 1), "sharpe": sharpe(r),
                 "maxdd": mdd(eq), "vol": float(r.std() * math.sqrt(365)), "exposure": float(expo.mean()) if len(expo) else None,
                 "n_trades": len(trades), "hit": float(np.mean([x > 0 for x in trades])) if trades else None,
                 "sharpe_h1": sharpe(r[r.index < mid]), "sharpe_h2": sharpe(r[r.index >= mid]),
                 "ret_h1": float(eq[eq.index < mid].iloc[-1] / eq.iloc[0] - 1), "ret_h2": float(eq.iloc[-1] / eq[eq.index < mid].iloc[-1] - 1)})
    curves[label] = eq
    if i % 10 == 0: print(f"  {i}/{len(S)} done", flush=True)
df = pd.DataFrame(rows)
# benchmarks
for nm, eq in (("BTC", B.BTCeq), ("ETH", B.ETHeq), ("EW universe", (1 + ew[sl]).cumprod())):
    r = eq.pct_change().dropna(); yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    df.loc[len(df)] = {"family": "bench", "label": nm, "total": float(eq.iloc[-1] - 1), "cagr": float(eq.iloc[-1] ** (1 / yrs) - 1), "sharpe": sharpe(r), "maxdd": mdd(eq),
                       "vol": float(r.std() * math.sqrt(365)), "exposure": 1.0, "n_trades": 0, "hit": None, "sharpe_h1": sharpe(r[r.index < mid]), "sharpe_h2": sharpe(r[r.index >= mid]),
                       "ret_h1": float(eq[eq.index < mid].iloc[-1] / eq.iloc[0] - 1), "ret_h2": float(eq.iloc[-1] / eq[eq.index < mid].iloc[-1] - 1)}
    curves[nm] = eq

# multiple-testing benchmark: expected max Sharpe of N independent noise strategies over T daily obs
N = len(S); T = len(ew[sl])
noise_max = math.sqrt(2 * math.log(N)) * math.sqrt(365 / T)
# holdout: rank by first-half Sharpe, evaluate second-half
strat = df[df.family != "bench"].copy()
top_h1 = strat.sort_values("sharpe_h1", ascending=False).head(10)

# leverage overlay on top strategies: L x daily return - (L-1) x 10%/yr funding, wipeout at 0
def lever(eq, Lv, fund=0.10):
    r = eq.pct_change().fillna(0); lr = Lv * r - (Lv - 1) * fund / 365
    e = (1 + lr).cumprod(); e[e.cummin() <= 0] = 0
    return e
top_full = strat.sort_values("sharpe", ascending=False).head(10)
lev_rows = []
for _, row in top_full.head(5).iterrows():
    for Lv in (1, 2, 3):
        e2 = lever(curves[row.label], Lv); r2 = e2.pct_change().dropna()
        lev_rows.append({"label": row.label, "L": Lv, "total": float(e2.iloc[-1] - 1), "sharpe": sharpe(r2) if e2.iloc[-1] > 0 else float("nan"), "maxdd": mdd(e2), "wiped": bool(e2.iloc[-1] <= 0)})

pd.set_option("display.width", 250); pd.set_option("display.float_format", lambda v: f"{v:,.2f}"); pd.set_option("display.max_colwidth", 60)
print(f"\n=== {N} strategies, {start.date()} -> {idx[-1].date()} ({T} days). Expected MAX Sharpe from {N} pure-noise strategies on this much data ≈ {noise_max:.2f} ===")
print("\nSharpe distribution across all strategies:", strat.sharpe.describe()[["mean", "50%", "75%", "max"]].round(2).to_dict())
print("share with Sharpe > BTC:", f"{(strat.sharpe > df[df.label=='BTC'].sharpe.iloc[0]).mean():.0%}", "| share positive total:", f"{(strat.total > 0).mean():.0%}")
print("\nTOP 15 by full-sample Sharpe:")
print(strat.sort_values("sharpe", ascending=False).head(15)[["family", "label", "total", "cagr", "sharpe", "maxdd", "exposure", "n_trades", "hit", "sharpe_h1", "sharpe_h2"]].to_string(index=False))
print("\nHOLDOUT: top 10 by FIRST-half Sharpe -> how they did in the SECOND half:")
print(top_h1[["label", "sharpe_h1", "ret_h1", "sharpe_h2", "ret_h2", "total"]].to_string(index=False))
print(f"second-half Sharpe of the first-half top-10: mean {top_h1.sharpe_h2.mean():.2f} | median {top_h1.sharpe_h2.median():.2f} | all strategies' second-half median {strat.sharpe_h2.median():.2f} | BTC h2 {df[df.label=='BTC'].sharpe_h2.iloc[0]:.2f}")
print("\nBY FAMILY (median Sharpe, best Sharpe, median maxDD):")
print(strat.groupby("family").agg(n=("label", "count"), med_sharpe=("sharpe", "median"), best_sharpe=("sharpe", "max"), med_dd=("maxdd", "median"), med_total=("total", "median")).round(2).to_string())
print("\nLEVERAGE overlay (10%/yr funding on borrowed portion, daily rebalanced) on the top 5:")
print(pd.DataFrame(lev_rows).to_string(index=False))
print("\nbenchmarks:"); print(df[df.family == "bench"][["label", "total", "sharpe", "maxdd", "sharpe_h1", "sharpe_h2"]].to_string(index=False))
json.dump({"n": N, "T": T, "noise_max_sharpe": noise_max, "start": str(start.date()), "end": str(idx[-1].date()),
           "table": df.replace({np.nan: None}).to_dict("records"), "leverage": lev_rows,
           "curves": {k: [[str(d.date()), round(float(v), 5)] for d, v in curves[k].dropna().items()] for k in list(top_full.label) + ["BTC", "ETH", "EW universe"]}},
          open("bt_results_search.json", "w"))
print("saved bt_results_search.json")

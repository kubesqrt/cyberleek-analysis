"""Joint test: breakout 2x/8wk + exit on slowdown + trailing stop + cheap-on-P/S sizing, 5 vs 10 slots."""
import json, math, numpy as np, pandas as pd, bt_engine as B
idx, PX, REV, eligible, ret, ew, start = B.idx, B.PX, B.REV, B.eligible, B.ret, B.ew, B.start
sl = slice(start, None); COST = B.COST
rev7 = REV.rolling(7).sum(); rev30 = REV.rolling(30).sum(); prior8 = rev7.shift(7).rolling(49).mean()
entry = ((rev7 >= rev7.rolling(56).max()) & (rev7 / prior8 >= 2.0) & (prior8 > 0)); exit_ = rev7 < rev7.shift(1).rolling(28).mean()
mcap_now = json.load(open("bt_mcap_now.json")); gecko_of = {}
for e in B.U:
    key = e["symbol"] or e["name"]
    if key not in REV.columns: key = key + "_" + e["gecko"]
    if key in REV.columns: gecko_of[key] = e["gecko"]
mc_now = pd.Series({c: mcap_now.get(g) for c, g in gecko_of.items()}, dtype="float").reindex(REV.columns)
MC = PX.mul(mc_now / PX.ffill().iloc[-1], axis=1); rev_yield = (rev30 * 365 / 30) / MC
cheap = 0.25 + 1.75 * rev_yield.where(eligible).rank(axis=1, pct=True)

def sim(size=None, max_pos=10, stop=None):
    ent = (entry & eligible).fillna(False); cols = list(PX.columns); T = len(idx)
    entA = ent.values; exA = exit_.fillna(False).values; pxA = PX.values; eligA = eligible.fillna(False).values
    prioA = (rev7 / prior8).fillna(0).values; sizeA = None if size is None else size.fillna(1.0).values
    cash = 1.0; pos = {}; equity = np.zeros(T); expo = np.zeros(T); trades = []; pend_in, pend_out = [], []
    for t in range(T):
        for c in pend_out:
            if c in pos and not np.isnan(pxA[t, c]):
                p = pos.pop(c); val = p["units"] * pxA[t, c] * (1 - COST); cash += val; trades.append(val / p["cost"] - 1)
        for c in pend_in:
            if c not in pos and len(pos) < max_pos and not np.isnan(pxA[t, c]):
                mv = cash + sum(pp["units"] * pxA[t, k] for k, pp in pos.items() if not np.isnan(pxA[t, k]))
                mult = 1.0 if sizeA is None else float(np.clip(sizeA[t - 1, c], 0.25, 2.0)); alloc = min(cash, mult * mv / max_pos)
                if alloc <= 0: continue
                pos[c] = {"units": alloc * (1 - COST) / pxA[t, c], "cost": alloc, "peak": pxA[t, c]}; cash -= alloc
        pend_in, pend_out = [], []
        mv = cash + sum(p["units"] * pxA[t, c] for c, p in pos.items() if not np.isnan(pxA[t, c])); equity[t] = mv; expo[t] = (mv - cash) / mv if mv > 0 else 0
        for c, p in list(pos.items()):
            if not np.isnan(pxA[t, c]): p["peak"] = max(p["peak"], pxA[t, c])
            if exA[t, c] or not eligA[t, c] or (stop is not None and pxA[t, c] < p["peak"] * (1 - stop)): pend_out.append(c)
        cands = [c for c in range(len(cols)) if entA[t, c] and c not in pos and c not in pend_out]; cands.sort(key=lambda c: -prioA[t, c]); pend_in = cands[: max(0, max_pos - len(pos))]
    eq = pd.Series(equity, idx)[sl]; return eq / eq.iloc[0], pd.Series(expo, idx)[sl], trades
def sharpe(r): v = r.std() * math.sqrt(365); return float(r.mean() * 365 / v) if v > 0 else float("nan")
mid = start + (idx[-1] - start) / 2
rows = {}; curves = {}
for label, kw in {"base (10 slots, equal wt)": {}, "+ 25% stop": dict(stop=0.25), "+ cheap P/S sizing": dict(size=cheap),
                  "+ stop + cheap sizing": dict(size=cheap, stop=0.25), "+ stop + cheap sizing, 5 slots": dict(size=cheap, stop=0.25, max_pos=5),
                  "+ cheap sizing, 5 slots": dict(size=cheap, max_pos=5), "+ stop, 5 slots": dict(stop=0.25, max_pos=5)}.items():
    eq, ex, tr = sim(**kw); r = eq.pct_change().dropna()
    rows[label] = {"total": float(eq.iloc[-1] - 1), "sharpe": sharpe(r), "maxdd": float((eq / eq.cummax() - 1).min()), "exposure": float(ex.mean()), "n": len(tr), "hit": float(np.mean([x > 0 for x in tr])),
                   "sharpe_h1": sharpe(r[r.index < mid]), "sharpe_h2": sharpe(r[r.index >= mid]), "ret_h2": float(eq.iloc[-1] / eq[eq.index < mid].iloc[-1] - 1), "ytd2026": float(eq.iloc[-1] / eq[eq.index <= "2026-01-01"].iloc[-1] - 1)}
    curves[label] = eq
df = pd.DataFrame(rows).T; pd.set_option("display.width", 200); pd.set_option("display.float_format", lambda v: f"{v:,.3f}")
print("JOINT TEST (all use breakout 2x/8wk, exit on revenue slowdown):"); print(df.to_string())
json.dump({"stats": {k: v for k, v in rows.items()}, "curves": {k: [[str(d.date()), round(float(v), 5)] for d, v in c.items()] for k, c in curves.items()}}, open("bt_results_combo.json", "w"))

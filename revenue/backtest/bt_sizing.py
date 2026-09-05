"""Position-sizing study on the best breakout rule (2x / 8-wk high -> exit when revenue slows),
plus vol-targeted leverage overlays.  Reuses the sanitised panel from bt_engine.
"""
import json, os, math
import numpy as np, pandas as pd
import bt_engine as B

idx, PX, REV, eligible, ret, ew, start = B.idx, B.PX, B.REV, B.eligible, B.ret, B.ew, B.start
sl = slice(start, None); COST = B.COST; MAX_POS = 10
rev7 = REV.rolling(7).sum(); rev30 = REV.rolling(30).sum(); prior8 = rev7.shift(7).rolling(49).mean()
entry = ((rev7 >= rev7.rolling(56).max()) & (rev7 / prior8 >= 2.0) & (prior8 > 0))
exit_ = rev7 < rev7.shift(1).rolling(28).mean()

# ---- panels: capture, mcap/fdv proxies, vol, liquidity ----
def load_dir(e, d):
    s = None
    for slug in e["slugs"]:
        f = f"{d}/{slug}.json"
        if not os.path.exists(f): continue
        pts = json.load(open(f))
        if not pts: continue
        ser = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(v or 0) for t, v in pts})
        s = ser if s is None else s.add(ser, fill_value=0)
    return s
keys, gecko_of = {}, {}
for e in B.U:
    key = e["symbol"] or e["name"]
    if key not in REV.columns: key = key + "_" + e["gecko"]
    if key in REV.columns: keys[key] = e; gecko_of[key] = e["gecko"]
HREV = pd.DataFrame({k: (load_dir(e, "bt_hrev") if load_dir(e, "bt_hrev") is not None else pd.Series(dtype=float)) for k, e in keys.items()}).reindex(idx).reindex(columns=REV.columns)
HREV = HREV.where(REV.notna(), np.nan).fillna(0.0)
capture = (HREV.rolling(30).sum() / rev30.replace(0, np.nan)).clip(upper=1.5).fillna(0)
mcap_now = json.load(open("bt_mcap_now.json"))
fdv_now = json.load(open("bt_fdv_now.json")) if os.path.exists("bt_fdv_now.json") else {}
last = PX.ffill().iloc[-1]
mc_now = pd.Series({c: mcap_now.get(g) for c, g in gecko_of.items()}, dtype="float").reindex(REV.columns)
fd_now = pd.Series({c: (fdv_now.get(g) or {}).get("fdv") for c, g in gecko_of.items()}, dtype="float").reindex(REV.columns)
MC = PX.mul(mc_now / last, axis=1); FDV = PX.mul(fd_now / last, axis=1)
ann = rev30 * 365 / 30
rev_yield = ann / MC; fdv_yield = ann / FDV; dilution = (MC / FDV).clip(upper=1)
vol30 = ret.rolling(30).std() * math.sqrt(365)
consistency = (rev7 > rev7.shift(7)).rolling(56).mean()      # share of last 8 weeks with rising weekly revenue
px_trend = (PX > PX.rolling(30).mean()).astype(float)
def load_vol(g):
    f = f"bt_vol/{g}.json"
    if not os.path.exists(f): return None
    pts = json.load(open(f)).get("volumes") or []
    if not pts: return None
    s = pd.Series({pd.Timestamp(int(t / 1000), unit="s").normalize(): float(v) for t, v in pts if v is not None}); return s[~s.index.duplicated(keep="last")].sort_index()
VOL = pd.DataFrame({c: load_vol(g) for c, g in gecko_of.items()}).reindex(idx).reindex(columns=REV.columns).ffill(limit=5)
turnover = (VOL.rolling(7).mean() / MC)
def xr(df): return df.where(eligible).rank(axis=1, pct=True)   # cross-sectional percentile rank, 0..1
def tilt(rank_df, lo=0.5, hi=1.5): return lo + (hi - lo) * rank_df   # map rank -> size multiplier

SIZES = {
    "equal weight (base)": None,
    "capture 0.5-1.5x (prev best)": 0.5 + capture.clip(upper=1),
    "cheap on P/S: rev-yield rank 0.5-1.5x": tilt(xr(rev_yield)),
    "cheap on P/S, stronger tilt 0.25-2x": tilt(xr(rev_yield), 0.25, 2.0),
    "cheap on P/F: fdv-yield rank 0.5-1.5x": tilt(xr(fdv_yield)),
    "low dilution overhang (mcap/FDV high) 0.5-1.5x": tilt(xr(dilution)),
    "expensive on P/S (inverse test) 0.5-1.5x": tilt(1 - xr(rev_yield)),
    "capture x cheapness (rank avg) 0.5-1.5x": tilt((xr(rev_yield) + xr(capture)) / 2),
    "inverse vol (risk parity) 0.5-1.5x": tilt(xr(1 / vol30)),
    "bigger earners (rev30 rank) 0.5-1.5x": tilt(xr(rev30)),
    "small-cap tilt (low mcap) 0.5-1.5x": tilt(1 - xr(MC)),
    "large-cap tilt (high mcap) 0.5-1.5x": tilt(xr(MC)),
    "breakout strength (ratio/2) 0.5-2x": (rev7 / prior8 / 2).clip(0.5, 2),
    "price trend confirm (above 30d avg -> 1.5x else 0.75x)": 0.75 + 0.75 * px_trend,
    "revenue consistency (8-wk up-weeks share) 0.5-1.5x": tilt(consistency.fillna(0)),
    "liquidity: turnover rank 0.5-1.5x (365d of data)": tilt(xr(turnover).fillna(0.5)),
    "composite: capture + cheap + inverse vol 0.5-1.5x": tilt((xr(capture) + xr(rev_yield) + xr(1 / vol30)) / 3),
    "composite stronger 0.25-2x": tilt((xr(capture) + xr(rev_yield) + xr(1 / vol30)) / 3, 0.25, 2.0),
}

def sim(size=None, max_pos=MAX_POS):
    ent = (entry & eligible).fillna(False); cols = list(PX.columns); T = len(idx)
    entA = ent.values; exA = exit_.fillna(False).values; pxA = PX.values; eligA = eligible.fillna(False).values
    prioA = (rev7 / prior8).fillna(0).values; sizeA = None if size is None else size.fillna(1.0).values
    cash = 1.0; pos = {}; equity = np.zeros(T); expo = np.zeros(T); trades = []
    pend_in, pend_out = [], []
    for t in range(T):
        for c in pend_out:
            if c in pos and not np.isnan(pxA[t, c]):
                p = pos.pop(c); val = p["units"] * pxA[t, c] * (1 - COST); cash += val; trades.append(val / p["cost"] - 1)
        for c in pend_in:
            if c not in pos and len(pos) < max_pos and not np.isnan(pxA[t, c]):
                mv = cash + sum(pp["units"] * pxA[t, k] for k, pp in pos.items() if not np.isnan(pxA[t, k]))
                mult = 1.0 if sizeA is None else float(np.clip(sizeA[t - 1, c], 0.25, 2.0))
                alloc = min(cash, mult * mv / max_pos)
                if alloc <= 0: continue
                pos[c] = {"units": alloc * (1 - COST) / pxA[t, c], "cost": alloc}; cash -= alloc
        pend_in, pend_out = [], []
        mv = cash + sum(p["units"] * pxA[t, c] for c, p in pos.items() if not np.isnan(pxA[t, c]))
        equity[t] = mv; expo[t] = (mv - cash) / mv if mv > 0 else 0
        for c in list(pos):
            if exA[t, c] or not eligA[t, c]: pend_out.append(c)
        cands = [c for c in range(len(cols)) if entA[t, c] and c not in pos and c not in pend_out]
        cands.sort(key=lambda c: -prioA[t, c]); pend_in = cands[: max(0, max_pos - len(pos))]
    eq = pd.Series(equity, idx)[sl]; eq = eq / eq.iloc[0]
    return eq, pd.Series(expo, idx)[sl], trades

def sharpe(r): v = r.std() * math.sqrt(365); return float(r.mean() * 365 / v) if v > 0 else float("nan")
def mdd(eq): return float((eq / eq.cummax() - 1).min())
mid = start + (idx[-1] - start) / 2
rows, curves = [], {}
for name, sz in SIZES.items():
    eq, expo, tr = sim(sz); r = eq.pct_change().dropna()
    rows.append({"sizing": name, "total": float(eq.iloc[-1] - 1), "sharpe": sharpe(r), "maxdd": mdd(eq), "vol": float(r.std() * math.sqrt(365)),
                 "exposure": float(expo.mean()), "n": len(tr), "hit": float(np.mean([x > 0 for x in tr])), "avg": float(np.mean(tr)),
                 "sharpe_h1": sharpe(r[r.index < mid]), "sharpe_h2": sharpe(r[r.index >= mid])})
    curves[name] = eq
df = pd.DataFrame(rows)
pd.set_option("display.width", 240); pd.set_option("display.float_format", lambda v: f"{v:,.3f}"); pd.set_option("display.max_colwidth", 58)
print("SIZING STUDY on breakout 2x/8wk -> exit on slowdown,", start.date(), "->", idx[-1].date())
print(df.sort_values("sharpe", ascending=False).to_string(index=False))

# ---- leverage: constant vs vol-targeted, on base and on the best sizing ----
def lever_const(eq, Lv, fund=0.10):
    r = eq.pct_change().fillna(0); e = (1 + Lv * r - (Lv - 1) * fund / 365).cumprod(); e[e.cummin() <= 0] = 0; return e
def lever_voltarget(eq, target, cap=3.0, fund=0.10):
    r = eq.pct_change().fillna(0); rv = r.rolling(30).std() * math.sqrt(365)
    Lt = (target / rv).clip(upper=cap).shift(1).fillna(1.0).clip(lower=0)
    e = (1 + Lt * r - (Lt - 1).clip(lower=0) * fund / 365).cumprod(); e[e.cummin() <= 0] = 0; return e, Lt
best = df.sort_values("sharpe", ascending=False).iloc[0].sizing
lev = []
for nm in ["equal weight (base)", best]:
    eq = curves[nm]
    for Lv in (1, 2, 3):
        e2 = lever_const(eq, Lv); r2 = e2.pct_change().dropna()
        lev.append({"strategy": nm, "overlay": f"constant {Lv}x", "total": float(e2.iloc[-1] - 1), "sharpe": sharpe(r2) if e2.iloc[-1] > 0 else float("nan"), "maxdd": mdd(e2), "avg_lev": float(Lv)})
    for tg in (0.4, 0.6, 0.8):
        e2, Lt = lever_voltarget(eq, tg); r2 = e2.pct_change().dropna()
        lev.append({"strategy": nm, "overlay": f"vol-target {int(tg*100)}% (cap 3x)", "total": float(e2.iloc[-1] - 1), "sharpe": sharpe(r2) if e2.iloc[-1] > 0 else float("nan"), "maxdd": mdd(e2), "avg_lev": float(Lt[sl].mean())})
L = pd.DataFrame(lev)
print("\nLEVERAGE OVERLAYS (10%/yr funding on borrowed portion; daily rebalanced; wipeout at 0):")
print(L.to_string(index=False))
json.dump({"sizing": df.replace({np.nan: None}).to_dict("records"), "leverage": L.replace({np.nan: None}).to_dict("records"),
           "curves": {k: [[str(d.date()), round(float(v), 5)] for d, v in curves[k].items()] for k in ["equal weight (base)", best]}},
          open("bt_results_sizing.json", "w"))
print("saved bt_results_sizing.json; best sizing:", best)

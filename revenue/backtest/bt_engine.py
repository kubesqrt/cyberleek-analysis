"""Revenue-breakout backtest.

Signal:  rev7d breaks out — rev7d >= K x mean(rev7d over prior 8 weeks, excluding
         current week) AND rev7d is a new N-day high.
Exit:    revenue momentum slows (rev7d < trailing 4-week average of rev7d), or
         variants (2 down weeks, fixed 28d hold), optional -25% trailing stop.
Trading: signal computed on day t (UTC-complete data), executed at close t+1,
         equal notional 1/MAX_POS per position, costs COST per side.
"""
import json, os, math, sys
import numpy as np, pandas as pd

U = json.load(open("bt_universe.json"))
COST = 0.005
MAX_POS = 10
MIN_REV30 = 100_000        # point-in-time eligibility: >=$100k revenue / 30d
MIN_HIST = 90              # days of revenue history before a name is eligible

def load_rev(e):
    s = None
    for slug in e["slugs"]:
        f = f"bt_rev/{slug}.json"
        if not os.path.exists(f): continue
        pts = json.load(open(f))
        if not pts: continue
        ser = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(v or 0) for t, v in pts})
        s = ser if s is None else s.add(ser, fill_value=0)
    return s

def load_px(g):
    f = f"bt_px/{g}.json"
    if not os.path.exists(f): return None
    pts = json.load(open(f))
    if not pts: return None
    ser = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(p) for t, p in pts})
    return ser[~ser.index.duplicated(keep="last")].sort_index()

rev, px, names = {}, {}, {}
for e in U:
    r = load_rev(e); p = load_px(e["gecko"])
    if r is None or p is None or len(r) < MIN_HIST or len(p) < MIN_HIST: continue
    key = e["symbol"] or e["name"]
    if key in rev: key = key + "_" + e["gecko"]
    rev[key] = r; px[key] = p; names[key] = e["name"]

REV = pd.DataFrame(rev).sort_index()
PX = pd.DataFrame(px).sort_index()
idx = pd.date_range(max(REV.index.min(), PX.index.min()), min(REV.index.max(), PX.index.max()), freq="D")
REV = REV.reindex(idx)
PX = PX.reindex(idx).ffill(limit=3)
# revenue: NaN before first report; zeros inside history are real zeros
first_rev = REV.apply(lambda c: c.first_valid_index())
for c in REV.columns:
    fv = first_rev[c]
    if fv is not None:
        REV.loc[fv:, c] = REV.loc[fv:, c].fillna(0.0)

BTC = load_px("bitcoin").reindex(idx).ffill(); ETH = load_px("ethereum").reindex(idx).ffill()

# ---- data sanitation: a genuine token can't 4x AND round-trip in a day; such prints are feed errors
_r = PX.pct_change()
_bad_days = (_r > 3.0) | (_r < -0.9)
_dropped = []
for c in PX.columns:
    if _bad_days[c].any():
        # if the spike reverts within 3 days it's a bad print -> mask those days; else drop the token entirely
        for d in idx[_bad_days[c].values]:
            i = idx.get_loc(d)
            win = PX[c].iloc[max(0, i - 1): i + 4]
            if win.iloc[0] > 0 and abs(win.iloc[-1] / win.iloc[0] - 1) < 1.0:
                PX.loc[idx[i]: idx[min(len(idx) - 1, i + 2)], c] = np.nan
            else:
                _dropped.append(c); break
PX = PX.drop(columns=list(set(_dropped))).ffill(limit=3)
REV = REV[PX.columns]
print("sanitised: dropped", sorted(set(_dropped)), "| masked bad prints in", int((PX.isna() & ~PX.ffill().isna()).sum().sum()), "cells") if __name__ == "__main__" else None

rev7 = REV.rolling(7).sum()
rev30 = REV.rolling(30).sum()
hist_days = REV.notna().cumsum()
eligible = (rev30 >= MIN_REV30) & (hist_days >= MIN_HIST) & PX.notna()
ret = PX.pct_change()

def signals(K=1.5, N=28, exit_rule="slow", stop=None, price_only=False):
    """returns entry/exit boolean frames."""
    if price_only:
        base = PX
        prior = PX.shift(7).rolling(49).mean()
        hi = PX.rolling(N).max()
        entry = (PX >= hi) & (PX / prior >= K)
    else:
        prior = rev7.shift(7).rolling(49).mean()      # prior 8 weeks, current week excluded
        hi = rev7.rolling(N).max()
        entry = (rev7 >= hi) & (rev7 / prior >= K) & (prior > 0)
    if exit_rule == "slow":
        ex = (rev7 < rev7.shift(1).rolling(28).mean()) if not price_only else (PX < PX.shift(1).rolling(28).mean())
    elif exit_rule == "2down":
        ex = (rev7 < rev7.shift(7)) & (rev7.shift(7) < rev7.shift(14))
    elif exit_rule == "hold28":
        ex = None
    else:
        raise ValueError(exit_rule)
    return entry & eligible, ex

def run(K=1.5, N=28, exit_rule="slow", stop=None, price_only=False, label=None):
    entry, ex = signals(K, N, exit_rule, stop, price_only)
    cols = list(PX.columns); T = len(idx)
    entryA = entry.fillna(False).values; exA = None if ex is None else ex.fillna(False).values
    retA = ret.fillna(0).values; pxA = PX.values; eligA = eligible.values
    ratioA = (rev7 / rev7.shift(7).rolling(49).mean()).fillna(0).values if not price_only else (PX / PX.shift(7).rolling(49).mean()).fillna(0).values
    cash = 1.0; pos = {}  # col -> dict(units, entry_px, entry_t, peak)
    equity = np.zeros(T); trades = []; expo = np.zeros(T)
    pending_entries = []; pending_exits = []
    for t in range(T):
        # execute yesterday's decisions at today's close
        for c in pending_exits:
            if c in pos and not np.isnan(pxA[t, c]):
                p = pos.pop(c); val = p["units"] * pxA[t, c] * (1 - COST)
                cash += val
                trades.append({"sym": cols[c], "entry": str(idx[p["entry_t"]].date()), "exit": str(idx[t].date()),
                               "ret": val / p["cost"] - 1, "days": t - p["entry_t"]})
        for c in pending_entries:
            if c not in pos and len(pos) < MAX_POS and not np.isnan(pxA[t, c]):
                alloc = min(cash, 1.0 / MAX_POS * max(cash + sum(pp["units"] * pxA[t, k] for k, pp in pos.items() if not np.isnan(pxA[t, k])), 1e-9))
                alloc = min(alloc, cash)
                if alloc <= 0: continue
                units = alloc * (1 - COST) / pxA[t, c]
                cash -= alloc
                pos[c] = {"units": units, "entry_px": pxA[t, c], "entry_t": t, "peak": pxA[t, c], "cost": alloc}
        pending_entries, pending_exits = [], []
        # mark
        mv = cash + sum(p["units"] * pxA[t, c] for c, p in pos.items() if not np.isnan(pxA[t, c]))
        equity[t] = mv; expo[t] = (mv - cash) / mv if mv > 0 else 0
        # decide for tomorrow
        for c, p in list(pos.items()):
            if not np.isnan(pxA[t, c]): p["peak"] = max(p["peak"], pxA[t, c])
            leave = False
            if exA is not None and exA[t, c]: leave = True
            if exit_rule == "hold28" and t - p["entry_t"] >= 28: leave = True
            if stop is not None and pxA[t, c] < p["peak"] * (1 - stop): leave = True
            if not eligA[t, c]: leave = True
            if leave: pending_exits.append(c)
        cands = [c for c in range(len(cols)) if entryA[t, c] and c not in pos and c not in pending_exits]
        cands.sort(key=lambda c: -ratioA[t, c])
        pending_entries = cands[: max(0, MAX_POS - len(pos))]
    eq = pd.Series(equity, idx)
    return {"label": label or f"K{K}_N{N}_{exit_rule}{'_stop'+str(stop) if stop else ''}{'_PRICE' if price_only else ''}",
            "equity": eq, "trades": trades, "exposure": float(expo.mean()), "expo_series": pd.Series(expo, idx)}

def stats(eq, trades=None, expo=None):
    eq = eq.dropna(); r = eq.pct_change().dropna()
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    tot = eq.iloc[-1] / eq.iloc[0] - 1
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan
    vol = r.std() * math.sqrt(365)
    sharpe = (r.mean() * 365) / vol if vol > 0 else np.nan
    dd = (eq / eq.cummax() - 1).min()
    out = {"total": tot, "cagr": cagr, "vol": vol, "sharpe": sharpe, "maxdd": dd}
    if trades is not None and len(trades):
        tr = pd.DataFrame(trades)
        out.update({"n_trades": len(tr), "hit": float((tr.ret > 0).mean()), "avg_ret": float(tr.ret.mean()),
                    "med_ret": float(tr.ret.median()), "avg_days": float(tr.days.mean()),
                    "best": float(tr.ret.max()), "worst": float(tr.ret.min())})
    if expo is not None: out["exposure"] = expo
    return out

# ---------- benchmarks ----------
start = eligible.sum(axis=1).ge(15).idxmax()   # first day with >=15 eligible names
sl = slice(start, None)
ew = (ret.where(eligible.shift(1)).mean(axis=1)).fillna(0)
EW = (1 + ew[sl]).cumprod()
BTCeq = (BTC[sl] / BTC[sl].iloc[0]); ETHeq = (ETH[sl] / ETH[sl].iloc[0])

# ---------- event study ----------
def event_study(K=1.5, N=28):
    entry, _ = signals(K, N)
    ev = []
    fwd = {h: PX.shift(-h - 1) / PX.shift(-1) - 1 for h in (7, 28, 90)}     # buy at t+1 close
    ewfwd = {h: (1 + ew).cumprod().shift(-h - 1) / (1 + ew).cumprod().shift(-1) - 1 for h in (7, 28, 90)}
    e2 = entry & ~entry.shift(1).fillna(False).astype(bool)   # first day only
    for c in PX.columns:
        for t in idx[e2[c].fillna(False).values]:
            if t < start: continue
            row = {"sym": c, "date": str(t.date())}
            for h in (7, 28, 90):
                row[f"r{h}"] = fwd[h].at[t, c]; row[f"x{h}"] = fwd[h].at[t, c] - ewfwd[h].at[t]
            ev.append(row)
    return pd.DataFrame(ev)

if __name__ == "__main__":
    print("panel:", REV.shape, "from", idx[0].date(), "to", idx[-1].date(), "| backtest start", start.date())
    print("eligible names now:", int(eligible.iloc[-1].sum()), "| avg eligible:", round(eligible[sl].sum(axis=1).mean(), 1))
    results = {}
    grid = []
    for K in (1.5, 2.0):
        for N in (28, 56):
            for ex in ("slow", "2down", "hold28"):
                grid.append(dict(K=K, N=N, exit_rule=ex))
    grid.append(dict(K=1.5, N=28, exit_rule="slow", stop=0.25))
    grid.append(dict(K=1.5, N=28, exit_rule="slow", price_only=True, label="PRICE breakout control"))
    grid.append(dict(K=2.0, N=56, exit_rule="slow", price_only=True, label="PRICE breakout control K2 N56"))
    rows = []
    for g in grid:
        r = run(**g); eq = r["equity"][sl]; eq = eq / eq.iloc[0]
        s = stats(eq, r["trades"], r["exposure"]); s["label"] = r["label"]
        # exposure-matched benchmark: EW universe return scaled by the strategy's own daily exposure
        matched = (1 + ew[sl] * r["expo_series"][sl].shift(1).fillna(0)).cumprod()
        s["matched_bench_total"] = float(matched.iloc[-1] - 1)
        s["alpha_vs_matched"] = float((eq.iloc[-1] - 1) - (matched.iloc[-1] - 1))
        rows.append(s); results[r["label"]] = {"equity": eq, "trades": r["trades"], "stats": s}
    for nm, eq in (("BTC", BTCeq), ("ETH", ETHeq), ("EW universe", EW)):
        s = stats(eq); s["label"] = nm; rows.append(s); results[nm] = {"equity": eq, "trades": [], "stats": s}
    df = pd.DataFrame(rows).set_index("label")
    pd.set_option("display.width", 200); pd.set_option("display.float_format", lambda v: f"{v:,.3f}")
    print(df[["total", "cagr", "vol", "sharpe", "maxdd", "n_trades", "hit", "avg_ret", "med_ret", "avg_days", "exposure", "matched_bench_total", "alpha_vs_matched"]].to_string())
    # per-year regime breakdown
    print("\nBY YEAR (total return):")
    yr = pd.DataFrame({k: v_["equity"] for k, v_ in results.items()}).dropna(how="all")
    yr = yr.groupby(yr.index.year).apply(lambda g: g.iloc[-1] / g.iloc[0] - 1)
    print(yr[[c for c in ["K1.5_N28_slow", "K2.0_N56_slow", "K2.0_N56_hold28", "PRICE breakout control", "BTC", "ETH", "EW universe"] if c in yr.columns]].to_string(float_format=lambda v: f"{v:+.1%}"))
    def es_print(es, tag):
        print(f"\nEVENT STUDY ({tag}) n = {len(es)}")
        for h in (7, 28, 90):
            x = es[f"x{h}"].dropna(); t = x.mean() / (x.std() / math.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else float("nan")
            print(f"  +{h:2d}d  raw mean {es[f'r{h}'].mean():+.1%} median {es[f'r{h}'].median():+.1%} hit {(es[f'r{h}']>0).mean():.0%} | excess vs EW mean {x.mean():+.1%} median {x.median():+.1%} hit {(x>0).mean():.0%} t={t:+.2f}")
    es = event_study(1.5, 28); es_print(es, "K=1.5, N=28")
    es2 = event_study(2.0, 56); es_print(es2, "K=2.0, N=56")
    # persist for the results page
    out = {"start": str(start.date()), "end": str(idx[-1].date()), "n_universe": int(len(PX.columns)),
           "avg_eligible": float(eligible[sl].sum(axis=1).mean()), "cost": COST, "max_pos": MAX_POS,
           "curves": {k: [[str(d.date()), round(float(v), 5)] for d, v in v_["equity"].dropna().items()] for k, v_ in results.items()},
           "stats": {k: {kk: (None if (isinstance(vv, float) and np.isnan(vv)) else vv) for kk, vv in v_["stats"].items()} for k, v_ in results.items()},
           "trades": {k: v_["trades"] for k, v_ in results.items() if v_["trades"]},
           "events": {"K1.5_N28": es.to_dict("records"), "K2.0_N56": es2.to_dict("records")}}
    json.dump(out, open("bt_results.json", "w"))
    print("saved bt_results.json")

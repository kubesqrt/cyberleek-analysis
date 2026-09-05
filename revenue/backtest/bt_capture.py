"""Does revenue that flows to the TOKEN (holders revenue) matter more than protocol revenue?
Variants of the breakout strategy using DeFiLlama dailyHoldersRevenue, plus an event study
splitting breakouts by capture ratio.  Reuses the panel from bt_engine.
"""
import json, os, math
import numpy as np, pandas as pd
import bt_engine as B

idx, PX, REV, rev7, eligible, ret, ew, start = B.idx, B.PX, B.REV, B.rev7, B.eligible, B.ret, B.ew, B.start
sl = slice(start, None); COST = B.COST; MAX_POS = B.MAX_POS

# ---- holders revenue panel, same entity keys as REV ----
def load_hrev(e):
    s = None
    for slug in e["slugs"]:
        f = f"bt_hrev/{slug}.json"
        if not os.path.exists(f): continue
        pts = json.load(open(f))
        if not pts: continue
        ser = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(v or 0) for t, v in pts})
        s = ser if s is None else s.add(ser, fill_value=0)
    return s
hcols = {}
for e in B.U:
    key = e["symbol"] or e["name"]
    if key not in REV.columns: key = key + "_" + e["gecko"]
    if key not in REV.columns: continue
    h = load_hrev(e)
    hcols[key] = h if h is not None else pd.Series(dtype=float)
HREV = pd.DataFrame(hcols).reindex(idx).reindex(columns=REV.columns)
HREV = HREV.where(REV.notna(), np.nan).fillna(0.0)          # zero where protocol reports but no holder revenue
hrev7 = HREV.rolling(7).sum(); hrev30 = HREV.rolling(30).sum(); rev30 = REV.rolling(30).sum()
capture = (hrev30 / rev30.replace(0, np.nan)).clip(upper=1.5)   # trailing-30d share of revenue paid to holders
has_cap = (hrev30 > 0)
print("names with any holders revenue over the sample:", int((HREV.sum() > 0).sum()), "of", len(REV.columns))
print("eligible names now with capture>0:", int((eligible.iloc[-1] & has_cap.iloc[-1]).sum()), "of", int(eligible.iloc[-1].sum()))

def run_variant(K=2.0, N=56, base="rev", elig_extra=None, prio="ratio", size_by_capture=False, label=""):
    """Generic breakout runner. base='rev' or 'hrev' for the series driving entry/exit."""
    S = rev7 if base == "rev" else hrev7
    prior = S.shift(7).rolling(49).mean(); hi = S.rolling(N).max()
    entry = (S >= hi) & (S / prior >= K) & (prior > 0)
    ex = S < S.shift(1).rolling(28).mean()
    elig = eligible if elig_extra is None else (eligible & elig_extra)
    entry = (entry & elig).fillna(False)
    cols = list(PX.columns); T = len(idx)
    entryA = entry.values; exA = ex.fillna(False).values; pxA = PX.values; eligA = elig.fillna(False).values
    ratioA = (S / prior).fillna(0).values; capA = capture.fillna(0).values
    cash = 1.0; pos = {}; equity = np.zeros(T); trades = []; expo = np.zeros(T)
    pend_in, pend_out = [], []
    for t in range(T):
        for c in pend_out:
            if c in pos and not np.isnan(pxA[t, c]):
                p = pos.pop(c); val = p["units"] * pxA[t, c] * (1 - COST); cash += val
                trades.append({"sym": cols[c], "ret": val / p["cost"] - 1, "days": t - p["entry_t"], "cap": p["cap"]})
        for c in pend_in:
            if c not in pos and len(pos) < MAX_POS and not np.isnan(pxA[t, c]):
                mv = cash + sum(pp["units"] * pxA[t, k] for k, pp in pos.items() if not np.isnan(pxA[t, k]))
                mult = (0.5 + min(capA[t - 1, c], 1.0)) if size_by_capture else 1.0
                alloc = min(cash, mult * mv / MAX_POS)
                if alloc <= 0: continue
                pos[c] = {"units": alloc * (1 - COST) / pxA[t, c], "entry_t": t, "cost": alloc, "cap": float(capA[t - 1, c])}
                cash -= alloc
        pend_in, pend_out = [], []
        mv = cash + sum(p["units"] * pxA[t, c] for c, p in pos.items() if not np.isnan(pxA[t, c]))
        equity[t] = mv; expo[t] = (mv - cash) / mv if mv > 0 else 0
        for c in list(pos):
            if exA[t, c] or not eligA[t, c]: pend_out.append(c)
        cands = [c for c in range(len(cols)) if entryA[t, c] and c not in pos and c not in pend_out]
        cands.sort(key=(lambda c: -ratioA[t, c]) if prio == "ratio" else (lambda c: (-capA[t, c], -ratioA[t, c])))
        pend_in = cands[: max(0, MAX_POS - len(pos))]
    eq = pd.Series(equity, idx)[sl]; eq = eq / eq.iloc[0]
    s = B.stats(eq, trades, float(expo[idx >= start].mean()))
    matched = (1 + ew[sl] * pd.Series(expo, idx)[sl].shift(1).fillna(0)).cumprod()
    s["alpha_vs_matched"] = float((eq.iloc[-1] - 1) - (matched.iloc[-1] - 1)); s["label"] = label
    return eq, s, trades

variants = [
    dict(label="BASE: total revenue breakout 2x/8wk (as published)"),
    dict(label="Holders-revenue breakout 2x/8wk (signal on revenue-to-token only)", base="hrev"),
    dict(label="Holders-revenue breakout 1.5x/4wk", base="hrev", K=1.5, N=28),
    dict(label="Total-rev breakout, only tokens with capture > 0", elig_extra=has_cap),
    dict(label="Total-rev breakout, only capture >= 25%", elig_extra=(capture >= 0.25)),
    dict(label="Total-rev breakout, only capture >= 50%", elig_extra=(capture >= 0.50)),
    dict(label="Total-rev breakout, prioritise high-capture names for slots", prio="capture"),
    dict(label="Total-rev breakout, size positions by capture (0.5x-1.5x)", size_by_capture=True),
    dict(label="Total-rev breakout, prioritise + size by capture", prio="capture", size_by_capture=True),
    dict(label="Total-rev breakout, EXCLUDE capture > 0 (no-capture names only)", elig_extra=~has_cap),
]
rows, curves = [], {}
for v in variants:
    eq, s, tr = run_variant(**{k: v[k] for k in v if k != "label"}, label=v["label"])
    rows.append(s); curves[v["label"]] = eq
df = pd.DataFrame(rows).set_index("label")
pd.set_option("display.width", 230); pd.set_option("display.float_format", lambda v: f"{v:,.3f}")
print("\n", df[["total", "cagr", "sharpe", "maxdd", "n_trades", "hit", "avg_ret", "avg_days", "exposure", "alpha_vs_matched"]].to_string())

# ---- event study: breakout forward excess return by capture bucket ----
prior = rev7.shift(7).rolling(49).mean(); hi = rev7.rolling(56).max()
entry = ((rev7 >= hi) & (rev7 / prior >= 2.0) & (prior > 0) & eligible).fillna(False)
e2 = entry & ~entry.shift(1).fillna(False).astype(bool)
fwd = {h: PX.shift(-h - 1) / PX.shift(-1) - 1 for h in (7, 28, 90)}
ewc = (1 + ew).cumprod(); ewf = {h: ewc.shift(-h - 1) / ewc.shift(-1) - 1 for h in (7, 28, 90)}
ev = []
for c in PX.columns:
    for t in idx[e2[c].values]:
        if t < start: continue
        cap = capture.at[t, c]; cap = 0.0 if pd.isna(cap) else float(cap)
        row = {"sym": c, "date": str(t.date()), "cap": cap, "bucket": "0 (none/unreported)" if cap <= 0 else ("0-25%" if cap < 0.25 else ("25-75%" if cap < 0.75 else "75%+"))}
        for h in (7, 28, 90): row[f"x{h}"] = fwd[h].at[t, c] - ewf[h].at[t]
        ev.append(row)
es = pd.DataFrame(ev)
print("\nEVENT STUDY — excess forward return after a 2x/8wk breakout, by capture bucket at entry")
for b in ["0 (none/unreported)", "0-25%", "25-75%", "75%+"]:
    g = es[es.bucket == b]
    if len(g) < 5: continue
    line = f"  {b:22} n={len(g):4d}"
    for h in (7, 28, 90):
        x = g[f"x{h}"].dropna(); t = x.mean() / (x.std() / math.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else float("nan")
        line += f" | +{h}d mean {x.mean():+.1%} med {x.median():+.1%} hit {(x>0).mean():.0%} t={t:+.1f}"
    print(line)
json.dump({"stats": {k: {kk: (None if isinstance(vv, float) and np.isnan(vv) else vv) for kk, vv in r.items()} for k, r in zip(df.index, rows)},
           "curves": {k: [[str(d.date()), round(float(v), 5)] for d, v in c.items()] for k, c in curves.items()},
           "events": es.to_dict("records")}, open("bt_results_capture.json", "w"))
print("saved bt_results_capture.json")

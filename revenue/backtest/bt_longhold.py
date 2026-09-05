"""Long-term revenue-trend holds: rare entries on sustained revenue ramps, hold until a
monthly revenue breakdown.  Tradability gate from CoinGecko volume/mcap history.
Reuses the panel from bt_engine.
"""
import json, os, math
import numpy as np, pandas as pd
import bt_engine as B

idx, PX, REV, eligible, ret, ew, start = B.idx, B.PX, B.REV, B.eligible, B.ret, B.ew, B.start
sl = slice(start, None); COST = B.COST
rev30 = REV.rolling(30).sum()

# ---- volume / mcap panel ----
gecko_of = {}
for e in B.U:
    key = e["symbol"] or e["name"]
    if key not in REV.columns: key = key + "_" + e["gecko"]
    if key in REV.columns: gecko_of[key] = e["gecko"]
def load_series(g, field):
    f = f"bt_vol/{g}.json"
    if not os.path.exists(f): return None
    pts = json.load(open(f)).get(field) or []
    if not pts: return None
    s = pd.Series({pd.Timestamp(int(t / 1000), unit="s").normalize(): float(v) for t, v in pts if v is not None})
    return s[~s.index.duplicated(keep="last")].sort_index()
VOL = pd.DataFrame({c: load_series(g, "volumes") for c, g in gecko_of.items()}).reindex(idx).reindex(columns=REV.columns)
MC = pd.DataFrame({c: load_series(g, "market_caps") for c, g in gecko_of.items()}).reindex(idx).reindex(columns=REV.columns)
VOL = VOL.ffill(limit=5); MC = MC.ffill(limit=5)
vol7 = VOL.rolling(7).mean()
print("volume history for", int(VOL.notna().any().sum()), "of", len(REV.columns), "names; from", VOL.dropna(how="all").index.min().date() if VOL.notna().any().any() else None)
# CoinGecko public history is capped at 365d: before that, fall back to a market-cap proxy
# (today's mcap scaled by price = constant-supply approximation) and assume volume adequate.
mcap_now = json.load(open("bt_mcap_now.json"))
mc_now = pd.Series({c: mcap_now.get(g) for c, g in gecko_of.items()}, dtype="float").reindex(REV.columns)
MC_PROXY = PX.mul(mc_now / PX.ffill().iloc[-1], axis=1)
MC_H = MC.where(MC.notna(), MC_PROXY)

def tradable(min_mcap=10e6, min_vol=500e3):
    vol_ok = (vol7 >= min_vol).where(vol7.notna(), True)     # unknown volume (pre-history) -> rely on mcap
    return (MC_H >= min_mcap) & vol_ok

# ---- entry signals ----
mom = rev30 / rev30.shift(30) - 1
first_cross = (rev30 >= 1e6) & (rev30.shift(1) < 1e6) & (rev30.cummax().shift(1) < 1e6) & (mom > 0.5)   # first ever crossing of $1M/30d while ramping
ramp3 = (rev30 > rev30.shift(30)) & (rev30.shift(30) > rev30.shift(60)) & (rev30.shift(60) > rev30.shift(90)) & (rev30 >= 1e6)
rank = rev30.where(eligible).rank(axis=1, ascending=False)
climber = (rank <= 50) & (rank.shift(60) - rank >= 20)
ENTRIES = {"first $1M crossing while ramping": first_cross, "3 rising months & >=$1M": ramp3, "rank climber (+20 into top 50)": climber,
           "ANY of the three": first_cross | ramp3 | climber}

def run(entry_sig, exit_theta=0.5, exit_mode="peak", max_pos=15, gate=True, label=""):
    """buy & hold until rev30 < (1-theta) x trailing-90d peak (exit_mode='peak') or MoM < -theta (exit_mode='mom')."""
    peak90 = rev30.rolling(90).max()
    ex = (rev30 < (1 - exit_theta) * peak90) if exit_mode == "peak" else (mom < -exit_theta)
    elig = eligible & (tradable() if gate else True)
    ent = (entry_sig & elig).fillna(False)
    cols = list(PX.columns); T = len(idx)
    entA = ent.values; exA = ex.fillna(False).values; pxA = PX.values; eligA = eligible.fillna(False).values
    cash = 1.0; pos = {}; equity = np.zeros(T); expo = np.zeros(T); trades = []; log = []
    pend_in, pend_out = [], []
    for t in range(T):
        for c in pend_out:
            if c in pos and not np.isnan(pxA[t, c]):
                p = pos.pop(c); val = p["units"] * pxA[t, c] * (1 - COST); cash += val
                trades.append({"sym": cols[c], "entry": str(idx[p["t"]].date()), "exit": str(idx[t].date()), "ret": val / p["cost"] - 1, "days": t - p["t"], "why": p["why"]})
        for c, why in pend_in:
            if c not in pos and len(pos) < max_pos and not np.isnan(pxA[t, c]):
                mv = cash + sum(pp["units"] * pxA[t, k] for k, pp in pos.items() if not np.isnan(pxA[t, k]))
                alloc = min(cash, mv / max_pos)
                if alloc <= 0: continue
                pos[c] = {"units": alloc * (1 - COST) / pxA[t, c], "t": t, "cost": alloc, "why": why}; cash -= alloc
                log.append({"sym": cols[c], "date": str(idx[t].date()), "why": why})
        pend_in, pend_out = [], []
        mv = cash + sum(p["units"] * pxA[t, c] for c, p in pos.items() if not np.isnan(pxA[t, c]))
        equity[t] = mv; expo[t] = (mv - cash) / mv if mv > 0 else 0
        for c in list(pos):
            if exA[t, c] or not eligA[t, c]: pend_out.append(c)
        cands = [c for c in range(len(cols)) if entA[t, c] and c not in pos and c not in pend_out]
        pend_in = [(c, label) for c in cands[: max(0, max_pos - len(pos))]]
    eq = pd.Series(equity, idx)[sl]; eq = eq / eq.iloc[0]
    s = B.stats(eq, trades, float(expo[idx >= start].mean())); s["label"] = label
    matched = (1 + ew[sl] * pd.Series(expo, idx)[sl].shift(1).fillna(0)).cumprod()
    s["alpha_vs_matched"] = float((eq.iloc[-1] - 1) - (matched.iloc[-1] - 1))
    openp = [{"sym": cols[c], "entry": str(idx[p["t"]].date()), "unreal": float(pxA[T - 1, c] * p["units"] / p["cost"] - 1), "days": T - 1 - p["t"]} for c, p in pos.items()]
    return eq, s, trades, openp, log

rows, curves, detail = [], {}, {}
grid = []
for en, sig in ENTRIES.items():
    grid.append(dict(entry_sig=sig, label=f"{en} | exit: rev30 < 50% of 90d peak"))
grid += [dict(entry_sig=ENTRIES["ANY of the three"], exit_theta=0.4, label="ANY | exit: rev30 < 60% of 90d peak (tighter)"),
         dict(entry_sig=ENTRIES["ANY of the three"], exit_theta=0.6, label="ANY | exit: rev30 < 40% of 90d peak (looser)"),
         dict(entry_sig=ENTRIES["ANY of the three"], exit_mode="mom", exit_theta=0.3, label="ANY | exit: MoM revenue < -30%"),
         dict(entry_sig=ENTRIES["ANY of the three"], gate=False, label="ANY | no tradability gate (for comparison)")]
for g in grid:
    eq, s, tr, op, lg = run(**g)
    rows.append(s); curves[g["label"]] = eq; detail[g["label"]] = {"trades": tr, "open": op, "log": lg}
df = pd.DataFrame(rows).set_index("label")
pd.set_option("display.width", 230); pd.set_option("display.float_format", lambda v: f"{v:,.3f}")
print("\nLONG-HOLD VARIANTS", start.date(), "->", idx[-1].date())
print(df[["total", "cagr", "sharpe", "maxdd", "n_trades", "hit", "avg_ret", "avg_days", "exposure", "alpha_vs_matched"]].to_string())
for k in ("BTC", "ETH"):
    e = (B.BTCeq if k == "BTC" else B.ETHeq); print(f"{k:8} total {e.iloc[-1]-1:+.1%}")
print(f"EW univ  total {(1+ew[sl]).cumprod().iloc[-1]-1:+.1%}")

best = "ANY of the three | exit: rev30 < 50% of 90d peak"
d = detail[best]
print(f"\n== {best} ==")
print("entries (chronological):")
for l in d["log"]: print(f"  {l['date']}  {l['sym']}")
print("closed trades:")
for t in sorted(d["trades"], key=lambda x: x["entry"]): print(f"  {t['sym']:10} {t['entry']} -> {t['exit']}  {t['ret']:+.1%}  {t['days']}d")
print("open now:")
for o in sorted(d["open"], key=lambda x: -x["unreal"]): print(f"  {o['sym']:10} since {o['entry']}  {o['unreal']:+.1%}  {o['days']}d")

# when would each signal have first fired for the big winners?
print("\nFirst signal date for notable names (any entry rule, with tradability gate):")
sig = (ENTRIES["ANY of the three"] & eligible & tradable()).fillna(False)
for nm in ["HYPE", "LIT", "PONS", "PUMP", "SKY", "AERO", "EDGE", "MET", "JUP", "CAKE"]:
    if nm in sig.columns:
        f = sig[nm][sig[nm]].index
        if len(f):
            t0 = f[0]; p0 = PX.at[t0, nm]; pn = PX[nm].dropna().iloc[-1]
            print(f"  {nm:6} first signal {t0.date()}  price then {p0:.4g} -> now {pn:.4g} ({pn/p0-1:+.0%}); revenue30d then ${rev30.at[t0, nm]/1e6:.1f}M")
        else: print(f"  {nm:6} never signalled (gate/eligibility)")
    else: print(f"  {nm:6} not in panel")
json.dump({"stats": {r["label"]: {k: (None if isinstance(v, float) and np.isnan(v) else v) for k, v in r.items()} for r in rows},
           "curves": {k: [[str(d_.date()), round(float(v), 5)] for d_, v in c.items()] for k, c in curves.items()},
           "detail": detail}, open("bt_results_longhold.json", "w"), default=str)
print("saved bt_results_longhold.json")

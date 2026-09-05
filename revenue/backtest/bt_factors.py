"""Cross-sectional revenue strategies (weekly-rebalanced rank portfolios) + event studies.
Reuses the panel built in bt_engine (REV, PX, rev7, rev30, eligible, ret, ew, start, idx).
"""
import json, math
import numpy as np, pandas as pd
import bt_engine as B

COST = B.COST
REB = 7            # rebalance every 7 days
TOPQ = 0.2         # long top quintile
idx, PX, REV, rev7, rev30, eligible, ret, ew, start = B.idx, B.PX, B.REV, B.rev7, B.rev30, B.eligible, B.ret, B.ew, B.start
sl = slice(start, None)

mcap_now = json.load(open("bt_mcap_now.json"))
gecko_of = {}
for e in B.U:
    key = e["symbol"] or e["name"]
    gecko_of[key] = e["gecko"]; gecko_of[key + "_" + e["gecko"]] = e["gecko"]
last_px = PX.ffill().iloc[-1]
mc_now = pd.Series({c: mcap_now.get(gecko_of.get(c)) for c in PX.columns}, dtype="float")
MCAP = PX.mul(mc_now / last_px, axis=1)          # historical mcap ≈ today's mcap scaled by price (constant-supply approx)

# ---------- factor scores (computed on day t, traded at t+1 close) ----------
rev_mom = rev30 / rev30.shift(30) - 1
g1 = rev7 / rev7.shift(7) - 1; g0 = rev7.shift(7) / rev7.shift(14) - 1
rev_accel = g1 - g0
rev_yield = (rev30 * (365 / 30)) / MCAP
px_mom30 = PX / PX.shift(30) - 1
def xrank(df):  # cross-sectional percentile rank among eligible names, per day
    return df.where(eligible).rank(axis=1, pct=True)
value_growth = (xrank(rev_mom) + xrank(rev_yield)) / 2
divergence = xrank(rev_mom) - xrank(px_mom30)

FACTORS = {
    "Revenue momentum (30d MoM, top quintile)": rev_mom,
    "Revenue acceleration (top quintile)": rev_accel,
    "Revenue yield / value (cheapest quintile)": rev_yield,
    "Value + growth combo (top quintile)": value_growth,
    "Divergence: revenue up, price lagging (top quintile)": divergence,
    "Price momentum control (30d, top quintile)": px_mom30,
}

def rank_portfolio(score, top=TOPQ, bottom=False, min_names=5):
    """weekly-rebalanced equal-weight portfolio of the top (or bottom) fraction by score."""
    T = len(idx); cols = PX.columns
    w = pd.Series(0.0, index=cols); eq = np.ones(T); expo = np.zeros(T); turn = 0.0
    sc = score.where(eligible)
    retA = ret.fillna(0)
    for t in range(1, T):
        r = float((w * retA.iloc[t]).sum())
        eq[t] = eq[t - 1] * (1 + r)
        if w.sum() > 0:  # drift weights with returns
            w = w * (1 + retA.iloc[t]); w = w / w.sum() * min(1.0, w.sum()) if w.sum() > 0 else w
        if (t - 1) % REB == 0 and idx[t] >= start:
            s = sc.iloc[t - 1].dropna()          # yesterday's scores -> trade today
            if len(s) >= min_names:
                k = max(min_names, int(round(len(s) * top)))
                pick = (s.nsmallest(k) if bottom else s.nlargest(k)).index
                new = pd.Series(0.0, index=cols); new[pick] = 1.0 / k
                tc = COST * float((new - w).abs().sum())
                eq[t] *= (1 - tc); turn += float((new - w).abs().sum())
                w = new
        expo[t] = float(w.sum())
    return pd.Series(eq, idx), float(expo[idx >= start].mean()), turn

results = {}
rows = []
for name, sc in FACTORS.items():
    eqs, expo, turn = rank_portfolio(sc)
    eqs = eqs[sl]; eqs = eqs / eqs.iloc[0]
    s = B.stats(eqs); s["exposure"] = expo; s["turnover_total"] = turn
    s["alpha_vs_EW"] = float(eqs.iloc[-1] - (1 + ew[sl]).cumprod().iloc[-1])
    s["label"] = name; rows.append(s); results[name] = {"equity": eqs, "stats": s}
# long/short spread on revenue momentum (top quintile minus bottom quintile, informational)
top_eq, _, _ = rank_portfolio(rev_mom); bot_eq, _, _ = rank_portfolio(rev_mom, bottom=True)
spread = (1 + (top_eq.pct_change().fillna(0) - bot_eq.pct_change().fillna(0)))[sl].cumprod()
s = B.stats(spread); s["label"] = "L/S spread: top − bottom revenue-momentum quintile"; s["exposure"] = None; s["alpha_vs_EW"] = None
rows.append(s); results[s["label"]] = {"equity": spread, "stats": s}
# bottom quintile revenue momentum (what happens to revenue losers)
s = B.stats(bot_eq[sl] / bot_eq[sl].iloc[0]); s["label"] = "Bottom revenue-momentum quintile (avoid list)"; s["exposure"] = None
s["alpha_vs_EW"] = float((bot_eq[sl] / bot_eq[sl].iloc[0]).iloc[-1] - (1 + ew[sl]).cumprod().iloc[-1]); rows.append(s)
results[s["label"]] = {"equity": bot_eq[sl] / bot_eq[sl].iloc[0], "stats": s}
for nm, eq in (("EW universe", (1 + ew[sl]).cumprod()), ("BTC", B.BTCeq)):
    s = B.stats(eq); s["label"] = nm; s["exposure"] = None; s["alpha_vs_EW"] = None; rows.append(s); results[nm] = {"equity": eq, "stats": s}

df = pd.DataFrame(rows).set_index("label")
pd.set_option("display.width", 220); pd.set_option("display.float_format", lambda v: f"{v:,.3f}")
print("FACTOR PORTFOLIOS", start.date(), "->", idx[-1].date())
print(df[["total", "cagr", "vol", "sharpe", "maxdd", "exposure", "alpha_vs_EW"]].to_string())

# ---------- event studies: fade (sell signal) and divergence (buy signal) ----------
def ev_study(sig, tag):
    e2 = (sig & eligible) & ~(sig & eligible).shift(1).fillna(False).astype(bool)
    fwd = {h: PX.shift(-h - 1) / PX.shift(-1) - 1 for h in (7, 28, 90)}
    ewc = (1 + ew).cumprod(); ewf = {h: ewc.shift(-h - 1) / ewc.shift(-1) - 1 for h in (7, 28, 90)}
    out = []
    for c in PX.columns:
        for t in idx[e2[c].fillna(False).values]:
            if t < start: continue
            row = {"sym": c, "date": str(t.date())}
            for h in (7, 28, 90):
                row[f"r{h}"] = fwd[h].at[t, c]; row[f"x{h}"] = fwd[h].at[t, c] - ewf[h].at[t]
            out.append(row)
    es = pd.DataFrame(out)
    print(f"\nEVENT STUDY — {tag}: n = {len(es)}")
    for h in (7, 28, 90):
        x = es[f"x{h}"].dropna(); r = es[f"r{h}"].dropna()
        t = x.mean() / (x.std() / math.sqrt(len(x))) if len(x) > 2 and x.std() > 0 else float("nan")
        print(f"  +{h:2d}d raw mean {r.mean():+.1%} med {r.median():+.1%} hit {(r>0).mean():.0%} | excess mean {x.mean():+.1%} med {x.median():+.1%} hit {(x>0).mean():.0%} t={t:+.2f}")
    return es

prior8 = rev7.shift(7).rolling(49).mean()
fade = (rev7 < 0.5 * prior8) & (rev7 <= rev7.rolling(28).min()) & (prior8 > 0)
es_fade = ev_study(fade, "revenue FADE (rev7d < 0.5× 8-wk avg, 4-wk low) — is it a sell signal?")
diverg = (px_mom30 < -0.20) & (rev_mom > 0)
es_div = ev_study(diverg, "DIVERGENCE (price −20%+ in 30d while revenue MoM > 0)")
accel_sig = (g1 > 0.25) & (g0 <= 0)
es_acc = ev_study(accel_sig, "ACCELERATION turn (WoW > +25% after a flat/down week)")

out = {"start": str(start.date()), "end": str(idx[-1].date()), "rebalance_days": REB, "top_fraction": TOPQ,
       "curves": {k: [[str(d.date()), round(float(v), 5)] for d, v in v_["equity"].dropna().items()] for k, v_ in results.items()},
       "stats": {k: {kk: (None if (isinstance(vv, float) and np.isnan(vv)) else vv) for kk, vv in v_["stats"].items()} for k, v_ in results.items()},
       "events": {"fade": es_fade.to_dict("records"), "divergence": es_div.to_dict("records"), "acceleration": es_acc.to_dict("records")}}
json.dump(out, open("bt_results2.json", "w"))
print("saved bt_results2.json")

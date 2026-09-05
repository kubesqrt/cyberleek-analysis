"""Long-term book: ranked candidates, target weights, holdings, drift, rebalancing suggestions and a monthly review.

Selection follows the 12-month factor test: rank on market cap, low volatility, absolute revenue, holders' APY and revenue
trend; ignore cheapness and short-term growth. Hard vetoes first (history, structural revenue decline, unlock overhang,
priced-for-perfection, no fee switch). Weights: inverse volatility capped at BOOK_CAP, or equal. Rebalance quarterly or on drift."""
import json, math, datetime as dt
import numpy as np, pandas as pd
from . import config as C, data as D, monitors as MO, safety as SF

BOOK_SIZE = int(__import__("os").environ.get("BOOK_SIZE", 12)); BOOK_CAP = float(__import__("os").environ.get("BOOK_CAP", 0.15))
DRIFT_TOL = 0.30            # rebalance a name when its weight is 30% (relative) away from target
REBALANCE_DAYS = 90         # otherwise quarterly
MIN_REV30_BOOK = 500_000; MIN_MONTHS = 9; MIN_SHARE_OK = 0.8; FDV_MAX = 3.0; PS_FDV_MAX = 60.0; PEAK_FRAC = 0.30

def holders_rev30(entity):
    """30-day revenue that DeFiLlama attributes to the token (buybacks, fee switch, distributions)."""
    tot = 0.0
    for slug in entity["slugs"]:
        try: s = D.llama_summary(slug, "dailyHoldersRevenue")
        except Exception: s = None
        if s and s["chart"]: tot += sum(float(v or 0) for _, v in s["chart"][-30:])
    return tot

def metrics(panel, c, t, entity, market, hrev30=None):
    rev30 = float(panel.rev30.at[t, c]); r90 = panel.rev30[c][t - pd.Timedelta(days=90): t]; peak12 = float(panel.rev30[c][t - pd.Timedelta(days=365): t].max())
    px = panel.PX[c].ffill(); vol60 = float(px.pct_change().iloc[-60:].std() * math.sqrt(365)) if px.notna().sum() > 30 else float("nan")
    months = panel.rev30[c][t - pd.Timedelta(days=365): t].resample("ME").last(); months_ok = float((months >= C.MIN_REV30).mean()) if len(months) else 0.0
    q = [float(panel.REV[c][t - pd.Timedelta(days=90 * (k + 1)) + pd.Timedelta(days=1): t - pd.Timedelta(days=90 * k)].sum()) for k in range(4)][::-1]
    mcap = market.get("mcap"); fdv = market.get("fdv"); ann = rev30 * 365 / 30
    m = {"sym": c, "name": entity["name"], "gecko": entity["gecko"], "category": entity.get("category"), "rev30": rev30, "rev_quarters": q, "vs90": (rev30 / float(r90.mean())) if len(r90) and float(r90.mean()) > 0 else None,
         "peak12": peak12, "vs_peak12": (rev30 / peak12) if peak12 > 0 else None, "hist": int(panel.hist.at[t, c]), "months_ok": months_ok, "mcap": mcap, "fdv": fdv, "fdv_mcap": (fdv / mcap) if fdv and mcap else None,
         "ps_mcap": (mcap / ann) if mcap and ann > 0 else None, "ps_fdv": (fdv / ann) if fdv and ann > 0 else None, "vol60": vol60, "vol24h": market.get("vol24h"), "price": float(px.iloc[-1]),
         "hrev30": hrev30, "capture": (hrev30 / rev30) if hrev30 is not None and rev30 > 0 else None, "holders_apy": (hrev30 * 365 / 30 / mcap) if hrev30 is not None and mcap else None,
         "px_12m": float(px.iloc[-1] / px.iloc[-365] - 1) if px.notna().sum() > 365 and px.iloc[-365] > 0 else None, "dd_12m": float((px.iloc[-365:] / px.iloc[-365:].cummax() - 1).min())}
    m["liquid"] = bool(m["vol24h"] and m["vol24h"] >= C.MIN_VOL30 and mcap and mcap >= C.MIN_MCAP)
    return m

def vetoes(m):
    f = []
    if not m["liquid"]: f.append("illiquid")
    if m["rev30"] < MIN_REV30_BOOK: f.append(f"revenue under ${MIN_REV30_BOOK/1e3:,.0f}k/month")
    if m["hist"] < 30 * MIN_MONTHS or m["months_ok"] < MIN_SHARE_OK: f.append(f"history: needs {MIN_MONTHS} months with {MIN_SHARE_OK:.0%} above $100k")
    if m["vs90"] is not None and m["vs90"] < 0.8: f.append(f"revenue {m['vs90']:.0%} of its 90-day average")
    if m["vs_peak12"] is not None and m["vs_peak12"] < PEAK_FRAC: f.append(f"revenue {m['vs_peak12']:.0%} of its 12-month peak")
    if m["fdv_mcap"] and m["fdv_mcap"] > FDV_MAX: f.append(f"FDV {m['fdv_mcap']:.1f}x market cap (unlock overhang)")
    if m["ps_fdv"] and m["ps_fdv"] > PS_FDV_MAX: f.append(f"P/S on FDV {m['ps_fdv']:.0f}x (priced for perfection)")
    q = m.get("rev_quarters") or []
    if len(q) >= 3 and max(q) > 0 and q[-1] < 0.4 * max(q): f.append(f"structural decline: last quarter {q[-1]/max(q):.0%} of its best of the last 4")
    if m["capture"] is not None and m["capture"] <= 0: f.append("token receives none of the revenue (no fee switch)")
    return f

STRUCTURAL = ("structural decline", "revenue 0", "token receives none", "illiquid", "revenue under")
def is_structural(v): return any(v.startswith(p) or p in v for p in STRUCTURAL) or ("of its 12-month peak" in v)

def build_book(panel, universe, n=BOOK_SIZE, weighting="invvol", cap=BOOK_CAP, log=print, t=None, hrev_lookup=None):
    """t: as-of date (default last complete day). hrev_lookup(entity, t) -> 30d holders revenue, for replays; default fetches live."""
    t = t or panel.asof(); rows = []
    ents = {e["gecko"]: e for e in universe}
    for c in panel.REV.columns:
        e = ents.get(panel.meta[c]["gecko"]); mk = panel.market(c)
        if not e or not mk.get("mcap"): continue
        if float(panel.rev30.at[t, c]) < MIN_REV30_BOOK or not (mk.get("vol24h") and mk["vol24h"] >= C.MIN_VOL30 / 2): continue
        m = metrics(panel, c, t, e, mk); rows.append(m)
    log(f"  holders revenue for {len(rows)} candidates…")
    for m in rows:
        h = hrev_lookup(ents[m["gecko"]], t) if hrev_lookup else holders_rev30(ents[m["gecko"]]); m["hrev30"] = h; m["capture"] = (h / m["rev30"]) if m["rev30"] > 0 else None; m["holders_apy"] = (h * 365 / 30 / m["mcap"]) if m["mcap"] else None
        m["vetoes"] = vetoes(m)
    df = pd.DataFrame(rows)
    if df.empty: return []
    rk = lambda s: s.rank(pct=True)
    qtrend = df.rev_quarters.map(lambda q: (q[-1] / (sum(q[:-1]) / max(1, len(q) - 1))) if len(q) >= 2 and sum(q[:-1]) > 0 else 1.0)
    df["quality"] = (rk(np.log(df.mcap.clip(lower=1))) + rk(-df.vol60.fillna(df.vol60.max())) + rk(np.log(df.rev30.clip(lower=1))) + rk(df.holders_apy.fillna(0)) + rk(df.vs90.fillna(1)) + rk(-df.fdv_mcap.fillna(1)) + rk(qtrend)) / 7
    df = df.sort_values("quality", ascending=False)
    ok = df[df.vetoes.map(len) == 0].head(n).copy()
    if len(ok): cap = max(cap, 1.0 / len(ok))
    if len(ok):
        if weighting == "equal": w = pd.Series(1 / len(ok), index=ok.index)
        else:
            raw = 1 / ok.vol60.fillna(ok.vol60.max()).clip(lower=0.2); w = raw / raw.sum()
            for _ in range(10):
                over = w > cap
                if not over.any(): break
                ex = (w[over] - cap).sum(); w[over] = cap; rest = ~over
                if w[rest].sum() > 0: w[rest] += ex * w[rest] / w[rest].sum()
        ok["weight"] = w
    book = ok.to_dict("records"); near = df[df.vetoes.map(len) == 1].head(10).to_dict("records")
    for r in book + near: r["rank"] = int(df.index.get_loc(df.index[df.sym == r["sym"]][0]) + 1) if False else None
    ranking = df[["sym", "quality"]].reset_index(drop=True); ranking["rank"] = ranking.index + 1; rankmap = dict(zip(ranking.sym, ranking["rank"]))
    for r in book + near: r["rank"] = rankmap.get(r["sym"])
    cands = {r["sym"]: {**r, "rank": rankmap.get(r["sym"])} for r in df.to_dict("records")}
    return {"asof": str(t.date()), "book": book, "near_misses": near, "n_candidates": len(df), "weighting": weighting, "cap": cap, "candidates": cands}

# ---------------- holdings
def holdings(panel=None):
    hs = [p for p in MO.positions("open") if p["kind"] in ("hold", "buy", "paper")]
    for h in hs:
        px = None
        if panel is not None and h["sym"] in panel.PX.columns: px = float(panel.PX[h["sym"]].ffill().iloc[-1])
        h["price"] = px; h["value"] = (h["size_usd"] * (px / h["entry_px"]) if px and h["entry_px"] else h["size_usd"]) or 0.0
    return hs

def sync_wallet(universe, wallet=None):
    """Read ERC-20 balances of every universe token on the EVM chains we know; returns {sym: (chain, address, units, usd)}."""
    from web3 import Web3
    wallet = wallet or C.WALLET_ADDRESS; out = {}
    from . import universe as UV
    mk = D.cg_markets([e["gecko"] for e in universe])
    for e in universe:
        contracts, _ = UV.contracts(e["gecko"])
        for chain, addr in contracts.items():
            cid = C.CHAIN_IDS.get(chain)
            if not isinstance(cid, int) or cid not in C.RPC_URLS: continue
            try:
                w3 = Web3(Web3.HTTPProvider(C.RPC_URLS[cid], request_kwargs={"timeout": 20})); tok = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=SF.__dict__.get("ERC20_ABI") or __import__("bot.execute", fromlist=["ERC20_ABI"]).ERC20_ABI)
                bal = tok.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
                if bal > 0:
                    dec = 18
                    try: dec = tok.functions.decimals().call()
                    except Exception: pass
                    units = bal / 10 ** dec; px = (mk.get(e["gecko"]) or {}).get("price") or 0
                    out[e["symbol"]] = (chain, addr, units, units * px)
            except Exception: continue
    return out

def rebalance(book, hs, cash=0.0, tol=DRIFT_TOL, last_rebalance=None):
    """Compare holdings with the target book and return suggested trades with reasons."""
    targets = {b["sym"]: b for b in book["book"]}; value = sum(h["value"] for h in hs) + cash
    cur = {}
    for h in hs: cur[h["sym"]] = cur.get(h["sym"], 0.0) + h["value"]
    trades = []; due = (last_rebalance is None) or ((dt.date.today() - dt.date.fromisoformat(last_rebalance)).days >= REBALANCE_DAYS)
    for sym, v in cur.items():
        w = v / value if value else 0
        if sym not in targets:
            m = (book.get("candidates") or {}).get(sym); vet = (m or {}).get("vetoes") or []
            structural = [x for x in vet if is_structural(x)]
            if m is None: trades.append({"action": "HOLD", "sym": sym, "usd": 0.0, "from_w": w, "to_w": w, "why": "not in the revenue universe (no DeFiLlama revenue or under $500k/month): review by hand", "urgent": False})
            elif structural: trades.append({"action": "SELL", "sym": sym, "usd": v, "from_w": w, "to_w": 0.0, "why": "fails: " + "; ".join(structural), "urgent": True})
            elif vet: trades.append({"action": "HOLD", "sym": sym, "usd": 0.0, "from_w": w, "to_w": w, "why": "keep, but the book would not add it: " + "; ".join(vet), "urgent": False})
            else: trades.append({"action": "HOLD", "sym": sym, "usd": 0.0, "from_w": w, "to_w": w, "why": f"passes the vetoes, ranked #{m.get('rank') or '?'} below the book; keep, do not add", "urgent": False})
        else:
            tw = targets[sym]["weight"]
            if value and abs(w - tw) / tw > tol and (due or abs(w - tw) / tw > 2 * tol):
                trades.append({"action": "TRIM" if w > tw else "ADD", "sym": sym, "usd": abs(w - tw) * value, "from_w": w, "to_w": tw, "why": f"drift {w:.1%} vs target {tw:.1%}", "urgent": False})
    for sym, b in targets.items():
        if sym not in cur and (due or not cur): trades.append({"action": "BUY", "sym": sym, "usd": b["weight"] * value, "from_w": 0.0, "to_w": b["weight"], "why": f"rank #{b['rank']} quality {b['quality']:.2f}, target {b['weight']:.1%}", "urgent": False})
    order = {"SELL": 0, "TRIM": 1, "BUY": 2, "ADD": 3, "HOLD": 4}; trades.sort(key=lambda x: (not x["urgent"], order[x["action"]], -x["usd"]))
    return {"value": value, "cash": cash, "due": due, "last_rebalance": last_rebalance, "trades": trades, "next_review": (dt.date.fromisoformat(last_rebalance) + dt.timedelta(days=REBALANCE_DAYS)).isoformat() if last_rebalance else None}

def review(book, hs, panel, universe):
    """Monthly review: each holding against the long-hold rules."""
    ents = {e["gecko"]: e for e in universe}; t = panel.asof(); out = []
    rankmap = {b["sym"]: b for b in book["book"]}; nearmap = {b["sym"]: b for b in book["near_misses"]}
    for h in hs:
        c = h["sym"]
        if c not in panel.REV.columns: out.append({"sym": c, "verdict": "UNKNOWN", "why": ["not in revenue universe any more"], "m": None}); continue
        e = ents.get(panel.meta[c]["gecko"]); m = metrics(panel, c, t, e, panel.market(c), holders_rev30(e) if e else None); v = vetoes(m)
        prev = float(panel.rev30[c].iloc[-31]) if len(panel.rev30) > 31 else None
        two_months = m["vs_peak12"] is not None and m["vs_peak12"] < PEAK_FRAC and prev is not None and m["peak12"] > 0 and prev < PEAK_FRAC * m["peak12"]
        structural = [x for x in v if is_structural(x)]
        if two_months: verdict, why = "SELL", [f"revenue below {PEAK_FRAC:.0%} of its 12-month peak for two consecutive months"]
        elif m["capture"] is not None and m["capture"] <= 0 and (h.get("thesis") and "fee switch reversed" in h["thesis"]): verdict, why = "SELL", ["fee switch appears off"]
        elif structural: verdict, why = "SELL", structural
        elif v: verdict, why = "HOLD", ["keep, do not add: " + "; ".join(v)] + ([f"warning: revenue at {m['vs_peak12']:.0%} of its 12-month peak"] if m["vs_peak12"] is not None and m["vs_peak12"] < 0.5 else [])
        elif c in rankmap: verdict, why = "KEEP", [f"rank #{rankmap[c]['rank']}, target {rankmap[c]['weight']:.1%}"]
        else: verdict, why = "HOLD", ["passes the vetoes but ranks below the book; do not add"]
        out.append({"sym": c, "verdict": verdict, "why": why, "m": m, "pnl": (h["value"] / h["size_usd"] - 1) if h.get("size_usd") else None})
    return out

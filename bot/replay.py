"""Replay the bot day by day over a window using its own scan / book / review logic, with historical market proxies
(mcap and FDV scaled by price; 30d volume from CoinGecko history; holders revenue from DeFiLlama history).
Usage: python -m bot.replay [START END] [--paper 10000]. Writes replay.json into BOT_DATA_DIR and prints the event log."""
import os, sys, json, re, math, datetime as dt
import numpy as np, pandas as pd
from bot import config as C, data as D, universe as UV, signals as SG, portfolio as PF, report as RP, thesis as TH
SCR = os.environ.get("REPLAY_CACHE_DIR", C.DATA_DIR)   # optional bt_vol/ and bt_hrev/ caches; otherwise fetched
strip = lambda s: re.sub(r"<[^>]+>", "", s).replace("&gt;", ">").replace("&lt;", "<").replace("&#x27;", "'").replace("&amp;", "&")
log = lambda *a: print(*a, file=sys.stderr, flush=True)
U = UV.build(); log(f"universe {len(U)}")
panel = SG.load_panel(U, log=log)
mk_now = D.cg_markets([e["gecko"] for e in U])
# historical proxies
def load_series(path, key):
    if not os.path.exists(path): return None
    d = json.load(open(path)); pts = d.get(key) if isinstance(d, dict) else d
    if not pts: return None
    s = pd.Series({pd.Timestamp(int(t) // (1000 if int(t) > 1e11 else 1), unit="s").normalize(): float(v) for t, v in pts if v is not None}); return s[~s.index.duplicated(keep="last")].sort_index()
VOL = {}; HREV = {}
for c in panel.REV.columns:
    g = panel.meta[c]["gecko"]; v = load_series(f"{SCR}/bt_vol/{g}.json", "volumes")
    if v is None:
        try: pts = D.cg_volume_history(g, 365); v = pd.Series({pd.Timestamp(t, unit="s").normalize(): x for t, x in pts}).sort_index() if pts else None
        except Exception as ex: log(f"  volume {g}: {ex}"); v = None
    if v is not None: VOL[c] = v[~v.index.duplicated(keep="last")].reindex(panel.idx).rolling(30, min_periods=5).mean()
    h = None
    for slug in panel.meta[c]["slugs"]:
        p = f"{SCR}/bt_hrev/{slug}.json"; pts = json.load(open(p)) if os.path.exists(p) else ((D.llama_summary(slug, "dailyHoldersRevenue") or {}).get("chart") or [])
        if pts:
            ser = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(x or 0) for t, x in pts}); h = ser if h is None else h.add(ser, fill_value=0)
    if h is not None: HREV[c] = h.reindex(panel.idx).fillna(0).rolling(30, min_periods=7).sum()
PXf = panel.PX.ffill(); last = PXf.iloc[-1]
def markets_at(t):
    m = {}
    for c in panel.REV.columns:
        g = panel.meta[c]["gecko"]; now = mk_now.get(g) or {}; px = PXf.at[t, c]
        if not now.get("mcap") or px != px or last[c] != last[c] or last[c] <= 0: continue
        r = px / last[c]; vol = float(VOL[c].at[t]) if c in VOL and VOL[c].at[t] == VOL[c].at[t] else now.get("vol24h")
        m[g] = {"price": float(px), "mcap": now["mcap"] * r, "fdv": (now.get("fdv") or 0) * r or None, "vol24h": vol}
    return m
ents = {e["gecko"]: e for e in U}
def hrev_lookup(entity, t):
    c = next((k for k in panel.REV.columns if panel.meta[k]["gecko"] == entity["gecko"]), None)
    return float(HREV[c].at[t]) if c in HREV and HREV[c].at[t] == HREV[c].at[t] else 0.0
panel.attach_markets(mk_now)   # P/S history uses current supply scaled by price; fine for the own-median filter
args = [a for a in sys.argv[1:] if not a.startswith("--")]
T0 = pd.Timestamp(args[0]) if args else panel.asof() - pd.Timedelta(days=92); T1 = pd.Timestamp(args[1]) if len(args) > 1 else panel.asof()
PAPER = float(sys.argv[sys.argv.index("--paper") + 1]) if "--paper" in sys.argv else 10_000.0
days = [d for d in panel.idx if T0 <= d <= T1]
events = []; seen = {}; book_prev = None; feed = []; BOOKS = {}
port = {"cash": PAPER, "units": {}, "entries": {}, "flows": {}}; values = []
def port_value(t): return port["cash"] + sum(u * PXf.at[t, c] for c, u in port["units"].items() if PXf.at[t, c] == PXf.at[t, c])
def rebalance_to(book, t, why):
    tot = port_value(t); tgt = {b["sym"]: b["weight"] for b in book["book"]}; trades = []
    for c in list(port["units"]):
        if c not in tgt: v = port["units"][c] * PXf.at[t, c]; trades.append(("SELL", c, v)); port["cash"] += port["units"].pop(c) * PXf.at[t, c] * 0.995; port["flows"][c] = port["flows"].get(c, 0) + v * 0.995
    for c, w in tgt.items():
        cur = port["units"].get(c, 0) * PXf.at[t, c]; d = w * tot - cur
        if abs(d) > 0.02 * tot:
            port["units"][c] = port["units"].get(c, 0) + d * 0.995 / PXf.at[t, c]; port["cash"] -= d; trades.append(("BUY" if d > 0 else "TRIM", c, abs(d))); port["flows"][c] = port["flows"].get(c, 0) - d
            if c not in port["entries"] or port["units"][c] <= 1e-12: port["entries"][c] = (t, PXf.at[t, c])
    events.append((t, "rebalance", f"⚖️ {why}: " + ", ".join(f"{a} {c} ${usd:,.0f}" for a, c, usd in trades)))
last_reb = None
for i, t in enumerate(days):
    panel.markets = markets_at(t)
    sigs = panel.scan(t)
    for s in sigs:
        if s["verdict"] in ("TRADE", "TRADE (beta)", "EARLY"):
            if s["sym"] in seen and (t - seen[s["sym"]]).days < 14: continue
            seen[s["sym"]] = t; events.append((t, "feed", strip(RP.alert_card(s)))); feed.append(s)
    # book: weekly (Thursdays) to keep it readable, plus first and last day
    if i == 0 or t.dayofweek == 3 or t == days[-1]:
        book = PF.build_book(panel, U, log=lambda *a: None, t=t, hrev_lookup=hrev_lookup); BOOKS[t] = book
        cur = [b["sym"] for b in book["book"]]
        if book_prev is None: events.append((t, "book", strip(RP.book_view(book))))
        elif cur != book_prev:
            a, b_ = set(book_prev), set(cur); events.append((t, "book", "📚 Book changed: " + (f"in {', '.join(sorted(b_ - a))}" if b_ - a else "") + (f" · out {', '.join(sorted(a - b_))}" if a - b_ else "") + " (targets shown at next rebalance)"))
        book_prev = cur
        if i == 0: rebalance_to(book, t, f"initial book, ${PAPER:,.0f} paper"); last_reb = t
        # structural sells in holdings -> act next rebalance check
        hs = [{"sym": c, "value": u * PXf.at[t, c], "size_usd": port["entries"][c][1] * u, "entry_px": port["entries"][c][1], "entry_date": str(port["entries"][c][0].date()), "kind": "hold", "id": k, "thesis": ""} for k, (c, u) in enumerate(port["units"].items())]
        rb = PF.rebalance(book, hs, port["cash"], last_rebalance=str(last_reb.date()))
        urgent = [x for x in rb["trades"] if x["action"] == "SELL"]
        if urgent and i > 0:
            for x in urgent:
                c = x["sym"]; v = port["units"][c] * PXf.at[t, c] * 0.995; port["cash"] += v; port["units"].pop(c); port["flows"][c] = port["flows"].get(c, 0) + v; events.append((t, "monitor", f"🔴 SELL {c} — {x['why']} → sold ${v:,.0f} at {PXf.at[t, c]:.4g}"))
        if i > 0 and (t - last_reb).days >= 90: rebalance_to(book, t, "quarterly rebalance"); last_reb = t
        if t.day <= 7 and t.dayofweek == 3 and i > 0 or t == days[-1]:
            rv = PF.review(book, hs, panel, U); events.append((t, "review", strip(RP.review_view(rv))))
    values.append((t, port_value(t)))
# performance of feed alerts
END = days[-1]; rows = []
for s in feed:
    c = s["sym"]; t = pd.Timestamp(s["date"]); f = t + pd.Timedelta(days=1)
    if f > END or PXf.at[f, c] != PXf.at[f, c]: continue
    px0 = PXf.at[f, c]; path = PXf[c][f:END]; peak = px0; ex = None
    for d, p in path.items():
        peak = max(peak, p)
        if s["rule"] != "early_watch" and s["young"] is False and panel.slow_exit.at[d, c] or p < peak * (1 - s["stop"]): ex = (d, p, "stop" if p < peak * (1 - s["stop"]) else "rev slowed"); break
    rows.append({"sym": c, "date": s["date"], "verdict": s["verdict"], "rule": s["rule"], "fill": px0, "now": path.iloc[-1] / px0 - 1, "peak": path.max() / px0 - 1, "exit": ex[0].date() if ex else None, "trade": (ex[1] / px0 - 1) if ex else path.iloc[-1] / px0 - 1, "why": ex[2] if ex else "open", "liquid": s["liquid"]})
FEED = pd.DataFrame(rows)
V = pd.Series(dict(values)); H = D.llama_prices("hyperliquid"); H = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): p for t, p in H}).reindex(panel.idx).ffill()
B = D.llama_prices("bitcoin"); B = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): p for t, p in B}).reindex(panel.idx).ffill()
liq = pd.DataFrame({c: (VOL[c] >= C.MIN_VOL30) if c in VOL else pd.Series(False, index=panel.idx) for c in panel.REV.columns})
ew = panel.PX.pct_change().where((panel.elig & liq).shift(1)).mean(axis=1).fillna(0); EW = (1 + ew).cumprod()
perf = {"book": V.iloc[-1] / V.iloc[0] - 1, "book_dd": float((V / V.cummax() - 1).min()), "HYPE": H[END] / H[T0] - 1, "BTC": B[END] / B[T0] - 1, "EW_liquid": EW[END] / EW[T0] - 1, "HYPE_px": (float(H[T0]), float(H[END])), "BTC_px": (float(B[T0]), float(B[END]))}
attr = {c: port["flows"].get(c, 0) + port["units"].get(c, 0) * PXf.at[END, c] for c in set(port["flows"]) | set(port["units"])}; perf["attribution"] = {k: v / PAPER for k, v in sorted(attr.items(), key=lambda kv: -kv[1])}
perf["monthly"] = {str(k.date()): float(v) for k, v in V.resample("ME").last().pct_change().dropna().items()}
json.dump({"events": [(str(t.date()), k, txt) for t, k, txt in events], "feed": FEED.to_dict("records"), "perf": perf, "values": [(str(t.date()), v) for t, v in values], "books": {str(t.date()): [(b["sym"], b["weight"]) for b in bk["book"]] for t, bk in BOOKS.items()}}, open(os.path.join(C.DATA_DIR, "replay.json"), "w"), default=str, indent=1)
print(f"EVENTS: {len(events)} | feed alerts {len(feed)} | book snapshots {len(BOOKS)}")
print("PERF:", {k: (f"{v:+.1%}" if isinstance(v, float) else v) for k, v in perf.items()})
print(FEED.to_string(index=False, formatters={"fill": "{:.4g}".format, "now": "{:+.0%}".format, "peak": "{:+.0%}".format, "trade": "{:+.0%}".format}))
for t, k, txt in events: print(f"\n=== {t.date()} [{k}] ===\n{txt}")

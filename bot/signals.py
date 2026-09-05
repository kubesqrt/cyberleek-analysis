"""Panel builder and signal engine.

Rules (from the backtests): established names trigger on a 2x weekly-revenue breakout to an 8-week high while
price-to-revenue is at or below its own 180-day median; tokens under 90 days old trigger on consecutive rising
revenue days with 7d revenue >= 1.25x the 2-week average; the first day a young name qualifies is an 'early watch'.
Catalyst-time filters reject one-day spikes, recurring distributions and fresh data sources, and flag market-wide weeks."""
import math, datetime as dt
import numpy as np, pandas as pd
from . import config as C, data as D

class Panel:
    def __init__(self, REV, PX, meta):
        self.REV, self.PX, self.meta = REV, PX, meta
        self.idx = REV.index
        self.rev7 = REV.rolling(7).sum(); self.rev14 = REV.rolling(14).sum(); self.rev30 = REV.rolling(30, min_periods=7).sum()
        self.hist = REV.notna().cumsum()
        self.prior = self.rev7.shift(7).rolling(7 * (C.LOOKBACK_WEEKS - 1), min_periods=7).mean()
        self.hi = self.rev7.rolling(7 * C.LOOKBACK_WEEKS, min_periods=7).max()
        self.ratio = (self.rev7 / self.prior).replace([np.inf, -np.inf], np.nan)
        self.up = REV > REV.shift(1)
        P0 = self.idx[0]
        self.tok_age = pd.DataFrame({c: ((self.idx - meta[c]["px_start"]).days if meta[c]["px_start"] > P0 + pd.Timedelta(days=3) else np.full(len(self.idx), 9999)) for c in REV.columns}, index=self.idx)
        self.elig = (self.rev30 >= C.MIN_REV30) & (self.hist >= C.MIN_HIST) & PX.notna()
        self.slow_exit = (self.rev7 < self.rev7.shift(1).rolling(7 * C.EXIT_SLOW_WEEKS, min_periods=7).mean()) | ((self.rev30 / self.rev30.shift(30) - 1) < C.EXIT_MOM)
        self.markets = {}

    def attach_markets(self, markets):
        """markets: {gecko_id: {price, mcap, fdv, vol24h}} -> P/S history (constant-supply proxy) and its 180d median."""
        self.markets = markets
        mc = pd.Series({c: (markets.get(self.meta[c]["gecko"]) or {}).get("mcap") for c in self.REV.columns}, dtype="float")
        last = self.PX.ffill().iloc[-1]
        MC = self.PX.ffill().mul(mc / last, axis=1)
        ann = self.rev30 * 365 / 30
        self.PS = (MC / ann).replace([np.inf, -np.inf], np.nan)
        self.ps_rel = self.PS / self.PS.rolling(180, min_periods=90).median()

    def asof(self):
        """Last complete day (DeFiLlama's current day is partial)."""
        today = pd.Timestamp(dt.datetime.utcnow().date())
        t = self.idx[-1]
        return t - pd.Timedelta(days=1) if t >= today else t

    # ---- catalyst-time signatures for one name on day t
    def signature(self, c, t):
        w = self.REV[c][t - pd.Timedelta(days=6): t]; r7 = float(w.sum())
        one_day = float(w.max() / r7) if r7 > 0 else float("nan")
        base = self.REV[c][t - pd.Timedelta(days=90): t]
        med = float(base.median()) if len(base) else 0.0
        # recurring lump: an ISOLATED one-day spike now (>= 3x the other days of its week) and another isolated spike
        # 25-35 days ago (>= 3x its own +/-3-day neighbours). A steady ramp from zero does not qualify.
        def isolated(series, i):
            v = series.iloc[i]; nb = pd.concat([series.iloc[max(0, i - 3): i], series.iloc[i + 1: i + 4]])
            return len(nb) >= 3 and nb.median() > 0 and v >= C.RECURRING_MULT * nb.median()
        now_iso = len(w) >= 4 and w.drop(w.idxmax()).median() > 0 and w.max() >= C.RECURRING_MULT * w.drop(w.idxmax()).median()
        rw_full = self.REV[c][t - pd.Timedelta(days=C.RECURRING_WINDOW[1] + 3): t - pd.Timedelta(days=C.RECURRING_WINDOW[0] - 3)]
        recurring = bool(now_iso and any(isolated(rw_full, i) for i in range(3, max(3, len(rw_full) - 3))))
        prev = self.REV[c][t - pd.Timedelta(days=56): t - pd.Timedelta(days=7)]
        zero_share = float((prev <= 0).mean()) if len(prev) else 1.0
        fresh_product = None
        for name, s in (self.meta[c].get("products") or {}).items():
            s = s[s > 0]
            if len(s) == 0: continue
            first = s.index.min(); last7 = float(s[t - pd.Timedelta(days=6): t].sum())
            if (t - first).days < C.FRESH_PRODUCT_DAYS and r7 > 0 and last7 / r7 >= 0.5: fresh_product = name
        el = self.elig.loc[t]; names = el[el].index
        breadth = float(((self.ratio.loc[t, names] >= 1.5)).mean()) if len(names) else 0.0
        rising = int(self.up[c][t - pd.Timedelta(days=6): t].sum())
        px = self.PX[c].ffill()
        px14 = float(px.at[t] / px.at[t - pd.Timedelta(days=14)] - 1) if (t - pd.Timedelta(days=14)) in px.index and px.at[t - pd.Timedelta(days=14)] > 0 else float("nan")
        return {"one_day_share": one_day, "recurring": recurring, "zero_share": zero_share, "fresh_product": fresh_product, "breadth": breadth, "rising_days": rising, "px_14d": px14}

    def chain_shares(self, c, t, days=7):
        """{chain: share of the last `days` revenue} from the per-chain breakdown."""
        tot = {}
        for name, ser in (self.meta[c].get("products") or {}).items():
            ch = name.split("|")[0]; v = float(ser[t - pd.Timedelta(days=days - 1): t].sum())
            if v > 0: tot[ch] = tot.get(ch, 0.0) + v
        s = sum(tot.values())
        return {k: v / s for k, v in sorted(tot.items(), key=lambda kv: -kv[1])} if s > 0 else {}

    def market(self, c):
        return self.markets.get(self.meta[c]["gecko"]) or {}

    def scan(self, t=None):
        """All signals for day t (default: last complete day)."""
        t = t or self.asof(); out = []
        for c in self.REV.columns:
            if not bool(self.elig.at[t, c]): continue
            hist = int(self.hist.at[t, c]); age = int(self.tok_age.at[t, c]); young = age <= C.YOUNG_TOKEN_AGE and hist >= C.MIN_HIST
            mature = hist > C.MATURE_HIST and not young
            r7 = float(self.rev7.at[t, c]); r30 = float(self.rev30.at[t, c]); ratio = float(self.ratio.at[t, c]) if self.ratio.at[t, c] == self.ratio.at[t, c] else float("nan")
            rel = float(self.ps_rel.at[t, c]) if hasattr(self, "ps_rel") and self.ps_rel.at[t, c] == self.ps_rel.at[t, c] else float("nan")
            rule = None
            if mature and self.rev7.at[t, c] >= self.hi.at[t, c] and ratio == ratio and ratio >= C.BREAKOUT_K and self.prior.at[t, c] > 0:
                rule = "breakout"
            elif young:
                ups = all(bool(self.up.at[t - pd.Timedelta(days=k), c]) for k in range(C.YOUNG_RISING_DAYS))
                if ups and r7 >= C.YOUNG_WOW * float(self.rev14.at[t, c]) / 2: rule = "young_rising"
                elif not bool(self.elig.at[t - pd.Timedelta(days=1), c]): rule = "early_watch"
            if not rule: continue
            sig = self.signature(c, t); m = self.market(c)
            px = float(self.PX[c].ffill().at[t]); ann = r30 * 365 / 30
            mcap = m.get("mcap"); fdv = m.get("fdv"); vol = m.get("vol24h")
            s = {"sym": c, "name": self.meta[c]["name"], "gecko": self.meta[c]["gecko"], "date": str(t.date()), "rule": rule, "young": young, "tok_age": None if age == 9999 else age, "rev_hist": hist,
                 "rev7": r7, "rev30": r30, "ratio": ratio, "ps_mcap": (mcap / ann) if mcap and ann > 0 else None, "ps_fdv": (fdv / ann) if fdv and ann > 0 else None, "ps_rel": None if rel != rel else rel,
                 "price": px, "mcap": mcap, "fdv": fdv, "fdv_mcap": (fdv / mcap) if fdv and mcap else None, "vol24h": vol, "chains": self.meta[c].get("chains") or [], "chain_shares": self.chain_shares(c, t), "category": self.meta[c].get("category"), **sig}
            s["liquid"] = bool(vol and vol >= C.MIN_VOL30 and mcap and mcap >= C.MIN_MCAP)
            s["verdict"], s["reasons"] = self.verdict(s)
            s["stop"] = C.TRAIL_STOP_YOUNG if young else C.TRAIL_STOP
            s["size_hint"] = "5% (early sleeve)" if young else "10%"
            out.append(s)
        order = {"TRADE": 0, "TRADE (beta)": 1, "EARLY": 2, "WATCH": 3, "REJECT": 4}
        return sorted(out, key=lambda s: (order.get(s["verdict"], 9), -(s["rev7"] or 0)))

    @staticmethod
    def verdict(s):
        reasons = []
        if s["one_day_share"] == s["one_day_share"] and s["one_day_share"] >= C.ONE_DAY_SHARE_MAX: reasons.append(f"one-day spike: {s['one_day_share']:.0%} of the week's revenue on a single day")
        if s["recurring"]: reasons.append("recurring lump: a similar spike 25-35 days ago (distribution schedule, not growth)")
        if s["zero_share"] > C.FRESH_ZERO_SHARE and not s.get("young"): reasons.append(f"fresh data source: {s['zero_share']:.0%} zero-revenue days in the prior 8 weeks")
        if s["fresh_product"]: reasons.append(f"adapter change: sub-product '{s['fresh_product']}' is under {C.FRESH_PRODUCT_DAYS} days old and carries the week")
        if reasons: return "REJECT", reasons
        if s["rule"] == "breakout" and s["ps_rel"] is not None and s["ps_rel"] > C.PS_REL_MAX: return "WATCH", [f"already re-rated: P/S is {s['ps_rel']:.2f}x its own 180d median (limit {C.PS_REL_MAX:.1f}x)"]
        if not s["liquid"]: return "WATCH", [f"illiquid: 24h volume ${(s['vol24h'] or 0)/1e3:,.0f}k, mcap ${(s['mcap'] or 0)/1e6:,.1f}M (need ${C.MIN_VOL30/1e3:,.0f}k/day and ${C.MIN_MCAP/1e6:,.0f}M)"]
        if s["rule"] == "early_watch": return "EARLY", ["first day this young token qualifies: early-sleeve candidate, 5% size, 50% stop, no revenue exit"]
        if s["breadth"] >= C.BREADTH_BETA: return "TRADE (beta)", [f"market-wide week: {s['breadth']:.0%} of the universe is also spiking; treat as beta, prefer leaders with capture and hold past the slowdown exit"]
        return "TRADE", []

def load_panel(U, limit=None, log=print):
    rev, px, meta = {}, {}, {}
    for i, e in enumerate(U[:limit] if limit else U):
        series = None; products = {}; chains = set(); cat = e.get("category")
        for slug in e["slugs"]:
            try: s = D.llama_summary(slug)
            except Exception as ex: log(f"  {slug}: {ex}"); s = None
            if not s or not s["chart"]: continue
            ser = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(v or 0) for t, v in s["chart"]})
            series = ser if series is None else series.add(ser, fill_value=0)
            chains |= set(s["chains"] or []); cat = cat or s.get("category")
            for t, d in s["breakdown"][-120:]:
                ts = pd.Timestamp(int(t), unit="s").normalize()
                for chain, prods in (d or {}).items():
                    for prod, v in (prods or {}).items():
                        k = f"{chain}|{prod}"; products.setdefault(k, {}); products[k][ts] = products[k].get(ts, 0) + float(v or 0)
        if series is None or len(series) < 7: continue
        try: pts = D.llama_prices(e["gecko"])
        except Exception as ex: log(f"  price {e['gecko']}: {ex}"); pts = []
        if len(pts) < 7: continue
        p = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(v) for t, v in pts}); p = p[~p.index.duplicated(keep="last")].sort_index()
        key = e["symbol"]
        if key in rev: key = f"{key}_{e['gecko']}"
        rev[key] = series[~series.index.duplicated(keep="last")].sort_index(); px[key] = p
        prods = {k: pd.Series(v).sort_index() for k, v in products.items()}
        meta[key] = {"name": e["name"], "gecko": e["gecko"], "chains": sorted(chains), "category": cat, "products": prods, "px_start": p.index.min(), "r30": e["r30"], "slugs": e["slugs"]}
        if i % 25 == 0: log(f"  panel {i}/{len(U[:limit] if limit else U)}")
    REV = pd.DataFrame(rev).sort_index(); PX = pd.DataFrame(px).sort_index()
    idx = pd.date_range(min(REV.index.min(), PX.index.min()), max(REV.index.max(), PX.index.max()), freq="D")
    REV = REV.reindex(idx); PX = PX.reindex(idx).ffill(limit=3)
    for c in REV.columns:
        fv = REV[c].first_valid_index()
        if fv is not None: REV.loc[fv:, c] = REV.loc[fv:, c].fillna(0.0)
    return Panel(REV, PX, meta)

"""Thesis cards, invalidation monitors and chain-wave detection (e.g. 'Robinhood Chain wave: PONS first-order, ARB revenue share')."""
import pandas as pd
from . import config as C, data as D

def invalidation_rules(sig, research=None, pool=None, wave=None):
    stop = sig.get("stop", C.TRAIL_STOP)
    rules = [
        {"kind": "rev_slowdown", "label": "7d revenue below its 4-week average (or 30d revenue down 30% m/m)", "action": "exit (momentum sleeve)" if not sig.get("young") else "note only (early sleeve uses the stop)"},
        {"kind": "rev_collapse", "label": "30d revenue below 50% of its 90-day peak", "threshold": 0.5, "action": "exit: thesis broken"},
        {"kind": "price_stop", "label": f"price {int(stop*100)}% below its peak since entry", "threshold": stop, "action": "exit"},
        {"kind": "liquidity", "label": f"best pool liquidity below 50% of entry level or 24h volume under ${C.MIN_VOL30/2/1e3:,.0f}k", "threshold": 0.5, "action": "reduce: exit liquidity shrinking"},
        {"kind": "contract", "label": "GoPlus verdict turns FAIL (tax, honeypot, ownership change)", "action": "exit immediately"},
    ]
    if sig.get("fdv_mcap") and sig["fdv_mcap"] > 3: rules.append({"kind": "unlock", "label": f"FDV is {sig['fdv_mcap']:.1f}x market cap: check the unlock schedule; a cliff inside the hold window invalidates", "action": "size down / avoid"})
    if wave: rules.append({"kind": "chain_wave", "chain": wave["chain"], "label": f"{wave['chain']} daily fees fall below 40% of their 7-day peak at entry (the wave is over)", "threshold": 0.4, "action": "exit wave positions"})
    for inv in (research or {}).get("invalidation", []) or []:
        if isinstance(inv, dict): rules.append({"kind": "manual", "label": f"{inv.get('signal')}: {inv.get('threshold')}", "action": "review"})
    return rules

def detect_chain_waves(signals, universe, min_triggers=2, growth=2.0, min_share=0.2, min_fees7=1_000_000, panel=None):
    """A chain is 'in a wave' when >= 2 protocols earning >= 20% of their week there trigger together, or its fees
    doubled week on week, and the chain itself earns >= $1M a week. Baskets are ranked by each protocol's revenue share on the chain."""
    by_chain = {}
    for s in signals:
        if s["verdict"].startswith("TRADE") or s["verdict"] == "EARLY":
            for ch, share in (s.get("chain_shares") or {}).items():
                if share >= min_share: by_chain.setdefault(ch, []).append(s["sym"])
    t = panel.asof() if panel is not None else None
    waves = []
    for ch, syms in by_chain.items():
        try: fees = D.llama_chain_fees(ch)
        except Exception: fees = []
        f = [v for _, v in fees[-14:]]
        g = (sum(f[-7:]) / sum(f[:7])) if len(f) == 14 and sum(f[:7]) > 0 else None
        fees7 = sum(f[-7:]) if len(f) >= 7 else 0
        if fees7 >= min_fees7 and (len(set(syms)) >= min_triggers or (g and g >= growth)):
            basket = []
            for e in universe:
                if ch not in (e.get("chains") or []) or e["r30"] < C.MIN_REV30: continue
                if any(b["sym"] == e["symbol"] for b in C.KNOWN_BENEFICIARIES.get(ch, [])): continue   # listed once, as the revenue-share line
                share = None
                if panel is not None and t is not None:
                    col = next((c for c in panel.REV.columns if panel.meta[c]["gecko"] == e["gecko"]), None)
                    if col: share = panel.chain_shares(col, t, days=7).get(ch, 0.0)
                if share is not None and share < 0.05: continue
                role = "first-order (receives the chain's activity)" if (e.get("category") in C.FIRST_ORDER_CATEGORIES) else "second-order"
                basket.append({"sym": e["symbol"], "name": e["name"], "role": role, "r30": e["r30"], "share": share, "triggered": e["symbol"] in syms})
            for b in C.KNOWN_BENEFICIARIES.get(ch, []): basket.append({"sym": b["sym"], "name": b["sym"], "role": "revenue share: " + b["why"], "r30": None, "triggered": b["sym"] in syms})
            basket.sort(key=lambda b: (0 if b["role"].startswith("first") else (1 if b["role"].startswith("revenue") else 2), -((b.get("share") or 0) * (b["r30"] or 0))))
            waves.append({"chain": ch, "triggered": sorted(set(syms)), "fee_growth_wow": g, "fees_7d": fees7, "basket": basket[:12]})
    return sorted(waves, key=lambda w: -len(w["triggered"]))

def card(sig, research=None, safety=None, pool=None, waves=None):
    wave = next((w for w in (waves or []) if any(ch in w["chain"] for ch in sig.get("chains") or [])), None)
    role = None
    if wave: role = "first-order" if sig.get("category") in C.FIRST_ORDER_CATEGORIES else "second-order"
    return {"sym": sig["sym"], "name": sig["name"], "verdict": sig["verdict"], "rule": sig["rule"], "driver_type": (research or {}).get("type", "unknown"), "catalyst": (research or {}).get("catalyst"),
            "beneficiary": (research or {}).get("beneficiary"), "wave": wave["chain"] if wave else None, "role_in_wave": role, "thesis": (research or {}).get("thesis", []), "must_stay_true": (research or {}).get("must_stay_true", []),
            "invalidation": invalidation_rules(sig, research, pool, wave), "risks": (research or {}).get("risks", []), "safety": safety, "confidence": (research or {}).get("confidence", "low"), "sources": (research or {}).get("sources", []),
            "sizing": sig.get("size_hint"), "stop": sig.get("stop")}

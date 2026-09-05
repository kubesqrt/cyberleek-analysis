"""CLI for testing without Telegram.
  python -m bot.run_scan [--limit N]                 scan and print cards
  python -m bot.run_scan --view SYM | --research SYM | --safety SYM | --plan SYM USD | --thesis
"""
import argparse, json, sys
from . import config as C, universe as UV, signals as SG, safety as SF, research as RS, thesis as TH, execute as EX, report as RP, scheduler as SC, portfolio as PF, monitors as MO

def strip(s):
    import re; return re.sub(r"<[^>]+>", "", s)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int); ap.add_argument("--view"); ap.add_argument("--research"); ap.add_argument("--safety"); ap.add_argument("--plan", nargs=2); ap.add_argument("--thesis", action="store_true"); ap.add_argument("--all", action="store_true"); ap.add_argument("--book", action="store_true"); ap.add_argument("--rebalance", action="store_true"); ap.add_argument("--review", action="store_true"); ap.add_argument("--quality")
    a = ap.parse_args()
    st = SC.refresh(SC.State, limit=a.limit)
    sigs = st.signals if a.all else [s for s in st.signals if s["verdict"] != "REJECT"]
    print(strip(RP.scan_summary(st.asof, st.signals, st.waves)))
    for s in sigs: print("\n" + strip(RP.alert_card(s)))
    if a.all: pass
    if a.view:
        s = next((x for x in st.signals if x["sym"].upper() == a.view.upper()), None); print(strip(RP.detail_view(s, st.panel)) if s else f"{a.view}: no signal today")
    if a.safety:
        e = UV.find(st.universe, a.safety); ch, addr, pool, _ = SF.token_location(e); print(strip(RP.safety_view(SF.check(e["symbol"], ch, addr, pool))))
    if a.research:
        s = next((x for x in st.signals if x["sym"].upper() == a.research.upper()), None); e = UV.find(st.universe, a.research)
        card = s or {"sym": e["symbol"], "name": e["name"], "gecko": e["gecko"], "slugs": e["slugs"], "date": st.asof}
        r = RS.research(card); ch, addr, pool, _ = SF.token_location(e); sf = SF.check(e["symbol"], ch, addr, pool) if ch else None
        print(strip(RP.thesis_view(TH.card(s or {**card, "verdict": "n/a", "rule": "n/a", "chains": e["chains"], "category": e.get("category")}, r, sf, pool, st.waves))))
    if a.plan:
        e = UV.find(st.universe, a.plan[0]); p = EX.plan_buy(e, float(a.plan[1])); print(strip(RP.plan_view(p, C.LIVE_TRADING))); print(json.dumps({k: v for k, v in p.items() if k in ("steps", "eff_price", "spot_price", "impact", "gas_usd", "fees_usd", "duration_s", "tool")}, indent=1, default=str))
    if a.book: print("\n" + strip(RP.book_view(st.book)))
    if a.quality:
        e = UV.find(st.universe, a.quality); c = next((k for k in st.panel.REV.columns if st.panel.meta[k]["gecko"] == e["gecko"]), None)
        m = PF.metrics(st.panel, c, st.panel.asof(), e, st.panel.market(c), PF.holders_rev30(e)); print("\n" + strip(RP.quality_view(m, PF.vetoes(m))))
    if a.rebalance:
        hs = PF.holdings(st.panel); cash = float(MO.setting("cash") or 0); rb = PF.rebalance(st.book, hs, cash, last_rebalance=MO.setting("last_rebalance"))
        print("\n" + strip(RP.portfolio_view(hs, cash, rb["value"]))); print("\n" + strip(RP.rebalance_view(rb)))
    if a.review: print("\n" + strip(RP.review_view(PF.review(st.book, PF.holdings(st.panel), st.panel, st.universe))))
    if a.thesis:
        for w in st.waves: print("\n" + strip(RP.wave_view(w)))

if __name__ == "__main__": main()

"""Daily pipeline: refresh universe + panel + markets, scan, detect waves, evaluate monitors. Usable from cron or the Telegram job queue."""
import json, datetime as dt
from . import config as C, data as D, universe as UV, signals as SG, thesis as TH, monitors as MO, safety as SF, report as RP, portfolio as PF

class State:
    universe = None; panel = None; signals = []; waves = []; asof = None; plans = {}; theses = {}; book = None

def refresh(state, limit=None, log=print):
    log("universe…"); state.universe = UV.build()
    log(f"panel for {len(state.universe[:limit] if limit else state.universe)} entities…"); state.panel = SG.load_panel(state.universe, limit=limit, log=log)
    log("markets…"); mk = D.cg_markets([e["gecko"] for e in (state.universe[:limit] if limit else state.universe)])
    state.panel.attach_markets(mk)
    state.asof = str(state.panel.asof().date()); state.signals = state.panel.scan(); state.waves = TH.detect_chain_waves(state.signals, state.universe, panel=state.panel)
    log("long-hold book…"); state.book = PF.build_book(state.panel, state.universe, log=log)
    MO.save_scan(state.asof, {"signals": state.signals, "waves": state.waves, "book": state.book}); log(f"scan {state.asof}: {len(state.signals)} signals, {len(state.waves)} waves, book {len((state.book or {}).get('book', []))}")
    return state

def pool_lookup(p):
    ent = UV.find(State.universe or UV.build(), p["sym"])
    if not ent: return None
    ch, addr, pool, _ = SF.token_location(ent); return pool
def safety_lookup(p):
    ent = UV.find(State.universe or UV.build(), p["sym"])
    if not ent: return None
    ch, addr, pool, _ = SF.token_location(ent); return SF.check(p["sym"], ch, addr, pool) if ch else None
def chain_fees7(chain):
    f = D.llama_chain_fees(chain); return sum(v for _, v in f[-7:]) if len(f) >= 7 else None

def daily_messages(state):
    msgs = []
    hs = PF.holdings(state.panel); cash = float(MO.setting("cash") or 0)
    if hs or cash:
        rb = PF.rebalance(state.book, hs, cash, last_rebalance=MO.setting("last_rebalance"))
        msgs.append(RP.portfolio_view(hs, cash, rb["value"]))
        if rb["trades"] or rb["due"]: msgs.append(RP.rebalance_view(rb))
    prev = MO.setting("book_syms"); cur = ",".join(b["sym"] for b in (state.book or {}).get("book", []))
    if prev is not None and prev != cur:
        a, b = set(prev.split(",")) - {""}, set(cur.split(",")) - {""}
        msgs.append("📚 Book changed: " + (f"in {', '.join(sorted(b - a))}" if b - a else "") + (f" · out {', '.join(sorted(a - b))}" if a - b else ""))
    MO.setting("book_syms", cur)
    msgs.append(RP.scan_summary(state.asof, state.signals, state.waves))
    for s in state.signals:
        if s["verdict"] in ("TRADE", "TRADE (beta)", "EARLY"): msgs.append(RP.alert_card(s))
    for w in state.waves: msgs.append(RP.wave_view(w))
    fired = MO.evaluate(state.panel, pool_lookup=pool_lookup, safety_lookup=safety_lookup, chain_fees_lookup=chain_fees7)
    for p, m, value in fired:
        txt = f"🔴 <b>Invalidation — {p['sym']}</b> (#{p['id']}): {m['label']} · {value or ''}"; MO.log_alert(p["sym"], m["kind"], txt); msgs.append(txt)
    return msgs

if __name__ == "__main__":
    import sys, urllib.request, urllib.parse
    st = refresh(State, limit=int(sys.argv[1]) if len(sys.argv) > 1 else None)
    for m in daily_messages(st):
        print("\n" + m)
        if C.TELEGRAM_BOT_TOKEN and C.TELEGRAM_ALLOWED_CHATS:
            for chat in C.TELEGRAM_ALLOWED_CHATS:
                urllib.request.urlopen(f"https://api.telegram.org/bot{C.TELEGRAM_BOT_TOKEN}/sendMessage", data=urllib.parse.urlencode({"chat_id": chat, "text": m, "parse_mode": "HTML", "disable_web_page_preview": "1"}).encode(), timeout=30)

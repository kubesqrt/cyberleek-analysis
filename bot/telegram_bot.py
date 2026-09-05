"""Telegram interface. Commands:
/scan  /alerts  /view SYM  /research SYM  /thesis  /safety SYM  /buy SYM USD [FROM_CHAIN]  /sell SYM [FRACTION]  /watch SYM  /positions  /monitors  /close ID  /help"""
import asyncio, json, logging, uuid, datetime as dt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from . import config as C, universe as UV, safety as SF, research as RS, thesis as TH, execute as EX, monitors as MO, report as RP, scheduler as SC

log = logging.getLogger("bot"); ST = SC.State

def allowed(update):
    return not C.TELEGRAM_ALLOWED_CHATS or update.effective_chat.id in C.TELEGRAM_ALLOWED_CHATS

async def send(update, text, **kw):
    for i in range(0, len(text), 3900): await update.effective_chat.send_message(text[i:i + 3900], parse_mode="HTML", disable_web_page_preview=True, **({} if i + 3900 < len(text) else kw))

def ensure_state():
    if ST.panel is None:
        asof, payload = MO.last_scan()
        if payload: ST.signals, ST.waves, ST.asof = payload["signals"], payload["waves"], asof
        ST.universe = ST.universe or UV.build()

def find_signal(sym):
    return next((s for s in ST.signals if s["sym"].upper() == sym.upper()), None)

def entity_or_signal_card(sym):
    e = UV.find(ST.universe, sym)
    if not e: return None, None
    s = find_signal(e["symbol"]) or find_signal(sym)
    card = s or {"sym": e["symbol"], "name": e["name"], "gecko": e["gecko"], "slugs": e["slugs"], "date": ST.asof, "verdict": "n/a", "rule": "n/a", "chains": e.get("chains") or [], "category": e.get("category"), "young": False, "stop": C.TRAIL_STOP, "size_hint": "10%"}
    return e, card

# ---------------- commands
async def cmd_help(update: Update, ctx):
    if not allowed(update): return
    await send(update, "<b>Revenue bot</b>\n/scan — refresh data and scan now (takes a few minutes)\n/alerts — today's tradeable signals\n/view SYM — detailed view\n/research SYM — catalyst, thesis, invalidation\n/thesis — chain waves and how to express them\n/safety SYM — scam and liquidity checks\n/buy SYM USD [FROM_CHAIN] — plan a buy (bridge+swap), confirm to execute\n/sell SYM [FRACTION] — plan a sell\n/watch SYM — monitor invalidation without buying\n/positions · /monitors · /close ID\n"
                 + ("🔴 LIVE trading is ON" if C.LIVE_TRADING and C.WALLET_PRIVATE_KEY else "🧪 Dry-run mode (set LIVE_TRADING=1 and WALLET_PRIVATE_KEY to execute)"))

async def cmd_scan(update: Update, ctx):
    if not allowed(update): return
    await send(update, "Refreshing DeFiLlama, prices and markets… this takes a few minutes.")
    try: await asyncio.to_thread(SC.refresh, ST, None, log.info)
    except Exception as e: await send(update, f"Scan failed: {e}"); return
    for m in SC.daily_messages(ST): await send(update, m)

async def cmd_alerts(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ST.signals: await send(update, "No scan yet. Run /scan."); return
    await send(update, RP.scan_summary(ST.asof, ST.signals, ST.waves))
    for s in ST.signals:
        if s["verdict"] in ("TRADE", "TRADE (beta)", "EARLY", "WATCH"): await send(update, RP.alert_card(s))

async def cmd_view(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ctx.args: await send(update, "Usage: /view SYM"); return
    s = find_signal(ctx.args[0])
    if not s: await send(update, f"{ctx.args[0]}: no signal in the last scan ({ST.asof}). Try /research or /safety."); return
    if ST.panel is None: await send(update, RP.alert_card(s)); return
    await send(update, RP.detail_view(s, ST.panel))

async def cmd_safety(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ctx.args: await send(update, "Usage: /safety SYM"); return
    e = UV.find(ST.universe, ctx.args[0])
    if not e: await send(update, "Unknown token (not in the DeFiLlama revenue universe)."); return
    ch, addr, pool, contracts = await asyncio.to_thread(SF.token_location, e)
    s = await asyncio.to_thread(SF.check, e["symbol"], ch, addr, pool)
    await send(update, RP.safety_view(s) + (f"Contracts: {', '.join(f'{k}: {v[:10]}…' for k, v in contracts.items())}" if contracts else ""))

async def cmd_research(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ctx.args: await send(update, "Usage: /research SYM"); return
    e, card = entity_or_signal_card(ctx.args[0])
    if not e: await send(update, "Unknown token."); return
    await send(update, f"Researching {e['symbol']}…" + ("" if C.ANTHROPIC_API_KEY else " (no ANTHROPIC_API_KEY: data-only view)"))
    r = await asyncio.to_thread(RS.research, card)
    ch, addr, pool, _ = await asyncio.to_thread(SF.token_location, e)
    sf = await asyncio.to_thread(SF.check, e["symbol"], ch, addr, pool) if ch else None
    tc = TH.card(card, r, sf, pool, ST.waves); ST.theses[e["symbol"]] = tc
    await send(update, RP.thesis_view(tc))

async def cmd_thesis(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ST.waves: await send(update, "No chain wave detected in the last scan."); return
    for w in ST.waves: await send(update, RP.wave_view(w))

async def cmd_buy(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if len(ctx.args) < 2: await send(update, "Usage: /buy SYM USD [FROM_CHAIN_ID]"); return
    e, card = entity_or_signal_card(ctx.args[0])
    if not e: await send(update, "Unknown token."); return
    usd = float(ctx.args[1]); from_chain = int(ctx.args[2]) if len(ctx.args) > 2 else None
    ch, addr, pool, _ = await asyncio.to_thread(SF.token_location, e)
    sf = await asyncio.to_thread(SF.check, e["symbol"], ch, addr, pool) if ch else {"verdict": "UNVERIFIED", "score": 0, "hard": [], "warn": [], "info": [], "sym": e["symbol"], "chain": ch, "address": addr}
    if sf["verdict"] == "FAIL": await send(update, RP.safety_view(sf) + "Refusing to plan a buy on a FAIL."); return
    p = await asyncio.to_thread(EX.plan_buy, e, usd, from_chain, None, None, (card.get("price") if card else None))
    pid = uuid.uuid4().hex[:8]; ST.plans[pid] = {"plan": p, "entity": e, "card": card, "safety": sf, "pool": pool, "chain": ch, "address": addr}
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm", callback_data=f"buy:{pid}"), InlineKeyboardButton("✖ Cancel", callback_data=f"cancel:{pid}")]]) if p.get("ok") else None
    await send(update, RP.safety_view(sf, short=True) + RP.plan_view(p, C.LIVE_TRADING and bool(C.WALLET_PRIVATE_KEY)), reply_markup=kb)

async def cmd_sell(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ctx.args: await send(update, "Usage: /sell SYM [FRACTION 0-1]"); return
    e = UV.find(ST.universe, ctx.args[0]); frac = float(ctx.args[1]) if len(ctx.args) > 1 else 1.0
    if not e: await send(update, "Unknown token."); return
    p = await asyncio.to_thread(EX.plan_sell, e, frac)
    if p.get("errors"): await send(update, "🛑 " + "; ".join(p["errors"])); return
    pid = uuid.uuid4().hex[:8]; ST.plans[pid] = {"plan": p, "entity": e, "sell": True}
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm sell", callback_data=f"sell:{pid}"), InlineKeyboardButton("✖ Cancel", callback_data=f"cancel:{pid}")]])
    await send(update, f"Sell {frac:.0%} of {e['symbol']} → ≈ ${p['usd_out']:,.0f} (min {p['tokens_min']:,.0f} stable) via " + ", ".join(str(s['tool']) for s in p['steps']), reply_markup=kb)

async def cmd_watch(update: Update, ctx):
    if not allowed(update): return
    ensure_state()
    if not ctx.args: await send(update, "Usage: /watch SYM"); return
    e, card = entity_or_signal_card(ctx.args[0])
    if not e: await send(update, "Unknown token."); return
    ch, addr, pool, _ = await asyncio.to_thread(SF.token_location, e)
    tc = ST.theses.get(e["symbol"]) or TH.card(card, None, None, pool, ST.waves)
    wave = tc.get("wave"); f7 = await asyncio.to_thread(SC.chain_fees7, wave) if wave else None
    pid = MO.add_position(card, "watch", 0, card.get("price") or (pool or {}).get("price_usd") or 0, ch, addr, tc, pool, wave, f7)
    await send(update, f"Watching {e['symbol']} as #{pid} with {len(tc['invalidation'])} invalidation monitors. /monitors to see them.")

async def cmd_positions(update: Update, ctx):
    if not allowed(update): return
    ensure_state(); await send(update, RP.positions_view(MO.positions("open"), ST.panel))

async def cmd_monitors(update: Update, ctx):
    if not allowed(update): return
    await send(update, RP.monitors_view(MO.monitors()))

async def cmd_close(update: Update, ctx):
    if not allowed(update): return
    if not ctx.args: await send(update, "Usage: /close ID"); return
    MO.close_position(int(ctx.args[0]), note="closed via /close"); await send(update, f"Closed #{ctx.args[0]}.")

async def on_button(update: Update, ctx):
    q = update.callback_query; await q.answer()
    if not allowed(update): return
    action, pid = q.data.split(":", 1); item = ST.plans.pop(pid, None)
    if not item: await q.edit_message_text("Plan expired. Re-run the command."); return
    if action == "cancel": await q.edit_message_text("Cancelled."); return
    res = await asyncio.to_thread(EX.execute, item["plan"])
    if action == "buy":
        p = item["plan"]; card = item["card"]; tc = ST.theses.get(item["entity"]["symbol"]) or TH.card(card, None, item["safety"], item["pool"], ST.waves)
        wave = tc.get("wave"); f7 = await asyncio.to_thread(SC.chain_fees7, wave) if wave else None
        pos = MO.add_position(card, "buy" if res.get("sent") else "paper", p["usd"], p.get("eff_price") or card.get("price") or 0, item["chain"], item["address"], tc, item["pool"], wave, f7, tx=json.dumps(res.get("hashes")) if res.get("sent") else None)
        txt = (f"✅ Sent: {res['hashes']}" if res.get("sent") else f"🧪 {res.get('reason')}") + f"\nRecorded as #{pos} with {len(tc['invalidation'])} monitors. /monitors"
    else:
        txt = f"✅ Sent: {res['hashes']}" if res.get("sent") else f"🧪 {res.get('reason')}"
    await q.edit_message_text(txt)

async def daily_job(ctx: ContextTypes.DEFAULT_TYPE):
    try: await asyncio.to_thread(SC.refresh, ST, None, log.info)
    except Exception as e: log.exception("daily refresh failed"); return
    for chat in C.TELEGRAM_ALLOWED_CHATS:
        for m in SC.daily_messages(ST):
            for i in range(0, len(m), 3900): await ctx.bot.send_message(chat, m[i:i + 3900], parse_mode="HTML", disable_web_page_preview=True)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not C.TELEGRAM_BOT_TOKEN: raise SystemExit("Set TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(C.TELEGRAM_BOT_TOKEN).build()
    for name, fn in [("start", cmd_help), ("help", cmd_help), ("scan", cmd_scan), ("alerts", cmd_alerts), ("view", cmd_view), ("research", cmd_research), ("thesis", cmd_thesis), ("safety", cmd_safety), ("buy", cmd_buy), ("sell", cmd_sell), ("watch", cmd_watch), ("positions", cmd_positions), ("monitors", cmd_monitors), ("close", cmd_close)]:
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(CallbackQueryHandler(on_button))
    if app.job_queue: app.job_queue.run_daily(daily_job, time=dt.time(hour=C.DAILY_HOUR_UTC, tzinfo=dt.timezone.utc))
    app.run_polling()

if __name__ == "__main__": main()

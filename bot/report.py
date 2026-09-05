"""Telegram-friendly (HTML) rendering of signals, theses, safety checks, plans, waves and monitors."""
import html, datetime as dt

def _m(v, unit="k"):
    if v is None or v != v: return "—"
    return f"${v/1e6:,.1f}M" if (unit == "M" or abs(v) >= 1e6) else f"${v/1e3:,.0f}k"
def _x(v): return "—" if v is None or v != v else f"{v:.1f}×"
def _p(v): return "—" if v is None or v != v else f"{v:+.0%}"
E = html.escape

ICON = {"TRADE": "🟢", "TRADE (beta)": "🟡", "EARLY": "🐣", "WATCH": "👀", "REJECT": "⛔"}

def alert_card(s):
    top = list((s.get('chain_shares') or {}).items())[:2]
    where = ', '.join(f"{ch} {sh:.0%}" for ch, sh in top) if top else (', '.join(s['chains'][:2]) or '?')
    head = f"{ICON.get(s['verdict'], '•')} <b>{E(s['sym'])}</b> · {E(s['name'])} · {E(where)}\n"
    rule = {"breakout": "2× revenue breakout (established)", "young_rising": f"early sleeve: {s['rising_days']} rising days, token {s['tok_age']}d old", "early_watch": f"early watch: first day eligible, token {s['tok_age']}d old"}[s["rule"]]
    body = (f"<b>{s['verdict']}</b> — {rule}\n"
            f"Rev 7d {_m(s['rev7'])} ({_x(s['ratio'])} vs 8wk) · 30d {_m(s['rev30'])}\n"
            f"P/S {_x(s['ps_mcap'])} mcap · {_x(s['ps_fdv'])} FDV · vs own median {_x(s['ps_rel'])} · FDV/mcap {_x(s['fdv_mcap'])}\n"
            f"Mcap {_m(s['mcap'], 'M')} · vol 24h {_m(s['vol24h'])} · price {s['price']:.4g}\n"
            f"Signature: 1-day share {s['one_day_share']:.0%} · breadth {s['breadth']:.0%} · px 14d {_p(s['px_14d'])}\n")
    if s.get("reasons"): body += "".join(f"↳ {E(r)}\n" for r in s["reasons"])
    body += f"Plan: size {s['size_hint']}, stop {int(s['stop']*100)}%, exit on revenue slowdown\n"
    body += f"/view {s['sym']} · /research {s['sym']} · /safety {s['sym']} · /buy {s['sym']} 500"
    return head + body

def scan_summary(asof, signals, waves):
    n = {k: sum(1 for s in signals if s["verdict"] == k) for k in ICON}
    out = f"<b>Scan {asof}</b>: {len(signals)} signals — 🟢 {n['TRADE']} trade · 🟡 {n['TRADE (beta)']} beta · 🐣 {n['EARLY']} early · 👀 {n['WATCH']} watch · ⛔ {n['REJECT']} rejected\n"
    for w in waves: out += f"🌊 <b>{E(w['chain'])} wave</b>: {', '.join(w['triggered'])} triggered; chain fees {_x(w['fee_growth_wow'])} w/w → /thesis\n"
    return out

def detail_view(s, panel):
    c = s["sym"]; t = panel.idx[panel.idx <= __import__('pandas').Timestamp(s["date"])][-1]
    rev = panel.REV[c][t - __import__('pandas').Timedelta(days=13): t]
    bars = "".join("▁▂▃▄▅▆▇█"[min(7, int(7 * v / rev.max()))] if rev.max() > 0 else "▁" for v in rev)
    prods = {}
    for name, ser in (panel.meta[c].get("products") or {}).items():
        v = float(ser[t - __import__('pandas').Timedelta(days=6): t].sum())
        if v > 0: prods[name] = v
    top = sorted(prods.items(), key=lambda kv: -kv[1])[:5]; tot = sum(prods.values()) or 1
    out = alert_card(s) + f"\n\n<b>Last 14 days</b> {bars}  (max {_m(rev.max())}/day)\n<b>Where the revenue comes from (7d)</b>\n"
    out += "".join(f"• {E(k)}: {_m(v)} ({v/tot:.0%})\n" for k, v in top)
    out += f"Category {E(str(s.get('category')))} · revenue history {s['rev_hist']}d · token age {s['tok_age'] or '>2y'}d\n"
    return out

def thesis_view(card):
    out = f"🧭 <b>Thesis — {E(card['sym'])}</b> ({E(card['name'])}) · {card['verdict']} · confidence {E(str(card['confidence']))}\n"
    out += f"<b>Driver</b>: {E(str(card['driver_type']))}" + (f" · wave: {E(card['wave'])} ({card['role_in_wave']})" if card.get("wave") else "") + "\n"
    if card.get("catalyst"): out += f"<b>Catalyst</b>: {E(str(card['catalyst']))}\n"
    if card.get("beneficiary"): out += f"<b>First-order beneficiary</b>: {E(str(card['beneficiary']))}\n"
    if card.get("thesis"): out += "<b>Thesis</b>\n" + "".join(f"• {E(str(x))}\n" for x in card["thesis"])
    if card.get("must_stay_true"): out += "<b>Must stay true</b>\n" + "".join(f"• {E(str(x))}\n" for x in card["must_stay_true"])
    out += "<b>Invalidation (monitored after /buy or /watch)</b>\n" + "".join(f"• {E(r['label'])} → {E(r['action'])}\n" for r in card["invalidation"])
    if card.get("risks"): out += "<b>Risks</b>\n" + "".join(f"• {E(str(x))}\n" for x in card["risks"][:6])
    if card.get("safety"): out += safety_view(card["safety"], short=True)
    out += f"Sizing {E(str(card['sizing']))} · stop {int((card['stop'] or 0.25)*100)}%\n"
    if card.get("sources"): out += "Sources: " + " · ".join(f'<a href="{E(u)}">{i+1}</a>' for i, u in enumerate(card["sources"][:4])) + "\n"
    return out

def safety_view(s, short=False):
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "🛑", "UNVERIFIED": "❔"}[s["verdict"]]
    out = f"{icon} <b>Safety {s['verdict']}</b> (score {s['score']}) · {E(str(s.get('chain')))} {E((s.get('address') or '')[:10])}…\n"
    if s["hard"]: out += "".join(f"🛑 {E(x)}\n" for x in s["hard"])
    if s["warn"]: out += "".join(f"⚠️ {E(x)}\n" for x in s["warn"])
    if not short: out += "".join(f"• {E(x)}\n" for x in s["info"])
    return out

def plan_view(p, live):
    if p.get("errors"): return f"🛑 <b>Cannot buy {E(p['sym'])}</b>\n" + "".join(f"• {E(e)}\n" for e in p["errors"]) + "".join(f"⚠️ {E(w)}\n" for w in p.get("warnings", []))
    out = f"🧾 <b>Buy plan {E(p['sym'])}</b> — ${p['usd']:,.0f} {E(p['from_token'])} on chain {p['from_chain']} → {E(str(p['to_chain_name']))}\n"
    out += "".join(f"{i+1}. {E(str(st['type']))} via {E(str(st['tool']))}: {E(str(st['from']))} (chain {st['from_chain']}) → {E(str(st['to']))} (chain {st['to_chain']})\n" for i, st in enumerate(p["steps"]))
    out += f"Get ≈ {p['tokens_out']:,.2f} {E(p['sym'])} (min {p['tokens_min']:,.2f}) · eff. price {p['eff_price']:.4g} vs spot {p['spot_price']:.4g} · impact {_p(p['impact'])}\n"
    out += f"Gas ≈ ${p['gas_usd']:.2f} · fees ≈ ${p['fees_usd']:.2f} · time ≈ {int(p['duration_s'] or 0)//60} min\n"
    if p.get("pool"): out += f"Pool: {E(str(p['pool']['dex']))} liquidity {_m(p['pool']['liquidity_usd'])}, 24h vol {_m(p['pool']['vol24h'])}\n"
    out += "".join(f"⚠️ {E(w)}\n" for w in p.get("warnings", []))
    out += ("🔴 LIVE: Confirm will sign and send." if live else "🧪 Dry run: LIVE_TRADING is off, Confirm records the position for monitoring only.")
    return out

def wave_view(w):
    out = f"🌊 <b>{E(w['chain'])} wave</b> — {len(w['triggered'])} triggers: {E(', '.join(w['triggered']))}; chain fees 7d {_m(w['fees_7d'], 'M')} ({_x(w['fee_growth_wow'])} w/w)\n<b>How to express it</b>\n"
    for b in w["basket"]: out += f"• {E(b['sym'])} — {E(b['role'])}" + (f" · rev30 {_m(b['r30'])}" if b.get("r30") else "") + (f" · {b['share']:.0%} of its revenue on {E(w['chain'])}" if b.get("share") is not None else "") + (" · 🔔 triggered" if b.get("triggered") else "") + "\n"
    return out

def positions_view(ps, panel=None):
    if not ps: return "No open positions or watches."
    out = "<b>Open</b>\n"
    for p in ps:
        px = None
        if panel is not None and p["sym"] in panel.PX.columns: px = float(panel.PX[p["sym"]].ffill().iloc[-1])
        out += f"#{p['id']} {E(p['sym'])} {p['kind']} · {p['sleeve']} · entry {p['entry_date']} @ {p['entry_px']:.4g}" + (f" → {px:.4g} ({px/p['entry_px']-1:+.0%})" if px and p["entry_px"] else "") + (f" · ${p['size_usd']:,.0f}" if p.get("size_usd") else "") + (f" · wave {E(p['wave'])}" if p.get("wave") else "") + "\n"
    return out

def monitors_view(ms):
    if not ms: return "No monitors."
    out = "<b>Monitors</b>\n"
    for m in ms: out += f"{'🔴' if m['state']=='fired' else '🟢'} {E(m['sym'])} · {E(m['label'])}" + (f" · {E(str(m['last_value']))}" if m.get("last_value") else "") + "\n"
    return out

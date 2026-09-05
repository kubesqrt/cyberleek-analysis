"""SQLite store for positions / watches and their invalidation monitors; evaluated on every scan."""
import json, os, sqlite3, time, datetime as dt
from . import config as C

def _db():
    os.makedirs(C.DATA_DIR, exist_ok=True)
    con = sqlite3.connect(C.DB_PATH); con.row_factory = sqlite3.Row
    con.executescript("""CREATE TABLE IF NOT EXISTS positions(id INTEGER PRIMARY KEY, sym TEXT, chain TEXT, address TEXT, kind TEXT, entry_date TEXT, entry_px REAL, peak_px REAL, size_usd REAL, sleeve TEXT,
                         entry_rev30 REAL, entry_liq REAL, entry_chain_fees7 REAL, wave TEXT, thesis TEXT, status TEXT DEFAULT 'open', tx TEXT, closed_date TEXT, exit_px REAL, note TEXT);
                         CREATE TABLE IF NOT EXISTS monitors(id INTEGER PRIMARY KEY, position_id INTEGER, kind TEXT, label TEXT, threshold REAL, state TEXT DEFAULT 'ok', last_value TEXT, fired_at TEXT);
                         CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY, ts TEXT, sym TEXT, kind TEXT, text TEXT);
                         CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY, ts TEXT, asof TEXT, payload TEXT);""")
    return con

def add_position(sig, kind, size_usd, entry_px, chain, address, thesis_card, pool=None, wave=None, chain_fees7=None, tx=None):
    con = _db()
    cur = con.execute("INSERT INTO positions(sym,chain,address,kind,entry_date,entry_px,peak_px,size_usd,sleeve,entry_rev30,entry_liq,entry_chain_fees7,wave,thesis,tx) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (sig["sym"], chain, address, kind, sig["date"], entry_px, entry_px, size_usd, "early" if sig.get("young") else "established", sig.get("rev30"), (pool or {}).get("liquidity_usd"), chain_fees7, wave, json.dumps(thesis_card, default=str), tx))
    pid = cur.lastrowid
    for r in thesis_card.get("invalidation", []):
        con.execute("INSERT INTO monitors(position_id,kind,label,threshold) VALUES(?,?,?,?)", (pid, r["kind"], r["label"], r.get("threshold")))
    con.commit(); return pid

def close_position(pid, exit_px=None, note=None):
    con = _db(); con.execute("UPDATE positions SET status='closed', closed_date=?, exit_px=?, note=? WHERE id=?", (str(dt.date.today()), exit_px, note, pid)); con.commit()

def positions(status="open"):
    con = _db(); return [dict(r) for r in con.execute("SELECT * FROM positions WHERE status=? ORDER BY id", (status,))]

def monitors(pid=None):
    con = _db(); q = "SELECT m.*, p.sym FROM monitors m JOIN positions p ON p.id=m.position_id WHERE p.status='open'" + (" AND position_id=?" if pid else "")
    return [dict(r) for r in con.execute(q, (pid,) if pid else ())]

def log_alert(sym, kind, text):
    con = _db(); con.execute("INSERT INTO alerts(ts,sym,kind,text) VALUES(?,?,?,?)", (dt.datetime.utcnow().isoformat(), sym, kind, text)); con.commit()

def save_scan(asof, payload):
    con = _db(); con.execute("INSERT INTO scans(ts,asof,payload) VALUES(?,?,?)", (dt.datetime.utcnow().isoformat(), asof, json.dumps(payload, default=str))); con.commit()

def last_scan():
    con = _db(); r = con.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 1").fetchone()
    return (r["asof"], json.loads(r["payload"])) if r else (None, None)

def evaluate(panel, pool_lookup=None, safety_lookup=None, chain_fees_lookup=None):
    """Check every monitor of every open position against current data. Returns list of (position, monitor, message)."""
    con = _db(); t = panel.asof(); fired = []
    for p in positions("open"):
        c = p["sym"]
        if c not in panel.REV.columns: continue
        px = float(panel.PX[c].ffill().at[t]); peak = max(p["peak_px"] or 0, px)
        con.execute("UPDATE positions SET peak_px=? WHERE id=?", (peak, p["id"]))
        rev7 = float(panel.rev7.at[t, c]); rev30 = float(panel.rev30.at[t, c]); avg4 = float(panel.rev7.shift(1).rolling(28, min_periods=7).mean().at[t, c])
        peak90 = float(panel.rev30[c][t - __import__("pandas").Timedelta(days=90): t].max())
        for m in con.execute("SELECT * FROM monitors WHERE position_id=?", (p["id"],)).fetchall():
            m = dict(m); hit, value = False, None
            if m["kind"] == "rev_slowdown": hit = bool(panel.slow_exit.at[t, c]); value = f"rev7 ${rev7/1e3:,.0f}k vs 4wk avg ${avg4/1e3:,.0f}k"
            elif m["kind"] == "rev_collapse": hit = peak90 > 0 and rev30 < (m["threshold"] or 0.5) * peak90; value = f"rev30 ${rev30/1e3:,.0f}k vs 90d peak ${peak90/1e3:,.0f}k"
            elif m["kind"] == "price_stop": hit = px < peak * (1 - (m["threshold"] or 0.25)); value = f"px {px:.4g} vs peak {peak:.4g} ({px/peak-1:+.0%})"
            elif m["kind"] == "liquidity" and pool_lookup:
                pool = pool_lookup(p); 
                if pool: hit = (p["entry_liq"] and pool["liquidity_usd"] < (m["threshold"] or 0.5) * p["entry_liq"]) or pool["vol24h"] < C.MIN_VOL30 / 2; value = f"liq ${pool['liquidity_usd']/1e3:,.0f}k vol24h ${pool['vol24h']/1e3:,.0f}k"
            elif m["kind"] == "contract" and safety_lookup:
                s = safety_lookup(p); hit = bool(s and s["verdict"] == "FAIL"); value = (s or {}).get("verdict")
            elif m["kind"] == "chain_wave" and chain_fees_lookup and p["wave"]:
                f7 = chain_fees_lookup(p["wave"]); hit = bool(p["entry_chain_fees7"] and f7 is not None and f7 < (m["threshold"] or 0.4) * p["entry_chain_fees7"]); value = f"chain fees 7d ${(f7 or 0)/1e6:,.1f}M vs entry ${(p['entry_chain_fees7'] or 0)/1e6:,.1f}M"
            new_state = "fired" if hit else "ok"
            if new_state == "fired" and m["state"] != "fired":
                fired.append((p, m, value)); con.execute("UPDATE monitors SET state='fired', fired_at=?, last_value=? WHERE id=?", (dt.datetime.utcnow().isoformat(), value, m["id"]))
            else: con.execute("UPDATE monitors SET state=?, last_value=? WHERE id=?", (new_state, value, m["id"]))
    con.commit(); return fired

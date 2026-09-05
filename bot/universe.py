"""Universe = protocols on DeFiLlama with a token and material revenue; token contract mapping via CoinGecko."""
import json, os, re, time
from . import config as C, data as D

U_PATH = os.path.join(C.DATA_DIR, "universe.json")

def build(min_r30=C.MIN_REV30, min_r1y=500_000, force=False):
    if not force and os.path.exists(U_PATH) and time.time() - os.path.getmtime(U_PATH) < 20 * 3600:
        return json.load(open(U_PATH))
    rev = D.llama_overview("dailyRevenue"); lite = D.llama_lite()
    pp = {p["id"]: p for p in lite["parentProtocols"]}
    slug = lambda n: re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")
    byslug = {slug(p["name"]): p for p in lite["protocols"]}
    ent = {}
    for p in rev["protocols"]:
        if p.get("protocolType") == "chain": continue
        par = p.get("parentProtocol"); key = par or "solo#" + p["slug"]; lp = byslug.get(p["slug"])
        e = ent.setdefault(key, {"key": key, "name": pp[par]["name"] if par in pp else p["name"],
                                 "gecko": (pp[par].get("gecko_id") if par in pp else (lp or {}).get("gecko_id")),
                                 "symbol": (pp[par].get("symbol") if par in pp else (lp or {}).get("symbol")),
                                 "slugs": [], "r1y": 0, "rall": 0, "r30": 0, "chains": set(), "category": p.get("category")})
        e["slugs"].append(p["slug"]); e["r1y"] += p.get("total1y") or 0; e["rall"] += p.get("totalAllTime") or 0; e["r30"] += p.get("total30d") or 0
        for c in (p.get("chains") or []): e["chains"].add(c)
    U = []
    for e in ent.values():
        if not e["gecko"] or e["gecko"] == "-": continue
        if e["r30"] >= min_r30 or e["r1y"] >= min_r1y or e["rall"] >= 2_000_000:
            e["chains"] = sorted(e["chains"]); sym = (e["symbol"] or "").strip()
            e["symbol"] = (sym if sym and sym != "-" else re.sub(r"[^A-Za-z0-9]", "", e["name"])).upper(); U.append(e)
    U.sort(key=lambda e: -e["r30"])
    os.makedirs(C.DATA_DIR, exist_ok=True); json.dump(U, open(U_PATH, "w"))
    return U

def find(U, sym_or_name):
    s = sym_or_name.strip().lower()
    for e in U:
        if e["symbol"].lower() == s or e["gecko"].lower() == s or e["name"].lower() == s: return e
    for e in U:
        if s in e["name"].lower(): return e
    return None

def contracts(gecko_id):
    """{DeFiLlama chain name: contract address} for the token, from CoinGecko platforms."""
    c = D.cg_coin(gecko_id) or {}
    out = {}
    for plat, addr in (c.get("platforms") or {}).items():
        ch = C.CG_PLATFORMS.get(plat)
        if ch: out[ch] = addr
    return out, c

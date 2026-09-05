"""Thin clients for DeFiLlama, CoinGecko, DexScreener, GoPlus and LI.FI with retries and a small disk cache."""
import json, os, time, hashlib, urllib.request, urllib.parse, urllib.error
from . import config as C

H = {"User-Agent": "Mozilla/5.0 (revenue-bot)", "Accept": "application/json"}
os.makedirs(os.path.join(C.DATA_DIR, "cache"), exist_ok=True)

def get(url, ttl=0, headers=None, timeout=60, retries=3, sleep=1.5):
    """GET JSON with retries. ttl>0 caches the parsed body on disk for that many seconds."""
    key = os.path.join(C.DATA_DIR, "cache", hashlib.sha1(url.encode()).hexdigest() + ".json")
    if ttl and os.path.exists(key) and time.time() - os.path.getmtime(key) < ttl:
        return json.load(open(key))
    err = None
    for k in range(retries):
        try:
            req = urllib.request.Request(url, headers={**H, **(headers or {})})
            body = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            if ttl: json.dump(body, open(key, "w"))
            return body
        except urllib.error.HTTPError as e:
            err = e
            if e.code == 429: time.sleep(sleep * 4 * (k + 1)); continue
            if e.code == 404: return None
            time.sleep(sleep * (k + 1))
        except Exception as e:
            err = e; time.sleep(sleep * (k + 1))
    raise RuntimeError(f"GET failed {url}: {err}")

# ---------------- DeFiLlama
def llama_overview(data_type="dailyRevenue"):
    return get(f"https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType={data_type}", ttl=6 * 3600)

def llama_lite():
    return get("https://api.llama.fi/lite/protocols2?b=2", ttl=6 * 3600)

def llama_summary(slug, data_type="dailyRevenue", ttl=12 * 3600):
    """Daily series plus per-chain / per-product breakdown for one protocol slug."""
    d = get(f"https://api.llama.fi/summary/fees/{urllib.parse.quote(slug)}?dataType={data_type}", ttl=ttl)
    if not d: return None
    return {"chart": d.get("totalDataChart") or [], "breakdown": d.get("totalDataChartBreakdown") or [], "chains": d.get("chains") or [],
            "category": d.get("category"), "gecko_id": d.get("gecko_id"), "name": d.get("name"), "total30d": d.get("total30d")}

def llama_chain_fees(chain, ttl=12 * 3600):
    d = get(f"https://api.llama.fi/overview/fees/{urllib.parse.quote(chain)}?excludeTotalDataChartBreakdown=true&dataType=dailyFees", ttl=ttl)
    return (d or {}).get("totalDataChart") or []

def llama_prices(gecko_id, days=760):
    """Daily closes via coins.llama.fi (no key, 500 points per call)."""
    now = int(time.time()); pts = {}
    for start in range(now - days * 86400, now, 380 * 86400):
        d = get(f"https://coins.llama.fi/chart/coingecko:{gecko_id}?start={start}&span=380&period=1d", ttl=6 * 3600)
        for p in ((d or {}).get("coins", {}).get(f"coingecko:{gecko_id}", {}).get("prices") or []): pts[p["timestamp"]] = p["price"]
    return sorted(pts.items())

# ---------------- CoinGecko
def _cg(url):
    h = {"x-cg-demo-api-key": C.CG_API_KEY} if C.CG_API_KEY else {}
    return get(url, headers=h, ttl=3600, sleep=3)

def cg_markets(ids):
    out = {}
    ids = list(dict.fromkeys(i for i in ids if i))
    for i in range(0, len(ids), 150):
        chunk = ",".join(ids[i:i + 150])
        for row in _cg(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={chunk}&per_page=250&page=1") or []:
            out[row["id"]] = {"price": row.get("current_price"), "mcap": row.get("market_cap"), "fdv": row.get("fully_diluted_valuation"), "vol24h": row.get("total_volume"),
                              "ath": row.get("ath"), "ath_date": row.get("ath_date"), "circ": row.get("circulating_supply"), "total": row.get("total_supply"), "max": row.get("max_supply")}
        time.sleep(2.5)
    return out

def cg_coin(gecko_id):
    d = _cg(f"https://api.coingecko.com/api/v3/coins/{gecko_id}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=false")
    if not d: return None
    md = d.get("market_data") or {}
    return {"id": d["id"], "symbol": (d.get("symbol") or "").upper(), "name": d.get("name"), "platforms": {k: v for k, v in (d.get("platforms") or {}).items() if v},
            "genesis": d.get("genesis_date"), "mcap": md.get("market_cap", {}).get("usd"), "fdv": md.get("fully_diluted_valuation", {}).get("usd"),
            "vol24h": md.get("total_volume", {}).get("usd"), "price": md.get("current_price", {}).get("usd"), "ath": md.get("ath", {}).get("usd"), "ath_date": md.get("ath_date", {}).get("usd")}

def cg_volume_history(gecko_id, days=90):
    d = _cg(f"https://api.coingecko.com/api/v3/coins/{gecko_id}/market_chart?vs_currency=usd&days={days}")
    return [(int(t) // 1000, v) for t, v in ((d or {}).get("total_volumes") or []) if v is not None]

# ---------------- DexScreener
def dex_pairs_for_token(chain_slug, address):
    d = get(f"https://api.dexscreener.com/token-pairs/v1/{chain_slug}/{address}", ttl=900)
    return d if isinstance(d, list) else ((d or {}).get("pairs") or [])

def dex_search(query):
    return ((get(f"https://api.dexscreener.com/latest/dex/search?q={urllib.parse.quote(query)}", ttl=900) or {}).get("pairs") or [])

def best_pool(pairs, symbol=None):
    ps = [p for p in pairs if not symbol or (p.get("baseToken", {}).get("symbol", "").upper() == symbol.upper())]
    ps = ps or pairs
    ps = sorted(ps, key=lambda p: -float((p.get("liquidity") or {}).get("usd") or 0))
    if not ps: return None
    p = ps[0]
    return {"chain": p.get("chainId"), "dex": p.get("dexId"), "pair": p.get("pairAddress"), "base": p.get("baseToken", {}).get("address"), "quote": p.get("quoteToken", {}).get("symbol"),
            "liquidity_usd": float((p.get("liquidity") or {}).get("usd") or 0), "vol24h": float((p.get("volume") or {}).get("h24") or 0), "price_usd": float(p.get("priceUsd") or 0),
            "created": (p.get("pairCreatedAt") or 0) / 1000, "n_pools": len(ps), "total_liq": sum(float((q.get("liquidity") or {}).get("usd") or 0) for q in ps), "url": p.get("url")}

# ---------------- GoPlus token security
def goplus(chain_id, address):
    if chain_id == "solana":
        d = get(f"https://api.gopluslabs.io/api/v1/solana/token_security?contract_addresses={address}", ttl=3600)
        return ((d or {}).get("result") or {}).get(address)
    d = get(f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={address}", ttl=3600)
    res = (d or {}).get("result") or {}
    return res.get(address.lower()) or res.get(address)

# ---------------- LI.FI (bridging + swaps, one quote)
def lifi_quote(from_chain, to_chain, from_token, to_token, from_address, from_amount_wei, slippage=0.01):
    q = urllib.parse.urlencode({"fromChain": from_chain, "toChain": to_chain, "fromToken": from_token, "toToken": to_token, "fromAddress": from_address,
                                "fromAmount": str(from_amount_wei), "slippage": slippage, "order": "RECOMMENDED"})
    return get(f"https://li.quest/v1/quote?{q}", retries=2)

def lifi_token(chain, token):
    return get(f"https://li.quest/v1/token?chain={chain}&token={urllib.parse.quote(token)}", ttl=6 * 3600, retries=2)

def lifi_chains():
    return ((get("https://li.quest/v1/chains", ttl=24 * 3600) or {}).get("chains") or [])

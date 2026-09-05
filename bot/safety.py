"""Scam / tradability checks: GoPlus token security + DexScreener pool facts -> PASS / WARN / FAIL / UNVERIFIED."""
import time
from . import config as C, data as D

def _f(v, default=0.0):
    try: return float(v)
    except Exception: return default

def check(sym, chain_name, address, pool=None):
    chain_id = C.CHAIN_IDS.get(chain_name)
    hard, warn, info = [], [], []
    g = None
    if chain_id and address:
        try: g = D.goplus(chain_id, address)
        except Exception as e: info.append(f"GoPlus unavailable: {e}")
    taxes = (None, None); top10 = None; lp_locked = None
    if g:
        if chain_id == "solana":
            if (g.get("mintable") or {}).get("status") == "1": warn.append("mint authority still active")
            if (g.get("freezable") or {}).get("status") == "1": warn.append("freeze authority active (can freeze your tokens)")
            if (g.get("transfer_fee") or {}).get("status") == "1": warn.append("transfer fee enabled")
            if g.get("closable", {}).get("status") == "1": hard.append("token account closable by authority")
            hs = g.get("holders") or []; top10 = sum(_f(h.get("percent")) for h in hs[:10]) * (100 if hs and _f(hs[0].get("percent")) <= 1 else 1)
        else:
            if g.get("is_honeypot") == "1": hard.append("honeypot: cannot sell")
            if g.get("cannot_sell_all") == "1": hard.append("cannot sell all tokens")
            if g.get("cannot_buy") == "1": hard.append("buying restricted")
            bt, st = _f(g.get("buy_tax")), _f(g.get("sell_tax")); taxes = (bt, st)
            if st > C.MAX_SELL_TAX: hard.append(f"sell tax {st:.0%}")
            elif st > 0.03: warn.append(f"sell tax {st:.0%}")
            if bt > C.MAX_BUY_TAX: hard.append(f"buy tax {bt:.0%}")
            if g.get("owner_change_balance") == "1": hard.append("owner can change balances")
            if g.get("selfdestruct") == "1": hard.append("contract has selfdestruct")
            if g.get("is_open_source") == "0": hard.append("contract not verified")
            if g.get("hidden_owner") == "1": warn.append("hidden owner")
            if g.get("can_take_back_ownership") == "1": warn.append("ownership can be taken back")
            if g.get("is_mintable") == "1": warn.append("mintable")
            if g.get("is_proxy") == "1": warn.append("upgradeable proxy")
            if g.get("transfer_pausable") == "1": warn.append("transfers pausable")
            if g.get("is_blacklisted") == "1": warn.append("blacklist function")
            if g.get("trading_cooldown") == "1": warn.append("trading cooldown")
            if g.get("is_anti_whale") == "1": info.append("anti-whale limits")
            hs = g.get("holders") or []; top10 = sum(_f(h.get("percent")) for h in hs[:10]) * 100
            cp = _f(g.get("creator_percent")) * 100; op = _f(g.get("owner_percent")) * 100
            if cp >= 20: warn.append(f"creator holds {cp:.0f}%")
            if op >= 20: warn.append(f"owner holds {op:.0f}%")
            lps = g.get("lp_holders") or []
            if lps:
                lp_locked = sum(_f(l.get("percent")) for l in lps if str(l.get("is_locked")) == "1") * 100
                cl = (pool or {}).get("dex") in ("uniswap", "aerodrome", "velodrome", "pancakeswap", "raydium", "orca", "shadow", "ramses", "pharaoh", "kittenswap")
                if lp_locked < 50 and g.get("is_in_dex") == "1": (info if cl else warn).append(f"{lp_locked:.0f}% of LP locked" + (" (concentrated-liquidity DEX: positions are NFTs, lock data not meaningful)" if cl else ""))
            info.append(f"holders {g.get('holder_count', '?')}")
        if top10 is not None and top10 >= 50: warn.append(f"top-10 holders {top10:.0f}%")
    else:
        info.append("no GoPlus data (chain unsupported or token not indexed)")
    if pool:
        if pool["liquidity_usd"] < C.MIN_POOL_LIQ: warn.append(f"thin pool: ${pool['liquidity_usd']/1e3:,.0f}k liquidity in the best pool")
        if pool.get("created") and (time.time() - pool["created"]) < 7 * 86400: warn.append("main pool is under 7 days old")
        info.append(f"best pool {pool['dex']} on {pool['chain']}: ${pool['liquidity_usd']/1e3:,.0f}k liquidity, ${pool['vol24h']/1e3:,.0f}k 24h volume, {pool['n_pools']} pools")
    score = max(0, 100 - 100 * bool(hard) - 12 * len(warn))
    verdict = "FAIL" if hard else ("WARN" if warn else ("PASS" if g else "UNVERIFIED"))
    return {"sym": sym, "chain": chain_name, "address": address, "verdict": verdict, "score": score, "hard": hard, "warn": warn, "info": info, "taxes": taxes, "top10_pct": top10, "lp_locked_pct": lp_locked, "goplus": bool(g)}

def token_location(entity):
    """Pick the chain/contract with the deepest pool. Returns (chain_name, address, pool, contracts)."""
    from . import universe as UV
    contracts, coin = UV.contracts(entity["gecko"])
    best = None
    for chain, addr in contracts.items():
        slug = {"Ethereum": "ethereum", "Arbitrum": "arbitrum", "Base": "base", "Robinhood Chain": "robinhood", "HyperEVM": "hyperevm", "Optimism": "optimism", "BSC": "bsc", "Polygon": "polygon", "Avalanche": "avalanche", "Sonic": "sonic", "Solana": "solana"}.get(chain)
        if not slug: continue
        try: pool = D.best_pool(D.dex_pairs_for_token(slug, addr), entity["symbol"])
        except Exception: pool = None
        if pool and (best is None or pool["liquidity_usd"] > best[2]["liquidity_usd"]): best = (chain, addr, pool)
    if best is None and contracts:
        chain, addr = next(iter(contracts.items())); return chain, addr, None, contracts
    if best is None:
        pool = D.best_pool(D.dex_search(entity["symbol"]), entity["symbol"])
        return (None, None, pool, contracts)
    return best[0], best[1], best[2], contracts

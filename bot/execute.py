"""Execution planner. Builds a bridge+swap route with LI.FI, checks liquidity and price impact, and (only when
LIVE_TRADING=1 and a key is configured) signs and sends it. Default is a dry-run plan you can read before confirming."""
import time
from . import config as C, data as D, safety as S

ERC20_ABI = [{"constant": True, "inputs": [{"name": "o", "type": "address"}, {"name": "s", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
             {"constant": False, "inputs": [{"name": "s", "type": "address"}, {"name": "a", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
             {"constant": True, "inputs": [{"name": "o", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]

def _steps(q):
    out = []
    for s in (q.get("includedSteps") or [q]):
        a = s.get("action", {}); out.append({"type": s.get("type"), "tool": s.get("toolDetails", {}).get("name") or s.get("tool"), "from_chain": a.get("fromChainId"), "to_chain": a.get("toChainId"),
                                              "from": a.get("fromToken", {}).get("symbol"), "to": a.get("toToken", {}).get("symbol")})
    return out

def plan_buy(entity, usd, from_chain=None, from_token=None, wallet=None, spot_price=None):
    from_chain = from_chain or C.DEFAULT_FROM_CHAIN; from_token = (from_token or C.DEFAULT_FROM_TOKEN).upper(); wallet = wallet or C.WALLET_ADDRESS
    plan = {"sym": entity["symbol"], "usd": usd, "ok": False, "warnings": [], "errors": [], "steps": [], "created": time.time()}
    chain_name, addr, pool, contracts = S.token_location(entity)
    plan.update({"to_chain_name": chain_name, "token": addr, "pool": pool, "contracts": contracts})
    if not chain_name or not addr: plan["errors"].append("no contract found for this token on a supported chain"); return plan
    to_chain = C.CHAIN_IDS.get(chain_name)
    if not isinstance(to_chain, int): plan["errors"].append(f"{chain_name} is not an EVM chain LI.FI can route to from here; buy manually"); return plan
    if usd > C.MAX_TRADE_USD: plan["errors"].append(f"trade ${usd:,.0f} exceeds MAX_TRADE_USD ${C.MAX_TRADE_USD:,.0f}")
    if pool:
        if pool["liquidity_usd"] < C.MIN_POOL_LIQ: plan["warnings"].append(f"thin pool: ${pool['liquidity_usd']/1e3:,.0f}k")
        if usd > C.MAX_TRADE_SHARE_OF_LIQ * pool["liquidity_usd"]: plan["errors"].append(f"trade is {usd/pool['liquidity_usd']:.1%} of pool liquidity (limit {C.MAX_TRADE_SHARE_OF_LIQ:.0%})")
        if pool["vol24h"] and usd > 0.1 * pool["vol24h"]: plan["warnings"].append(f"trade is {usd/pool['vol24h']:.0%} of 24h volume")
    src = (C.STABLES.get(from_chain) or {}).get(from_token)
    if not src: plan["errors"].append(f"no {from_token} address configured for chain {from_chain}"); return plan
    amount = int(round(usd * 10 ** 6))
    try: q = D.lifi_quote(from_chain, to_chain, src, addr, wallet, amount)
    except Exception as e: plan["errors"].append(f"LI.FI quote failed: {e}"); return plan
    if not q or "estimate" not in q: plan["errors"].append(f"LI.FI returned no route: {str(q)[:200]}"); return plan
    est = q["estimate"]; dec = int(q.get("action", {}).get("toToken", {}).get("decimals", 18))
    out_amt = int(est.get("toAmount", 0)) / 10 ** dec; min_amt = int(est.get("toAmountMin", 0)) / 10 ** dec
    gas = sum(float(g.get("amountUSD") or 0) for g in est.get("gasCosts") or []); fees = sum(float(f.get("amountUSD") or 0) for f in est.get("feeCosts") or [])
    eff_price = usd / out_amt if out_amt else None
    spot = spot_price or (pool or {}).get("price_usd")
    impact = (eff_price / spot - 1) if (eff_price and spot) else None
    if impact is not None and impact > C.MAX_PRICE_IMPACT: plan["errors"].append(f"price impact {impact:.1%} exceeds {C.MAX_PRICE_IMPACT:.0%}")
    plan.update({"from_chain": from_chain, "to_chain": to_chain, "from_token": from_token, "src": src, "amount_wei": amount, "tokens_out": out_amt, "tokens_min": min_amt, "eff_price": eff_price, "spot_price": spot, "impact": impact,
                 "gas_usd": gas, "fees_usd": fees, "duration_s": est.get("executionDuration"), "tool": q.get("toolDetails", {}).get("name") or q.get("tool"), "steps": _steps(q),
                 "approval_address": est.get("approvalAddress"), "tx": q.get("transactionRequest"), "quote_id": q.get("id")})
    plan["ok"] = not plan["errors"]; return plan

def plan_sell(entity, fraction=1.0, to_chain=None, to_token=None, wallet=None):
    """Sell on the token's own chain into a stablecoin there (bridge back separately if you want)."""
    wallet = wallet or C.WALLET_ADDRESS
    plan = {"sym": entity["symbol"], "ok": False, "warnings": [], "errors": [], "steps": []}
    chain_name, addr, pool, contracts = S.token_location(entity); plan.update({"to_chain_name": chain_name, "token": addr, "pool": pool})
    cid = C.CHAIN_IDS.get(chain_name)
    if not isinstance(cid, int): plan["errors"].append("non-EVM chain; sell manually"); return plan
    dst_chain = to_chain or cid; dst = (C.STABLES.get(dst_chain) or {}).get((to_token or "USDC").upper()) or next(iter((C.STABLES.get(dst_chain) or {}).values()), None)
    if not dst: plan["errors"].append(f"no stablecoin configured on chain {dst_chain}"); return plan
    bal = None
    if C.WALLET_PRIVATE_KEY:
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(C.RPC_URLS[cid])); tok = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=ERC20_ABI); bal = tok.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
        except Exception as e: plan["warnings"].append(f"balance lookup failed: {e}")
    if bal is None: plan["errors"].append("wallet balance unknown (no key/RPC); cannot size the sell"); return plan
    amount = int(bal * fraction)
    try: q = D.lifi_quote(cid, dst_chain, addr, dst, wallet, amount)
    except Exception as e: plan["errors"].append(f"LI.FI quote failed: {e}"); return plan
    if not q or "estimate" not in q: plan["errors"].append("no route"); return plan
    est = q["estimate"]; plan.update({"from_chain": cid, "to_chain": dst_chain, "src": addr, "amount_wei": amount, "usd_out": float(est.get("toAmountUSD") or 0), "tokens_min": int(est.get("toAmountMin", 0)) / 10 ** 6,
                                     "steps": _steps(q), "approval_address": est.get("approvalAddress"), "tx": q.get("transactionRequest")}); plan["ok"] = True; return plan

def execute(plan):
    """Sign and send. Refuses unless LIVE_TRADING=1 and a private key is set. Returns tx hashes."""
    if not (C.LIVE_TRADING and C.WALLET_PRIVATE_KEY): return {"sent": False, "reason": "LIVE_TRADING is off or no WALLET_PRIVATE_KEY; this was a dry run"}
    if not plan.get("ok") or not plan.get("tx"): return {"sent": False, "reason": "plan not executable: " + "; ".join(plan.get("errors") or ["no tx"])}
    if time.time() - plan.get("created", 0) > 120: return {"sent": False, "reason": "quote older than 2 minutes; re-plan"}
    from web3 import Web3
    from eth_account import Account
    acct = Account.from_key(C.WALLET_PRIVATE_KEY); w3 = Web3(Web3.HTTPProvider(C.RPC_URLS[plan["from_chain"]])); hashes = []
    src = plan["src"]
    if src.lower() != C.NATIVE:
        tok = w3.eth.contract(address=Web3.to_checksum_address(src), abi=ERC20_ABI); spender = Web3.to_checksum_address(plan["approval_address"])
        if tok.functions.allowance(acct.address, spender).call() < plan["amount_wei"]:
            tx = tok.functions.approve(spender, plan["amount_wei"]).build_transaction({"from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address), "chainId": plan["from_chain"]})
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.2); h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction); w3.eth.wait_for_transaction_receipt(h, timeout=180); hashes.append(("approve", h.hex()))
    t = plan["tx"]; tx = {"from": acct.address, "to": Web3.to_checksum_address(t["to"]), "data": t["data"], "value": int(t.get("value", "0x0"), 16) if isinstance(t.get("value"), str) else int(t.get("value") or 0),
                          "chainId": plan["from_chain"], "nonce": w3.eth.get_transaction_count(acct.address)}
    tx["gas"] = int(t["gasLimit"], 16) if isinstance(t.get("gasLimit"), str) else int(w3.eth.estimate_gas(tx) * 1.2)
    if t.get("gasPrice"): tx["gasPrice"] = int(t["gasPrice"], 16) if isinstance(t["gasPrice"], str) else int(t["gasPrice"])
    h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction); hashes.append(("swap/bridge", h.hex()))
    return {"sent": True, "hashes": hashes}

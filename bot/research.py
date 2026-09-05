"""Catalyst / thesis / invalidation research. Uses the Claude API with server-side web search when ANTHROPIC_API_KEY is set;
otherwise returns a data-only card with the links a human would open."""
import json, re, datetime as dt
from . import config as C

TAXONOMY = "product_launch | incentives | token_event | market_volatility | ecosystem_wave | one_off | organic_growth | unknown"

def _prompt(card):
    return f"""Today is {dt.date.today()}. A DeFi protocol's on-chain revenue (DeFiLlama) just triggered our breakout rule. Research WHY, then judge it.

DATA CARD (JSON):
{json.dumps(card, default=str)}

Tasks:
1. Find the catalyst for the revenue jump in the week ending {card.get('date')}: what happened, on what date. Use web search (news, the protocol's X/blog, DeFiLlama, Dune, CoinMarketCap updates). Be specific and factual; if nothing is found, say so.
2. Classify it as exactly one of: {TAXONOMY}. Note that market_volatility (a market-wide liquidation cascade or squeeze) and one_off (single-day fee, accounting artifact, monthly distribution, exploit) usually do not persist.
3. State the investment thesis in 3 bullets a busy person can digest, and who the first-order beneficiary of the driver is (this token, or another one).
4. List 3 things that must stay true for the thesis, each with a measurable check.
5. List 3-5 invalidation triggers with concrete thresholds (revenue, share, price, liquidity, chain volume, token unlocks, governance).
6. Scam / structural risk flags: team, unlocks, insiders, contract, wash trading, incentive-driven volume, liquidity provenance.
7. Confidence (high/medium/low) and 2-4 source URLs.

Return ONLY a JSON object with keys: catalyst (<=60 words), type, beneficiary, thesis (list of 3 strings), must_stay_true (list of 3 strings), invalidation (list of objects {{"signal","threshold"}}), risks (list of strings), confidence, sources (list of URLs)."""

def fallback(card):
    sym = card.get("sym", ""); name = card.get("name", sym); g = card.get("gecko", "")
    return {"catalyst": "No research key configured; data-only view.", "type": "unknown", "beneficiary": None,
            "thesis": [f"Revenue 7d ${card.get('rev7', 0)/1e3:,.0f}k is {card.get('ratio') or 0:.1f}x its 8-week baseline.", f"Signature: one-day share {card.get('one_day_share') or 0:.0%}, breadth {card.get('breadth') or 0:.0%}, rising days {card.get('rising_days')}.", "Open the links below to identify the driver."],
            "must_stay_true": ["Weekly revenue holds above its 4-week average", "Revenue comes from the product, not a one-off", "Token receives the revenue (buybacks / fee switch)"],
            "invalidation": [{"signal": "7d revenue", "threshold": "below 4-week average"}, {"signal": "30d revenue", "threshold": "below 50% of 90-day peak"}, {"signal": "price", "threshold": f"{int(card.get('stop', 0.25)*100)}% below peak since entry"}],
            "risks": ["not researched"], "confidence": "low",
            "sources": [f"https://defillama.com/protocol/{(card.get('slugs') or [g])[0]}", f"https://www.coingecko.com/en/coins/{g}", f"https://x.com/search?q={name}&f=live", f"https://dexscreener.com/search?q={sym}"]}

def research(card):
    if not C.ANTHROPIC_API_KEY: return fallback(card)
    import anthropic
    client = anthropic.Anthropic(api_key=C.ANTHROPIC_API_KEY)
    resp = client.messages.create(model=C.ANTHROPIC_MODEL, max_tokens=2500, tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
                                  messages=[{"role": "user", "content": _prompt(card)}])
    text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    if not m: return {**fallback(card), "catalyst": text[:400], "confidence": "low"}
    try: out = json.loads(m.group(0))
    except Exception: return {**fallback(card), "catalyst": text[:400], "confidence": "low"}
    out.setdefault("sources", []); out.setdefault("invalidation", []); out.setdefault("risks", []); return out

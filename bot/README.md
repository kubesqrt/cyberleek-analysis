# Revenue-breakout bot

Finds protocols whose on-chain revenue just broke out, filters the fake ones, researches the catalyst, writes a thesis with invalidation monitors, checks the token is not a scam, plans the buy (bridge + swap with liquidity and price-impact checks) and lets you confirm it from Telegram.

Everything the bot does is derived from the backtest work in `revenue/backtest/` and the Jun–Sep 2026 catalyst review.

## What it does, in order

1. **Universe** – every DeFiLlama protocol with a token and ≥ $100k of 30-day revenue (`universe.py`).
2. **Signals** (`signals.py`)
   - Established names (> 90 days of revenue): 7-day revenue ≥ 2× the mean of the prior 8 weekly windows **and** an 8-week high **and** price-to-revenue at or below its own 180-day median.
   - Early sleeve (token listed ≤ 90 days ago, ≥ 28 days of revenue): two consecutive rising revenue days and 7-day revenue ≥ 1.25× the 2-week average. The first day such a token qualifies is posted as **EARLY** (5% size, 50% stop, no revenue exit).
   - Catalyst-time filters (**REJECT**): ≥ 50% of the week's revenue on one day; a similar spike 25–35 days earlier (distribution schedule); > 25% zero-revenue days in the prior 8 weeks or a sub-product younger than 14 days carrying the week (adapter change). These removed 22 of 58 triggers in the last quarter whose trades averaged +1% against +19% for the rest.
   - **TRADE (beta)** when ≥ 35% of the universe spikes the same week: it is a market event, prefer leaders with capture and hold past the slowdown exit.
   - **WATCH** when the token fails the tradability gate ($500k/day volume, $10M cap) or has already re-rated.
3. **Chain waves** (`thesis.py`): several triggers on one chain, or chain fees doubling week on week, produce a basket: first-order beneficiaries (launchpads, DEXs, perps on that chain), revenue-share tokens (e.g. ARB books 10% of Robinhood Chain net revenue) and second-order names.
4. **Research** (`research.py`): with `ANTHROPIC_API_KEY` set, the Claude API with web search finds the catalyst, classifies it (product launch / incentives / token event / market volatility / ecosystem wave / one-off), writes a 3-bullet thesis, what must stay true, invalidation triggers with thresholds, and scam or structural risks. Without a key you get a data-only card with the links.
5. **Safety** (`safety.py`): GoPlus token security (honeypot, taxes, mint/pause/blacklist, ownership, holder and LP concentration) plus DexScreener pool depth and age → PASS / WARN / FAIL. A FAIL blocks `/buy`.
6. **Execution** (`execute.py`): LI.FI quote for stablecoin on your home chain → token on its chain (bridge + swap in one route, Robinhood Chain and HyperEVM supported). Refuses when the trade exceeds 5% of pool liquidity, price impact > 2%, or `MAX_TRADE_USD`. **Dry-run by default**: Confirm records a paper position and its monitors. Live sending needs `LIVE_TRADING=1` and `WALLET_PRIVATE_KEY`.
7. **Monitors** (`monitors.py`): every position or `/watch` gets invalidation monitors evaluated on each scan: revenue slowdown, revenue below 50% of 90-day peak, trailing stop (25% established, 50% early), liquidity halving, GoPlus turning FAIL, chain-wave fees below 40% of entry, unlock overhang note, plus the research-derived checks. Fired monitors are posted with the reading.

## Setup

```bash
pip install -r bot/requirements.txt
export TELEGRAM_BOT_TOKEN=...            # from @BotFather
export TELEGRAM_ALLOWED_CHATS=123456789   # your chat id(s), comma separated; the bot ignores everyone else
export ANTHROPIC_API_KEY=...             # optional, enables /research with web search
export COINGECKO_API_KEY=...             # optional demo key, fewer 429s
export DEFAULT_FROM_CHAIN=42161          # where your USDC sits (Arbitrum); DEFAULT_FROM_TOKEN=USDC
export WALLET_ADDRESS=0x...              # used for quotes; needed for /sell balances
# only when you are ready to let it send transactions:
# export LIVE_TRADING=1; export WALLET_PRIVATE_KEY=0x...; export MAX_TRADE_USD=2000
python -m bot.telegram_bot               # long-running; posts the daily scan at DAILY_HOUR_UTC (06:00)
```

Without Telegram: `python -m bot.run_scan --limit 80`, `--safety PONS`, `--research PONS`, `--plan PONS 200`, `--thesis`. Cron alternative: `python -m bot.scheduler` runs one daily pass and posts to Telegram if the token is set.

## Commands

| Command | What it does |
|---|---|
| `/scan` | refresh DeFiLlama revenue (with per-product breakdown), prices, market caps; scan; detect waves; evaluate monitors |
| `/alerts` | today's TRADE / beta / EARLY / WATCH cards |
| `/view SYM` | 14-day revenue sparkline, where the revenue comes from by product and chain, valuation, signature flags |
| `/research SYM` | catalyst, type, thesis, must-stay-true, invalidation, risks, sources |
| `/thesis` | chain waves and the basket that expresses each (first-order, revenue share, second-order) |
| `/safety SYM` | GoPlus + pool checks with the reasons |
| `/buy SYM USD [chain]` | safety check → route plan (steps, expected tokens, min out, effective vs spot price, impact, gas, time) → Confirm |
| `/sell SYM [fraction]` | route plan to a stablecoin on the token's chain → Confirm |
| `/watch SYM` | monitors without a position |
| `/positions` `/monitors` `/close ID` | bookkeeping |

## Keep in mind

- DeFiLlama revenue is only as good as its adapters; the filters catch most artifacts, not all. `/view` shows the product breakdown so you can see a single sub-product carrying the week.
- Market cap and FDV are current values; P/S history is a constant-supply proxy.
- The early sleeve is a lottery ticket by design: over the last six months it went 0-for-4 on everything except PONS.
- Chain waves are the setting where first-order beneficiaries worked and second-order names did not; the bot labels the role, you decide.
- Nothing here is investment advice. Keep `LIVE_TRADING` off until you have watched the dry-run plans for a while.

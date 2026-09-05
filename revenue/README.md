# Revenue vs Valuation dashboard

A CoinGecko-style screener that joins **protocol revenue** (DeFiLlama) with **token
market data** (CoinGecko) to answer one question: *does the token capture the cash
flow the protocol generates, and is it cheap or expensive against that revenue?*

Live page: `https://kubesqrt.github.io/cyberleek-analysis/revenue/`

## What it shows

Each row is a protocol (children like *Uniswap V1/V2/V3* are summed into the parent
**Uniswap**), with its token where one exists:

| Column | Meaning |
|---|---|
| Price / 7d % | token price and 7-day price change (CoinGecko) |
| Mcap / FDV | circulating market cap and fully-diluted valuation |
| Rev 30d | protocol **revenue** over the last 30 days — the take the protocol keeps (DeFiLlama `dailyRevenue`), not total user fees |
| Rev WoW | last 7d revenue vs the prior 7d |
| Rev MoM | last 30d revenue vs the prior 30d |
| vs 1y avg | last 30d vs the trailing-1-year monthly average (structural trend) |
| P/S | market cap ÷ annualized revenue (30d × 12.17) — lower = cheaper per revenue dollar |
| P/F | FDV ÷ annualized revenue — the fully-diluted version |
| Capture | share of revenue paid to token holders (burns, buybacks, staker/locker distributions) — the on-chain proxy for "does the token capture the revenue" |

Click any row for the daily-revenue chart (with a 7-day average) and extra facts
(annualized revenue, fees, holder revenue, Mcap/FDV dilution, 30d price change).

## Filters

- **Search** protocol or symbol
- **Category** (Dexs, Lending, Derivatives, Launchpad, …)
- **Revenue momentum**: weekly ↑, monthly ↑, both, *accelerating* (WoW > MoM > 0), or fading
- **Value capture**: token gets any revenue / ≥25% / ≥50% / none
- **Min 30d revenue** threshold
- **has token** — hide protocols with no traded token
- Every column is sortable (P/S and P/F sort ascending = cheapest first)

## How to read it

The interesting quadrant is **high & growing revenue + low P/S + high capture** — a
protocol making real money, whose token has a claim on it, priced cheaply against that
cash flow. The opposite (high P/S, 0% capture, fading revenue) is a token whose price
is disconnected from the business.

## Data & limitations

- 100% client-side; no build step, no keys. Data is fetched live on load and cached
  in your browser for 10 minutes.
- Revenue: DeFiLlama fee/revenue adapters. "Capture" depends on DeFiLlama's holders-
  revenue methodology, which not every protocol implements (shows 0% when unreported,
  which is not the same as "definitely zero").
- Market data: CoinGecko's public API (rate-limited; mcap falls back to DeFiLlama and
  FDV/price may be briefly missing under heavy load — hit ↻ refresh). FDV is null for
  tokens CoinGecko has no fully-diluted figure for.
- Chains (L1/L2 gas revenue) are excluded — this is a protocol/token view.
- Not investment advice; revenue adapters and token mappings can be wrong or lagged.
  Verify anything load-bearing on DeFiLlama / CoinGecko directly (row links provided).

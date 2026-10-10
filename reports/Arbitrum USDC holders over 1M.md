# Arbitrum protocols and venues holding more than $1M USDC

Snapshot date: 10 October 2026. Native USDC on Arbitrum One: ~2.67B on-chain supply (DefiLlama nets to ~$2.33B). USDC.e: $48M, wind-down asset.

Sources: DefiLlama per-protocol token breakdowns (`api.llama.fi/protocol/{slug}`, Arbitrum chain, latest day), DefiLlama yields pool list (pool TVL counts both sides of a pair), and on-chain reads / Arbiscan labels collected in `research_notes/USDG and stablecoin chain usage/arbitrum_usdc_holders.md`. Where DefiLlama and on-chain reads differ, both are shown.

## 1. Bridges and exchange custody (structurally USDC, low convertibility)

| Venue | USDC held ($M) | Note |
|---|---:|---|
| Hyperliquid Deposit Bridge 2 | 389 | Down from $5.1B (Oct 2025). Being deprecated for native CCTP mint. Not addressable. |
| Binance hot wallets | 272 to 360 | HW34 $272.5M labeled; ~$81M more in Binance-pattern proxies. DefiLlama: $279M. Needs a USDG-on-Arbitrum rail. |
| edgeX Bridge | 46 | Perp DEX deposit bridge. |
| TxFlow Bridge | 28 | Bridge custody. |
| Bybit | 28 | Exchange float. |
| BingX cold wallet | 22 | Arbiscan label. |
| Aster (bridge / treasury) | 18 | Perp DEX treasury. Candidate for a reserve-share deal. |
| LayerZero V2 (OFT lockboxes incl. Stargate) | 16 | Transit float. Already carries USDG. |
| Circle hot wallet | 11 | Issuer wallet. Skip. |
| Crypto.com | 11 | Exchange float. |
| Coinbase 83 | 10 | Circle-aligned. Skip. |
| KuCoin | 9 | Exchange float. |
| Bitget | 9 | Exchange float. Bitget already seeds Steakhouse vaults on Morpho. |
| NEAR Intents | 3 | Cross-chain settlement. |
| Gate | 3 | Exchange float. |
| Stargate V2 USDC pool | 1.5 | Already integrated with USDG. |
| Orderly Bridge | 1.3 | Perp DEX deposit bridge. |
| Reya Bridge | 1.3 | Canonical bridge of Reya L2. |
| Bitunix | 1.0 | Exchange float. |

## 2. Lending markets (highest priority: yield-sensitive, already integrating USDG)

| Protocol | USDC supplied ($M) | Of which borrowed ($M) | Note |
|---|---:|---:|---|
| Aave V3 Arbitrum | 180 | 161 | 89% utilisation, only $19M idle. USDG Direct-to-AIP listing posted 8 Oct 2026 (30M cap, non-collateral). |
| Fluid Lending | 55 to 71 | 65 | On-chain fUSDC 55.4M; DefiLlama 71M. Hosts the main USDG/USDC pool. |
| Compound V3 | 15 to 17 | 13 | cUSDCv3. |
| Morpho Blue | 6 | 6 | USDC vaults <$3M (BBQ USDC $2.4M, Bitget x Steakhouse USDC $1.5M) but USDG vaults already $16M. |
| Dolomite | 4 | 3 | Margin and GLV collateral. |

## 3. Perps and derivatives (USDC-margined; pitch GDN reserve share)

| Protocol | USDC held ($M) | Note |
|---|---:|---|
| GMX V2 GM pools | 65 to 85 | On-chain ~65M (BTC/USD 33M, ETH/USD 25M, SOL 4M, LINK 2M); DefiLlama 85M. GLV[USDG] vault live with 8-week boost. |
| Variational (OLP vault + treasury) | 37 | Not tracked by DefiLlama; on-chain read. |
| Gains Network gUSDC | 4 to 5 | USDC vault. |
| Ostium | 2 to 4 | USDC liquidity vault. |
| Apex Omni | 4 | Perp DEX. |
| Hegic | 3 | Options. |
| Aevo Perps | 1 | Perp DEX. |

## 4. DEX liquidity (pool TVL counts both sides; USDC share roughly half in volatile pairs)

| Protocol / pool | Pool TVL ($M) | Est. USDC ($M) | Note |
|---|---:|---:|---|
| Uniswap V3 WETH/USDC 0.05% | 35 | 14 | Largest USDC pool on Arbitrum. |
| Uniswap V3 WBTC/USDC | 8 | 4 | |
| Uniswap V3 WETH/USDC (second fee tier) | 5 | 3 | |
| Uniswap V3 USDC/USDT | 1.2 | 0.6 | |
| Uniswap V4 PoolManager (all pools) | 39 | 12 | ETH/USDC $8M, DORY/USDC $6M, WBTC/USDC $5M pools. Also holds $1M USDG. |
| Fluid DEX (all pools) | 35 | 15.5 | sUSDai/USDC $12M, USDC/USDT0 $12M, USDG/USDC $5M, USDai/USDC $4M, reUSD/USDC $3.5M. |
| Curve | 8 | 1.4 | sUSDai/USDC $1.4M, USDC/USDSM $1M. |
| PancakeSwap V3 | 7 | n/a | No token breakdown available. |
| Camelot V3 | 5 | <1 | PEAR/USDC $1.1M pool. |

## 5. Vaults, asset managers, RWA and yield

| Protocol | USDC held ($M) | Note |
|---|---:|---|
| Estate Protocol (RWA) | 14 | Tokenised real estate, USDC-denominated. |
| Spark Liquidity Layer (Sky PSM) | 10 | Structurally USDC. Skip. |
| D2 Finance | 9 | Options vaults. |
| Concrete | 9 | THUSD/USDC/ARB vault. |
| Lagoon | 7 | Vault infrastructure. |
| T3tris Finance | 7 | GAMI USDC vault. |
| Aera V3 | 5 | Treasury vaults (Gauntlet). |
| Steakhouse Financial vaults | 4 | Curator; already runs USDG Pro vault. |
| Radpie | 3 | Radiant yield. |
| Arrakis Modular | 2 | LP manager. |
| Beefy | 1.5 | Yield aggregator. |
| Gauntlet vaults | 1.4 | Curator; already runs USDG Premium vault. |
| Yield Yak | 1.2 | Yield aggregator. |
| DeFi Saver | 1.2 | Position manager. |
| Royco V1 | 1.2 | Incentive markets. |

Not USDC despite large stablecoin TVL: Pendle Arbitrum ($178M) is almost entirely sUSDai PT/YT; Spark Savings ($307M) is USDS/sUSDS; USD.AI ($346M) is USDai.

## 6. Unlabeled large holders

31 unlabeled addresses in the top 50 hold ~$364M combined, about $60M of it in round-number balances typical of treasuries or OTC desks. These are not attributable without Nansen or Arkham labels.

## Reading the list for USDG outreach

- Addressable DeFi USDC is roughly $440M: lending ~$250M, perps ~$110M, DEX ~$60M, vaults ~$20M.
- Lending (Aave, Fluid, Compound, Morpho) and GMX are the first targets; all four of the largest already have USDG hooks live or in governance.
- Variational, Aster, edgeX, Orderly and Apex are USDC-margined perp venues where a GDN reserve-share deal is the lever, as Coinbase did with Hyperliquid.
- Exchange float (Binance, Bybit, BingX, KuCoin, Bitget, Gate) only moves once USDG-on-Arbitrum deposits and withdrawals are listed; today only Kraken has that rail.
- Skip the Hyperliquid bridge, Circle and Coinbase wallets, Spark PSM and USDC.e.

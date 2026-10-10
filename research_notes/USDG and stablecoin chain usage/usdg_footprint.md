# USDG (Global Dollar) footprint as of 10 October 2026

Scope note: all figures are dated. "DefiLlama API (2026-10-10)" means pulled directly from `https://stablecoins.llama.fi/stablecoin/286` and `https://yields.llama.fi/pools` on 10 Oct 2026. GDN newsroom pages carry a confusing "published Oct 6, 2026" metadata stamp on every article (a site re-publish); the in-body dates are used here.

## KQ1. Which chains is USDG deployed on today, when did each launch, and what is supply per chain?

### Takeaway
As of 10 Oct 2026 USDG is natively issued on seven chains (Ethereum, Solana, Ink, X Layer, Robinhood Chain, Mantle, Arbitrum One) plus a LayerZero-wrapped "USDG0" on Hyperliquid, Plume and Aptos. Total supply is ~$3.05B (DefiLlama, 10 Oct 2026), with ~46% on X Layer, ~23% on Robinhood Chain, ~20% on Solana and ~8% on Ethereum; Ink, Arbitrum, Mantle and Hyperliquid together are under 4%. Arbitrum went live on 6 Oct 2026 and holds ~29M USDG so far. There is no deployment on Base, Polygon, Sui or Avalanche.

### Cited Findings

**Official contract addresses (Paxos docs, fetched 10 Oct 2026)** — [Paxos USDG mainnet docs](https://docs.paxos.com/stablecoin/usdg/mainnet)
- Ethereum: `0xe343167631d89B6Ffc58B88d6b7fB0228795491D`
- Ink: `0xe343167631d89B6Ffc58B88d6b7fB0228795491D` (same address as Ethereum)
- Arbitrum One: `0x004B506865409877C9fA29bfb1ebA929984B9bbC`
- Mantle: `0x063C1d1ef6e9099Ce3E8e9AD5C6173d12C49C086`
- Robinhood Chain: `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168`
- X Layer: `0x4ae46a509F6b1D9056937BA4500cb143933D2dc8`
- Solana mint: `2u1tszSeqZ3qBWF3uNGPFc8TzMk2tdiwknnRMWGWjGWH`

**Per-chain supply (DefiLlama API, 10 Oct 2026, total $3,050,296,719)** — [DefiLlama USDG page](https://defillama.com/stablecoin/global-dollar) / [API](https://stablecoins.llama.fi/stablecoin/286)
| Chain | Supply (USD) | Share | DefiLlama tracking start | Minted vs bridged (per DefiLlama) |
|---|---|---|---|---|
| X Layer | 1,399,704,317 | 45.9% | 2026-01-09 | all native-minted |
| Robinhood Chain | 703,047,821 | 23.0% | 2026-07-07 | all native-minted |
| Solana | 624,952,862 | 20.5% | 2025-07-12 | all native-minted |
| Ethereum | 257,555,114 | 8.4% | 2025-07-12 | 322.6M minted; ~65M counted as bridged out (to Ink) |
| Ink | 63,701,816 | 2.1% | 2025-07-12 | classified as bridged from Ethereum (minted = 0) |
| Hyperliquid L1 (USDG0) | 1,334,788 | 0.04% | 2026-04-28 | bridged (LayerZero OFT) |
| Arbitrum One | not yet tracked by DefiLlama | — | — | — |
| Mantle | not tracked by DefiLlama | — | — | — |

- Arbitrum One on-chain: Arbiscan shows total supply 29,243,646 USDG and 197 holders; the proxy contract was upgraded 12 Feb 2026 and 26 Mar 2026 (i.e., the contract existed months before the public launch) — [Arbiscan USDG token page](https://arbiscan.io/token/0x004B506865409877C9fA29bfb1ebA929984B9bbC) (fetched 10 Oct 2026).
- Solana on-chain supply via public RPC `getTokenSupply`: 625,580,477.59 USDG at slot 455,336,152 (10 Oct 2026) — [Solana RPC](https://api.mainnet-beta.solana.com) (my query); matches DefiLlama.
- Ink explorer: total supply 63,701,816 USDG, 6,478 holders, 24h volume $189M (fetched 10 Oct 2026) — [Ink explorer token page](https://explorer.inkonchain.com/token/0xe343167631d89B6Ffc58B88d6b7fB0228795491D).
- Ethereum: Etherscan shows total supply 323,174,711 USDG and 9,284 holders (fetched 10 Oct 2026) — [Etherscan holder chart](https://etherscan.io/token/tokenholderchart/0xe343167631d89B6Ffc58B88d6b7fB0228795491D). Note this is ~65M higher than DefiLlama's Ethereum figure because DefiLlama nets out the Ink-bridged balance.
- Cross-source figures for the big three chains (early Oct 2026): Crypto Briefing cites X Layer ~$1.51B, Robinhood Chain ~$703M, Solana ~$631M (late Sept 2026) — [Crypto Briefing, 6 Oct 2026](https://cryptobriefing.com/paxos-usdg-market-cap-3-billion/); Datawallet cites X Layer ~$1.44B (~92% of X Layer's stablecoin supply), Robinhood Chain ~$700M, Solana ~$642M — [Datawallet, early Oct 2026](https://www.datawallet.com/crypto/usdg-explained); Stablecoin Beat had X Layer USDG at $1.6B on 4 Sept 2026 within $1.7B total X Layer stablecoins — [Stablecoin Beat](https://stablecoinbeat.com/networks/x-layer/). The spread ($1.40B–$1.51B) reflects different dates and a declining X Layer balance in Sept–Oct.

**Launch chronology**
- Ethereum: USDG introduced Nov 2024 (Singapore-issued) — [CoinDesk, 4 Nov 2024](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies); [Paxos newsroom](https://www.paxos.com/newsroom/paxos-introduces-global-dollar-usdg).
- Solana: 25 Feb 2025 — [GDN newsroom](https://globaldollar.com/newsroom/global-dollar-usdg-stablecoin-now-available-on-solana-blockchain).
- Ink (Kraken's OP-Stack L2): 30 May 2025 — [GDN newsroom](https://globaldollar.com/newsroom/usdg-on-ink); [PRNewswire](https://www.prnewswire.com/news-releases/global-dollar-network-announces-usdg-launch-on-ink-blockchain-from-kraken-302468976.html).
- X Layer (OKX's L2): 26 Sept 2025; at launch "USDG issued by Paxos Issuance Europe is not yet available on X Layer" — [GDN newsroom](https://globaldollar.com/newsroom/global-dollar-network-announces-usdg-now-available-on-xlayer-from-okx).
- USDG0 (LayerZero OFT wrapper) on Hyperliquid, Plume, Aptos: late Nov 2025; USDG is locked in audited contracts and USDG0 minted 1:1 on the destination chain — [The Defiant](https://thedefiant.io/news/defi/paxos-labs-and-layerzero-launch-usdg0-to-expand-global-dollar-across-defi); [crypto.news](https://crypto.news/paxos-plume-hyperliquid-aptos-usdgo-stablecoin-2025/).
- Robinhood Chain (Arbitrum Orbit L2): public mainnet 1 Jul 2026; USDG is "the first stablecoin natively issued on that network" and the default lending asset in Robinhood Earn — [GDN press release, 1 Jul 2026](https://globaldollar.com/newsroom/usdg-is-now-available-on-robinhood-chain-as-the-lending-asset-in-robinhood-s-new-earn-product).
- Mantle: 3 Sept 2026, "one of the first natively minted stablecoins on the network"; Mantle joined GDN as a Network Partner — [Mantle/GDN press release via Yellow](https://yellow.com/press-releases/mantle-joins-global-dollar-network-as-usdg-circulation-surpasses-3b-across-150-partners); [GDN newsroom](https://globaldollar.com/newsroom/mantle).
- Arbitrum One: 6 Oct 2026, native issuance — [Arbitrum blog, 6 Oct 2026](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [GDN newsroom, 5 Oct 2026](https://globaldollar.com/newsroom/arbitrum).
- GDN's own list of chains as of the Arbitrum announcement: Ethereum, Ink, Mantle, Robinhood Chain, Solana, X Layer, Arbitrum One — [GDN newsroom, Arbitrum](https://globaldollar.com/newsroom/arbitrum).
- No source found for USDG on Base, Polygon, Sui or Avalanche; a search for those chains returned only the Arbitrum launch and an unrelated "USDsui" token — [search summary; Cointelegraph](https://cointelegraph.com/news/paxos-3b-usdg-stablecoin-launches-arbitrum).

### Inferences
- The "7 chains" figure GDN uses counts native issuance only; USDG0 on Hyperliquid/Plume/Aptos is a wrapper and DefiLlama tracks only the Hyperliquid leg (~$1.3M), implying USDG0 has not gained material traction after ~11 months.
- Ink supply is the same ERC-20 address as Ethereum and DefiLlama treats it as bridged via the OP Stack standard bridge; Paxos nonetheless lists Ink as a supported mainnet.

### Gaps
- Mantle on-chain supply: mantlescan.xyz returned 403 and explorer.mantle.xyz returned 502; no number found. DefiLlama does not break Mantle out.
- Plume and Aptos USDG0 balances: no tracker found.
- A Paxos "per-chain supply" transparency breakdown does not exist publicly; the Paxos transparency page lists only monthly attestation PDFs — [Paxos USDG transparency](https://www.paxos.com/usdg-transparency).

## KQ2. Which DeFi protocols list USDG, and what are pool/market sizes?

### Takeaway
By TVL, USDG DeFi usage is dominated by two venues: the Steakhouse-curated Morpho vault on Robinhood Chain (~$547M, the back end of Robinhood Earn) and Maple's syrupUSDG on Ethereum (~$504M). Everything else is sub-$100M: Aave V4 on Ethereum (~$60–75M across Core and Global Dollar hubs), Jupiter Lend on Solana (~$60M), Curve/Orca/Uniswap stable pools ($3–20M each), and a cluster of brand-new Arbitrum markets (Morpho/Gauntlet/Steakhouse, Fluid, GMX) totalling roughly $45M four days after launch.

### Cited Findings
**DefiLlama yields API, 10 Oct 2026 (110 pools contain "USDG"; top entries)** — [DefiLlama yields](https://defillama.com/yields?token=USDG) / [API](https://yields.llama.fi/pools)
| Chain | Protocol | Pool | TVL (USD) | APY |
|---|---|---|---|---|
| Robinhood Chain | Morpho Blue | STEAKUSDG (Steakhouse USDG vault) | 546,984,850 | 7.12% |
| Ethereum | Maple | USDG (syrupUSDG) | 504,180,351 | 5.06% |
| Robinhood Chain | Morpho Blue | SYRUPUSDG (collateral market) | 133,031,044 | — |
| X Layer | Aave V3 | PT-USDG-29OCT2026 | 60,344,028 | — |
| Solana | Jupiter Lend | USDG | 59,808,654 | 3.70% |
| Ethereum | Aave V4 | SYRUPUSDG | 51,324,055 | — |
| Ethereum | Curve | USDG-USDC | 20,036,744 | 0.06% |
| Solana | Orca | USDG-USDC | 18,081,074 | 0.10% |
| Arbitrum | Morpho Blue | SYRUPUSDG | 16,073,915 | — |
| Arbitrum | Morpho Blue | GTUSDGP (Gauntlet USDG Premium) | 10,724,394 | 8.00% |
| Solana | Kamino Liquidity | USDG-USDC | 10,506,983 | 0.04% |
| Robinhood Chain | Spark Savings | USDG | 10,345,051 | 3.8% |
| Ethereum | Aave V4 | USDG (Core) | 10,168,963 | 6.14% |
| Arbitrum | Morpho Blue | BBQUSDG (Steakhouse) | 5,388,033 | 8.00% |
| Arbitrum | Fluid DEX | USDG-USDC | 5,006,999 | 0.12% |
| Solana | Kamino Lend | USDG | 4,942,856 | 4.16% |
| Arbitrum | GMX V2 | USDG-USDG / USDC-USDG GLV vaults (4 pools) | ~9.8M combined | 0.08–0.31% |
| Ethereum | Uniswap V4 | USDC-USDG | 3,318,820 | 2.14% |
| Solana | Raydium | USDG-ONYC | 3,196,447 | 0.15% |
| Ink | Velodrome V3 | USDT0-USDG | 1,386,270 | 1.99% |
| Ink | Tydro (Aave-powered) | USDG | 1,047,858 | 1.70% |
| Ethereum | Pendle V2 | USDG | 398,330 | 3.6–4.3% |
| Ethereum | Aave V3 | USDG | 762,804 | 6.56% |
| Solana | Loopscale | USDG | 694,488 | 3.75% |

**Ethereum**
- Aave: USDG listed on Aave in late Dec 2025; Aave V4 launched on Ethereum mainnet in Mar 2026; as of June 2026 USDG on Aave had ~$50.5M net supplied, ~$41.5M borrowed (~82% utilisation), 828 unique suppliers, 170 borrowers, ~$316M cumulative deposits; launch supply-side incentives reached ~6.4% — [GDN, "How Aave is scaling USDG", 23 Jul 2026](https://globaldollar.com/newsroom/aave-usdg).
- Aave Labs joined GDN on 30 Mar 2026 making USDG a "native asset" on V4; Aave says GDN rewards it earns go back into the ecosystem rather than being kept as protocol revenue — [GDN, 30 Mar 2026](https://globaldollar.com/newsroom/usdg-aave-v4).
- Aave V4 "Global Dollar Hub" went live on Ethereum 1 Jul 2026 — [CryptoTimes, 1 Jul 2026](https://www.cryptotimes.io/2026/07/01/aave-v4-adds-global-dollar-hub-for-usdg-ecosystem/); Token Terminal reported USDG deposits >$60M in its first month — [Token Terminal, Aave July 2026 report](https://x.com/tokenterminal/article/2088252783803670645); Aavescan showed Core V4 with 48.4M USDG supplied / 28.1M borrowed (mid-July 2026) and the Global Dollar Hub at $23.6M supplied, mostly PT-USDG-24SEP2026 — [Aavescan Core V4](https://aavescan.com/ethereum-v4-core/usdg); [Aavescan Global Dollar Hub](https://aavescan.com/ethereum-v4-global-dollar).
- Maple's syrupUSDG launched 2 Jul 2026 on Ethereum and Robinhood Chain; Steakhouse selected syrupUSDG as collateral for the Robinhood Earn vault — [GDN, 2 Jul 2026](https://globaldollar.com/newsroom/maple-finance-joins-global-dollar-network).
- Uniswap handled $21.8B of USDG trading volume in Sept 2026, ~98% of USDG's DEX activity — [Crypto Briefing, 6 Oct 2026](https://cryptobriefing.com/paxos-usdg-market-cap-3-billion/).
- Pendle is named by GDN as a partner (fixed-rate yield) — [GDN 150-partners update, 21 Jul 2026](https://globaldollar.com/newsroom/150-partners).

**Solana**
- Lending venues Kamino, JupLend and Loopscale list USDG; Marinade, Solstice (eUSX) and OnRe (ONyc) use it as a core stable asset — [GDN, 4 Dec 2025](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap).
- Marinade "Stake SOL, Earn USDG": zero-commission validator converts all staking rewards/MEV into USDG paid each epoch; USDG Recipe TVL >249,000 SOL (Feb 2026) — [GDN, 10 Feb 2026](https://globaldollar.com/newsroom/marinade-usdg).
- Orca and Raydium host USDG/USDC and other pairs (see table above); Kamino lends USDG with KMNO incentives — [OKX Learn](https://www.okx.com/en-us/learn/kamino-usdc-usdg-yield-strategies).

**Robinhood Chain**
- Robinhood Earn: USDG is the default lending asset; Morpho provides infrastructure, Steakhouse Financial curates, collateral from Spark, Ethena and Maple (syrupUSDG); estimated ~7% APY displayed at launch — [Morpho blog](https://morpho.org/blog/robinhood-chooses-morpho-to-power-new-earn-product); [Steakhouse USDG vault on Morpho](https://app.morpho.org/robinhood-chain/vault/0xBeEff033F34C046626B8D0A041844C5d1A5409dd/steakhouse-usdg).
- Nearly 6,000 users interacted with Steakhouse vaults in the first ~10 days; initial TVL fluctuated between ~$16M and >$50M — [Crypto Briefing, 11 Jul 2026](https://cryptobriefing.com/steakhousefi-vaults-robinhood-chain-users/); Steakhouse vault deposits reached ~$417M by 31 Aug 2026 — [Datawallet](https://www.datawallet.com/crypto/usdg-explained); ~$547M on 10 Oct 2026 per DefiLlama (table above).

**Ink**
- Ink DeFi TVL was $209.9M across 70 protocols on 6 Oct 2026; main apps are Nado (CLOB DEX), Tydro (Aave-powered lending) and Uniswap v2/v3/v4 — [Chainstack](https://chainstack.com/what-is-ink/); USDG pools on Ink are small (Velodrome ~$1.4M, Tydro ~$1.0M per DefiLlama above).

**X Layer**
- Aave V3 on X Layer holds a PT-USDG-29OCT2026 market of ~$60M and a small ~$0.5M USDG market (DefiLlama above); Aave launched on X Layer for OKX Wallet users — [The Block](https://www.theblock.co/post/395594/aave-goes-live-okx-x-layer).

**Arbitrum (launch-day integrations, 6 Oct 2026)** — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/)
- Fluid and Uniswap: DEX liquidity; GMX: USDG is the deposit asset in the "GMX Dollar Vault" (GLV [USDG-USDG]) earning fees from BTC/ETH/SOL markets; Morpho: curated vaults (Gauntlet USDG Premium live; Steakhouse vault "shortly after"); Maple: syrupUSDG as a Morpho market; Kraken: deposits/withdrawals on Arbitrum One; Stargate (LayerZero): cross-chain transfers; LI.FI: one-step swaps into USDG on Arbitrum. CoinDesk adds "coming soon: Uniswap and Fhenix" — [CoinDesk, 6 Oct 2026](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth).

### Inferences
- Roughly $1.05B (about a third of all USDG) sits in just two yield products (Robinhood Earn/Steakhouse vault and syrupUSDG), both of which launched July 2026; the Q3 supply growth on Robinhood Chain is almost entirely Earn deposits.
- Arbitrum DeFi TVL (~$45M across Morpho/GMX/Fluid/Uniswap) exceeds the 29M native supply on Arbiscan because the Morpho "SYRUPUSDG" market is syrupUSDG collateral, not USDG, and because of timing differences between the two snapshots.

### Gaps
- No per-market numbers for Euler, Pendle beyond ~$0.4M, or Curve beyond the one USDG/USDC pool; I found no evidence of Euler or Fluid lending markets on Ethereum for USDG.
- Hyperliquid: no evidence of USDG0 being accepted as perps collateral; only ~$1.3M bridged.
- No Kamino/Jupiter governance-forum listing proposals surfaced in search.

## KQ3. Which centralized venues, wallets, fintechs and payment companies support USDG, and what do they do with it?

### Takeaway
Distribution is concentrated at three partners that run their own chains or L2s: OKX (X Layer, OKX Pay, OKX Money, margin/perps collateral), Robinhood (Robinhood Chain, Earn, in-app distribution) and Kraken (Ink, up to 5% rewards, Krak app, Arbitrum ramps). Mastercard added USDG to its on-chain settlement program (3 Jun 2026); Worldpay plans merchant settlement in USDG on Solana; Bitpanda, Gate, Gemini, KuCoin, SwissBorg, Bullish, Anchorage and others list, custody or hold it.

### Cited Findings
- **OKX**: joined GDN 14 Jul 2025 — [GDN, 14 Jul 2025](https://globaldollar.com/newsroom/okx-joins-global-dollar-network-alongside-leading-brands-including-worldpay-kraken-anchorage-digital-paxos-robinhood-and-30-additional-partners). Users holding USDG on OKX auto-receive rewards; OKX Pay offers enhanced rates with daily accrual; zero-fee USDG/USDC/USD conversion; USD/USDC/USDG share one order book for spot and perps; OKX Card (Europe, Mastercard) spends USDG with cashback in USDG; "hundreds of millions" of USDG held by OKX customers — [GDN, 13 Mar 2026](https://globaldollar.com/newsroom/okx-usdg). USDG/USDT spot pair listed 10 Jun 2026; USDG accepted as margin and perps collateral — [StablecoinInsider Q2 2026 report](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/). OKX Money standalone stablecoin app launched 6–7 Oct 2026 in LatAm, Africa, South Asia and Middle East with "up to 10% APY on eligible USDG balances" — [Blockhead, 7 Oct 2026](https://www.blockhead.co/2026/10/07/okx-launches-standalone-stablecoin-app-with-up-to-10-on-usdg-balances/). X Layer rewards "up to 3.85% APY", accrue daily, claim weekly, not available in USA/UK/EEA/Brazil/Australia/UAE/Turkey/Singapore — [OKX Learn, 26 Sept 2025](https://web3.okx.com/learn/usdg-xlayer).
- **Robinhood**: GDN co-founder; distributes USDG in-app; launched Robinhood Chain (Arbitrum stack) 1 Jul 2026 with USDG as the only native stablecoin and Earn's default lending asset; Earn displayed ~7% estimated yield at launch — [GDN, 1 Jul 2026](https://globaldollar.com/newsroom/usdg-is-now-available-on-robinhood-chain-as-the-lending-asset-in-robinhood-s-new-earn-product); [Datawallet](https://www.datawallet.com/crypto/usdg-explained). USDC bridged via Across from 13 chains converts to USDG on arrival — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/).
- **Kraken**: GDN co-founder (late 2024); rewards up to 5% annually on USDG balances (Oct 2025); Kraken+ members get boosted USDG rewards; Krak payments app supports USDG in 160+ countries — [GDN, 30 Oct 2025](https://globaldollar.com/newsroom/kraken-usdg); [GDN, 4 Dec 2025](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap). Kraken built Ink and supports USDG deposits/withdrawals on Arbitrum One — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/). Alpaca and Kraken use USDG to settle tokenized equities — [GDN, 4 Dec 2025](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap).
- **Mastercard**: joined GDN 24 Jun 2025; any Mastercard institution can mint, distribute and redeem USDG — [Ledger Insights, Jun 2025](https://www.ledgerinsights.com/mastercard-joins-global-dollar-network-for-stablecoins-enables-minting/). On 3 Jun 2026 Mastercard expanded settlement to regulated stablecoins incl. USDC, PYUSD, USDG, USDP, RLUSD and SoFiUSD for intraday/weekend/holiday settlement; early participants ARQ, CBW Bank, Cross River, Lead Bank, Nuvei — [Mastercard press release, Jun 2026](https://www.mastercard.com/global/en/news-and-trends/press/2026/june/mastercard-expands-settlement-capabilities-to-include-stablecoin.html); [The Block, 3 Jun 2026](https://www.theblock.co/news/markets/2026-06-03-mastercard-expands-stablecoin-settlement-options-with-usdc-pyusd-and-rlusd-403474).
- **Worldpay**: joined 23 Apr 2025; merchants expected to be able to settle in USDG on Solana; 40B+ transactions/yr, $2.2T volume — [GDN, 23 Apr 2025](https://globaldollar.com/newsroom/worldpay-joins-the-global-dollar-network-expanding-access-to-stablecoin-solutions-for-merchants-worldwide).
- **Bitpanda**: joined 5 Feb 2026; USDG trading, deposits and withdrawals for 7M+ registered users in Europe (MiCA version) — [PRNewswire, 5 Feb 2026](https://www.prnewswire.com/news-releases/bitpanda-joins-global-dollar-network-bringing-mica-compliant-usdg-to-european-markets-302679601.html).
- **EU launch partners (1 Jul 2025)**: Kraken, Gate, Coinmetro, SwissBorg, Zodia Custody, Orbital, Hercle, CoinsPaid, Bitwyre, Bitnet, HiFi — [GDN, 1 Jul 2025](https://globaldollar.com/newsroom/global-dollar-(usdg)-launches-in-the-eu).
- **Dec 2025 cohort** (named new partners): exchanges/trading Archax, B2C2, Bilira, Bitnet, Gate, Gemini, JST Digital, Keyrock, KuCoin, LBank, LTP, Merj, Ourbit, PDAX, SwissBorg, Wintermute, Wirex; infrastructure 1Money, Kravata, Tangem, TOPOS, Transak, WalletConnect; payments/fintech Alpaca, AMINA Bank, Confirmo, DeFi Development Corp., Keabank, Orbi, Reap, Ripe Money, Toku, Yellowcard. Earn programs at AMINA Bank, Gate, Kraken, Luno, OKX; corporate treasury holders Bullish, Kraken, OKX, Aleo, Galaxy, Confirmo, Gate, Fuze (Bullish received IPO proceeds in stablecoins Aug 2025); Orbi powers USDG card spend in Mexico; Toku runs USDG payroll — [GDN, 4 Dec 2025](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap).
- **Anchorage Digital**: founding member; cited as the US distribution path because it operates in every US state — [CoinDesk, 4 Nov 2024](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies).
- **Meow** (business banking) joined 9 Feb 2026; **Confirmo** (payments) profiled 5 Aug 2026; **Toku** payroll 22 Jan 2026 — [GDN newsroom index](https://globaldollar.com/newsroom).
- Exchange holdings on Ethereum (Etherscan, 10 Oct 2026): Kraken Hot Wallet 3 holds 38.1M (11.8%), OKX wallets 17.0M + 15.6M, Paxos wallets 17.8M + 15.0M, Aave Core Hub 10.2M — [Etherscan](https://etherscan.io/token/tokenholderchart/0xe343167631d89B6Ffc58B88d6b7fB0228795491D).

### Inferences
- Galaxy Digital and Nuvei are founding members but the only concrete activity found is Galaxy holding USDG in treasury and Nuvei participating in Mastercard's stablecoin settlement pilot; neither has a dedicated USDG product announcement.
- OKX's "up to 10%" and Robinhood's ~7% headline rates exceed T-bill yields (~3.5–4%), implying partners are subsidising from their GDN share plus marketing budgets.

### Gaps
- Zodia Custody beyond being an EU launch partner: no further detail found.
- Nuvei's specific USDG flows: not documented.

## KQ4. How does the GDN reward/revenue-sharing scheme work and how many members are there?

### Takeaway
GDN pays partners based on USDG they mint, hold (custody) and accept; Paxos says "up to 100%" of reserve returns on balances held on a partner's platform are passed through, with the network overall distributing >90% (Dec 2025) / "something like 97%" (Cascarilla, Nov 2024) of reserve economics. Membership grew from 7 founders (Nov 2024) to 25+ (May 2025), 100+ (Dec 2025), 130+ (Jul 2026) and 150+ (21 Jul 2026 onward). No published tier table, formula or payout percentages exist; payouts are weekly.

### Cited Findings
- Founding members: Anchorage Digital, Bullish, Galaxy Digital, Kraken, Nuvei, Paxos, Robinhood; Cascarilla: "We're distributing something like 97% of the economics"; rewards allocated "based on how they create connectivity and liquidity"; "Anybody can join the Global Dollar Network and accrue rewards for activity" — [CoinDesk, 4 Nov 2024](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies).
- Three reward streams on the GDN site: Hold ("Receive up to 100% of the returns generated by assets backing USDG held on your platform"), Mint ("Recurring revenue from increasing the total USDG in circulation"), Accept ("Incentives for inbound USDG deposits and payments") — [globaldollar.com](https://www.globaldollar.com/); [GDN network page](https://globaldollar.com/network). The network page has no tiers, eligibility or payout-frequency details; only a contact form and an "annual earning potential" calculator with illustrative-only disclaimers.
- "More than 90% of earnings on stablecoin holdings were distributed to network partners"; "Earn programs pay out weekly" — [GDN, 4 Dec 2025](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap).
- "Tens of millions" in USDG rewards paid to partners; partners can receive "up to 100% of the reserve rewards generated by USDG balances on their platforms" plus "additional rewards and incentives for activity that expands the network"; rewards subject to jurisdictional restrictions including EU — [GDN, 21 Jul 2026](https://globaldollar.com/newsroom/150-partners).
- Partner-count timeline: 7 at launch (Nov 2024) — [CoinDesk](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies); 25+ (12 May 2025) — [GDN](https://globaldollar.com/newsroom/25-members-network-milestone); 100+ (4 Dec 2025) — [GDN](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap); "more than 130" (2 Jul 2026) — [GDN Maple](https://globaldollar.com/newsroom/maple-finance-joins-global-dollar-network); 150+ (21 Jul 2026; still "150+" in the Sept Mantle and Oct Arbitrum releases) — [GDN](https://globaldollar.com/newsroom/150-partners); [GDN Arbitrum](https://globaldollar.com/newsroom/arbitrum).
- Arbitrum forum proposal describes GDN rewards as accruing "based on the USDG they hold, mint, and accept" and calls the Arbitrum share "a new dollar-denominated revenue line" (Arbitrum Foundation reply) but gives no percentage — [Arbitrum forum, 6 Oct 2026](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548).
- USDG holders receive no yield directly; income is shared with partners — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/).
- Conflicting third-party claim: Datawallet says Coinbase, Mastercard, Shopify, Stripe and Visa founded GDN; this is wrong (those back the rival "Open USD" consortium, live 30 Sept 2026) — [Datawallet](https://www.datawallet.com/crypto/usdg-explained) vs [CoinDesk 2024](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies) and [CoinDesk Oct 2026](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth).

### Inferences
- "Up to 100%" applies to the holding stream on a partner's own balances; the network-wide 90–97% figure implies Paxos retains a small single-digit cut, with the rest split among holders, minters and acceptors under bilateral terms that are not public.
- Chains (Arbitrum, Mantle, Robinhood Chain, X Layer) are now treated as "Network partners" in their own right, earning on USDG activity on their chain and redistributing to builders.

### Gaps
- Exact basis-point splits, minimum balance requirements, contract terms, and whether the "97%" still holds in 2026 are not published anywhere I could find.
- Total dollar amount of rewards paid: only "tens of millions" (Jul 2026).

## KQ5. What incentive or growth programs has Paxos/GDN run on specific chains?

### Takeaway
Growth has been bootstrapped chain-by-chain through the partner that owns the chain: OKX reward programs on X Layer (3.85% self-custody rewards, OKX Earn, OKX Money 10%), Robinhood's Earn product (~7%) on Robinhood Chain, Kraken's 5% rewards for Ink/Kraken users, Aave launch incentives (~6.4%) on Ethereum, and on Arbitrum a >$10M DRIP allocation plus a pending 100M-ARB DAO proposal. Paxos itself does not appear to run direct liquidity-mining programs; it pays partners.

### Cited Findings
- **X Layer**: USDG rewards up to 3.85% APY for holding on X Layer via OKX Wallet linked to exchange account (from 26 Sept 2025) — [OKX Learn](https://web3.okx.com/learn/usdg-xlayer); OKX Earn auto-rewards, OKX Pay enhanced rates, OKX Card cashback in USDG — [GDN, 13 Mar 2026](https://globaldollar.com/newsroom/okx-usdg); OKX Money up to 10% (Oct 2026) — [Blockhead](https://www.blockhead.co/2026/10/07/okx-launches-standalone-stablecoin-app-with-up-to-10-on-usdg-balances/). X Layer USDG grew from ~$323M (1 Apr 2026) to ~$1.72B (30 Jun 2026) — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/).
- **Robinhood Chain**: Robinhood Earn (~7% est. APY, reported as fixed for year one) drove supply from ~$212M (8 Jul 2026) to ~$718M (6 Oct 2026) — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/); [Datawallet](https://www.datawallet.com/crypto/usdg-explained). One analysis suggests the 7% "could reflect customer acquisition subsidization rather than natural borrowing demand" while the underlying Steakhouse vault showed 1.6–1.9% in July 2026 — [CryptoDaily, Jul 2026](https://cryptodaily.co.uk/2026/07/robinhood-earn-morpho-hood-stablecoin-yield-catalyst); [StakingRewards](https://www.stakingrewards.com/defi/0xbeefff136e3684273e6aa75a1669b784b373a4fd).
- **Solana**: Marinade's zero-commission "Stake SOL, Earn USDG" validator (Feb 2026); Jupiter Lend launched with USDG vaults and $2M incentives; Kamino pays KMNO on USDG — [GDN Marinade](https://globaldollar.com/newsroom/marinade-usdg); [OKX Learn Kamino](https://www.okx.com/en-us/learn/kamino-usdc-usdg-yield-strategies). Worldpay merchant settlement is on Solana — [GDN Worldpay](https://globaldollar.com/newsroom/worldpay-joins-the-global-dollar-network-expanding-access-to-stablecoin-solutions-for-merchants-worldwide).
- **Ethereum/Aave**: supply-side incentives ~6.4% at USDG's Aave launch (Dec 2025); Aave recycles its GDN rewards into USDG growth on V4 — [GDN Aave](https://globaldollar.com/newsroom/aave-usdg); [GDN Aave V4](https://globaldollar.com/newsroom/usdg-aave-v4).
- **Ink**: Kraken's up to 5% rewards and Krak app; Ink's own TVL is only ~$210M so USDG DeFi there is minor — [GDN Kraken](https://globaldollar.com/newsroom/kraken-usdg); [Chainstack](https://chainstack.com/what-is-ink/).
- **Arbitrum**: "More than $10 million in incentives through the DRIP program (already in place)"; Arbitrum Foundation "USDG on Arbitrum" program accepting applications; DAO proposal for +100M ARB to DRIP and ATMC treasury deployment — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/). A KuCoin flash item puts the initial allocation at ~7M ARB (>$10M) — [KuCoin News](https://www.kucoin.com/news/flash/arbitrum-dao-proposes-100m-arb-allocation-to-boost-usdg-stablecoin-adoption); this 7M-ARB figure does not appear in the Arbitrum blog or forum text and is single-sourced.
- **Mantle**: joined as Network Partner sharing rewards; Mantle positions USDG for RWA/institutional use (Mantle stablecoin TVL >$982M, RWA TVL ~$240M) — [Yellow press release, 3 Sept 2026](https://yellow.com/press-releases/mantle-joins-global-dollar-network-as-usdg-circulation-surpasses-3b-across-150-partners).
- Crystal Intelligence (July 2026 data) characterises USDG growth as "expanded on yield-sharing rewards programmes: supply that leaves when the incentive does" — [Crystal Intelligence](https://crystalintelligence.com/stablecoin/what-drove-the-stablecoin-supply-down/).

### Inferences
- Every chain with >$50M of USDG has a partner-funded consumer yield program attached; chains without one (Ink, Hyperliquid, Mantle so far) have stayed small.

### Gaps
- No public figures for how much GDN reward money each chain partner has received.
- Dune dashboards: none specific to USDG found; Entropy's arbdata.com/usdg dashboard loads dynamically and returned no values — [arbdata.com/usdg](https://arbdata.com/usdg).

## KQ6. Total supply trend over the last 12 months and biggest holders

### Takeaway
USDG grew ~4.2x in twelve months (from ~$0.72B on 1 Oct 2025 to a peak of ~$3.36B on 1 Aug 2026) then contracted ~9% to ~$3.05B by 10 Oct 2026, with the decline concentrated on X Layer and Ethereum. Holdings are dominated by exchange/platform wallets (OKX on X Layer, Robinhood Earn vault, Kraken) rather than retail DeFi.

### Cited Findings
**Monthly total supply (DefiLlama API, first of each month, USD)** — [DefiLlama API](https://stablecoins.llama.fi/stablecoin/286)
| Date | Supply | Date | Supply |
|---|---|---|---|
| 2025-08-01 | 326.9M | 2026-03-01 | 1,663.1M |
| 2025-09-01 | 551.6M | 2026-04-01 | 1,725.0M |
| 2025-10-01 | 719.4M | 2026-05-01 | 2,353.6M |
| 2025-11-01 | 991.5M | 2026-06-01 | 2,547.4M |
| 2025-12-01 | 1,036.1M | 2026-07-01 | 2,850.0M |
| 2026-01-01 | 1,232.8M | 2026-08-01 | 3,358.1M (peak) |
| 2026-02-01 | 1,491.5M | 2026-09-01 | 3,278.4M |
| | | 2026-10-01 | 3,088.8M |
| | | 2026-10-10 | 3,050.3M |

- Crossed $1B market cap early Nov/Dec 2025 — [GDN, 4 Dec 2025](https://globaldollar.com/newsroom/global-dollar-network-grows-to-more-than-100-partners-and-usdg-stablecoin-crosses-1-billion-in-market-cap); $3B+ by 21 Jul 2026 — [GDN](https://globaldollar.com/newsroom/150-partners); "approximately $3.2B, +340% y/y" late Sept 2026 — [Crypto Briefing](https://cryptobriefing.com/paxos-usdg-market-cap-3-billion/); CoinGecko ~$3.17B on 5 Oct 2026 — [CoinMarketCap AI summary](https://coinmarketcap.com/cmc-ai/global-dollar-usdg/latest-updates/); DefiLlama ~$3.09B 6–7 Oct and $3.05B 10 Oct — [DefiLlama](https://defillama.com/stablecoin/global-dollar). The Mantle release simultaneously says "surpasses $3B" and "climbed past $3.5 billion" — [Yellow](https://yellow.com/press-releases/mantle-joins-global-dollar-network-as-usdg-circulation-surpasses-3b-across-150-partners). Ranked 7th-largest stablecoin (Oct 2026) — [Cointelegraph](https://cointelegraph.com/news/paxos-3b-usdg-stablecoin-launches-arbitrum).
- Supply down ~2.7% over 7 days and ~2.9% over 1 month in early Oct 2026 with "weaker balances on X Layer and Ethereum during September" — [Datawallet](https://www.datawallet.com/crypto/usdg-explained). No source attributes the decline to a specific cause.
- Ethereum top holders (Etherscan, 10 Oct 2026; supply 323.2M, 9,284 holders; top 100 = 99.3%): unlabeled 0xeAEaA6D1… 101.9M (31.5%), Kraken Hot Wallet 3 38.1M (11.8%), Paxos 4 17.8M, OKX 154 17.0M, OKX 219 15.6M, Paxos 7 15.0M, unlabeled 0x228c9f02… 13.0M, Aave Core Hub 10.2M (3.1%) — [Etherscan](https://etherscan.io/token/tokenholderchart/0xe343167631d89B6Ffc58B88d6b7fB0228795491D).
- Solana (SolanaCompass, ~9–10 Oct 2026): 24,119 holders; top 10 hold ~72.3%, top 25 ~88.8%; largest single account 14.4%; none labelled; two small entries match Orca and Raydium USDG/USDC pools — [SolanaCompass](https://solanacompass.com/tokens/2u1tszSeqZ3qBWF3uNGPFc8TzMk2tdiwknnRMWGWjGWH). Phantom counted 15,867 Solana holders in July 2026 — [Phantom](https://phantom.com/tokens/solana/2u1tszSeqZ3qBWF3uNGPFc8TzMk2tdiwknnRMWGWjGWH).
- Pharos flags that "more than half of native supply sits on X Layer" as a material concentration (Sept 2026) — [Pharos](https://pharos.watch/stablecoin/usdg-paxos/); Crypto Briefing: "X Layer alone holds nearly half the supply" — [Crypto Briefing](https://cryptobriefing.com/paxos-usdg-market-cap-3-billion/).
- Robinhood Chain: ~69% of that chain's stablecoin supply was USDG by early Aug 2026 — [Datawallet](https://www.datawallet.com/crypto/usdg-explained); ~$547M of the ~$703M on the chain is in the Steakhouse Morpho vault (DefiLlama, 10 Oct 2026).
- Reserve composition (KPMG, Aug 2026 report as summarised): ~51% government MMFs, ~46% T-bills, <3% bank deposits — [Datawallet](https://www.datawallet.com/crypto/usdg-explained); Pharos: roughly half in a BNY Dreyfus government MMF, remainder T-bills maturing within weeks, small cash sleeve at banks in Singapore and Luxembourg; DBS and Standard Chartered named — [Pharos](https://pharos.watch/stablecoin/usdg-paxos/). Attestations by KPMG LLP from 27 Feb 2026 (Enrome LLP before) under ISCA standards; latest listed month Aug 2026 — [Paxos USDG transparency](https://www.paxos.com/usdg-transparency). StablecoinInsider's claim that WithumSmith+Brown attests USDG conflicts with Paxos's page and is likely wrong — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/).
- Peg: one single-source report of a brief May 2026 dip linked to an "Arbitrum TMX contract vulnerability" that recovered the same session — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/); not corroborated elsewhere.

### Inferences
- The unlabeled 101.9M Ethereum holder (31.5%) is very likely a Paxos or large-partner custody/bridge wallet; combined with Kraken, OKX, Paxos and Aave, labelled or likely-custodial addresses hold >60% of Ethereum supply.
- Roughly 80–85% of total USDG is on partner-controlled chains (X Layer, Robinhood Chain) or in exchange wallets; "organic" DeFi outside Earn/syrupUSDG is on the order of $150–250M.

### Gaps
- No per-chain historical series for X Layer/Ethereum decline causes; no Paxos commentary on the Aug–Oct 2026 contraction.
- No labelled Solana holder data (Solscan returned 403); the Solana RPC `getTokenLargestAccounts` call returned no data.
- Latest KPMG attestation PDF figures (tokens outstanding, per-entity SG vs EU split) not retrieved.

## KQ7. Is USDG live on Arbitrum today, and what has been said about it?

### Takeaway
Yes. USDG launched natively on Arbitrum One on 6 Oct 2026 and Arbitrum joined GDN as a Network partner; on-chain supply is ~29M USDG (Arbiscan, 10 Oct 2026) with ~$45M of USDG-related DeFi TVL. A non-constitutional ArbitrumDAO proposal (posted 6 Oct 2026) to make USDG a core strategic initiative, add 100M ARB to DRIP, and route treasury/AEP fees into USDG is in forum discussion (6–15 Oct), with an off-chain vote 15–22 Oct and on-chain vote 29 Oct–12 Nov 2026.

### Cited Findings
- Launch: "USDG is now live on Arbitrum One" (6 Oct 2026); integrations Fluid, Uniswap, GMX (GLV USDG vault), Morpho (Gauntlet USDG Premium live; Steakhouse to follow), Maple syrupUSDG, Kraken on/off-ramp, Stargate/LayerZero bridge, LI.FI — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [GDN, 5 Oct 2026](https://globaldollar.com/newsroom/arbitrum); [CoinDesk, 6 Oct 2026](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth).
- Quotes: Steven Goldfeder (Offchain Labs): "For too long, though, none of that activity has happened in a dollar aligned with the ecosystem creating it"; Brendan Ma (Arbitrum Foundation): "Until today, the ecosystem has not directly shared in the growth and economics of this asset class" and "With USDG, Arbitrum and builders across the platform now have a stake in the growth upside"; Peter Jonas (Paxos CRO): "Global Dollar Network exists to put USDG where that activity happens and to reward the partners who make it useful" — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [CoinDesk](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth).
- Rationale: Arbitrum holds ~$3.8–4B of stablecoins, ~60% USDC, from which Arbitrum earns no reserve income; USDG lets the chain "capture a share of the economics" — [CoinDesk](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth); [KuCoin blog](https://www.kucoin.com/blog/paxos-usdg-lands-on-arbitrum-defi-as-the-chain-holds-3-8-billion-in-stablecoins).
- DAO proposal "Adopting USDG as a Core Strategic Initiative for the ArbitrumDAO" by Entropy Advisors with Offchain Labs, Arbitrum Foundation and OpCo: (1) add 100M ARB to DRIP (original 80M over four seasons; ~65M remaining, rising to ~165M), merge Seasons 2–4 into one USDG-focused season; (2) ATMC deploys treasury (holds ~$66M in tokenized MMF/stablecoins) toward USDG incl. minting from existing stablecoin allocation and seeding protocol-owned liquidity; (3) route AEP fees (net of 20% to Developer Guild) to the TM Portfolio and convert to USDG; (4) Entropy runs it as a Special Project at no extra cost. Aspiration: convert 15–20% of ~$4B existing Arbitrum stablecoins within year one; formal KPIs to be set by the OAT. Timeline: forum 6–15 Oct, Snapshot 15–22 Oct, on-chain 29 Oct–12 Nov 2026 — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548).
- Community: stonecoldpat and Arbitrum Foundation support; NikitaOnchain posted DRIP Season 1 retention data (Morpho Arbitrum +203%, Fluid Arbitrum +128% borrowing at +180 days) and asked for per-protocol retention targets — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548).
- Status: proposal not yet voted; "passage is not guaranteed" — [CoinDesk](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth); [Coininsider](https://www.coininsider.org/news/arbitrum-joins-paxos-led-global-dollar-network-to-capture-stablecoin-revenue/).
- Pre-launch signals: the Arbitrum USDG proxy was deployed/upgraded 12 Feb and 26 Mar 2026 — [Arbiscan](https://arbiscan.io/token/0x004B506865409877C9fA29bfb1ebA929984B9bbC); Robinhood Chain (an Arbitrum Orbit chain) had USDG as its sole native stablecoin since 1 Jul 2026 — [GDN](https://globaldollar.com/newsroom/usdg-is-now-available-on-robinhood-chain-as-the-lending-asset-in-robinhood-s-new-earn-product); Standard Chartered noted Arbitrum receives 10% of net protocol revenue from Robinhood Chain — [Cointelegraph](https://cointelegraph.com/news/paxos-3b-usdg-stablecoin-launches-arbitrum).
- Other L2s: Mantle (3 Sept 2026) is the only other 2026 L2 launch; GDN said in Jul 2026 "blockchains grew to 5, with more planned" — [GDN 150-partners](https://globaldollar.com/newsroom/150-partners). No announcements found for Base, Optimism mainnet, Polygon, Avalanche or Sui.

### Inferences
- Arbitrum is the first chain where a DAO (rather than a corporate partner) is proposing to spend its own treasury to grow USDG, which makes the 29 Oct–12 Nov on-chain vote the key near-term catalyst for Arbitrum USDG supply.
- Early Arbitrum supply (~29M) is tiny relative to the 15–20% conversion aspiration (~$600–800M), so the chain's share will depend on DRIP incentives actually landing.

### Gaps
- No Arbitrum-specific GDN reward percentage disclosed.
- No daily Arbitrum supply series yet (DefiLlama has not added the chain; arbdata.com values not retrievable).

## KQ8. Regulatory status (MAS, MiCA/FIN-FSA, NYDFS, GENIUS Act)

### Takeaway
USDG is issued by Paxos Digital Singapore (MAS Major Payment Institution) and, for the EU, by Paxos Issuance Europe OY (FIN-FSA supervised, MiCA-compliant, since 1 Jul 2025). It is not an NYDFS- or OCC-issued token; Paxos Trust (now an OCC national trust since Dec 2025) issues PYUSD/USDP under US oversight, and Paxos's GENIUS Act commentary names PYUSD but says nothing about USDG, whose US path would be via the Act's foreign-issuer/comparable-regime route.

### Cited Findings
- Singapore: issued by Paxos Digital Singapore, "a Major Payments Institution supervised by the Monetary Authority of Singapore"; redeemable 1:1 from Paxos — [globaldollar.com](https://www.globaldollar.com/); originally "substantively compliant" with MAS's then-upcoming framework with DBS as primary bank (Nov 2024) — [CoinDesk](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies).
- EU: Paxos Issuance Europe OY regulated by FIN-FSA; MiCA requires part of reserves at European banking partners; all EU holders may redeem against PIE at par at any time; EU consumer launch 1 Jul 2025 — [GDN, 1 Jul 2025](https://globaldollar.com/newsroom/global-dollar-(usdg)-launches-in-the-eu); EU white paper at paxos.com/terms-and-conditions/usdg-eu-whitepaper — [Bitpanda PR](https://www.prnewswire.com/news-releases/bitpanda-joins-global-dollar-network-bringing-mica-compliant-usdg-to-european-markets-302679601.html). MiCA transition ended 1 Jul 2026, with EU venues restricting USDT — [StablecoinInsider](https://stablecoininsider.org/usdg-q2-2026-report-supply-growth-partner-expansion-and-the-robinhood-chain-moment/). EU-issued USDG was not initially on X Layer — [GDN X Layer](https://globaldollar.com/newsroom/global-dollar-network-announces-usdg-now-available-on-xlayer-from-okx).
- US: Paxos converted its NYDFS limited-purpose trust charter to an OCC national trust charter on 12 Dec 2025 — [Paxos newsroom](https://www.paxos.com/newsroom/occ-approves-paxos-application-to-convert-to-occ-trust-paxos-to-complete-conversion-imminently-to-become-a-federally-regulated-blockchain-infrastructure-provider); Paxos says it "qualifies as a permitted payment stablecoin issuer under the GENIUS Act" and that PYUSD is issued under that supervision, but makes no statement about USDG — [Paxos GENIUS Act blog](https://www.paxos.com/blog/genius-act). Paxos describes USDG as "issued by MAS regulated and MiCA compliant entities" while PYUSD/USDP are under OCC oversight — [paxos.com](https://www.paxos.com/).
- GENIUS Act timing: effective the earlier of 18 Jan 2027 or 120 days after final rules; Treasury proposed rules Aug 2026 with comments closing 19 Oct 2026; exchanges have until 18 Jul 2028 to stop offering non-qualifying tokens — [Datawallet](https://www.datawallet.com/crypto/usdg-explained); [Paxos GENIUS Act blog](https://www.paxos.com/blog/genius-act).
- US availability is via partners (e.g., Anchorage, Robinhood, Kraken) rather than direct US issuance — [CoinDesk 2024](https://www.coindesk.com/business/2024/11/04/new-global-dollar-stablecoin-backed-by-robinhood-kraken-paxos-and-other-crypto-heavies); reward programs are geo-restricted (OKX X Layer rewards exclude USA, UK, EEA, Singapore etc.) — [OKX Learn](https://web3.okx.com/learn/usdg-xlayer).
- Pharos notes bankruptcy-remoteness for USDG "depends on contract terms, not a trust structure" unlike Paxos Trust coins — [Pharos](https://pharos.watch/stablecoin/usdg-paxos/).
- Attestations: KPMG LLP from 27 Feb 2026 (previously Enrome LLP), ISCA standards, monthly; Aug 2026 is the latest listed — [Paxos USDG transparency](https://www.paxos.com/usdg-transparency).

### Inferences
- USDG's US position after Jan 2027 depends on Treasury's comparable-regime determination for Singapore/EU issuers or on Paxos adding a US-issued leg; nothing public indicates the latter is planned.

### Gaps
- No MAS or FIN-FSA register entry retrieved directly; status is from Paxos/GDN statements and press.
- No Paxos statement found on USDG's treatment under GENIUS Act foreign-issuer rules.

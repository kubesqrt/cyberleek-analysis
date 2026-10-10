# Who holds USDC on Arbitrum One (as of 10 October 2026) — segmented for USDG conversion targeting

Scope note: native USDC = `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`; bridged USDC.e = `0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8`. "On-chain read" below means an `eth_call` (balanceOf / totalSupply / totalAssets) I ran against a public Arbitrum RPC (`arbitrum-one-rpc.publicnode.com`) at block 513,577,870 (2026-10-10 17:27 UTC); each such figure links to the Arbiscan page for the address so it can be re-checked. Arbiscan's top-holder table was retrieved from its holder endpoint on 2026-10-10 (the "Analytics Snapshot" on that page is live). All dollar figures treat 1 USDC = $1.

Context that changes the whole analysis: USDG went live natively on Arbitrum One on 6 October 2026, Arbitrum joined the Global Dollar Network, and an Arbitrum DAO proposal (Entropy Advisors with Offchain Labs, the Arbitrum Foundation and OpCo) to add 100M ARB to DRIP and deploy treasury assets for USDG liquidity is in forum discussion (6–15 Oct), with an offchain vote 15–22 Oct and onchain vote 29 Oct–12 Nov 2026 — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [Arbitrum forum proposal](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548); [CoinDesk, 6 Oct 2026](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth). USDG on Arbitrum is `0x004b506865409877c9fa29bfb1eba929984b9bbc` (Arbiscan token search result "Global Dollar", website globaldollar.com) with total supply 29,243,646 USDG at the block above (on-chain read) — [Arbiscan USDG](https://arbiscan.io/token/0x004b506865409877c9fa29bfb1eba929984b9bbc).

## Key question 1: What are the top 50 USDC holders on Arbitrum and what entities are they?

### Takeaway
The top 50 addresses hold ≈$1.27B (47.7%) of 2.668B native USDC; the two largest are the Hyperliquid deposit bridge ($389.7M, 14.6%) and Binance Hot Wallet 34 ($272.5M, 10.2%). Labeled DeFi contracts in the top 50 total only ≈$174M; ≈$364M sits in 31 unlabeled addresses (many with round balances suggesting treasuries/OTC desks), and USDC.e is a $48M legacy tail.

### Cited Findings
Supply and holder counts
- Native USDC totalSupply on Arbitrum: 2,668,168,442 USDC; USDC.e totalSupply: 48,054,181 (on-chain read, 2026-10-10) — [Arbiscan native USDC](https://arbiscan.io/token/0xaf88d065e77c8cC2239327C5EDb3A432268e5831); [Arbiscan USDC.e](https://arbiscan.io/token/0xff970a61a04b1ca14834a43f5de4533ebddb5cc8).
- Arbiscan token page shows 5,757,813 holders for native USDC and "Max Total Supply 2,667,904,052" (fetched 2026-10-10); a secondary guide cites ~5.64M holders on 29 Sep 2026 and 632,325 USDC.e holders on 23 Sep 2026 — [Arbiscan](https://arbiscan.io/token/0xaf88d065e77c8cC2239327C5EDb3A432268e5831); [eco.com guide](https://eco.com/support/en/articles/14998919-usdc-on-arbitrum-complete-guide).
- DefiLlama puts USDC circulating on Arbitrum at $2,356M on 2026-10-10 (vs $2,746M on 10 Sep 2026, $2,254M on 12 Jul 2026, $2,213M on 13 Apr 2026, $2,399M on 10 Oct 2025, $1,461M on 10 Oct 2024) — [DefiLlama stablecoin chart API, Arbitrum/USDC](https://stablecoins.llama.fi/stablecoincharts/Arbitrum?stablecoin=2). Conflict: this is ~$310M below the on-chain totalSupply (2.668B); the Arbitrum DAO forum states "~$4B in stablecoins on Arbitrum One excluding the Hyperliquid bridge", which suggests DefiLlama nets out bridge-locked USDC — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548).
- All stablecoins on Arbitrum: $4,132M on 2026-10-10 (vs $4,763M a year earlier). By asset (DefiLlama, 2026-10-10): USDC $2,329.6M, USDT $823.4M, PYUSD $359.0M, USDai $344.2M, USDS $99.7M, rwaUSDi $77.4M, USDe $1.9M, USDG $0 (not yet indexed) — [DefiLlama stablecoins API](https://stablecoins.llama.fi/stablecoins?includePrices=false); [chain chart](https://stablecoins.llama.fi/stablecoincharts/Arbitrum). CoinDesk/KuCoin cite "~$3.8B, ~60% USDC" and an eco.com piece cites $4.14B with USDC 56% / USDT 20% (15 Sep 2026) — [CoinDesk](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth); [KuCoin, 8 Oct 2026](https://www.kucoin.com/blog/paxos-usdg-lands-on-arbitrum-defi-as-the-chain-holds-3-8-billion-in-stablecoins); [eco.com](https://eco.com/support/en/articles/15210575-arbitrum-stablecoin-aggregators-2026-top-routing-platforms).

Top 50 native-USDC holders (Arbiscan holder table, 2026-10-10; labels are Arbiscan's) — [Arbiscan holders tab](https://arbiscan.io/token/0xaf88d065e77c8cC2239327C5EDb3A432268e5831#balances)
1. `0x2Df1c51E09aECF9cacB7bc98cB1742757f163dF7` Hyperliquid: Deposit Bridge 2 — 389,738,740 (14.61%)
2. `0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055` Binance: Hot Wallet 34 (proxy) — 272,504,514 (10.21%)
3. `0xc64e528c6439a204da1b519e78aa43f9e4b32f00` unlabeled proxy (same implementation `0xd206ac7f…` as Binance HW34) — 46,090,766 (1.73%)
4. `0x47c031236e19d024b42f8AE6780E44A573170703` GMX: GM BTC/USD [WBTC-USDC] — 32,925,760 (1.23%)
5. `0xcDE3F99b…eFEc24565` unlabeled — 28,458,997 (1.07%)
6. `0x74bBBb0E7F0bAd6938509Dd4B556a39A4Db1F2Cd` Variational: Core OLP Vault — 26,274,732 (0.98%)
7. `0x70d95587d40A2caf56bd97485aB3Eec10Bee6336` GMX: GM ETH/USD [WETH-USDC] — 25,467,223 (0.95%)
8. `0x6fa5b6d93e2539caea358518d3fe8f75418e5a1d` unlabeled proxy (impl `0xd206ac7f…`) — 23,000,984 (0.86%)
9. `0x0b07f64ABc342B68AEc57c0936E4B6fD4452967E` BingX: Cold Wallet — 21,607,022 (0.81%)
10. `0x724dc807b04555b71ed48a6896b6f41593b8c637` Aave: aArbUSDCn (idle reserve liquidity) — 19,004,409 (0.71%)
11. `0x9e36cb86a159d479ced94fa05036f235ac40e1d5` Aster: Treasury — 18,120,811 (0.68%)
12. `0x22ef827d179e11d1e309ed4e5d8eb500df5ed9ea` unlabeled proxy — 18,094,835 (0.68%)
13. `0x519c721D…d60496a47` unlabeled — 16,069,577 (0.60%)
14. `0xDB5e6C7a…8Aa7b5dd0` unlabeled — 15,917,770 (0.60%)
15. `0xc8477506…7FAb82f36` unlabeled — 15,194,470 (0.57%)
16. `0xF96d9b5f…3a9E50001` unlabeled — 14,874,064 (0.56%)
17. `0x82675d0553d802039e6776c006beb1b820a69d55` unlabeled proxy — 14,807,955 (0.56%)
18. `0xC6962004f452bE9203591991D15f6b388e09E8D0` Uniswap V3 WETH/USDC 0.05% pool — 13,959,444 (0.52%)
19. `0x9071d430…3D6Cf5C0B` unlabeled — 13,722,908 (0.51%)
20. `0xEa4CD3F1…d2eF12B74` unlabeled — 13,666,266 (0.51%)
21. `0x360E68faCcca8cA495c1B759Fd9EEe466db9FB32` Uniswap V4: Pool Manager — 12,044,945 (0.45%)
22. `0x463f5D63e5a5EDB8615b0e485A090a18Aba08578` Circle: Hot Wallet — 11,437,664 (0.43%)
23. `0x1714400FF23dB4aF24F9fd64e7039e6597f18C2b` Crypto.com 4 — 11,353,806 (0.43%)
24. `0x5E91B40467fB8902c46a7b6Cb90482363188D645` Variational: Protocol Treasury — 10,439,623 (0.39%)
25. `0x564220f3f6f2d0ED28Bf6A75F344Fad7C6134a68` Coinbase 83 — 10,015,040 (0.38%)
26. `0xC584d67A…77dbB6b29` unlabeled — 10,001,107
27. `0xEd1A3a4B…3D9B03481` unlabeled — 10,000,009
28. `0x2aE5E08f…00A2b83E7` unlabeled — 10,000,000
29. `0x2B05F8e1cACC6974fD79A673a341Fe1f58d27266` Spark: PSM 3 (Sky) — 9,999,899
30. `0x47A761bb…643714e4F` unlabeled — 9,424,139
31. `0x75288264…E2f3E5004` unlabeled — 8,662,164
32. `0x4beeceeF…41906afa5` unlabeled — 8,590,000
33. `0x239cC15d…48B85841b` unlabeled — 8,465,835
34. `0xe483Ec81…f76c01E37` unlabeled — 7,804,998
35. `0xA0533554…7Ba389888` unlabeled — 7,659,748
36. `0x891ABe3F…F784298C4` unlabeled — 7,164,384
37. `0xD4F0e0b9…8Ea453b0e` unlabeled — 7,010,000
38. `0xaDFffc33…3d6ed116D` unlabeled — 6,294,914
39. `0x52aa899454998be5b000ad077a46bbe360f4e497` Fluid: Liquidity Proxy — 6,251,470
40. `0xb0473ca01e91981623b65daf84ab7bc94a7e4000` unlabeled proxy (impl `0xd206ac7f…`) — 6,150,066
41. `0x03B9A189…2282130FA` unlabeled — 5,965,004
42. `0x1E4590f4…6A853125b` unlabeled — 5,713,870
43. `0x51C72848c68a965f66FA7a88855F9f7784502a7F` "Market Maker: 0x51c7…2a7f" — 5,679,761
44. `0xb2746ef5c9021def18a7568a56380eef6041eca6` unlabeled proxy (impl `0xd206ac7f…`) — 5,567,998
45. `0x2c2f7642…0B8D1a96c` unlabeled — 5,426,693
46. `0x93228d328c9c74c2BFE9f97638bbb5ef322f2Bd5` Bybit: Wallet 4 — 5,146,384
47. `0x8aD4E042…bf933bd88` unlabeled — 5,034,018
48. `0xb8e6d31e7b212b2b7250ee9c26c56cebbfbe6b23` KuCoin 15 — 5,002,345
49. `0x007d76eE…443D967A0` unlabeled — 4,999,992
50. `0xcc3A4101…7472c6c9A` unlabeled — 4,470,662
(Arbiscan truncates unlabeled addresses in its table; full addresses are shown where the page exposed them.)

USDC.e top holders (Arbiscan, 2026-10-10; supply $48.05M; top-100 concentration 63.0%, top 10 = 37.4%): #1 unlabeled `0x1eED63Ef…b974F477b` 8.68M (18.1%); #2 `0x4306ba10…` 2.10M; #9 Multichain anyUSDC token contract 0.67M (stranded); #11 Market Maker 0x51c7 0.38M; #12 Stargate S*USDC 0.38M; #17 Camelot POL 0.32M; #21 Compound cUSDCev3 0.30M; #24 OKX 230 0.28M — [Arbiscan USDC.e holders](https://arbiscan.io/token/0xff970a61a04b1ca14834a43f5de4533ebddb5cc8#balances).

Entity notes
- Variational is an RFQ-based perp DEX on Arbitrum where trades run against the Omni Liquidity Provider (OLP) pool; margin and settlement are USDC on Arbitrum — [DefiLlama Variational platform page](https://defillama.com/rwa/platform/variational); [Substack explainer, ~Jan 2026](https://corgiltalks.substack.com/p/the-only-rfq-based-perp-dex-variational).
- Aave aArbUSDCn balance is only the un-borrowed portion of the reserve; total USDC supplied to Aave v3 Arbitrum = aArbUSDCn totalSupply 178,816,402 and variable debt totalSupply 159,937,298 (89.4% utilisation) (on-chain read) — [aArbUSDCn](https://arbiscan.io/token/0x724dc807b04555b71ed48a6896b6F41593b8C637); [variableDebtArbUSDCn](https://arbiscan.io/token/0xf611aEb5013fD2c0511c9CD55c7dc5C1140741A6).

### Inferences
- Summing Arbiscan labels within the top 50: bridge $389.7M; labeled CEX wallets ≈$325.6M (Binance 272.5, BingX 21.6, Crypto.com 11.4, Coinbase 10.0, Bybit 5.1, KuCoin 5.0) plus Circle's own hot wallet $11.4M; labeled DeFi/protocol contracts ≈$174M (GMX GM pools 58.4, Variational 36.7, Aave idle 19.0, Aster treasury 18.1, Uniswap v3+v4 26.0, Spark PSM 10.0, Fluid 6.3); one labeled market maker $5.7M; 31 unlabeled addresses ≈$364M.
- Four of the unlabeled top-50 proxies (#3, #8, #40, #44; ≈$80.8M) share the implementation contract used by Binance Hot Wallet 34, so they are plausibly exchange-operated deposit/sweep wallets — this is an inference from bytecode reuse, not a confirmed label.
- Round balances (10,000,000; 10,000,009; 8,590,000; 7,010,000; 4,999,992) are characteristic of treasury/OTC/market-maker parking rather than DeFi positions; these ~$60M are candidates for direct OTC conversion outreach but need Nansen/Arkham attribution.

### Gaps
- Arbiscan truncates unlabeled addresses in its holder table and I could not retrieve Nansen/Arkham entity labels for the 31 unlabeled top-50 holders (~$364M); Arbiscan's full token-holder-chart page returned 403.
- Vertex Clearinghouse, Synthetix v3, Wintermute/Jump/OKX/Kraken addresses I queried held ~0 native USDC on Arbitrum; DefiLlama shows Vertex and Synthetix v3 Arbitrum TVL at $0 — I found no source explaining whether these have wound down on Arbitrum.

## Key question 2: How much USDC on Arbitrum sits in DeFi contracts vs EOAs vs CEX wallets?

### Takeaway
Of 2.668B native USDC, roughly 15% is locked in the Hyperliquid bridge, ~12–15% in identifiable CEX hot/cold wallets, ~20–25% in DeFi contracts (lending ~$250M supplied, perps ~$110M, DEX pools ~$60M), and roughly half is in EOAs/unlabeled wallets, of which $1.23B (46%) sits outside the top 100 addresses.

### Cited Findings
Lending (USDC actually supplied, 2026-10-10 on-chain reads unless noted)
- Aave v3 Arbitrum USDC: 178.8M supplied / 159.9M borrowed / 19.0M idle — [aArbUSDCn](https://arbiscan.io/token/0x724dc807b04555b71ed48a6896b6F41593b8C637). Aavescan showed $272.1M supplied / $164.2M borrowed as of 15 Mar 2026; DefiLlama Aave v3 Arbitrum TVL (all assets) $508.4M now vs $802.7M 180 days ago and $1,138.5M a year ago — [Aavescan Arbitrum USDC](https://aavescan.com/arbitrum-v3/usdc); [DefiLlama aave-v3 API](https://api.llama.fi/protocol/aave-v3).
- Fluid: fUSDC lending vault totalAssets 55.36M USDC; the Fluid Liquidity Layer holds 6.25M idle USDC and 2.42M USDG — [fUSDC](https://arbiscan.io/token/0x1A996cb54bb95462040408C06122D45D6Cdb6096); [Fluid Liquidity](https://arbiscan.io/address/0x52Aa899454998Be5b000Ad077a46Bbe360F4e497). DefiLlama: Fluid lending Arbitrum TVL $138.5M (borrowed $112.5M), Fluid DEX $35.2M — [DefiLlama fluid-lending](https://api.llama.fi/protocol/fluid-lending); [fluid-dex](https://api.llama.fi/protocol/fluid-dex).
- Compound v3 Arbitrum: cUSDCv3 totalSupply 14.94M (3.49M idle); USDC.e comet 0.30M — [cUSDCv3](https://arbiscan.io/token/0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf); DefiLlama Compound v3 Arbitrum TVL $68.6M — [API](https://api.llama.fi/protocol/compound-v3).
- Morpho Arbitrum: DefiLlama TVL $32.1M (borrowed $21.3M); Morpho API lists V2 vault assets of $21.2M, of which Gauntlet USDG Premium $10.73M (`0x390c1bb0…`), Steakhouse USDG Pro $5.39M (`0xbeeFf72B…`), Bitget x Steakhouse USDT0 $2.19M, Bitget x Steakhouse USDC $1.55M, Steakhouse USDC High Yield $0.44M, Gauntlet USDC Prime $0.27M; the V1 Gauntlet USDC Core vault holds 0.46M (on-chain totalAssets) — [DefiLlama morpho-blue](https://api.llama.fi/protocol/morpho-blue); [Morpho API](https://blue-api.morpho.org/graphql); [Gauntlet USDC Core](https://app.morpho.org/arbitrum/vault/0x7e97fa6893871A2751B5fE961978DCCb2c201E65/gauntlet-usdc-core). Note: a May 2026 report put the Arbitrum Portal's Morpho-powered USDC vault at $13.3M TVL — [CryptoBriefing](https://cryptobriefing.com/morpho-stablecoin-earn-arbitrum-portal/).
- Dolomite Margin holds 1.22M USDC + 0.04M USDC.e; DefiLlama Dolomite Arbitrum TVL $23.7M; Silo v2 Arbitrum $0.2M; Euler v2 Arbitrum $1.0M — [Dolomite Margin](https://arbiscan.io/address/0x6Bd780E7fDf01D77e4d475c821f1e7AE05409072); [DefiLlama dolomite](https://api.llama.fi/protocol/dolomite); [silo-v2](https://api.llama.fi/protocol/silo-v2); [euler-v2](https://api.llama.fi/protocol/euler-v2).

Perps/derivatives
- GMX V2 GM pools (USDC side): BTC/USD 32.93M, ETH/USD 25.47M, SOL/USD 4.40M, LINK/USD 1.77M, ARB/USD 0.84M = ~65.4M USDC; GLP (V1 vault) 0.02M USDC + 0.26M USDC.e — [GM BTC/USD](https://arbiscan.io/address/0x47c031236e19d024b42f8AE6780E44A573170703); [GM ETH/USD](https://arbiscan.io/address/0x70d95587d40A2caf56bd97485aB3Eec10Bee6336); DefiLlama GMX v2 Arbitrum TVL $202.3M (vs $440.8M a year ago) — [API](https://api.llama.fi/protocol/gmx-v2-perps).
- Variational OLP vault 26.27M + protocol treasury 10.44M; Aster treasury 18.12M (Arbiscan table above). Gains gUSDC vault 4.15M; Ostium vault 2.34M; Vertex clearinghouse ~0; Synthetix v3 core 0 — [gUSDC](https://arbiscan.io/address/0xd3443ee1e91aF28e5FB858Fbd0D72A63bA8046E0); [Ostium vault](https://arbiscan.io/address/0x20d419a8e12C45f88fDA7c5760bb6923Cee27F98); DefiLlama Ostium $4.3M, Gains $6.5M, Vertex $0 — [ostium](https://api.llama.fi/protocol/ostium); [gains-network](https://api.llama.fi/protocol/gains-network); [vertex-perps](https://api.llama.fi/protocol/vertex-perps).

DEX liquidity
- Uniswap v3 WETH/USDC 0.05% 13.96M; WBTC/USDC 0.05% 3.66M; USDC/USDT 0.01% 0.29M; Uniswap v4 PoolManager 12.04M USDC (plus 1.01M USDG) — Arbiscan table above; DefiLlama Uniswap v3 Arbitrum $136.0M, v4 $38.6M (v4 was $443.6M a year ago) — [uniswap-v3](https://api.llama.fi/protocol/uniswap-v3); [uniswap-v4](https://api.llama.fi/protocol/uniswap-v4).
- Camelot v3 $4.7M, Curve $8.2M (2pool holds 0.16M USDC.e), PancakeSwap v3 $7.3M, Balancer v3 $0.9M, Ramses CL $0.1M (DefiLlama Arbitrum TVLs, 2026-10-10) — [camelot-v3](https://api.llama.fi/protocol/camelot-v3); [curve-dex](https://api.llama.fi/protocol/curve-dex); [pancakeswap-amm-v3](https://api.llama.fi/protocol/pancakeswap-amm-v3); [balancer-v3](https://api.llama.fi/protocol/balancer-v3); [ramses-cl](https://api.llama.fi/protocol/ramses-cl).

Yield/structured
- Pendle Arbitrum TVL $178.3M (vs $426.9M a year ago) but dominated by sUSDai (USD.AI) markets: DefiLlama's sUSDai page lists Pendle V2 $72.5M, $72.4M of it on Arbitrum, and ~$353M of sUSDai's AUM on Arbitrum — [DefiLlama pendle](https://api.llama.fi/protocol/pendle); [DefiLlama sUSDai](https://defillama.com/rwa/asset/sUSDai). Beefy $8.2M, Jones DAO $1.0M, Umami $0.4M, Yearn $0.2M, Spectra $0 on Arbitrum — [beefy](https://api.llama.fi/protocol/beefy); [jones-dao](https://api.llama.fi/protocol/jones-dao); [umami-finance](https://api.llama.fi/protocol/umami-finance); [yearn-finance](https://api.llama.fi/protocol/yearn-finance); [spectra](https://api.llama.fi/protocol/spectra).

Bridges
- Stargate v2 USDC pool 1.52M USDC (DefiLlama Stargate Arbitrum ~$9–10M all assets); Across SpokePool 0.10M; Synapse 0.0003M; Hop USDC bridge 0; Circle CCTP TokenMessenger holds 8 USDC (CCTP burns rather than locks) — [Stargate pool](https://arbiscan.io/address/0xe8CDF27AcD73a434D661C84887215F7598e7d0d3); [Across](https://arbiscan.io/address/0xe35e9842fceaCA96570B734083f4a58e8F7C5f2A); [stargate-v2](https://api.llama.fi/protocol/stargate-v2); [across](https://api.llama.fi/protocol/across).

Treasuries
- Arbitrum DAO treasury timelock `0xF3FC178157fb3c87548bAA86F9d24BA38E649B58` holds 6 USDC (on-chain read); the DAO's ATMC holds ~$66M in tokenized MMF and stablecoin positions and "may mint USDG from its stablecoin allocation" — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548). The Arbitrum Foundation reported non-native (ex-ARB) treasury assets of $125M at 30 Jun 2026 — [Arbitrum Foundation H1 2026 update, 2 Sep 2026](https://blog.arbitrum.foundation/arbitrum-foundation-reports-first-half-2026-progress-update/).

### Inferences
- Identifiable DeFi USDC on Arbitrum (lending supplied ~$250M + GM/perp vaults ~$110M + DEX pools ~$60M + misc ~$20M) is roughly $440M, i.e. ~16–17% of native supply; Hyperliquid bridge 14.6%; labeled CEX ≥12% (likely higher if the Binance-pattern proxies are exchange wallets); the remainder (~55%) is EOAs, unlabeled treasuries and small holders.
- DeFi USDC on Arbitrum has roughly halved in a year (Aave Arbitrum TVL −55%, GMX −54%, Uniswap v4 −91%, Pendle −58% y/y), so DeFi is a shrinking share of the holder base; the incentive-driven USDG programmes are entering a market where idle lending liquidity is scarce (Aave USDC at 89% utilisation).

### Gaps
- No Dune/Nansen "contract vs EOA" split for Arbitrum USDC was retrievable; the split above is built from Arbiscan labels and my own contract reads and does not cover every protocol (e.g., Silo/Euler/Camelot pool-level USDC balances).

## Key question 3: How concentrated is the holder base and how is the holder count growing?

### Takeaway
Arbiscan's live analytics on 2026-10-10 show top-5 = 28.8%, top-10 = 33.1%, top-100 = 53.8% of native USDC, a Gini of 0.9986, and 2,208 "whale" addresses (0.04% of holders) controlling 81.4% while 5.40M "shrimp" addresses (93.8%) hold 0.07%.

### Cited Findings
- Native USDC concentration (Arbiscan Holders Overview, snapshot 2026-10-10): Top 1–5 769.26M (28.81%); Top 6–10 115.43M (4.32%); Top 11–25 209.59M (7.85%); Top 26–50 177.05M (6.63%); Top 51–100 165.24M (6.19%); Outside top 100 1.23B (46.20%); 5 holders own ≥1% of supply — [Arbiscan holders](https://arbiscan.io/token/0xaf88d065e77c8cC2239327C5EDb3A432268e5831#balances).
- Tier distribution (same source): Whale 2,208 holders (0.04%) = 81.37% of supply; Shark 11,162 (0.19%) = 12.50%; Dolphin 37,831 (0.66%) = 4.60%; Fish 91,197 (1.58%) = 1.17%; Crab 212,179 (3.69%) = 0.28%; Shrimp 5,402,654 (93.84%) = 0.07%.
- USDC.e: top-100 concentration 63.0%, top-5 29.9%, top-10 37.4%, whale concentration 55.3% — [Arbiscan USDC.e holders](https://arbiscan.io/token/0xff970a61a04b1ca14834a43f5de4533ebddb5cc8#balances).
- Holder count: 5,757,813 (Arbiscan, 2026-10-10) vs ~5.64M on 29 Sep 2026 per a secondary guide — [Arbiscan](https://arbiscan.io/token/0xaf88d065e77c8cC2239327C5EDb3A432268e5831); [eco.com](https://eco.com/support/en/articles/14998919-usdc-on-arbitrum-complete-guide). Network-wide, Arbitrum reports ~90M addresses and nearly 3B transactions at USDG launch — [KuCoin](https://www.kucoin.com/blog/paxos-usdg-lands-on-arbitrum-defi-as-the-chain-holds-3-8-billion-in-stablecoins).
- Supply trend: $1.46B (Oct 2024) → $2.40B (Oct 2025) → $2.21B (Apr 2026) → $2.75B (Sep 2026) → $2.36B (10 Oct 2026) per DefiLlama — [chart API](https://stablecoins.llama.fi/stablecoincharts/Arbitrum?stablecoin=2).

### Inferences
- The ~5.4M shrimp addresses are economically irrelevant (~$1.9M combined); converting even all of them to USDG would not move supply. The addressable base is ~13,400 whale+shark addresses holding ~94% of USDC, and within that the top ~100 (54%).
- The September-to-October 2026 drop of ~$390M in DefiLlama's USDC figure coincides with the Hyperliquid bridge falling from $485.7M (11 Sep) to $389.4M (10 Oct), but that explains only ~$100M; the rest is unexplained outflow.

### Gaps
- Arbiscan does not publish its whale/shark dollar thresholds; "median balance" for retail was not available (the tier table implies the median holder has well under $1).
- No time series of holder-count growth was found beyond the two point estimates above.

## Key question 4: For Aave, Morpho, Fluid, GMX, Pendle (and Hyperliquid): USDC TVL, existing Paxos-stablecoin listings, listing decision-makers and process

### Takeaway
Morpho, Fluid and GMX already have USDG live on Arbitrum as of 6 Oct 2026 (Gauntlet and Steakhouse Morpho vaults ≈$16M, Fluid USDG/USDC pool, GMX GLV [USDG] vault ≈$5.65M); Aave has a Direct-to-AIP USDG-Arbitrum listing (TokenLogic, 8 Oct 2026, 30M cap, non-collateral); Pendle needs a yield-bearing USDG wrapper (e.g., Maple's syrupUSDG); Hyperliquid is contractually USDC-aligned via Coinbase.

### Cited Findings
Aave
- Aave v3 Arbitrum USDC supplied 178.8M / borrowed 159.9M (on-chain, 10 Oct 2026) — [aArbUSDCn](https://arbiscan.io/token/0x724dc807b04555b71ed48a6896b6F41593b8C637). TokenLogic's listing post notes USDC and USD₮0 reserves "run at high utilisation, while other stablecoin reserves are frozen or small" — [Aave governance, 8 Oct 2026](https://governance.aave.com/t/direct-to-aip-asset-listing-usdg-arbitrum/25811).
- USDG is already listed on Aave V3 Ethereum Core (deposit/borrow, not collateral; LlamaRisk conditioned support on a formal bug bounty; flagged Paxos's HSM-multisig admin and counterparty concentration); USDG supply on Aave grew from $94.1M to $123.2M in the 90 days to 8 Oct 2026; Chaos Labs recommended cutting USDG slope2 from 50% to 30% on Ethereum Core (Mar 2026) — [ARFC Onboard USDG to Aave V3 Core](https://governance.aave.com/t/arfc-onboard-usdg-to-aave-v3-core-instance/23271); [Chaos Labs USDG IR adjustment](https://governance.aave.com/t/chaos-labs-risk-stewards-usdg-interest-rate-adjustment-on-aave-v3-06-03-26/24242); [Direct-to-AIP USDG Arbitrum](https://governance.aave.com/t/direct-to-aip-asset-listing-usdg-arbitrum/25811).
- Arbitrum listing proposal (TokenLogic, created 8 Oct 2026): supply cap 30M, borrow cap 27.6M, collateral disabled, reserve factor 10%, IR curve matching Arbitrum USDC (slope1 4%, slope2 30%, optimal 90%), Chainlink USDG/USD with 1.04 cap adapter; steps: community feedback → Risk & Technical Service Provider feedback → deposit ≥$150 USDG to the Short Executor → AIP vote — [Aave governance](https://governance.aave.com/t/direct-to-aip-asset-listing-usdg-arbitrum/25811).
- Decision-makers: Chaos Labs exited Aave's risk mandate in April 2026; LlamaRisk absorbed its functions and now holds the Risk Council multisigs — [Chaos Labs is leaving Aave](https://governance.aave.com/t/chaos-labs-is-leaving-aave/24386); [LlamaRisk continuity post](https://governance.aave.com/t/llamarisk-ensuring-continuity-of-aaves-risk-management/24397); [Yahoo/CoinDesk coverage](https://finance.yahoo.com/markets/crypto/articles/chaos-labs-exits-aave-crypto-104536551.html).
- Precedent on PYUSD: Paxos is "the issuer of record for PYUSD" and PYUSD on Arbitrum is $359M (DefiLlama, 10 Oct 2026), having peaked at $475M in Q1 2026 — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548); [Arbitrum Foundation H1 2026](https://blog.arbitrum.foundation/arbitrum-foundation-reports-first-half-2026-progress-update/); [DefiLlama](https://stablecoins.llama.fi/stablecoins?includePrices=false). I found no Aave governance thread on PYUSD on Arbitrum.

Morpho
- Arbitrum USDG vaults live at launch: Gauntlet USDG Premium (`0x390c1bb01F3F627144a40617e287d4cE3D5aBCfa`, $10.73M) and Steakhouse USDG Pro (`0xbeeFf72B77e7584a450E887125F25E8D8819016a`, $5.39M) per Morpho API on 10 Oct 2026; Morpho Blue core holds 1.78M idle USDG; Morpho markets include Maple's syrupUSDG — [Morpho API](https://blue-api.morpho.org/graphql); [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/). By contrast Morpho's Arbitrum USDC vaults total under $3M.
- Listing is curator-driven (Gauntlet, Steakhouse, KPK, "Bitget x Steakhouse" vaults exist on Arbitrum); DRIP Season 1 routed 505K ARB in epochs 10–12 to Steakhouse vaults on Morpho for USDT0 borrowing and USDC/USDT0 lending — [DRIP January 2026 update](https://forum.arbitrum.foundation/t/drip-january-2026-update/30546).

Fluid
- Fluid hosts USDG DEX liquidity on Arbitrum; the Fluid Liquidity Layer holds 2.42M USDG and 6.25M idle USDC (10 Oct 2026); TokenLogic notes USDG's secondary liquidity on Arbitrum "is concentrated in the Fluid USDG/USDC pool" — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [Aave governance](https://governance.aave.com/t/direct-to-aip-asset-listing-usdg-arbitrum/25811); [Fluid Liquidity on Arbiscan](https://arbiscan.io/address/0x52Aa899454998Be5b000Ad077a46Bbe360F4e497). Fluid USDC lending vault = 55.4M (on-chain).

GMX
- GMX Dollar Vault "GLV [USDG-USDG]" launched 6 Oct 2026: USDG deposits spread across BTC/ETH/SOL GM pools, expected base 7–12% APR, plus an 8%+ boost for 8 weeks on up to $100M program TVL, funded by Arbitrum's USDG program and GMX; GM [USDG] pools open to whitelisted large depositors with a 5% boost (contact @GMXPartners, "USDG whitelist"); no deposit fee, withdrawal fee ≤0.04–0.07% — [GMX Substack, 6 Oct 2026](https://gmxio.substack.com/p/deposit-dollars-earn-dollars-the); [GMX interface PR #3009](https://github.com/gmx-io/gmx-interface/pull/3009). One report says the vault drew $5.65M and holds "nearly 20% of USDG on the network" — [Coinfomania](https://coinfomania.com/gmx-dollar-vault-secures-5-65m-in-deposits-boosting-usdg/). Existing USDC GM pools hold ~65M USDC (above).

Pendle
- Pendle Arbitrum TVL $178M is mostly sUSDai PT/YT markets (~$72M Pendle sUSDai TVL on Arbitrum, PTs at ~9–11% implied) rather than USDC — [DefiLlama sUSDai](https://defillama.com/rwa/asset/sUSDai); [USD.AI May 2026 recap](https://usd.ai/insights/usdai-may-2026-recap). I found no current Pendle USDC or USDG market on Arbitrum; Maple's syrupUSDG (live on Arbitrum via Morpho) is the obvious yield-bearing wrapper a Pendle market would need — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/).

Hyperliquid
- On 14 May 2026 Coinbase became Hyperliquid's official USDC treasury deployer (USDC as "aligned quote asset"); Native Markets agreed to let Coinbase buy USDH brand assets; USDH is being sunset with fee-free redemption to USDC — [The Block, 14 May 2026](https://www.theblock.co/news/ecosystems/2026-05-14-coinbase-hyperliquid-official-deployer-usdc-401233). Secondary coverage says that under "AQAv2" Coinbase shares "the vast majority of USDC reserve yields with Hyperliquid" and that Coinbase and Circle committed to stake HYPE — [Yellow](https://yellow.com/news/hyperliquid-routes-usdc-coinbase-usdh-winddown); [BeInCrypto](https://beincrypto.com/coinbase-usdh-hyperliquid-shifts-to-usdc/). (Coinbase's own blog returned 403.)

### Inferences
- Paxos has already cleared the hardest listing gates on Arbitrum (Morpho, Fluid, GMX live; Aave in Direct-to-AIP); the binding constraint is now liquidity and demand, not listing approval. The Aave listing being non-collateral means USDG cannot yet be used for looping, which limits its appeal versus USDC for the leveraged-borrow demand DRIP created.
- Hyperliquid is the one large segment where USDG is structurally excluded: the quote asset is contractually USDC with reserve yield shared back to Hyperliquid, so a GDN-style yield share has no differentiated pitch there.

### Gaps
- Compound v3, Dolomite, Silo and Euler listing processes/decision-makers for USDG on Arbitrum were not researched (small USDC balances).
- No source gave the exact GDN reward-share percentage; the Arbitrum proposal says rewards accrue "based on USDG held, minted, and accepted" without a formula.

## Key question 5: Which holders are yield-sensitive, liquidity-sensitive, or structurally locked to USDC?

### Takeaway
Yield-sensitive capital is the ~$440M in Arbitrum DeFi (lending suppliers, GM/GLV LPs, Morpho/Steakhouse depositors) plus the ~$60M of round-balance unlabeled treasuries; liquidity-sensitive capital is CEX hot wallets (~$326M+), market makers and perp venues' margin pools; structurally locked is the Hyperliquid bridge ($390M, shrinking) and CCTP-dependent flows.

### Cited Findings
- DRIP Season 1 (3 Sep 2025–17 Feb 2026, 24M ARB budget, Aave/Morpho/Fluid/Euler/Dolomite/Silo) grew dollar-denominated lending markets 38% to ~$770M and yield-bearing stablecoin supply from $130M to >$1B — demonstrating that Arbitrum lenders move for incentives — [DRIP Season 1 recap](https://forum.arbitrum.foundation/t/drip-season-1-launch-recap/29921); [Castle Labs](https://research.castlelabs.io/p/inside-arbitrum-drip-season-1); [SpotedCrypto summary](https://www.spotedcrypto.com/paxos-usdg-arbitrum-launch-drip-proposal/). Castle Labs notes incentive-driven market size "later declined following the ETH price and broader market weakness" — [Castle Labs](https://research.castlelabs.io/p/inside-arbitrum-drip-season-1).
- Observational +180-day borrowing retention vs baseline after DRIP S1 (independent analyst NikitaOnchain in the USDG thread): Fluid 128%, Morpho 203%, Aave V3 36%, Dolomite 28%, Silo V2 15%, Euler V2 2%, Compound V3 (not in DRIP) 32% — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548).
- GDN partners earn reserve rewards "according to the USDG demand it creates"; Arbitrum will reinvest the majority during the growth phase into builder incentives, each deal requiring ⅔ DRIP-committee approval; Merkl is the distribution partner — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548).
- Hyperliquid bridge Arbitrum-side TVL (DefiLlama): $602M (11 Oct 2024) → $2,077M (19 Apr 2025) → $5,120M (11 Oct 2025) → $3,524M (14 Apr 2026) → $374M (13 Jul 2026) → $486M (11 Sep 2026) → $389M (10 Oct 2026); Hyperliquid L1-side $6,584M; USDC on Hyperliquid L1 $7,154M — [DefiLlama hyperliquid-bridge API](https://api.llama.fi/protocol/hyperliquid-bridge); [DefiLlama stablecoins](https://stablecoins.llama.fi/stablecoins?includePrices=false). Hyperliquid announced (Dec 2025) that USDC is linked between HyperCore and HyperEVM with CCTP deposits from Arbitrum deployed by Circle and that "in the final state, the Arbitrum bridge will be deprecated and all USDC will be natively minted" — [Hyperliquid on X](https://x.com/HyperliquidX/status/1997852864308486319); [CCN](https://www.ccn.com/news/technology/hyperliquid-retires-arbitrum-bridge-for-native-usdc/). Circle launched native USDC and CCTP V2 on HyperEVM in Sep 2025 — [Circle on X](https://x.com/circle/status/1967928959947116873).
- Kraken (GDN partner) supports USDG deposits/withdrawals on Arbitrum One; Robinhood, OKX, Mastercard, Bullish are GDN partners; Robinhood Chain (built on Arbitrum tech) uses USDG as its dollar asset with $700.8M USDG there (DefiLlama) and bridges inbound USDC to USDG via relayer — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [Arbitrum Robinhood Chain post](https://blog.arbitrum.io/robinhood-chain-mainnet/); [DefiLlama](https://stablecoins.llama.fi/stablecoins?includePrices=false).
- Circle's own hot wallet holds $11.4M USDC on Arbitrum; Spark PSM 3 (Sky) holds $10.0M — Arbiscan table above.

### Inferences
- Yield-sensitive (move for GDN yield share / DRIP): Aave USDC suppliers ($179M; most are passive lenders earning ~1.5–3%), Fluid lenders ($55M), GM/GLV LPs (~$65M in GM USDC, already offered a GLV[USDG] with 8%+ boost), Morpho/Steakhouse depositors (<$3M USDC but the curators already run USDG vaults), Compound ($15M), Beefy/Jones/Umami aggregators (~$10M), Pendle users (if a syrupUSDG PT market exists), ATMC/DAO treasury (~$66M MMF+stables), and the ~$60M of round-balance treasuries.
- Liquidity-sensitive (need deep pairs, fast on/off-ramps): Binance HW34 ($272M), BingX, Crypto.com, Coinbase 83, Bybit, KuCoin (~$54M), Variational/Aster/Ostium/Gains margin and treasuries (~$61M), Uniswap v3/v4 LPs (~$30M USDC in top pools), the labeled market maker ($5.7M). These will only hold USDG once CEX listings of USDG-on-Arbitrum withdrawals (Kraken is live; Binance/OKX/Bybit are not evidenced) and a USDG/USDC pool deeper than Fluid's current ~$2.4M USDG exist.
- Structurally locked to USDC: Hyperliquid Bridge2 ($390M, with Coinbase as USDC treasury deployer and bridge migration to native CCTP mint), CCTP flows, Circle hot wallet, Coinbase 83, Spark PSM (Sky's USDC peg module). Note the bridge is already down ~92% from its Oct 2025 peak; the remaining balance is a float that the bridge's deprecation plan will drain regardless of Paxos action.

### Gaps
- I found no article dating or sizing the 2026 bulk migration of bridge USDC to natively minted USDC (the DefiLlama series shows the $3.1B drop between April and July 2026 but no source narrates it).
- No evidence either way on Binance/OKX/Bybit supporting USDG withdrawals on Arbitrum.

## Key question 6: Precedents of Arbitrum protocols adding or switching a base stablecoin, and the incentives attached

### Takeaway
Every Arbitrum stablecoin onboarding with traction (GHO on Aave, USDe on GMX, USDT0 on Morpho/Aave, syrupUSDC on Fluid/Morpho, sUSDai on Pendle) was paired with ARB incentives via STIP/STIP-Bridge/DRIP; USDG's own launch follows the template with ~7M ARB (>$10M) seed incentives, an 8-week GMX boost and a proposed 100M-ARB DRIP top-up.

### Cited Findings
- GMX added an ETH-USD [wstETH-USDe] GM market with ARB incentives for early LPs (funded from GMX's 5.4M-ARB STIP-Bridge allocation), 20x Ethena points, and a ~25% APR target per GM pool on weekly epochs — [GMX Substack](https://gmxio.substack.com/p/gmx-launches-an-eth-usd-wsteth-usde); [GMX STIP-Bridge update](https://forum.arbitrum.foundation/t/gmx-stip-b-bi-weekly-update-6/26717).
- Aave GHO launched on Arbitrum mid-2024 (bridged via CCIP, not natively mintable); bridging inflows were "primarily driven by the ARB incentive program for GHO borrowing, led by ACI" plus Merit rewards; the Arbitrum DAO grant's success KPI was GHO supply ≥10x grant size at 6 months and 15x at 12 months; supply was 5M GHO by Oct 2024 — [Aave governance: GHO Safety Module on Arbitrum](https://governance.aave.com/t/temp-check-activate-and-deploy-gho-safety-module-on-arbitrum/17805); [GHO on Base ARFC (lessons from Arbitrum)](https://governance.aave.com/t/arfc-launch-gho-on-base-set-aci-as-emissions-manager-for-rewards/19338); [The Defiant](https://thedefiant.io/news/defi/aave-launches-gho-stablecoin-on-arbitrum).
- DRIP Season 1 discretionary allocations: 325K ARB for syrupUSDC markets on Morpho and Fluid (epochs 3–5); 505K ARB for Steakhouse Morpho vaults, mostly USDT0 borrowing and USDC/USDT0 lending (epochs 10–12); Aave rewards paused in Oct 2025 then 400K ARB (epoch 10) and 200K (epoch 11); USDai/sUSDai were added to DRIP (Sep 2025) — [DRIP October 2025 update](https://forum.arbitrum.foundation/t/drip-october-2025-update/30187); [DRIP January 2026 update](https://forum.arbitrum.foundation/t/drip-january-2026-update/30546); [Dablendo on X](https://x.com/Dablendo01/status/1964330751580672089). Total S1 spend is reported as 16.705M ARB (Jan 2026 projection) vs 14.6M ARB (secondary summary) — conflict — [DRIP Jan 2026](https://forum.arbitrum.foundation/t/drip-january-2026-update/30546); [SpotedCrypto](https://www.spotedcrypto.com/paxos-usdg-arbitrum-launch-drip-proposal/).
- USDG launch incentives: ">$10 million in incentives through DRIP" (Arbitrum blog) / "about 7 million ARB" (KuCoin); proposal to add 100M ARB to DRIP, bringing DRIP to ~165M ARB including ~65M unspent, merging Seasons 2–4 into one USDG season, allowing POL seeding and liquidity arrangements, mandate through ~12 Nov 2026 (one-year mark) — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/); [KuCoin](https://www.kucoin.com/blog/paxos-usdg-lands-on-arbitrum-defi-as-the-chain-holds-3-8-billion-in-stablecoins); [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548). The proposal targets capturing 15–20% of the ~$4B float in year one ("hundreds of millions" of USDG) and routes all AEP fees (net of 20% to the Developer Guild) into USDG — same forum source.
- Early USDG traction on Arbitrum (10 Oct 2026, four days post-launch): total supply 29.24M; Fluid 2.42M, Morpho Blue 1.78M, Uniswap v4 1.01M, Morpho V2 USDG vaults ~$16.1M, GMX Dollar Vault ~$5.65M (press) — on-chain reads cited above; [Coinfomania](https://coinfomania.com/gmx-dollar-vault-secures-5-65m-in-deposits-boosting-usdg/).

### Inferences
- The GHO KPI template (supply ≥10x grant) and DRIP retention data (Fluid/Morpho retained >100% of borrowing at +180d; Aave 36%) suggest Paxos should concentrate USDG incentives on Fluid and Morpho (sticky) and treat Aave as a listing-for-credibility rather than a retention engine.
- Hyperliquid's own switch (USDH → USDC with Coinbase yield-share) shows that venues will choose the stablecoin whose issuer shares reserve economics; GDN's partner-reward model is the same mechanism, so the pitch to Variational, Aster, Ostium and Gains (USDC-margined perps, ~$60M) is a direct reserve-share deal rather than ARB emissions.

### Gaps
- No source quantifies the size of the Fluid USDG/USDC pool or the Uniswap USDG pool beyond on-chain contract balances.
- The forum page contains an inconsistency on DRIP mandate end (12 Nov 2026 vs an approved extension to 1 Jul 2027); unresolved.

## Segment map with sizes, addressability and USDG outreach priority (as of 10 Oct 2026)

### Takeaway
Ranked by expected convertible dollars per unit of effort: (1) DeFi lending/LP capital already integrated (Aave/Fluid/GMX/Morpho, ~$320M USDC) and (2) Arbitrum DAO/Foundation treasuries (~$66M ATMC + $125M Foundation non-ARB assets) are top priority; CEX wallets (~$330M+) are second (need listings); unlabeled round-balance treasuries (~$60M) third; Hyperliquid bridge ($390M) is not addressable.

### Cited Findings (segment table; figures from sections above)
1. Hyperliquid bridge — $389.7M USDC (14.6%), down from $5.12B (Oct 2025); used as deposit custody for HyperCore; USDC is the contractual quote asset with Coinbase as treasury deployer; bridge slated for deprecation in favour of native CCTP mint. Addressability: none. Priority: 11 (skip) — [DefiLlama](https://api.llama.fi/protocol/hyperliquid-bridge); [The Block](https://www.theblock.co/news/ecosystems/2026-05-14-coinbase-hyperliquid-official-deployer-usdc-401233).
2. Lending — Aave $178.8M supplied (89% utilised), Fluid $55.4M, Compound $14.9M, Morpho <$3M USDC (but $16.1M USDG), Dolomite ~$1.2M, Silo/Euler ≈0. Use: passive yield and collateral for looping. Needs: Aave AIP approval (in flight), collateral enablement later, DRIP/Merkl rewards on USDG supply/borrow, Fluid USDG vault + looping, curator vaults. Priority: 1 — sources in Q2/Q4.
3. DEX liquidity — Uniswap v3 ~$18M USDC in top three pools, v4 $12.0M, Curve/Camelot/Pancake/Balancer/Ramses ~$21M TVL combined. Use: fee income, routing. Needs: USDG/USDC concentrated pool with POL seeding (proposal allows POL) and Merkl LP rewards; Uniswap integration "set to follow". Priority: 5 — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548); [CoinDesk](https://www.coindesk.com/business/2026/10/05/arbitrum-joins-paxos-led-stablecoin-group-global-dollar-to-capture-digital-dollar-growth).
4. Perps/derivatives — GMX GM pools ~$65.4M USDC; Variational OLP + treasury $36.7M; Aster treasury $18.1M; Gains $4.2M; Ostium $2.3M; Vertex/Synthetix ≈0. Use: LP collateral / margin. Needs: GLV[USDG] boost already live for GMX; for Variational/Aster/Ostium/Gains a USDG-margin option plus GDN reserve-share. Priority: 2 (GMX) / 4 (others) — Arbiscan table; [GMX Substack](https://gmxio.substack.com/p/deposit-dollars-earn-dollars-the).
5. Yield/structured — Pendle $178M (mostly sUSDai, not USDC); Beefy $8.2M; Jones $1.0M; Umami $0.4M; Yearn $0.2M. Needs: a syrupUSDG or vault-token PT market on Pendle; Beefy/Yearn strategies on USDG vaults. Priority: 6 — [DefiLlama pendle](https://api.llama.fi/protocol/pendle).
6. CEX hot wallets — Binance HW34 $272.5M; BingX cold $21.6M; Crypto.com 4 $11.4M; Coinbase 83 $10.0M; Bybit W4 $5.1M; KuCoin 15 $5.0M; OKX 230 $0.3M USDC.e; plus ~$80.8M in Binance-pattern proxies (inferred). Use: customer withdrawal/deposit float. Needs: USDG-on-Arbitrum deposit/withdrawal listing (Kraken live; OKX and Robinhood are GDN members but no Arbitrum-rail evidence), partner reward share. Priority: 3 — Arbiscan table; [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/).
7. Treasuries/DAOs — Arbitrum DAO timelock ~0 USDC but ATMC ~$66M MMF+stables (may mint USDG), AEP fees to be converted to USDG; Arbitrum Foundation $125M non-ARB assets (composition unknown); Aster treasury $18.1M; Variational treasury $10.4M; Spark PSM 3 $10.0M (Sky; structurally USDC); Camelot POL $0.3M USDC.e; GMX DAO/Treasure not found in top holders. Priority: 1 (Arbitrum entities) / 4 (project treasuries) — [Arbitrum forum](https://forum.arbitrum.foundation/t/adopting-usdg-as-a-core-strategic-initiative-for-the-arbitrumdao/31548); [Arbitrum Foundation H1 2026](https://blog.arbitrum.foundation/arbitrum-foundation-reports-first-half-2026-progress-update/).
8. Bridges/cross-chain — Stargate v2 USDC pool $1.5M (Stargate already carries USDG via LayerZero), Across $0.1M, Synapse/Hop ≈0, CCTP holds nothing (burn/mint), Multichain anyUSDC $0.67M USDC.e stranded. Use: transit float. Addressability: already done (Stargate/LI.FI/LayerZero integrated). Priority: 8 — [Arbitrum blog](https://blog.arbitrum.io/usdg-is-live-on-arbitrum/).
9. Payments/fintech/RWA — PYUSD $359M on Arbitrum (Paxos-issued; peak $475M Q1 2026) is the closest analogue and could be the first "conversion" cohort; Circle hot wallet $11.4M (locked); Robinhood Chain holds $700.8M USDG on its own chain; Mastercard expanded stablecoin settlement on Arbitrum (no figures); BUIDL/BENJI/USDY are deployed on Arbitrum per secondary sources but no Arbitrum-specific AUM found. Priority: 2 (PYUSD holders, Robinhood/Kraken rails) — [DefiLlama](https://stablecoins.llama.fi/stablecoins?includePrices=false); [Arbitrum Foundation H1 2026](https://blog.arbitrum.foundation/arbitrum-foundation-reports-first-half-2026-progress-update/); [eco.com tokenized treasuries](https://eco.com/support/en/articles/15210582-top-tokenized-treasury-funds-2026-buidl-ousg-usdy-benji-compared).
10. Market makers/whales — labeled "Market Maker 0x51c7…2a7f" $5.7M USDC + $0.4M USDC.e; ~$364M across 31 unlabeled top-50 addresses (≈$60M in round-number balances); Wintermute/Jump addresses I checked hold ~0 on Arbitrum. Needs: OTC mint/redeem at par with Paxos, reward-share for held balances. Priority: 3 — Arbiscan table.
11. Long-tail retail — 5.40M shrimp addresses hold 0.07% ($1.9M); 212K crabs 0.28%; 91K fish 1.17%; 37.8K dolphins 4.6%. Needs: wallet/portal default (Arbitrum Portal "stablecoin earn"), Kraken/Robinhood on-ramps. Priority: 9 (brand, not dollars) — [Arbiscan](https://arbiscan.io/token/0xaf88d065e77c8cC2239327C5EDb3A432268e5831#balances); [CryptoBriefing on Arbitrum Portal earn](https://cryptobriefing.com/morpho-stablecoin-earn-arbitrum-portal/).

### Inferences
- Realistic year-one convertible pool: DeFi ~$320M (lending + GM) + Arbitrum entities ~$100M + PYUSD-adjacent ~$359M (already Paxos) + CEX float contingent on listings ~$300M. This is consistent with the DAO's own 15–20% of $4B target ("hundreds of millions").
- USDC.e ($48M) is a wind-down asset; targeting it is low value except for the single $8.7M unlabeled holder.

### Gaps
- Entity attribution for the unlabeled top-50 addresses, CEX-by-CEX USDG rail status, Foundation treasury composition, Fluid/Uniswap USDG pool depths, and Arbitrum-specific BUIDL/BENJI/USDY balances remain unverified.

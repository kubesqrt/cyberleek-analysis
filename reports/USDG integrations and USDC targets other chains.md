# USDG integrations and USDC targets on chains other than Arbitrum

Snapshot 10 October 2026. Source: DefiLlama per-protocol token breakdowns (supplied = idle + borrowed on each chain), cross-checked with the USDG footprint notes. Amounts in $M. Protocols already covered in the Arbitrum list are excluded from section 2 and shown in the appendix instead.

USDG is natively issued on Ethereum, Solana, Ink, X Layer, Robinhood Chain, Mantle and Arbitrum. USDG0 (LayerZero wrapper) exists on Hyperliquid, Plume and Aptos but holds only about $1.3M.

## 1. Protocols that already hold or integrate USDG (outside Arbitrum)

| Chain | Protocol | Category | USDG ($M) | USDC on same chain ($M) |
|---|---|---|---:|---:|
| X Layer | OKX | CEX | 1145.6 | 0.0 |
| Robinhood Chain | Morpho Blue | Lending | 553.4 | 0.0 |
| Robinhood Chain | Steakhouse Financial | Risk Curators | 548.1 | 0.0 |
| Ethereum | Maple | Lending | 403.5 | 3622.0 |
| Ethereum | Aave V4 | Lending | 115.6 | 45.2 |
| Solana | OKX | CEX | 113.1 | 0.0 |
| Robinhood Chain | Lighter Robinhood Perps | Derivatives | 101.9 | 0.0 |
| Solana | Kamino Lend | Lending | 79.3 | 315.9 |
| X Layer | Pendle V2 | Yield | 63.7 | 0.0 |
| Solana | Steakhouse Financial | Risk Curators | 47.4 | 22.4 |
| Solana | Gate | CEX | 20.3 | 4.7 |
| Robinhood Chain | Grove Finance | Onchain Capital Allocator | 15.1 | 0.0 |
| Robinhood Chain | Fables | Dexs | 10.9 | 0.0 |
| Solana | KuCoin | CEX | 10.7 | 11.2 |
| Solana | Ourbit | CEX | 10.1 | 0.6 |
| Ethereum | Curve DEX | Dexs | 9.4 | 108.4 |
| Solana | SwissBorg | CEX | 7.1 | 5.2 |
| Solana | Loopscale Lending | Lending | 4.8 | 43.4 |
| Ethereum | Aave V3 | Lending | 4.6 | 2412.9 |
| Solana | Jupiter Lend | Lending | 3.0 | 509.0 |
| Robinhood Chain | Ramses CL V2 | Dexs | 2.2 | 0.0 |
| Robinhood Chain | Arrakis Modular | Liquidity Manager | 1.7 | 0.0 |
| Ethereum | Arrakis Modular | Liquidity Manager | 1.6 | 7.2 |
| Robinhood Chain | Snuggle | Liquidity Manager | 1.6 | 0.0 |
| X Layer | Aave V3 | Lending | 1.5 | 3.6 |
| Robinhood Chain | SushiSwap V3 | Dexs | 1.5 | 0.0 |
| Solana | Manifest Trade | Dexs | 1.5 | 6.1 |
| Ink | Tydro | Lending | 1.5 | 68.4 |
| Ethereum | Pendle V2 | Yield | 1.4 | 0.0 |
| Ethereum | LayerZero V2 | Bridge | 1.3 | 52.1 |
| Robinhood Chain | Uniswap V2 | Dexs | 1.3 | 0.0 |
| Robinhood Chain | Longbow | Lending | 1.1 | 0.0 |
| Robinhood Chain | Beefy | Yield Aggregator | 1.1 | 0.0 |
| Robinhood Chain | Mellow Core | Onchain Capital Allocator | 1.0 | 0.0 |
| Robinhood Chain | up v3 | Dexs | 0.6 | 0.0 |
| Ethereum | Ekubo | Dexs | 0.6 | 0.3 |
| Robinhood Chain | Ekubo | Dexs | 0.5 | 0.0 |
| Solana | Sentora Curator | Risk Curators | 0.4 | 0.0 |
| Solana | OSL Exchange | CEX | 0.3 | 0.5 |
| Robinhood Chain | Symbiosis | Cross Chain Bridge | 0.2 | 0.0 |
| Robinhood Chain | T3tris Finance | Onchain Capital Allocator | 0.2 | 0.0 |
| Ink | Velodrome V3 | Dexs | 0.2 | 0.4 |
| Robinhood Chain | Native Credit Pool | Lending | 0.2 | 0.0 |
| Ethereum | Origin ARM | Yield | 0.1 | 0.1 |
| Robinhood Chain | UNCX Network V4 | Token Locker | 0.1 | 0.0 |
| Robinhood Chain | Pendle V2 | Yield | 0.1 | 0.0 |
| Robinhood Chain | Curve DEX | Dexs | 0.1 | 0.0 |

Not captured by DefiLlama token breakdowns but documented in the footprint notes: Orca and Raydium USDG/USDC pools on Solana (~$18M and ~$3M), Jupiter Lend USDG vaults (~$60M), Kamino USDG market with KMNO rewards, Loopscale, Marinade "Stake SOL, Earn USDG", Solstice eUSX and OnRe ONyc using USDG as base asset, Aave V3 on X Layer PT-USDG market (~$60M), Uniswap V4 USDC/USDG pool on Ethereum (~$3.3M), Velodrome and Tydro on Ink (~$1M each), Kraken and OKX exchange rails, Robinhood Earn.

## 2. USDC holders on other chains not yet integrated with USDG (new names only, supplied USDC over $1M)


### Ethereum (USDG native on this chain; 147 candidates, 9,810 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Sky Lending | CDP | 4424.5 |
| Polygon Bridge | Chain | 1009.0 |
| Lighter Bridge | Bridge | 615.4 |
| MEXC | CEX | 340.6 |
| Anemoy Capital | RWA | 326.3 |
| M0 | Stablecoin Issuer | 203.1 |
| Re | RWA | 190.6 |
| Upshift | Onchain Capital Allocator | 179.2 |
| Armitage by Wintermute | Risk Curators | 123.2 |
| RockawayX | Risk Curators | 114.3 |
| Avalon Superearn | Yield | 111.5 |
| Deribit | CEX | 106.4 |
| Wildcat Protocol | Uncollateralized Lending | 102.1 |
| Huma | RWA | 100.0 |
| cap | Lending | 73.9 |
| Circle Gateway | Cross Chain Bridge | 66.9 |
| USDCx | Stablecoin Wrapper | 66.9 |
| KPK | Risk Curators | 64.4 |
| infiniFi | Yield | 58.1 |
| Arbitrum Bridge | Canonical Bridge | 52.9 |
| Crypto-com | CEX | 52.1 |
| SparkLend | Lending | 48.3 |
| Fluid Lite | Yield Aggregator | 43.9 |
| Yearn Finance | Yield Aggregator | 42.0 |
| Makina | Onchain Capital Allocator | 37.9 |
| Clearstar | Risk Curators | 37.4 |
| Derive V3 Options | Options | 36.8 |
| Ember Protocol | Onchain Capital Allocator | 35.2 |
| dYdX V3 | Derivatives | 32.3 |
| Paradex Bridge | Bridge | 32.3 |
| Avalanche Core Bridge | Canonical Bridge | 32.1 |
| Bitstamp | CEX | 31.8 |
| Euler V2 | Lending | 30.5 |
| Theo Network thUSD | RWA | 29.7 |
| OpenTrade | RWA | 28.3 |
| Veda | Onchain Capital Allocator | 27.8 |
| ether.fi Liquid | Onchain Capital Allocator | 27.4 |
| Nonce Capital | Risk Curators | 27.2 |
| Optimism Bridge | Canonical Bridge | 25.7 |
| Contango V2 | Derivatives | 23.7 |
| Waterline | Risk Curators | 23.5 |
| zkSync Era txBridge | Canonical Bridge | 22.7 |
| Mantle Bridge | Canonical Bridge | 22.3 |
| CCIP | Bridge | 21.8 |
| Aave V2 | Lending | 20.6 |
| Aera V2 | Onchain Capital Allocator | 20.5 |
| Toobit | CEX | 20.0 |
| Piku Finance | Basis Trading | 19.0 |
| Galaxy Curation | Risk Curators | 18.3 |
| Yearn Curating | Risk Curators | 18.1 |
| Y10K Capital | Risk Curators | 17.8 |
| Hyperithm | Risk Curators | 17.3 |
| Api3 | Risk Curators | 16.9 |
| Railgun | Privacy | 16.7 |
| Bitfinex | CEX | 16.6 |
| Gami Labs | Risk Curators | 16.5 |
| Hakutora | Risk Curators | 15.8 |
| Phemex | CEX | 15.4 |
| xDAI Stake Bridge | Canonical Bridge | 15.0 |
| Enzyme Finance | Indexes | 14.9 |
| NEAR Bridge | Canonical Bridge | 14.9 |
| PulseChain Bridge | Canonical Bridge | 14.5 |
| Axelar | Bridge | 13.7 |
| Syntropia | Yield Aggregator | 13.1 |
| Ethena USDe | Basis Trading | 12.7 |
| SX Rollup Bridge | Canonical Bridge | 10.9 |
| Sierra Protocol | Yield | 10.4 |
| Flux Finance | Lending | 10.3 |
| YieldNest | Onchain Capital Allocator | 9.6 |
| Sky Money | Risk Curators | 9.3 |
| Fusion by IPOR | Onchain Capital Allocator | 8.8 |
| Reserve Protocol | Indexes | 8.5 |
| Tulipa Capital | Risk Curators | 8.4 |
| Byte Exchange | CEX | 8.3 |
| AUTOfinance | Yield | 8.2 |
| Agua | Onchain Capital Allocator | 8.0 |
| Alchemix V3 | Synthetics | 7.7 |
| Katana Pre-Launch | Farm | 7.7 |
| Compound V2 | Lending | 7.7 |
| NEMO Trading | Risk Curators | 7.7 |
| Keyrock | Risk Curators | 7.4 |
| Seamless V2 | Lending | 7.2 |
| Dialectic | Risk Curators | 7.0 |
| UltraYield Curator | Risk Curators | 6.9 |
| UltraYield Vaults | Onchain Capital Allocator | 6.8 |
| Yuzu Money | Yield | 6.7 |
| Superform | Yield Aggregator | 6.7 |
| Base Bridge | Canonical Bridge | 6.5 |
| VALR | CEX | 6.4 |
| BloFin | CEX | 6.2 |
| Legion | Launchpad | 6.1 |
| Resolv USR | Basis Trading | 6.1 |
| Origin Dollar | Yield Aggregator | 6.1 |
| TAU Labs | Risk Curators | 6.0 |
| Royco V2 | Yield | 5.8 |
| 9Summits | Risk Curators | 5.6 |
| Re7 Labs | Risk Curators | 5.3 |
| Scroll Bridge | Canonical Bridge | 4.9 |
| Starknet Bridge | Canonical Bridge | 4.7 |
| Presto | Risk Curators | 4.3 |
| Lista Lending | Lending | 4.3 |
| Polygon zkEVM Bridge | Canonical Bridge | 4.3 |
| K3 Capital | Risk Curators | 4.2 |
| Metis Bridge | Canonical Bridge | 4.2 |
| 1212 Capital | Risk Curators | 3.6 |
| BYDFi | CEX | 3.3 |
| Multichain | Bridge | 3.1 |
| Strata Markets | Yield | 3.1 |
| Kamui | RWA | 3.1 |
| cBridge | Bridge | 3.0 |
| Niza | CEX | 2.9 |
| TermFinance Lend | Lending | 2.9 |
| Zama | Privacy | 2.8 |
| Aave Horizon RWA | Lending | 2.6 |
| PoolTogether V3 | Yield Lottery | 2.6 |
| Symbiotic | Collateral Markets | 2.6 |
| FermiSwap | Dexs | 2.5 |
| fx Protocol | Dual-Token Stablecoin | 2.5 |
| Immutable zkEVM | Chain | 2.5 |
| Rysk V12 | Options Vault | 2.4 |
| THORChain DEX | Dexs | 2.4 |
| eva Markets | RWA | 2.4 |
| Cronos zkEVM Bridge | Canonical Bridge | 2.2 |
| MEV Capital | Risk Curators | 2.2 |
| CEX.IO | CEX | 2.2 |
| Chain Fusion | Decentralized BTC | 2.0 |
| NaraUSD | RWA | 2.0 |
| APX Bridge | Bridge | 1.8 |
| Pickle | Yield Aggregator | 1.7 |
| HashKey Exchange | CEX | 1.7 |
| Poloniex | CEX | 1.6 |
| LeveX | CEX | 1.5 |
| Fuel Bridge | Bridge | 1.5 |
| YO Protocol | Yield Aggregator | 1.4 |
| Across | Cross Chain Bridge | 1.4 |
| SharpByte Capital | Risk Curators | 1.4 |
| Manta Pacific | Canonical Bridge | 1.4 |
| Harvest Finance | Yield Aggregator | 1.4 |
| BitVenus | CEX | 1.3 |
| Morpho Midnight | Lending | 1.3 |
| Okcoin | CEX | 1.3 |
| Reservoir Protocol | CDP | 1.3 |
| Vectis Finance | Yield | 1.3 |
| Sonic Gateway | Canonical Bridge | 1.1 |
| Superfluid | Payments | 1.1 |
| Backpack | CEX | 1.0 |
| mStable V2 | CDP | 1.0 |

### Solana (USDG native on this chain; 38 candidates, 954 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Jupiter Perpetual Exchange | Derivatives | 272.4 |
| Huma | RWA | 162.9 |
| Save | Lending | 130.3 |
| RockawayX | Risk Curators | 62.2 |
| Lulo | Yield Aggregator | 30.5 |
| Pacifica Perps | Derivatives | 26.6 |
| GMX Solana | Derivatives | 25.3 |
| Phoenix Perp | Derivatives | 22.5 |
| Neutral Trade | Onchain Capital Allocator | 22.1 |
| PumpSwap | Dexs | 19.5 |
| Project 0 | Lending | 16.3 |
| Backpack | CEX | 12.9 |
| Jupiter Lend DEX | Dexs | 12.8 |
| Unitas USDu | Basis Trading | 12.4 |
| Meteora vaults | Yield Aggregator | 9.8 |
| Serum | Dexs | 9.7 |
| BisonFi | Dexs | 9.7 |
| Upshift | Onchain Capital Allocator | 8.8 |
| Meteora DAMM V1 | Dexs | 8.3 |
| marginfi Lending | Lending | 7.9 |
| BULK | Derivatives | 7.8 |
| Futarchy AMM | Dexs | 7.3 |
| Exponent Strategy Vaults | Onchain Capital Allocator | 6.8 |
| Loopscale Curation | Risk Curators | 6.8 |
| Meteora DAMM V2 | Dexs | 6.5 |
| Tessera V | Dexs | 4.3 |
| Vectis Finance | Yield | 3.9 |
| JupUSD | Basis Trading | 3.6 |
| Byreal | Dexs | 3.1 |
| GoonFi | Dexs | 3.0 |
| Bumpin Trade | Derivatives | 2.7 |
| DOOAR V2 | Dexs | 2.7 |
| Phemex | CEX | 2.7 |
| MEXC | CEX | 2.7 |
| NEAR Bridge | Canonical Bridge | 2.4 |
| Bitstamp | CEX | 2.1 |
| Realms | Governance Incentives | 1.9 |
| VALR | CEX | 1.2 |

### Ink (USDG native on this chain; 2 candidates, 331 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Veda | Onchain Capital Allocator | 328.9 |
| Nado Spot | Dexs | 2.4 |

### Mantle (USDG native on this chain; 3 candidates, 37 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| CIAN Yield Layer | Yield Aggregator | 34.0 |
| IntentX | Derivatives | 2.3 |
| Agni Finance | Dexs | 1.1 |

### Hyperliquid L1 (USDG0 wrapper only; 12 candidates, 468 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Hyperliquid HLP | Derivatives | 180.8 |
| Hyperliquid Spot Orderbook | Dexs | 165.4 |
| HyperLend Pooled | Lending | 54.8 |
| Felix Vaults | Onchain Capital Allocator | 17.9 |
| GrowiHF | Yield | 13.6 |
| Rysk V12 | Options Vault | 11.2 |
| Project X | Dexs | 8.0 |
| nest CL | Dexs | 5.2 |
| Hyperbeat Earn | Yield Aggregator | 4.6 |
| Monetrix USDM | Basis Trading | 3.1 |
| K3 Capital | Risk Curators | 2.1 |
| Upshift | Onchain Capital Allocator | 1.7 |

### Plume Mainnet (USDG0 wrapper only; 2 candidates, 39 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| OpenTrade | RWA | 32.7 |
| Sierra Protocol | Yield | 6.0 |

### Aptos (USDG0 wrapper only; 4 candidates, 41 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Decibel | Derivatives | 29.5 |
| KAIO | RWA | 6.6 |
| Echelon Market | Lending | 2.8 |
| Aptin Finance V2 | Lending | 2.3 |

### Base (no USDG on this chain; 40 candidates, 308 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Aerodrome Slipstream | Dexs | 55.0 |
| Clearstar | Risk Curators | 42.4 |
| Aerodrome V1 | Dexs | 41.3 |
| XSY | Basis Trading | 13.0 |
| Pangolins | Risk Curators | 11.7 |
| Veranta | Derivatives | 11.3 |
| Extra Finance Leverage Farming | Leveraged Farming | 11.1 |
| ZEROBASE CeDeFi | Basis Trading | 10.5 |
| YO Protocol | Yield Aggregator | 8.3 |
| Aerodrome Ignition | Launchpad | 8.3 |
| Anemoy Capital | RWA | 7.2 |
| 40 Acres | Lending | 6.0 |
| Moonwell Lending | Lending | 5.8 |
| Fusion by IPOR | Onchain Capital Allocator | 5.5 |
| KPK | Risk Curators | 4.6 |
| Harvest Finance | Yield Aggregator | 4.5 |
| Brickken | RWA | 4.4 |
| SoDEX Bridge | Bridge | 4.0 |
| Block Analitica | Risk Curators | 3.8 |
| Moonwell Vaults | Onchain Capital Allocator | 3.7 |
| Anthias Labs | Risk Curators | 3.7 |
| AUTOfinance | Yield | 3.7 |
| Yearn Curating | Risk Curators | 3.3 |
| Spectra MetaVaults Outside V2 | Onchain Capital Allocator | 3.0 |
| Spectra MetaVaults | Onchain Capital Allocator | 3.0 |
| IntentX | Derivatives | 2.9 |
| MEXC | CEX | 2.7 |
| Gami Labs | Risk Curators | 2.6 |
| Morpho Midnight | Lending | 2.5 |
| Exactly | Lending | 2.3 |
| BloFin | CEX | 2.1 |
| Alchemix V3 | Synthetics | 2.1 |
| Galaxy Curation | Risk Curators | 2.0 |
| Umia | Launchpad | 1.9 |
| Superform | Yield Aggregator | 1.7 |
| Yearn Finance | Yield Aggregator | 1.6 |
| Arcadia V2 | Liquidity Manager | 1.6 |
| Re7 Labs | Risk Curators | 1.3 |
| Hydrex Integral | Dexs | 1.2 |
| alphagrowth | Risk Curators | 1.1 |

### Polygon (no USDG on this chain; 5 candidates, 370 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Polymarket International | Prediction Market | 359.6 |
| Quickswap Dex | Dexs | 5.1 |
| Aave V2 | Lending | 2.6 |
| Enzyme Finance | Indexes | 1.6 |
| StableHodl | Yield | 1.3 |

### Binance (no USDG on this chain; 9 candidates, 122 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Unitas USDu | Basis Trading | 40.3 |
| Venus Core Pool | Lending | 39.6 |
| Brickken | RWA | 20.1 |
| PancakeSwap AMM | Dexs | 8.3 |
| MEXC | CEX | 5.3 |
| PancakeSwap Infinity | Dexs | 3.0 |
| Lista DEX | Dexs | 2.4 |
| ZEROBASE CeDeFi | Basis Trading | 1.9 |
| APX Bridge | Bridge | 1.3 |

### Optimism (no USDG on this chain; 5 candidates, 237 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Nonce Capital | Risk Curators | 88.1 |
| Veda | Onchain Capital Allocator | 88.0 |
| EtherFi Borrowing Market | Lending | 55.2 |
| Velodrome V2 | Dexs | 4.3 |
| Exactly | Lending | 1.7 |

### Sui (no USDG on this chain; 13 candidates, 204 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Current | Lending | 61.0 |
| NAVI Lending | Lending | 45.6 |
| Suilend | Lending | 39.3 |
| Ember Protocol | Onchain Capital Allocator | 29.9 |
| Cetus CLMM | Dexs | 5.9 |
| DeepBook V3 | Dexs | 4.4 |
| KAIO | RWA | 4.1 |
| Mole | Yield | 3.7 |
| Bluefin Spot | Dexs | 3.3 |
| Haedal Lending Vault | Yield | 3.2 |
| Momentum | Dexs | 1.3 |
| Bucket CDP | CDP | 1.1 |
| Scallop Lend | Lending | 1.0 |

### Monad (no USDG on this chain; 10 candidates, 258 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Hyperithm | Risk Curators | 148.4 |
| Curvance | Lending | 42.2 |
| Euler V2 | Lending | 19.1 |
| K3 Capital | Risk Curators | 13.3 |
| Agua | Onchain Capital Allocator | 9.1 |
| August Digital | Risk Curators | 8.0 |
| Yuzu Money | Yield | 7.6 |
| Clearstar | Risk Curators | 5.8 |
| Neverland | Lending | 2.9 |
| Upshift | Onchain Capital Allocator | 1.9 |

### Stellar (no USDG on this chain; 12 candidates, 210 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Blend Pools V2 | Lending | 55.1 |
| Stellar DeFi Hub | Farm | 37.2 |
| Upshift | Onchain Capital Allocator | 25.0 |
| Gami Labs | Risk Curators | 25.0 |
| DeFindex | Yield Aggregator | 19.5 |
| Templar Protocol | Lending | 14.0 |
| Aquarius Stellar | Dexs | 12.7 |
| Sushi Stellar | Dexs | 7.4 |
| Stellar AMM | Dexs | 5.0 |
| Defa By InvoiceMate | RWA | 4.0 |
| Huma | RWA | 2.7 |
| Stellar DEX | Dexs | 2.4 |

### Starknet (no USDG on this chain; 5 candidates, 123 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Extended Perps | Derivatives | 112.8 |
| Vesu | Lending | 4.4 |
| Re7 Labs | Risk Curators | 3.7 |
| Troves | Yield | 1.1 |
| Defa By InvoiceMate | RWA | 1.1 |

### Pharos (no USDG on this chain; 3 candidates, 177 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| R25 | RWA | 135.1 |
| Ember Protocol | Onchain Capital Allocator | 30.7 |
| RockawayX | Risk Curators | 11.2 |

### Arc (no USDG on this chain; 2 candidates, 12 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Circle Gateway | Cross Chain Bridge | 10.5 |
| Aero Lite | Dexs | 1.3 |

### Avalanche (no USDG on this chain; 1 candidates, 3 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| KAIO | RWA | 3.0 |

### Sonic (no USDG on this chain; 2 candidates, 17 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Stability | Liquidity Manager | 9.0 |
| Euler V2 | Lending | 7.6 |

### Morph (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| BulbaSwap V3 | Dexs | 2.0 |

### xDai (no USDG on this chain; 2 candidates, 164 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| RealT Tokens | RWA | 155.1 |
| RealT RMM Marketplace V2 | Lending | 8.8 |

### dYdX (no USDG on this chain; 1 candidates, 71 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| dYdX V4 | Derivatives | 70.6 |

### Cronos (no USDG on this chain; 4 candidates, 29 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Moonlander | Derivatives | 15.9 |
| VVS Standard | Dexs | 9.6 |
| Tectonic | Lending | 2.0 |
| VVS Flawless | Dexs | 1.8 |

### Sei (no USDG on this chain; 2 candidates, 20 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| KAIO | RWA | 14.7 |
| Saphyre V3 | Dexs | 5.7 |

### Near (no USDG on this chain; 3 candidates, 26 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Rhea Lend | Lending | 12.0 |
| Rhea Dex | Dexs | 9.9 |
| KAIO | RWA | 4.0 |

### Hedera (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| SaucerSwap V2 | Dexs | 2.1 |

### Move (no USDG on this chain; 1 candidates, 31 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Avalon Superearn | Yield | 30.8 |

### RISE (no USDG on this chain; 2 candidates, 29 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| RISEx | Derivatives | 21.2 |
| Icarus CL | Dexs | 8.0 |

### World Chain (no USDG on this chain; 1 candidates, 12 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Re7 Labs | Risk Curators | 12.3 |

### Linea (no USDG on this chain; 1 candidates, 1 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Deri V4 | Options | 1.0 |

### zkSync Era (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| SyncSwap | Dexs | 2.4 |

### Chainflip (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Chainflip AMM | Dexs | 1.8 |

### Elrond (no USDG on this chain; 1 candidates, 1 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Hatom Lending | Lending | 1.1 |

### Flare (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| SparkDEX V3.1 | Dexs | 1.6 |

### HydraDX (no USDG on this chain; 2 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Hydration Lending | Lending | 1.1 |
| Hydration DEX | Dexs | 1.1 |

### Immutable zkEVM (no USDG on this chain; 2 candidates, 8 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| KAIO | RWA | 6.3 |
| Quickswap V3 | Dexs | 1.4 |

### Proton (no USDG on this chain; 1 candidates, 4 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| MetalX Lending | Lending | 3.9 |

### Pulse (no USDG on this chain; 1 candidates, 3 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| PulseX V1 | Dexs | 3.4 |

### Ronin (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Katana DEX | Dexs | 1.9 |

### Silicon zkEVM (no USDG on this chain; 1 candidates, 3 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Orbit Bridge | Bridge | 2.6 |

### Tempo (no USDG on this chain; 1 candidates, 2 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Tempo Stablecoin Dex | Dexs | 1.6 |

### Waves (no USDG on this chain; 2 candidates, 11 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Vires Finance | Lending | 9.8 |
| Waves Exchange | Farm | 1.4 |

### ZIGChain (no USDG on this chain; 2 candidates, 6 USDC)

| Protocol | Category | USDC supplied ($M) |
|---|---|---:|
| Nawa Protocol | RWA | 3.5 |
| Defa By InvoiceMate | RWA | 2.1 |

## Appendix: protocols already in the Arbitrum list, with their USDC on other chains (over $10M)

| Chain | Protocol | USDC supplied ($M) |
|---|---|---:|
| Hyperliquid L1 | Hyperliquid Bridge | 6584.0 |
| Ethereum | Binance CEX | 6205.4 |
| Ethereum | Aave V3 | 2412.9 |
| Base | Morpho Blue | 2368.2 |
| Ethereum | Morpho Blue | 1184.7 |
| Base | Steakhouse Financial | 971.5 |
| Solana | Binance CEX | 750.8 |
| Base | Gauntlet | 599.6 |
| Ethereum | Bybit | 456.4 |
| Ethereum | Compound V3 | 410.9 |
| Ethereum | Steakhouse Financial | 330.1 |
| Arc | Morpho Blue | 195.2 |
| Ethereum | Gauntlet | 192.0 |
| Base | Aave V3 | 182.2 |
| Monad | Aave V3 | 174.6 |
| Base | Binance CEX | 167.8 |
| Ethereum | Fluid Lending | 167.7 |
| Ethereum | Dolomite | 137.2 |
| Sui | Binance CEX | 112.8 |
| Ethereum | Curve DEX | 108.4 |
| Sonic | Binance CEX | 99.4 |
| Stellar | Binance CEX | 85.1 |
| Monad | Morpho Blue | 84.9 |
| Base | Aera V3 | 80.4 |
| Ethereum | Lagoon | 77.5 |
| Ethereum | LayerZero V2 | 52.1 |
| Ethereum | Bitget | 47.4 |
| Morph | Gauntlet | 43.0 |
| Morph | Morpho Blue | 43.0 |
| Ethereum | Stargate V2 | 40.0 |
| Polygon | Binance CEX | 37.6 |
| Solana | Bybit | 36.4 |
| Algorand | Binance CEX | 33.3 |
| Ethereum | Bitunix | 33.1 |
| Polygon | Aave V3 | 31.3 |
| Ethereum | Concrete | 31.1 |
| Hyperliquid L1 | Morpho Blue | 27.9 |
| Ethereum | Fluid DEX | 27.0 |
| Binance | LayerZero V2 | 26.0 |
| Binance | Stargate V2 | 25.9 |
| Binance | Bybit | 25.5 |
| Solana | BingX | 25.1 |
| Ethereum | KuCoin | 24.8 |
| Sonic | Bybit | 24.7 |
| Solana | Steakhouse Financial | 22.4 |
| Hedera | Binance CEX | 21.8 |
| Ethereum | Spark Liquidity Layer | 20.5 |
| Ethereum | Gate | 19.5 |
| Ethereum | NEAR Intents | 18.7 |
| Base | Bybit | 16.9 |
| Solana | Bitget | 15.6 |
| Base | Fluid Lending | 14.0 |
| Polygon | Bybit | 13.9 |
| Binance | Aave V3 | 13.5 |
| Monad | Bybit | 12.9 |
| Pharos | Morpho Blue | 12.8 |
| Solana | Aster Bridge | 12.6 |
| World Chain | Morpho Blue | 12.4 |
| Optimism | Aave V3 | 11.9 |
| Ethereum | Aster Bridge | 11.9 |
| Optimism | Binance CEX | 11.3 |
| Solana | KuCoin | 11.2 |
| Mantle | Bybit | 10.9 |
| Binance | Bitget | 10.9 |
| Base | Compound V3 | 10.7 |

# Launchpad primitives: research and brainstorm

Date: 2026-09-07. Starting point: the Pons (Robinhood Chain) and stock-paired (StonkFun,
Long.xyz, Pons v2 stock pairs) launchpads, and the question "what would a launchpad look
like if the innovation were in liquidity, yield and vaults rather than in the bonding curve?"

Nothing here is investment advice. Numbers are from public sources as of the date above
and are cited so they can be re-checked.

---

## 1. Where the market is (what already exists)

The launchpad stack has converged on one lifecycle: **bonding curve → graduation →
permanently locked LP → creator fee share**. Everything competitive in 2026 is a variation
on that. The table is the prior art any new primitive has to beat.

| Platform | Chain | What is distinctive | Liquidity after graduation | Yield / vault angle |
|---|---|---|---|---|
| Pump.fun | Solana | 62% of Solana launches, ~95% of graduations. Jan-2026 "dynamic fee" model where creator fees are market-driven; creator fee can be split to up to 10 wallets. | Migrates to PumpSwap CPMM; LP locked. | None. Quote SOL sits idle. |
| Bonk.fun / Bags / Believe | Solana | Fee routing: Bags routes fees to third parties (creators who did not launch), Believe 50/50 platform/creator, Bonk buys back BONK. | Raydium / Meteora locked LP. | None. |
| Raydium LaunchLab | Solana | 90% of LP burned, 10% locked as "Burn & Earn" fee key NFT for creator. | CPMM, locked. | None. |
| Meteora DBC / DAMM v2 | Solana | Fully configurable curve, fee scheduler (high fee at t=0 decaying), rate limiter, Alpha Vault (whitelisted pre-launch deposits vs snipers), M3M3 (swap fees from locked LP paid to top-999 stakers). | DAMM v2, locked; partner + creator claim fees from the lock. | M3M3 is the closest to "holder yield", funded only by swap fees. |
| StonkFun / LaunchOnSF | Solana | Tokens paired with xStocks (SPYx etc.). Buyback-and-burn of top-10 tokens by mcap from v3 pool fees every few minutes. STONK did ~$135M volume on 2026-09-06. | Raydium LaunchLab pools. | None beyond buybacks. |
| Pons v2 | Robinhood Chain | Whole supply minted to curve, no creator allocation. Graduates into a Uniswap v4 full-range position behind a custom hook, permanently locked. Pairs: ETH, USDG, tokenized NVDA/AAPL/HOOD. 1% pool fee split 70/30 creator/protocol. Creator buybacks vest over 5 years. Second-largest launchpad by fees (~$19.8M / 30d). ~25% of volume priced in tokenized stocks. | v4 full-range, locked. | None. |
| Long.xyz | Robinhood Chain | Memes paired directly with NVDA/TSLA/SPCX; pool accumulates stock as memes get bought. LongX wraps 3x-leveraged NVDA. | Locked. | None. |
| Noxa | Robinhood Chain | No curve: single-sided Uniswap v3 position at launch, never migrates. Went dark after bot spam. | v3, locked. | None. |
| Flaunch | Base | 30-min fixed-price no-sell window; hook wraps all pool ETH to flETH (lent on Aave, ~2% yield) which funds a zero-platform-fee model; "Progressive Bid Wall" buys the token with accrued fees and re-posts the bid as price rises; LPs paid in ETH only. | v4 hook-managed. | **Yes**: Aave yield on pool ETH, but it goes to the platform, not to holders or to the pool. |
| Doppler | EVM / v4 | Dutch-auction dynamic bonding curve: if sales are behind schedule the curve auctions down; multicurve initialiser seeds several curves in one pool; LP is migrated, not burned. | v2/v3/v4 or no-op. | None. |
| Clanker | Base | MEV capture inside the hook, dynamic fees, revenue tokenisation. | v4. | None. |
| Virtuals Genesis / Unicorn | Base | Tiered raise with automatic refund if tier not met or oversubscribed; agent revenue can fund buybacks. | Locked. | Revenue-backed, but only for agents with revenue. |
| Zora | Base | Content coins pair with the creator coin, creator coins pair with ZORA: **hierarchical pairing**. 50% of supply vests to creator. | v4. | None. |
| Bunni v2, EulerSwap | EVM / v4 | Not launchpads, but the two working examples of "AMM reserves that also earn lending yield" (rehypothecation to Aave/Yearn; EulerSwap uses Euler vault deposits as swap reserves). | n/a | **Yes**, for LPs. Never wired into a launchpad. |
| Kamino + xStocks | Solana | Tokenized stocks accepted as collateral; 92% utilised lending market; $31M of the $53M tokenized-stock collateral on Solana. | n/a | xStocks pass dividends through supply rebase. |
| Hyperliquid HIP-3 / perps.fun | Hyperliquid | Builder-deployed perp markets ("pump.fun for perps"); $3B+ OI by June 2026. | n/a | Funding rates are a yield source nobody routes to spot holders. |

Sources: see section 7.

### What is still broken

- **Survival.** Under 5% of launches are alive after 30 days. Most die in the first hour.
- **Idle capital.** Every graduated pool on Solana holds SOL or USDC that earns nothing. Flaunch proved the yield exists (~2% on ETH via Aave; lending stables on Solana runs 5-10%), then kept it for the platform.
- **Nobody manages the liquidity.** "Burn the LP" fixes rugs but freezes a full-range position forever. Fees accrue to a creator NFT and are claimed out, so the pool never deepens.
- **No floor.** The only bid is the AMM curve, so price can and does go to zero. Buybacks (Flaunch PBW, StonkFun top-10 burns) are discretionary and stop when fees stop.
- **Holding has no cashflow.** Fees go to creators (Pump, Bags, Pons) or to the platform, not to the people holding through the drawdown. M3M3 is the only counterexample and it only pays the top 999 stakers.
- **Stock pairs change the exit liquidity, not the risk.** Pairing with NVDAx means the pool accumulates NVDA, but the meme still goes to zero against NVDA. The pairing is a narrative, not a mechanism.
- **No short side.** Without a borrow or perp market there is no bear-funded price discovery, and no one paying longs to hold.
- **Fragmentation.** Every token has its own thin pool; a launchpad with 100k tokens has 100k puddles.

The primitives below are chosen to attack these directly.

---

## 2. Primitive catalog

Each primitive: what it is, why it is new relative to the table above, who gets paid, the
failure modes, and a rough build difficulty. They are designed to compose; section 3 picks
a coherent subset.

### P1. Productive locked liquidity ("the pool that earns while nobody trades")

**Mechanism.** At graduation the LP is locked, as today, but the quote side of the pool
(SOL / USDC / xStock) is held as a yield-bearing receipt (kSOL, a Kamino/marginfi deposit,
flETH-style, or sSPYx via Kamino's xStocks market) instead of raw quote. Swaps settle
against the receipt at its current exchange rate, so traders see a normal pool. Yield is
harvested by a keeper and routed by a per-token policy set at launch and immutable after:

| Sink | Effect |
|---|---|
| Re-add to pool ("self-deepening") | Yield buys the token and is added as liquidity; liquidity grows even at zero volume. |
| Floor vault (P2) | Raises the hard floor every epoch. |
| Holder yield (P4) | Pays conviction stakers. |
| Creator | Replaces part of the swap-fee take, so trading fees can be lower. |

**Why new.** Flaunch does the Aave leg but keeps the yield to fund a zero-fee model. Bunni
and EulerSwap do it for generic LPs. No launchpad has made "the pool earns" a token-level
property with a governable sink.

**Risks.** Lending-protocol risk moves into every pool (a Kamino exploit touches every
graduated token). Withdrawal liquidity on the lending side: if the lending pool is 95%
utilised, a large sell cannot be settled. Mitigation: keep a cash buffer (say 20-30% of
quote) un-lent, lend only the remainder, and cap per-lending-market exposure across the
whole launchpad.

**Difficulty.** Medium on EVM (a v4 hook, Bunni already open-sourced the pattern). Medium-
high on Solana (fork Meteora DAMM v2 / DBC and make the quote vault a receipt token; the
DBC repo is public).

### P2. Rising hard floor (redemption vault with burn-on-fill)

**Mechanism.** A fixed share of curve proceeds (example: 25%) never enters the AMM. It goes
into a **floor vault**. Any holder can burn tokens and receive `floor_vault / circulating_supply`
in quote at any time. The vault only grows: it receives its share of P1 yield and a slice of
swap fees (example: 30%), and it is also lent out via P1 so it compounds. Nothing withdraws
from it except redemptions, and every redemption burns supply, so floor-per-token is
monotonically non-decreasing.

Two implementations, equivalent economically:

1. **Redemption instruction.** Simple, explicit, needs a "redeem" button.
2. **Floor bid in the AMM.** Post the vault as a single-bin bid at the floor price (DLMM bin
   on Solana, single tick on v4). Tokens the bid buys are burned by a hook ("burn-on-fill")
   and the bid is re-posted at the new, higher floor. Composable: any aggregator route hits
   the floor automatically, no special UI. This is Flaunch's Progressive Bid Wall made
   permanent, funded from principal instead of fees, and paired with a burn.

**Why new.** Nouns-style ragequit and Olympus-style backing exist for DAO / reserve tokens.
No memecoin launchpad gives every launch a redeemable, ratcheting floor from day one.
StonkFun's and Flaunch's buybacks are discretionary and fee-dependent; this is
principal-backed and mechanical.

**Worked example** (quote units are SOL; supply 1B; curve sells 800M and raises 100 SOL):

| Bucket | Amount | Notes |
|---|---|---|
| AMM liquidity | 70 SOL + 200M reserved tokens | Graduation price 3.5e-7 SOL |
| Floor vault | 25 SOL | Floor = 25 / 800M = 3.1e-8 SOL, about 9% of graduation price |
| Creator + protocol | 5 SOL | |

After one year at 7% lending yield on 95 SOL (both buckets lent per P1) and, say, 30 SOL of
swap fees (30% to floor): floor vault is 25 + 1.75 + 9 ≈ 36 SOL, floor up 44% with zero
redemptions. If price falls to the floor and 200M tokens redeem, the vault pays out 9 SOL,
supply drops to 600M, floor-per-token is unchanged. A launch that "dies" now settles at
its floor instead of at zero, and the floor is the insurance every buyer paid for at the
curve.

**Risks.** 25% less AMM depth at graduation (thinner book, more slippage). Floor arbitrage
bots will redeem whenever AMM price < floor, which is intended. The floor share must be
fixed at launch and displayed on the curve so buyers price it in.

**Difficulty.** Low-medium as a redemption instruction. Medium as a burn-on-fill bid.

### P3. Vault-native token: buys above NAV mint, sells below NAV redeem

The purist version of P1 + P2: the token *is* an ERC-4626 / SPL vault share. NAV per token
is the floor. The bonding curve sells shares at a premium to NAV; the premium is what funds
the AMM and the creator. Sells below NAV are redemptions; sells above NAV are AMM swaps.
Every meme becomes "a vault with a story on top", which is also a legible pitch for
stock-paired launches: "a share of a rising NVDAx reserve, with a meme premium".

**Why new.** Ties P1/P2 into one object that lending protocols, aggregators and wallets
already understand (a vault share with a NAV). Prior art in NFT floor-liquidity
protocols and reserve-currency DAOs; never applied to launchpad tokens.

**Risks.** Regulatory: a token with a redeemable NAV looks more like a fund unit than a
meme. Keep the reserve in the same asset the token was sold in and avoid any
management-fee language. Worth legal review before shipping.

### P4. Conviction yield with forfeiture (the "tontine" distribution)

**Mechanism.** Fees and P1 yield allocated to holders are not paid pro-rata to balance.
They accrue to a **conviction score** = balance × time held (like M3M3 but for everyone,
and time-weighted rather than top-999). Selling, or transferring out, forfeits the seller's
unclaimed accrual, which is redistributed to the remaining stakers. Claiming does not reset
the timer; selling does.

**Why new.** M3M3 pays swap fees to the largest stakers, which favours whales. Here the
weight grows with time, and quitters subsidise stayers, so holding through a drawdown is
paid for by the people who caused it. The forfeiture mechanic is closer to a tontine than
to a staking pool and has not been used for launchpad fee distribution.

**Risks.** Wash-holding through multiple wallets is fine (time is what counts, not wallet
count). Large, old holders get a big share; that is the point, but publish the curve so it
is not a surprise. Must be paired with P2 so "hold for yield" does not mean "hold to zero".

**Difficulty.** Low-medium. A staking program with a timestamped position and a forfeiture
pool.

### P5. Bear-funded yield: a native borrow market at graduation

**Mechanism.** Graduation creates, in the same transaction, an isolated lending market for
the token: holders deposit tokens as lendable supply, shorts borrow them (posting quote
collateral) and pay a utilisation-based interest rate to the depositors. Because the
token has a redeemable floor (P2), the lender's downside is bounded: borrowed tokens can
always be redeemed for at least the floor, so collateral requirements can be set from the
floor, not from a manipulable spot price.

**Why new.** No launchpad ships a short side. Hyperliquid HIP-3 markets exist only for
tokens big enough to justify a 500k HYPE bond. This gives every graduated token a short
market on day one, and it turns bears into the yield source for longs.

**Risks.** Oracle: use the pool TWAP with the floor as a hard lower bound. Squeeze risk on
thin tokens, which is a feature for the memes and a bug for the shorts. Liquidations need
a keeper and enough AMM depth; cap borrowable supply to a fraction of AMM depth.

**Difficulty.** High. Isolated-market lending is a solved design (Kamino isolated markets,
Morpho Blue on EVM), but wiring it into graduation and to the floor oracle is real work.
Morpho Blue-style immutable markets are the model on EVM.

### P6. Floor-collateral credit line ("borrow against your bag without selling")

**Mechanism.** Because P2 guarantees `floor_per_token` in quote, a lender can advance up to
`floor × balance` against locked tokens with no liquidation risk: if the loan is not
repaid, the lender redeems the collateral at the floor. Holders get liquidity without
selling, so hype-cycle sell pressure drops. The floor vault itself can be the lender
(it lends its own quote to holders at a rate, another P1 yield source), or a third-party
vault can be.

**Why new.** Lending against memecoins exists (Kamino/marginfi list a few large ones) but
needs a price oracle and liquidation engine. Lending at the floor needs neither.

**Risks.** Low individually; the LTV is by construction 100% of a guaranteed value. Systemic
risk if the floor vault lends out too much of itself and cannot meet redemptions; cap
floor-vault lending at a fraction (say 50%) and keep the remainder as a cash buffer.

**Difficulty.** Low-medium once P2 exists.

### P7. Stock-paired with the yield actually attached ("fee-to-equity DCA")

The stock-pair launchpads changed the pool asset but left the mechanism alone. Three ways
to make the stock pairing do work:

- **Yield-bearing stock quote.** Pair against the Kamino-deposited version of the xStock
  (sSPYx-style receipt) so the pool's stock side earns lending yield, per P1. Kamino's
  xStocks market runs ~92% utilised, so the yield is real and the demand is there.
- **Fees paid out in stock and auto-accumulated.** Swap fees on a NVDAx-paired meme are
  received in NVDAx. Route the holder share (P4) into a per-holder equity vault: holding the
  meme is a dollar-cost-averaged accumulation of NVDAx, funded by the traders. "Hold the
  meme, get paid in Nvidia" is a stronger story than "the pool holds Nvidia".
- **Delta-choice at launch.** The creator picks the exposure of the floor vault: raw stock
  (long the equity), hedged stock (stock + short perp on HIP-3, so the floor is
  dollar-stable but earns the basis), or stable. The meme's floor then either tracks the
  equity or is dollar-flat; buyers choose which kind of "meme stock" they want.

**Why new.** Pons v2, StonkFun and Long.xyz all pair and stop. None of them make the stock
side productive or distribute it.

**Risks.** xStocks are exposure, not shares; say so everywhere. Backed/xStocks issuer risk
concentrates across every stock-paired token. Rebasing dividends have to be handled by
the pool accounting (DLMM/CPMM do not expect rebasing quotes; use the receipt token,
which does not rebase, as the actual pool asset).

### P8. Curve-phase yield and graduation insurance

**Mechanism.** Deposits sitting on the bonding curve before graduation are lent out too
(same P1 rails). The yield during the curve phase funds an **insurance pool**: if a token
fails to graduate within N days, or graduates and then falls below X% of graduation
price within 30 days, curve buyers can claim a refund of part of their principal from the
insurance pool. Losing launches subsidise the insurance for the next cohort.

**Why new.** Virtuals refunds only when a tier is missed before launch. Post-graduation
failure, the mode in which >95% of buyers lose, is uninsured everywhere.

**Risks.** Adverse selection: creators launch junk to farm the insurance. Mitigate by
paying insurance only to non-creator wallets, capping it, and funding it from yield and
a small fee rather than promising a fixed payout.

**Difficulty.** Medium; mostly accounting and a claims keeper.

### P9. Managed liquidity via rent auctions (am-AMM for locked LP)

**Mechanism.** The locked LP does not have to be full-range. Auction the right to manage
the position's range (a "manager" who can concentrate it around price, JIT it, or run the
floor bid) to the highest bidder for the next epoch. The rent goes to the floor vault or to
holders. The manager cannot withdraw, only reshape, so the rug guarantee holds.

**Why new.** Bunni's am-AMM auctions the swap-fee stream to a manager; here the auction is
for range management of a permanently locked launch position. Market makers get to
manage memecoin liquidity without the founder trusting them with the LP tokens.

**Risks.** A manager can set a useless range; bound the allowed range (e.g. must cover
±50% of TWAP). Small tokens will get no bidders and default to full-range.

**Difficulty.** Medium-high. Interesting mainly for tokens that reach real volume.

### P10. Hierarchical pairing into a launchpad index (fixes fragmentation)

**Mechanism.** Zora pairs content coins with the creator coin and creator coins with ZORA.
Generalise: every graduate pairs with the **launchpad's index token** (say, `LP-INDEX`),
and the index token is itself a vault (P3) whose reserve is a slice of every graduate
(e.g. 2% of each token's supply at graduation plus a share of each floor vault). Buying
any meme buys the index, buying the index deepens every meme. Sector indices (NVDA-memes,
AI-agent memes) sit between the tokens and the top index.

**Why new.** Zora's hierarchy exists but the parent is one creator's coin, not a
diversified reserve. No Solana launchpad pairs anything against anything but SOL/USDC
(and now xStocks). This makes the launchpad token itself the settlement asset, which is
what BONK tried to do socially but not structurally.

**Risks.** Index token becomes reflexive: a wave of dead memes weighs on the index and
therefore on every live pair. Weight the index by floor vaults (P2), which do not go to
zero, rather than by spot. Also, routing SOL → index → meme adds a hop; aggregators
handle this but the UI must quote the all-in price.

**Difficulty.** Medium. It is mostly a pairing policy plus an index vault.

### P11. Creator earn-out instead of creator fee

**Mechanism.** Creator fees are escrowed and streamed only while the token clears
milestones (TWAP above graduation price, floor vault growth, holder count). Missed
milestones divert the stream to the floor vault. Pons already vests creator buybacks over
5 years; this vests the fee itself and makes it conditional.

**Why new.** Every current model pays the creator on volume, which rewards launch-and-dump.
Paying on durability is a different incentive.

**Risks.** Creators go elsewhere for instant fees. Position it as opt-in with a badge
("earn-out launch") that buyers can filter for; Pons' success shows a chunk of the market
pays for creator alignment.

### P12. Table stakes (not new, but required)

Anti-snipe fee scheduler (Meteora), no-sell fixed-price window (Flaunch), whitelisted
pre-launch deposits (Alpha Vault), whole supply on the curve with no creator allocation
(Pons), immutable fee routing to up to N wallets (Pump, Bags), dutch-auction curve that
lowers price when sales stall (Doppler). A new launchpad should ship all of these on day
one; none of them is a differentiator any more.

---

## 3. A coherent product: "floor-and-yield launchpad"

Not every primitive above belongs in v1. The subset that composes cleanly, is buildable on
Solana with existing rails (Meteora DBC/DAMM v2 fork, Kamino/marginfi for lending,
xStocks for stock pairs), and gives a one-sentence pitch:

> Every token launched here has a hard floor that only goes up, its liquidity earns yield
> while it sits, and the yield goes to the people who hold.

**Lifecycle**

1. **Curve.** Whole supply on a DBC-style curve, fee scheduler for the first minutes,
   creator allocation zero. Curve deposits are lent (P8) and the yield seeds the insurance
   pool. Quote asset chosen at launch: SOL, USDC, or a Kamino-receipt xStock (P7).
2. **Graduation** (single transaction): 70% of proceeds + reserved supply → locked DAMM
   v2 pool whose quote side is a lending receipt (P1); 25% → floor vault posted as a
   burn-on-fill floor bid (P2); 5% → protocol + creator escrow (P11).
3. **Live.** Keeper harvests lending yield each epoch and splits it by the immutable
   policy: 40% re-added as liquidity, 40% floor vault, 20% holder yield. Swap fees (1%):
   30% floor, 40% conviction stakers with forfeiture (P4), 30% creator earn-out.
4. **Optional at scale.** When a token crosses a depth threshold, open the isolated
   borrow market (P5) and the floor-collateral credit line (P6), and let range
   management go to auction (P9).
5. **Index.** From the first graduate onward, 2% of supply and 10% of each floor vault's
   inflows go into the launchpad index vault (P10); later launches may pair against the
   index instead of SOL.

**What this changes for each participant**

| Participant | Today | Here |
|---|---|---|
| Curve buyer | Loses ~100% in the modal case | Loses at most (1 − floor share), gets insurance claim on early death |
| Holder | No cashflow, subsidises creator | Yield from lending + fees + quitters' forfeits; can borrow at floor |
| Creator | Paid on volume, incentive to dump | Paid on durability, escrowed |
| Platform | Takes fees | Takes a slice of yield and fees; owns the index token |
| Short seller | No venue | Borrow market, pays holders |

**Numbers to validate before building** (these decide whether the pitch is real):

- Lending yield actually achievable on the quote side at launchpad scale (SOL lending on
  Kamino/marginfi ~3-6%, USDC ~5-9%, xStocks market higher but capacity-limited).
- Floor share sensitivity: at 25% the floor is ~9% of graduation price in the example
  above; at 40% it is ~20% but AMM depth drops accordingly. Simulate slippage vs floor.
- Yield sink split: how much re-added liquidity is needed for depth to grow faster than
  volume decays on the median token (the CYBERLEEK / CLUSSY / HOOKR history in this repo
  is a usable volume-decay dataset).
- Forfeiture curve for P4: what fraction of sellers leave in the first day, hence how
  much the tontine actually pays stayers.

---

## 4. Ideas considered and parked

- **Perp-funded holder yield** (route HIP-3 funding to spot holders): needs a perp venue
  and a 500k HYPE bond per market; only viable for the top few tokens.
- **Protocol-owned liquidity grants** (platform matches liquidity for tokens that pass
  metrics): Robinhood-Chain-style incentive spend, not a primitive.
- **AI-curated launches** (MemeToro-style): distribution, not mechanism.
- **Fee-denominated buyback of the top-N tokens** (StonkFun): already exists, and it
  rewards size rather than holders.

---

## 5. Suggested next steps

1. Pick the v1 subset (recommendation: P1 + P2 + P4 + P12, with P7 as the stock-pair
   option) and write the parameter sheet: floor share, yield split, fee split, cash
   buffer, lending caps.
2. Build a small agent-based simulation of the lifecycle using the volume-decay curves
   from this repo's memecoin dataset, to size the floor and yield sinks.
3. Prototype on a Meteora DBC fork with a Kamino receipt as quote; the DBC program and
   SDKs are public.
4. Legal read on P2/P3 (redeemable floor) before it goes near a UI.

---

## 6. One-line summaries (for the pitch deck)

- **Productive locked liquidity**: the pool earns lending yield while nobody trades.
- **Rising floor**: every launch has a redeemable floor that only goes up.
- **Vault-native token**: the meme is a vault share with a premium on top.
- **Conviction yield**: quitters pay stayers.
- **Bear-funded yield**: shorts borrow from holders and pay them for it.
- **Floor credit line**: borrow against your bag without selling, no liquidations.
- **Stock pairs that work**: fees in NVDAx, accumulated for holders, on a yield-bearing quote.
- **Graduation insurance**: dead launches pay back part of the principal.
- **Rent-the-range**: market makers manage locked liquidity without touching it.
- **Launchpad index**: every meme pairs with a reserve of every meme.
- **Creator earn-out**: creators get paid for tokens that last.

---

## 7. Sources

- Pons v2 mechanics: https://www.coingabbar.com/en/crypto-blogs-details/pons-launchpad-v2-how-new-tokens-are-priced-and-launched ; on-chain events and stock pairs: https://docs.bitquery.io/docs/blockchain/robinhood/pons-api/ ; fee share and 70/30 split: https://thedefiant.io/news/defi/pump-fun-launchpad-fee-share-falls-robinhood-chain-pons-noxa ; Uniswap Labs buying PONS: https://thedefiant.io/news/defi/uniswap-labs-bought-pons-token-for-long-term-alignment
- StonkFun: https://www.theblock.co/news/defi/2026-09-06-stonk-surges-250-to-140-million-market-cap-as-stock-paired-solana-launchpad-stonkfun-pulls-volume-to-raydium-and-jupiter-413621
- Long.xyz: https://airdropalert.com/blogs/what-is-long-xyz/
- Noxa: https://docs.noxa.fi/launchpad/overview/ ; https://crypto.news/cashcat-noxa-launchpad-outage-226-million-question/
- Flaunch (flETH via Aave, Progressive Bid Wall, fixed-price window): https://www.uniswapfoundation.org/blog/builder-stories-how-flaunch-is-revolutionizing-liquidity-with-hooks ; https://followin.io/en/feed/16394864 ; https://www.blocmates.com/articles/flaunch-redefining-launchpads-with-fixed-price-fair-launch
- Doppler: https://github.com/whetstoneresearch/doppler/blob/main/docs/Doppler.md ; https://docs.doppler.lol/how-it-works/implementation
- Clanker: https://clanker.gitbook.io/clanker-documentation/references/core-contracts/v4 ; hooks overview: https://www.quillaudits.com/research/uniswap-development/uniswap-v4/hooks-ecosystem
- Bunni v2 rehypothecation, am-AMM: https://research.auditless.com/p/bunni-how-to-build-a-leading-uniswap ; https://blog.bunni.xyz/posts/dawn-of-lp-profitability/
- Meteora DBC / fee scheduler / locked LP fees: https://github.com/MeteoraAg/dynamic-bonding-curve ; https://docs.meteora.ag/developer-guide/guides/dbc/bonding-curve-configs ; Alpha Vault: https://docs.meteora.ag/anti-sniper-suite/alpha-vault/what-is-alpha-vault ; M3M3: https://meteoraag.medium.com/introducing-m3m3-a-new-era-for-memecoin-hodling-a88a470d2adf
- Raydium LaunchLab fees and Burn & Earn: https://docs.raydium.io/raydium/launchlab/how-creator-fees-work ; https://docs.raydium.io/raydium/pool-creation/launchlab/creator-fee-share
- Pump.fun 2026 fee model and market share: https://coinmarketcap.com/academy/article/pumpfun-overhauls-creator-fees-amid-launch-spike ; https://bravenewcoin.com/insights/pump-fun-introduces-creator-fee-sharing-system-to-rebalance-platform-incentives ; https://coinbureau.com/analysis/best-memecoin-launchpads
- Bags fee routing: https://dev.to/sivarampg/bagsfm-the-solana-launchpad-thats-changing-creator-monetization-4g7n ; Believe: https://defillama.com/protocol/launch-coin-on-believe
- Virtuals Genesis refunds and Unicorn: https://whitepaper.virtuals.io/about-virtuals/tokenization-platform/genesis-launch/genesis-refund-policy ; https://whitepaper.virtuals.io/info-hub/builders-hub/agent-launch-guide/how-to-unicorn-launch
- Zora hierarchical pairing: https://docs.zora.co/coins
- xStocks + Kamino: https://thedefiant.io/news/defi/kamino-becomes-first-major-defi-lender-to-accept-tokenized-stocks-as-collateral ; https://www.kucoin.com/news/flash/kamino-lend-controls-82-6-of-tokenized-stock-lending-on-solana ; dividends via rebase: https://support.kraken.com/articles/xstocks-faq
- HIP-3 / perps.fun: https://www.datawallet.com/crypto/hip-3-explained-hyperliquid-upgrade ; https://perps.fun/
- Survival and problems: https://www.motiontrade.com/blog/how-meme-coins-launch-in-2026-the-launchpad-wars-and-a-changing-meme-market-explained ; https://cryptoslate.com/launchpads/meme-coin-platforms/

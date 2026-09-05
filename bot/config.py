"""All settings come from environment variables; nothing secret is stored in the repo."""
import os, json

def _env(name, default=None, cast=str):
    v = os.environ.get(name)
    if v is None or v == "": return default
    try: return cast(v)
    except Exception: return default

DATA_DIR = _env("BOT_DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
DB_PATH = os.path.join(DATA_DIR, "bot.sqlite")

# --- integrations (all optional except Telegram for the chat interface)
TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_CHATS = {int(x) for x in _env("TELEGRAM_ALLOWED_CHATS", "").split(",") if x.strip().lstrip("-").isdigit()}
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = _env("ANTHROPIC_MODEL", "claude-sonnet-5")
CG_API_KEY = _env("COINGECKO_API_KEY")            # optional demo key raises CoinGecko rate limits

# --- execution: OFF unless both are set. Never commit a key.
LIVE_TRADING = _env("LIVE_TRADING", "0") == "1"
WALLET_PRIVATE_KEY = _env("WALLET_PRIVATE_KEY")
WALLET_ADDRESS = _env("WALLET_ADDRESS", "0x000000000000000000000000000000000000dEaD")   # quotes work with any address
RPC_URLS = {
    1: _env("RPC_ETHEREUM", "https://eth.llamarpc.com"),
    42161: _env("RPC_ARBITRUM", "https://arb1.arbitrum.io/rpc"),
    8453: _env("RPC_BASE", "https://mainnet.base.org"),
    4663: _env("RPC_ROBINHOOD", "https://rpc.mainnet.chain.robinhood.com"),
    999: _env("RPC_HYPEREVM", "https://rpc.hyperliquid.xyz/evm"),
    10: _env("RPC_OPTIMISM", "https://mainnet.optimism.io"),
    56: _env("RPC_BSC", "https://bsc-dataseed.binance.org"),
    137: _env("RPC_POLYGON", "https://polygon-rpc.com"),
    43114: _env("RPC_AVALANCHE", "https://api.avax.network/ext/bc/C/rpc"),
    146: _env("RPC_SONIC", "https://rpc.soniclabs.com"),
}
DEFAULT_FROM_CHAIN = _env("DEFAULT_FROM_CHAIN", 42161, int)     # where your stablecoins sit
DEFAULT_FROM_TOKEN = _env("DEFAULT_FROM_TOKEN", "USDC")

# --- signal rules (from the backtest work)
MIN_REV30 = 100_000          # 30-day revenue floor to be in the universe
MIN_HIST = 28                # days of revenue history before a name can trigger
MATURE_HIST = 90             # established names need this much revenue history
YOUNG_TOKEN_AGE = 90         # token listed within this many days = early sleeve
BREAKOUT_K = 2.0             # 7d revenue >= K x mean of prior 8 weekly windows
LOOKBACK_WEEKS = 8
PS_REL_MAX = 1.0             # established names: P/S at or below its own 180d median at entry (0.7 = tight)
YOUNG_RISING_DAYS = 2        # early sleeve: consecutive rising revenue days
YOUNG_WOW = 1.25             # early sleeve: 7d revenue >= 1.25 x 2-week average
EXIT_SLOW_WEEKS = 4          # exit when 7d revenue < 4-week average
EXIT_MOM = -0.30             # or 30d revenue down 30% month on month
TRAIL_STOP = 0.25            # trailing stop for the established sleeve
TRAIL_STOP_YOUNG = 0.50      # early sleeve needs room (PONS dipped 41% before its run)

# --- catalyst-time filters (from the Jun-Sep 2026 catalyst review)
ONE_DAY_SHARE_MAX = 0.50     # reject if >= 50% of the week's revenue landed on one day
RECURRING_WINDOW = (25, 35)  # a similar spike 25-35 days earlier = distribution schedule, not growth
RECURRING_MULT = 3.0
FRESH_ZERO_SHARE = 0.25      # > 25% zero-revenue days in the prior 8 weeks = data source just started
FRESH_PRODUCT_DAYS = 14      # a sub-product younger than this carrying >= 50% of the week = adapter change
BREADTH_BETA = 0.35          # >= 35% of the universe spiking the same week = market event, not a stock story

# --- tradability
MIN_VOL30 = 500_000          # 30d average daily volume (CoinGecko)
MIN_MCAP = 10_000_000
MIN_POOL_LIQ = 500_000       # best pool liquidity (DexScreener)
MAX_TRADE_SHARE_OF_LIQ = 0.05
MAX_PRICE_IMPACT = 0.02
MAX_TRADE_USD = _env("MAX_TRADE_USD", 2_000, float)
MAX_BUY_TAX = 0.10
MAX_SELL_TAX = 0.10

DAILY_HOUR_UTC = _env("DAILY_HOUR_UTC", 6, int)

# DeFiLlama chain name -> chain id used by GoPlus / LI.FI / RPC
CHAIN_IDS = {"Ethereum": 1, "Arbitrum": 42161, "Base": 8453, "Robinhood Chain": 4663, "HyperEVM": 999, "Hyperliquid L1": 999,
             "Optimism": 10, "OP Mainnet": 10, "BSC": 56, "Binance": 56, "Polygon": 137, "Avalanche": 43114, "Sonic": 146, "Solana": "solana"}
# CoinGecko platform id -> DeFiLlama chain name
CG_PLATFORMS = {"ethereum": "Ethereum", "arbitrum-one": "Arbitrum", "base": "Base", "robinhood": "Robinhood Chain", "hyperevm": "HyperEVM",
                "optimistic-ethereum": "Optimism", "binance-smart-chain": "BSC", "polygon-pos": "Polygon", "avalanche": "Avalanche", "sonic": "Sonic", "solana": "Solana"}
# categories that receive a chain's activity directly (first-order beneficiaries of a chain wave)
FIRST_ORDER_CATEGORIES = {"Launchpad", "Dexs", "Dexes", "DEX Aggregator", "Chain", "Rollup", "Derivatives", "Perps", "Liquidity manager"}
# tokens that book a share of another chain's revenue (not visible from DeFiLlama's chain field)
KNOWN_BENEFICIARIES = {"Robinhood Chain": [{"sym": "ARB", "why": "Arbitrum Foundation books 10% of Robinhood Chain net revenue plus Timeboost; its DeFiLlama series is effectively a Robinhood Chain proxy"}]}
# stablecoin addresses for the buy leg
STABLES = {42161: {"USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"},
           1: {"USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7"},
           8453: {"USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"},
           10: {"USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"},
           56: {"USDT": "0x55d398326f99059fF775485246999027B3197955", "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"},
           137: {"USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"},
           43114: {"USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"}}
NATIVE = "0x0000000000000000000000000000000000000000"

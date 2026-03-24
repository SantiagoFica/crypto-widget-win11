# Colors
COLOR_BG              = "#1A1A2E"
COLOR_BG_ALPHA        = 235          # 0-255 transparency for main window
COLOR_BG_ROW          = "#1A1A2E"
COLOR_BG_ROW_ALT      = "#16213E"
COLOR_ACCENT          = "#E94560"
COLOR_TEXT_PRIMARY    = "#EAEAEA"
COLOR_TEXT_SECONDARY  = "#8892A4"
COLOR_POSITIVE        = "#00C896"
COLOR_NEGATIVE        = "#E94560"
COLOR_SPARKLINE_UP    = "#00C896"
COLOR_SPARKLINE_DOWN  = "#E94560"
COLOR_BORDER          = "#2A2A4A"
COLOR_TITLE           = "#4FC3F7"
COLOR_WATCH           = "#FFB74D"

# Dimensions
WINDOW_WIDTH_DEFAULT  = 360
ROW_HEIGHT            = 78
TITLE_BAR_HEIGHT      = 38
SPARKLINE_WIDTH       = 90
SPARKLINE_HEIGHT      = 42
CORNER_RADIUS         = 12
PERIOD_BTN_WIDTH      = 44
PERIOD_BTN_HEIGHT     = 22

# API
COINGECKO_BASE        = "https://api.coingecko.com/api/v3"

PERIOD_DAYS = {
    "1D":  1,
    "7D":  7,
    "30D": 30,
    "90D": 90,
    "1Y":  365,
}

# Known coins: display symbol -> coingecko id
KNOWN_COINS = {
    "BTC":   "bitcoin",
    "ETH":   "ethereum",
    "SOL":   "solana",
    "BNB":   "binancecoin",
    "XRP":   "ripple",
    "ADA":   "cardano",
    "DOGE":  "dogecoin",
    "DOT":   "polkadot",
    "AVAX":  "avalanche-2",
    "MATIC": "matic-network",
    "LINK":  "chainlink",
    "UNI":   "uniswap",
    "LTC":   "litecoin",
    "BCH":   "bitcoin-cash",
    "ATOM":  "cosmos",
    "NEAR":  "near",
    "APT":   "aptos",
    "ARB":   "arbitrum",
    "OP":    "optimism",
    "INJ":   "injective-protocol",
}

# Reverse map: coingecko id -> symbol
COIN_ID_TO_SYMBOL = {v: k for k, v in KNOWN_COINS.items()}

# Tip analysis thresholds
TIP_STRONG_BULL_PCT  =  10.0
TIP_BULL_PCT         =   3.0
TIP_BEAR_PCT         =  -3.0
TIP_STRONG_BEAR_PCT  = -10.0
TIP_HIGH_VOLATILITY  =   5.0

DEFAULT_REFRESH_SECONDS = 60
MIN_REFRESH_SECONDS     = 30

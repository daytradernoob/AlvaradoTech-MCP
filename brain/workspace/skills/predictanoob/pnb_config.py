"""
PredictaNoob — Central Config
All tunable parameters in one place. Adjust here, never dig into strategy files.
"""

# ─── Trading ──────────────────────────────────────────────────────────────────
MAX_CONTRACTS      = 1       # Max contracts per trade
HALT_BELOW_CENTS   = 2000   # Stop trading if balance < $20.00

# ─── Crypto (KXBTC15M) ────────────────────────────────────────────────────────
CRYPTO_SERIES      = "KXBTC15M"
LOOP_INTERVAL_S    = 30       # Seconds between market polls (inside 15-min window)
WINDOW_MINUTES     = 15       # Contract duration in minutes

# Becker Optimism Bias thresholds
BECKER_YES_CEILING = 0.55     # YES ask above this → retail optimism → buy NO
BECKER_YES_FLOOR   = 0.0      # YES ask below this → buy YES (disabled until validated)

# Momentum signal (yfinance 1-min BTC bars)
MOMENTUM_LOOKBACK_BARS = 5    # Number of 1-min bars for momentum calc
MOMENTUM_BEARISH_THRESH = -0.0005   # % change per bar ≤ this → bearish confirmation for NO
MOMENTUM_BULLISH_THRESH =  0.0005   # % change per bar ≥ this → bullish confirmation for YES

# Orderbook skew: NO_depth / YES_depth ratio > this = market leaning YES (confirms NO trade)
SKEW_NO_CONFIRM    = 1.15    # NO side deeper than YES by 15% = crowd buying YES

# EV & fees
KALSHI_FEE_RATE    = 0.07    # 7% of (C × P × (1-P))
MIN_EV             = 0.04    # Minimum fee-adjusted EV to enter
MIN_MINUTES_TO_CLOSE = 8     # Skip entry if contract expires in < 8 min
MIN_VOLUME         = 100     # Minimum contract volume (liquidity filter)
MIN_PRICE          = 0.05    # Skip if YES or NO ask < 5¢ (untraded ghost market)
GHOST_SPREAD       = 0.98    # yes_ask + no_ask ≥ this → already settled, skip

# ─── Weather ──────────────────────────────────────────────────────────────────
MIN_MARGIN_F       = 5       # NOAA forecast must be ≥ 5°F from threshold
MAX_YES_ASK        = 0.30    # Only buy NO when YES ≤ 30¢
MIN_HIST_RATE      = 0.70    # Historical NO win rate ≥ 70% required
MIN_EV_WEATHER     = 0.05    # Weather EV floor
SKIP_SERIES        = {"KXHIGHTDC", "KXHIGHTHOU"}  # Sustained underperformers

"""
PredictaNoob — Central Config
All tunable parameters in one place. Adjust here, never dig into strategy files.
"""

# ─── Trading ──────────────────────────────────────────────────────────────────
HALT_BELOW_CENTS   = 2000    # Stop trading if balance < $20.00

# Kelly sizing (both engines)
KELLY_FRACTION     = 0.10    # Tenth-Kelly — conservative on small account
KELLY_MAX_CONTRACTS = 3      # Hard cap regardless of Kelly output
KELLY_MIN_CONTRACTS = 1      # Always trade at least 1 if signal fires

# ─── Crypto (KXBTC15M) ────────────────────────────────────────────────────────
CRYPTO_SERIES      = "KXBTC15M"
LOOP_INTERVAL_S    = 30       # Seconds between market polls
WINDOW_MINUTES     = 15       # Contract duration in minutes

# Becker Optimism Bias thresholds
BECKER_YES_CEILING = 0.55     # YES ask above this → retail optimism → buy NO
BECKER_YES_FLOOR   = 0.0      # YES ask below this → buy YES (disabled until validated)

# Momentum signal (yfinance 1-min BTC bars)
MOMENTUM_LOOKBACK_BARS  = 5
MOMENTUM_BEARISH_THRESH = -0.0005   # slope ≤ this → bearish (confirms NO)
MOMENTUM_BULLISH_THRESH =  0.0005   # slope ≥ this → bullish (confirms YES)

# Orderbook skew: NO_depth / YES_depth > this = crowd is on YES (confirms NO trade)
SKEW_NO_CONFIRM    = 1.15

# EV & fees
KALSHI_FEE_RATE    = 0.07    # 7% of (C × P × (1-P))
MIN_EV             = 0.04    # Minimum fee-adjusted EV (crypto)
MIN_MINUTES_TO_CLOSE = 8     # Skip if < 8 min left (near-expiry, already decided)
MAX_MINUTES_TO_CLOSE = 50   # Skip if > 50 min left (too early, pricing inefficient)
MIN_VOLUME         = 100
MIN_PRICE          = 0.04    # Skip if YES or NO ask < 4¢ (settled/untraded side)

# ─── Weather ──────────────────────────────────────────────────────────────────
MIN_MARGIN_F       = 5       # NOAA must be ≥ 5°F from threshold (hard cutoff)
UNCERTAINTY_MARGIN_FULL = 10 # ≥ 10°F margin → full confidence, no EV penalty
UNCERTAINTY_EV_BUFFER   = 0.04  # Extra EV required in 5–10°F uncertainty zone

MIN_HIST_RATE      = 0.70    # Historical win rate ≥ 70% required
MIN_EV_WEATHER     = 0.05    # Base EV floor (uncertainty buffer stacks on top)
SKIP_SERIES        = {"KXHIGHTDC", "KXHIGHTHOU"}  # Sustained underperformers

---
name: predictanoob
description: "PredictaNoob — Kalshi prediction market trading engine. Triggers: predictanoob, pnb status, pnb report, trading update, kalshi status, how are we doing, check trades, pnb balance, go live, halt trading, pnb logs."
---

# PredictaNoob — AlvaradoTech Platform Skill

Autonomous prediction market trading on Kalshi. Two signal engines run continuously on the SEi miniPC.

## Architecture

```
pnb_config.py     — All tunable parameters (single source of truth)
pnb_auth.py       — Kalshi RSA-PSS authentication (api.elections.kalshi.com)
pnb_state.py      — Position tracking / dedup (prevents loop-buy bug)
pnb_learn.py      — Learning engine (near-miss log, price distribution, recommendations)
pnb_telegram.py   — Telegram notifications via OpenClaw bot

pnb_crypto.py     — Crypto engine: KXBTC15M 15-min BTC contracts
                    Signals: Becker Bias + BTC Momentum (yfinance) + Orderbook Skew
                    Runs: systemd user service (continuous, 30s poll)

pnb_weather.py    — Weather engine: city daily high temperature contracts
                    Signals: NOAA forecast margin + 50-year backtest hit rate
                    Runs: cron 9AM, 12PM, 3PM MST

pnb_status.py     — Daily report (balance, positions, W/L, learning intel)
                    Runs: cron 8AM MST → Telegram
```

## Execution Steps

**Step 1 — Status report**

Run: `python3 /home/rob-alvarado/AlvaradoTech-MCP/brain/workspace/skills/predictanoob/pnb_status.py`

**Step 2 — Service health**

```bash
systemctl --user status pnb-crypto   # Check crypto engine
tail -30 /home/rob-alvarado/RJA/.pnb/pnb_crypto.log
tail -30 /home/rob-alvarado/RJA/.pnb/pnb_weather.log
```

**Step 3 — If user asks to go LIVE**

Confirm: "This will enable real-money trading on Kalshi. Balance: $[X]. Confirm go LIVE?"
Then: `sed -i 's/LIVE_TRADING=false/LIVE_TRADING=true/' /home/rob-alvarado/RJA/.pnb/.env`
Then restart crypto engine: `systemctl --user restart pnb-crypto`

**Step 4 — If user asks to HALT**

`sed -i 's/LIVE_TRADING=true/LIVE_TRADING=false/' /home/rob-alvarado/RJA/.pnb/.env`
`systemctl --user stop pnb-crypto`

**Step 5 — If user asks to tune thresholds**

All config in: `/home/rob-alvarado/AlvaradoTech-MCP/brain/workspace/skills/predictanoob/pnb_config.py`
Key knobs: BECKER_YES_CEILING, MIN_HIST_RATE, MIN_EV, MOMENTUM_BEARISH_THRESH

## Key Files on SEi (192.168.0.165)

| File | Purpose |
|------|---------|
| `/home/rob-alvarado/RJA/.pnb/.env` | LIVE_TRADING, MIN_BALANCE_CENTS |
| `/home/rob-alvarado/RJA/.pnb/kalshi_private.pem` | RSA private key (chmod 600) |
| `/home/rob-alvarado/RJA/.pnb/pnb_state.json` | Open positions |
| `/home/rob-alvarado/RJA/.pnb/pnb_learn.json` | Learning data |
| `/home/rob-alvarado/RJA/.pnb/weather_backtest.json` | 50-yr temperature backtest |
| `/home/rob-alvarado/RJA/.pnb/pnb_crypto.log` | Crypto engine log |
| `/home/rob-alvarado/RJA/.pnb/pnb_weather.log` | Weather engine log |

## Signal Logic Summary

**Crypto (KXBTC15M):**
1. YES ask > 0.55 → Becker Optimism Bias → signal NO
2. BTC 5-bar 1-min momentum must not contradict (no bullish momentum on NO trade)
3. Kalshi orderbook NO/YES depth ratio > 1.15 confirms crowd leaning YES
4. Fee-aware EV = (win_prob × profit) - ((1-win_prob) × loss) - Kalshi_fee ≥ 4%

**Weather (KXHIGH*):**
1. NOAA forecast ≥ 5°F below threshold → NO signal
2. Historical NO win rate ≥ 70% (50-yr backtest, nearest-5°F snap)
3. YES ask ≤ 0.30 (strong NO implied by market)
4. EV ≥ 5%

## Goal

Grow Kalshi balance from $25.83 → $50.00 to fund AlvaradoTech VPS.

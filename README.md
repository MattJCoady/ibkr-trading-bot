# IBKR trading bot

Moving-average crossover bot for Interactive Brokers. Paper trading by default.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Backtest (no IBKR needed)
```bash
python backtest.py SPY --start 2015-01-01
```

## Paper trade
1. Open TWS (or IB Gateway) and log into your **paper** account.
2. Settings → API → enable "ActiveX and Socket Clients". The paper port is 7497 (TWS) or 4002 (Gateway).
3. Run `python bot.py SPY --qty 10 --dry-run` to see the order it would place, then drop `--dry-run`.
4. Schedule it once a day after the close, e.g. cron: `15 16 * * 1-5 cd /path/to/bot && .venv/bin/python bot.py SPY --qty 10`

## Live trading
The bot refuses to trade any account that doesn't start with `DU` (IBKR's paper prefix) unless you pass `--live`.

## Adding your own rules
Write a function in `strategies.py` that takes a DataFrame with a `close` column and returns 1 (long) or 0 (flat) per bar. Add it to `STRATEGIES`, then use `--strategy yourname` with both `backtest.py` and `bot.py`.

Run the tests with `pytest`.

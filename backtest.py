"""Backtest a strategy on daily bars from Yahoo Finance.
Usage: python backtest.py SPY --strategy sma --start 2015-01-01"""
import argparse

import pandas as pd
import yfinance as yf

from strategies import STRATEGIES


def run(df: pd.DataFrame, strategy, cost: float = 0.0005) -> dict:
    target = strategy(df)
    held = target.shift(1).fillna(0)  # trade on the bar after the signal: no lookahead
    rets = df["close"].pct_change().fillna(0)
    trades = held.diff().abs().fillna(0)
    equity = (1 + held * rets - trades * cost).cumprod()
    return {
        "total_return": equity.iloc[-1] - 1,
        "buy_hold_return": df["close"].iloc[-1] / df["close"].iloc[0] - 1,
        "max_drawdown": (equity / equity.cummax() - 1).min(),
        "trades": int(trades.sum()),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("symbol")
    p.add_argument("--strategy", default="sma", choices=STRATEGIES)
    p.add_argument("--start", default="2015-01-01")
    a = p.parse_args()
    df = yf.download(a.symbol, start=a.start, auto_adjust=True, progress=False, multi_level_index=False)
    if df.empty:
        raise SystemExit(f"No data for {a.symbol} (bad symbol or no network).")
    df.columns = df.columns.str.lower()
    for k, v in run(df, STRATEGIES[a.strategy]).items():
        print(f"{k:>16}: {v:.2%}" if isinstance(v, float) else f"{k:>16}: {v}")


if __name__ == "__main__":
    main()

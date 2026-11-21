"""Strategies: each takes a DataFrame with a 'close' column and returns the
target position per bar (1 = long, 0 = flat). Add your own rules here and
register them in STRATEGIES."""
import pandas as pd


def sma_crossover(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.Series:
    fast_ma = df["close"].rolling(fast).mean()
    slow_ma = df["close"].rolling(slow).mean()
    return (fast_ma > slow_ma).astype(int)


STRATEGIES = {"sma": sma_crossover}

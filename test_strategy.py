import pandas as pd

from backtest import run
from strategies import sma_crossover


def test_crossover_goes_long_in_uptrend_and_flat_in_downtrend():
    close = pd.Series(list(range(100, 200)) + list(range(200, 100, -1)), dtype=float)
    df = pd.DataFrame({"close": close})
    sig = sma_crossover(df, fast=5, slow=20)
    assert sig.iloc[60] == 1
    assert sig.iloc[-1] == 0


def test_backtest_has_no_lookahead():
    # Signal flips long on the jump bar; the jump itself must not be captured.
    df = pd.DataFrame({"close": [100.0, 100.0, 200.0, 200.0]})
    res = run(df, lambda d: (d["close"] > 150).astype(int), cost=0)
    assert res["total_return"] == 0
    assert res["trades"] == 1

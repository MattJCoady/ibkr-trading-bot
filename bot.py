"""Run once per trading day (e.g. from cron after the close). Pulls daily bars
from IBKR, computes the strategy's target, and orders the difference.
Needs TWS or IB Gateway running with the API enabled.

Paper only unless you pass --live AND the account is a live one.
Usage: python bot.py SPY --qty 10 [--port 7497] [--dry-run]"""
import argparse

import pandas as pd
from ib_async import IB, MarketOrder, Stock, util

from strategies import STRATEGIES


def main():
    p = argparse.ArgumentParser()
    p.add_argument("symbol")
    p.add_argument("--qty", type=int, required=True, help="shares to hold when long")
    p.add_argument("--strategy", default="sma", choices=STRATEGIES)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=7497, help="7497 TWS paper, 4002 Gateway paper")
    p.add_argument("--client-id", type=int, default=1)
    p.add_argument("--dry-run", action="store_true", help="print the order, don't send it")
    p.add_argument("--live", action="store_true", help="allow a real-money account")
    a = p.parse_args()

    ib = IB()
    ib.connect(a.host, a.port, clientId=a.client_id)
    try:
        account = ib.managedAccounts()[0]
        # IBKR paper accounts start with "DU"; anything else is real money.
        if not account.startswith("DU") and not a.live:
            raise SystemExit(f"Account {account} is LIVE. Refusing without --live.")

        contract = Stock(a.symbol, "SMART", "USD")
        ib.qualifyContracts(contract)
        bars = ib.reqHistoricalData(contract, "", "1 Y", "1 day", "TRADES", useRTH=True)
        df = util.df(bars)
        if df is None or df.empty:
            raise SystemExit("No historical data returned.")
        target = int(STRATEGIES[a.strategy](df).iloc[-1]) * a.qty

        held = sum(p.position for p in ib.positions(account) if p.contract.conId == contract.conId)
        delta = int(target - held)
        print(f"{account} {a.symbol}: held {held}, target {target}, order {delta:+d}")
        if delta == 0 or a.dry_run:
            return
        trade = ib.placeOrder(contract, MarketOrder("BUY" if delta > 0 else "SELL", abs(delta)))
        ib.sleep(5)
        print("order status:", trade.orderStatus.status)
    finally:
        ib.disconnect()


if __name__ == "__main__":
    main()

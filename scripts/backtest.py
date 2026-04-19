#!/usr/bin/env python3
"""
Theta-Prime Backtester
----------------------
Simulates a cash-secured put selling strategy on historical data.

Usage:
    python scripts/backtest.py AAPL --delta 0.20 --dte 30
    python scripts/backtest.py NVDA --delta 0.15 --dte 45 --start 2022-01-01
"""

import argparse
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_put(S: float, K: float, T: float, r: float, sigma: float) -> Dict:
    """Return put price and Greeks via Black-Scholes."""
    if T <= 0 or sigma <= 0:
        intrinsic = max(K - S, 0.0)
        return {"price": intrinsic, "delta": -1.0 if S < K else 0.0, "theta": 0.0}

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    put_price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    delta = norm_cdf(d1) - 1.0
    gamma = norm_cdf(d1) / (S * sigma * math.sqrt(T))
    theta = (
        -(S * norm_cdf(d1) * sigma) / (2 * math.sqrt(T))
        + r * K * math.exp(-r * T) * norm_cdf(-d2)
    ) / 365.0
    vega = S * norm_cdf(d1) * math.sqrt(T) / 100.0

    return {
        "price": max(0.0, put_price),
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega,
        "d1": d1,
        "d2": d2,
    }


def simulate_put_selling(
    prices: List[float],
    dates: List[str],
    target_delta: float = 0.20,
    dte: int = 30,
    risk_free_rate: float = 0.045,
    iv_estimate: float = 0.30,
    position_size: float = 10_000.0,
) -> Dict:
    """
    Walk forward through price history and simulate selling a put every `dte` days.
    Records each trade: entry date, strike, premium collected, exit PnL.
    """
    trades = []
    i = 0
    total_days = len(prices)

    while i < total_days - dte:
        S = prices[i]
        entry_date = dates[i]
        T = dte / 365.0

        # Find strike closest to target delta
        best_strike = None
        best_delta_diff = float("inf")

        for pct in [x * 0.01 for x in range(60, 100)]:
            K = S * pct
            result = black_scholes_put(S, K, T, risk_free_rate, iv_estimate)
            diff = abs(abs(result["delta"]) - target_delta)
            if diff < best_delta_diff:
                best_delta_diff = diff
                best_strike = K
                best_entry_result = result

        if best_strike is None:
            i += dte
            continue

        premium = best_entry_result["price"]
        if premium < 0.01:
            i += dte
            continue

        # Check exit price at expiry
        exit_idx = min(i + dte, total_days - 1)
        S_exit = prices[exit_idx]
        exit_date = dates[exit_idx]

        intrinsic_at_expiry = max(best_strike - S_exit, 0.0)
        pnl = (premium - intrinsic_at_expiry) * 100  # per contract
        win = intrinsic_at_expiry == 0.0

        max_contracts = int(position_size / (best_strike * 100))
        scaled_pnl = pnl * max(1, max_contracts)

        trades.append({
            "entry_date": entry_date,
            "exit_date": exit_date,
            "spot_entry": round(S, 2),
            "spot_exit": round(S_exit, 2),
            "strike": round(best_strike, 2),
            "premium": round(premium, 4),
            "delta": round(best_entry_result["delta"], 4),
            "pnl": round(scaled_pnl, 2),
            "win": win,
            "contracts": max(1, max_contracts),
        })

        i += dte

    if not trades:
        return {"trades": [], "summary": {}}

    wins = [t for t in trades if t["win"]]
    losses = [t for t in trades if not t["win"]]
    total_pnl = sum(t["pnl"] for t in trades)
    win_rate = len(wins) / len(trades) * 100

    return {
        "trades": trades,
        "summary": {
            "total_trades": len(trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate_pct": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "avg_pnl_per_trade": round(total_pnl / len(trades), 2),
            "best_trade": round(max(t["pnl"] for t in trades), 2),
            "worst_trade": round(min(t["pnl"] for t in trades), 2),
        },
    }


def run_backtest(
    ticker: str,
    delta: float = 0.20,
    dte: int = 30,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    try:
        import yfinance as yf
    except ImportError:
        print("yfinance not installed. Run: pip install yfinance")
        return

    print(f"\nTheta-Prime Backtester")
    print(f"Ticker : {ticker.upper()}")
    print(f"Delta  : {delta:.2f}  |  DTE: {dte}  |  Period: {start or '2y ago'} → {end or 'today'}")
    print("-" * 55)

    period = "2y" if start is None else "max"
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        print(f"No data found for {ticker}")
        return

    hist.reset_index(inplace=True)
    hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")

    if start:
        hist = hist[hist["Date"] >= start]
    if end:
        hist = hist[hist["Date"] <= end]

    if len(hist) < dte * 2:
        print("Not enough data for backtesting.")
        return

    prices = hist["Close"].tolist()
    dates = hist["Date"].tolist()

    # Estimate IV from historical volatility
    import statistics
    if len(prices) >= 21:
        returns = [math.log(prices[i] / prices[i - 1]) for i in range(1, min(21, len(prices)))]
        daily_vol = statistics.stdev(returns)
        iv_estimate = daily_vol * math.sqrt(252)
    else:
        iv_estimate = 0.30

    result = simulate_put_selling(prices, dates, target_delta=delta, dte=dte, iv_estimate=iv_estimate)

    if not result["trades"]:
        print("No trades generated.")
        return

    s = result["summary"]
    print(f"\nSummary:")
    print(f"  Trades       : {s['total_trades']}")
    print(f"  Win Rate     : {s['win_rate_pct']}%  ({s['wins']} wins / {s['losses']} losses)")
    print(f"  Total PnL    : ${s['total_pnl']:,.2f}")
    print(f"  Avg PnL/Trade: ${s['avg_pnl_per_trade']:,.2f}")
    print(f"  Best Trade   : ${s['best_trade']:,.2f}")
    print(f"  Worst Trade  : ${s['worst_trade']:,.2f}")

    print(f"\nTrade Log (last 10):")
    print(f"  {'Entry':<12} {'Exit':<12} {'Strike':>8} {'Premium':>8} {'Delta':>7} {'PnL':>10} {'W/L'}")
    print("  " + "-" * 65)
    for t in result["trades"][-10:]:
        wl = "WIN" if t["win"] else "LOSS"
        print(
            f"  {t['entry_date']:<12} {t['exit_date']:<12} "
            f"${t['strike']:>7.2f} ${t['premium']:>7.4f} "
            f"{t['delta']:>7.4f} ${t['pnl']:>9.2f}  {wl}"
        )

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Theta-Prime Put-Selling Backtester")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    parser.add_argument("--delta", type=float, default=0.20, help="Target delta (default: 0.20)")
    parser.add_argument("--dte", type=int, default=30, help="Days to expiration (default: 30)")
    parser.add_argument("--start", type=str, default=None, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=None, help="End date YYYY-MM-DD")
    args = parser.parse_args()

    run_backtest(args.ticker, delta=args.delta, dte=args.dte, start=args.start, end=args.end)

import sys
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import yfinance as yf
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import scripts.market_scanner as scanner

app = FastAPI(
    title="Theta-Prime API",
    description="Options scanner for put-selling opportunities with VIX-based risk filtering.",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "TSLA", "JPM", "V", "UNH",
]


class WatchlistRequest(BaseModel):
    tickers: List[str]
    min_pop: float = 0.70


def get_vix_market_status():
    try:
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="1d")

        if vix_data.empty:
            current_vix = 20.0
        else:
            current_vix = float(vix_data["Close"].iloc[-1])

        if current_vix < 18:
            status = "Safe"
            crash_prob = current_vix / 100.0
            safety_score = 100 - current_vix
        elif current_vix <= 25:
            status = "Caution"
            crash_prob = current_vix / 100.0
            safety_score = 100 - current_vix
        else:
            status = "Danger"
            crash_prob = min(1.0, current_vix / 50.0)
            safety_score = max(0, 100 - current_vix)

        return {
            "status": status,
            "crash_probability": crash_prob,
            "safety_score": max(0, min(100, safety_score)),
            "vix": current_vix,
        }
    except Exception:
        return {
            "status": "Unknown",
            "crash_probability": 0.25,
            "safety_score": 75.0,
            "vix": None,
        }


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.2.0"}


@app.get("/api/vix")
async def get_vix():
    """Return current VIX level with market regime classification."""
    vix_status = get_vix_market_status()
    return vix_status


@app.get("/api/scan/{ticker}")
async def scan_ticker(
    ticker: str,
    min_pop: float = Query(default=0.50, ge=0.0, le=1.0, description="Minimum probability of profit (0–1)"),
):
    ticker = ticker.upper().strip()
    if not ticker or len(ticker) > 10:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol")

    try:
        print(f"Scanning ticker: {ticker} (min_pop={min_pop})")
        opportunities_data = scanner.get_data(ticker, min_pop=min_pop)

        vix_status = get_vix_market_status()

        if not opportunities_data:
            return {
                "ticker": ticker,
                "market_status": vix_status["status"],
                "crash_probability": vix_status["crash_probability"],
                "safety_score": vix_status["safety_score"],
                "vix": vix_status["vix"],
                "opportunities": [],
            }

        opportunities = opportunities_data.get("opportunities", [])

        return {
            "ticker": ticker,
            "market_status": vix_status["status"],
            "crash_probability": vix_status["crash_probability"],
            "safety_score": vix_status["safety_score"],
            "vix": vix_status["vix"],
            "opportunities": opportunities,
            "spot_price": opportunities_data.get("spot_price"),
            "expiry": opportunities_data.get("expiry"),
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e),
            "market_status": "Error",
            "crash_probability": None,
            "opportunities": [],
        }


@app.post("/api/watchlist")
async def scan_watchlist(request: WatchlistRequest):
    """Batch-scan a list of tickers and return all opportunities ranked by win probability."""
    tickers = [t.upper().strip() for t in request.tickers if t.strip()]
    if not tickers:
        raise HTTPException(status_code=400, detail="No tickers provided")
    if len(tickers) > 25:
        raise HTTPException(status_code=400, detail="Maximum 25 tickers per request")

    vix_status = get_vix_market_status()
    results = []

    for ticker in tickers:
        try:
            data = scanner.get_data(ticker, min_pop=request.min_pop)
            if data and data.get("opportunities"):
                best = max(data["opportunities"], key=lambda o: o["win_prob"])
                results.append({
                    "ticker": ticker,
                    "spot_price": data.get("spot_price"),
                    "expiry": data.get("expiry"),
                    "best_opportunity": best,
                    "total_opportunities": len(data["opportunities"]),
                })
        except Exception as e:
            print(f"Watchlist scan failed for {ticker}: {e}")

    results.sort(key=lambda r: r["best_opportunity"]["win_prob"], reverse=True)

    return {
        "market_status": vix_status["status"],
        "vix": vix_status["vix"],
        "safety_score": vix_status["safety_score"],
        "scanned": len(tickers),
        "results": results,
    }


@app.get("/api/watchlist/default")
async def get_default_watchlist():
    """Return the default watchlist of tickers."""
    return {"tickers": DEFAULT_WATCHLIST}


@app.get("/api/chart/{ticker}")
async def get_chart_data(
    ticker: str,
    period: str = Query(default="1y", description="Data period: 1mo, 3mo, 6mo, 1y, 2y"),
):
    ticker = ticker.upper().strip()
    valid_periods = {"1mo", "3mo", "6mo", "1y", "2y"}
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Choose from: {', '.join(valid_periods)}")

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"historical": []}

        hist.reset_index(inplace=True)

        if "Date" not in hist.columns:
            return {"historical": []}

        hist["Date"] = pd.to_datetime(hist["Date"]).dt.strftime("%Y-%m-%d")

        historical = []
        for _, row in hist.iterrows():
            if any(pd.isna(row.get(col)) for col in ["Open", "High", "Low", "Close"]):
                continue
            historical.append({
                "time": str(row["Date"]),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if not pd.isna(row.get("Volume")) else 0,
            })

        return {"historical": historical, "ticker": ticker, "period": period}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"historical": [], "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

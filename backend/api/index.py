import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import yfinance as yf
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import scripts.market_scanner as scanner

app = FastAPI(title="Theta-Prime API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


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
            "vix": current_vix
        }
    except Exception as e:
        return {
            "status": "Unknown",
            "crash_probability": 0.25,
            "safety_score": 75.0,
            "vix": None
        }


@app.get("/api/scan/{ticker}")
async def scan_ticker(ticker: str):
    try:
        print(f"Scanning ticker: {ticker}")
        opportunities_data = scanner.get_data(ticker, min_pop=0.50)
        
        if not opportunities_data:
            print(f"No opportunities data found for {ticker}")
            vix_status = get_vix_market_status()
            return {
                "ticker": ticker,
                "market_status": vix_status["status"],
                "crash_probability": vix_status["crash_probability"],
                "safety_score": vix_status["safety_score"],
                "vix": vix_status["vix"],
                "opportunities": []
            }
        
        vix_status = get_vix_market_status()
        
        opportunities = opportunities_data.get("opportunities", [])
        
        return {
            "ticker": ticker,
            "market_status": vix_status["status"],
            "crash_probability": vix_status["crash_probability"],
            "safety_score": vix_status["safety_score"],
            "vix": vix_status["vix"],
            "opportunities": opportunities,
            "spot_price": opportunities_data.get("spot_price"),
            "expiry": opportunities_data.get("expiry")
        }
        
    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e),
            "market_status": "Error",
            "crash_probability": None,
            "opportunities": []
        }


@app.get("/api/chart/{ticker}")
async def get_chart_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            return {"historical": []}
        
        hist.reset_index(inplace=True)
        
        if 'Date' not in hist.columns:
            return {"historical": []}
        
        hist['Date'] = pd.to_datetime(hist['Date']).dt.strftime('%Y-%m-%d')
        
        historical = []
        for _, row in hist.iterrows():
            if pd.isna(row.get("Open")) or pd.isna(row.get("High")) or pd.isna(row.get("Low")) or pd.isna(row.get("Close")):
                continue
            
            historical.append({
                "time": str(row['Date']),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
            })
        
        return {"historical": historical}
        
    except Exception as e:
        import traceback
        print(f"Chart data error for {ticker}: {e}")
        traceback.print_exc()
        return {"historical": [], "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


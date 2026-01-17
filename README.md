# Theta-Prime

Options scanner that filters put-selling opportunities based on win probability and market conditions.

I built this because I wanted a faster way to scan through S&P 500 stocks and find good put-selling setups without manually checking each one. The standard approach of selling puts blind doesn't work when the market is crashing, so I added VIX-based risk filtering to avoid bad trades.

## What it does

Scans tickers for put options and calculates win probabilities using Black-Scholes formulas. The C++ engine handles batch processing for speed - can calculate Greeks for thousands of options in milliseconds. Before showing any trades, it checks the VIX to see if market conditions are safe.

The frontend shows filtered opportunities with win probabilities above your threshold, along with current market status and relevant metrics.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
python models/regime_net.py train
```

## Run

Backend:
```bash
source venv/bin/activate
PYTHONPATH=. uvicorn backend.api.index:app --reload --host 127.0.0.1 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Stack

- C++ with pybind11 for the math engine
- FastAPI for the backend
- Next.js 14 with Tailwind for the frontend
- PyTorch for the market regime model (currently using VIX instead)

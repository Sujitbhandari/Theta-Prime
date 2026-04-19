# Theta-Prime

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Options scanner that filters put-selling opportunities based on win probability and market conditions.

Built for traders who want a faster way to scan through S&P 500 stocks and find good put-selling setups without manually checking each one. The standard approach of selling puts blind doesn't work when the market is crashing, so Theta-Prime adds VIX-based risk filtering to avoid bad trades.

---

## Features

- **C++ Greeks Engine** — Black-Scholes Greeks (delta, gamma, theta, vega, rho) calculated via pybind11 in milliseconds for thousands of options
- **VIX Risk Filter** — Automatically blocks trade signals when market volatility is elevated
- **Win Probability Scanner** — Filters put opportunities above a configurable PoP threshold (default 80%)
- **Watchlist Batch Scan** — Scan multiple tickers in one request via `/api/watchlist`
- **Live Price Charts** — 1-year OHLC candlestick chart for any ticker
- **Market Regime Badge** — Real-time Safe / Caution / Danger status based on VIX

---

## Architecture

```
Theta-Prime/
├── backend/
│   ├── api/index.py          # FastAPI app — scan, chart, watchlist, VIX endpoints
│   └── cpp_engine/           # C++ source for fast_greeks pybind11 module
├── frontend/
│   ├── app/                  # Next.js 14 app router
│   └── components/           # RegimeBadge, OpportunityTable, StatsPanel, …
├── scripts/
│   ├── market_scanner.py     # Core scanning + Greeks logic
│   └── backtest.py           # Historical win-rate backtester
├── models/
│   └── regime_net.py         # PyTorch market-regime classifier (WIP)
├── tests/
│   └── test_scanner.py       # Unit tests for scanner utilities
└── requirements.txt
```

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

## Run

**Backend:**
```bash
source venv/bin/activate
PYTHONPATH=. uvicorn backend.api.index:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## API Reference

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/scan/{ticker}` | Scan a single ticker for put opportunities |
| `GET /api/chart/{ticker}` | 1-year OHLC price history |
| `GET /api/vix` | Current VIX level and market regime |
| `POST /api/watchlist` | Batch scan a list of tickers |

---

## Stack

- **C++** with pybind11 for the math engine
- **FastAPI** for the backend
- **Next.js 14** with Tailwind CSS for the frontend
- **yfinance** for market data
- **PyTorch** for the market regime model (currently using VIX threshold)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

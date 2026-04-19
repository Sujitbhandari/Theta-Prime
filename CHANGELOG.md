# Changelog

All notable changes to Theta-Prime are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- `/api/vix` endpoint returning current VIX and regime classification
- `/api/watchlist` POST endpoint for batch-scanning multiple tickers, ranked by win probability
- `/api/watchlist/default` endpoint returning a curated default watchlist
- `period` query parameter on `/api/chart/{ticker}` (1mo / 3mo / 6mo / 1y / 2y)
- Volume field in chart OHLC response
- `scripts/backtest.py` — walk-forward put-selling backtester with P&L reporting
- `tests/test_scanner.py` — unit tests for Black-Scholes, PoP, VIX regime, and backtest simulator
- GitHub Actions CI workflow (Python 3.11/3.12 lint + tests, Next.js type-check)
- GitHub CodeQL security analysis workflow
- README badges (Python, Next.js, FastAPI, License)
- API reference table in README
- `CONTRIBUTING.md` guidelines

### Changed
- Backend API version bumped to `1.2.0`
- `/api/scan/{ticker}` now accepts a `min_pop` query parameter (0–1)
- Ticker validation added (uppercase normalisation, max length guard)
- Improved error handling across all endpoints using FastAPI `HTTPException`
- Chart endpoint validates `period` against an allowed set

### Fixed
- Crash when `yfinance` returns an empty DataFrame for VIX

---

## [1.1.0] — 2025-03-19

### Added
- `PriceChart` component with 1-year candlestick view
- `StatsPanel` opportunity metrics section
- VIX safety score visualisation

### Changed
- Frontend migrated to Next.js 14 App Router

---

## [1.0.0] — 2025-01-16

### Added
- Initial release
- C++ pybind11 Greeks engine (`fast_greeks`)
- FastAPI backend with `/api/scan` and `/api/chart`
- Next.js 14 frontend with `RegimeBadge`, `OpportunityTable`, `TickerSearch`
- VIX-based market regime filtering

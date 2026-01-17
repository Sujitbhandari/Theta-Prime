#!/usr/bin/env python3

import time
import random
import sys
import math
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf
from requests_cache import CachedSession

try:
    import fast_greeks
except ImportError:
    print("ERROR: fast_greeks module not found!")
    print("Please install it first by running: pip install -e .")
    sys.exit(1)


def get_sp500_tickers() -> List[str]:
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        sp500_table = tables[0]
        tickers = sp500_table["Symbol"].tolist()
    except Exception as e:
        print(f"Warning: Could not fetch from Wikipedia ({e}). Using hardcoded list.")
        tickers = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B",
            "V", "JNJ", "WMT", "XOM", "JPM", "UNH", "MA", "PG", "HD", "CVX",
            "LLY", "MRK", "ABBV", "AVGO", "COST", "PEP", "ADBE", "NFLX", "TMO",
            "CSCO", "MCD", "ABT", "DHR", "VZ", "WFC", "ACN", "DIS", "CRM",
            "PM", "NKE", "HON", "NEE", "QCOM", "TXN", "INTU", "AMD", "UPS",
            "MS", "RTX", "SPGI", "C", "GS"
        ]
    
    cleaned_tickers = []
    for ticker in tickers:
        cleaned = ticker.replace(".", "-")
        cleaned_tickers.append(cleaned)
    
    return cleaned_tickers


class SmartFetcher:
    def __init__(self, cache_expire_seconds: int = 3600):
        self.last_request_time = 0.0
    
    def _throttle(self):
        min_delay = 0.5
        max_delay = 1.5
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        self.last_request_time = time.time()
    
    def fetch_option_chain(self, ticker: str) -> Optional[yf.Ticker]:
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                self._throttle()
                
                stock = yf.Ticker(ticker)
                option_dates = stock.options
                
                if not option_dates:
                    return None
                
                return stock
                
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"Request failed for {ticker}, retrying in {delay:.1f}s... ({e})")
                    time.sleep(delay)
                else:
                    print(f"Failed to fetch {ticker} after {max_retries} attempts: {e}")
                    return None
        
        return None


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def calculate_probability_of_profit(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    implied_vol: float,
    delta: float
) -> float:
    if time_to_expiry <= 0 or implied_vol <= 0:
        return 50.0
    
    if abs(delta) >= 1.0:
        return 50.0
    
    pop = 1.0 + delta
    
    pop = max(0.001, min(0.999, pop))
    
    return pop * 100.0


def process_ticker(ticker: str, risk_free_rate: float = 0.05) -> Optional[Dict]:
    fetcher = SmartFetcher()
    
    print(f"Processing {ticker}...")
    stock = fetcher.fetch_option_chain(ticker)
    
    if not stock:
        return None
    
    try:
        info = stock.info
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        
        if not current_price:
            print(f"Could not get current price for {ticker}")
            return None
        
        option_dates = stock.options
        if not option_dates:
            print(f"No option dates found for {ticker}")
            return None
        
        nearest_expiry = option_dates[0]
        opt_chain = stock.option_chain(nearest_expiry)
        puts = opt_chain.puts
        
        if puts.empty:
            print(f"No puts found for {ticker}")
            return None
        
        expiry_date = pd.to_datetime(nearest_expiry)
        now = pd.Timestamp.now()
        time_to_expiry = (expiry_date - now).total_seconds() / (365.0 * 24 * 3600)
        
        if time_to_expiry <= 0:
            time_to_expiry = 1.0 / 365.0
        
        strikes = puts["strike"].values.tolist()
        bid_prices = puts["bid"].values.tolist()
        ask_prices = puts["ask"].values.tolist()
        ivs = puts["impliedVolatility"].values.tolist()
        
        mid_prices = [(bid + ask) / 2.0 for bid, ask in zip(bid_prices, ask_prices)]
        
        valid_indices = []
        spot_prices_list = []
        strikes_list = []
        ttes = []
        rates = []
        vols = []
        
        for i in range(len(strikes)):
            if ivs[i] > 0 and mid_prices[i] > 0:
                valid_indices.append(i)
                spot_prices_list.append(current_price)
                strikes_list.append(strikes[i])
                ttes.append(time_to_expiry)
                rates.append(risk_free_rate)
                vols.append(ivs[i])
        
        if not valid_indices:
            print(f"No valid options for {ticker}")
            return None
        
        calc = fast_greeks.OptionCalculator()
        
        start_time = time.time()
        greeks_results = calc.calculate_put_greeks_batch(
            spot_prices_list,
            strikes_list,
            ttes,
            rates,
            vols
        )
        calc_time = (time.time() - start_time) * 1000
        
        best_option = None
        best_pop = 0.0
        
        for idx, valid_idx in enumerate(valid_indices):
            price, delta, gamma, theta, vega, rho = greeks_results[idx]
            strike = strikes[valid_idx]
            mid_price = mid_prices[valid_idx]
            iv = ivs[valid_idx]
            
            pop = calculate_probability_of_profit(
                current_price, strike, time_to_expiry, risk_free_rate, iv, delta
            )
            
            if -0.30 <= delta <= -0.15 and pop > best_pop:
                best_pop = pop
                best_option = {
                    "strike": strike,
                    "delta": delta,
                    "gamma": gamma,
                    "theta": theta,
                    "vega": vega,
                    "premium": mid_price,
                    "iv": iv,
                    "pop": pop
                }
        
        if best_option:
            best_option["calc_time_ms"] = calc_time
            best_option["expiry"] = nearest_expiry
            best_option["spot_price"] = current_price
            best_option["num_options_processed"] = len(valid_indices)
        
        return best_option
        
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_data(ticker: str, risk_free_rate: float = 0.045, min_pop: float = 0.80) -> Optional[Dict]:
    fetcher = SmartFetcher()
    
    stock = fetcher.fetch_option_chain(ticker)
    
    if not stock:
        return None
    
    try:
        info = stock.info
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        
        if not current_price or current_price <= 0:
            return None
        
        option_dates = stock.options
        if not option_dates:
            return None
        
        nearest_expiry = option_dates[0]
        opt_chain = stock.option_chain(nearest_expiry)
        puts = opt_chain.puts
        
        if puts.empty:
            return None
        
        expiry_date = pd.to_datetime(nearest_expiry)
        now = pd.Timestamp.now()
        time_to_expiry = (expiry_date - now).total_seconds() / (365.0 * 24 * 3600)
        
        if time_to_expiry <= 0:
            time_to_expiry = 1.0 / 365.0
        
        strikes = puts["strike"].values.tolist()
        bid_prices = puts["bid"].values.tolist()
        ask_prices = puts["ask"].values.tolist()
        ivs_raw = puts["impliedVolatility"].values.tolist()
        
        mid_prices = [(bid + ask) / 2.0 for bid, ask in zip(bid_prices, ask_prices)]
        
        valid_indices = []
        spot_prices_list = []
        strikes_list = []
        ttes = []
        rates = []
        vols = []
        
        strike_min = current_price * 0.70
        strike_max = current_price * 1.30
        
        for i in range(len(strikes)):
            strike = strikes[i]
            iv_raw = ivs_raw[i] if i < len(ivs_raw) else 0
            
            if iv_raw <= 0 or mid_prices[i] <= 0:
                continue
            
            if strike < strike_min or strike > strike_max:
                continue
            
            if strike < 0.50:
                continue
            
            iv_normalized = iv_raw
            
            if iv_normalized > 4.0:
                iv_normalized = iv_normalized / 100.0
            
            if iv_normalized > 5.0:
                iv_normalized = 5.0
            
            if iv_normalized < 0.001 or iv_normalized > 2.0:
                continue
            
            valid_indices.append(i)
            spot_prices_list.append(current_price)
            strikes_list.append(strike)
            ttes.append(time_to_expiry)
            rates.append(risk_free_rate)
            vols.append(iv_normalized)
        
        if not valid_indices:
            return None
        
        calc = fast_greeks.OptionCalculator()
        
        print(f"Processing {len(valid_indices)} valid options for {ticker}")
        
        greeks_results = calc.calculate_put_greeks_batch(
            spot_prices_list,
            strikes_list,
            ttes,
            rates,
            vols
        )
        
        opportunities = []
        options_before_filter = 0
        
        for idx, valid_idx in enumerate(valid_indices):
            price, delta, gamma, theta, vega, rho = greeks_results[idx]
            strike = strikes[valid_idx]
            mid_price = mid_prices[valid_idx]
            iv_normalized = vols[idx]
            
            options_before_filter += 1
            
            if abs(delta) < 0.01:
                continue
            
            if not (-0.35 <= delta <= -0.10):
                continue
            
            if mid_price < 0.05:
                continue
            
            pop = calculate_probability_of_profit(
                current_price, strike, time_to_expiry, risk_free_rate, iv_normalized, delta
            )
            
            pop = max(10.0, min(95.0, pop))
            
            pop_ratio = pop / 100.0
            
            if pop_ratio >= min_pop:
                opportunities.append({
                    "strike": float(strike),
                    "expiry": nearest_expiry,
                    "premium": float(mid_price),
                    "win_prob": float(pop_ratio),
                    "delta": float(delta),
                    "gamma": float(gamma),
                    "theta": float(theta),
                    "vega": float(vega),
                    "iv": float(iv_normalized)
                })
        
        print(f"Found {options_before_filter} options before filtering, {len(opportunities)} opportunities after filtering (min_pop={min_pop})")
        
        if opportunities:
            return {
                "ticker": ticker,
                "spot_price": float(current_price),
                "expiry": nearest_expiry,
                "opportunities": opportunities
            }
        
        return None
        
    except Exception as e:
        print(f"Error in get_data for {ticker}: {e}")
        return None


def main():
    print("S&P 500 Market Scanner\n")
    
    print("Fetching S&P 500 ticker list...")
    all_tickers = get_sp500_tickers()
    print(f"Found {len(all_tickers)} tickers\n")
    
    sample_size = 5
    random.seed(42)
    sample_tickers = random.sample(all_tickers, min(sample_size, len(all_tickers)))
    
    print(f"Processing {sample_size} random tickers...\n")
    
    results = []
    for ticker in sample_tickers:
        result = process_ticker(ticker)
        if result:
            results.append((ticker, result))
            print(f"Ticker: {ticker} | C++ Calculation Time: {result['calc_time_ms']:.3f}ms | "
                  f"Best Put to Sell: Strike ${result['strike']:.2f} (PoP: {result['pop']:.1f}%)")
        else:
            print(f"Ticker: {ticker} | Failed to process")
        print()
    
    if results:
        print("Summary:")
        for ticker, result in results:
            print(f"  {ticker}: Strike ${result['strike']:.2f}, Delta {result['delta']:.3f}, "
                  f"PoP {result['pop']:.1f}%")


if __name__ == "__main__":
    main()


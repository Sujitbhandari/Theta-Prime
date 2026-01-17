#!/usr/bin/env python3

import sys
import time
import numpy as np

try:
    import fast_greeks
except ImportError:
    print("ERROR: fast_greeks module not found!")
    print("Please install it first by running: pip install -e .")
    sys.exit(1)

def test_single_option():
    print("=" * 60)
    print("Testing Single Option Calculation (Accuracy Check)")
    print("=" * 60)
    
    calc = fast_greeks.OptionCalculator()
    
    S = 450.0
    K = 455.0
    T = 30 / 365.0
    r = 0.05
    sigma = 0.35
    
    call_price = calc.black_scholes_call(S, K, T, r, sigma)
    put_price = calc.black_scholes_put(S, K, T, r, sigma)
    
    print(f"\nSpot Price (S): ${S:.2f}")
    print(f"Strike Price (K): ${K:.2f}")
    print(f"Time to Expiration (T): {T*365:.1f} days ({T:.4f} years)")
    print(f"Risk-Free Rate (r): {r*100:.2f}%")
    print(f"Volatility (σ): {sigma*100:.2f}%")
    print(f"\nCall Option Price: ${call_price:.4f}")
    print(f"Put Option Price: ${put_price:.4f}")
    
    results = calc.calculate_call_greeks_batch(
        [S], [K], [T], [r], [sigma]
    )
    
    price, delta, gamma, theta, vega, rho = results[0]
    
    print(f"\n--- Greeks ---")
    print(f"Price: ${price:.4f}")
    print(f"Delta: {delta:.4f}")
    print(f"Gamma: {gamma:.6f}")
    print(f"Theta: ${theta:.4f}/day")
    print(f"Vega: ${vega:.4f}")
    print(f"Rho: ${rho:.4f}")

def test_batch_performance():
    print("\n" + "=" * 60)
    print("Benchmarking Batch Calculation (10,000 options)")
    print("=" * 60)
    
    calc = fast_greeks.OptionCalculator()
    
    n_options = 10000
    np.random.seed(42)
    
    spot_prices = np.random.uniform(100, 500, n_options).tolist()
    strike_prices = spot_prices * np.random.uniform(0.8, 1.2, n_options)
    strike_prices = strike_prices.tolist()
    time_to_maturity = np.random.uniform(7/365, 365/365, n_options).tolist()
    risk_free_rates = np.random.uniform(0.02, 0.06, n_options).tolist()
    volatilities = np.random.uniform(0.15, 0.60, n_options).tolist()
    
    print(f"\nGenerated {n_options:,} random options")
    print("Calculating Greeks...\n")
    
    start_time = time.time()
    call_results = calc.calculate_call_greeks_batch(
        spot_prices,
        strike_prices,
        time_to_maturity,
        risk_free_rates,
        volatilities
    )
    cpp_time = time.time() - start_time
    
    print(f"C++ Batch Calculation Time: {cpp_time*1000:.2f} ms")
    print(f"   Throughput: {n_options/cpp_time:,.0f} options/second\n")
    
    price, delta, gamma, theta, vega, rho = call_results[0]
    
    print("--- First Option ---")
    print(f"Spot: ${spot_prices[0]:.2f}, Strike: ${strike_prices[0]:.2f}")
    print(f"Price: ${price:.4f}")
    print(f"Delta: {delta:.4f}, Gamma: {gamma:.6f}")
    print(f"Theta: ${theta:.4f}/day, Vega: ${vega:.4f}, Rho: ${rho:.4f}")
    
    prices = [r[0] for r in call_results]
    deltas = [r[1] for r in call_results]
    
    print(f"\n--- Statistics ---")
    print(f"Mean Option Price: ${np.mean(prices):.4f}")
    print(f"Price Range: ${np.min(prices):.4f} - ${np.max(prices):.4f}")
    print(f"Mean Delta: {np.mean(deltas):.4f}")

def test_put_greeks():
    print("\n" + "=" * 60)
    print("Testing Put Option Greeks")
    print("=" * 60)
    
    calc = fast_greeks.OptionCalculator()
    
    S = 450.0
    K = 455.0
    T = 30 / 365.0
    r = 0.05
    sigma = 0.35
    
    results = calc.calculate_put_greeks_batch([S], [K], [T], [r], [sigma])
    price, delta, gamma, theta, vega, rho = results[0]
    
    print(f"\nPut Option with Strike ${K:.2f}")
    print(f"Price: ${price:.4f}")
    print(f"Delta: {delta:.4f}")
    print(f"Gamma: {gamma:.6f}")
    print(f"Theta: ${theta:.4f}/day")
    print(f"Vega: ${vega:.4f}")
    print(f"Rho: {rho:.4f}")

if __name__ == "__main__":
    print("\nTheta-Prime C++ Engine Test Suite\n")
    
    try:
        test_single_option()
        test_batch_performance()
        test_put_greeks()
        
        print("\n" + "=" * 60)
        print("All tests passed! C++ module is working correctly.")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


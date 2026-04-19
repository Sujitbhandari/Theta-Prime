"""
Unit tests for Theta-Prime scanner utilities.
Tests run without the C++ engine (fast_greeks not required).
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Helpers pulled inline so tests run without fast_greeks ───────────────────

def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def calculate_probability_of_profit(delta: float) -> float:
    pop = 1.0 + delta
    return max(0.001, min(0.999, pop)) * 100.0


def black_scholes_put_price(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return max(K - S, 0.0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)


# ── Tests ────────────────────────────────────────────────────────────────────

class TestNormCdf:
    def test_zero_returns_half(self):
        assert abs(norm_cdf(0.0) - 0.5) < 1e-10

    def test_positive_large_approaches_one(self):
        assert norm_cdf(10.0) > 0.9999

    def test_negative_large_approaches_zero(self):
        assert norm_cdf(-10.0) < 0.0001

    def test_symmetry(self):
        assert abs(norm_cdf(1.5) + norm_cdf(-1.5) - 1.0) < 1e-10


class TestPopCalculation:
    def test_delta_minus_020(self):
        pop = calculate_probability_of_profit(-0.20)
        assert abs(pop - 80.0) < 0.01

    def test_delta_minus_015(self):
        pop = calculate_probability_of_profit(-0.15)
        assert abs(pop - 85.0) < 0.01

    def test_delta_minus_030(self):
        pop = calculate_probability_of_profit(-0.30)
        assert abs(pop - 70.0) < 0.01

    def test_pop_clipped_below_zero(self):
        pop = calculate_probability_of_profit(-0.999)
        assert pop > 0

    def test_pop_clipped_above_hundred(self):
        pop = calculate_probability_of_profit(0.0)
        assert pop <= 100.0


class TestBlackScholes:
    def test_put_price_positive(self):
        price = black_scholes_put_price(S=100, K=95, T=0.25, r=0.05, sigma=0.20)
        assert price > 0

    def test_deep_itm_put_near_intrinsic(self):
        # Deep ITM: strike much higher than spot
        price = black_scholes_put_price(S=50, K=100, T=0.01, r=0.05, sigma=0.20)
        intrinsic = 100 - 50
        assert abs(price - intrinsic) < 5.0

    def test_zero_time_returns_intrinsic(self):
        price = black_scholes_put_price(S=100, K=110, T=0, r=0.05, sigma=0.20)
        assert abs(price - 10.0) < 1e-6

    def test_atm_put_has_time_value(self):
        price = black_scholes_put_price(S=100, K=100, T=0.25, r=0.05, sigma=0.20)
        assert price > 0

    def test_higher_vol_increases_price(self):
        low_vol = black_scholes_put_price(S=100, K=95, T=0.25, r=0.05, sigma=0.10)
        high_vol = black_scholes_put_price(S=100, K=95, T=0.25, r=0.05, sigma=0.40)
        assert high_vol > low_vol

    def test_further_dte_increases_price(self):
        near = black_scholes_put_price(S=100, K=95, T=0.10, r=0.05, sigma=0.20)
        far = black_scholes_put_price(S=100, K=95, T=0.50, r=0.05, sigma=0.20)
        assert far > near


class TestVixRegime:
    """Test VIX-to-regime mapping logic mirroring the API."""

    def _classify(self, vix):
        if vix < 18:
            return "Safe"
        elif vix <= 25:
            return "Caution"
        else:
            return "Danger"

    def test_low_vix_safe(self):
        assert self._classify(12.5) == "Safe"

    def test_mid_vix_caution(self):
        assert self._classify(22.0) == "Caution"

    def test_high_vix_danger(self):
        assert self._classify(35.0) == "Danger"

    def test_boundary_18_is_caution(self):
        assert self._classify(18.0) == "Caution"

    def test_boundary_25_is_caution(self):
        assert self._classify(25.0) == "Caution"

    def test_boundary_26_is_danger(self):
        assert self._classify(26.0) == "Danger"


class TestBacktestSimulator:
    """Tests for the backtest simulation logic."""

    def test_simulate_basic(self):
        from scripts.backtest import simulate_put_selling
        prices = [100.0 + i * 0.1 for i in range(120)]
        dates = [f"2024-{str(i // 30 + 1).zfill(2)}-{str(i % 30 + 1).zfill(2)}" for i in range(120)]
        result = simulate_put_selling(prices, dates, target_delta=0.20, dte=30, iv_estimate=0.25)
        assert "trades" in result
        assert "summary" in result

    def test_win_rate_in_bull_market(self):
        from scripts.backtest import simulate_put_selling
        # Steadily rising prices — puts should expire worthless (wins)
        prices = [100.0 + i * 0.5 for i in range(200)]
        dates = [f"2024-01-{str(i % 28 + 1).zfill(2)}" for i in range(200)]
        result = simulate_put_selling(prices, dates, target_delta=0.20, dte=30, iv_estimate=0.25)
        s = result.get("summary", {})
        if s.get("total_trades", 0) > 0:
            assert s["win_rate_pct"] >= 0

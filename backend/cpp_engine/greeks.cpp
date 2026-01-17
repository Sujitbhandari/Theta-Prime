#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <vector>
#include <algorithm>

namespace py = pybind11;

double norm_cdf(double x) {
    return 0.5 * (1.0 + std::erf(x / std::sqrt(2.0)));
}

double norm_pdf(double x) {
    return std::exp(-0.5 * x * x) / std::sqrt(2.0 * M_PI);
}

class OptionCalculator {
public:
    OptionCalculator() = default;

    double black_scholes_call(double S, double K, double T, double r, double sigma) {
        if (T <= 0.0) return std::max(S - K, 0.0);
        if (sigma <= 0.0) return std::max(S * std::exp(-r * T) - K * std::exp(-r * T), 0.0);

        double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
        double d2 = d1 - sigma * std::sqrt(T);

        return S * norm_cdf(d1) - K * std::exp(-r * T) * norm_cdf(d2);
    }

    double black_scholes_put(double S, double K, double T, double r, double sigma) {
        if (T <= 0.0) return std::max(K - S, 0.0);
        if (sigma <= 0.0) return std::max(K * std::exp(-r * T) - S * std::exp(-r * T), 0.0);

        double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
        double d2 = d1 - sigma * std::sqrt(T);

        return K * std::exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1);
    }

    std::vector<std::vector<double>> calculate_call_greeks_batch(
        const std::vector<double>& spot_prices,
        const std::vector<double>& strike_prices,
        const std::vector<double>& time_to_maturity,
        const std::vector<double>& risk_free_rates,
        const std::vector<double>& volatilities
    ) {
        size_t n = spot_prices.size();
        std::vector<std::vector<double>> results(n, std::vector<double>(6));

        for (size_t i = 0; i < n; ++i) {
            double S = spot_prices[i];
            double K = strike_prices[i];
            double T = std::max(time_to_maturity[i], 1e-6);
            double r = risk_free_rates[i];
            double sigma = std::max(volatilities[i], 1e-6);

            double sqrt_T = std::sqrt(T);
            double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T);
            double d2 = d1 - sigma * sqrt_T;

            double price = S * norm_cdf(d1) - K * std::exp(-r * T) * norm_cdf(d2);
            results[i][0] = price;

            results[i][1] = norm_cdf(d1);
            results[i][2] = norm_pdf(d1) / (S * sigma * sqrt_T);

            double theta1 = -(S * norm_pdf(d1) * sigma) / (2.0 * sqrt_T);
            double theta2 = -r * K * std::exp(-r * T) * norm_cdf(d2);
            results[i][3] = (theta1 + theta2) / 365.0;

            results[i][4] = S * norm_pdf(d1) * sqrt_T / 100.0;
            results[i][5] = K * T * std::exp(-r * T) * norm_cdf(d2) / 100.0;
        }

        return results;
    }

    std::vector<std::vector<double>> calculate_put_greeks_batch(
        const std::vector<double>& spot_prices,
        const std::vector<double>& strike_prices,
        const std::vector<double>& time_to_maturity,
        const std::vector<double>& risk_free_rates,
        const std::vector<double>& volatilities
    ) {
        size_t n = spot_prices.size();
        std::vector<std::vector<double>> results(n, std::vector<double>(6));

        for (size_t i = 0; i < n; ++i) {
            double S = spot_prices[i];
            double K = strike_prices[i];
            double T = std::max(time_to_maturity[i], 1e-6);
            double r = risk_free_rates[i];
            double sigma = std::max(volatilities[i], 1e-6);

            double sqrt_T = std::sqrt(T);
            double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T);
            double d2 = d1 - sigma * sqrt_T;

            double price = K * std::exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1);
            results[i][0] = price;

            results[i][1] = -norm_cdf(-d1);
            results[i][2] = norm_pdf(d1) / (S * sigma * sqrt_T);

            double theta1 = -(S * norm_pdf(d1) * sigma) / (2.0 * sqrt_T);
            double theta2 = r * K * std::exp(-r * T) * norm_cdf(-d2);
            results[i][3] = (theta1 + theta2) / 365.0;

            results[i][4] = S * norm_pdf(d1) * sqrt_T / 100.0;
            results[i][5] = -K * T * std::exp(-r * T) * norm_cdf(-d2) / 100.0;
        }

        return results;
    }
};

PYBIND11_MODULE(fast_greeks, m) {
    m.doc() = "Black-Scholes Greeks calculator";

    py::class_<OptionCalculator>(m, "OptionCalculator")
        .def(py::init<>())
        .def("black_scholes_call", &OptionCalculator::black_scholes_call,
             py::arg("S"), py::arg("K"), py::arg("T"), py::arg("r"), py::arg("sigma"))
        .def("black_scholes_put", &OptionCalculator::black_scholes_put,
             py::arg("S"), py::arg("K"), py::arg("T"), py::arg("r"), py::arg("sigma"))
        .def("calculate_call_greeks_batch", &OptionCalculator::calculate_call_greeks_batch,
             py::arg("spot_prices"), py::arg("strike_prices"), py::arg("time_to_maturity"),
             py::arg("risk_free_rates"), py::arg("volatilities"))
        .def("calculate_put_greeks_batch", &OptionCalculator::calculate_put_greeks_batch,
             py::arg("spot_prices"), py::arg("strike_prices"), py::arg("time_to_maturity"),
             py::arg("risk_free_rates"), py::arg("volatilities"));
}


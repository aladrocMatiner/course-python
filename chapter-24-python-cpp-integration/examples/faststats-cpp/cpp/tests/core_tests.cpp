#include "faststats_cpp/core.hpp"

#include <cmath>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

int failures = 0;

void check(const bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        ++failures;
    }
}

bool close(const double left, const double right) {
    return std::abs(left - right) <=
           std::max(1e-12, 1e-12 * std::max(std::abs(left), std::abs(right)));
}

template <typename Function>
void check_invalid(Function&& function, const std::string& message) {
    bool rejected = false;
    try {
        function();
    } catch (const std::invalid_argument&) {
        rejected = true;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << message << " (wrong exception: "
                  << error.what() << ")\n";
        ++failures;
        return;
    }
    check(rejected, message);
}

}  // namespace

int main() {
    const auto summary = faststats::summarize(
        std::vector<double>{-3.0, -3.0, -1.0}, 0.5);
    check(summary.count == 3, "summary count");
    check(close(summary.minimum, -3.0), "summary minimum");
    check(close(summary.maximum, -1.0), "summary maximum");
    check(close(summary.mean, -7.0 / 3.0), "input-order mean");
    check(summary.anomaly_count == 3,
          "anomalies are classified against the final mean");
    check(close(summary.anomaly_ratio, 1.0), "anomaly ratio");

    const auto tolerance = faststats::summarize(
        std::vector<double>{0.0, 2.0}, 1.0);
    check(tolerance.anomaly_count == 0,
          "threshold equality is excluded by tolerance band");

    check_invalid(
        [] { static_cast<void>(faststats::summarize(std::vector<double>{}, 0.0)); },
        "empty batch rejected");
    check_invalid(
        [] {
            static_cast<void>(faststats::summarize(
                std::vector<double>{std::numeric_limits<double>::infinity()},
                0.0));
        },
        "non-finite batch rejected");
    check_invalid(
        [] { static_cast<void>(faststats::summarize(std::vector<double>{1.0}, -1.0)); },
        "negative threshold rejected");
    check_invalid(
        [] {
            static_cast<void>(faststats::summarize(
                std::vector<double>(faststats::max_samples + 1, 1.0), 0.0));
        },
        "oversized batch rejected");

    std::vector<double> constant{4.0, 4.0};
    faststats::normalize_in_place(constant.data(), constant.size());
    check(constant == std::vector<double>({0.0, 0.0}),
          "constant buffer normalizes to zero");

    std::vector<double> values{2.0, 4.0, 6.0};
    faststats::normalize_in_place(values.data(), values.size());
    check(close(values[0], 0.0) && close(values[1], 0.5) &&
              close(values[2], 1.0),
          "normalization contract");

    std::vector<double> invalid_values{1.0,
                                       std::numeric_limits<double>::quiet_NaN(),
                                       3.0};
    const auto before = invalid_values;
    check_invalid(
        [&invalid_values] {
            faststats::normalize_in_place(invalid_values.data(),
                                          invalid_values.size());
        },
        "normalization validates before mutation");
    check(std::isnan(invalid_values[1]) && invalid_values[0] == before[0] &&
              invalid_values[2] == before[2],
          "failed normalization is transactional");

    faststats::OnlineStats online;
    check(online.count() == 0 && !online.minimum() && !online.maximum() &&
              !online.mean(),
          "empty online state");
    online.extend(std::vector<double>{1.0, 2.0, 3.0});
    check(online.count() == 3 && close(*online.mean(), 2.0),
          "online extension");
    const auto old_count = online.count();
    const auto old_mean = online.mean();
    check_invalid(
        [&online] {
            online.extend(std::vector<double>{4.0,
                                               std::numeric_limits<double>::infinity()});
        },
        "invalid online extension rejected");
    check(online.count() == old_count && online.mean() == old_mean,
          "invalid online extension preserves state");
    online.reset();
    check(online.count() == 0 && !online.mean(), "online reset");

    return failures == 0 ? 0 : 1;
}

#pragma once

#include <cstddef>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace faststats {

inline constexpr std::size_t max_samples = 1'000'000;
inline constexpr double max_magnitude = 1e150;
inline constexpr double comparison_tolerance = 1e-12;

struct Summary {
    std::size_t count;
    double minimum;
    double maximum;
    double mean;
    std::size_t anomaly_count;
    double anomaly_ratio;
};

class DomainError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

[[nodiscard]] Summary summarize(const double* values, std::size_t size,
                                double threshold);
[[nodiscard]] Summary summarize(const std::vector<double>& values,
                                double threshold);
void normalize_in_place(double* values, std::size_t size);

class OnlineStats {
public:
    void add(double value);
    void extend(const std::vector<double>& values);
    void reset() noexcept;

    [[nodiscard]] std::size_t count() const noexcept;
    [[nodiscard]] std::optional<double> minimum() const noexcept;
    [[nodiscard]] std::optional<double> maximum() const noexcept;
    [[nodiscard]] std::optional<double> mean() const noexcept;

private:
    std::size_t count_{0};
    double minimum_{0.0};
    double maximum_{0.0};
    double mean_{0.0};
};

}  // namespace faststats

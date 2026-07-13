#include "faststats_cpp/core.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace faststats {
namespace {

void validate_size(const std::size_t size) {
    if (size == 0 || size > max_samples) {
        throw std::invalid_argument("sample count must be between 1 and 1000000");
    }
}

void validate_value(const double value) {
    if (!std::isfinite(value) || std::abs(value) > max_magnitude) {
        throw std::invalid_argument("sample must be finite and abs(sample) <= 1e150");
    }
}

void validate_threshold(const double threshold) {
    if (!std::isfinite(threshold) || threshold < 0.0 ||
        threshold > max_magnitude) {
        throw std::invalid_argument("threshold must be finite and in [0, 1e150]");
    }
}

bool close_to_threshold(const double delta, const double threshold) {
    const double scale =
        std::max(std::abs(delta), std::abs(threshold));
    return std::abs(delta - threshold) <=
           std::max(comparison_tolerance,
                    comparison_tolerance * scale);
}

}  // namespace

Summary summarize(const double* values, const std::size_t size,
                  const double threshold) {
    validate_size(size);
    validate_threshold(threshold);
    if (values == nullptr) {
        throw std::invalid_argument("sample pointer cannot be null");
    }

    double minimum = std::numeric_limits<double>::infinity();
    double maximum = -std::numeric_limits<double>::infinity();
    double mean = 0.0;
    for (std::size_t index = 0; index < size; ++index) {
        const double value = values[index];
        validate_value(value);
        minimum = std::min(minimum, value);
        maximum = std::max(maximum, value);
        const double count = static_cast<double>(index + 1);
        mean += (value - mean) / count;
    }

    std::size_t anomaly_count = 0;
    for (std::size_t index = 0; index < size; ++index) {
        const double delta = std::abs(values[index] - mean);
        if (delta > threshold && !close_to_threshold(delta, threshold)) {
            ++anomaly_count;
        }
    }

    return Summary{size,
                   minimum,
                   maximum,
                   mean,
                   anomaly_count,
                   static_cast<double>(anomaly_count) /
                       static_cast<double>(size)};
}

Summary summarize(const std::vector<double>& values, const double threshold) {
    return summarize(values.data(), values.size(), threshold);
}

void normalize_in_place(double* values, const std::size_t size) {
    validate_size(size);
    if (values == nullptr) {
        throw std::invalid_argument("sample pointer cannot be null");
    }

    double minimum = std::numeric_limits<double>::infinity();
    double maximum = -std::numeric_limits<double>::infinity();
    for (std::size_t index = 0; index < size; ++index) {
        validate_value(values[index]);
        minimum = std::min(minimum, values[index]);
        maximum = std::max(maximum, values[index]);
    }

    if (minimum == maximum) {
        std::fill(values, values + size, 0.0);
        return;
    }
    const double range = maximum - minimum;
    for (std::size_t index = 0; index < size; ++index) {
        values[index] = (values[index] - minimum) / range;
    }
}

void OnlineStats::add(const double value) {
    validate_value(value);
    if (count_ >= max_samples) {
        throw std::invalid_argument("online sample count cannot exceed 1000000");
    }
    if (count_ == 0) {
        minimum_ = value;
        maximum_ = value;
        mean_ = value;
        count_ = 1;
        return;
    }
    minimum_ = std::min(minimum_, value);
    maximum_ = std::max(maximum_, value);
    ++count_;
    mean_ += (value - mean_) / static_cast<double>(count_);
}

void OnlineStats::extend(const std::vector<double>& values) {
    if (values.size() > max_samples - count_) {
        throw std::invalid_argument("online sample count cannot exceed 1000000");
    }
    for (const double value : values) {
        validate_value(value);
    }
    for (const double value : values) {
        add(value);
    }
}

void OnlineStats::reset() noexcept {
    count_ = 0;
    minimum_ = 0.0;
    maximum_ = 0.0;
    mean_ = 0.0;
}

std::size_t OnlineStats::count() const noexcept { return count_; }

std::optional<double> OnlineStats::minimum() const noexcept {
    return count_ == 0 ? std::nullopt : std::optional<double>(minimum_);
}

std::optional<double> OnlineStats::maximum() const noexcept {
    return count_ == 0 ? std::nullopt : std::optional<double>(maximum_);
}

std::optional<double> OnlineStats::mean() const noexcept {
    return count_ == 0 ? std::nullopt : std::optional<double>(mean_);
}

}  // namespace faststats

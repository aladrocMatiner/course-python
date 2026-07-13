#include "score.hpp"

#include <stdexcept>
#include <utility>

namespace course {

ScoreReport::ScoreReport(std::vector<double> values)
    : values_(std::move(values)), label_("practice batch") {
    if (values_.empty()) {
        throw std::invalid_argument("a score batch cannot be empty");
    }
}

double ScoreReport::mean() const {
    double current = 0.0;
    std::size_t count = 0;
    for (const double value : values_) {
        ++count;
        current += (value - current) / static_cast<double>(count);
    }
    return current;
}

const std::string& ScoreReport::label() const noexcept { return label_; }

}  // namespace course

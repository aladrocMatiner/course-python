#include "score.hpp"

#include <cmath>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {

int failures = 0;

void check(const bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        ++failures;
    }
}

}  // namespace

int main() {
    const course::ScoreReport report(std::vector<double>{6.0, 8.0, 10.0});
    check(std::abs(report.mean() - 8.0) < 1e-12, "mean is 8");
    check(report.label() == "practice batch", "label is retained by RAII object");

    bool rejected_empty = false;
    try {
        const course::ScoreReport invalid(std::vector<double>{});
        static_cast<void>(invalid);
    } catch (const std::invalid_argument&) {
        rejected_empty = true;
    }
    check(rejected_empty, "empty input is a recoverable exception");
    return failures == 0 ? 0 : 1;
}

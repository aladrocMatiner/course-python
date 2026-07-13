#pragma once

#include <string>
#include <vector>

namespace course {

class ScoreReport {
public:
    explicit ScoreReport(std::vector<double> values);

    [[nodiscard]] double mean() const;
    [[nodiscard]] const std::string& label() const noexcept;

private:
    std::vector<double> values_;
    std::string label_;
};

}  // namespace course

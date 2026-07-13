#include "score.hpp"

#include <exception>
#include <iostream>
#include <vector>

int main() {
    try {
        const course::ScoreReport report(std::vector<double>{6.0, 8.0, 10.0});
        std::cout << report.label() << ": mean=" << report.mean() << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}

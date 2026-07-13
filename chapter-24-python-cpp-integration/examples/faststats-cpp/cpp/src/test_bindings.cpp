#include "faststats_cpp/core.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <mutex>
#include <stdexcept>
#include <vector>

#ifndef FASTSTATS_TEST_HOOKS
#error "test_bindings.cpp must only compile with FASTSTATS_TEST_HOOKS"
#endif

namespace py = pybind11;

namespace {

class TwoPartyRendezvous {
public:
    void meet(const std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        const std::size_t observed_generation = generation_;
        ++arrivals_;
        if (arrivals_ == 2) {
            arrivals_ = 0;
            ++generation_;
            condition_.notify_all();
            return;
        }
        if (!condition_.wait_for(lock, timeout, [this, observed_generation] {
                return generation_ != observed_generation;
            })) {
            arrivals_ = 0;
            ++generation_;
            condition_.notify_all();
            throw std::runtime_error(
                "timed out waiting for a second native call");
        }
    }

private:
    std::mutex mutex_;
    std::condition_variable condition_;
    std::size_t arrivals_{0};
    std::size_t generation_{0};
};

TwoPartyRendezvous rendezvous;

faststats::Summary summarize_after_rendezvous(
    const std::vector<double>& values, const double threshold,
    const int timeout_milliseconds) {
    if (timeout_milliseconds < 1 || timeout_milliseconds > 10'000) {
        throw std::invalid_argument("timeout must be between 1 and 10000 ms");
    }
    py::gil_scoped_release release;
    rendezvous.meet(std::chrono::milliseconds(timeout_milliseconds));
    return faststats::summarize(values, threshold);
}

}  // namespace

PYBIND11_MODULE(_faststats_test, module) {
    module.doc() = "Test-only rendezvous; never installed in a wheel";
    module.def("summarize_after_rendezvous", &summarize_after_rendezvous,
               py::arg("values"), py::arg("threshold"),
               py::arg("timeout_milliseconds") = 2000);
}

#include "faststats_cpp/core.hpp"

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <atomic>
#include <cmath>
#include <cstdint>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace {

constexpr long long max_exact_integer = 9'007'199'254'740'992LL;

double convert_value(const py::handle value) {
    if (PyBool_Check(value.ptr()) != 0) {
        throw py::type_error("bool is not an accepted numeric sample");
    }
    if (PyLong_CheckExact(value.ptr()) != 0) {
        int overflow = 0;
        const long long converted = PyLong_AsLongLongAndOverflow(value.ptr(), &overflow);
        if (overflow != 0 || converted > max_exact_integer ||
            converted < -max_exact_integer) {
            PyErr_Clear();
            throw py::value_error("integer samples require abs(value) <= 2**53");
        }
        return static_cast<double>(converted);
    }
    if (PyFloat_CheckExact(value.ptr()) != 0) {
        return PyFloat_AS_DOUBLE(value.ptr());
    }
    throw py::type_error(
        "samples must be built-in int or float values (not bool or subclasses)");
}

double convert_threshold(const py::handle value) {
    if (PyBool_Check(value.ptr()) != 0) {
        throw py::type_error("threshold must be a built-in int or float");
    }
    double threshold = 0.0;
    if (PyLong_CheckExact(value.ptr()) != 0) {
        threshold = PyLong_AsDouble(value.ptr());
        if (PyErr_Occurred() != nullptr) {
            PyErr_Clear();
            throw py::value_error("threshold is outside the supported range");
        }
    } else if (PyFloat_CheckExact(value.ptr()) != 0) {
        threshold = PyFloat_AS_DOUBLE(value.ptr());
    } else {
        throw py::type_error("threshold must be a built-in int or float");
    }
    if (!std::isfinite(threshold) || threshold < 0.0 ||
        threshold > faststats::max_magnitude) {
        throw py::value_error("threshold must be finite and in [0, 1e150]");
    }
    return threshold;
}

std::vector<double> copy_iterable(const py::handle samples,
                                  const bool allow_empty = false) {
    std::vector<double> copied;
    for (const py::handle item : py::iter(samples)) {
        if (copied.size() == faststats::max_samples) {
            throw py::value_error("sample count must not exceed 1000000");
        }
        const double value = convert_value(item);
        if (!std::isfinite(value) || std::abs(value) > faststats::max_magnitude) {
            throw py::value_error("samples must be finite and abs(value) <= 1e150");
        }
        copied.push_back(value);
    }
    if (!allow_empty && copied.empty()) {
        throw py::value_error("sample count must be between 1 and 1000000");
    }
    return copied;
}

struct CheckedBuffer {
    py::buffer_info info;
    double* values;
    std::size_t size;
};

CheckedBuffer check_buffer(py::buffer buffer, const bool require_writable) {
    py::buffer_info info = buffer.request();
    if (info.ndim != 1) {
        throw py::value_error("buffer must be one-dimensional");
    }
    if (info.itemsize != static_cast<py::ssize_t>(sizeof(double)) ||
        info.format != py::format_descriptor<double>::format()) {
        throw py::value_error("buffer format must be a native double");
    }
    if (info.shape[0] < 1 ||
        static_cast<std::size_t>(info.shape[0]) > faststats::max_samples) {
        throw py::value_error("buffer length must be between 1 and 1000000");
    }
    if (info.strides[0] != static_cast<py::ssize_t>(sizeof(double))) {
        throw py::value_error("buffer must be contiguous with a positive stride");
    }
    if (require_writable && info.readonly) {
        throw py::value_error("buffer must be writable");
    }
    const auto address = reinterpret_cast<std::uintptr_t>(info.ptr);
    if (address % alignof(double) != 0) {
        throw py::value_error("buffer storage is not aligned for double");
    }
    auto* const values = static_cast<double*>(info.ptr);
    const auto size = static_cast<std::size_t>(info.shape[0]);
    return CheckedBuffer{std::move(info), values, size};
}

enum class ProcessingMode { copied, borrowed };

class Metadata {
public:
    explicit Metadata(std::string label) : label_(std::move(label)) {}
    [[nodiscard]] const std::string& label() const noexcept { return label_; }

private:
    std::string label_;
};

class Dataset {
public:
    explicit Dataset(std::string label) : metadata_(std::move(label)) {}
    [[nodiscard]] const Metadata& metadata() const noexcept { return metadata_; }

private:
    Metadata metadata_;
};

class BorrowingView {
public:
    explicit BorrowingView(const Dataset& dataset) : metadata_(&dataset.metadata()) {}
    [[nodiscard]] const std::string& label() const noexcept {
        return metadata_->label();
    }

private:
    const Metadata* metadata_;
};

class TrackedResource {
public:
    explicit TrackedResource(std::string name) : name_(std::move(name)) {
        ++live_count_;
    }
    TrackedResource(const TrackedResource&) = delete;
    TrackedResource& operator=(const TrackedResource&) = delete;
    ~TrackedResource() noexcept { --live_count_; }

    [[nodiscard]] const std::string& name() const noexcept { return name_; }
    [[nodiscard]] static int live_count() noexcept { return live_count_.load(); }

private:
    std::string name_;
    static std::atomic<int> live_count_;
};

std::atomic<int> TrackedResource::live_count_{0};

std::unique_ptr<TrackedResource> make_resource(const std::string& name) {
    return std::make_unique<TrackedResource>(name);
}

void consume_resource(std::unique_ptr<TrackedResource> resource) {
    if (!resource) {
        throw std::invalid_argument("resource cannot be null");
    }
}

class ProgressObserver {
public:
    virtual ~ProgressObserver() = default;
    virtual void on_progress(std::size_t completed) = 0;
};

class PyProgressObserver : public ProgressObserver,
                           public py::trampoline_self_life_support {
public:
    using ProgressObserver::ProgressObserver;
    void on_progress(const std::size_t completed) override {
        PYBIND11_OVERRIDE_PURE(void, ProgressObserver, on_progress, completed);
    }
};

class ObserverRunner {
public:
    explicit ObserverRunner(std::shared_ptr<ProgressObserver> observer)
        : observer_(std::move(observer)) {
        if (!observer_) {
            throw std::invalid_argument("observer cannot be null");
        }
    }
    void run(const std::size_t completed) { observer_->on_progress(completed); }

private:
    std::shared_ptr<ProgressObserver> observer_;
};

std::string summary_repr(const faststats::Summary& summary) {
    std::ostringstream output;
    output << "Summary(count=" << summary.count << ", minimum="
           << summary.minimum << ", maximum=" << summary.maximum
           << ", mean=" << summary.mean << ", anomaly_count="
           << summary.anomaly_count << ", anomaly_ratio="
           << summary.anomaly_ratio << ')';
    return output.str();
}

}  // namespace

PYBIND11_MODULE(_native, module) {
    module.doc() = "Private native implementation for faststats_cpp";

    py::register_exception<faststats::DomainError>(module, "FaststatsError",
                                                    PyExc_RuntimeError);

    py::class_<faststats::Summary>(module, "Summary")
        .def_property_readonly("count", [](const faststats::Summary& value) {
            return value.count;
        })
        .def_property_readonly("minimum", [](const faststats::Summary& value) {
            return value.minimum;
        })
        .def_property_readonly("maximum", [](const faststats::Summary& value) {
            return value.maximum;
        })
        .def_property_readonly("mean", [](const faststats::Summary& value) {
            return value.mean;
        })
        .def_property_readonly("anomaly_count",
                               [](const faststats::Summary& value) {
                                   return value.anomaly_count;
                               })
        .def_property_readonly("anomaly_ratio",
                               [](const faststats::Summary& value) {
                                   return value.anomaly_ratio;
                               })
        .def("__repr__", &summary_repr);

    py::enum_<ProcessingMode>(module, "ProcessingMode")
        .value("COPIED", ProcessingMode::copied)
        .value("BORROWED", ProcessingMode::borrowed)
        .export_values();

    module.def(
        "summarize",
        [](const py::iterable samples, const py::object threshold) {
            const auto copied = copy_iterable(samples);
            return faststats::summarize(copied, convert_threshold(threshold));
        },
        py::arg("samples"), py::kw_only(), py::arg("threshold") = 0.0,
        "Copy and summarize an iterable of exact built-in int/float values.");

    module.def(
        "summarize_many",
        [](const py::iterable samples, const py::object threshold) {
            const auto copied = copy_iterable(samples);
            const double checked_threshold = convert_threshold(threshold);
            py::gil_scoped_release release;
            return faststats::summarize(copied, checked_threshold);
        },
        py::arg("samples"), py::kw_only(), py::arg("threshold") = 0.0,
        "Summarize owned C++ storage while the GIL is released.");

    module.def(
        "summarize_buffer",
        [](py::buffer buffer, const py::object threshold) {
            const auto checked = check_buffer(std::move(buffer), false);
            return faststats::summarize(checked.values, checked.size,
                                        convert_threshold(threshold));
        },
        py::arg("buffer"), py::kw_only(), py::arg("threshold") = 0.0,
        "Read a call-scoped contiguous double buffer while holding the GIL.");

    module.def(
        "normalize_in_place",
        [](py::buffer buffer) {
            const auto checked = check_buffer(std::move(buffer), true);
            faststats::normalize_in_place(checked.values, checked.size);
        },
        py::arg("buffer"),
        "Normalize a writable contiguous double buffer transactionally.");

    module.def(
        "summarize_with_progress",
        [](const py::iterable samples, const py::object threshold,
           const py::function& callback) {
            const auto copied = copy_iterable(samples);
            const auto result =
                faststats::summarize(copied, convert_threshold(threshold));
            callback(result.count, result.mean);
            return result;
        },
        py::arg("samples"), py::kw_only(), py::arg("threshold") = 0.0,
        py::arg("callback"),
        "Summarize and invoke a Python callback after native work completes.");

    py::class_<faststats::OnlineStats>(module, "OnlineStats")
        .def(py::init<>())
        .def("add", [](faststats::OnlineStats& self, const py::object value) {
            const double checked = convert_value(value);
            if (!std::isfinite(checked) ||
                std::abs(checked) > faststats::max_magnitude) {
                throw py::value_error(
                    "sample must be finite and abs(value) <= 1e150");
            }
            self.add(checked);
        })
        .def("extend", [](faststats::OnlineStats& self,
                          const py::iterable values) {
            self.extend(copy_iterable(values, true));
        })
        .def("reset", &faststats::OnlineStats::reset)
        .def_property_readonly("count", &faststats::OnlineStats::count)
        .def_property_readonly("minimum", &faststats::OnlineStats::minimum)
        .def_property_readonly("maximum", &faststats::OnlineStats::maximum)
        .def_property_readonly("mean", &faststats::OnlineStats::mean)
        .def("__repr__", [](const faststats::OnlineStats& self) {
            std::ostringstream output;
            output << "OnlineStats(count=" << self.count() << ", mean=";
            if (self.mean()) {
                output << *self.mean();
            } else {
                output << "None";
            }
            output << ')';
            return output.str();
        });

    py::class_<Metadata>(module, "Metadata")
        .def_property_readonly("label", &Metadata::label);
    py::class_<Dataset>(module, "Dataset")
        .def(py::init<std::string>(), py::arg("label"))
        .def_property_readonly("metadata", &Dataset::metadata,
                               py::return_value_policy::reference_internal);
    py::class_<BorrowingView>(module, "BorrowingView")
        .def(py::init<const Dataset&>(), py::arg("dataset"),
             py::keep_alive<1, 2>())
        .def_property_readonly("label", &BorrowingView::label);
    py::class_<TrackedResource, py::smart_holder>(module, "TrackedResource")
        .def_property_readonly("name", &TrackedResource::name)
        .def_static("live_count", &TrackedResource::live_count);
    module.def("make_resource", &make_resource, py::arg("name"),
               "Return one uniquely owned RAII resource via smart_holder.");
    module.def("consume_resource", &consume_resource, py::arg("resource"),
               "Transfer unique ownership to C++ and release it deterministically.");

    py::class_<ProgressObserver, PyProgressObserver, py::smart_holder>(
        module, "ProgressObserver")
        .def(py::init<>())
        .def("on_progress", &ProgressObserver::on_progress);
    py::class_<ObserverRunner>(module, "ObserverRunner")
        .def(py::init<std::shared_ptr<ProgressObserver>>(), py::arg("observer"),
             py::keep_alive<1, 2>())
        .def("run", &ObserverRunner::run, py::arg("completed"));

    module.def("_raise_domain_error_for_test", [] {
        throw faststats::DomainError("demonstration domain failure");
    });
}

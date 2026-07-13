#include <pybind11/pybind11.h>

namespace py = pybind11;

int add(const int left, const int right) { return left + right; }

PYBIND11_MODULE(hello_cpp, module) {
    module.doc() = "A deliberately small C++17 extension";
    module.def("add", &add, py::arg("left"), py::arg("right"),
               "Add two integers in C++.");
}

#include <pybind11/embed.h>

#include <filesystem>
#include <iostream>
#include <string>

namespace py = pybind11;

namespace {

int run_strategy(const std::filesystem::path& requested_directory) {
    std::error_code path_error;
    const auto strategy_directory =
        std::filesystem::canonical(requested_directory, path_error);
    if (path_error || !std::filesystem::is_directory(strategy_directory)) {
        std::cerr << "strategy directory is missing or not a directory\n";
        return 2;
    }

    py::scoped_interpreter interpreter;
    try {
        py::module_ sys = py::module_::import("sys");
        sys.attr("dont_write_bytecode") = py::bool_(true);
        const py::list original_path = sys.attr("path");
        py::list controlled_path;
        controlled_path.append(py::str(strategy_directory.string()));
        // Keep only absolute interpreter/library paths after the one trusted
        // strategy directory. Empty and relative entries can name the cwd and
        // are deliberately removed, so a decoy beside the executable cannot
        // shadow the fixed strategy module.
        for (const py::handle item : original_path) {
            const auto entry = std::filesystem::path(py::cast<std::string>(item));
            if (!entry.empty() && entry.is_absolute() &&
                entry != strategy_directory) {
                controlled_path.append(py::str(entry.string()));
            }
        }
        sys.attr("path") = controlled_path;

        py::module_ strategy = py::module_::import("trusted_strategy");
        py::object evaluate = strategy.attr("evaluate");
        if (!PyCallable_Check(evaluate.ptr())) {
            std::cerr << "trusted_strategy.evaluate is not callable\n";
            return 3;
        }
        py::list values;
        values.append(1.0);
        values.append(2.0);
        values.append(3.0);
        py::object result = evaluate(values);
        if (PyFloat_CheckExact(result.ptr()) == 0) {
            std::cerr << "strategy result must be a built-in float\n";
            return 4;
        }
        std::cout << "score=" << result.cast<double>() << '\n';
        return 0;
    } catch (const py::error_already_set& error) {
        std::cerr << "Python strategy failed: " << error.what() << '\n';
        return 3;
    } catch (const std::exception& error) {
        std::cerr << "embedded host failed: " << error.what() << '\n';
        return 3;
    }
}

}  // namespace

int main(const int argc, char** argv) {
    if (argc != 3 || std::string(argv[1]) != "--strategy-dir") {
        std::cerr << "usage: embed_strategy --strategy-dir TRUSTED_LOCAL_DIRECTORY\n";
        return 2;
    }
    try {
        return run_strategy(argv[2]);
    } catch (const std::exception& error) {
        std::cerr << "host setup failed: " << error.what() << '\n';
        return 3;
    }
}

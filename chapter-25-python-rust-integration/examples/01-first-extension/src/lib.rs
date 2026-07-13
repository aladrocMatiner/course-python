use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn double(value: i64) -> PyResult<i64> {
    value
        .checked_mul(2)
        .ok_or_else(|| PyValueError::new_err("doubling would overflow a signed 64-bit integer"))
}

#[pyfunction]
fn greeting(name: &str) -> String {
    format!("Hello, {name}, from Rust!")
}

#[pymodule(gil_used = true)]
fn first_pyo3_extension(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(double, module)?)?;
    module.add_function(wrap_pyfunction!(greeting, module)?)?;
    Ok(())
}

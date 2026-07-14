mod domain;

#[cfg(feature = "test-hooks")]
mod test_hooks;

#[cfg(feature = "test-hooks")]
use pyo3::exceptions::PyRuntimeError;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBool, PyFloat, PyInt, PyModule};

use domain::{DomainError, OnlineStatsData, SummaryData};

const MAX_EXACT_INTEGER: i64 = 1_i64 << 53;

fn domain_error(error: DomainError) -> PyErr {
    PyValueError::new_err(error.to_string())
}

#[allow(clippy::cast_precision_loss)] // Values are checked against Python's exact 2**53 bound first.
fn exact_number(value: &Bound<'_, PyAny>, label: &str) -> PyResult<f64> {
    let py = value.py();
    let value_type = value.get_type();
    if value_type.is(py.get_type::<PyBool>()) {
        return Err(PyTypeError::new_err(format!(
            "{label} must be an exact built-in int or float, not bool"
        )));
    }
    if value_type.is(py.get_type::<PyInt>()) {
        let integer = value.extract::<i64>().map_err(|_| {
            PyValueError::new_err(format!("{label} integer magnitude must not exceed 2**53"))
        })?;
        if integer.unsigned_abs() > MAX_EXACT_INTEGER as u64 {
            return Err(PyValueError::new_err(format!(
                "{label} integer magnitude must not exceed 2**53"
            )));
        }
        return Ok(integer as f64);
    }
    if value_type.is(py.get_type::<PyFloat>()) {
        return value.extract::<f64>();
    }
    Err(PyTypeError::new_err(format!(
        "{label} must be an exact built-in int or float"
    )))
}

fn extract_samples(samples: &Bound<'_, PyAny>) -> PyResult<Vec<f64>> {
    let iterator = samples.try_iter().map_err(|_| {
        PyTypeError::new_err("samples must be an iterable of exact built-in int or float values")
    })?;
    let mut values = Vec::new();
    for (index, item) in iterator.enumerate() {
        if index >= domain::MAX_SAMPLES {
            return Err(domain_error(DomainError::TooManySamples));
        }
        values.push(exact_number(&item?, &format!("samples[{index}]"))?);
    }
    domain::validate_values(&values).map_err(domain_error)?;
    Ok(values)
}

#[pyclass(frozen, skip_from_py_object, module = "faststats_rs._native")]
#[derive(Clone)]
struct Summary {
    #[pyo3(get)]
    count: usize,
    #[pyo3(get)]
    minimum: f64,
    #[pyo3(get)]
    maximum: f64,
    #[pyo3(get)]
    mean: f64,
    #[pyo3(get)]
    anomaly_count: usize,
    #[pyo3(get)]
    anomaly_ratio: f64,
}

impl From<SummaryData> for Summary {
    fn from(value: SummaryData) -> Self {
        Self {
            count: value.count,
            minimum: value.minimum,
            maximum: value.maximum,
            mean: value.mean,
            anomaly_count: value.anomaly_count,
            anomaly_ratio: value.anomaly_ratio,
        }
    }
}

#[pymethods]
impl Summary {
    fn __repr__(&self) -> String {
        format!(
            "Summary(count={}, minimum={:?}, maximum={:?}, mean={:?}, anomaly_count={}, anomaly_ratio={:?})",
            self.count,
            self.minimum,
            self.maximum,
            self.mean,
            self.anomaly_count,
            self.anomaly_ratio
        )
    }
}

#[pyfunction]
#[pyo3(signature = (samples, *, threshold))]
fn summarize(
    py: Python<'_>,
    samples: &Bound<'_, PyAny>,
    threshold: &Bound<'_, PyAny>,
) -> PyResult<Summary> {
    let values = extract_samples(samples)?;
    let threshold = exact_number(threshold, "threshold")?;
    domain::validate_threshold(threshold).map_err(domain_error)?;
    let result = py.detach(move || domain::summarize(&values, threshold));
    result.map(Summary::from).map_err(domain_error)
}

#[cfg(feature = "test-hooks")]
#[pyfunction]
#[pyo3(signature = (samples, *, threshold))]
fn summarize_with_rendezvous(
    py: Python<'_>,
    samples: &Bound<'_, PyAny>,
    threshold: &Bound<'_, PyAny>,
) -> PyResult<Summary> {
    let values = extract_samples(samples)?;
    let threshold = exact_number(threshold, "threshold")?;
    domain::validate_threshold(threshold).map_err(domain_error)?;
    py.detach(test_hooks::wait_for_pair)
        .map_err(PyRuntimeError::new_err)?;
    let result = py.detach(move || domain::summarize(&values, threshold));
    result.map(Summary::from).map_err(domain_error)
}

#[pyclass(module = "faststats_rs._native")]
#[derive(Default)]
struct OnlineStats {
    state: OnlineStatsData,
}

#[pymethods]
impl OnlineStats {
    #[new]
    fn new() -> Self {
        Self::default()
    }

    #[getter]
    fn count(&self) -> usize {
        self.state.count()
    }

    #[getter]
    fn minimum(&self) -> Option<f64> {
        self.state.minimum()
    }

    #[getter]
    fn maximum(&self) -> Option<f64> {
        self.state.maximum()
    }

    #[getter]
    fn mean(&self) -> Option<f64> {
        self.state.mean()
    }

    fn add(&mut self, value: &Bound<'_, PyAny>) -> PyResult<()> {
        let value = exact_number(value, "value")?;
        self.state.extend(&[value]).map_err(domain_error)
    }

    fn extend(&mut self, values: &Bound<'_, PyAny>) -> PyResult<()> {
        let values = extract_samples_allow_empty(values)?;
        self.state.extend(&values).map_err(domain_error)
    }

    fn reset(&mut self) {
        self.state.reset();
    }

    fn __repr__(&self) -> String {
        format!(
            "OnlineStats(count={}, minimum={:?}, maximum={:?}, mean={:?})",
            self.count(),
            self.minimum(),
            self.maximum(),
            self.mean()
        )
    }
}

fn extract_samples_allow_empty(samples: &Bound<'_, PyAny>) -> PyResult<Vec<f64>> {
    let iterator = samples.try_iter().map_err(|_| {
        PyTypeError::new_err("values must be an iterable of exact built-in int or float values")
    })?;
    let mut values = Vec::new();
    for (index, item) in iterator.enumerate() {
        if index >= domain::MAX_SAMPLES {
            return Err(domain_error(DomainError::TooManySamples));
        }
        values.push(exact_number(&item?, &format!("values[{index}]"))?);
    }
    if !values.is_empty() {
        domain::validate_values(&values).map_err(domain_error)?;
    }
    Ok(values)
}

#[pyfunction]
#[pyo3(signature = (label, payload, note=None))]
fn describe_payload(label: &str, payload: &[u8], note: Option<&str>) -> (String, usize, bool) {
    (label.to_owned(), payload.len(), note.is_some())
}

#[pymodule(gil_used = true)]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Summary>()?;
    module.add_class::<OnlineStats>()?;
    module.add_function(wrap_pyfunction!(summarize, module)?)?;
    module.add_function(wrap_pyfunction!(describe_payload, module)?)?;
    #[cfg(feature = "test-hooks")]
    module.add_function(wrap_pyfunction!(summarize_with_rendezvous, module)?)?;
    Ok(())
}

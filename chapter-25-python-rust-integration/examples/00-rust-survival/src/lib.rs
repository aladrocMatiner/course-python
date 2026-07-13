//! Small Rust-only examples used before introducing Python bindings.

use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub sensor: String,
    pub value: f64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseReadingError {
    MissingSeparator,
    EmptySensor,
    InvalidNumber,
    NonFiniteNumber,
}

impl fmt::Display for ParseReadingError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let message = match self {
            Self::MissingSeparator => "expected SENSOR:VALUE",
            Self::EmptySensor => "sensor name cannot be empty",
            Self::InvalidNumber => "value is not a number",
            Self::NonFiniteNumber => "value must be finite",
        };
        formatter.write_str(message)
    }
}

#[must_use]
#[allow(clippy::cast_precision_loss)] // This first lesson intentionally uses a small in-memory slice.
pub fn average(values: &[f64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let sum: f64 = values.iter().sum();
    Some(sum / values.len() as f64)
}

/// Parse the bounded teaching format `SENSOR:VALUE`.
///
/// # Errors
///
/// Returns a descriptive variant when the separator, sensor, or finite number
/// contract is not satisfied.
pub fn parse_reading(text: &str) -> Result<Reading, ParseReadingError> {
    let (sensor, raw_value) = text
        .split_once(':')
        .ok_or(ParseReadingError::MissingSeparator)?;
    if sensor.trim().is_empty() {
        return Err(ParseReadingError::EmptySensor);
    }
    let value: f64 = raw_value
        .trim()
        .parse()
        .map_err(|_| ParseReadingError::InvalidNumber)?;
    if !value.is_finite() {
        return Err(ParseReadingError::NonFiniteNumber);
    }
    Ok(Reading {
        sensor: sensor.trim().to_owned(),
        value,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn average_has_a_value_for_non_empty_slice() {
        assert_eq!(average(&[2.0, 4.0, 6.0]), Some(4.0));
    }

    #[test]
    fn average_uses_none_for_empty_slice() {
        assert_eq!(average(&[]), None);
    }

    #[test]
    fn parse_reading_returns_structured_data() {
        assert_eq!(
            parse_reading("lab: 21.5"),
            Ok(Reading {
                sensor: "lab".to_owned(),
                value: 21.5,
            })
        );
    }

    #[test]
    fn parse_reading_returns_a_recoverable_error() {
        assert_eq!(
            parse_reading("lab:not-a-number"),
            Err(ParseReadingError::InvalidNumber)
        );
    }
}

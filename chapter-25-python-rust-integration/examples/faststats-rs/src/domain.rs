//! Python-independent bounded statistics domain.

use std::fmt;

pub const MAX_SAMPLES: usize = 1_000_000;
pub const MAX_ABS_VALUE: f64 = 1.0e150;
const REL_TOL: f64 = 1.0e-12;
const ABS_TOL: f64 = 1.0e-12;

#[derive(Debug, Clone, PartialEq)]
pub struct SummaryData {
    pub count: usize,
    pub minimum: f64,
    pub maximum: f64,
    pub mean: f64,
    pub anomaly_count: usize,
    pub anomaly_ratio: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DomainError {
    Empty,
    TooManySamples,
    NonFiniteValue,
    ValueOutOfRange,
    InvalidThreshold,
}

impl fmt::Display for DomainError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let message = match self {
            Self::Empty => "samples must contain at least one value",
            Self::TooManySamples => "sample count must not exceed 1,000,000",
            Self::NonFiniteValue => "sample values must be finite",
            Self::ValueOutOfRange => "sample values must have absolute value at most 1e150",
            Self::InvalidThreshold => "threshold must be finite and between 0 and 1e150",
        };
        formatter.write_str(message)
    }
}

fn close_to(left: f64, right: f64) -> bool {
    (left - right).abs() <= (REL_TOL * left.abs().max(right.abs())).max(ABS_TOL)
}

pub fn validate_threshold(threshold: f64) -> Result<(), DomainError> {
    if !threshold.is_finite() || !(0.0..=MAX_ABS_VALUE).contains(&threshold) {
        return Err(DomainError::InvalidThreshold);
    }
    Ok(())
}

pub fn validate_values(values: &[f64]) -> Result<(), DomainError> {
    if values.is_empty() {
        return Err(DomainError::Empty);
    }
    if values.len() > MAX_SAMPLES {
        return Err(DomainError::TooManySamples);
    }
    for value in values {
        if !value.is_finite() {
            return Err(DomainError::NonFiniteValue);
        }
        if value.abs() > MAX_ABS_VALUE {
            return Err(DomainError::ValueOutOfRange);
        }
    }
    Ok(())
}

pub fn summarize(values: &[f64], threshold: f64) -> Result<SummaryData, DomainError> {
    validate_values(values)?;
    validate_threshold(threshold)?;

    let mut minimum = values[0];
    let mut maximum = values[0];
    let mut mean = 0.0;
    for (index, value) in values.iter().copied().enumerate() {
        minimum = minimum.min(value);
        maximum = maximum.max(value);
        let count = f64::from(u32::try_from(index + 1).map_err(|_| DomainError::TooManySamples)?);
        mean += (value - mean) / count;
    }

    let anomaly_count = values
        .iter()
        .filter(|value| {
            let delta = (**value - mean).abs();
            delta > threshold && !close_to(delta, threshold)
        })
        .count();

    let anomaly_count_f64 =
        f64::from(u32::try_from(anomaly_count).map_err(|_| DomainError::TooManySamples)?);
    let count_f64 =
        f64::from(u32::try_from(values.len()).map_err(|_| DomainError::TooManySamples)?);
    Ok(SummaryData {
        count: values.len(),
        minimum,
        maximum,
        mean,
        anomaly_count,
        anomaly_ratio: anomaly_count_f64 / count_f64,
    })
}

#[derive(Debug, Clone, Default, PartialEq)]
pub struct OnlineStatsData {
    count: usize,
    minimum: Option<f64>,
    maximum: Option<f64>,
    mean: Option<f64>,
}

impl OnlineStatsData {
    pub fn count(&self) -> usize {
        self.count
    }

    pub fn minimum(&self) -> Option<f64> {
        self.minimum
    }

    pub fn maximum(&self) -> Option<f64> {
        self.maximum
    }

    pub fn mean(&self) -> Option<f64> {
        self.mean
    }

    pub fn extend(&mut self, values: &[f64]) -> Result<(), DomainError> {
        if self.count.saturating_add(values.len()) > MAX_SAMPLES {
            return Err(DomainError::TooManySamples);
        }
        if !values.is_empty() {
            validate_values(values)?;
        }
        let mut next = self.clone();
        for value in values.iter().copied() {
            next.count += 1;
            next.minimum = Some(next.minimum.map_or(value, |old| old.min(value)));
            next.maximum = Some(next.maximum.map_or(value, |old| old.max(value)));
            let old_mean = next.mean.unwrap_or(0.0);
            let count =
                f64::from(u32::try_from(next.count).map_err(|_| DomainError::TooManySamples)?);
            next.mean = Some(old_mean + (value - old_mean) / count);
        }
        *self = next;
        Ok(())
    }

    pub fn reset(&mut self) {
        *self = Self::default();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn summary_uses_final_mean_for_anomalies() {
        let summary = summarize(&[-3.0, -3.0, -1.0], 0.5).unwrap();
        assert_eq!(summary.count, 3);
        assert_eq!(summary.anomaly_count, 3);
        assert!((summary.mean + 7.0 / 3.0).abs() < 1.0e-12);
    }

    #[test]
    fn threshold_tolerance_band_is_not_anomalous() {
        let summary = summarize(&[0.0, 2.0], 1.0 + 5.0e-13).unwrap();
        assert_eq!(summary.anomaly_count, 0);
    }

    #[test]
    fn invalid_domain_inputs_return_specific_errors() {
        assert_eq!(summarize(&[], 0.0), Err(DomainError::Empty));
        assert_eq!(summarize(&[1.0], -1.0), Err(DomainError::InvalidThreshold));
        assert_eq!(
            summarize(&[f64::INFINITY], 0.0),
            Err(DomainError::NonFiniteValue)
        );
        assert_eq!(
            summarize(&[MAX_ABS_VALUE * 2.0], 0.0),
            Err(DomainError::ValueOutOfRange)
        );
    }

    #[test]
    fn invalid_extension_is_transactional() {
        let mut stats = OnlineStatsData::default();
        stats.extend(&[1.0, 2.0]).unwrap();
        let previous = stats.clone();
        assert_eq!(stats.extend(&[f64::NAN]), Err(DomainError::NonFiniteValue));
        assert_eq!(stats, previous);
    }

    #[test]
    fn reset_restores_empty_state() {
        let mut stats = OnlineStatsData::default();
        stats.extend(&[2.0]).unwrap();
        stats.reset();
        assert_eq!(stats, OnlineStatsData::default());
    }
}

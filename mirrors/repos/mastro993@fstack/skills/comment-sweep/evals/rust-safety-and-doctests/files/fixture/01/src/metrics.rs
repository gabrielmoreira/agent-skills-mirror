//! Samples and summaries.

/// One measurement of a named metric.
#[derive(Debug, Clone, PartialEq)]
pub struct Sample {
    /// Metric name, such as `http.requests`.
    pub name: String,
    /// Measured value.
    pub value: f64,
    /// Milliseconds since the Unix epoch.
    pub timestamp_ms: u64,
}

impl Sample {
    /// Creates a sample of `name` with `value`, taken at `timestamp_ms`.
    pub fn new(name: impl Into<String>, value: f64, timestamp_ms: u64) -> Self {
        Self {
            name: name.into(),
            value,
            timestamp_ms,
        }
    }
}

/// Count, sum, and range of a set of samples.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Summary {
    /// Number of samples.
    pub count: usize,
    /// Sum of their values.
    pub sum: f64,
    /// Smallest value.
    pub min: f64,
    /// Largest value.
    pub max: f64,
}

/// Summarizes `samples`, or returns `None` when there are none.
///
/// ```rust
/// use tally::{summarize, Sample};
///
/// let s = summarize(&[Sample::new("x", 1.0, 0), Sample::new("x", 3.0, 1)]).unwrap();
/// assert_eq!((s.count, s.sum, s.min, s.max), (2, 4.0, 1.0, 3.0));
/// ```
#[must_use]
pub fn summarize(samples: &[Sample]) -> Option<Summary> {
    let (first, rest) = samples.split_first()?;
    let mut summary = Summary {
        count: 1,
        sum: first.value,
        min: first.value,
        max: first.value,
    };
    // loop over every sample and update the running totals
    for sample in rest {
        summary.count += 1;
        summary.sum += sample.value;
        summary.min = summary.min.min(sample.value);
        summary.max = summary.max.max(sample.value);
    }
    Some(summary)
}

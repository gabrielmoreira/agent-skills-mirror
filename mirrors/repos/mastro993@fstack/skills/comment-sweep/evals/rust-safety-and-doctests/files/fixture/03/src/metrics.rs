//! Samples, summaries, and the recorder that hands samples to the ring buffer.

use crate::ring::Producer;

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

/// Pushes samples into a ring buffer, counting the ones dropped because it was full.
///
/// ```rust
/// use tally::{ring, Recorder, Sample};
///
/// let (tx, mut rx) = ring::channel(1);
/// let mut recorder = Recorder::new(tx);
/// recorder.record(Sample::new("x", 1.0, 0));
/// recorder.record(Sample::new("x", 2.0, 1));
/// assert_eq!(recorder.dropped(), 1);
/// assert_eq!(rx.pop().map(|s| s.value), Some(1.0));
/// ```
pub struct Recorder {
    tx: Producer<Sample>,
    dropped: u64,
}

impl Recorder {
    /// Creates a recorder that feeds `tx`.
    #[must_use]
    pub fn new(tx: Producer<Sample>) -> Self {
        Self { tx, dropped: 0 }
    }

    /// Records `sample`, or counts it as dropped when the buffer is full.
    pub fn record(&mut self, sample: Sample) {
        // if the push fails, bump the dropped counter
        if self.tx.push(sample).is_err() {
            self.dropped += 1;
        }
    }

    /// Number of samples dropped so far because the buffer was full.
    #[must_use]
    pub fn dropped(&self) -> u64 {
        self.dropped
    }
}

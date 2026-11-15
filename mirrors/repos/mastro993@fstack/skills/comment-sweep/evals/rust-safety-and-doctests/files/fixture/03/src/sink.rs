//! Writes samples drained from a ring buffer as line protocol, one sample per line.

use std::io::{self, Write};
use std::time::Duration;

use crate::ring::Consumer;
use crate::Sample;

/// Help text for the sink's output format.
pub const FORMAT_HELP: &str = r#"format: "name value timestamp_ms", see http://example.com/line-protocol // one sample per line"#;

/// Where spooled line-protocol files are written; shell tools expand the pattern.
pub const SPOOL_GLOB: &str = "/var/spool/tally/*.lp";

/// Drains a [`Consumer`] into a writer.
pub struct Sink<W> {
    rx: Consumer<Sample>,
    out: W,
    written: u64,
}

impl<W: Write> Sink<W> {
    /// Creates a sink that drains `rx` into `out`.
    pub fn new(rx: Consumer<Sample>, out: W) -> Self {
        Self { rx, out, written: 0 }
    }

    /// Pops every waiting sample, writes it as `name value timestamp_ms`, then flushes `out`.
    /// Returns how many samples were written.
    ///
    /// ```rust
    /// use tally::{ring, Sample, Sink};
    ///
    /// let (mut tx, rx) = ring::channel(4);
    /// tx.push(Sample::new("cpu", 0.5, 1_700_000_000_000)).unwrap();
    /// let mut sink = Sink::new(rx, Vec::new());
    /// assert_eq!(sink.flush().unwrap(), 1);
    /// assert_eq!(sink.into_inner(), b"cpu 0.5 1700000000000\n");
    /// ```
    ///
    /// # Errors
    ///
    /// Returns the first I/O error from `out`. The sample being written when it failed is lost.
    pub fn flush(&mut self) -> io::Result<usize> {
        let mut count = 0;
        // drain the ring buffer
        while let Some(sample) = self.rx.pop() {
            writeln!(self.out, "{} {} {}", sample.name, sample.value, sample.timestamp_ms)?;
            count += 1;
            self.written += 1;
        }
        self.out.flush()?;
        Ok(count)
    }

    /// Samples written per second over `elapsed`.
    #[allow(clippy::cast_precision_loss)]
    pub fn rate(&self, elapsed: Duration) -> f64 {
        self.written as f64 / elapsed.as_secs_f64()
    }

    /// Consumes the sink and returns its writer.
    pub fn into_inner(self) -> W {
        self.out
    }
}

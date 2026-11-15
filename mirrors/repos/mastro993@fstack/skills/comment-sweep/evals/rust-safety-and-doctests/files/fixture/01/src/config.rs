//! Settings loaded from a `key = value` file.

use std::time::Duration;

use crate::Error;

/// Runtime settings.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Config {
    /// How many samples can wait between the recorder and the writer.
    pub buffer_capacity: usize,
    /// How often the writer flushes.
    pub flush_interval: Duration,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            buffer_capacity: 1024,
            flush_interval: Duration::from_secs(10),
        }
    }
}

impl Config {
    /// Parses settings from `text`, starting from the defaults.
    ///
    /// Blank lines and lines starting with `#` are ignored.
    ///
    /// # Errors
    ///
    /// Returns [`Error::Syntax`] for a line without `=`, [`Error::UnknownKey`] for an
    /// unrecognized key, and [`Error::InvalidValue`] for a value that doesn't parse.
    ///
    /// # Examples
    ///
    /// ```rust
    /// let config = tally::Config::parse("buffer_capacity = 64\nflush_interval_ms = 500").unwrap();
    /// assert_eq!(config.buffer_capacity, 64);
    /// ```
    pub fn parse(text: &str) -> Result<Self, Error> {
        let mut config = Self::default();
        for (index, raw) in text.lines().enumerate() {
            let line = raw.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            let (key, value) = line.split_once('=').ok_or(Error::Syntax { line: index + 1 })?;
            let (key, value) = (key.trim(), value.trim());
            let invalid = || Error::InvalidValue {
                key: key.to_owned(),
                value: value.to_owned(),
            };
            match key {
                "buffer_capacity" => config.buffer_capacity = value.parse().map_err(|_| invalid())?,
                "flush_interval_ms" => {
                    let ms = value.parse().map_err(|_| invalid())?;
                    config.flush_interval = Duration::from_millis(ms);
                }
                _ => return Err(Error::UnknownKey(key.to_owned())),
            }
        }
        Ok(config)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_unknown_keys() {
        assert_eq!(
            Config::parse("colour = blue"),
            Err(Error::UnknownKey("colour".to_owned()))
        );
    }

    #[test]
    fn reports_the_line_of_a_syntax_error() {
        assert_eq!(
            Config::parse("# comment\n\nbuffer_capacity"),
            Err(Error::Syntax { line: 3 })
        );
    }
}

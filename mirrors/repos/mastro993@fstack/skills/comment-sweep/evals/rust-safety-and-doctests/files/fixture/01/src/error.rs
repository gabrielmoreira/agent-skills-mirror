//! Errors returned by this crate.

use std::fmt;

/// Everything that can go wrong while loading a [`Config`](crate::Config).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// A line was not of the form `key = value`.
    Syntax {
        /// 1-based line number.
        line: usize,
    },
    /// The key is not one this crate understands.
    UnknownKey(String),
    /// The value could not be parsed for its key.
    InvalidValue {
        /// The key whose value was rejected.
        key: String,
        /// The rejected value.
        value: String,
    },
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Syntax { line } => write!(f, "line {line}: expected `key = value`"),
            Self::UnknownKey(key) => write!(f, "unknown key `{key}`"),
            Self::InvalidValue { key, value } => write!(f, "invalid value `{value}` for `{key}`"),
        }
    }
}

impl std::error::Error for Error {}

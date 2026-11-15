//! Small in-process metrics collection.
//!
//! Build [`Sample`]s, summarize them with [`summarize`], and load settings with [`Config`].

#![deny(missing_docs)]
#![deny(clippy::undocumented_unsafe_blocks)]
#![warn(clippy::pedantic)]

pub mod config;
pub mod error;
pub mod metrics;

pub use config::Config;
pub use error::Error;
pub use metrics::{summarize, Sample, Summary};

//! Small in-process metrics collection.
//!
//! Build [`Sample`]s, summarize them with [`summarize`], and load settings with [`Config`].
//! A [`Recorder`] hands samples through a lock-free [`ring`] buffer to a [`Sink`] on
//! another thread.

#![deny(missing_docs)]
#![deny(clippy::undocumented_unsafe_blocks)]
#![warn(clippy::pedantic)]

pub mod config;
pub mod error;
pub mod metrics;
pub mod ring;
pub mod sink;

pub use config::Config;
pub use error::Error;
pub use metrics::{summarize, Recorder, Sample, Summary};
pub use sink::Sink;

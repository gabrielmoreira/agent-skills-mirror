use std::time::{Duration, Instant};

/// A login session that expires after a period without activity.
pub struct Session {
    last_seen: Instant,
    idle_timeout: Duration,
}

impl Session {
    pub fn new(idle_timeout: Duration) -> Self {
        Session {
            last_seen: Instant::now(),
            idle_timeout,
        }
    }

    /// Records activity, which keeps the session alive for another idle timeout.
    pub fn touch(&mut self) {
        self.last_seen = Instant::now();
    }

    pub fn is_expired(&self) -> bool {
        self.last_seen.elapsed() > self.idle_timeout
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread::sleep;

    #[test]
    fn new_session_is_not_expired() {
        let session = Session::new(Duration::from_secs(60));
        assert!(!session.is_expired());
    }

    #[test]
    fn session_expires_after_idle_timeout() {
        let session = Session::new(Duration::from_millis(50));
        sleep(Duration::from_millis(80));
        assert!(session.is_expired());
    }

    #[test]
    fn touch_keeps_session_alive() {
        let mut session = Session::new(Duration::from_millis(100));
        sleep(Duration::from_millis(70));
        session.touch();
        sleep(Duration::from_millis(70));
        assert!(!session.is_expired());
    }

    #[test]
    fn fresh_session_with_long_timeout_is_not_expired() {
        let session = Session::new(Duration::from_secs(3600));
        assert!(!session.is_expired());
    }
}

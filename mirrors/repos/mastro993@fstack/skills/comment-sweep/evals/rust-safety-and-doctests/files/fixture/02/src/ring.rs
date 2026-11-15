//! A lock-free single-producer, single-consumer ring buffer.
//!
//! [`channel`] returns a [`Producer`] and a [`Consumer`] that share a fixed-size buffer.
//! Neither side ever blocks: [`Producer::push`] hands the value back when the buffer is
//! full, and [`Consumer::pop`] returns `None` when it is empty.
//!
//! ```rust
//! let (mut tx, mut rx) = tally::ring::channel(2);
//! tx.push(1).unwrap();
//! tx.push(2).unwrap();
//! assert_eq!(tx.push(3), Err(3));
//! assert_eq!(rx.pop(), Some(1));
//! ```

use std::cell::UnsafeCell;
use std::mem::MaybeUninit;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

// switched to AtomicUsize per review (was AtomicU32)
struct Inner<T> {
    slots: Box<[UnsafeCell<MaybeUninit<T>>]>,
    head: AtomicUsize,
    tail: AtomicUsize,
}

// SAFETY: slots are only reached through the one Producer and the one Consumer, and the
// head/tail hand-off gives each slot to exactly one of them at a time, so sharing Inner
// across threads is sound whenever the values themselves can be sent.
unsafe impl<T: Send> Sync for Inner<T> {}

/// The sending half of a ring buffer, created by [`channel`].
pub struct Producer<T> {
    inner: Arc<Inner<T>>,
}

/// The receiving half of a ring buffer, created by [`channel`].
pub struct Consumer<T> {
    inner: Arc<Inner<T>>,
}

/// Creates a ring buffer that holds up to `capacity` values and returns its two halves.
///
/// # Panics
///
/// Panics if `capacity` is zero. `capacity` must be a power of two.
///
/// # Examples
///
/// ```rust
/// let (tx, rx) = tally::ring::channel::<u64>(8);
/// assert_eq!(tx.capacity(), 8);
/// assert!(rx.is_empty());
/// ```
#[must_use]
pub fn channel<T>(capacity: usize) -> (Producer<T>, Consumer<T>) {
    assert!(capacity > 0, "ring capacity must be non-zero");
    let slots = (0..=capacity)
        .map(|_| UnsafeCell::new(MaybeUninit::uninit()))
        .collect();
    let inner = Arc::new(Inner {
        slots,
        head: AtomicUsize::new(0),
        tail: AtomicUsize::new(0),
    });
    (
        Producer {
            inner: Arc::clone(&inner),
        },
        Consumer { inner },
    )
}

impl<T> Producer<T> {
    /// Returns the capacity.
    ///
    /// # Arguments
    ///
    /// * `&self` - a reference to self
    ///
    /// # Returns
    ///
    /// * `usize` - the capacity
    #[must_use]
    pub fn capacity(&self) -> usize {
        self.inner.slots.len() - 1
    }

    /// Appends `value`, or hands it back in `Err` when the buffer is full.
    ///
    /// Never blocks and never allocates.
    ///
    /// ```rust
    /// let (mut tx, _rx) = tally::ring::channel(1);
    /// assert_eq!(tx.push("a"), Ok(()));
    /// assert_eq!(tx.push("b"), Err("b"));
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `Err(value)` when the buffer is full.
    pub fn push(&mut self, value: T) -> Result<(), T> {
        let inner = &*self.inner;
        // load the tail
        let tail = inner.tail.load(Ordering::Relaxed);
        let next = inner.next(tail);
        // check if full
        if next == inner.head.load(Ordering::Acquire) {
            return Err(value);
        }
        // SAFETY: only this Producer writes slots, and the Consumer does not read slot `tail`
        // until the Release store below publishes it.
        unsafe { (*inner.slots[tail].get()).write(value) };
        // increment the tail
        inner.tail.store(next, Ordering::Release);
        Ok(())
    }
}

impl<T> Consumer<T> {
    /// Removes and returns the oldest value, or `None` when the buffer is empty.
    ///
    /// ```rust
    /// let (mut tx, mut rx) = tally::ring::channel(4);
    /// tx.push(7).unwrap();
    /// assert_eq!(rx.pop(), Some(7));
    /// assert_eq!(rx.pop(), None);
    /// ```
    pub fn pop(&mut self) -> Option<T> {
        let inner = &*self.inner;
        let head = inner.head.load(Ordering::Relaxed);
        // Acquire here pairs with the Release in push(); do not weaken
        let tail = inner.tail.load(Ordering::Acquire);
        if head == tail {
            return None;
        }
        // SAFETY: head != tail, so push() wrote this slot and published it with the Release
        // store we just observed, and only this Consumer reads slots.
        let value = unsafe { (*inner.slots[head].get()).assume_init_read() };
        // increment the head
        inner.head.store(inner.next(head), Ordering::Release);
        Some(value)
    }

    /* old peek, kept in case the sink needs it again
    pub fn peek(&self) -> Option<&T> {
        let head = self.inner.head.load(Ordering::Relaxed);
        /* empty when head == tail */
        if head == self.inner.tail.load(Ordering::Acquire) {
            return None;
        }
        Some(unsafe { (*self.inner.slots[head].get()).assume_init_ref() })
    }
    */

    // TODO(#42): add a blocking pop_wait() for consumers that would rather park than spin.
    // https://github.com/tally-rs/tally/issues/42

    /// Returns how many values are waiting.
    ///
    /// The producer may push at the same time, so the count can be stale by the time it
    /// returns.
    #[must_use]
    pub fn len(&self) -> usize {
        let inner = &*self.inner;
        let head = inner.head.load(Ordering::Relaxed);
        let tail = inner.tail.load(Ordering::Acquire);
        (tail + inner.slots.len() - head) % inner.slots.len()
    }

    /// Returns `true` when no values are waiting.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

// ====== helpers ======

impl<T> Inner<T> {
    fn next(&self, index: usize) -> usize {
        (index + 1) % self.slots.len()
    }
}

// TODO: drop the values still in the buffer when both halves are gone
impl<T> Drop for Inner<T> {
    fn drop(&mut self) {
        let tail = *self.tail.get_mut();
        let mut head = *self.head.get_mut();
        while head != tail {
            // SAFETY: the slots from head up to tail were written by push() and never read
            // by pop(), and `&mut self` means neither half is left to touch them.
            unsafe { self.slots[head].get_mut().assume_init_drop() };
            head = self.next(head);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::channel;
    use std::sync::Arc;
    use std::thread;

    #[test]
    fn values_arrive_in_order_across_threads() {
        let (mut tx, mut rx) = channel(16);
        let producer = thread::spawn(move || {
            for i in 0..10_000_u32 {
                let mut value = i;
                while let Err(back) = tx.push(value) {
                    value = back;
                    std::hint::spin_loop();
                }
            }
        });
        let mut expected = 0;
        while expected < 10_000 {
            if let Some(value) = rx.pop() {
                assert_eq!(value, expected);
                expected += 1;
            }
        }
        producer.join().unwrap();
    }

    #[test]
    fn dropping_both_halves_drops_unread_values() {
        let marker = Arc::new(());
        let (mut tx, rx) = channel(4);
        tx.push(Arc::clone(&marker)).unwrap();
        tx.push(Arc::clone(&marker)).unwrap();
        drop((tx, rx));
        assert_eq!(Arc::strong_count(&marker), 1);
    }
}

//go:build !js

//go:generate stringer -type=State

// Package ratelimit implements a token-bucket rate limiter.
package ratelimit

import (
	"sync"
	"time"
)

// State is the limiter's state.
type State int

// The states
const (
	Open   State = iota // open
	Closed              // closed
)

// Limiter is a token bucket.
type Limiter struct {
	// mu guards tokens and last; Allow is called from many goroutines.
	mu     sync.Mutex
	tokens float64
	last   time.Time
	rate   float64 // tokens per second
	burst  float64
}

// NewLimiter returns a Limiter that allows rate events per second, in bursts of up to burst.
func NewLimiter(rate, burst float64) *Limiter {
	// create the limiter
	return &Limiter{tokens: burst, last: time.Now(), rate: rate, burst: burst}
}

// New returns a Limiter.
//
// Deprecated: use NewLimiter, which takes the burst size explicitly.
func New(rate float64) *Limiter { return NewLimiter(rate, rate) }

// Allow reports whether an event may happen now.
func (l *Limiter) Allow() bool {
	// lock the mutex
	l.mu.Lock()
	defer l.mu.Unlock() // unlock when done
	now := time.Now()
	// refill tokens based on elapsed time
	l.tokens = min(l.burst, l.tokens+now.Sub(l.last).Seconds()*l.rate)
	l.last = now
	// if l.tokens < 1 { log.Println("denied") }
	if l.tokens < 1 {
		return false
	}
	l.tokens-- // use a token
	return true
}

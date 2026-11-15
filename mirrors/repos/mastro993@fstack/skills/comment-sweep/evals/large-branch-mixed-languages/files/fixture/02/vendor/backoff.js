/**
 * tiny-backoff v1.4.2
 * Vendored copy. Upstream: https://github.com/example/tiny-backoff
 */
"use strict";

// default options
var DEFAULTS = {
  base: 1000, // base delay
  factor: 2, // multiplier
  max: 60000, // cap
  jitter: true, // add jitter
};

// merge options with defaults
function merge(opts) {
  var out = {};
  // copy defaults
  for (var k in DEFAULTS) out[k] = DEFAULTS[k];
  // copy user options
  if (opts) for (var j in opts) out[j] = opts[j];
  return out;
}

// compute the delay for attempt n
function delay(attempt, opts) {
  var o = merge(opts);
  // exponential growth
  var d = o.base * Math.pow(o.factor, attempt);
  // clamp to max
  if (d > o.max) d = o.max;
  // full jitter
  if (o.jitter) d = Math.random() * d;
  return Math.round(d);
}

// sleep helper
function sleep(ms) {
  return new Promise(function (resolve) {
    setTimeout(resolve, ms);
  });
}

// retry fn up to `retries` times
async function retry(fn, retries, opts) {
  var lastErr;
  for (var i = 0; i <= retries; i++) {
    try {
      return await fn(i);
    } catch (err) {
      lastErr = err;
      // console.log("retrying", i);
      if (i < retries) await sleep(delay(i, opts));
    }
  }
  throw lastErr;
}

module.exports = { delay: delay, retry: retry, sleep: sleep };

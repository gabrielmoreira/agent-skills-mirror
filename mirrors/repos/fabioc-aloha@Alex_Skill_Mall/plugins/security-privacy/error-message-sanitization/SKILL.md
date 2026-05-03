---
type: skill
lifecycle: stable
inheritance: inheritable
name: error-message-sanitization
description: Raw error messages leak internal information to users:
tier: standard
applyTo: '**/*error*,**/*message*,**/*sanitization*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Error Message Sanitization

## The Problem

Raw error messages leak internal information to users:

- File paths reveal directory structure
- Stack traces expose code organization
- Internal state shows implementation details
- SDK errors contain connection strings or endpoints

```javascript
// Bad: leaks internals
catch (err) {
  res.status(500).json({ error: err.message, stack: err.stack });
}
```

## The Solution

Sanitize at system boundaries before returning errors to users.

```javascript
function sanitizeForUser(error) {
  let msg = error.message || 'An error occurred';
  
  // Strip absolute paths
  msg = msg.replace(/[A-Z]:\\[^\s]+/gi, '[path]');
  msg = msg.replace(/\/(?:home|usr|var|etc)[^\s]+/gi, '[path]');
  
  // Strip stack traces
  msg = msg.replace(/\s+at\s+.+\(.+:\d+:\d+\)/g, '');
  
  // Strip connection strings
  msg = msg.replace(/(?:mongodb|postgresql|mysql|redis):\/\/[^\s]+/gi, '[connection]');
  
  // Strip Azure resource IDs
  msg = msg.replace(/\/subscriptions\/[a-f0-9-]+/gi, '/subscriptions/[id]');
  
  return msg;
}

// Usage
catch (err) {
  console.error('Internal error:', err); // Full error for logs
  res.status(500).json({ 
    error: sanitizeForUser(err),
    requestId: req.id // For support correlation
  });
}
```

## Verification

```javascript
const testCases = [
  'Failed at C:\\Users\\dev\\project\\src\\api.js:42',
  'Connection failed: mongodb://user:pass@host:27017/db',
  '/subscriptions/abc-123/resourceGroups/prod/...',
  'Error in /home/deploy/app/server.js'
];

testCases.forEach(msg => {
  const sanitized = sanitizeForUser({ message: msg });
  console.log(sanitized);
  // Should not contain actual paths, credentials, or resource IDs
});
```

## When to Apply

- REST API error responses
- GraphQL error messages
- WebSocket error events
- Any user-facing error display

## Tags

`security` `error-handling` `api` `privacy`

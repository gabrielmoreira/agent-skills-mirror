#!/usr/bin/env bash
# PR #42 (per-line-discount, pushed, the user's checkout) and main's PR #45 both rewrite lineTotal.
source ./lib.sh
start_repo main
put package.json <<'X'
{
  "name": "shop",
  "private": true,
  "type": "module",
  "scripts": { "test": "node --test" }
}
X
put .github/workflows/ci.yml <<'X'
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm test
X
put src/cart.js <<'X'
// Prices are in cents.
export function lineTotal(item) {
  return item.price * item.qty;
}

export function orderTotal(items, discount = 0) {
  const subtotal = items.reduce((sum, item) => sum + lineTotal(item), 0);
  return Math.round(subtotal * (1 - discount));
}
X
put test/cart.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { lineTotal, orderTotal } from '../src/cart.js';

test('lineTotal multiplies price by quantity', () => {
  assert.equal(lineTotal({ price: 250, qty: 3 }), 750);
});

test('orderTotal sums the lines', () => {
  assert.equal(orderTotal([{ price: 250, qty: 2 }, { price: 100, qty: 1 }]), 600);
});
X
commit "Initial cart"
git push -q -u origin main
base=$(git rev-parse HEAD)

git checkout -q -b per-line-discount
put src/cart.js <<'X'
// Prices are in cents.
export function lineTotal(item, discount = 0) {
  return Math.round(item.price * item.qty * (1 - discount));
}

export function orderTotal(items, discount = 0) {
  return items.reduce((sum, item) => sum + lineTotal(item, discount), 0);
}
X
commit "wip" 42
cat >> test/cart.test.js <<'X'

test('orderTotal rounds the discount per line, like billing', () => {
  const items = [{ price: 333, qty: 1 }, { price: 333, qty: 1 }, { price: 333, qty: 1 }];
  assert.equal(orderTotal(items, 0.1), 900);
});
X
commit "fix tests" 42
git push -q -u origin per-line-discount

git checkout -q main
put src/cart.js <<'X'
// Prices are in cents.
export function lineTotal(item) {
  if (!Number.isInteger(item.qty) || item.qty < 1) {
    throw new RangeError(`quantity must be a whole number of at least 1, got ${item.qty}`);
  }
  return item.price * item.qty;
}

export function orderTotal(items, discount = 0) {
  const subtotal = items.reduce((sum, item) => sum + lineTotal(item), 0);
  return Math.round(subtotal * (1 - discount));
}
X
cat >> test/cart.test.js <<'X'

test('lineTotal rejects quantities that are not whole numbers of at least 1', () => {
  for (const qty of [-1, 0, 1.5]) {
    assert.throws(() => lineTotal({ price: 250, qty }), RangeError);
  }
});
X
commit "Reject quantities below 1 (#45)" 45
git push -q origin main
# The user's local main and origin/main predate #45: they haven't fetched since.
git checkout -q per-line-discount
git branch -f main "$base"
git update-ref refs/remotes/origin/main "$base"

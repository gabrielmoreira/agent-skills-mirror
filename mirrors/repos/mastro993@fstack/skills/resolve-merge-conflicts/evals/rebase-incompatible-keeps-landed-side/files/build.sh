#!/usr/bin/env bash
# PR #21 (bankers-rounding, 3 commits, pushed as a draft) and main's PR #19 both rewrite roundMoney,
# incompatibly on negative ties; both also add an export to src/index.js.
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
put src/money.js <<'X'
// Rounds an amount in dollars to whole cents.
export function roundMoney(amount) {
  return Math.round(amount * 100) / 100;
}
X
put src/cart.js <<'X'
import { roundMoney } from './money.js';

export function lineTotal(item) {
  return roundMoney(item.price * item.qty);
}
X
put src/index.js <<'X'
export { roundMoney } from './money.js';
export { lineTotal } from './cart.js';
X
put test/money.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { roundMoney } from '../src/money.js';

test('roundMoney rounds to whole cents', () => {
  assert.equal(roundMoney(1.234), 1.23);
  assert.equal(roundMoney(0.375), 0.38);
});
X
commit "Initial money helpers"
git push -q -u origin main
base=$(git rev-parse HEAD)

git checkout -q -b bankers-rounding
put src/money.js <<'X'
// Rounds an amount in dollars to whole cents. Exact ties go to the even cent (ACC-7).
export function roundMoney(amount) {
  const cents = amount * 100;
  const floor = Math.floor(cents);
  const rest = cents - floor;
  if (rest > 0.5) return (floor + 1) / 100;
  if (rest < 0.5) return floor / 100;
  return (floor % 2 === 0 ? floor : floor + 1) / 100;
}
X
cat >> test/money.test.js <<'X'

test('roundMoney sends ties to the even cent', () => {
  assert.equal(roundMoney(0.125), 0.12);
  assert.equal(roundMoney(0.625), 0.62);
  assert.equal(roundMoney(0.875), 0.88);
});
X
commit "wip rounding" 21
put src/invoice.js <<'X'
import { lineTotal } from './cart.js';
import { roundMoney } from './money.js';

export function invoiceTotal(items) {
  return roundMoney(items.reduce((sum, item) => sum + lineTotal(item), 0));
}
X
put test/invoice.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { invoiceTotal } from '../src/invoice.js';

test('invoiceTotal sums rounded lines', () => {
  assert.equal(invoiceTotal([{ price: 0.125, qty: 1 }, { price: 1, qty: 2 }]), 2.12);
});
X
commit "invoice" 21
put src/index.js <<'X'
export { roundMoney } from './money.js';
export { lineTotal } from './cart.js';
export { invoiceTotal } from './invoice.js';
X
commit "export" 21
git push -q -u origin bankers-rounding

git checkout -q main
put src/money.js <<'X'
// Rounds an amount in dollars to whole cents, halves away from zero, so a refund mirrors its charge.
export function roundMoney(amount) {
  return (Math.sign(amount) * Math.round(Math.abs(amount) * 100)) / 100;
}
X
put src/refund.js <<'X'
import { lineTotal } from './cart.js';

export function refundTotal(items) {
  return -items.reduce((sum, item) => sum + lineTotal(item), 0);
}
X
put src/index.js <<'X'
export { roundMoney } from './money.js';
export { lineTotal } from './cart.js';
export { refundTotal } from './refund.js';
X
cat >> test/money.test.js <<'X'

test('roundMoney rounds negative amounts to the same magnitude as positive ones', () => {
  assert.equal(roundMoney(-0.375), -0.38);
  assert.equal(roundMoney(-0.125), -0.13);
  assert.equal(roundMoney(-1.234), -1.23);
});
X
put test/refund.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { refundTotal } from '../src/refund.js';

test('refundTotal is the negated total of the lines', () => {
  assert.equal(refundTotal([{ price: 1.25, qty: 2 }]), -2.5);
});
X
commit "Round negative amounts away from zero (#19)" 19
git push -q origin main
git checkout -q bankers-rounding
git branch -f main "$base"
git update-ref refs/remotes/origin/main "$base"

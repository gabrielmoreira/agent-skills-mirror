#!/usr/bin/env bash
# PR #33 (receipt-tax, pushed) adds tax and line totals using formatPrice; main's PR #31 renamed
# formatPrice to formatMoney and threaded the currency. cart.js and bin/receipt.js conflict;
# PR #33's new src/tax.js merges cleanly but still imports formatPrice.
source ./lib.sh
start_repo main
put package.json <<'X'
{
  "name": "receipts",
  "private": true,
  "type": "module",
  "bin": { "receipt": "bin/receipt.js" },
  "scripts": { "test": "node --test" }
}
X
put README.md <<'X'
# receipts

Prints store receipts.

    node bin/receipt.js examples/order.json

Run the tests with `npm test`.
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
      - run: node bin/receipt.js examples/order.json
X
put examples/order.json <<'X'
{ "currency": "USD", "taxRate": 0.08, "items": [ { "name": "Notebook", "price": 450, "qty": 2 }, { "name": "Pen", "price": 125, "qty": 3 } ] }
X
put src/format.js <<'X'
// Amounts are in cents.
export function formatPrice(cents) {
  return `$${(cents / 100).toFixed(2)}`;
}
X
put src/cart.js <<'X'
import { formatPrice } from './format.js';

export function describeLine(item) {
  return `${item.qty} x ${item.name} @ ${formatPrice(item.price)}`;
}

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}
X
put bin/receipt.js <<'X'
#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { describeLine, subtotal } from '../src/cart.js';
import { formatPrice } from '../src/format.js';

const order = JSON.parse(readFileSync(process.argv[2], 'utf8'));
for (const item of order.items) console.log(describeLine(item));
console.log(`Total: ${formatPrice(subtotal(order.items))}`);
X
put test/cart.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { describeLine, subtotal } from '../src/cart.js';

test('describeLine shows quantity, name and unit price', () => {
  assert.equal(describeLine({ name: 'Pen', price: 125, qty: 3 }), '3 x Pen @ $1.25');
});

test('subtotal sums the lines', () => {
  assert.equal(subtotal([{ price: 125, qty: 3 }, { price: 450, qty: 2 }]), 1275);
});
X
commit "Initial receipts"
git push -q -u origin main
base=$(git rev-parse HEAD)

git checkout -q -b receipt-tax
put src/tax.js <<'X'
import { formatPrice } from './format.js';

export function taxLine(subtotalCents, rate) {
  return `Tax (${Math.round(rate * 100)}%): ${formatPrice(Math.round(subtotalCents * rate))}`;
}
X
put test/tax.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { taxLine } from '../src/tax.js';

test('taxLine shows the rate and the rounded tax', () => {
  assert.equal(taxLine(1275, 0.08), 'Tax (8%): $1.02');
});
X
commit "tax line" 33
put src/cart.js <<'X'
import { formatPrice } from './format.js';

export function describeLine(item) {
  return `${item.qty} x ${item.name} @ ${formatPrice(item.price)} = ${formatPrice(item.price * item.qty)}`;
}

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}
X
put bin/receipt.js <<'X'
#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { describeLine, subtotal } from '../src/cart.js';
import { formatPrice } from '../src/format.js';
import { taxLine } from '../src/tax.js';

const order = JSON.parse(readFileSync(process.argv[2], 'utf8'));
for (const item of order.items) console.log(describeLine(item));
const sub = subtotal(order.items);
const tax = Math.round(sub * order.taxRate);
console.log(taxLine(sub, order.taxRate));
console.log(`Total: ${formatPrice(sub + tax)}`);
X
put test/cart.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { describeLine, subtotal } from '../src/cart.js';

test('describeLine shows quantity, name, unit price and line total', () => {
  assert.equal(describeLine({ name: 'Pen', price: 125, qty: 3 }), '3 x Pen @ $1.25 = $3.75');
});

test('subtotal sums the lines', () => {
  assert.equal(subtotal([{ price: 125, qty: 3 }, { price: 450, qty: 2 }]), 1275);
});
X
commit "line totals" 33
git push -q -u origin receipt-tax

git checkout -q main
put src/format.js <<'X'
// Amounts are in cents.
export function formatMoney(cents, currency = 'USD') {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(cents / 100);
}
X
put src/cart.js <<'X'
import { formatMoney } from './format.js';

export function describeLine(item, currency = 'USD') {
  return `${item.qty} x ${item.name} @ ${formatMoney(item.price, currency)}`;
}

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}
X
put bin/receipt.js <<'X'
#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { describeLine, subtotal } from '../src/cart.js';
import { formatMoney } from '../src/format.js';

const order = JSON.parse(readFileSync(process.argv[2], 'utf8'));
for (const item of order.items) console.log(describeLine(item, order.currency));
console.log(`Total: ${formatMoney(subtotal(order.items), order.currency)}`);
X
put examples/berlin-order.json <<'X'
{ "currency": "EUR", "taxRate": 0.19, "items": [ { "name": "Notizbuch", "price": 450, "qty": 2 }, { "name": "Stift", "price": 125, "qty": 3 } ] }
X
cat >> test/cart.test.js <<'X'

test('describeLine prints the order currency', () => {
  assert.equal(describeLine({ name: 'Stift', price: 125, qty: 3 }, 'EUR'), '3 x Stift @ €1.25');
});
X
put test/format.test.js <<'X'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatMoney } from '../src/format.js';

test('formatMoney formats cents in the given currency', () => {
  assert.equal(formatMoney(1275), '$12.75');
  assert.equal(formatMoney(1275, 'EUR'), '€12.75');
});
X
commit "Receipts in the order's currency (#31)" 31
git push -q origin main
git checkout -q receipt-tax
git branch -f main "$base"
git update-ref refs/remotes/origin/main "$base"

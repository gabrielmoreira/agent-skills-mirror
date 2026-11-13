import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { priceCart, subtotalCents } from './pricing.ts';

const MORNING = new Date(2026, 10, 12, 9, 0);

describe('priceCart', () => {
  it('sums line items', () => {
    const price = priceCart(
      [
        { sku: 'tea', unitPriceCents: 450, quantity: 2 },
        { sku: 'mug', unitPriceCents: 1200, quantity: 1 },
      ],
      undefined,
      MORNING,
    );
    assert.equal(price.subtotalCents, 2100);
    assert.equal(price.totalCents, 2100);
  });

  it('computes the subtotal for several items', () => {
    const price = priceCart(
      [
        { sku: 'tea', unitPriceCents: 300, quantity: 1 },
        { sku: 'jam', unitPriceCents: 500, quantity: 2 },
      ],
      undefined,
      MORNING,
    );
    assert.equal(price.subtotalCents, 1300);
  });

  it('applies a percentage coupon', () => {
    const price = priceCart([{ sku: 'mug', unitPriceCents: 1200, quantity: 1 }], { code: 'TEN', percentOff: 10 }, MORNING);
    assert.equal(price.discountCents, 120);
    assert.equal(price.totalCents, 1080);
  });

  it('gives no happy hour discount outside happy hour', () => {
    const price = priceCart([{ sku: 'mug', unitPriceCents: 1000, quantity: 1 }]);
    assert.equal(price.discountCents, 0);
  });

  it('adds the happy hour discount between 17:00 and 19:00', () => {
    const price = priceCart([{ sku: 'mug', unitPriceCents: 1000, quantity: 1 }], undefined, new Date(2026, 10, 12, 17, 30));
    assert.equal(price.discountCents, 100);
  });
});

describe('subtotalCents', () => {
  it('adds price times quantity', () => {
    assert.equal(subtotalCents([{ sku: 'tea', unitPriceCents: 450, quantity: 2 }]), 900);
  });
});

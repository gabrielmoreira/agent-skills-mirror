import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';
import { addDays, db } from '../src/db.js';
import { placeHold } from '../src/holds.js';
import { checkOut, renew } from '../src/loans.js';
import { sendReminders } from '../src/reminders.js';

const day0 = new Date('2026-03-02T00:00:00Z');

beforeEach(() => {
  for (const table of Object.values(db)) table.length = 0;
  db.members.push({ id: 1, name: 'Ines Okafor', email: 'ines@example.org' }, { id: 2, name: 'Tom Reyes', email: 'tom@example.org' });
  db.titles.push({ id: 1, name: 'The Overstory' });
  db.copies.push({ id: 1, titleId: 1 });
});

test('a loan renews once', () => {
  const loan = checkOut(1, 1, day0);
  assert.equal(renew(loan.id).ok, true);
  assert.equal(renew(loan.id).reason, 'renewal-limit');
});

test('a waiting hold blocks renewal', () => {
  const loan = checkOut(1, 1, day0);
  placeHold(1, 2, day0);
  assert.equal(renew(loan.id).reason, 'hold-waiting');
});

test('the first reminder goes out when the loan is already overdue', () => {
  checkOut(1, 1, day0);
  sendReminders(addDays(day0, 20));
  assert.equal(db.outbox.length, 0);
  sendReminders(addDays(day0, 28));
  assert.equal(db.outbox.length, 1);
});

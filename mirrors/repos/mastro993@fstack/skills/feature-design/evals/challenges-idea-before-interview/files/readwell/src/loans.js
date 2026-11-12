import { addDays, db } from './db.js';
import { holdsWaiting } from './holds.js';

export const LOAN_DAYS = 21;
export const MAX_RENEWALS = 1; // docs/adr/0003

export function checkOut(copyId, memberId, now = new Date()) {
  const loan = {
    id: db.loans.length + 1,
    copyId,
    memberId,
    dueDate: addDays(now, LOAN_DAYS),
    renewals: 0,
    returnedAt: null,
  };
  db.loans.push(loan);
  return loan;
}

// Renewals happen at the desk or from the member's "My loans" page after logging in.
export function renew(loanId, now = new Date()) {
  const loan = db.loans.find((l) => l.id === loanId);
  if (!loan || loan.returnedAt) return { ok: false, reason: 'not-on-loan' };
  if (loan.renewals >= MAX_RENEWALS) return { ok: false, reason: 'renewal-limit' };
  const copy = db.copies.find((c) => c.id === loan.copyId);
  if (holdsWaiting(copy.titleId).length > 0) return { ok: false, reason: 'hold-waiting' }; // docs/adr/0002
  loan.dueDate = addDays(loan.dueDate, LOAN_DAYS);
  loan.renewals += 1;
  return { ok: true, dueDate: loan.dueDate };
}

export function giveBack(loanId, now = new Date()) {
  const loan = db.loans.find((l) => l.id === loanId);
  loan.returnedAt = now;
  return loan;
}

export function isOverdue(loan, now = new Date()) {
  return !loan.returnedAt && loan.dueDate < now;
}

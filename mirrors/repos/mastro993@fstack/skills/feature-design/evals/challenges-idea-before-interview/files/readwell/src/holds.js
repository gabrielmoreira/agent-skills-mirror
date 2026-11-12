import { db } from './db.js';

export function placeHold(titleId, memberId, now = new Date()) {
  const hold = { id: db.holds.length + 1, titleId, memberId, placedAt: now };
  db.holds.push(hold);
  return hold;
}

export function holdsWaiting(titleId) {
  return db.holds.filter((h) => h.titleId === titleId);
}

// In-memory stand-in for the SQLite tables, so the modules and tests run without setup.
export const db = {
  members: [], // { id, name, email }
  titles: [], // { id, name }
  copies: [], // { id, titleId }
  loans: [], // { id, copyId, memberId, dueDate, renewals, returnedAt }
  holds: [], // { id, titleId, memberId, placedAt }
  outbox: [], // { to, subject, body }
};

export function addDays(date, days) {
  const d = new Date(date);
  d.setUTCDate(d.getUTCDate() + days);
  return d;
}

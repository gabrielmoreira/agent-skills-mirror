import { db } from './db.js';
import { isOverdue } from './loans.js';

// Nightly job (cron, 02:00). Email only: docs/adr/0001.
// Members hear from us once a loan is already overdue, then every 7 days until the copy is back.
export function sendReminders(now = new Date()) {
  for (const loan of db.loans) {
    if (!isOverdue(loan, now)) continue;
    const daysOver = Math.floor((now - loan.dueDate) / 86_400_000);
    if (daysOver % 7 !== 0) continue;
    const member = db.members.find((m) => m.id === loan.memberId);
    const copy = db.copies.find((c) => c.id === loan.copyId);
    const title = db.titles.find((t) => t.id === copy.titleId);
    db.outbox.push({
      to: member.email,
      subject: `Overdue: ${title.name}`,
      body: `Your loan of "${title.name}" was due on ${loan.dueDate.toISOString().slice(0, 10)}. Please bring it back to the desk.`,
    });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) sendReminders();

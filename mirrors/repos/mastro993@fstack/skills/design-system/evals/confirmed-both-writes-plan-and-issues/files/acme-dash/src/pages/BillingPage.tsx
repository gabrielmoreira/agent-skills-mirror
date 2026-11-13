import { Button } from "../features/billing/Button";

const invoices = [
  { id: "INV-104", amount: "$1,240.00", status: "Paid" },
  { id: "INV-105", amount: "$980.00", status: "Overdue" },
];

export function BillingPage() {
  return (
    <main className="mx-auto max-w-5xl p-8">
      <h1 className="text-2xl font-bold">Billing</h1>
      <section className="mt-6 rounded-lg border border-gray-200 bg-white p-4 shadow">
        <h2 className="text-base font-semibold">Current plan</h2>
        <p className="mt-1 text-sm text-gray-500">Team, 12 seats</p>
        <Button kind="secondary" className="mt-4">Change plan</Button>
      </section>
      <section className="mt-4 rounded-xl border border-[#E3E5EA] bg-white p-[18px] shadow-sm">
        <h2 className="text-base font-semibold">Invoices</h2>
        <ul className="mt-2 divide-y">
          {invoices.map((i) => (
            <li key={i.id} className="flex justify-between py-2 text-sm">
              <span>{i.id}</span>
              <span className={i.status === "Overdue" ? "text-[#C8372D]" : "text-gray-500"}>{i.amount}</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

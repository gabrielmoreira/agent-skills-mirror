import { useState } from "react";
import { HabitRow, type Habit } from "../components/HabitRow";

const initial: Habit[] = [
  { id: "h1", name: "Drink a glass of water", doneToday: true, weekCount: 5 },
  { id: "h2", name: "10 minutes of reading", doneToday: false, weekCount: 3 },
  { id: "h3", name: "Walk after lunch", doneToday: false, weekCount: 4 },
];

export function Today() {
  const [habits, setHabits] = useState(initial);
  const toggle = (id: string) =>
    setHabits((hs) => hs.map((h) => (h.id === id ? { ...h, doneToday: !h.doneToday } : h)));
  return (
    <main className="mx-auto max-w-md p-4">
      <h1 className="text-xl font-bold">Today</h1>
      <ul className="mt-4">
        {habits.map((h) => <HabitRow key={h.id} habit={h} onToggle={() => toggle(h.id)} />)}
      </ul>
      <button className="mt-6 w-full rounded bg-blue-500 py-2 text-white">Add a habit</button>
    </main>
  );
}

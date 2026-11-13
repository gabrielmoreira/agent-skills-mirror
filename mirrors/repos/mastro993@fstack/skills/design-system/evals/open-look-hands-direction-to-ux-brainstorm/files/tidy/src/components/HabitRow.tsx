export type Habit = { id: string; name: string; doneToday: boolean; weekCount: number };

export function HabitRow({ habit, onToggle }: { habit: Habit; onToggle: () => void }) {
  return (
    <li className="flex items-center justify-between border-b border-gray-200 py-3">
      <label className="flex items-center gap-3">
        <input type="checkbox" checked={habit.doneToday} onChange={onToggle} />
        <span className={habit.doneToday ? "text-gray-400 line-through" : "text-gray-900"}>{habit.name}</span>
      </label>
      <span className="text-xs text-gray-500">{habit.weekCount}/7 this week</span>
    </li>
  );
}

export function NewHabit({ onSave }: { onSave: (name: string) => void }) {
  return (
    <main className="mx-auto max-w-md p-4">
      <h1 className="text-xl font-bold">New habit</h1>
      <form
        className="mt-4 flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          onSave(new FormData(e.currentTarget).get("name") as string);
        }}
      >
        <label className="text-sm">What do you want to do each day?</label>
        <input name="name" className="rounded border border-gray-300 p-2" placeholder="e.g. Stretch for 5 minutes" />
        <button className="rounded bg-green-600 py-2 text-white">Save</button>
      </form>
    </main>
  );
}

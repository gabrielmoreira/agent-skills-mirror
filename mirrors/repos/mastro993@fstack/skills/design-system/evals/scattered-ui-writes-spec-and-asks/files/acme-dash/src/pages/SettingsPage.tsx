import { DeleteAccountDialog } from "../features/settings/DeleteAccountDialog";
import Btn from "../features/settings/components/Btn";
import { useSession } from "../lib/store";

export function SettingsPage() {
  const { user, signOut } = useSession();
  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="mt-6 rounded-[10px] border border-[#E3E5EA] bg-white p-4">
        <label className="block text-sm font-medium" htmlFor="name">Display name</label>
        <input id="name" defaultValue={user?.name} className="mt-1 w-full rounded-[6px] border border-[#E3E5EA] px-3 py-2 text-sm" />
        <div className="mt-4 flex gap-2">
          <Btn>Save</Btn>
          <Btn variant="outline" onClick={signOut}>Sign out</Btn>
        </div>
      </div>
      <div className="mt-6">
        <DeleteAccountDialog onDelete={signOut} />
      </div>
    </main>
  );
}

import * as Dialog from "@radix-ui/react-dialog";
import Btn from "./components/Btn";

export function DeleteAccountDialog({ onDelete }: { onDelete: () => void }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <Btn variant="danger">Delete account</Btn>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[440px] -translate-x-1/2 -translate-y-1/2 rounded-lg bg-surface p-6">
          <Dialog.Title className="text-lg font-semibold">Delete your account?</Dialog.Title>
          <Dialog.Description className="mt-2 text-sm text-muted">This removes every project you own.</Dialog.Description>
          <div className="mt-6 flex justify-end gap-2">
            <Dialog.Close asChild>
              <Btn variant="outline">Cancel</Btn>
            </Dialog.Close>
            <Btn variant="danger" onClick={onDelete}>Delete</Btn>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

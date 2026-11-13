import { useEffect } from "react";

type Props = { open: boolean; title: string; message: string; onConfirm: () => void; onCancel: () => void };

export function ConfirmModal({ open, title, message, onConfirm, onCancel }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onCancel}>
      <div className="w-[420px] rounded-[10px] bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-[#16181D]">{title}</h2>
        <p className="mt-2 text-sm text-gray-500">{message}</p>
        <div className="mt-6 flex justify-end gap-2">
          <button className="rounded-md px-4 py-2 text-sm" onClick={onCancel}>Cancel</button>
          <button className="rounded-md bg-[#C8372D] px-4 py-2 text-sm text-white" onClick={onConfirm}>Delete</button>
        </div>
      </div>
    </div>
  );
}

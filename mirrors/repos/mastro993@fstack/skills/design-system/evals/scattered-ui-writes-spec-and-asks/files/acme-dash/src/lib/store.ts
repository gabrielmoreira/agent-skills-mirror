import { create } from "zustand";

type Session = { user: { name: string; avatarUrl?: string } | null; signOut: () => void };

export const useSession = create<Session>((set) => ({
  user: { name: "Dana Ortiz" },
  signOut: () => set({ user: null }),
}));

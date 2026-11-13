import { create } from "zustand";

type SessionState = { user: { name: string } | null; signOut: () => void };

export const useSessionStore = create<SessionState>((set) => ({
  user: { name: "Priya Shah" },
  signOut: () => set({ user: null }),
}));

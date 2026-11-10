// Workspace settings for Shiftly, a shift-scheduling app for restaurants and shops.
// Managers edit these; staff only see their own notification settings.

export type Role = "owner" | "manager" | "staff";

export interface WorkspaceSettings {
  workspaceName: string; // e.g. "Trattoria Da Gino – Milano Centro"
  timezone: string; // IANA, e.g. "Europe/Rome"
  weekStartsOn: "monday" | "sunday";
  locations: Array<{ id: string; name: string; address: string }>; // 1–40 per workspace
  scheduling: {
    publishDeadlineDays: number; // schedule must be published N days before the week starts
    allowShiftSwaps: boolean;
    swapsNeedApproval: boolean;
    maxHoursPerWeek: number | null;
    minRestHoursBetweenShifts: number;
  };
  timeClock: {
    enabled: boolean;
    geofenceMeters: number | null;
    earlyClockInMinutes: number;
    autoClockOutAfterHours: number | null;
  };
  notifications: {
    shiftPublished: { email: boolean; push: boolean; sms: boolean };
    swapRequested: { email: boolean; push: boolean; sms: boolean };
    shiftReminder: { email: boolean; push: boolean; sms: boolean; minutesBefore: number };
  };
  billing: { plan: "free" | "team" | "business"; seats: number; seatsUsed: number };
}

/**
 * Sovereign Frontend Client State & UI Contracts
 * Co-authored-by: Flowork OS <agent@floworkos.com>
 */

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "reconnecting";

export interface GatewayUIState {
  readonly status: ConnectionStatus;
  readonly sessionId: string | null;
  readonly activeTasks: ReadonlyArray<TaskViewModel>;
  readonly lastError: string | null;
  readonly latencyMs: number;
}

export interface TaskViewModel {
  readonly taskId: string;
  readonly name: string;
  readonly progressPercent: number;
  readonly isRunning: boolean;
  readonly exitCode: number | null;
}

export interface ClientUIEvents {
  readonly onTaskSubmit: (name: string, payload: Record<string, unknown>) => Promise<void>;
  readonly onTaskCancel: (taskId: string) => Promise<void>;
  readonly onReconnect: () => Promise<void>;
}

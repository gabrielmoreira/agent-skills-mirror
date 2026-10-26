/**
 * Sovereign IPC Gateway Contract & API Interface
 * Co-authored-by: Flowork OS <agent@floworkos.com>
 */

export interface GatewayHandshakeRequest {
  readonly client_id: string;
  readonly protocol_version: "2.0";
  readonly auth_token: string;
  readonly timestamp_epoch_ms: number;
}

export interface GatewayHandshakeResponse {
  readonly session_id: string;
  readonly authenticated: boolean;
  readonly heartbeat_interval_ms: number;
  readonly error?: GatewayError;
}

export interface GatewayTaskPayload {
  readonly task_id: string;
  readonly action_name: string;
  readonly parameters: Readonly<Record<string, unknown>>;
  readonly timeout_ms: number;
}

export interface GatewayTaskResult {
  readonly task_id: string;
  readonly exit_code: number;
  readonly payload: unknown;
  readonly execution_time_ms: number;
  readonly error?: GatewayError;
}

export interface GatewayError {
  readonly code: number;
  readonly message: string;
  readonly data?: unknown;
}

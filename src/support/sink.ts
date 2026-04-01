/**
 * support/sink.ts — Minimal reporter sinks for global and per-repo output.
 */

import type { RuntimeAdapter } from "./runtime.ts";

export type FinishRepoInfo = {
  repo: string;
  files: number;
  followed: number;
  skipped?: boolean;
  unsupported?: string;
  error?: string;
};

export type FinishStageInfo = {
  ok: boolean;
  elapsed: number;
  error?: string;
  code?: number | null;
  detail?: string | string[] | null;
};

export type DashboardLike = {
  updateSlot(
    slot: number,
    info: { stage: string; action?: string; detail?: string },
  ): void;
  completeSlot(slot: number, info: FinishRepoInfo): void;
  failSlot(slot: number, info: FinishRepoInfo, lines: string[]): void;
};

export type ReporterSink = {
  startStage?(stage: string, action: string): void;
  finishStage?(result: FinishStageInfo): void;
  line(text: string): void;
  finishRepo?(info: FinishRepoInfo): void;
};

function formatDuration(ms: number): string {
  return `${(ms / 1000).toFixed(2)}s`;
}

export function makeGlobalSink(runtime: RuntimeAdapter): ReporterSink {
  const term = runtime.terminal();
  const out = (text: string) => term.stdout.write(text);
  let depth = 0;

  function indent(): string {
    return "  ".repeat(Math.max(0, depth));
  }

  return {
    startStage(stage, action) {
      out(`${indent()}- ${stage}: ${action}\n`);
      depth += 1;
    },

    finishStage(result) {
      depth = Math.max(0, depth - 1);
      out(
        `${indent()}${result.ok ? "ok" : "error"} ${
          formatDuration(result.elapsed)
        }\n`,
      );
    },

    line(text) {
      out(`${indent()}${text}\n`);
    },
  };
}

const MAX_ERROR_LINES = 4;

export function makeRepoSink(
  dashboard: DashboardLike,
  slot: number,
): ReporterSink {
  const bufferedLines: string[] = [];
  let currentStage = "";
  let currentAction = "";
  function remember(text: string): void {
    const line = text.trim();
    if (!line) return;
    bufferedLines.push(line);
    dashboard.updateSlot(slot, {
      stage: currentStage,
      action: currentAction,
      detail: line,
    });
  }

  return {
    startStage(stage, action) {
      currentStage = stage;
      currentAction = action;
      dashboard.updateSlot(slot, { stage, action });
    },

    line(text) {
      remember(text);
    },

    finishRepo(info) {
      if (info.error) {
        dashboard.failSlot(slot, info, bufferedLines.slice(-MAX_ERROR_LINES));
        return;
      }
      dashboard.completeSlot(slot, info);
    },
  };
}

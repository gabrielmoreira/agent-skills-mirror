/**
 * support/dashboard.ts — Live terminal dashboard for parallel repo processing.
 *
 * Keeps a live bottom region with one primary line and one optional secondary
 * line per active slot. Completed repos move into permanent history above the
 * live region. Non-TTY mode prints one line per repo with no cursor control.
 */

import type { RuntimeAdapter } from "./runtime.ts";
import type { FinishRepoInfo } from "./sink.ts";

type SlotState = {
  repo: string;
  stage: string;
  action?: string;
  detail?: string;
  startedAt: number;
} | null;

type Counters = {
  total: number;
  ok: number;
  skip: number;
  empty: number;
  unsupported: number;
  err: number;
};

const STAGE_WIDTH = 10;
const REPO_WIDTH = 34;
const DETAIL_WIDTH = 78;

function formatDuration(ms: number): string {
  return `${(ms / 1000).toFixed(1)}s`;
}

function padRight(value: string, width: number): string {
  return value.length >= width
    ? value
    : value + " ".repeat(width - value.length);
}

function truncate(value: string, width: number): string {
  return value.length > width ? `${value.slice(0, width - 3)}...` : value;
}

export class LiveDashboard {
  private readonly write: (text: string) => void;
  private readonly isTTY: boolean;
  private readonly slots: SlotState[];
  private readonly counters: Counters;
  private readonly concurrency: number;
  private linesDrawn = 0;
  private processed = 0;

  constructor(runtime: RuntimeAdapter, concurrency: number, totalJobs: number) {
    const terminal = runtime.terminal();
    this.write = (text: string) => terminal.stdout.write(text);
    this.isTTY = terminal.stdout.isTTY() && runtime.getEnv("TERM") !== "dumb";
    this.concurrency = concurrency;
    this.slots = Array.from({ length: concurrency }, () => null);
    this.counters = {
      total: totalJobs,
      ok: 0,
      skip: 0,
      empty: 0,
      unsupported: 0,
      err: 0,
    };
  }

  startSlot(slot: number, repo: string): void {
    this.slots[slot] = {
      repo,
      stage: "resolve",
      action: "git ref",
      startedAt: Date.now(),
    };
    this.redraw();
  }

  updateSlot(
    slot: number,
    info: { stage: string; action?: string; detail?: string },
  ): void {
    const current = this.slots[slot];
    if (!current) return;
    this.slots[slot] = {
      ...current,
      stage: info.stage || current.stage,
      action: info.action ?? current.action,
      detail: info.detail,
    };
    this.redraw();
  }

  completeSlot(slot: number, info: FinishRepoInfo): void {
    this.processed += 1;
    if (info.skipped) this.counters.skip += 1;
    else if (info.unsupported) this.counters.unsupported += 1;
    else if (info.files === 0) this.counters.empty += 1;
    else this.counters.ok += 1;

    const elapsed = Date.now() - (this.slots[slot]?.startedAt ?? Date.now());
    this.slots[slot] = null;

    if (this.isTTY) this.erase();
    this.write(`${this.formatCompletion(info, elapsed)}\n`);
    this.redraw();
  }

  failSlot(slot: number, info: FinishRepoInfo, lines: string[]): void {
    this.processed += 1;
    this.counters.err += 1;

    const elapsed = Date.now() - (this.slots[slot]?.startedAt ?? Date.now());
    const stage = this.slots[slot]?.stage ?? "";
    this.slots[slot] = null;

    if (this.isTTY) this.erase();
    for (const line of this.formatFailure(info, elapsed, stage, lines)) {
      this.write(`${line}\n`);
    }
    this.redraw();
  }

  finish(failedRepos: { repo: string; error: string }[]): void {
    if (this.isTTY) this.erase();

    const lines = [
      "",
      "------------------------------------------------------------",
      `Mirror complete  ${this.counters.total} repos`,
      `  synced:       ${this.counters.ok}`,
      `  skipped:      ${this.counters.skip}`,
      `  empty:        ${this.counters.empty}`,
      `  unsupported:  ${this.counters.unsupported}`,
      `  errors:       ${this.counters.err}`,
    ];

    if (failedRepos.length > 0) {
      lines.push("");
      lines.push("Failed repos:");
      for (const { repo, error } of failedRepos) {
        lines.push(`  ERR ${repo}: ${error}`);
      }
    }

    lines.push("------------------------------------------------------------");

    for (const line of lines) {
      this.write(`${line}\n`);
    }
  }

  private formatCompletion(info: FinishRepoInfo, elapsed: number): string {
    const duration = formatDuration(elapsed);
    if (info.skipped) return `. ${info.repo}  ${duration}`;
    if (info.unsupported) return `WARN ${info.repo}  unsupported  ${duration}`;
    if (info.files === 0) {
      return `WARN ${info.repo}  no files matched  ${duration}`;
    }
    return `OK ${info.repo}  files=${info.files} followed=${info.followed}  ${duration}`;
  }

  private formatFailure(
    info: FinishRepoInfo,
    elapsed: number,
    stage: string,
    lines: string[],
  ): string[] {
    const block = [
      `ERR ${info.repo}  ${info.error ?? "failed"}  ${formatDuration(elapsed)}`,
    ];
    if (stage) block.push(`  stage: ${stage}`);
    if (lines.length > 0) {
      block.push("  last output:");
      for (const line of lines) {
        block.push(`    ${truncate(line, DETAIL_WIDTH)}`);
      }
    }
    return block;
  }

  private redraw(): void {
    if (!this.isTTY) return;
    this.erase();
    const lines = this.buildBottomLines();
    this.write(lines.join("\n") + "\n");
    this.linesDrawn = lines.length;
  }

  private erase(): void {
    if (!this.isTTY || this.linesDrawn === 0) return;
    this.write("\r" + "\x1b[1A".repeat(this.linesDrawn) + "\x1b[J");
    this.linesDrawn = 0;
  }

  private buildBottomLines(): string[] {
    const lines = [
      `mirror  ${this.processed}/${this.counters.total}  ok=${this.counters.ok}  skip=${this.counters.skip}  empty=${this.counters.empty}  unsupported=${this.counters.unsupported}  err=${this.counters.err}`,
    ];

    for (let slot = 0; slot < this.concurrency; slot++) {
      const state = this.slots[slot];
      const prefix = `[${slot + 1}/${this.concurrency}]`;
      if (!state) {
        lines.push(`${prefix} . idle`);
        continue;
      }

      const elapsed = formatDuration(Date.now() - state.startedAt);
      const primary = `${prefix} > ${padRight(state.stage, STAGE_WIDTH)} ${
        truncate(state.repo, REPO_WIDTH)
      }  ${elapsed}`;
      lines.push(primary);
      if (state.action) {
        lines.push(`      ${truncate(state.action, DETAIL_WIDTH)}`);
      }

      if (state.detail && state.detail !== state.action) {
        lines.push(`      ${truncate(state.detail, DETAIL_WIDTH)}`);
      }
    }

    return lines;
  }
}

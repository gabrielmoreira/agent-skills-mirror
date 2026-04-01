/**
 * output.ts — Execution reporter with pluggable output sink.
 */

import type { RuntimeAdapter } from "./runtime.ts";
import type { FinishRepoInfo, FinishStageInfo, ReporterSink } from "./sink.ts";

export type RunResult = {
  stdout: string;
  stderr: string;
  code: number | null;
  signal: string | null;
  elapsed: number;
};

export type Reporter = {
  finishRepo(info: FinishRepoInfo): void;
  startStage(stage: string, action: string): void;
  finishStage(result: FinishStageInfo): void;
  info(msg: string): void;
  warn(msg: string): void;
  error(msg: string): void;
  run(opts: {
    cwd?: string;
    env?: Record<string, string>;
    suppressStderrPatterns?: RegExp[];
    silent?: boolean;
  }, command: string): Promise<RunResult>;
  execQuiet(
    argv: string[],
    options?: { cwd?: string; env?: Record<string, string> },
  ): Promise<void>;
};

function normalizeDetail(detail?: string | string[] | null): string[] {
  if (!detail) return [];
  const values = Array.isArray(detail) ? detail : [detail];
  return values.map((value) => value.trim()).filter(Boolean);
}

export function makeReporter(
  runtime: RuntimeAdapter,
  sink: ReporterSink,
): Reporter {
  async function run(
    runOpts: {
      cwd?: string;
      env?: Record<string, string>;
      suppressStderrPatterns?: RegExp[];
      silent?: boolean;
    },
    command: string,
  ): Promise<RunResult> {
    const shell = await runtime.shellPath();
    const silent = runOpts.silent === true;
    const startedAt = Date.now();
    let stdout = "";
    let stderr = "";

    const suppress = runOpts.suppressStderrPatterns ?? [
      /No such remote/i,
      /fatal: couldn't find remote ref/i,
    ];

    function shouldSuppress(line: string): boolean {
      return suppress.some((pattern) => pattern.test(line));
    }

    if (!silent) {
      sink.line(`$ ${command}`);
    }

    const { code, signal } = await runtime.spawnCapture(shell, command, {
      cwd: runOpts.cwd,
      env: runOpts.env,
      onStdout(text) {
        stdout += text;
        if (silent) return;
        for (
          const line of text.split("\n").map((value) => value.trimEnd()).filter(
            Boolean,
          )
        ) {
          sink.line(line);
        }
      },
      onStderr(text) {
        stderr += text;
        if (silent) return;
        for (
          const line of text.split("\n").map((value) => value.trimEnd()).filter(
            Boolean,
          )
        ) {
          if (!shouldSuppress(line)) {
            sink.line(line);
          }
        }
      },
    });

    return {
      stdout,
      stderr,
      code,
      signal,
      elapsed: Date.now() - startedAt,
    };
  }

  async function execQuiet(
    argv: string[],
    options?: { cwd?: string; env?: Record<string, string> },
  ): Promise<void> {
    const { code } = await runtime.spawnDirect(argv, options);
    if (code !== 0) {
      throw new Error(
        `Command failed: ${argv.join(" ")} (code=${code ?? "null"})`,
      );
    }
  }

  return {
    finishRepo(info) {
      sink.finishRepo?.(info);
    },

    startStage(stage, action) {
      sink.startStage?.(stage, action);
    },

    finishStage(result) {
      const details = normalizeDetail(result.detail);
      for (const line of details) {
        sink.line(line);
      }
      if (!result.ok) {
        if (result.code !== undefined && result.code !== null) {
          sink.line(`exit=${result.code}`);
        }
        if (result.error) {
          sink.line(result.error);
        }
        if (!result.error && details.length === 0) {
          sink.line("stage failed");
        }
      }
      sink.finishStage?.(result);
    },

    info(msg) {
      sink.line(msg);
    },

    warn(msg) {
      sink.line(`warning: ${msg}`);
    },

    error(msg) {
      sink.line(`error: ${msg}`);
    },

    run,
    execQuiet,
  };
}

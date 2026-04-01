/**
 * Thin re-export of the `debug` package so every module imports from one
 * place and the namespace prefix stays consistent.
 *
 * Usage:
 *   import { createDebug } from './debug.ts';
 *   const dbg = createDebug('mirror:scope');
 *   dbg('resolved %s → %O', path, value);
 *
 * Enable at runtime:
 *   DEBUG=mirror:*          — all mirror namespaces
 *   DEBUG=engine:*          — engine step execution
 *   DEBUG=mirror:*,engine:* — both
 */
// deno-lint-ignore-file no-explicit-any
import createDebugFactory from 'debug';

export type DebugFn = (...args: any[]) => void;

export function createDebug(namespace: string): DebugFn {
  return createDebugFactory(namespace) as unknown as DebugFn;
}

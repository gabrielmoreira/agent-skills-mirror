import { AsyncLocalStorage } from "node:async_hooks";
import { readProjectEnvId } from "./project-config.js";

/**
 * Where this resolution got its env id.
 * The first four values are already in shipped queries. Do not rename them.
 * `default` stays `default` (an empty result, not a rename to `unresolved`).
 */
export const ENV_SOURCES = [
    "cloudBaseOptions",
    "process.env.CLOUDBASE_ENV_ID",
    "envManager.cachedEnvId",
    "project",
    "login_state",
    "auto_bound",
    "default",
] as const;

export type EnvSource = (typeof ENV_SOURCES)[number];

export type EnvBinding = {
    envId: string | null;
    source: EnvSource;
};

export type EnvSlot = {
    binding: EnvBinding | null;
};

const envCall = new AsyncLocalStorage<EnvSlot>();

function isReportableEnvId(envId: string | null | undefined): envId is string {
    return !!envId && envId !== "local" && envId !== "unknown";
}

/** Write into the current slot. Outside a slot this is a no-op and does not touch process globals. */
export function noteEnvBinding(binding: EnvBinding): void {
    const slot = envCall.getStore();
    if (!slot || binding.source === "default" || !isReportableEnvId(binding.envId)) {
        return;
    }
    slot.binding = { envId: binding.envId, source: binding.source };
}

export function clearEnvBinding(): void {
    const slot = envCall.getStore();
    if (slot) {
        slot.binding = null;
    }
}

export function hasEnvSlot(): boolean {
    return envCall.getStore() !== undefined;
}

export function readReportedEnv(): { envId: string; envIdSource: EnvSource } {
    const binding = envCall.getStore()?.binding;
    if (!binding || binding.source === "default" || !isReportableEnvId(binding.envId)) {
        return { envId: "unknown", envIdSource: "default" };
    }
    return { envId: binding.envId, envIdSource: binding.source };
}

/**
 * Env id shown on the start page, the usage card, and confirmation text.
 * An explicit envId on this call wins, matching the resolver ladder.
 * Otherwise the current slot (login state, project, cache, or env var already noted).
 * Does not read process.env or the manager cache: on a hosted request those belong to the server machine.
 */
export function readDisplayedEnvId(explicitEnvId?: string | null): string | null {
    if (isReportableEnvId(explicitEnvId)) {
        return explicitEnvId;
    }
    const reported = readReportedEnv();
    if (reported.envIdSource !== "default") {
        return reported.envId;
    }
    return null;
}

export function runWithEnvSlot<T>(slot: EnvSlot, fn: () => T): T {
    return envCall.run(slot, fn);
}

/** One fresh slot. Tests and any caller that must not share another request's binding. */
export function runInEnvSlot<T>(fn: () => T): T {
    return envCall.run({ binding: null }, fn);
}

/**
 * Read-only snapshot for process start. Does not call setEnvId and does not list envs.
 * `cachedEnvId` is passed in so this module does not import the manager (that import cycles).
 */
export function peekLocalEnvBinding(input: {
    cachedEnvId?: string | null;
    loginEnvId?: string | null;
}): EnvBinding {
    if (isReportableEnvId(input.cachedEnvId)) {
        return { envId: input.cachedEnvId, source: "envManager.cachedEnvId" };
    }
    const fromEnv = process.env.CLOUDBASE_ENV_ID;
    if (isReportableEnvId(fromEnv)) {
        return { envId: fromEnv, source: "process.env.CLOUDBASE_ENV_ID" };
    }
    const projectEnvId = readProjectEnvId();
    if (isReportableEnvId(projectEnvId)) {
        return { envId: projectEnvId, source: "project" };
    }
    if (isReportableEnvId(input.loginEnvId)) {
        return { envId: input.loginEnvId, source: "login_state" };
    }
    return { envId: null, source: "default" };
}

#!/usr/bin/env node

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const TOKEN_PATH = path.join(os.homedir(), ".openloomi", "token");
const BASE_URLS = process.env.OPENLOOMI_BASE_URL
  ? [process.env.OPENLOOMI_BASE_URL]
  : ["http://localhost:3515", "http://localhost:3415", "http://localhost:3414"];
const USAGE = `Usage: openloomi-goals <command>

Commands:
  list [runtime-session-id]
  get <runtime-session-id> <goal-id>
`;

function authToken() {
  try {
    return Buffer.from(
      fs.readFileSync(TOKEN_PATH, "utf8").trim(),
      "base64",
    ).toString("utf8");
  } catch {
    return null;
  }
}

class HttpResponseError extends Error {}

async function requestAt(baseUrl, endpoint) {
  const token = authToken();
  const response = await fetch(new URL(endpoint, baseUrl), {
    headers: {
      Accept: "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    signal: AbortSignal.timeout(10_000),
  });
  const text = await response.text();
  let result;
  try {
    result = text ? JSON.parse(text) : {};
  } catch {
    result = { error: text || `HTTP ${response.status}` };
  }
  if (!response.ok) {
    const detail = result.cause || result.error || result.code;
    throw new HttpResponseError(
      detail
        ? typeof detail === "string"
          ? detail
          : JSON.stringify(detail)
        : `HTTP ${response.status}`,
    );
  }
  return result;
}

async function apiRequest(endpoint) {
  let lastError;
  for (const baseUrl of BASE_URLS) {
    try {
      return await requestAt(baseUrl, endpoint);
    } catch (error) {
      lastError = error;
      if (error instanceof HttpResponseError) throw error;
    }
  }
  throw lastError ?? new Error("OpenLoomi is not running");
}

function required(value, name) {
  if (!value) throw new Error(`${name} is required`);
  return value;
}

function detailUrl(runtimeSessionId, goalId) {
  return `/api/agent-goals/${encodeURIComponent(
    goalId,
  )}?runtimeSessionId=${encodeURIComponent(runtimeSessionId)}`;
}

async function main() {
  const [command = "list", sessionArg, goalArg] = process.argv.slice(2);
  if (["help", "--help", "-h"].includes(command)) {
    process.stdout.write(USAGE);
    return;
  }

  let result;
  if (command === "list") {
    result = sessionArg
      ? await apiRequest(
          `/api/agent-goals?runtimeSessionId=${encodeURIComponent(sessionArg)}`,
        )
      : await apiRequest("/api/agent-goals/active");
  } else if (command === "get") {
    result = await apiRequest(
      detailUrl(
        required(sessionArg, "runtime-session-id"),
        required(goalArg, "goal-id"),
      ),
    );
  } else {
    throw new Error(`unknown command: ${command}`);
  }
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

main().catch((error) => {
  process.stderr.write(
    `${error instanceof Error ? error.message : String(error)}\n`,
  );
  process.exitCode = 1;
});

#!/usr/bin/env node

const DEFAULT_API_BASE = 'https://openapi.felo.ai';
const DEFAULT_INTERVAL_SEC = 10;
const DEFAULT_MAX_WAIT_SEC = 1800;
const DEFAULT_TIMEOUT_SEC = 60;
const MAX_RETRIES = 2;
const RETRY_BASE_MS = 1000;

function usage() {
  console.error(
    [
      'Usage:',
      '  node felo-slides/scripts/run_ppt_task.mjs --query "your prompt" [options]',
      '',
      'Options:',
      '  --query <text>        PPT prompt (required)',
      '  --interval <seconds>  Poll interval, default 10',
      '  --max-wait <seconds>  Max wait time, default 1800',
      '  --timeout <seconds>   Request timeout, default 60',
      '  --json                Print JSON output',
      '  --verbose             Print polling status to stderr',
      '  --help                Show this help',
    ].join('\n')
  );
}

function parseArgs(argv) {
  const out = {
    query: '',
    intervalSec: DEFAULT_INTERVAL_SEC,
    maxWaitSec: DEFAULT_MAX_WAIT_SEC,
    timeoutSec: DEFAULT_TIMEOUT_SEC,
    json: false,
    verbose: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === '--help' || a === '-h') {
      out.help = true;
    } else if (a === '--json') {
      out.json = true;
    } else if (a === '--verbose' || a === '-v') {
      out.verbose = true;
    } else if (a === '--query') {
      out.query = argv[i + 1] ?? '';
      i += 1;
    } else if (a === '--interval') {
      out.intervalSec = Number.parseInt(argv[i + 1] ?? '', 10);
      i += 1;
    } else if (a === '--max-wait') {
      out.maxWaitSec = Number.parseInt(argv[i + 1] ?? '', 10);
      i += 1;
    } else if (a === '--timeout') {
      out.timeoutSec = Number.parseInt(argv[i + 1] ?? '', 10);
      i += 1;
    } else if (!a.startsWith('-') && !out.query) {
      out.query = a;
    }
  }

  if (!Number.isFinite(out.intervalSec) || out.intervalSec <= 0) out.intervalSec = DEFAULT_INTERVAL_SEC;
  if (!Number.isFinite(out.maxWaitSec) || out.maxWaitSec <= 0) out.maxWaitSec = DEFAULT_MAX_WAIT_SEC;
  if (!Number.isFinite(out.timeoutSec) || out.timeoutSec <= 0) out.timeoutSec = DEFAULT_TIMEOUT_SEC;
  return out;
}

function normalizeStatus(v) {
  return String(v ?? '').trim().toUpperCase();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function createError(message, details = {}) {
  const err = new Error(message);
  Object.assign(err, details);
  return err;
}

function getMessage(payload) {
  return (
    payload?.message ||
    payload?.error ||
    payload?.msg ||
    payload?.code ||
    'Unknown error'
  );
}

function isApiError(payload) {
  const status = payload?.status;
  const code = payload?.code;
  if (typeof status === 'string' && status.toLowerCase() === 'error') return true;
  if (typeof code === 'string' && code && code.toUpperCase() !== 'OK') return true;
  return false;
}

function isRetryableHttpStatus(status) {
  return status === 429 || status >= 500;
}

function getRequestId(payload) {
  return payload?.request_id || payload?.requestId || null;
}

function formatErrorMessage(prefix, payload) {
  const parts = [prefix];
  const code = payload?.code;
  const requestId = getRequestId(payload);
  if (code) parts.push(`code=${code}`);
  if (requestId) parts.push(`request_id=${requestId}`);
  return parts.join(' | ');
}

function buildSuccessPayload(taskId, taskStatus, urls, createData, historicalData) {
  return {
    task_id: taskId,
    task_status: taskStatus,
    ppt_url: urls.pptUrl || null,
    live_doc_url: urls.liveDocUrl || null,
    livedoc_short_id:
      createData.livedoc_short_id ?? historicalData.live_doc_short_id ?? historicalData.livedoc_short_id ?? null,
    ppt_business_id: createData.ppt_business_id ?? null,
  };
}

async function fetchJson(url, init, timeoutMs) {
  let lastError;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(url, { ...init, signal: controller.signal });
      let body = {};
      try {
        body = await res.json();
      } catch {
        body = {};
      }

      if (!res.ok) {
        const error = createError(
          formatErrorMessage(`HTTP ${res.status}: ${getMessage(body)}`, body),
          {
            httpStatus: res.status,
            code: body?.code ?? null,
            requestId: getRequestId(body),
          }
        );
        if (attempt < MAX_RETRIES && isRetryableHttpStatus(res.status)) {
          lastError = error;
          await sleep(RETRY_BASE_MS * Math.pow(2, attempt));
          continue;
        }
        throw error;
      }
      if (isApiError(body)) {
        throw createError(formatErrorMessage(getMessage(body), body), {
          code: body?.code ?? null,
          requestId: getRequestId(body),
        });
      }
      return body;
    } catch (err) {
      if (err?.name === 'AbortError') {
        lastError = createError(`Request timed out after ${timeoutMs / 1000}s`);
      } else {
        lastError = err;
      }
      if (attempt < MAX_RETRIES && (err?.name === 'AbortError' || err instanceof TypeError)) {
        await sleep(RETRY_BASE_MS * Math.pow(2, attempt));
        continue;
      }
      throw lastError;
    } finally {
      clearTimeout(timer);
    }
  }

  throw lastError ?? new Error('Unknown request error');
}

function extractTaskUrls(historicalData, createData) {
  const pptUrl = historicalData?.ppt_url || '';
  const liveDocUrl =
    historicalData?.live_doc_url ||
    (historicalData?.live_doc_short_id || historicalData?.livedoc_short_id || createData?.livedoc_short_id
      ? `https://felo.ai/livedoc/${historicalData?.live_doc_short_id || historicalData?.livedoc_short_id || createData?.livedoc_short_id}`
      : '');
  return {
    pptUrl,
    liveDocUrl,
    displayUrl: pptUrl || liveDocUrl,
  };
}

async function createTask(apiKey, apiBase, query, timeoutMs) {
  const payload = await fetchJson(
    `${apiBase}/v2/ppts`,
    {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    },
    timeoutMs
  );
  const data = payload?.data ?? {};
  if (!data.task_id) {
    throw new Error('Unexpected response: missing task_id');
  }
  return data;
}

async function queryHistorical(apiKey, apiBase, taskId, timeoutMs) {
  const payload = await fetchJson(
    `${apiBase}/v2/tasks/${encodeURIComponent(taskId)}/historical`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
    },
    timeoutMs
  );
  return payload?.data ?? {};
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    process.exit(0);
  }
  if (!args.query) {
    usage();
    process.exit(1);
  }

  const apiKey = process.env.FELO_API_KEY?.trim();
  if (!apiKey) {
    console.error('ERROR: FELO_API_KEY not set');
    process.exit(1);
  }

  const apiBase = (process.env.FELO_API_BASE?.trim() || DEFAULT_API_BASE).replace(/\/$/, '');
  const timeoutMs = args.timeoutSec * 1000;
  const intervalMs = args.intervalSec * 1000;
  const maxWaitMs = args.maxWaitSec * 1000;

  const createData = await createTask(apiKey, apiBase, args.query, timeoutMs);
  const taskId = createData.task_id;
  if (args.verbose || args.json) {
    console.error(`Task ID: ${taskId}`);
  }

  const startAt = Date.now();
  let lastStatus = '';

  while (Date.now() - startAt <= maxWaitMs) {
    const historicalData = await queryHistorical(apiKey, apiBase, taskId, timeoutMs);
    const taskStatus = normalizeStatus(historicalData.task_status || historicalData.status);
    const urls = extractTaskUrls(historicalData, createData);
    lastStatus = taskStatus || 'UNKNOWN';

    if (args.verbose) {
      const elapsedSec = Math.floor((Date.now() - startAt) / 1000);
      console.error(`[${elapsedSec}s] Status: ${lastStatus}`);
    }

    if (taskStatus === 'COMPLETED' || taskStatus === 'SUCCESS') {
      if (!urls.displayUrl) {
        throw new Error('Task completed but no ppt_url/live_doc_url is available');
      }
      const successData = buildSuccessPayload(taskId, taskStatus, urls, createData, historicalData);
      if (args.json) {
        console.log(
          JSON.stringify(
            {
              status: 'ok',
              data: successData,
            },
            null,
            2
          )
        );
      } else {
        console.log(urls.displayUrl);
      }
      return;
    }

    if (taskStatus === 'FAILED' || taskStatus === 'ERROR') {
      const errorMessage = historicalData?.error_message || '';
      const detail = errorMessage ? `; error_message=${errorMessage}` : '';
      throw createError(`Task ${taskId} finished with status: ${taskStatus}${detail}`, {
        taskId,
        taskStatus,
        errorMessage,
      });
    }

    await sleep(intervalMs);
  }

  throw createError(`Timed out after ${args.maxWaitSec}s. Last status: ${lastStatus || 'UNKNOWN'}`, {
    taskId,
    taskStatus: lastStatus || 'UNKNOWN',
  });
}

main().catch((err) => {
  console.error(`ERROR: ${err?.message || err}`);
  process.exit(1);
});

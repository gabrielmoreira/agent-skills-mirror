#!/usr/bin/env node
'use strict';

/**
 * genspark-claw MCP server (stdio transport, zero dependencies).
 *
 * Speaks newline-delimited JSON-RPC 2.0 over stdin/stdout, implementing the
 * Model Context Protocol handshake plus three tools that expose this skill
 * pack to any MCP-compliant client (Claude Desktop, Cursor, Windsurf, …).
 *
 * Wire it up in claude_desktop_config.json:
 * {
 *   "mcpServers": {
 *     "genspark-claw": {
 *       "command": "node",
 *       "args": ["/path/to/genspark-claw/mcp/mcp-server.js"]
 *     }
 *   }
 * }
 *
 * Or run the self-test:  node mcp/mcp-server.js --test
 */

const readline = require('node:readline');
const { listBundledSkills, findSkill, validateTarget, version } = require('../src/index');

const PROTOCOL_VERSION = '2024-11-05';
const SERVER_INFO = { name: 'genspark-claw', version };

const TOOLS = [
  {
    name: 'list_skills',
    description: 'List all agent skills bundled in the genspark-claw pack, with name, version and description.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
  {
    name: 'get_skill',
    description: 'Get the full SKILL.md instructions for one bundled skill by name, ready to follow or install.',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Skill name, e.g. "super-research"' },
      },
      required: ['name'],
      additionalProperties: false,
    },
  },
  {
    name: 'validate_skill',
    description: 'Validate a SKILL.md file (or a directory of skills) against the cross-runtime skill convention.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Absolute path to a SKILL.md file or a skills directory' },
      },
      required: ['path'],
      additionalProperties: false,
    },
  },
];

function textResult(text) {
  return { content: [{ type: 'text', text }] };
}

function callTool(name, args) {
  switch (name) {
    case 'list_skills': {
      const skills = listBundledSkills();
      return textResult(JSON.stringify(skills.map((s) => ({
        name: s.name,
        version: s.version,
        description: s.description,
        compatibility: s.compatibility,
        triggers: s.triggers,
      })), null, 2));
    }
    case 'get_skill': {
      const skill = findSkill(args && args.name);
      if (!skill) {
        return { content: [{ type: 'text', text: `Unknown skill "${args && args.name}". Use list_skills to see available skills.` }], isError: true };
      }
      return textResult(skill.raw);
    }
    case 'validate_skill': {
      if (!args || typeof args.path !== 'string') {
        return { content: [{ type: 'text', text: 'Missing required argument: path' }], isError: true };
      }
      const results = validateTarget(args.path);
      return textResult(JSON.stringify(results, null, 2));
    }
    default:
      return { content: [{ type: 'text', text: `Unknown tool "${name}"` }], isError: true };
  }
}

function handleMessage(msg) {
  const { id, method, params } = msg;

  // Notifications (no id) need no response.
  if (id === undefined || id === null) return null;

  switch (method) {
    case 'initialize':
      return {
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: PROTOCOL_VERSION,
          capabilities: { tools: {} },
          serverInfo: SERVER_INFO,
        },
      };
    case 'ping':
      return { jsonrpc: '2.0', id, result: {} };
    case 'tools/list':
      return { jsonrpc: '2.0', id, result: { tools: TOOLS } };
    case 'tools/call': {
      try {
        const result = callTool(params && params.name, (params && params.arguments) || {});
        return { jsonrpc: '2.0', id, result };
      } catch (err) {
        return {
          jsonrpc: '2.0',
          id,
          result: { content: [{ type: 'text', text: `Tool error: ${err.message}` }], isError: true },
        };
      }
    }
    default:
      return {
        jsonrpc: '2.0',
        id,
        error: { code: -32601, message: `Method not found: ${method}` },
      };
  }
}

function start() {
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  rl.on('line', (line) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    let msg;
    try {
      msg = JSON.parse(trimmed);
    } catch {
      process.stdout.write(`${JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } })}\n`);
      return;
    }
    const response = handleMessage(msg);
    if (response) process.stdout.write(`${JSON.stringify(response)}\n`);
  });
}

function selfTest() {
  const init = handleMessage({ jsonrpc: '2.0', id: 1, method: 'initialize', params: {} });
  const list = handleMessage({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
  const call = handleMessage({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'list_skills', arguments: {} } });
  const ok = init.result.serverInfo.name === 'genspark-claw'
    && list.result.tools.length === TOOLS.length
    && !call.result.isError
    && call.result.content[0].text.includes('super-research');
  console.log(ok ? 'MCP self-test passed: initialize, tools/list, tools/call all OK.' : 'MCP self-test FAILED.');
  process.exit(ok ? 0 : 1);
}

if (require.main === module) {
  if (process.argv.includes('--test')) selfTest();
  else start();
}

module.exports = { start, handleMessage, TOOLS, PROTOCOL_VERSION };

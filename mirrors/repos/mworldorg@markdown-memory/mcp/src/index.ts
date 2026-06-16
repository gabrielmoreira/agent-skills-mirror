#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { scan } from './scan.js';
import { loadPatterns } from './patterns.js';

const patterns = loadPatterns();

const server = new McpServer({ name: 'mm-mcp', version: '0.1.0' });

server.registerTool(
  'mm_secret_scan',
  {
    title: 'Secret scanner',
    description:
      'Детерминированно сканирует текст на секреты по канону config/secret-patterns.json. ' +
      'Возвращает только классы (A — высокоточные, B — warn-only) и счётчики. ' +
      'НИКОГДА не возвращает сырое значение секрета.',
    inputSchema: { text: z.string() },
  },
  async ({ text }) => {
    const result = scan(text, patterns);
    const aFindings = result.findings.filter((f) => f.class === 'A');

    let summary: string;
    if (aFindings.length > 0 || result.classBCount > 0) {
      const parts: string[] = [];
      if (aFindings.length > 0) {
        parts.push(`🔒 Класс A: ${aFindings.map((f) => `${f.id}×${f.count}`).join(', ')}`);
      }
      if (result.classBCount > 0) {
        parts.push(`⚠️ Класс B (warn): ${result.classBCount}`);
      }
      summary = parts.join('; ');
    } else {
      summary = '🔒 секретов не найдено';
    }

    return {
      content: [{ type: 'text', text: summary }],
      structuredContent: result as unknown as Record<string, unknown>,
    };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);

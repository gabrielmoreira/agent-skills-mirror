#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import puppeteer, { Browser, Page, ConsoleMessage, HTTPRequest } from 'puppeteer';
import fs from 'fs-extra';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { createHash, randomUUID } from 'crypto';
import { glob } from 'glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Project root is two directories up from build/index.js (mcp/build -> mcp -> workspace)
const projectRoot = path.resolve(__dirname, '..', '..');
const SCREENSHOTS_DIR = path.resolve(projectRoot, 'mcp', 'screenshots');

interface DevToolsArgs {
  url?: string;
  selector?: string;
  filePath?: string;
  content?: string;
  command?: string;
  cwd?: string;
  timeout?: number;
  width?: number;
  height?: number;
  format?: string;
  query?: string;
  pattern?: string;
  port?: number;
  endpoint?: string;
  value?: string;
  x?: number;
  y?: number;
  ms?: number;
  algorithm?: string;
  fix?: boolean;
  strict?: boolean;
  watch?: boolean;
  coverage?: boolean;
  quality?: number;
  fullPage?: boolean;
  includeAttributes?: boolean;
  clearAfter?: boolean;
  resourceTypes?: string[];
  limit?: number;
  recursive?: boolean;
  basePath?: string;
  source?: string;
  destination?: string;
}

interface NetworkRequestInfo {
  url: string;
  method: string;
  type: string;
  headers: Record<string, string>;
}

// Security: Path Traversal Protection
function safePath(filePath: string): string {
  if (!filePath) {
    throw new McpError(ErrorCode.InvalidParams, 'Path is required');
  }
  const resolved = path.resolve(projectRoot, filePath);
  const normalizedRoot = path.normalize(projectRoot);
  const normalizedResolved = path.normalize(resolved);
  
  if (normalizedResolved === normalizedRoot) {
    return normalizedResolved;
  }
  
  const rootPrefix = normalizedRoot.endsWith(path.sep) ? normalizedRoot : normalizedRoot + path.sep;
  
  if (!normalizedResolved.startsWith(rootPrefix)) {
    throw new McpError(
      ErrorCode.InvalidParams,
      `Access denied: Path '${filePath}' resolves outside the workspace directory`
    );
  }
  return normalizedResolved;
}

// Security: Protocol Restriction
function validateUrl(urlString: string): string {
  try {
    const parsed = new URL(urlString);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      throw new McpError(
        ErrorCode.InvalidParams,
        `Access denied: Protocol '${parsed.protocol}' is not allowed. Only http: and https: URLs are supported.`
      );
    }
    return urlString;
  } catch (error) {
    if (error instanceof McpError) throw error;
    throw new McpError(ErrorCode.InvalidParams, `Invalid URL format: ${urlString}`);
  }
}

// Security: Command Whitelist and Injection Protection
const ALLOWED_BINARIES = new Set(['pnpm', 'npm', 'npx', 'git', 'vitest', 'eslint', 'tsc']);

function sanitizeAndValidateCommand(command: string): string {
  const trimmed = command.trim();
  if (!trimmed) {
    throw new McpError(ErrorCode.InvalidParams, 'Command is empty');
  }
  
  // Block shell chaining, redirection, and variable expansion characters
  const dangerousChars = [';', '&', '|', '$', '(', ')', '>', '<', '\n', '\r', '`'];
  for (const char of dangerousChars) {
    if (trimmed.includes(char)) {
      throw new McpError(
        ErrorCode.InvalidParams,
        `Access denied: Command contains forbidden shell character '${char}'`
      );
    }
  }
  
  // Validate that the base executable is whitelisted
  const firstWord = trimmed.split(/\s+/)[0];
  const baseBinary = path.basename(firstWord).replace(/\.(cmd|exe|bat|sh)$/i, '');
  
  if (!ALLOWED_BINARIES.has(baseBinary)) {
    throw new McpError(
      ErrorCode.InvalidParams,
      `Access denied: Command binary '${baseBinary}' is not in the whitelist. Allowed: ${Array.from(ALLOWED_BINARIES).join(', ')}`
    );
  }
  
  return trimmed;
}

class DevToolsServer {
  private server: Server;
  private browser: Browser | null = null;
  private activePage: Page | null = null;
  private consoleLogs: string[] = [];
  private networkRequests: NetworkRequestInfo[] = [];

  constructor() {
    this.server = new Server(
      {
        name: 'devtools-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    this.setupResourceHandlers();
    this.setupToolHandlers();

    this.server.onerror = (error) => console.error('[MCP Error]', error);
    
    const handleExit = async () => {
      await this.cleanup();
      process.exit(0);
    };
    
    process.on('SIGINT', handleExit);
    process.on('SIGTERM', handleExit);
  }

  private async getBrowser(): Promise<Browser> {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--window-size=1920,1080'
        ],
        defaultViewport: { width: 1920, height: 1080 }
      });
    }
    return this.browser;
  }

  private async getPage(): Promise<Page> {
    const browser = await this.getBrowser();
    if (!this.activePage) {
      this.activePage = await browser.newPage();
      await this.activePage.setViewport({ width: 1920, height: 1080 });

      // Continuously capture console logs in memory
      this.activePage.on('console', (msg: ConsoleMessage) => {
        this.consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
        if (this.consoleLogs.length > 1000) {
          this.consoleLogs.shift();
        }
      });

      // Continuously capture network requests in memory
      this.activePage.on('request', (req: HTTPRequest) => {
        this.networkRequests.push({
          url: req.url(),
          method: req.method(),
          type: req.resourceType(),
          headers: req.headers(),
        });
        if (this.networkRequests.length > 2000) {
          this.networkRequests.shift();
        }
      });
    }
    return this.activePage;
  }

  private async cleanup(): Promise<void> {
    try {
      this.consoleLogs = [];
      this.networkRequests = [];
      if (this.activePage) {
        await this.activePage.close().catch(() => {});
        this.activePage = null;
      }
      if (this.browser) {
        await this.browser.close().catch(() => {});
        this.browser = null;
      }
    } catch {
      // ignore cleanup errors
    }
  }

  private setupResourceHandlers() {
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 'devtools://screenshots/latest',
          name: 'Latest screenshot taken',
          mimeType: 'image/png',
          description: 'The most recent screenshot captured by the screenshot tool',
        },
        {
          uri: 'devtools://console/logs',
          name: 'Browser console logs',
          mimeType: 'application/json',
          description: 'Captured browser console logs from the active page',
        },
        {
          uri: 'devtools://page/dom',
          name: 'Current page DOM structure',
          mimeType: 'text/html',
          description: 'Full HTML DOM of the currently active page',
        },
      ],
    }));

    this.server.setRequestHandler(
      ReadResourceRequestSchema,
      async (request) => {
        const uri = request.params.uri;

        if (uri === 'devtools://screenshots/latest') {
          if (!await fs.pathExists(SCREENSHOTS_DIR)) {
            throw new McpError(ErrorCode.InvalidRequest, 'No screenshots available');
          }
          const files = await fs.readdir(SCREENSHOTS_DIR);
          const pngFiles = files
            .filter((f) => f.endsWith('.png'))
            .sort()
            .reverse();

          if (pngFiles.length === 0) {
            throw new McpError(ErrorCode.InvalidRequest, 'No screenshots available');
          }

          const latest = path.join(SCREENSHOTS_DIR, pngFiles[0]);
          const data = await fs.readFile(latest);
          return {
            contents: [
              {
                uri,
                mimeType: 'image/png',
                blob: data.toString('base64'),
              },
            ],
          };
        }

        if (uri === 'devtools://console/logs') {
          return {
            contents: [
              {
                uri,
                mimeType: 'application/json',
                text: JSON.stringify({ logs: this.consoleLogs }, null, 2),
              },
            ],
          };
        }

        if (uri === 'devtools://page/dom') {
          if (!this.activePage) {
            throw new McpError(
              ErrorCode.InvalidRequest,
              'No active page. Navigate to a URL first.'
            );
          }
          const html = await this.activePage.content();
          return {
            contents: [
              {
                uri,
                mimeType: 'text/html',
                text: html,
              },
            ],
          };
        }

        throw new McpError(
          ErrorCode.InvalidRequest,
          `Unknown resource: ${uri}`
        );
      }
    );
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        // ========== BROWSER NAVIGATION TOOLS ==========
        {
          name: 'browse_navigate',
          description: 'Navigate to an HTTP/HTTPS URL and wait for the page to load',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: 'URL to navigate to (must start with http:// or https://)',
              },
              timeout: {
                type: 'number',
                description: 'Navigation timeout in milliseconds (default: 30000)',
                default: 30000,
              },
            },
            required: ['url'],
          },
        },
        {
          name: 'browse_click',
          description: 'Click on an element on the page using CSS selector',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS selector for the element to click',
              },
            },
            required: ['selector'],
          },
        },
        {
          name: 'browse_type',
          description: 'Type text into an input field',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS selector for the input element',
              },
              content: {
                type: 'string',
                description: 'Text to type into the field',
              },
            },
            required: ['selector', 'content'],
          },
        },
        {
          name: 'browse_select',
          description: 'Select an option from a dropdown/select element by value',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS selector for the select element',
              },
              value: {
                type: 'string',
                description: 'Value to select',
              },
            },
            required: ['selector', 'value'],
          },
        },
        {
          name: 'browse_hover',
          description: 'Hover over an element on the page',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS selector for the element to hover over',
              },
            },
            required: ['selector'],
          },
        },
        {
          name: 'browse_scroll',
          description: 'Scroll the page by a specified amount of pixels',
          inputSchema: {
            type: 'object',
            properties: {
              x: {
                type: 'number',
                description: 'Horizontal scroll amount in pixels',
                default: 0,
              },
              y: {
                type: 'number',
                description: 'Vertical scroll amount in pixels',
                default: 0,
              },
            },
          },
        },
        {
          name: 'browse_go_back',
          description: 'Navigate back in browser history',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'browse_go_forward',
          description: 'Navigate forward in browser history',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'browse_reload',
          description: 'Reload the current browser page',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },

        // ========== INSPECTION TOOLS ==========
        {
          name: 'inspect_dom',
          description: 'Get the full DOM content of the current page or a specific element',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'Optional CSS selector to inspect a specific element',
              },
              includeAttributes: {
                type: 'boolean',
                description: 'Include element attributes in output',
                default: true,
              },
            },
          },
        },
        {
          name: 'inspect_element',
          description: 'Get detailed details about a specific element (position, size, attributes, text)',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS selector for the element to inspect',
              },
            },
            required: ['selector'],
          },
        },
        {
          name: 'inspect_console_logs',
          description: 'Capture and return console logs from the browser',
          inputSchema: {
            type: 'object',
            properties: {
              clearAfter: {
                type: 'boolean',
                description: 'Clear logs buffer after capturing',
                default: true,
              },
            },
          },
        },
        {
          name: 'inspect_network_requests',
          description: 'Capture network requests made by the page',
          inputSchema: {
            type: 'object',
            properties: {
              resourceTypes: {
                type: 'array',
                items: { type: 'string' },
                description: 'Filter by resource types (xhr, fetch, document, stylesheet, script, image, etc.)',
              },
              limit: {
                type: 'number',
                description: 'Maximum number of requests to return',
                default: 50,
              },
            },
          },
        },
        {
          name: 'inspect_cookies',
          description: 'Get all cookies for the current page',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'inspect_local_storage',
          description: 'Get localStorage data for the current page',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'inspect_session_storage',
          description: 'Get sessionStorage data for the current page',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'inspect_metrics',
          description: 'Get page performance metrics (load time, DOM nodes, etc.)',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },

        // ========== SCREENSHOT TOOLS ==========
        {
          name: 'screenshot_page',
          description: 'Take a screenshot of the current page or a specific element',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'Optional CSS selector to screenshot only a specific element',
              },
              format: {
                type: 'string',
                description: 'Image format: png, jpeg, webp (default: png)',
                enum: ['png', 'jpeg', 'webp'],
                default: 'png',
              },
              quality: {
                type: 'number',
                description: 'Image quality (1-100, only for jpeg/webp)',
                default: 80,
              },
              fullPage: {
                type: 'boolean',
                description: 'Capture full scrollable page (default: false)',
                default: false,
              },
            },
          },
        },
        {
          name: 'screenshot_element',
          description: 'Take a screenshot of a specific element on the page',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS selector for the element to screenshot',
              },
              format: {
                type: 'string',
                description: 'Image format: png, jpeg, webp',
                enum: ['png', 'jpeg', 'webp'],
                default: 'png',
              },
            },
            required: ['selector'],
          },
        },

        // ========== FILE SYSTEM TOOLS (Restricted to workspace) ==========
        {
          name: 'file_read',
          description: 'Read the contents of a file in the workspace (read sandboxed)',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Path to the file to read (relative to workspace root)',
              },
            },
            required: ['filePath'],
          },
        },
        {
          name: 'file_write',
          description: 'Write content to a file in the workspace (write sandboxed)',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Path to the file to write (relative to workspace root)',
              },
              content: {
                type: 'string',
                description: 'Content to write to the file',
              },
            },
            required: ['filePath', 'content'],
          },
        },
        {
          name: 'file_search',
          description: 'Search for files matching a glob pattern in the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              pattern: {
                type: 'string',
                description: 'Glob pattern to search (e.g., "**/*.ts")',
              },
              basePath: {
                type: 'string',
                description: 'Base path to search from (relative to workspace root, default: workspace root)',
              },
            },
            required: ['pattern'],
          },
        },
        {
          name: 'file_delete',
          description: 'Delete a file or directory inside the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Path to the file/directory to delete (relative to workspace root)',
              },
              recursive: {
                type: 'boolean',
                description: 'Delete directories recursively',
                default: false,
              },
            },
            required: ['filePath'],
          },
        },
        {
          name: 'file_info',
          description: 'Get metadata information about a file or directory in the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Path to the file or directory (relative to workspace root)',
              },
            },
            required: ['filePath'],
          },
        },
        {
          name: 'file_list_dir',
          description: 'List contents of a directory in the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Path to the directory (relative to workspace root)',
              },
              recursive: {
                type: 'boolean',
                description: 'List recursively',
                default: false,
              },
            },
            required: ['filePath'],
          },
        },
        {
          name: 'file_copy',
          description: 'Copy a file from source to destination inside the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              source: {
                type: 'string',
                description: 'Source file path (relative to workspace root)',
              },
              destination: {
                type: 'string',
                description: 'Destination file path (relative to workspace root)',
              },
            },
            required: ['source', 'destination'],
          },
        },

        // ========== DEBUGGING / DEVELOPMENT TOOLS ==========
        {
          name: 'debug_lint',
          description: 'Run ESLint on a file or directory in the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Path to lint (relative to workspace root)',
              },
              fix: {
                type: 'boolean',
                description: 'Auto-fix lint issues when possible',
                default: false,
              },
            },
            required: ['filePath'],
          },
        },
        {
          name: 'debug_typecheck',
          description: 'Run TypeScript type checking on the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Optional specific file to typecheck (relative to workspace root)',
              },
              strict: {
                type: 'boolean',
                description: 'Use strict type checking',
                default: true,
              },
            },
          },
        },
        {
          name: 'debug_audit',
          description: 'Run npm/pnpm audit for dependency vulnerabilities',
          inputSchema: {
            type: 'object',
            properties: {
              cwd: {
                type: 'string',
                description: 'Optional directory path relative to workspace root containing package.json (default: workspace root)',
              },
            },
          },
        },
        {
          name: 'debug_run_tests',
          description: 'Run Vitest tests in the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              filePath: {
                type: 'string',
                description: 'Optional specific test file to run (relative to workspace root)',
              },
              watch: {
                type: 'boolean',
                description: 'Run in watch mode',
                default: false,
              },
              coverage: {
                type: 'boolean',
                description: 'Generate test coverage report',
                default: false,
              },
            },
          },
        },
        {
          name: 'debug_build',
          description: 'Build the project (runs build script in package.json)',
          inputSchema: {
            type: 'object',
            properties: {
              cwd: {
                type: 'string',
                description: 'Optional directory path relative to workspace root (default: workspace root)',
              },
            },
          },
        },

        // ========== EXECUTION TOOLS (Restricted & Sanitized) ==========
        {
          name: 'exec_run',
          description: 'Run a whitelisted command (pnpm, npm, npx, git, vitest, eslint, tsc) in the workspace',
          inputSchema: {
            type: 'object',
            properties: {
              command: {
                type: 'string',
                description: 'Command to execute (e.g. "pnpm test", "git status")',
              },
              cwd: {
                type: 'string',
                description: 'Working directory path (relative to workspace root, default: workspace root)',
              },
              timeout: {
                type: 'number',
                description: 'Timeout in milliseconds',
                default: 30000,
              },
            },
            required: ['command'],
          },
        },
        {
          name: 'exec_evaluate_javascript',
          description: 'Execute JavaScript code in the browser context of the current page',
          inputSchema: {
            type: 'object',
            properties: {
              content: {
                type: 'string',
                description: 'JavaScript code snippet to execute inside the browser',
              },
            },
            required: ['content'],
          },
        },
        {
          name: 'exec_check_port',
          description: 'Check if a port is in use and what process is using it (OS agnostic)',
          inputSchema: {
            type: 'object',
            properties: {
              port: {
                type: 'number',
                description: 'Port number to check',
              },
            },
            required: ['port'],
          },
        },
        {
          name: 'exec_health_check',
          description: 'Perform a health check request against an HTTP/HTTPS endpoint',
          inputSchema: {
            type: 'object',
            properties: {
              endpoint: {
                type: 'string',
                description: 'HTTP/HTTPS endpoint URL to check (e.g. http://localhost:3000/api/health)',
              },
              timeout: {
                type: 'number',
                description: 'Timeout in milliseconds',
                default: 5000,
              },
            },
            required: ['endpoint'],
          },
        },

        // ========== UTILITY TOOLS ==========
        {
          name: 'util_wait',
          description: 'Wait for a specified amount of time in milliseconds',
          inputSchema: {
            type: 'object',
            properties: {
              ms: {
                type: 'number',
                description: 'Milliseconds to wait',
                minimum: 100,
                maximum: 60000,
              },
            },
            required: ['ms'],
          },
        },
        {
          name: 'util_generate_id',
          description: 'Generate a unique UUID v4 identifier',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'util_hash',
          description: 'Generate a cryptographic hash of a string',
          inputSchema: {
            type: 'object',
            properties: {
              content: {
                type: 'string',
                description: 'Content to hash',
              },
              algorithm: {
                type: 'string',
                description: 'Hash algorithm (md5, sha1, sha256, sha512)',
                enum: ['md5', 'sha1', 'sha256', 'sha512'],
                default: 'sha256',
              },
            },
            required: ['content'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        return await this.handleToolCall(request.params.name, request.params.arguments ?? {});
      } catch (error: unknown) {
        if (error instanceof McpError) throw error;
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Error: ${message}` }],
          isError: true,
        };
      }
    });
  }

  private async handleToolCall(name: string, args: Record<string, unknown>) {
    switch (name) {
      // ========== BROWSER NAVIGATION ==========
      case 'browse_navigate': {
        const { url, timeout = 30000 } = args as DevToolsArgs;
        if (!url) throw new McpError(ErrorCode.InvalidParams, 'URL is required');
        const validatedUrl = validateUrl(url);
        
        const page = await this.getPage();
        await page.goto(validatedUrl, {
          waitUntil: 'networkidle0',
          timeout: timeout as number,
        });
        const title = await page.title();
        return {
          content: [{ type: 'text', text: `Navigated to ${validatedUrl}\nPage title: ${title}` }],
        };
      }

      case 'browse_click': {
        const { selector } = args as DevToolsArgs;
        if (!selector) throw new McpError(ErrorCode.InvalidParams, 'Selector is required');
        const page = await this.getPage();
        await page.waitForSelector(selector);
        await page.click(selector);
        return {
          content: [{ type: 'text', text: `Clicked element: ${selector}` }],
        };
      }

      case 'browse_type': {
        const { selector, content } = args as DevToolsArgs;
        if (!selector || content === undefined) {
          throw new McpError(ErrorCode.InvalidParams, 'Selector and content are required');
        }
        const page = await this.getPage();
        await page.waitForSelector(selector);
        await page.type(selector, content);
        return {
          content: [{ type: 'text', text: `Typed "${content}" into ${selector}` }],
        };
      }

      case 'browse_select': {
        const { selector, value } = args as DevToolsArgs;
        if (!selector || !value) {
          throw new McpError(ErrorCode.InvalidParams, 'Selector and value are required');
        }
        const page = await this.getPage();
        await page.waitForSelector(selector);
        await page.select(selector, value);
        return {
          content: [{ type: 'text', text: `Selected "${value}" in ${selector}` }],
        };
      }

      case 'browse_hover': {
        const { selector } = args as DevToolsArgs;
        if (!selector) throw new McpError(ErrorCode.InvalidParams, 'Selector is required');
        const page = await this.getPage();
        await page.waitForSelector(selector);
        await page.hover(selector);
        return {
          content: [{ type: 'text', text: `Hovered over: ${selector}` }],
        };
      }

      case 'browse_scroll': {
        const { x = 0, y = 0 } = args as DevToolsArgs;
        const page = await this.getPage();
        await page.evaluate((scrollX, scrollY) => {
          window.scrollBy(scrollX, scrollY);
        }, x as number, y as number);
        return {
          content: [{ type: 'text', text: `Scrolled by (${x}, ${y})` }],
        };
      }

      case 'browse_go_back': {
        const page = await this.getPage();
        await page.goBack({ waitUntil: 'networkidle0' });
        return {
          content: [{ type: 'text', text: 'Navigated back' }],
        };
      }

      case 'browse_go_forward': {
        const page = await this.getPage();
        await page.goForward({ waitUntil: 'networkidle0' });
        return {
          content: [{ type: 'text', text: 'Navigated forward' }],
        };
      }

      case 'browse_reload': {
        const page = await this.getPage();
        await page.reload({ waitUntil: 'networkidle0' });
        return {
          content: [{ type: 'text', text: 'Page reloaded' }],
        };
      }

      // ========== INSPECTION ==========
      case 'inspect_dom': {
        const { selector } = args as DevToolsArgs;
        const page = await this.getPage();
        let html: string;
        if (selector) {
          html = await page.evaluate((sel: string) => {
            const el = document.querySelector(sel);
            return el ? el.outerHTML : `Element not found: ${sel}`;
          }, selector);
        } else {
          html = await page.content();
        }
        return {
          content: [{ type: 'text', text: html }],
        };
      }

      case 'inspect_element': {
        const { selector } = args as DevToolsArgs;
        if (!selector) throw new McpError(ErrorCode.InvalidParams, 'Selector is required');
        const page = await this.getPage();
        const info = await page.evaluate((sel: string) => {
          const el = document.querySelector(sel);
          if (!el) return { error: `Element not found: ${sel}` };
          const rect = el.getBoundingClientRect();
          const computed = window.getComputedStyle(el);
          return {
            tag: el.tagName,
            id: el.id,
            class: el.className,
            text: (el.textContent || '').trim().substring(0, 500),
            attributes: Array.from(el.attributes).map(a => ({ name: a.name, value: a.value })),
            boundingBox: {
              x: rect.x,
              y: rect.y,
              width: rect.width,
              height: rect.height,
              top: rect.top,
              right: rect.right,
              bottom: rect.bottom,
              left: rect.left,
            },
            visible: rect.width > 0 && rect.height > 0,
            innerHTML: (el as HTMLElement).innerHTML?.substring(0, 1000),
          };
        }, selector);
        return {
          content: [{ type: 'text', text: JSON.stringify(info, null, 2) }],
        };
      }

      case 'inspect_console_logs': {
        const { clearAfter = true } = args as DevToolsArgs;
        const logs = [...this.consoleLogs];
        if (clearAfter) {
          this.consoleLogs = [];
        }
        return {
          content: [{ type: 'text', text: logs.length > 0 ? logs.join('\n') : 'No console logs captured' }],
        };
      }

      case 'inspect_network_requests': {
        const { resourceTypes, limit = 50 } = args as { resourceTypes?: string[]; limit?: number };
        let filtered = this.networkRequests;
        if (resourceTypes && resourceTypes.length > 0) {
          filtered = filtered.filter(req => resourceTypes.includes(req.type.toLowerCase()));
        }
        const slice = filtered.slice(-limit);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(slice, null, 2),
          }],
        };
      }

      case 'inspect_cookies': {
        const page = await this.getPage();
        const cookies = await page.cookies();
        return {
          content: [{ type: 'text', text: JSON.stringify(cookies, null, 2) }],
        };
      }

      case 'inspect_local_storage': {
        const page = await this.getPage();
        const storage = await page.evaluate(() => {
          const items: Record<string, string> = {};
          for (let i = 0; i < window.localStorage.length; i++) {
            const key = window.localStorage.key(i);
            if (key) items[key] = window.localStorage.getItem(key) || '';
          }
          return items;
        });
        return {
          content: [{ type: 'text', text: JSON.stringify(storage, null, 2) }],
        };
      }

      case 'inspect_session_storage': {
        const page = await this.getPage();
        const storage = await page.evaluate(() => {
          const items: Record<string, string> = {};
          for (let i = 0; i < window.sessionStorage.length; i++) {
            const key = window.sessionStorage.key(i);
            if (key) items[key] = window.sessionStorage.getItem(key) || '';
          }
          return items;
        });
        return {
          content: [{ type: 'text', text: JSON.stringify(storage, null, 2) }],
        };
      }

      case 'inspect_metrics': {
        const page = await this.getPage();
        const metrics = await page.evaluate(() => ({
          domNodes: document.querySelectorAll('*').length,
          scripts: document.scripts.length,
          stylesheets: document.styleSheets.length,
          images: document.images.length,
          links: document.links.length,
          bodySize: document.body?.innerHTML.length || 0,
          title: document.title,
          url: window.location.href,
          userAgent: navigator.userAgent,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight,
          },
        }));
        const perfMetrics = await page.metrics();
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ ...metrics, performance: perfMetrics }, null, 2),
          }],
        };
      }

      // ========== SCREENSHOTS ==========
      case 'screenshot_page': {
        const {
          selector,
          format = 'png',
          quality = 80,
          fullPage = false,
        } = args as DevToolsArgs;
        const page = await this.getPage();
        await fs.ensureDir(SCREENSHOTS_DIR);
        const filename = `screenshot_${Date.now()}.${format}`;
        const filepath = path.join(SCREENSHOTS_DIR, filename);

        if (selector) {
          const el = await page.waitForSelector(selector);
          if (!el) throw new McpError(ErrorCode.InvalidRequest, `Element not found: ${selector}`);
          await el.screenshot({
            path: filepath,
            type: format as 'png' | 'jpeg' | 'webp',
            quality: format !== 'png' ? (quality as number) : undefined,
          });
        } else {
          await page.screenshot({
            path: filepath,
            type: format as 'png' | 'jpeg' | 'webp',
            quality: format !== 'png' ? (quality as number) : undefined,
            fullPage: fullPage as boolean,
          });
        }

        return {
          content: [{
            type: 'text',
            text: `Screenshot saved: ${filepath}\nFormat: ${format}\n${selector ? `Element: ${selector}` : 'Full page'}`,
          }],
        };
      }

      case 'screenshot_element': {
        const { selector, format = 'png' } = args as DevToolsArgs;
        if (!selector) throw new McpError(ErrorCode.InvalidParams, 'Selector is required');
        const page = await this.getPage();
        await fs.ensureDir(SCREENSHOTS_DIR);
        const filename = `element_${Date.now()}.${format}`;
        const filepath = path.join(SCREENSHOTS_DIR, filename);

        const el = await page.waitForSelector(selector);
        if (!el) throw new McpError(ErrorCode.InvalidRequest, `Element not found: ${selector}`);
        await el.screenshot({
          path: filepath,
          type: format as 'png' | 'jpeg' | 'webp',
        });

        return {
          content: [{
            type: 'text',
            text: `Element screenshot saved: ${filepath}\nSelector: ${selector}`,
          }],
        };
      }

      // ========== FILE SYSTEM (Path Traversal Protected) ==========
      case 'file_read': {
        const { filePath } = args as DevToolsArgs;
        if (!filePath) throw new McpError(ErrorCode.InvalidParams, 'filePath is required');
        const fullPath = safePath(filePath);
        if (!await fs.pathExists(fullPath)) {
          throw new McpError(ErrorCode.InvalidRequest, `File not found: ${filePath}`);
        }
        const content = await fs.readFile(fullPath, 'utf-8');
        const stat = await fs.stat(fullPath);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              path: filePath,
              size: stat.size,
              modified: stat.mtime,
              content,
            }, null, 2),
          }],
        };
      }

      case 'file_write': {
        const { filePath, content } = args as DevToolsArgs;
        if (!filePath || content === undefined) {
          throw new McpError(ErrorCode.InvalidParams, 'filePath and content are required');
        }
        const fullPath = safePath(filePath);
        await fs.ensureDir(path.dirname(fullPath));
        await fs.writeFile(fullPath, content, 'utf-8');
        return {
          content: [{ type: 'text', text: `File written: ${filePath} (${content.length} bytes)` }],
        };
      }

      case 'file_search': {
        const { pattern, basePath } = args as DevToolsArgs;
        if (!pattern) throw new McpError(ErrorCode.InvalidParams, 'pattern is required');
        const searchPath = basePath ? safePath(basePath) : projectRoot;
        
        const files = await glob(pattern, { cwd: searchPath, nodir: true });
        
        // Filter matches to guarantee absolute path security (prevent glob escaping root)
        const safeMatches = files
          .map(f => path.resolve(searchPath, f))
          .filter(full => {
            try {
              safePath(path.relative(projectRoot, full));
              return true;
            } catch {
              return false;
            }
          })
          .map(full => path.relative(projectRoot, full));

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              pattern,
              basePath: path.relative(projectRoot, searchPath) || '.',
              matches: safeMatches.length,
              files: safeMatches.slice(0, 200),
            }, null, 2),
          }],
        };
      }

      case 'file_delete': {
        const { filePath } = args as DevToolsArgs;
        if (!filePath) throw new McpError(ErrorCode.InvalidParams, 'filePath is required');
        const fullPath = safePath(filePath);
        if (fullPath === projectRoot) {
          throw new McpError(ErrorCode.InvalidParams, 'Access denied: Cannot delete project root');
        }
        await fs.remove(fullPath);
        return {
          content: [{ type: 'text', text: `Deleted: ${filePath}` }],
        };
      }

      case 'file_info': {
        const { filePath } = args as DevToolsArgs;
        if (!filePath) throw new McpError(ErrorCode.InvalidParams, 'filePath is required');
        const fullPath = safePath(filePath);
        if (!await fs.pathExists(fullPath)) {
          throw new McpError(ErrorCode.InvalidRequest, `Not found: ${filePath}`);
        }
        const stat = await fs.stat(fullPath);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              path: filePath,
              exists: true,
              isFile: stat.isFile(),
              isDirectory: stat.isDirectory(),
              size: stat.size,
              created: stat.birthtime,
              modified: stat.mtime,
              permissions: stat.mode.toString(8),
            }, null, 2),
          }],
        };
      }

      case 'file_list_dir': {
        const { filePath } = args as DevToolsArgs;
        if (!filePath) throw new McpError(ErrorCode.InvalidParams, 'filePath is required');
        const fullPath = safePath(filePath);
        if (!await fs.pathExists(fullPath)) {
          throw new McpError(ErrorCode.InvalidRequest, `Directory not found: ${filePath}`);
        }
        const items = await fs.readdir(fullPath);
        const contents = [];
        for (const item of items) {
          const itemPath = path.join(fullPath, item);
          const stat = await fs.stat(itemPath);
          contents.push({
            name: item,
            isFile: stat.isFile(),
            isDirectory: stat.isDirectory(),
            size: stat.size,
            modified: stat.mtime,
          });
        }
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              path: filePath,
              items: contents.length,
              contents,
            }, null, 2),
          }],
        };
      }

      case 'file_copy': {
        const { source, destination } = args as DevToolsArgs;
        if (!source || !destination) {
          throw new McpError(ErrorCode.InvalidParams, 'source and destination are required');
        }
        const srcPath = safePath(source);
        const destPath = safePath(destination);
        await fs.ensureDir(path.dirname(destPath));
        await fs.copy(srcPath, destPath);
        return {
          content: [{ type: 'text', text: `Copied ${source} → ${destination}` }],
        };
      }

      // ========== DEBUGGING / DEVELOPMENT ==========
      case 'debug_lint': {
        const { filePath, fix = false } = args as DevToolsArgs;
        if (!filePath) throw new McpError(ErrorCode.InvalidParams, 'filePath is required');
        const fullPath = safePath(filePath);
        try {
          const fixFlag = fix ? '--fix' : '';
          const output = execSync(
            `npx eslint ${fixFlag} "${fullPath}" --format json 2>&1 || true`,
            { cwd: projectRoot, encoding: 'utf-8', timeout: 30000 }
          );
          return {
            content: [{ type: 'text', text: output || 'No lint issues found' }],
          };
        } catch {
          return {
            content: [{ type: 'text', text: 'ESLint not configured or failed to run. Ensure dependencies are installed.' }],
          };
        }
      }

      case 'debug_typecheck': {
        const { filePath } = args as DevToolsArgs;
        try {
          const target = filePath ? `"${safePath(filePath)}"` : '--noEmit';
          const output = execSync(
            `npx tsc ${target} 2>&1 || true`,
            { cwd: projectRoot, encoding: 'utf-8', timeout: 60000 }
          );
          return {
            content: [{ type: 'text', text: output || 'TypeScript check passed — no errors' }],
          };
        } catch {
          return {
            content: [{ type: 'text', text: 'TypeScript not configured or failed to run.' }],
          };
        }
      }

      case 'debug_audit': {
        const { cwd } = args as DevToolsArgs;
        const auditCwd = cwd ? safePath(cwd) : projectRoot;
        try {
          const output = execSync(
            'pnpm audit 2>&1 || true',
            { cwd: auditCwd, encoding: 'utf-8', timeout: 60000 }
          );
          return {
            content: [{ type: 'text', text: output || 'No vulnerabilities found' }],
          };
        } catch {
          return {
            content: [{ type: 'text', text: 'pnpm not available or package.json not found in the target directory.' }],
          };
        }
      }

      case 'debug_run_tests': {
        const { filePath, watch = false, coverage = false } = args as DevToolsArgs;
        let cmd = 'npx vitest run';
        if (filePath) cmd += ` "${safePath(filePath)}"`;
        if (watch) cmd = cmd.replace(' run', '');
        if (coverage) cmd += ' --coverage';
        try {
          const output = execSync(`${cmd} 2>&1 || true`, {
            cwd: projectRoot,
            encoding: 'utf-8',
            timeout: 120000,
          });
          return {
            content: [{ type: 'text', text: output }],
          };
        } catch {
          return {
            content: [{ type: 'text', text: 'Vitest failed or is not configured.' }],
          };
        }
      }

      case 'debug_build': {
        const { cwd } = args as DevToolsArgs;
        const buildCwd = cwd ? safePath(cwd) : projectRoot;
        try {
          const output = execSync('pnpm build 2>&1 || true', {
            cwd: buildCwd,
            encoding: 'utf-8',
            timeout: 120000,
          });
          return {
            content: [{ type: 'text', text: output || 'Build completed successfully' }],
          };
        } catch {
          return {
            content: [{ type: 'text', text: 'Build failed or build script not found.' }],
          };
        }
      }

      // ========== EXECUTION (Restricted & Whitelisted) ==========
      case 'exec_run': {
        const { command, cwd, timeout = 30000 } = args as DevToolsArgs;
        if (!command) throw new McpError(ErrorCode.InvalidParams, 'command is required');
        
        const validatedCommand = sanitizeAndValidateCommand(command);
        const execCwd = cwd ? safePath(cwd) : projectRoot;
        
        try {
          const output = execSync(validatedCommand, {
            cwd: execCwd,
            encoding: 'utf-8',
            timeout: timeout as number,
            maxBuffer: 1024 * 1024,
          });
          return {
            content: [{ type: 'text', text: output || 'Command executed successfully (no output)' }],
          };
        } catch (error: unknown) {
          if (error instanceof Error) {
            return {
              content: [{ type: 'text', text: `Command failed: ${error.message}` }],
              isError: true,
            };
          }
          throw error;
        }
      }

      case 'exec_evaluate_javascript': {
        const { content } = args as DevToolsArgs;
        if (content === undefined) {
          throw new McpError(ErrorCode.InvalidParams, 'JavaScript content is required');
        }
        const page = await this.getPage();
        const result = await page.evaluate((code: string) => {
          try {
            const fn = new Function(code);
            const output = fn();
            return JSON.stringify(output, null, 2);
          } catch (e: unknown) {
            return `Error: ${e instanceof Error ? e.message : String(e)}`;
          }
        }, content);
        return {
          content: [{ type: 'text', text: result }],
        };
      }

      case 'exec_check_port': {
        const { port } = args as DevToolsArgs;
        if (typeof port !== 'number') {
          throw new McpError(ErrorCode.InvalidParams, 'port is required and must be a number');
        }
        try {
          let cmd = '';
          if (process.platform === 'win32') {
            cmd = `netstat -ano | findstr :${port}`;
          } else {
            cmd = `lsof -i :${port} || ss -tulpn | grep :${port}`;
          }
          const output = execSync(cmd, { encoding: 'utf-8', timeout: 5000 });
          return {
            content: [{ type: 'text', text: output }],
          };
        } catch {
          return {
            content: [{ type: 'text', text: `Port ${port} is not in use or utility check failed.` }],
          };
        }
      }

      case 'exec_health_check': {
        const { endpoint, timeout = 5000 } = args as DevToolsArgs;
        if (!endpoint) throw new McpError(ErrorCode.InvalidParams, 'endpoint is required');
        const validatedUrl = validateUrl(endpoint);
        
        const page = await this.getPage();
        try {
          const response = await page.goto(validatedUrl, {
            waitUntil: 'networkidle0',
            timeout: timeout as number,
          });
          if (!response) throw new Error('No response received');
          const status = response.status();
          const body = await response.text();
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                endpoint: validatedUrl,
                status,
                ok: status >= 200 && status < 400,
                body: body.substring(0, 2000),
              }, null, 2),
            }],
          };
        } catch (error: unknown) {
          return {
            content: [{
              type: 'text',
              text: `Health check failed for ${validatedUrl}: ${error instanceof Error ? error.message : 'Unknown error'}`,
            }],
            isError: true,
          };
        }
      }

      // ========== UTILITY ==========
      case 'util_wait': {
        const { ms } = args as DevToolsArgs;
        if (!ms) throw new McpError(ErrorCode.InvalidParams, 'ms is required');
        await new Promise(resolve => setTimeout(resolve, ms as number));
        return {
          content: [{ type: 'text', text: `Waited for ${ms}ms` }],
        };
      }

      case 'util_generate_id': {
        return {
          content: [{ type: 'text', text: randomUUID() }],
        };
      }

      case 'util_hash': {
        const { content, algorithm = 'sha256' } = args as DevToolsArgs;
        if (content === undefined) {
          throw new McpError(ErrorCode.InvalidParams, 'content is required');
        }
        const hash = createHash(algorithm).update(content).digest('hex');
        return {
          content: [{ type: 'text', text: JSON.stringify({ algorithm, hash }, null, 2) }],
        };
      }

      default:
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${name}`
        );
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('DevTools MCP server running on stdio');
  }
}

const server = new DevToolsServer();
server.run();

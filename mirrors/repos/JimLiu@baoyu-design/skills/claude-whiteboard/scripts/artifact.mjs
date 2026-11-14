#!/usr/bin/env node
// claude-whiteboard: local Artifact tool (prebuilt; do not edit).

import { createHash as createHash5 } from "node:crypto";
import fs10 from "node:fs";
import path9 from "node:path";
import { fileURLToPath } from "node:url";

import { createHash } from "node:crypto";
import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
var STATE_FILE = ".artifact-server.json";
var LOG_FILE = ".artifact-server.log";
var EXPORTS_DIR = "exports";
function readState(root) {
  try {
    return JSON.parse(fs.readFileSync(path.join(root, STATE_FILE), "utf8"));
  } catch {
    return null;
  }
}
function alive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error.code === "EPERM";
  }
}
async function runningServer(root, kind, probe) {
  const state = readState(root);
  if (!state || state.kind !== kind || !alive(state.pid)) return null;
  try {
    const response = await fetch(new URL(probe, state.url), { signal: AbortSignal.timeout(2e3) });
    return response.ok ? state : null;
  } catch {
    return null;
  }
}
function writeState(state) {
  fs.writeFileSync(path.join(state.root, STATE_FILE), `${JSON.stringify(state, null, 2)}
`);
  writeGitignore(state.root, state.kind);
}
function removeState(root) {
  const state = readState(root);
  if (state && state.pid !== process.pid && alive(state.pid)) return;
  fs.rmSync(path.join(root, STATE_FILE), { force: true });
}
var GITIGNORE_FILE = ".gitignore";
var gitignoreLines = (kind) => [STATE_FILE, LOG_FILE, ".sharing.json", ...kind === "docs" ? [] : ["/history/"], `/${EXPORTS_DIR}/`, "*.tmp", ".tmp-*", ".DS_Store"];
function writeGitignore(root, kind) {
  const file = path.join(root, GITIGNORE_FILE);
  try {
    fs.writeFileSync(file, ["# Written by open-artifacts when the editor first opened this folder: what only this computer's editor server needs.", ...gitignoreLines(kind), ""].join("\n"), { flag: "wx" });
  } catch {
  }
}
async function listen(server, port, host) {
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, () => resolve());
  });
  const address = server.address();
  return typeof address === "object" && address ? address.port : port;
}
var PORT_TRIES = 100;
var PortsTaken = class extends Error {
  code = "PORT_IN_USE";
  from;
  to;
  constructor(from, to) {
    super(`${from === to ? `Port ${from} is` : `Ports ${from} to ${to} are all`} in use; pick another --port (0 takes any free one).`);
    this.from = from;
    this.to = to;
  }
};
var NetworkBlocked = class extends Error {
  code = "NETWORK_BLOCKED";
  constructor() {
    super(
      "A sandbox blocks local network here (127.0.0.1), so the server cannot start and no port is really in use. Run this same command with local network allowed, outside the sandbox, asking for that permission if your commands need approval."
    );
  }
};
function loopbackBlocked(port) {
  return new Promise((resolve) => {
    const socket = net.connect({ host: "127.0.0.1", port });
    const done = (blocked) => {
      socket.destroy();
      resolve(blocked);
    };
    socket.setTimeout(300, () => done(false));
    socket.once("connect", () => done(false));
    socket.once("error", (error) => done(error.code === "EPERM" || error.code === "EACCES"));
  });
}
var isBenchmarkRange = (address) => /^198\.1[89]\./.test(address);
function isTailnet(address) {
  const m = /^100\.(\d{1,3})\./.exec(address);
  return !!m && Number(m[1]) >= 64 && Number(m[1]) <= 127;
}
var isTunnel = (name) => /(^|[^a-z0-9])(utun|tun|tap|wg|ppp|ipsec)\d*($|[^a-z0-9])/i.test(name) || /vpn|wintun|tunnel/i.test(name);
var ipv4Number = (address) => address.split(".").reduce((n, part) => n * 256 + Number(part), 0);
function isOwnNetwork(entry) {
  if (!/^\d+\.\d+\.\d+\.\d+$/.test(entry.netmask)) return false;
  const mask = ipv4Number(entry.netmask);
  if (mask >= ipv4Number("255.255.255.252")) return true;
  const address = ipv4Number(entry.address);
  return ((address & mask) >>> 0) + 1 === address;
}
function lanAddresses() {
  const out = /* @__PURE__ */ new Map();
  for (const [name, list] of Object.entries(os.networkInterfaces())) {
    for (const entry of list ?? []) {
      if (entry.family !== "IPv4" || entry.internal || entry.address.startsWith("169.254.") || isBenchmarkRange(entry.address)) continue;
      const rank = isTailnet(entry.address) ? 2 : isTunnel(name) || isOwnNetwork(entry) ? 1 : 0;
      out.set(entry.address, Math.min(rank, out.get(entry.address) ?? rank));
    }
  }
  return [...out.keys()].sort((a, b) => out.get(a) - out.get(b));
}
function answers(host, port) {
  return new Promise((resolve) => {
    const socket = net.connect({ host, port });
    const done = (taken) => {
      socket.destroy();
      resolve(taken);
    };
    socket.setTimeout(300, () => done(false));
    socket.once("connect", () => done(true));
    socket.once(
      "error",
      (error) => done(!["ECONNREFUSED", "EADDRNOTAVAIL", "EAFNOSUPPORT", "ENETUNREACH", "EHOSTUNREACH", "EACCES", "EPERM"].includes(error.code ?? ""))
    );
  });
}
async function answersAnyPort(address) {
  const server = net.createServer();
  let port;
  try {
    port = await new Promise((resolve, reject) => {
      server.once("error", reject);
      server.listen(0, address, () => {
        const bound = server.address();
        resolve(typeof bound === "object" && bound ? bound.port : 0);
      });
    });
  } catch {
    return false;
  } finally {
    await new Promise((resolve) => server.close(() => resolve()));
  }
  return port > 0 && answers(address, port);
}
async function listenFree(server, from, host, first) {
  if (await loopbackBlocked(first || from || 1)) throw new NetworkBlocked();
  if (from === 0) return listen(server, 0, host);
  const to = Math.min(from + PORT_TRIES - 1, 65535);
  const range = Array.from({ length: to - from + 1 }, (_, i) => from + i);
  const ports = first ? [first, ...range.filter((port) => port !== first)] : range;
  const wildcard = host === "0.0.0.0" || host === "::";
  const lan = lanAddresses().filter((address) => address !== host);
  const answering = await Promise.all(lan.map(answersAnyPort));
  const probes = [.../* @__PURE__ */ new Set([...wildcard ? [] : [host], "127.0.0.1", "::1", ...lan.filter((_, i) => !answering[i])])];
  for (const port of ports) {
    if ((await Promise.all(probes.map((address) => answers(address, port)))).some(Boolean)) continue;
    try {
      return await listen(server, port, host);
    } catch (error) {
      if (error.code !== "EADDRINUSE") throw error;
    }
  }
  throw new PortsTaken(from, to);
}
function serverOrigin(host, port) {
  const shown2 = host === "0.0.0.0" || host === "::" ? "127.0.0.1" : host.includes(":") ? `[${host}]` : host;
  return `http://${shown2}:${port}`;
}
var pagePathOf = (kind, root) => `/${kind}/${createHash("sha256").update(path.resolve(root)).digest("base64url").slice(0, 22)}/`;
var pageGone = (dir, owner) => owner ? `This page's files are no longer in ${dir}: the skill was moved, renamed or removed while its server ran. Stop the server and open the artifact again (the agent that opened it can do both).` : "This page's files are gone from the computer that shares it. Ask whoever shared it to open it again.";
function sendJson(response, status, body, headers = {}) {
  const text = JSON.stringify(body);
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(text),
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    ...headers
  });
  response.end(text);
}
var TooLarge = class extends Error {
};
function readBody(request, limit) {
  return new Promise((resolve, reject) => {
    const declared = Number(request.headers["content-length"]);
    if (Number.isFinite(declared) && declared > limit) {
      reject(new TooLarge());
      request.resume();
      return;
    }
    const chunks = [];
    let size = 0;
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > limit) {
        reject(new TooLarge());
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", reject);
  });
}
function sameOrigin(request) {
  const origin = request.headers.origin;
  if (origin === void 0) return true;
  const host = request.headers.host;
  if (!host) return false;
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}
function sendFile(request, response, file, headers) {
  response.writeHead(200, headers);
  if (request.method === "HEAD") {
    response.end();
    return;
  }
  const stream = fs.createReadStream(file);
  stream.on("error", () => response.destroy());
  response.on("close", () => stream.destroy());
  stream.pipe(response);
}
var errorText = (error) => error instanceof Error ? error.message : String(error);

import { spawn } from "node:child_process";
import dns from "node:dns/promises";
import { EventEmitter } from "node:events";
import fs3 from "node:fs";
import http from "node:http";
import os2 from "node:os";
import path3 from "node:path";

import crypto from "node:crypto";
import fs2 from "node:fs";
import path2 from "node:path";
var GUEST_ROLES = ["editor", "commenter", "viewer"];
var isGuestRole = (value) => typeof value === "string" && GUEST_ROLES.includes(value);
var SHARING_FILE = ".sharing.json";
var MAX_GUESTS = 200;
var MAX_NAME = 40;
var token = (bytes = 18) => crypto.randomBytes(bytes).toString("base64url");
var isRecord = (value) => typeof value === "object" && value !== null && !Array.isArray(value);
function fresh() {
  return { lan: false, links: { editor: { token: token(), on: true }, commenter: { token: token(), on: true }, viewer: { token: token(), on: true } }, guests: [] };
}
function cleanName(raw) {
  const name = typeof raw === "string" ? raw.replace(/[\u0000-\u001f\u007f@<>]/g, "").replace(/\s+/g, " ").trim() : "";
  return [...name].slice(0, MAX_NAME).join("");
}
function guestUser(guest) {
  return { id: `guest-${guest.id}`, name: guest.name, email: `${guest.name}@${guest.id}.guest` };
}
function isLoopback(address) {
  if (!address) return false;
  const a = address.startsWith("::ffff:") ? address.slice(7) : address;
  return a === "::1" || a.startsWith("127.");
}
var Sharing = class _Sharing {
  file;
  state;
  constructor(root) {
    this.file = path2.join(root, SHARING_FILE);
    this.state = _Sharing.read(this.file);
  }
  static read(file) {
    let raw;
    try {
      raw = JSON.parse(fs2.readFileSync(file, "utf8"));
    } catch {
      return fresh();
    }
    const state = fresh();
    if (!isRecord(raw)) return state;
    state.lan = raw.lan === true;
    if (typeof raw.port === "number" && Number.isInteger(raw.port) && raw.port > 0 && raw.port < 65536) state.port = raw.port;
    if (isRecord(raw.links)) {
      for (const role of GUEST_ROLES) {
        const link = raw.links[role];
        if (isRecord(link) && typeof link.token === "string" && link.token.length >= 16) state.links[role] = { token: link.token, on: link.on !== false };
      }
    }
    if (isRecord(raw.owner) && typeof raw.owner.token === "string" && raw.owner.token.length >= 32) state.owner = { token: raw.owner.token };
    if (Array.isArray(raw.guests)) {
      for (const g of raw.guests) {
        if (!isRecord(g) || typeof g.id !== "string" || typeof g.secret !== "string" || !isGuestRole(g.role) || typeof g.link !== "string") continue;
        state.guests.push({
          id: g.id,
          secret: g.secret,
          name: cleanName(g.name) || "Guest",
          role: g.role,
          link: g.link,
          joined: typeof g.joined === "string" ? g.joined : (/* @__PURE__ */ new Date(0)).toISOString(),
          ...typeof g.seen === "string" ? { seen: g.seen } : {}
        });
      }
    }
    return state;
  }
  save() {
    const tmp = `${this.file}.${process.pid}.tmp`;
    fs2.writeFileSync(tmp, `${JSON.stringify(this.state, null, 2)}
`, { mode: 384 });
    fs2.renameSync(tmp, this.file);
  }
  /** The role whose link has this token, while that link is on. */
  linkRole(tokenGiven) {
    for (const role of GUEST_ROLES) {
      const link = this.state.links[role];
      if (link.on && tokenGiven.length === link.token.length && crypto.timingSafeEqual(Buffer.from(tokenGiven), Buffer.from(link.token))) return role;
    }
    return null;
  }
  /** The owner's link token (`state.owner`), made and saved the first time it is asked for. */
  ownerToken() {
    if (!this.state.owner) {
      this.state.owner = { token: token(32) };
      this.save();
    }
    return this.state.owner.token;
  }
  /** Whether `given` is the owner's link token (a cookie or a link's). */
  isOwnerToken(given) {
    const own = this.state.owner?.token;
    if (!given || !own) return false;
    const a = Buffer.from(given);
    const b = Buffer.from(own);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
  }
  /** A new owner's link: the old one, and every browser that came in through it, stop working. */
  resetOwner() {
    this.state.owner = { token: token(32) };
    this.save();
  }
  /** The guest a cookie names, if they still have access (their link on and not reset). */
  guest(secret) {
    if (!secret) return null;
    const guest = this.state.guests.find((g) => g.secret === secret);
    return guest && this.valid(guest) ? guest : null;
  }
  valid(guest) {
    const link = this.state.links[guest.role];
    return link.on && link.token === guest.link && this.state.guests.includes(guest);
  }
  join(role, name) {
    const guest = { id: token(4), secret: token(24), name: cleanName(name) || "Guest", role, link: this.state.links[role].token, joined: (/* @__PURE__ */ new Date()).toISOString() };
    this.state.guests.push(guest);
    if (this.state.guests.length > MAX_GUESTS) this.state.guests.splice(0, this.state.guests.length - MAX_GUESTS);
    this.save();
    return guest;
  }
  /** Marks a guest seen now (saved at most once a minute per guest). */
  seen(guest) {
    const now = /* @__PURE__ */ new Date();
    if (guest.seen && now.getTime() - Date.parse(guest.seen) < 6e4) return;
    guest.seen = now.toISOString();
    this.save();
  }
  setLan(on, port) {
    this.state.lan = on;
    if (on && port) this.state.port = port;
    this.save();
  }
  setLink(role, on) {
    this.state.links[role].on = on;
    this.save();
  }
  /** A new token for the link: the old link stops working and the guests who came through it are dropped. */
  resetLink(role) {
    const old = this.state.links[role].token;
    this.state.links[role] = { token: token(), on: this.state.links[role].on };
    this.state.guests = this.state.guests.filter((g) => g.link !== old);
    this.save();
  }
  /**
   * Gives a guest another role. They now hang on that role's link (turning it off or resetting it drops them), so a role
   * whose link is off would shut them out: false then, as for a guest who isn't there.
   */
  setRole(id, role) {
    const guest = this.state.guests.find((g) => g.id === id);
    if (!guest || !this.state.links[role].on) return false;
    guest.role = role;
    guest.link = this.state.links[role].token;
    this.save();
    return true;
  }
  removeGuest(id) {
    const before = this.state.guests.length;
    this.state.guests = this.state.guests.filter((g) => g.id !== id);
    if (this.state.guests.length === before) return false;
    this.save();
    return true;
  }
};

import { createHash as createHash2 } from "node:crypto";
var GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
var MAX_MESSAGE = 64 * 1024 * 1024;
var WebSocketConnection = class {
  socket;
  buffer = Buffer.alloc(0);
  parts = [];
  partOpcode = 0;
  closed = false;
  handlers = {};
  constructor(socket, head) {
    this.socket = socket;
    socket.on("data", (chunk) => this.receive(chunk));
    socket.on("close", () => this.finish());
    socket.on("error", () => this.finish());
    if (head.length) this.receive(head);
  }
  get open() {
    return !this.closed;
  }
  sendText(text) {
    this.send(1, Buffer.from(text, "utf8"));
  }
  sendBinary(data) {
    this.send(2, data);
  }
  close(code = 1e3, reason = "") {
    if (this.closed) return;
    const body = Buffer.alloc(2 + Buffer.byteLength(reason));
    body.writeUInt16BE(code, 0);
    body.write(reason, 2);
    this.send(8, body);
    this.socket.end();
    this.finish();
  }
  finish() {
    if (this.closed) return;
    this.closed = true;
    this.socket.destroy();
    this.handlers.close?.();
  }
  send(opcode, payload) {
    if (this.closed) return;
    const length = payload.length;
    let header;
    if (length < 126) {
      header = Buffer.from([128 | opcode, length]);
    } else if (length < 65536) {
      header = Buffer.alloc(4);
      header[0] = 128 | opcode;
      header[1] = 126;
      header.writeUInt16BE(length, 2);
    } else {
      header = Buffer.alloc(10);
      header[0] = 128 | opcode;
      header[1] = 127;
      header.writeBigUInt64BE(BigInt(length), 2);
    }
    this.socket.write(Buffer.concat([header, payload]));
  }
  receive(chunk) {
    this.buffer = this.buffer.length ? Buffer.concat([this.buffer, chunk]) : chunk;
    for (; ; ) {
      if (this.buffer.length < 2) return;
      const first = this.buffer[0];
      const second = this.buffer[1];
      const fin = (first & 128) !== 0;
      const opcode = first & 15;
      const masked = (second & 128) !== 0;
      let length = second & 127;
      let offset = 2;
      if (length === 126) {
        if (this.buffer.length < 4) return;
        length = this.buffer.readUInt16BE(2);
        offset = 4;
      } else if (length === 127) {
        if (this.buffer.length < 10) return;
        const big = this.buffer.readBigUInt64BE(2);
        if (big > BigInt(MAX_MESSAGE)) return this.close(1009, "message too big");
        length = Number(big);
        offset = 10;
      }
      const maskLength = masked ? 4 : 0;
      if (this.buffer.length < offset + maskLength + length) return;
      const mask = masked ? this.buffer.subarray(offset, offset + 4) : null;
      const payload = Buffer.from(this.buffer.subarray(offset + maskLength, offset + maskLength + length));
      if (mask) for (let index = 0; index < payload.length; index++) payload[index] = payload[index] ^ mask[index & 3];
      this.buffer = this.buffer.subarray(offset + maskLength + length);
      this.frame(fin, opcode, payload);
      if (this.closed) return;
    }
  }
  frame(fin, opcode, payload) {
    switch (opcode) {
      case 8:
        this.close(payload.length >= 2 ? payload.readUInt16BE(0) : 1e3);
        return;
      case 9:
        this.send(10, payload);
        return;
      case 10:
        return;
      case 0:
      case 1:
      case 2: {
        if (opcode !== 0) {
          this.parts = [];
          this.partOpcode = opcode;
        }
        this.parts.push(payload);
        if (this.parts.reduce((total, part) => total + part.length, 0) > MAX_MESSAGE) return this.close(1009, "message too big");
        if (!fin) return;
        const message = Buffer.concat(this.parts);
        this.parts = [];
        if (this.partOpcode === 1) this.handlers.text?.(message.toString("utf8"));
        else this.handlers.binary?.(message);
        return;
      }
      default:
        this.close(1002, "unknown opcode");
    }
  }
};
function acceptWebSocket(request, socket, head, protocol) {
  const key = request.headers["sec-websocket-key"];
  if (typeof key !== "string" || String(request.headers.upgrade).toLowerCase() !== "websocket") {
    socket.end("HTTP/1.1 400 Bad Request\r\n\r\n");
    return null;
  }
  const accept = createHash2("sha1").update(key + GUID).digest("base64");
  socket.write(["HTTP/1.1 101 Switching Protocols", "Upgrade: websocket", "Connection: Upgrade", `Sec-WebSocket-Accept: ${accept}`, ...protocol ? [`Sec-WebSocket-Protocol: ${protocol}`] : [], "", ""].join("\r\n"));
  return new WebSocketConnection(socket, head);
}

var HUB_ROUTE = "/__hub";
var STREAM_PROTOCOL = "baoyu-sse";
var STREAM_REFUSED = 4e3;
function buildOf(script2) {
  const real = fs3.realpathSync(script2);
  const { mtimeMs, size } = fs3.statSync(real);
  return `${real}:${mtimeMs}:${size}`;
}
var SiteClash = class extends Error {
};
var StreamResponse = class extends EventEmitter {
  status = 200;
  headersSent = false;
  writableEnded = false;
  destroyed = false;
  ws;
  constructor(ws) {
    super();
    this.ws = ws;
  }
  writeHead(status) {
    this.status = status;
    this.headersSent = true;
    return this;
  }
  setHeader() {
    return this;
  }
  flushHeaders() {
  }
  write(chunk) {
    if (this.status === 200 && !this.writableEnded) this.ws.sendText(String(chunk));
    return true;
  }
  end(chunk) {
    if (this.writableEnded) return this;
    if (chunk !== void 0) this.write(chunk);
    this.writableEnded = true;
    this.ws.close(this.status === 200 ? 1e3 : STREAM_REFUSED + Math.min(this.status, 999));
    return this;
  }
  destroy() {
    this.destroyed = true;
    return this.end();
  }
  closed() {
    this.writableEnded = true;
    this.emit("close");
  }
};
var Hub = class {
  port = 0;
  kind;
  host;
  build;
  factory;
  /** Sites' logs go to its stderr too: it runs in someone's terminal, not in the background. */
  echo;
  server;
  /** page → site. */
  sites = /* @__PURE__ */ new Map();
  adding = /* @__PURE__ */ new Map();
  startedAt = /* @__PURE__ */ new Map();
  hosts = /* @__PURE__ */ new Set();
  /** One listener per LAN address while any site is open to the network. */
  lanServers = /* @__PURE__ */ new Map();
  /** Names that resolve to an address listened on, asked for by `allowName` (lower case, no port). */
  lanNames = /* @__PURE__ */ new Set();
  network;
  constructor(options) {
    this.echo = options.echo;
    this.kind = options.kind;
    this.build = options.build;
    this.host = options.host;
    this.factory = options.site;
    this.server = this.createServer();
    const hub = this;
    this.network = {
      get port() {
        return hub.port;
      },
      addresses: () => [...this.lanServers.keys()],
      open: () => this.openLan(),
      release: () => this.releaseLan(),
      allowName: (name) => this.allowName(name)
    };
  }
  createServer() {
    const server = http.createServer((request, response) => {
      this.onRequest(request, response).catch((error) => {
        process.stderr.write(`[${(/* @__PURE__ */ new Date()).toISOString()}] request failed: ${error instanceof Error ? error.stack ?? error.message : String(error)}
`);
        if (!response.headersSent) sendJson(response, 500, { code: "internal", message: "internal error" });
        else response.destroy();
      });
    });
    server.on("upgrade", (request, socket, head) => this.onUpgrade(request, socket, head));
    return server;
  }
  /** Listens at the first free port from `port`; `first` is tried before them. */
  async listen(port, first) {
    this.port = await listenFree(this.server, port, this.host, first);
    const named = this.host === "0.0.0.0" || this.host === "::" ? [] : [this.host.includes(":") ? `[${this.host}]:${this.port}` : `${this.host}:${this.port}`];
    this.hosts = /* @__PURE__ */ new Set([`127.0.0.1:${this.port}`, `localhost:${this.port}`, `[::1]:${this.port}`, ...named]);
    return this.port;
  }
  /** Ends every site and the listeners; what the folders' state files say goes with them. */
  close() {
    for (const site of [...this.sites.values()]) this.drop(site);
    this.closeLan();
    this.server.close();
    this.server.closeAllConnections?.();
  }
  /** On a signal (or a stray error, logged): every site's record goes and the process exits. */
  ownProcess() {
    const shutdown = () => {
      this.close();
      process.exit(0);
    };
    for (const signal of ["SIGINT", "SIGTERM", "SIGHUP"]) process.on(signal, shutdown);
    const stray = (error) => process.stderr.write(`[${(/* @__PURE__ */ new Date()).toISOString()}] uncaught: ${error instanceof Error ? error.stack ?? error.message : String(error)}
`);
    process.on("uncaughtException", stray);
    process.on("unhandledRejection", stray);
  }
  // ---- the sites -------------------------------------------------------------------------------------------------
  urlOf(site) {
    return `${serverOrigin(this.host, this.port)}${site.page}`;
  }
  stateOf(site) {
    const lan = site.share.lanUrls();
    return { pid: process.pid, url: this.urlOf(site), port: this.port, root: site.root, kind: this.kind, startedAt: this.startedAt.get(site.page) ?? (/* @__PURE__ */ new Date()).toISOString(), ...lan.length ? { lan } : {} };
  }
  /** Mounts a folder (already mounted: the same site), writing its <root>/.artifact-server.json. */
  add(root, options) {
    const mounted = [...this.sites.values()].find((site) => site.root === root);
    if (mounted) return (options.lan && !mounted.share.shared ? mounted.share.setLan(true) : Promise.resolve()).then(() => this.stateOf(mounted));
    const adding = this.adding.get(root);
    if (adding) return adding;
    const work = this.mount(root, options).finally(() => this.adding.delete(root));
    this.adding.set(root, work);
    return work;
  }
  async mount(root, { agentHook, lan = false }) {
    const file = path3.join(root, LOG_FILE);
    const log = (line) => {
      const text = `[${(/* @__PURE__ */ new Date()).toISOString()}] ${line}
`;
      try {
        fs3.appendFileSync(file, text);
      } catch {
      }
      if (this.echo) process.stderr.write(text);
    };
    const open2 = (other2) => this.add(other2, agentHook ? { agentHook } : {}).then((state2) => new URL(state2.url).pathname);
    const site = await this.factory(root, { log, network: this.network, ...agentHook ? { agentHook } : {}, open: open2 });
    const other = this.sites.get(site.page);
    if (other) {
      site.close();
      throw new SiteClash(`${other.root} is already open at ${site.page}.`);
    }
    this.sites.set(site.page, site);
    this.startedAt.set(site.page, (/* @__PURE__ */ new Date()).toISOString());
    try {
      await site.share.start(lan);
    } catch (error) {
      this.drop(site);
      throw error;
    }
    const state = this.stateOf(site);
    const { lan: _lan, ...record } = state;
    writeState(record);
    log(`serving ${root} at ${state.url}${agentHook ? `; each comment sent to the agent runs: ${agentHook}` : ""}`);
    return state;
  }
  drop(site) {
    this.sites.delete(site.page);
    this.startedAt.delete(site.page);
    removeState(site.root);
    site.close();
  }
  /** Ends one site; true when one was mounted there. The process ends with its last site. */
  remove(root) {
    const site = [...this.sites.values()].find((candidate) => candidate.root === root);
    if (site) this.drop(site);
    return site !== void 0;
  }
  // ---- the network side ------------------------------------------------------------------------------------------
  async openLan() {
    const addresses = lanAddresses().filter((address) => !this.lanServers.has(address));
    const answering = await Promise.all(addresses.map(answersAnyPort));
    for (const address of addresses.filter((_, i) => !answering[i])) {
      const server = this.createServer();
      try {
        await listen(server, this.port, address);
        this.lanServers.set(address, server);
      } catch (error) {
        server.close();
        process.stderr.write(`[${(/* @__PURE__ */ new Date()).toISOString()}] not listening on ${address}:${this.port}: ${errorText(error)}
`);
      }
    }
    return [...this.lanServers.keys()];
  }
  /** A site stopped sharing: the listeners stay while another is shared, or open to its owner on another device. */
  releaseLan() {
    if (![...this.sites.values()].some((site) => site.share.listening)) this.closeLan();
  }
  closeLan() {
    for (const server of this.lanServers.values()) {
      server.close();
      server.closeAllConnections?.();
    }
    this.lanServers.clear();
    this.lanNames.clear();
  }
  /** The machine's own names, as hostAllowed takes them. */
  isMachineName(name) {
    const machine = os2.hostname().toLowerCase();
    return name === machine || name === `${machine.replace(/\.local$/, "")}.local`;
  }
  /**
   * Answer at `name` too while listening: an address listened on, the machine's name, or a name that resolves to an
   * address listened on (looked up once, now: Tailscale's MagicDNS name, a hosts entry).
   */
  async allowName(name) {
    const lower = name.toLowerCase();
    if (!lower || !this.lanServers.size) return false;
    if (this.lanServers.has(lower) || this.isMachineName(lower) || this.lanNames.has(lower)) return true;
    const found = await dns.lookup(lower, { all: true, family: 4 }).catch(() => []);
    if (!found.some((entry) => this.lanServers.has(entry.address))) return false;
    this.lanNames.add(lower);
    return true;
  }
  /**
   * A Host header this hub answers: its own names, and while something is shared (or open to its owner on another
   * device), its LAN addresses, its machine name and the names allowName took.
   */
  hostAllowed(request) {
    const host = request.headers.host ?? "";
    if (this.hosts.has(host)) return true;
    if (!this.lanServers.size) return false;
    const suffix = `:${this.port}`;
    if (!host.endsWith(suffix)) return false;
    const name = host.slice(0, -suffix.length).toLowerCase();
    return this.lanServers.has(name) || this.isMachineName(name) || this.lanNames.has(name);
  }
  // ---- requests --------------------------------------------------------------------------------------------------
  /** The site whose address `pathname` is under, with the path below it. */
  under(pathname) {
    const [, first, second] = pathname.split("/");
    const site = first && second ? this.sites.get(`/${first}/${second}/`) : void 0;
    if (site) return { site, rest: pathname.slice(site.page.length - 1) };
    for (const candidate of this.sites.values()) if (candidate.claims?.(pathname)) return { site: candidate, rest: pathname };
    return null;
  }
  /** The site a page at this request's Referer belongs to. */
  referred(request) {
    const referer = request.headers.referer;
    if (typeof referer !== "string") return null;
    try {
      const at = new URL(referer);
      return at.host === request.headers.host ? this.under(at.pathname)?.site ?? null : null;
    } catch {
      return null;
    }
  }
  /** The sites this request's person may see. */
  seenBy(request) {
    return [...this.sites.values()].filter((site) => site.share.viewerOf(request));
  }
  async onRequest(request, response) {
    if (!this.hostAllowed(request)) {
      request.resume();
      response.writeHead(421, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }).end("Misdirected request");
      return;
    }
    const url = new URL(request.url ?? "/", "http://local");
    const pathname = url.pathname;
    if (pathname === HUB_ROUTE) return this.control(request, response);
    if (pathname === "/favicon.ico") {
      response.writeHead(204).end();
      return;
    }
    if (pathname === "/" || pathname === "/index.html") return this.landing(request, response, url.search);
    const at = this.under(pathname);
    if (at) {
      if (at.rest === "") {
        request.resume();
        response.writeHead(308, { Location: `${pathname}/${url.search}`, "Cache-Control": "no-store" }).end();
        return;
      }
      request.url = `${at.rest}${url.search}`;
      return at.site.handle(request, response);
    }
    const site = await this.answering(request, pathname);
    if (site) return site.handle(request, response);
    request.resume();
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }).end("Not found");
  }
  /** The site that answers a path outside every site's address. */
  async answering(request, pathname) {
    const link = /^\/s\/([A-Za-z0-9_-]{16,64})$/.exec(pathname);
    if (link) return [...this.sites.values()].find((site) => site.share.sharing.linkRole(link[1])) ?? null;
    const blob = /^\/_blob\/([0-9a-f]{32})$/.exec(pathname);
    if (blob) {
      const referred = this.referred(request);
      const seen = this.seenBy(request);
      for (const site of referred && seen.includes(referred) ? [referred, ...seen] : seen) if (await site.hasBlob?.(blob[1])) return site;
      return null;
    }
    for (const site of this.sites.values()) if (site.common?.(pathname)) return site;
    return this.referred(request);
  }
  /** `/`: where this person goes. */
  landing(request, response, search) {
    const seen = this.seenBy(request);
    const only = seen[0];
    if (seen.length === 1 && only) {
      request.resume();
      response.writeHead(302, { Location: `${only.page}${search}`, "Cache-Control": "no-store" }).end();
      return;
    }
    const any = only ?? [...this.sites.values()][0];
    if (!any) {
      request.resume();
      response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }).end("Nothing is open here.");
      return;
    }
    if (!only) return any.share.denied(request, response);
    any.share.sendList(response, seen.map((site) => ({ page: site.page, title: site.share.title() })));
  }
  /** The CLIs' route: over loopback, from a process (a browser's POST carries an Origin). */
  async control(request, response) {
    const info = { hub: 1, kind: this.kind, build: this.build, host: this.host, pid: process.pid };
    if (!isLoopback(request.socket.remoteAddress) || request.headers.origin !== void 0) {
      request.resume();
      return sendJson(response, 403, { code: "not_granted", message: "Only a local process can do this." });
    }
    if (request.method === "GET") return sendJson(response, 200, info);
    if (request.method !== "POST") {
      request.resume();
      return sendJson(response, 405, { code: "method_not_allowed", message: "GET or POST." });
    }
    let body;
    try {
      body = JSON.parse((await readBody(request, 64 << 10)).toString("utf8"));
    } catch {
      return sendJson(response, 400, { code: "invalid_argument", message: "The call is not JSON." });
    }
    if (typeof body.root !== "string" || !path3.isAbsolute(body.root)) return sendJson(response, 400, { code: "invalid_argument", message: "root: an absolute path." });
    if (body.action === "mount") {
      try {
        const state = await this.add(body.root, { ...typeof body.agentHook === "string" && body.agentHook ? { agentHook: body.agentHook } : {}, lan: body.lan === true });
        return sendJson(response, 200, { ...info, state });
      } catch (error) {
        sendJson(response, error instanceof SiteClash ? 409 : 400, { ...info, code: error.code ?? "SERVER_FAILED", message: errorText(error) });
        return this.endIfEmpty();
      }
    }
    if (body.action === "unmount") {
      const removed = this.remove(body.root);
      const remaining = this.sites.size;
      sendJson(response, 200, { ...info, removed, remaining });
      return this.endIfEmpty();
    }
    return sendJson(response, 400, { code: "invalid_argument", message: "action: mount or unmount." });
  }
  /** The process ends with its last site. */
  endIfEmpty() {
    if (this.sites.size > 0 || this.adding.size > 0) return;
    this.close();
    setImmediate(() => process.exit(0));
  }
  onUpgrade(request, socket, head) {
    socket.on("error", () => {
    });
    const url = new URL(request.url ?? "/", "http://local");
    const at = this.hostAllowed(request) && this.originOk(request) ? this.under(url.pathname) : null;
    if (!at) {
      socket.end("HTTP/1.1 403 Forbidden\r\n\r\n");
      return;
    }
    request.url = `${at.rest}${url.search}`;
    const asked = String(request.headers["sec-websocket-protocol"] ?? "").split(",").map((p) => p.trim());
    if (asked.includes(STREAM_PROTOCOL)) return this.stream(at.site, request, socket, head, url);
    if (at.site.upgrade) return at.site.upgrade(request, socket, head);
    socket.end("HTTP/1.1 404 Not Found\r\n\r\n");
  }
  originOk(request) {
    const origin = request.headers.origin;
    if (origin === void 0) return true;
    try {
      return new URL(origin).host === request.headers.host;
    } catch {
      return false;
    }
  }
  /** An event stream over a WebSocket: the site's handler answers it as a GET. */
  stream(site, request, socket, head, url) {
    const ws = acceptWebSocket(request, socket, head, STREAM_PROTOCOL);
    if (!ws) return;
    const last = url.searchParams.get("__lastEventId");
    if (last !== null) {
      request.headers["last-event-id"] = last;
      url.searchParams.delete("__lastEventId");
      request.url = `${request.url?.split("?")[0]}${url.search}`;
    }
    request.method = "GET";
    const response = new StreamResponse(ws);
    ws.handlers = {
      close: () => {
        response.closed();
        request.emit("close");
      }
    };
    Promise.resolve(site.handle(request, response)).catch(() => ws.close(STREAM_REFUSED + 500));
  }
};
async function hubAt(origin) {
  try {
    const response = await fetch(`${origin}${HUB_ROUTE}`, { signal: AbortSignal.timeout(1e3) });
    if (!response.ok) return null;
    const info = await response.json();
    return info.hub === 1 ? info : null;
  } catch {
    return null;
  }
}
async function joinHub(call, below = Infinity) {
  if (call.port === 0) return null;
  const ports = call.portGiven ? [call.port] : Array.from({ length: PORT_TRIES }, (_, i) => call.port + i).filter((port) => port <= 65535 && port < below);
  const build = buildOf(call.script);
  const origins = ports.map((port) => serverOrigin(call.host, port));
  const infos = await Promise.all(origins.map(hubAt));
  for (const [i, info] of infos.entries()) {
    if (!info || info.kind !== call.kind || info.build !== build || info.host !== call.host) continue;
    const response = await fetch(`${origins[i]}${HUB_ROUTE}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "mount", root: call.root, ...call.agentHook ? { agentHook: call.agentHook } : {}, lan: call.lan === true }),
      signal: AbortSignal.timeout(2e4)
    }).catch(() => null);
    if (!response) continue;
    const body = await response.json().catch(() => ({}));
    if (response.ok && body.state) return body.state;
    if (response.status === 409) continue;
    throw Object.assign(new Error(body.message ?? `the server answered ${response.status}`), { code: body.code ?? "SERVER_FAILED" });
  }
  return null;
}
async function leaveHub(state) {
  let remaining = 0;
  const response = await fetch(`${new URL(state.url).origin}${HUB_ROUTE}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "unmount", root: state.root }),
    signal: AbortSignal.timeout(5e3)
  }).catch(() => null);
  const body = response ? await response.json().catch(() => null) : null;
  if (body?.hub === 1) remaining = Number(body.remaining ?? 0);
  else if (alive(state.pid)) process.kill(state.pid, "SIGTERM");
  const deadline = Date.now() + 5e3;
  while (remaining === 0 && alive(state.pid) && Date.now() < deadline) await new Promise((resolve) => setTimeout(resolve, 100));
  if (remaining === 0 && alive(state.pid)) return false;
  fs3.rmSync(path3.join(state.root, STATE_FILE), { force: true });
  return true;
}
function holdSite(state) {
  const leave = () => {
    void leaveHub(state).finally(() => process.exit(0));
  };
  for (const signal of ["SIGINT", "SIGTERM", "SIGHUP"]) process.on(signal, leave);
  setInterval(() => {
    if (!alive(state.pid) || readState(state.root)?.pid !== state.pid) process.exit(0);
  }, 2e3);
}
async function serveHub(call) {
  const joined = await joinHub(call);
  const stayed = (state) => {
    if (!call.background) holdSite(state);
    return { ...state, joined: true };
  };
  if (joined) return stayed(joined);
  const hub = new Hub({ kind: call.kind, build: buildOf(call.script), host: call.host, site: call.site, echo: !call.background });
  const { state: sharing } = new Sharing(call.root);
  const linksPort = !call.portGiven && (call.lan || sharing.lan) ? sharing.port : void 0;
  const port = await hub.listen(call.port, linksPort);
  const lower = call.portGiven ? null : await joinHub(call, port);
  if (lower) {
    hub.close();
    return stayed(lower);
  }
  hub.ownProcess();
  try {
    return { ...await hub.add(call.root, { ...call.agentHook ? { agentHook: call.agentHook } : {}, lan: call.lan === true }), joined: false };
  } catch (error) {
    hub.close();
    throw error;
  }
}
async function openOnHub(call) {
  if (await loopbackBlocked(call.port || 1)) throw new NetworkBlocked();
  const joined = await joinHub(call);
  if (joined) return { state: joined };
  const logFile = path3.join(call.root, LOG_FILE);
  const fd = fs3.openSync(logFile, "a");
  const child = spawn(process.execPath, [...call.command, "--background"], { detached: true, stdio: ["ignore", "ignore", fd] });
  child.unref();
  fs3.closeSync(fd);
  let exited = false;
  child.once("exit", () => exited = true);
  const deadline = Date.now() + 15e3;
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 120));
    const state = await call.running();
    if (state) return { state };
    if (exited && !readState(call.root)) break;
  }
  return { tail: fs3.existsSync(logFile) ? fs3.readFileSync(logFile, "utf8").split("\n").slice(-12).join("\n") : "" };
}

import { createHash as createHash3 } from "node:crypto";
import fs6 from "node:fs";
import os4 from "node:os";
import path6 from "node:path";

import fs4 from "node:fs";
import fsp from "node:fs/promises";
import path4 from "node:path";
import { promisify } from "node:util";
import zlib from "node:zlib";
var LOCAL_FILES = /* @__PURE__ */ new Set([STATE_FILE, LOG_FILE, SHARING_FILE]);
var LOCAL_DIRS = /* @__PURE__ */ new Set([EXPORTS_DIR]);
var JUNK_FILES = /* @__PURE__ */ new Set([".DS_Store", "Thumbs.db", "desktop.ini", ".git"]);
var isTemp = (name) => name.endsWith(".tmp") || name.startsWith(".tmp-");
var STORED = /* @__PURE__ */ new Set([".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".heic", ".mp4", ".m4v", ".mov", ".webm", ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".flac", ".woff", ".woff2", ".zip", ".gz", ".br", ".zst", ".7z"]);
var MAX_ENTRIES = 65535;
var MAX_BYTES = 4294967295;
var ArchiveTooLarge = class extends Error {
  code = "TOO_LARGE";
};
async function archiveEntries(root, skip = []) {
  const folder = path4.basename(path4.resolve(root)) || "artifact";
  const skipped = new Set(skip.map((file) => path4.resolve(file)));
  const entries = [];
  const walk = async (dir, rel) => {
    let names;
    try {
      names = await fsp.readdir(dir, { withFileTypes: true });
    } catch (error) {
      if (rel && error.code === "ENOENT") return;
      throw error;
    }
    for (const dirent of names.sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)) {
      const name = dirent.name;
      if (JUNK_FILES.has(name) || isTemp(name) || !rel && (LOCAL_FILES.has(name) || LOCAL_DIRS.has(name) && dirent.isDirectory())) continue;
      const file = path4.join(dir, name);
      if (skipped.has(file)) continue;
      const inner = rel ? `${rel}/${name}` : name;
      if (dirent.isDirectory()) await walk(file, inner);
      else if (dirent.isFile()) {
        const stat = await fsp.stat(file).catch(() => null);
        if (stat?.isFile()) entries.push({ name: `${folder}/${inner}`, file, size: stat.size, mode: stat.mode & 511, mtime: stat.mtime });
      }
    }
  };
  await walk(path4.resolve(root), "");
  if (entries.length > MAX_ENTRIES) throw new ArchiveTooLarge(`The folder holds ${entries.length} files, more than a zip holds (${MAX_ENTRIES}); copy the folder itself instead.`);
  const bound = entries.reduce((sum, entry) => sum + entry.size + 2 * (46 + Buffer.byteLength(entry.name)), 22);
  if (bound > MAX_BYTES) throw new ArchiveTooLarge(`The folder holds ${(bound / 2 ** 30).toFixed(1)} GiB, more than a zip holds (4 GiB); copy the folder itself instead.`);
  return entries;
}
var CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 3988292384 ^ c >>> 1 : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();
function crc32(bytes) {
  let crc = 4294967295;
  for (let i = 0; i < bytes.length; i++) crc = CRC_TABLE[(crc ^ bytes[i]) & 255] ^ crc >>> 8;
  return (crc ^ 4294967295) >>> 0;
}
function dosTime(date) {
  const year = date.getFullYear();
  if (year < 1980) return { time: 0, date: 1 << 5 | 1 };
  if (year > 2107) return { time: 23 << 11 | 59 << 5 | 29, date: 127 << 9 | 12 << 5 | 31 };
  return {
    time: date.getHours() << 11 | date.getMinutes() << 5 | date.getSeconds() >> 1,
    date: year - 1980 << 9 | date.getMonth() + 1 << 5 | date.getDate()
  };
}
var deflateRaw = promisify(zlib.deflateRaw);
var UTF8 = 1 << 11;
async function writeZip(entries, write) {
  const central = [];
  let offset = 0;
  const put = async (chunk) => {
    await write(chunk);
    offset += chunk.length;
  };
  for (const entry of entries) {
    let data;
    try {
      data = entry.data ?? await fsp.readFile(entry.file);
    } catch (error) {
      if (error.code === "ENOENT") continue;
      throw error;
    }
    const crc = crc32(data);
    let method = 0;
    let body = data;
    if (data.length > 0 && !STORED.has(path4.extname(entry.name).toLowerCase())) {
      const deflated = await deflateRaw(data);
      if (deflated.length < data.length) {
        method = 8;
        body = deflated;
      }
    }
    if (offset + body.length > MAX_BYTES) throw new ArchiveTooLarge("The folder grew past what a zip holds (4 GiB) while it was being zipped.");
    const name = Buffer.from(entry.name, "utf8");
    const { time, date } = dosTime(entry.mtime);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(67324752, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(UTF8, 6);
    local.writeUInt16LE(method, 8);
    local.writeUInt16LE(time, 10);
    local.writeUInt16LE(date, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(body.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(name.length, 26);
    local.writeUInt16LE(0, 28);
    const header = Buffer.alloc(46);
    header.writeUInt32LE(33639248, 0);
    header.writeUInt16LE(3 << 8 | 20, 4);
    header.writeUInt16LE(20, 6);
    header.writeUInt16LE(UTF8, 8);
    header.writeUInt16LE(method, 10);
    header.writeUInt16LE(time, 12);
    header.writeUInt16LE(date, 14);
    header.writeUInt32LE(crc, 16);
    header.writeUInt32LE(body.length, 20);
    header.writeUInt32LE(data.length, 24);
    header.writeUInt16LE(name.length, 28);
    header.writeUInt32LE((32768 | (entry.mode || 420) | 384) << 16 >>> 0, 38);
    header.writeUInt32LE(offset, 42);
    central.push(header, name);
    await put(Buffer.concat([local, name]));
    await put(body);
  }
  const start = offset;
  const directory = Buffer.concat(central);
  await put(directory);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(101010256, 0);
  end.writeUInt16LE(central.length / 2, 8);
  end.writeUInt16LE(central.length / 2, 10);
  end.writeUInt32LE(directory.length, 12);
  end.writeUInt32LE(start, 16);
  await put(end);
  return offset;
}
function archiveFileName(root, now = /* @__PURE__ */ new Date()) {
  const day = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
  return `${path4.basename(path4.resolve(root)) || "artifact"}-${day}.zip`;
}
async function writeArchive(root, out) {
  const file = path4.resolve(out);
  const entries = await archiveEntries(root, [file]);
  const tmp = path4.join(path4.dirname(file), `.${path4.basename(file)}.${process.pid}.tmp`);
  const handle = await fsp.open(tmp, "w");
  let bytes;
  try {
    bytes = await writeZip(entries, async (chunk) => {
      await handle.write(chunk);
    });
    await handle.close();
  } catch (error) {
    await handle.close().catch(() => {
    });
    await fsp.rm(tmp, { force: true });
    throw error;
  }
  await fsp.rename(tmp, file);
  return { file, files: entries.length, bytes };
}
async function archiveCommand(root, out) {
  const where = out ? path4.resolve(out) : path4.dirname(path4.resolve(root));
  const target = fs4.statSync(where, { throwIfNoEntry: false })?.isDirectory() ? path4.join(where, archiveFileName(root)) : where;
  const { file, files, bytes } = await writeArchive(root, target);
  return { file, folder: path4.basename(path4.resolve(root)), files, bytes, leftOut: [...LOCAL_FILES] };
}
function attachment(name) {
  const ascii = name.replace(/[^\x20-\x7e]|["\\]/g, "_");
  return `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(name)}`;
}
async function sendArchive(request, response, root) {
  request.resume();
  let entries;
  try {
    entries = await archiveEntries(root);
  } catch (error) {
    const text = JSON.stringify({ code: error instanceof ArchiveTooLarge ? "too_large" : "upstream_error", message: error instanceof Error ? error.message : String(error) });
    response.writeHead(error instanceof ArchiveTooLarge ? 413 : 500, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }).end(text);
    return;
  }
  response.writeHead(200, {
    "Content-Type": "application/zip",
    "Content-Disposition": attachment(archiveFileName(root)),
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff"
  });
  if (request.method === "HEAD") {
    response.end();
    return;
  }
  const write = (chunk) => new Promise((resolve, reject) => {
    if (response.destroyed) return reject(new Error("The download was cancelled."));
    if (response.write(chunk)) return resolve();
    const drained = () => {
      response.off("close", closed);
      resolve();
    };
    const closed = () => {
      response.off("drain", drained);
      reject(new Error("The download was cancelled."));
    };
    response.once("drain", drained);
    response.once("close", closed);
  });
  try {
    await writeZip(entries, write);
    response.end();
  } catch {
    response.destroy();
  }
}

import fs5 from "node:fs";
import fsp2 from "node:fs/promises";
import os3 from "node:os";
import path5 from "node:path";
var MAX_BYTES2 = 4294967295;
function shown(file) {
  const home = os3.homedir();
  return home && (file === home || file.startsWith(home + path5.sep)) ? `~${file.slice(home.length)}` : file;
}
function saved(file, bytes) {
  return { path: file, name: path5.basename(file), folder: path5.dirname(file), shown: shown(file), bytes };
}
function safeFileName(raw) {
  let name = (raw.replace(/\\/g, "/").split("/").pop() ?? "").replace(/[\u0000-\u001f\u007f<>:"|?*]/g, "_").replace(/^[.\s]+|[.\s]+$/g, "");
  if (name.length > 200) {
    const ext = path5.extname(name).slice(0, 16);
    name = name.slice(0, 200 - ext.length) + ext;
  }
  return name || "download";
}
async function openFree(dir, name) {
  const ext = path5.extname(name);
  const stem = name.slice(0, name.length - ext.length);
  for (let n = 0; ; n++) {
    const file = path5.join(dir, n === 0 ? name : `${stem} (${n})${ext}`);
    try {
      return { file, handle: await fsp2.open(file, "wx") };
    } catch (error) {
      if (error.code !== "EEXIST" || n >= 999) throw error;
    }
  }
}
async function saveDownload(request, response, root) {
  const declared = Number(request.headers["content-length"]);
  if (Number.isFinite(declared) && declared > MAX_BYTES2) {
    request.resume();
    return sendJson(response, 413, { code: "too_large", message: "The file is over 4 GiB." });
  }
  const name = safeFileName(new URL(request.url ?? "/", "http://local").searchParams.get("name") ?? "");
  let file = "";
  let handle = null;
  let bytes = 0;
  try {
    const dir = path5.join(root, EXPORTS_DIR);
    await fsp2.mkdir(dir, { recursive: true });
    ({ file, handle } = await openFree(dir, name));
    for await (const chunk of request) {
      bytes += chunk.length;
      if (bytes > MAX_BYTES2) throw Object.assign(new Error("The file is over 4 GiB."), { status: 413 });
      await handle.write(chunk);
    }
    await handle.close();
    handle = null;
  } catch (error) {
    await handle?.close().catch(() => {
    });
    if (file) await fsp2.rm(file, { force: true });
    request.resume();
    const status = error.status ?? 500;
    if (!response.headersSent) sendJson(response, status, { code: status === 413 ? "too_large" : "upstream_error", message: error instanceof Error ? error.message : String(error) });
    return;
  }
  sendJson(response, 200, saved(file, bytes));
}
async function saveArchive(request, response, root) {
  request.resume();
  try {
    const { file } = await archiveCommand(root, void 0);
    sendJson(response, 200, saved(file, fs5.statSync(file).size));
  } catch (error) {
    const tooLarge = error instanceof ArchiveTooLarge;
    sendJson(response, tooLarge ? 413 : 500, { code: tooLarge ? "too_large" : "upstream_error", message: error instanceof Error ? error.message : String(error) });
  }
}

var ShareError = class extends Error {
};
var canEditAs = (role) => role === "owner" || role === "editor";
function commentsViewer(viewer) {
  return {
    author: viewer.guest ? { kind: "user", name: viewer.user.name, principal: viewer.user.email } : { kind: "user", name: viewer.user.name },
    canComment: viewer.role !== "viewer",
    canSend: viewer.role === "owner",
    admin: viewer.role === "owner"
  };
}
var isRecord2 = (value) => typeof value === "object" && value !== null && !Array.isArray(value);
var esc = (text) => text.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
var script = (value) => JSON.stringify(value).replace(/</g, "\\u003c");
function hostName(host) {
  const value = host.trim().toLowerCase();
  if (value.startsWith("[")) return value.slice(1, value.indexOf("]") > 0 ? value.indexOf("]") : void 0);
  const colons = value.split(":").length - 1;
  return colons === 1 ? value.slice(0, value.indexOf(":")) : value;
}
function localOwner() {
  let name = "You";
  try {
    name = os4.userInfo().username.trim() || name;
  } catch {
  }
  return { id: "local", name, email: `${name}@localhost` };
}
var guestCookieName = (kind, root) => `${kind.replace(/-/g, "_")}_guest_${createHash3("sha256").update(path6.resolve(root)).digest("hex").slice(0, 12)}`;
function dbAccess(viewer, segs, adminRead = /* @__PURE__ */ new Set()) {
  const admin = canEditAs(viewer.role);
  const read = segs[0] === "data" && segs[1] === "users" && segs.length > 2 ? segs[2] === viewer.user.id : admin || !adminRead.has(segs[0] ?? "");
  return { read, write: read && admin };
}
var ShareHost = class {
  sharing;
  options;
  network;
  page;
  /** Open to the local network now (the hub's listeners are up, for this artifact too). */
  on = false;
  /** Open to its owner on another device (`open --remote`): the listeners are up, guests stay out unless `on`. */
  remote = false;
  live = /* @__PURE__ */ new Set();
  constructor(options) {
    this.options = options;
    this.network = options.network;
    this.page = options.page;
    this.sharing = new Sharing(options.root);
  }
  get port() {
    return this.network.port;
  }
  /** The hub took the artifact: open to the network now with `lan`, or if it was left shared. */
  async start(lan = false) {
    const { state } = this.sharing;
    if (!lan && !state.lan) return;
    if (state.port && state.port !== this.port) this.options.log(`port ${state.port} (the shared links') is not this server's; it is on ${this.port}: give the new links out again`);
    await this.setLan(true);
  }
  /** The artifact at each LAN address it is shared on ([] while it is not). */
  lanUrls() {
    return this.on ? this.network.addresses().map((a) => `http://${a}:${this.port}${this.page}`) : [];
  }
  /** Open to the local network now. */
  get shared() {
    return this.on;
  }
  /** Someone may reach it over the network now (guests, or its owner on another device): the hub keeps listening. */
  get listening() {
    return this.on || this.remote;
  }
  /** The artifact's name, for the join page and the list of what is open at the server's root. */
  title() {
    return this.options.title();
  }
  /**
   * Opens the artifact to the local network or closes it, and returns the addresses it is on. Guests already in keep
   * their place for when it opens again.
   */
  async setLan(on) {
    if (!on) {
      this.on = false;
      this.network.release();
      for (const live of [...this.live]) if (live.viewer.guest) live.close("unshared");
      if (this.sharing.state.lan) this.sharing.setLan(false);
      return [];
    }
    const addresses = await this.network.open();
    this.on = addresses.length > 0;
    if (!this.sharing.state.lan || this.sharing.state.port !== this.port) this.sharing.setLan(true, this.port);
    this.options.log(`shared on the local network: ${addresses.map((a) => `http://${a}:${this.port}${this.page}`).join(", ") || "(no LAN address)"}`);
    return addresses;
  }
  /**
   * Opens the artifact to its owner on another device, or closes that, and returns the owner's link, at `host` when
   * that is this computer's (the address the owner's browser already reaches it by), else at its first network address.
   * Guests are not let in by it: that is `setLan`.
   */
  async setRemote(on, host) {
    if (!on) {
      this.remote = false;
      for (const live of [...this.live]) if (live.viewer.remote) live.close("unshared");
      this.network.release();
      return null;
    }
    const addresses = await this.network.open();
    if (!addresses.length) {
      this.network.release();
      throw new ShareError("This computer has no network address to open it at.");
    }
    this.remote = true;
    const name = hostName(host ?? "");
    const sorted = [...addresses].sort((a, b) => Number(isTailnet(a)) - Number(isTailnet(b)));
    const address = name && (addresses.includes(name) || await this.network.allowName?.(name)) ? name : sorted[0];
    const url = `http://${address.includes(":") ? `[${address}]` : address}:${this.port}${this.page}o/${this.sharing.ownerToken()}`;
    this.options.log(`open to its owner on another device at http://${address}:${this.port}${this.page}`);
    return { url, address };
  }
  /** The artifact left the hub: it stays shared in .sharing.json, for the next time it opens. */
  close() {
    this.on = false;
    this.remote = false;
    this.network.release();
  }
  // ---- who is asking ---------------------------------------------------------------------------------------------
  cookie(request, name = this.options.cookieName) {
    for (const part of (request.headers.cookie ?? "").split(";")) {
      const eq = part.indexOf("=");
      if (eq > 0 && part.slice(0, eq).trim() === name) return part.slice(eq + 1).trim();
    }
    return void 0;
  }
  /** The cookie the owner's link leaves in a browser on another device. */
  get ownerCookie() {
    return `${this.options.cookieName}_owner`;
  }
  /**
   * Who a request is: the owner over loopback, or by the owner's link's cookie while the artifact is open to them on
   * another device; a guest by their cookie (while their link is on and the artifact is shared), else nobody. Loopback
   * is always the owner, so trying a link on this computer can't lock the owner out of their own artifact; a guest
   * comes over a LAN address (this computer's own included: that is how the owner sees what a role sees).
   */
  isLocal(request) {
    return this.options.local ? this.options.local(request) : isLoopback(request.socket.remoteAddress);
  }
  viewerOf(request) {
    if (this.isLocal(request)) return { role: "owner", user: this.options.owner };
    if (this.remote && this.sharing.isOwnerToken(this.cookie(request, this.ownerCookie))) return { role: "owner", user: this.options.owner, remote: true };
    const guest = this.on ? this.sharing.guest(this.cookie(request)) : null;
    if (!guest) return null;
    this.sharing.seen(guest);
    return { role: guest.role, user: guestUser(guest), guest };
  }
  /** Keeps track of a stream or socket `viewer` holds open; call the returned function when it closes. */
  attach(viewer, close) {
    const live = { viewer, close };
    this.live.add(live);
    return () => this.live.delete(live);
  }
  /** `attach` for an HTTP stream (server-sent events): it ends when its person loses access. */
  hold(viewer, response) {
    const detach = this.attach(viewer, () => response.end());
    response.on("close", detach);
  }
  /** Still allowed in: the owner, or a guest whose link is on and who was not removed. */
  stillIn(viewer) {
    return !viewer.guest || this.on && this.sharing.valid(viewer.guest);
  }
  /** Ends the streams of guests who lost access (a link turned off or reset, a guest removed). */
  dropRevoked() {
    for (const live of [...this.live]) if (live.viewer.guest && !this.sharing.valid(live.viewer.guest)) live.close("revoked");
  }
  me(viewer) {
    return { role: viewer.role, id: viewer.user.id, name: viewer.user.name, email: viewer.user.email };
  }
  // ---- routes ----------------------------------------------------------------------------------------------------
  /** Answers the share link and /__share paths; false for any other path. */
  async route(request, response) {
    const p = new URL(request.url ?? "/", "http://local").pathname;
    const method = request.method ?? "GET";
    const link = /^\/s\/([A-Za-z0-9_-]{16,64})$/.exec(p);
    const ownerLink = /^\/o\/([A-Za-z0-9_-]{16,64})$/.exec(p);
    const ours = link || ownerLink || p === "/__share" || p.startsWith("/__share/");
    if (!ours) return false;
    if (method === "POST" && !sameOrigin(request)) {
      request.resume();
      sendJson(response, 403, { code: "not_granted", message: "Cross-origin write refused." });
      return true;
    }
    if (link) {
      if (method === "GET" || method === "POST") await this.join(request, response, method, link[1]);
      else response.writeHead(405, { Allow: "GET, POST" }).end();
      return true;
    }
    if (ownerLink) {
      request.resume();
      if (method === "GET" || method === "HEAD") this.ownerIn(request, response, ownerLink[1]);
      else response.writeHead(405, { Allow: "GET" }).end();
      return true;
    }
    const viewer = this.viewerOf(request);
    if (!viewer) {
      this.denied(request, response);
      return true;
    }
    if (method === "GET" && p === "/__share/me") return sendJson(response, 200, this.me(viewer)), true;
    if (method === "GET" && p === "/__share/boot.js") {
      const body = this.bootScript(viewer, new URL(request.url ?? "/", "http://local").searchParams);
      response.writeHead(200, { "Content-Type": "text/javascript; charset=utf-8", "Content-Length": Buffer.byteLength(body), "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" }).end(body);
      return true;
    }
    if (method === "GET" && p === "/__share/invite") return sendJson(response, 200, this.invites(viewer, request.headers.host ?? "")), true;
    if (method === "GET" && p === "/__share/ui.js") {
      fs6.stat(this.options.uiFile, (error, stat) => {
        if (error || !stat.isFile()) return sendJson(response, 404, { code: "not_found", message: "The Share panel is missing." });
        sendFile(request, response, this.options.uiFile, { "Content-Type": "text/javascript; charset=utf-8", "Content-Length": stat.size, "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
      });
      return true;
    }
    if (viewer.role !== "owner") return sendJson(response, 403, { code: "not_granted", message: "Only the owner can do this." }), true;
    if ((method === "GET" || method === "HEAD") && p === "/__share/archive") return await sendArchive(request, response, this.options.root), true;
    if (method === "POST" && p === "/__share/archive") return await saveArchive(request, response, this.options.root), true;
    if (method === "POST" && p === "/__share/save") return await saveDownload(request, response, this.options.root), true;
    if (p === "/__share") return await this.shareApi(request, response, method), true;
    sendJson(response, 404, { code: "not_found", message: "Not found" });
    return true;
  }
  /**
   * The tags a page puts first in its <head>: the boot script and the Share panel (the owner's, or a guest's). `query`
   * ("?…") goes to the boot script, for `globals`.
   */
  headTags(_viewer, query = "") {
    let tags = `<script src="${this.page}__share/boot.js${query.replace(/[<>"']/g, "").replace(/&/g, "&amp;")}"></script>`;
    if (fs6.existsSync(this.options.uiFile)) tags += `<script type="module" src="${this.page}__share/ui.js"></script>`;
    return tags;
  }
  /** `html` with the head tags first in its <head>; null when it has none. */
  injectHead(html, viewer, query = "") {
    const at = html.search(/<head(\s[^>]*)?>/i);
    if (at < 0) return null;
    const end = html.indexOf(">", at) + 1;
    return html.slice(0, end) + this.headTags(viewer, query) + html.slice(end);
  }
  /** What the page runs before anything else (see ROOT_SHIM, SECURE_CONTEXT_SHIM and GUEST_WATCH). */
  bootScript(viewer, query = new URLSearchParams()) {
    const share2 = { ...this.me(viewer), noun: this.options.noun, title: this.options.title(), ...this.options.reactions ? { reactions: true } : {} };
    let js = `(function(BASE){${ROOT_SHIM}})(${script(this.page)});${SECURE_CONTEXT_SHIM}window.__baoyuShare=${script(share2)};`;
    for (const [name, value] of Object.entries(this.options.globals?.(viewer, query) ?? {})) js += `window[${script(name)}]=${script(value)};`;
    if (this.options.agentName) js += `window.__baoyuAgentName=${script(this.options.agentName)};`;
    if (viewer.guest) js += GUEST_WATCH;
    return js;
  }
  /** Nobody's request: a page for a browser's navigation, JSON for anything else. */
  denied(request, response) {
    request.resume();
    const navigation = (request.method === "GET" || request.method === "HEAD") && /\btext\/html\b/.test(request.headers.accept ?? "");
    if (!navigation) return sendJson(response, 403, { code: "not_granted", message: `This ${this.options.noun.en} is not shared with you.` });
    const t = this.words(request);
    this.sendPage(response, 403, t.noAccessTitle, `<h1>${esc(t.noAccessTitle)}</h1><p>${esc(t.noAccess)}</p>${this.ownerHint(request, t)}`);
  }
  /** `/` on the server for someone who may see more than one artifact: a page of links. */
  sendList(response, sites) {
    const noun = this.options.noun.en;
    this.sendPage(response, 200, `Open ${noun}s`, `<h1>Open ${esc(noun)}s</h1><ul>${sites.map((site) => `<li><a href="${esc(site.page)}">${esc(site.title)}</a></li>`).join("")}</ul>`);
  }
  /** A small page of our own (the join form, the refusal), in the reader's language. */
  sendPage(response, status, title, body, headers = {}) {
    const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><style>${PAGE_CSS}</style></head><body><main>${body}</main></body></html>`;
    response.writeHead(status, {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'",
      ...headers
    }).end(html);
  }
  /** On the computer that shares the artifact, over its LAN address: the way back to the owner's page. */
  ownerHint(request, t) {
    const from = (request.socket.remoteAddress ?? "").replace(/^::ffff:/, "");
    if (!this.network.addresses().includes(from)) return "";
    const url = `http://127.0.0.1:${this.port}${this.page}`;
    return `<p class="note">${esc(t.ownerHere)} <a href="${esc(url)}">${esc(url)}</a></p>`;
  }
  /**
   * GET /o/<token>: the owner's link. On another device it leaves the owner's cookie (while the artifact is open to them
   * there) and goes on to the page, its query kept (`?comment=` opens a thread); over loopback it is the page anyway.
   */
  ownerIn(request, response, token2) {
    const local = this.isLocal(request);
    if (!this.sharing.isOwnerToken(token2) || !local && !this.remote) {
      const t = this.words(request);
      return this.sendPage(response, 404, t.linkGoneTitle, `<h1>${esc(t.linkGoneTitle)}</h1><p>${esc(t.linkGone)}</p>`);
    }
    const search = new URL(request.url ?? "/", "http://local").search;
    const headers = { Location: `${this.page}${search}`, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" };
    if (!local) {
      headers["Set-Cookie"] = `${this.ownerCookie}=${token2}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000`;
      this.options.log(`share: the owner came in from another device (${request.socket.remoteAddress})`);
    }
    response.writeHead(303, headers).end();
  }
  /** GET /s/<token>: the name form (or straight in, for a guest already in through this link); POST: join. */
  async join(request, response, method, token2) {
    const t = this.words(request);
    const role = this.sharing.linkRole(token2);
    const local = this.isLocal(request);
    const form = method === "POST" ? await readBody(request, 8 << 10).then((body) => body.toString("utf8"), () => "") : "";
    const title = this.options.title();
    if (!role || !local && !this.on) return this.sendPage(response, 404, t.linkGoneTitle, `<h1>${esc(t.linkGoneTitle)}</h1><p>${esc(t.linkGone)}</p>`);
    if (local) {
      const lan = this.on ? this.network.addresses()[0] : void 0;
      const there = lan ? `http://${lan}:${this.port}${this.page}s/${token2}` : "";
      const tryIt = there ? `<p>${esc(t.tryRole(t.roles[role]))} <a href="${esc(there)}">${esc(there)}</a></p>` : "";
      return this.sendPage(response, 200, title, `<h1>${esc(title)}</h1><p>${esc(t.youOwn)} <a href="${esc(this.page)}">${esc(t.openAsOwner)}</a></p>${tryIt}`);
    }
    const current = this.sharing.guest(this.cookie(request));
    if (method === "GET" && current && current.link === this.sharing.state.links[role].token) {
      response.writeHead(303, { Location: this.page, "Cache-Control": "no-store" }).end();
      return;
    }
    if (method === "GET") {
      return this.sendPage(
        response,
        200,
        title,
        `<h1>${esc(title)}</h1><p>${esc(t.invited(t.roles[role]))}</p><form method="post"><label for="n">${esc(t.yourName)}</label><input id="n" name="name" maxlength="${MAX_NAME}" value="${esc(current?.name ?? "")}" required autofocus autocomplete="name"><button type="submit">${esc(t.open)}</button></form><p class="note">${esc(t.nameNote)}</p>`
      );
    }
    const name = new URLSearchParams(form).get("name") ?? "";
    const guest = this.sharing.join(role, name);
    this.options.log(`share: ${guest.name} joined as ${role} (${request.socket.remoteAddress})`);
    const cookie = `${this.options.cookieName}=${guest.secret}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000`;
    response.writeHead(303, { Location: this.page, "Set-Cookie": cookie, "Cache-Control": "no-store" }).end();
  }
  /**
   * The links this person may pass on: their own role's and the ones below it that are on (the owner: every one on), at
   * the address they came by (`host`, a Host header the hub let in). A guest could forward the link they joined
   * with anyway; a lower one gives no more than that. Who joins through one shows in the owner's panel like anyone else.
   */
  invites(viewer, host) {
    const { links } = this.sharing.state;
    const from = viewer.role === "owner" ? 0 : GUEST_ROLES.indexOf(viewer.role);
    return { links: GUEST_ROLES.slice(from).filter((role) => links[role].on).map((role) => ({ role, url: `http://${host}${this.page}s/${links[role].token}` })) };
  }
  /** Links, addresses and people, for the share panel and `artifact.mjs share`. */
  shareView() {
    const addresses = (this.on ? this.network.addresses() : []).sort((a, b) => Number(isTailnet(a)) - Number(isTailnet(b)));
    const local = addresses.filter((a) => !isTailnet(a));
    const base = local.length ? `http://${local[0]}:${this.port}` : addresses.length ? `http://${addresses[0]}:${this.port}` : `http://127.0.0.1:${this.port}`;
    const tailnet = addresses.find(isTailnet);
    const online = /* @__PURE__ */ new Set();
    for (const live of this.live) if (live.viewer.guest) online.add(live.viewer.guest.id);
    const { links, guests } = this.sharing.state;
    const lan = addresses.length ? addresses : [...lanAddresses()].sort((a, b) => Number(isTailnet(a)) - Number(isTailnet(b)));
    const network = lan.length ? `http://${lan[0]}:${this.port}` : base;
    return {
      title: this.options.title(),
      lan: this.on,
      remote: this.remote,
      port: this.port,
      page: this.page,
      addresses,
      local: `http://127.0.0.1:${this.port}${this.page}`,
      links: Object.fromEntries(GUEST_ROLES.map((role) => [role, { on: links[role].on, url: `${base}${this.page}s/${links[role].token}`, networkUrl: `${network}${this.page}s/${links[role].token}` }])),
      ...tailnet ? { tailnet: { address: tailnet, links: Object.fromEntries(GUEST_ROLES.map((role) => [role, { on: links[role].on, url: `http://${tailnet}:${this.port}${this.page}s/${links[role].token}` }])) } } : {},
      guests: guests.filter((g) => this.sharing.valid(g) || links[g.role].token === g.link).map((g) => ({ id: g.id, name: g.name, role: g.role, joined: g.joined, ...g.seen ? { seen: g.seen } : {}, online: online.has(g.id), active: this.sharing.valid(g) }))
    };
  }
  /**
   * The owner's sharing calls: `lan` {on}, `link` {role, on}, `reset` {role} (a new link: the old one and the guests
   * who came through it stop working; role `owner` the owner's own link), `role` {guest, role} (a guest's role, while
   * that role's link is on), `remove` {guest}, `remote` {on, host?} (open to the owner on another device: the answer
   * then has `remoteLink` {url, address}, the owner's link). Answers the view after.
   */
  async share(action) {
    const role = action.role;
    let remote = null;
    switch (action.action) {
      case "lan": {
        const addresses = await this.setLan(action.on === true);
        if (action.on === true && !addresses.length) throw new ShareError("This computer has no local network address to share on.");
        break;
      }
      case "link":
        if (!isGuestRole(role)) throw new ShareError("role: editor, commenter or viewer");
        this.sharing.setLink(role, action.on === true);
        break;
      case "reset":
        if (role === "owner") {
          this.sharing.resetOwner();
          for (const live of [...this.live]) if (live.viewer.remote) live.close("revoked");
          break;
        }
        if (!isGuestRole(role)) throw new ShareError("role: owner, editor, commenter or viewer");
        this.sharing.resetLink(role);
        break;
      case "remote":
        remote = await this.setRemote(action.on === true, typeof action.host === "string" ? action.host : void 0);
        break;
      case "role": {
        if (!isGuestRole(role)) throw new ShareError("role: editor, commenter or viewer");
        if (typeof action.guest !== "string" || !this.sharing.state.guests.some((g) => g.id === action.guest)) throw new ShareError("no such guest");
        if (!this.sharing.setRole(action.guest, role)) throw new ShareError(`The ${role} link is off: turn it on first.`);
        for (const live of [...this.live]) if (live.viewer.guest?.id === action.guest) live.close("revoked");
        break;
      }
      case "remove":
        if (typeof action.guest !== "string" || !this.sharing.removeGuest(action.guest)) throw new ShareError("no such guest");
        break;
      default:
        throw new ShareError("action: lan, link, reset, role, remove or remote");
    }
    this.options.log(`share: ${JSON.stringify(action)}`);
    this.dropRevoked();
    return { ...this.shareView(), ...remote ? { remoteLink: remote } : {} };
  }
  async shareApi(request, response, method) {
    if (method === "GET") return sendJson(response, 200, this.shareView());
    if (method !== "POST") return sendJson(response, 405, { code: "method_not_allowed", message: `${method} is not allowed here.` });
    let action;
    try {
      action = JSON.parse((await readBody(request, 64 << 10)).toString("utf8"));
    } catch {
      return sendJson(response, 400, { code: "invalid_argument", message: "The call is not JSON." });
    }
    if (!isRecord2(action)) return sendJson(response, 400, { code: "invalid_argument", message: "Expected {action, ...}." });
    try {
      return sendJson(response, 200, await this.share(action));
    } catch (error) {
      if (error instanceof ShareError) return sendJson(response, 400, { code: "invalid_argument", message: error.message });
      throw error;
    }
  }
  words(request) {
    const zh = /^zh\b/i.test(request.headers["accept-language"] ?? "");
    return (zh ? ZH : EN)(this.options.noun);
  }
};
var ROOT_SHIM = `
var P=location.protocol==='https:'?'wss:':'ws:';
function under(u){try{var a=new URL(String(u),location.href);if(a.host===location.host&&/^(https?|wss?):$/.test(a.protocol)&&a.pathname.indexOf(BASE)!==0)a.pathname=BASE+a.pathname.slice(1);return a.href}catch(e){return u}}
var F=window.fetch;
window.fetch=function(i,o){if(typeof Request==='function'&&i instanceof Request){var r=under(i.url);return F.call(this,r===i.url?i:new Request(r,i),o)}return F.call(this,under(i&&i.href||i),o)};
var X=XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open=function(m,u){var a=[].slice.call(arguments);a[1]=under(u);return X.apply(this,a)};
var W=window.WebSocket;
function WS(u,p){return p===undefined?new W(under(u)):new W(under(u),p)}
WS.prototype=W.prototype;WS.CONNECTING=0;WS.OPEN=1;WS.CLOSING=2;WS.CLOSED=3;
window.WebSocket=WS;
if(navigator.sendBeacon){var B=navigator.sendBeacon;navigator.sendBeacon=function(u,d){return B.call(navigator,under(u),d)}}
class S extends EventTarget{
constructor(u){super();this.url=under(u);this.withCredentials=false;this.readyState=0;this.onopen=this.onmessage=this.onerror=null;this.l='';this.c()}
c(){var t=this,a=new URL(t.url);a.protocol=P;if(t.l)a.searchParams.set('__lastEventId',t.l);var w=t.w=new W(a.href,'baoyu-sse'),b='';
w.onopen=function(){t.readyState=1;t.f(new Event('open'))};
w.onmessage=function(e){b+=e.data;var i;while((i=b.indexOf('\\n\\n'))>=0){t.b(b.slice(0,i));b=b.slice(i+2)}};
w.onclose=function(e){if(t.readyState===2)return;if(e.code>=4000){t.readyState=2;t.f(new Event('error'));return}t.readyState=0;t.f(new Event('error'));t.r=setTimeout(function(){t.c()},1000)}}
b(s){var n='message',d=[],h=false;s.split('\\n').forEach(function(x){if(!x||x[0]===':')return;var i=x.indexOf(':'),k=i<0?x:x.slice(0,i),v=i<0?'':x.slice(i+1).replace(/^ /,'');if(k==='event')n=v;else if(k==='data'){d.push(v);h=true}else if(k==='id')this.l=v}.bind(this));if(h)this.f(new MessageEvent(n,{data:d.join('\\n'),origin:location.origin,lastEventId:this.l}))}
f(e){this.dispatchEvent(e);var h=this['on'+e.type];if(typeof h==='function')h.call(this,e)}
close(){this.readyState=2;clearTimeout(this.r);if(this.w)this.w.close()}
}
S.CONNECTING=0;S.OPEN=1;S.CLOSED=2;
window.EventSource=S;
`;
var SECURE_CONTEXT_SHIM = "if(window.crypto&&!crypto.randomUUID)crypto.randomUUID=function(){var b=crypto.getRandomValues(new Uint8Array(16)),h='',i;b[6]=b[6]&15|64;b[8]=b[8]&63|128;for(i=0;i<16;i++){h+=(b[i]+256).toString(16).slice(1);if(i==3||i==5||i==7||i==9)h+='-'}return h};";
var GUEST_WATCH = "setInterval(function(){fetch('/__share/me',{cache:'no-store'}).then(function(r){if(r.status===403)return location.reload();return r.json().then(function(m){if(m&&m.role&&m.role!==window.__baoyuShare.role)location.reload()})},function(){})},5000);";
var PAGE_CSS = `
:root { color-scheme: light dark; --bg: #f7f6f3; --card: #fff; --fg: #1f1e1d; --muted: #6b6a66; --line: #e3e1dc; --accent: #c96442; }
@media (prefers-color-scheme: dark) { :root { --bg: #1f1e1d; --card: #2a2927; --fg: #f2f1ee; --muted: #a8a6a0; --line: #3a3936; } }
* { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; padding: 16px; }
main { width: min(420px, 100%); background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 28px; }
h1 { font-size: 20px; margin: 0 0 8px; word-break: break-word; }
p { margin: 0 0 16px; color: var(--muted); }
label { display: block; font-size: 13px; margin: 0 0 6px; color: var(--muted); }
input { width: 100%; font: inherit; padding: 9px 11px; border: 1px solid var(--line); border-radius: 8px; background: transparent; color: inherit; margin: 0 0 14px; }
button { width: 100%; font: inherit; font-weight: 600; padding: 10px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; cursor: pointer; }
.note { font-size: 12px; margin: 14px 0 0; }
a { color: var(--accent); overflow-wrap: anywhere; }
`;
var EN = (noun) => ({
  noAccessTitle: "No access",
  noAccess: `This ${noun.en} is not shared with you. Ask its owner for a link.`,
  linkGoneTitle: "This link does not work",
  linkGone: `The link was turned off or replaced, or the ${noun.en} is no longer shared. Ask its owner for a new one.`,
  invited: (what) => `You were invited to ${what} this ${noun.en}.`,
  yourName: "Your name (others see it on your comments and edits)",
  open: `Open the ${noun.en}`,
  nameNote: "This browser keeps your place; the owner can remove it at any time.",
  roles: { editor: "edit", commenter: "comment on", viewer: "view" },
  youOwn: `This is your ${noun.en}: on this computer you are its owner.`,
  openAsOwner: "Open it",
  tryRole: (what) => `To see it as someone invited to ${what} it does, open the link at the network address, here or on another device:`,
  ownerHere: `You are on the computer that shares this ${noun.en}. Open it as the owner at`
});
var ZH = (noun) => ({
  noAccessTitle: "\u65E0\u6743\u8BBF\u95EE",
  noAccess: `${noun.zhThis}\u6CA1\u6709\u5206\u4EAB\u7ED9\u4F60\u3002\u8BF7\u5411\u6240\u6709\u8005\u8981\u4E00\u4E2A\u94FE\u63A5\u3002`,
  linkGoneTitle: "\u94FE\u63A5\u5DF2\u5931\u6548",
  linkGone: `\u8FD9\u4E2A\u94FE\u63A5\u5DF2\u88AB\u5173\u95ED\u6216\u91CD\u7F6E\uFF0C\u6216\u8005${noun.zhThis}\u5DF2\u505C\u6B62\u5206\u4EAB\u3002\u8BF7\u5411\u6240\u6709\u8005\u8981\u4E00\u4E2A\u65B0\u94FE\u63A5\u3002`,
  invited: (what) => `\u4F60\u88AB\u9080\u8BF7${what}${noun.zhThis}\u3002`,
  yourName: "\u4F60\u7684\u540D\u5B57\uFF08\u522B\u4EBA\u4F1A\u5728\u4F60\u7684\u8BC4\u8BBA\u548C\u7F16\u8F91\u4E0A\u770B\u5230\u5B83\uFF09",
  open: `\u6253\u5F00${noun.zh}`,
  nameNote: "\u8FD9\u4E2A\u6D4F\u89C8\u5668\u4F1A\u8BB0\u4F4F\u4F60\u7684\u8EAB\u4EFD\uFF1B\u6240\u6709\u8005\u53EF\u4EE5\u968F\u65F6\u79FB\u9664\u3002",
  roles: { editor: "\u7F16\u8F91", commenter: "\u8BC4\u8BBA", viewer: "\u67E5\u770B" },
  youOwn: `\u8FD9\u662F\u4F60\u7684${noun.zh}\uFF1A\u5728\u8FD9\u53F0\u7535\u8111\u4E0A\u4F60\u662F\u6240\u6709\u8005\u3002`,
  openAsOwner: `\u6253\u5F00${noun.zh}`,
  tryRole: (what) => `\u60F3\u770B\u770B\u53D7\u9080${what}\u7684\u4EBA\u770B\u5230\u4EC0\u4E48\uFF0C\u7528\u5C40\u57DF\u7F51\u5730\u5740\u6253\u5F00\u8FD9\u4E2A\u94FE\u63A5\uFF08\u5728\u8FD9\u53F0\u7535\u8111\u6216\u522B\u7684\u8BBE\u5907\u4E0A\u90FD\u884C\uFF09\uFF1A`,
  ownerHere: `\u4F60\u5728\u5206\u4EAB${noun.zhThis}\u7684\u7535\u8111\u4E0A\u3002\u4EE5\u6240\u6709\u8005\u8EAB\u4EFD\u6253\u5F00\uFF1A`
});

var MAX_EDIT = 2e3;
function editScript(a, b) {
  const n = a.length;
  const m = b.length;
  const limit = Math.min(n + m, MAX_EDIT);
  const offset = limit + 1;
  const v = new Int32Array(2 * limit + 3);
  const trace = [];
  let found = -1;
  for (let d = 0; d <= limit; d++) {
    trace.push(v.slice(offset - d - 1, offset + d + 2));
    for (let k = -d; k <= d; k += 2) {
      let x2 = k === -d || k !== d && v[offset + k - 1] < v[offset + k + 1] ? v[offset + k + 1] : v[offset + k - 1] + 1;
      let y2 = x2 - k;
      while (x2 < n && y2 < m && a[x2] === b[y2]) {
        x2++;
        y2++;
      }
      v[offset + k] = x2;
      if (x2 >= n && y2 >= m) {
        found = d;
        break;
      }
    }
    if (found >= 0) break;
  }
  if (found < 0) return null;
  const ops = [];
  let x = n;
  let y = m;
  for (let d = found; d > 0; d--) {
    const prev = trace[d];
    const at = (k2) => prev[k2 + d + 1];
    const k = x - y;
    const prevK = k === -d || k !== d && at(k - 1) < at(k + 1) ? k + 1 : k - 1;
    const prevX = at(prevK);
    const prevY = prevX - prevK;
    while (x > prevX && y > prevY) {
      ops.push("=");
      x--;
      y--;
    }
    ops.push(x === prevX ? "+" : "-");
    x = prevX;
    y = prevY;
  }
  while (x > 0 && y > 0) {
    ops.push("=");
    x--;
    y--;
  }
  return ops.reverse();
}
function hunksOf(base, side, mine) {
  const ops = editScript(base, side);
  if (!ops) return null;
  const out = [];
  let open2 = null;
  let i = 0;
  let j = 0;
  for (const op of ops) {
    if (op === "=") {
      open2 = null;
      i++;
      j++;
      continue;
    }
    if (!open2) out.push(open2 = { start: i, end: i, lines: [], mine });
    if (op === "-") open2.end = ++i;
    else open2.lines.push(side[j++]);
  }
  return out.flatMap(
    (h) => h.end - h.start > 1 && h.lines.length === h.end - h.start ? h.lines.flatMap((line, k) => {
      const at = h.start + k;
      return line === base[at] ? [] : [{ start: at, end: at + 1, lines: [line], mine }];
    }) : [h]
  );
}
function applyHunks(base, start, end, hunks) {
  const out = [];
  let at = start;
  for (const h of hunks) {
    out.push(...base.slice(at, h.start), ...h.lines);
    at = h.end;
  }
  out.push(...base.slice(at, end));
  return out;
}
function mergeText(base, mine, current, at, conflicts) {
  const lines = base.split("\n");
  const ours = hunksOf(lines, mine.split("\n"), true);
  const theirs = ours && hunksOf(lines, current.split("\n"), false);
  if (!ours || !theirs) return null;
  const all = [...ours, ...theirs].sort((x, y) => x.start - y.start || x.end - y.end);
  const out = [];
  const lost = [];
  let done = 0;
  for (let i = 0; i < all.length; ) {
    const region = [all[i++]];
    const start = region[0].start;
    let end = region[0].end;
    for (; i < all.length; i++) {
      const h = all[i];
      if (!(h.start < end || h.start === h.end && start === end && h.start === start)) break;
      region.push(h);
      end = Math.max(end, h.end);
    }
    out.push(...lines.slice(done, start));
    const mineLines = applyHunks(lines, start, end, region.filter((h) => h.mine));
    if (region.every((h) => h.mine === region[0].mine)) out.push(...applyHunks(lines, start, end, region));
    else {
      const theirLines = applyHunks(lines, start, end, region.filter((h) => !h.mine));
      if (mineLines.join("\n") !== theirLines.join("\n")) lost.push(`${at}@${start + 1}`);
      out.push(...mineLines);
    }
    done = end;
  }
  out.push(...lines.slice(done));
  conflicts.push(...lost);
  return out.join("\n");
}

var isObject = (v) => typeof v === "object" && v !== null && !Array.isArray(v);
var canon = (v) => {
  if (v === void 0) return void 0;
  if (Array.isArray(v)) return `[${v.map((x) => canon(x) ?? "null").join(",")}]`;
  if (isObject(v)) {
    return `{${Object.keys(v).filter((k) => v[k] !== void 0).sort().map((k) => `${JSON.stringify(k)}:${canon(v[k])}`).join(",")}}`;
  }
  return JSON.stringify(v);
};
var same = (a, b) => canon(a) === canon(b);
var byId = (v) => {
  if (!Array.isArray(v)) return null;
  const out = /* @__PURE__ */ new Map();
  for (const item of v) {
    if (!isObject(item) || typeof item.id !== "string" || out.has(item.id)) return null;
    out.set(item.id, item);
  }
  return out;
};
var parseJson = (text) => {
  if (typeof text !== "string") return null;
  try {
    return { value: JSON.parse(text) };
  } catch {
    return null;
  }
};
var layoutLike = (value, like) => {
  if (!like.includes("\n")) return JSON.stringify(value);
  const indent = /\n([ \t]+)\S/.exec(like)?.[1] ?? "  ";
  return JSON.stringify(value, null, indent) + (like.endsWith("\n") ? "\n" : "");
};
function mergeDoc(base, mine, current) {
  if (current === null) return { result: mine, conflicts: [] };
  const conflicts = [];
  const result = mergeValue(base, mine, current, "", conflicts);
  return { result: isObject(result) ? result : mine, conflicts };
}
function mergeWrite(base, mine, current) {
  if (mine === null) return { result: null, conflicts: current === null || same(current, base) ? [] : ["."] };
  if (current === null) return same(mine, base) ? { result: null, conflicts: [] } : { result: mine, conflicts: ["."] };
  return mergeDoc(base, mine, current);
}
function mergeValue(base, mine, current, at, conflicts) {
  if (same(mine, base)) return current;
  if (same(current, base) || same(mine, current)) return mine;
  if (isObject(base) && isObject(mine) && isObject(current)) return mergeObject(base, mine, current, at, conflicts);
  const b = byId(base);
  const m = byId(mine);
  const c = byId(current);
  if (b && m && c) return mergeList(b, m, c, mine, current, at, conflicts);
  if (typeof base === "string" && typeof mine === "string" && typeof current === "string") {
    const text = mergeText(base, mine, current, at || ".", conflicts);
    if (text !== null) return text;
  }
  conflicts.push(at || ".");
  return mine;
}
function mergeObject(base, mine, current, at, conflicts) {
  const out = {};
  const keys = [.../* @__PURE__ */ new Set([...Object.keys(mine), ...Object.keys(current), ...Object.keys(base)])];
  const jsonText = mine.kind === "json" && current.kind === "json" && base.kind === "json";
  for (const k of keys) {
    if (k === "__proto__") continue;
    const where = at ? `${at}.${k}` : k;
    let v;
    const texts = jsonText && k === "text" ? [parseJson(base.text), parseJson(mine.text), parseJson(current.text)] : null;
    if (texts && texts[0] && texts[1] && texts[2] && !same(mine.text, base.text) && !same(current.text, base.text)) {
      const merged = mergeValue(texts[0].value, texts[1].value, texts[2].value, where, conflicts);
      v = same(merged, texts[1].value) ? mine.text : same(merged, texts[2].value) ? current.text : layoutLike(merged, mine.text);
    } else {
      v = mergeValue(base[k], mine[k], current[k], where, conflicts);
    }
    if (v !== void 0) out[k] = v;
  }
  return out;
}
function mergeList(base, mine, current, mineList, currentList, at, conflicts) {
  const merged = /* @__PURE__ */ new Map();
  for (const id of /* @__PURE__ */ new Set([...mine.keys(), ...current.keys(), ...base.keys()])) {
    const v = mergeValue(base.get(id), mine.get(id), current.get(id), `${at}[${id}]`, conflicts);
    if (v !== void 0) merged.set(id, v);
  }
  const order = mineList.map((item) => item.id).filter((id) => merged.has(id));
  currentList.forEach((item, i) => {
    const id = item.id;
    if (!merged.has(id) || order.includes(id)) return;
    let after = -1;
    for (let j = i - 1; j >= 0 && after < 0; j--) after = order.indexOf(currentList[j].id);
    order.splice(after + 1, 0, id);
  });
  return order.map((id) => merged.get(id));
}
var utf8 = new TextDecoder("utf-8", { fatal: true });

import { createHash as createHash4, randomBytes } from "node:crypto";
import fs7 from "node:fs";
import path7 from "node:path";
var HISTORY_DIR = "history";
var INDEX = "index.json";
var OBJECTS = "objects";
var IDLE_MS = 3e4;
var SPAN_MS = 5 * 6e4;
var MAX_VERSIONS = 500;
var MAX_NOTICES = 50;
var NOTICE_DAYS = 7;
var AGENT = { by: "agent", user: { id: "agent", name: "Agent" } };
var SYSTEM = { by: "system", user: { id: "system", name: "" } };
var sha256 = (bytes) => createHash4("sha256").update(bytes).digest("hex");
var SHA = /^[0-9a-f]{64}$/;
var isRecord3 = (value) => typeof value === "object" && value !== null && !Array.isArray(value);
function writeAtomic(file, data) {
  fs7.mkdirSync(path7.dirname(file), { recursive: true });
  const tmp = path7.join(path7.dirname(file), `.${path7.basename(file)}.${process.pid}.${randomBytes(4).toString("hex")}.tmp`);
  try {
    fs7.writeFileSync(tmp, data);
    fs7.renameSync(tmp, file);
  } catch (error) {
    fs7.rmSync(tmp, { force: true });
    throw error;
  }
}
var emptyIndex = () => ({ format: 1, next: 1, base: {}, versions: [], notices: [] });
function readUser(value) {
  return isRecord3(value) && typeof value.id === "string" && typeof value.name === "string" ? { id: value.id, name: value.name } : null;
}
var isAuthor = (value) => value === "human" || value === "agent" || value === "system";
function parseIndex(raw) {
  const index = emptyIndex();
  if (!isRecord3(raw)) return index;
  if (isRecord3(raw.base)) {
    for (const [p, s] of Object.entries(raw.base)) if (typeof s === "string" && SHA.test(s)) index.base[p] = s;
  }
  if (Array.isArray(raw.versions)) {
    for (const v of raw.versions) {
      if (!isRecord3(v) || typeof v.n !== "number" || !isAuthor(v.by) || typeof v.at !== "string" || !isRecord3(v.changes)) continue;
      const user = readUser(v.user);
      if (!user) continue;
      const changes = {};
      for (const [p, s] of Object.entries(v.changes)) if (s === null || typeof s === "string" && SHA.test(s)) changes[p] = s;
      const version = { n: v.n, first: typeof v.first === "string" ? v.first : v.at, at: v.at, by: v.by, user, changes };
      if (typeof v.role === "string") version.role = v.role;
      if (typeof v.restoredFrom === "number") version.restoredFrom = v.restoredFrom;
      if (version.restoredFrom !== void 0 && v.restoredPart === true) version.restoredPart = true;
      if (Array.isArray(v.overwrote)) {
        const list = [];
        for (const o of v.overwrote) {
          const who = isRecord3(o) ? readUser(o.user) : null;
          if (!isRecord3(o) || !who || typeof o.path !== "string" || o.lost !== null && typeof o.lost !== "string" || typeof o.n !== "number" || !isAuthor(o.by)) continue;
          list.push({
            path: o.path,
            lost: o.lost,
            n: o.n,
            by: o.by,
            user: who,
            ...o.soft === true ? { soft: true } : {},
            ...o.chosen === true ? { chosen: true } : {},
            ...typeof o.base === "string" && SHA.test(o.base) ? { base: o.base } : {}
          });
        }
        if (list.length) version.overwrote = list;
      }
      index.versions.push(version);
    }
  }
  index.versions.sort((a, b) => a.n - b.n);
  const last = index.versions.at(-1);
  index.next = Math.max(typeof raw.next === "number" ? raw.next : 1, (last?.n ?? 0) + 1);
  if (Array.isArray(raw.notices)) {
    for (const n of raw.notices) {
      if (!isRecord3(n) || typeof n.id !== "string" || typeof n.to !== "string" || typeof n.path !== "string" || typeof n.n !== "number") continue;
      if (n.kind !== "overwritten" && n.kind !== "overwrote") continue;
      const by = readUser(n.by);
      const lost = isRecord3(n.lost) ? n.lost : null;
      const lostUser = lost ? readUser(lost.user) : null;
      if (!by || !lost || !lostUser || lost.sha !== null && typeof lost.sha !== "string" || typeof lost.n !== "number" || !isAuthor(lost.by)) continue;
      index.notices.push({
        id: n.id,
        to: n.to,
        at: typeof n.at === "string" ? n.at : (/* @__PURE__ */ new Date(0)).toISOString(),
        kind: n.kind,
        path: n.path,
        n: n.n,
        by,
        byAuthor: isAuthor(n.byAuthor) ? n.byAuthor : "human",
        lost: { sha: lost.sha, n: lost.n, by: lost.by, user: lostUser },
        ...n.soft === true ? { soft: true } : {},
        ...typeof n.base === "string" && SHA.test(n.base) ? { base: n.base } : {}
      });
    }
  }
  return index;
}
var History = class {
  dir;
  index;
  /** path → sha: what the files hold after the newest version. */
  headState;
  constructor(root) {
    this.dir = path7.join(root, HISTORY_DIR);
    let raw = null;
    try {
      raw = JSON.parse(fs7.readFileSync(path7.join(this.dir, INDEX), "utf8"));
    } catch {
    }
    this.index = parseIndex(raw);
    this.headState = this.fold(Infinity);
    this.index.notices = this.index.notices.filter((n) => (this.headState.get(n.path) ?? null) !== n.lost.sha);
  }
  get empty() {
    return this.index.versions.length === 0 && Object.keys(this.index.base).length === 0;
  }
  /** What the files hold now, as far as the history knows (path → sha). */
  head() {
    return this.headState;
  }
  versions() {
    return this.index.versions;
  }
  version(n) {
    return this.index.versions.find((v) => v.n === n);
  }
  /** The files after the versions numbered up to `upto` (the base and every version at or below it). */
  fold(upto) {
    const state = new Map(Object.entries(this.index.base));
    for (const version of this.index.versions) {
      if (version.n > upto) break;
      for (const [p, s] of Object.entries(version.changes)) {
        if (s === null) state.delete(p);
        else state.set(p, s);
      }
    }
    return state;
  }
  /** The files right after version `n`; null when it is not kept. */
  stateAt(n) {
    return this.version(n) ? this.fold(n) : null;
  }
  /** The files right before version `n`. */
  stateBefore(n) {
    return this.fold(n - 1);
  }
  /** The content with this sha, from the objects. */
  read(sha) {
    if (!SHA.test(sha)) return null;
    try {
      return fs7.readFileSync(path7.join(this.dir, OBJECTS, sha));
    } catch {
      return null;
    }
  }
  /** Keeps a content that no version holds (an overwrite's `base`); its sha. */
  put(bytes) {
    const sha = sha256(bytes);
    this.putObject(sha, bytes);
    return sha;
  }
  size(sha) {
    if (!SHA.test(sha)) return null;
    try {
      return fs7.statSync(path7.join(this.dir, OBJECTS, sha)).size;
    } catch {
      return null;
    }
  }
  /** The newest version that changed `path`, with what it left there. */
  lastChange(p) {
    for (let i = this.index.versions.length - 1; i >= 0; i--) {
      const version = this.index.versions[i];
      if (p in version.changes) return { version, sha: version.changes[p] };
    }
    return null;
  }
  /**
   * Records changes: path → its content now (null: deleted). Those equal to the head are left out; nothing left, no
   * version (null). The rest join the open version of the same person, or start a new one.
   */
  record(changes, who, extra = {}, now = /* @__PURE__ */ new Date()) {
    const changed = {};
    for (const [p, bytes] of changes) {
      const sha = bytes === null ? null : sha256(bytes);
      if ((this.headState.get(p) ?? null) === sha) continue;
      if (bytes !== null && sha !== null) this.putObject(sha, bytes);
      changed[p] = sha;
    }
    if (Object.keys(changed).length === 0) return null;
    const iso = now.toISOString();
    const last = this.index.versions.at(-1);
    const joins = !!last && who.by !== "system" && last.by === who.by && last.user.id === who.user.id && last.restoredFrom === void 0 && extra.restoredFrom === void 0 && now.getTime() - Date.parse(last.at) < IDLE_MS && now.getTime() - Date.parse(last.first) < SPAN_MS;
    let version;
    if (joins) {
      version = last;
      version.at = iso;
      Object.assign(version.changes, changed);
      if (who.user.name) version.user = { ...who.user };
    } else {
      version = { n: this.index.next++, first: iso, at: iso, by: who.by, user: { ...who.user }, changes: changed };
      if (who.role) version.role = who.role;
      if (extra.restoredFrom !== void 0) version.restoredFrom = extra.restoredFrom;
      if (extra.restoredFrom !== void 0 && extra.restoredPart) version.restoredPart = true;
      this.index.versions.push(version);
    }
    for (const [p, s] of Object.entries(changed)) {
      if (s === null) this.headState.delete(p);
      else this.headState.set(p, s);
    }
    this.index.notices = this.index.notices.filter(
      (n) => !(n.path in changed && (changed[n.path] === n.lost.sha || extra.restoredFrom !== void 0 && n.to === who.user.id))
    );
    if (extra.overwrote?.length) {
      version.overwrote = [...(version.overwrote ?? []).filter((o) => !extra.overwrote.some((x) => x.path === o.path)), ...extra.overwrote];
      this.notify(version, who, extra.overwrote, now);
    }
    this.prune(now);
    this.save();
    return version;
  }
  /** Notices for an overwrite: to whoever lost their change (the agent's go to the owner), and a hard one's saver unless they chose it. */
  notify(version, who, overwrote, now) {
    const at = now.toISOString();
    for (const o of overwrote) {
      const lost = { sha: o.lost, n: o.n, by: o.by, user: o.user };
      const victim = o.by === "agent" ? "local" : o.user.id;
      const fields = {
        at,
        path: o.path,
        n: version.n,
        by: { ...who.user },
        byAuthor: who.by,
        lost,
        ...o.soft ? { soft: true } : {},
        ...o.base ? { base: o.base } : {}
      };
      const same3 = (n) => n.path === o.path && n.n === version.n;
      this.index.notices = this.index.notices.filter((n) => !same3(n));
      if (victim !== who.user.id) this.index.notices.push({ id: randomBytes(6).toString("hex"), to: victim, kind: "overwritten", ...fields });
      if (!o.soft && !o.chosen) this.index.notices.push({ id: randomBytes(6).toString("hex"), to: who.user.id, kind: "overwrote", ...fields });
    }
  }
  /** The notices for this person, newest first. */
  noticesFor(userId) {
    return this.index.notices.filter((n) => n.to === userId).reverse();
  }
  notice(id) {
    return this.index.notices.find((n) => n.id === id);
  }
  /** Dismisses one of this person's notices; false when they have none by that id. */
  dismiss(userId, id) {
    const before = this.index.notices.length;
    this.index.notices = this.index.notices.filter((n) => !(n.id === id && n.to === userId));
    if (this.index.notices.length === before) return false;
    this.save();
    return true;
  }
  /**
   * What to write to bring version `n` back: path → content (null: delete), for `paths` (default: every file it or the
   * head holds), only where the head differs. null when the version is not kept or a content is missing.
   */
  restoreTo(n, paths, tracked = () => true) {
    const target = this.stateAt(n);
    if (!target) return null;
    const out = /* @__PURE__ */ new Map();
    const all = paths ?? [.../* @__PURE__ */ new Set([...target.keys(), ...this.headState.keys()])];
    for (const p of all) {
      if (!tracked(p)) continue;
      const want = target.get(p) ?? null;
      if ((this.headState.get(p) ?? null) === want) continue;
      if (want === null) {
        out.set(p, null);
        continue;
      }
      const bytes = this.read(want);
      if (!bytes) return null;
      out.set(p, bytes);
    }
    return out;
  }
  /** Each version's changes as added, edited or deleted (what the file held before it decides). */
  fileChanges() {
    const out = /* @__PURE__ */ new Map();
    const state = new Map(Object.entries(this.index.base));
    for (const version of this.index.versions) {
      const list = [];
      for (const [p, s] of Object.entries(version.changes)) {
        const had = state.has(p);
        list.push({ path: p, op: s === null ? "deleted" : had ? "edited" : "added" });
        if (s === null) state.delete(p);
        else state.set(p, s);
      }
      out.set(version.n, list);
    }
    return out;
  }
  putObject(sha, bytes) {
    const file = path7.join(this.dir, OBJECTS, sha);
    if (fs7.existsSync(file)) return;
    writeAtomic(file, bytes);
  }
  /** Past MAX_VERSIONS the oldest fold into the base; old notices go; contents no one holds are removed. */
  prune(now) {
    let folded = false;
    while (this.index.versions.length > MAX_VERSIONS) {
      const old = this.index.versions.shift();
      for (const [p, s] of Object.entries(old.changes)) {
        if (s === null) delete this.index.base[p];
        else this.index.base[p] = s;
      }
      folded = true;
    }
    const oldest = now.getTime() - NOTICE_DAYS * 864e5;
    const kept = this.index.versions[0]?.n ?? Infinity;
    const perPerson = /* @__PURE__ */ new Map();
    this.index.notices = this.index.notices.filter((n) => Date.parse(n.at) >= oldest && n.lost.n >= kept).reverse().filter((n) => {
      const count = (perPerson.get(n.to) ?? 0) + 1;
      perPerson.set(n.to, count);
      return count <= MAX_NOTICES;
    }).reverse();
    if (folded) this.collect();
  }
  /** Removes the objects that neither the base, a version nor a notice holds (with the base an overwrite was made on). */
  collect() {
    const keep = new Set(Object.values(this.index.base));
    for (const version of this.index.versions) {
      for (const s of Object.values(version.changes)) if (s) keep.add(s);
      for (const o of version.overwrote ?? []) if (o.base) keep.add(o.base);
    }
    for (const notice of this.index.notices) {
      if (notice.lost.sha) keep.add(notice.lost.sha);
      if (notice.base) keep.add(notice.base);
    }
    let names;
    try {
      names = fs7.readdirSync(path7.join(this.dir, OBJECTS));
    } catch {
      return;
    }
    for (const name of names) if (SHA.test(name) && !keep.has(name)) fs7.rmSync(path7.join(this.dir, OBJECTS, name), { force: true });
  }
  save() {
    writeAtomic(path7.join(this.dir, INDEX), `${JSON.stringify(this.index)}
`);
  }
};
var MAX_DIFF_BYTES = 1024 * 1024;
var CONTEXT = 3;
var MAX_DIFF_LINES = 3e3;
var MAX_LINE = 2e3;
var decoder = new TextDecoder("utf-8", { fatal: true });
function textOf(bytes) {
  if (bytes === null) return null;
  if (bytes.includes(0)) return void 0;
  try {
    return decoder.decode(bytes);
  } catch {
    return void 0;
  }
}
var splitLines = (text) => text === null || text === "" ? [] : text.replace(/\r\n?/g, "\n").replace(/\n$/, "").split("\n");
function diffContents(before, after) {
  if ((before?.length ?? 0) > MAX_DIFF_BYTES || (after?.length ?? 0) > MAX_DIFF_BYTES) return { tooLarge: true, added: 0, removed: 0, lines: [] };
  const a = textOf(before);
  const b = textOf(after);
  if (a === void 0 || b === void 0) return { binary: true, added: 0, removed: 0, lines: [] };
  const left = splitLines(a);
  const right = splitLines(b);
  let head = 0;
  while (head < left.length && head < right.length && left[head] === right[head]) head++;
  let tail = 0;
  while (tail < left.length - head && tail < right.length - head && left[left.length - 1 - tail] === right[right.length - 1 - tail]) tail++;
  const middle = editScript(left.slice(head, left.length - tail), right.slice(head, right.length - tail));
  if (!middle) return { tooLarge: true, added: 0, removed: 0, lines: [] };
  const ops = [...Array(head).fill("="), ...middle, ...Array(tail).fill("=")];
  const all = [];
  let i = 0;
  let j = 0;
  let added = 0;
  let removed = 0;
  const cut = (s) => s.length > MAX_LINE ? `${s.slice(0, MAX_LINE)}\u2026` : s;
  for (const op of ops) {
    if (op === "=") all.push([" ", cut(right[j++])]), i++;
    else if (op === "-") all.push(["-", cut(left[i++])]), removed++;
    else all.push(["+", cut(right[j++])]), added++;
  }
  const keep = new Uint8Array(all.length);
  all.forEach(([kind], at) => {
    if (kind === " ") return;
    for (let x = Math.max(0, at - CONTEXT); x <= Math.min(all.length - 1, at + CONTEXT); x++) keep[x] = 1;
  });
  const lines = [];
  let skipped = 0;
  let truncated = false;
  for (let at = 0; at < all.length; at++) {
    if (!keep[at]) {
      skipped++;
      continue;
    }
    if (skipped) lines.push(["~", String(skipped)]);
    skipped = 0;
    if (lines.length >= MAX_DIFF_LINES) {
      truncated = true;
      break;
    }
    lines.push(all[at]);
  }
  if (skipped && !truncated) lines.push(["~", String(skipped)]);
  return { added, removed, lines, ...truncated ? { truncated: true } : {} };
}

var whoOf = (viewer) => ({ by: "human", user: { id: viewer.user.id, name: viewer.user.name }, role: viewer.role });
var MAX_BODY = 64 << 10;
var HistoryHost = class {
  history;
  options;
  constructor(options) {
    this.options = options;
    this.history = options.history;
  }
  /** What the page's boot script tells the panel (window.__baoyuHistory); `preview` on a version's preview page. */
  bootGlobal(viewer, preview) {
    const global = { base: this.options.base, canRestore: canEditAs(viewer.role), me: viewer.user.id };
    const version = preview === void 0 ? void 0 : this.history.version(preview);
    if (version) {
      const newest = this.history.versions().at(-1);
      global.preview = { n: version.n, at: version.at, by: version.by, name: version.user.name, current: version === newest, current_url: this.options.base };
    }
    return global;
  }
  notices(viewer, label) {
    const head = this.history.head();
    const gone = (n) => !head.has(n.path) && this.history.version(n.n)?.changes[n.path] === null;
    return this.history.noticesFor(viewer.user.id).map((n) => noticeView(n, label, this.history.version(n.lost.n)?.at, gone(n)));
  }
  list(viewer) {
    const label = this.options.labels();
    const versions = this.history.versions();
    const changes = this.history.fileChanges();
    const newest = versions.at(-1);
    const rows = [...versions].reverse().map((v) => ({
      n: v.n,
      first: v.first,
      at: v.at,
      by: v.by,
      name: v.user.name,
      userId: v.user.id,
      ...v.role ? { role: v.role } : {},
      ...v.restoredFrom !== void 0 ? { restoredFrom: v.restoredFrom } : {},
      ...v.restoredPart ? { restoredPart: true } : {},
      ...v === newest ? { current: true } : {},
      preview: this.options.previewUrl(v.n),
      files: (changes.get(v.n) ?? []).map((c) => ({ path: c.path, op: c.op, label: label(c.path) })),
      ...v.overwrote?.length ? { overwrote: v.overwrote.map((o) => ({ path: o.path, label: label(o.path), name: o.user.name, by: o.by, n: o.n, ...o.soft ? { soft: true } : {} })) } : {}
    }));
    return { me: viewer.user.id, canRestore: canEditAs(viewer.role), rows, notices: this.notices(viewer, label) };
  }
  /** Answers `__history…` (`sub` is what follows it); false for a path it doesn't know. */
  async handle(request, response, sub, viewer) {
    const method = request.method ?? "GET";
    const url = new URL(request.url ?? "/", "http://local");
    if (method === "POST" && !sameOrigin(request)) {
      request.resume();
      sendJson(response, 403, { code: "not_granted", message: "Cross-origin write refused." });
      return true;
    }
    if (method === "GET" && (sub === "" || sub === "/")) return sendJson(response, 200, this.list(viewer)), true;
    if (sub === "/notices") {
      if (method === "GET") return sendJson(response, 200, { notices: this.notices(viewer, this.options.labels()) }), true;
      if (method !== "POST") return sendJson(response, 405, { code: "method_not_allowed", message: "GET or POST" }), true;
      const body = await this.body(request, response);
      if (!body) return true;
      if (typeof body.dismiss !== "string") return sendJson(response, 400, { code: "invalid_argument", message: "Expected {dismiss: id}." }), true;
      this.history.dismiss(viewer.user.id, body.dismiss);
      return sendJson(response, 200, { notices: this.notices(viewer, this.options.labels()) }), true;
    }
    const versionRoute = /^\/(\d+)\/(diff|restore)$/.exec(sub);
    if (versionRoute) {
      const n = Number(versionRoute[1]);
      const version = this.history.version(n);
      if (!version) return sendJson(response, 404, { code: "not_found", message: `There is no version ${n} (it may be too old to keep).` }), true;
      if (versionRoute[2] === "diff") {
        if (method !== "GET") return sendJson(response, 405, { code: "method_not_allowed", message: "GET" }), true;
        const p = url.searchParams.get("path") ?? "";
        if (!(p in version.changes)) return sendJson(response, 404, { code: "not_found", message: `Version ${n} did not change ${p}.` }), true;
        const before = this.history.stateBefore(n).get(p) ?? null;
        const after = version.changes[p] ?? null;
        return sendJson(response, 200, this.diff(p, before, after)), true;
      }
      if (method !== "POST") return sendJson(response, 405, { code: "method_not_allowed", message: "POST" }), true;
      if (!canEditAs(viewer.role)) return sendJson(response, 403, { code: "not_writer", message: "Only the owner and editors can bring a version back." }), true;
      const body = await this.body(request, response);
      if (!body) return true;
      const paths = Array.isArray(body.paths) ? body.paths.filter((p) => typeof p === "string") : void 0;
      const changes = this.history.restoreTo(n, paths, this.options.tracked);
      if (!changes) return sendJson(response, 409, { code: "unavailable", message: `Version ${n} can't be brought back: a file it holds is missing from the history.` }), true;
      const made = await this.options.apply(changes, whoOf(viewer), { restoredFrom: n });
      this.options.log(`history: ${viewer.user.name} brought back version ${n}${paths ? ` (${paths.join(", ")})` : ""}${made ? ` as version ${made.n}` : " (nothing to change)"}`);
      return sendJson(response, 200, { version: made?.n ?? null, changed: [...changes.keys()] }), true;
    }
    const noticeRoute = /^\/notice\/([0-9a-f]{6,32})\/(diff|recover)$/.exec(sub);
    if (noticeRoute) {
      const notice = this.history.notice(noticeRoute[1]);
      if (!notice || notice.to !== viewer.user.id) return sendJson(response, 404, { code: "not_found", message: "No such notice." }), true;
      if (noticeRoute[2] === "diff") {
        if (method !== "GET") return sendJson(response, 405, { code: "method_not_allowed", message: "GET" }), true;
        const now2 = this.history.head().get(notice.path) ?? null;
        const nowBytes = now2 === null ? null : this.history.read(now2);
        const back2 = this.recovered(notice, nowBytes);
        if (now2 && !nowBytes || !back2) return sendJson(response, 200, { path: notice.path, label: this.options.labels()(notice.path), missing: true, added: 0, removed: 0, lines: [], now: now2 }), true;
        return sendJson(response, 200, { ...this.diffBytes(notice.path, nowBytes, back2.bytes), now: now2 }), true;
      }
      if (method !== "POST") return sendJson(response, 405, { code: "method_not_allowed", message: "POST" }), true;
      if (!canEditAs(viewer.role)) return request.resume(), sendJson(response, 403, { code: "not_writer", message: "Only the owner and editors can change the files." }), true;
      const body = await this.body(request, response);
      if (!body) return true;
      const now = this.history.head().get(notice.path) ?? null;
      if ("now" in body && body.now !== now) {
        return sendJson(response, 409, { code: "changed", message: "This changed while you were looking. Compare again." }), true;
      }
      const back = this.recovered(notice, now === null ? null : this.history.read(now));
      if (!back) return sendJson(response, 409, { code: "unavailable", message: "That content is no longer in the history." }), true;
      const made = await this.options.apply(/* @__PURE__ */ new Map([[notice.path, back.bytes]]), whoOf(viewer), { restoredFrom: notice.lost.n, ...back.part ? { restoredPart: true } : {} });
      this.history.dismiss(viewer.user.id, notice.id);
      this.options.log(`history: ${viewer.user.name} brought back ${notice.lost.user.name}'s ${back.bytes === null ? "deletion of " : ""}${notice.path} (version ${notice.lost.n}${back.part ? ", what was replaced" : ""})`);
      return sendJson(response, 200, { version: made?.n ?? null }), true;
    }
    return false;
  }
  /** Before → after of one file, with the versions' names for the panel's header. */
  diff(p, before, after) {
    const read = (sha) => sha === null ? null : this.history.read(sha);
    const a = read(before);
    const b = read(after);
    if (before && !a || after && !b) return { path: p, label: this.options.labels()(p), missing: true, added: 0, removed: 0, lines: [] };
    return this.diffBytes(p, a, b);
  }
  diffBytes(p, a, b) {
    const [x, y] = this.options.diffSides ? this.options.diffSides(p, a, b) : [a, b];
    return { path: p, label: this.options.labels()(p), ...diffContents(x, y) };
  }
  /**
   * What bringing a notice's lost content back writes to its file (`now`: what the file holds): the lost content merged
   * into it when the notice has a base and the server can merge (`part` when that is not the whole lost content), else
   * the whole lost content; a deletion deletes it again (bytes null). null: not in the history.
   */
  recovered(notice, now) {
    if (notice.lost.sha === null) return { bytes: null, part: false };
    const lost = this.history.read(notice.lost.sha);
    if (!lost) return null;
    const base = notice.base ? this.history.read(notice.base) : null;
    const merged = base && this.options.recover ? this.options.recover(notice.path, base, lost, now) : null;
    return merged ? { bytes: merged, part: !merged.equals(lost) } : { bytes: lost, part: false };
  }
  async body(request, response) {
    try {
      const raw = (await readBody(request, MAX_BODY)).toString("utf8");
      const body = raw.trim() ? JSON.parse(raw) : {};
      if (typeof body === "object" && body !== null && !Array.isArray(body)) return body;
    } catch {
    }
    sendJson(response, 400, { code: "invalid_argument", message: "Expected a JSON object." });
    return null;
  }
};
function noticeView(n, label, lostAt, gone) {
  return {
    ...lostAt ? { lostAt } : {},
    id: n.id,
    kind: n.kind,
    at: n.at,
    path: n.path,
    label: label(n.path),
    n: n.n,
    name: n.by.name,
    by: n.byAuthor,
    lostName: n.lost.user.name,
    lostBy: n.lost.by,
    lostN: n.lost.n,
    ...n.soft ? { soft: true } : {},
    // Bringing it back puts back only what was replaced (a write with a base); into a deleted file, all of it.
    ...n.base && !gone ? { part: true } : {},
    ...gone ? { removed: true } : {},
    // What was replaced is a deletion: bringing it back deletes the file again.
    ...n.lost.sha === null ? { deleted: true } : {}
  };
}
var plain = (text) => ({ en: text, zh: text });

var OVERLAP_MS = 6e4;
var docBytes = (data) => Buffer.from(`${JSON.stringify(data, null, 2)}
`);
var parse = (bytes) => {
  if (bytes === null) return null;
  try {
    const value = JSON.parse(bytes.toString("utf8"));
    return typeof value === "object" && value !== null && !Array.isArray(value) ? value : null;
  } catch {
    return null;
  }
};
var same2 = (a, b) => JSON.stringify(a) === JSON.stringify(b);
var DbHistory = class {
  history;
  host;
  options;
  /**
   * Document → who is writing it from the page, and what the write is (a restore; a merged write: the document it was
   * made on and the values in it that replaced someone else's), until the rescan after it.
   */
  pending;
  /** The first rescan also looks for documents deleted while no server ran. */
  first;
  constructor(options) {
    this.options = options;
    this.history = new History(options.root);
    this.pending = /* @__PURE__ */ new Map();
    this.first = true;
    this.host = new HistoryHost({
      history: this.history,
      labels: () => {
        const named = options.labels();
        return (p) => named(p) ?? plain(p);
      },
      base: options.base,
      previewUrl: (n) => `${options.base}?at=${n}`,
      apply: async (changes, who, extra) => this.apply(changes, who, extra),
      tracked: options.tracked,
      diffSides: textSides,
      recover: (_path, base, lost, now) => {
        const b = parse(base);
        const l = parse(lost);
        const n = parse(now);
        if (!b || !l) return null;
        return n ? docBytes(mergeDoc(b, l, n).result) : lost;
      },
      log: options.log
    });
  }
  /**
   * A page's write of `path` by `who`, until `settle`: the rescan in between records it as theirs. `merge`: the write was
   * merged (mergeDoc) from this base, and these are the values in it that replaced someone else's (empty: nothing lost).
   */
  attribute(path10, who, merge) {
    this.pending.set(path10, { who, ...merge ? { merge } : {} });
  }
  /** After the page's write and its rescan (the write may have changed nothing, or failed). */
  settle(path10) {
    this.pending.delete(path10);
  }
  /** Records the rescan's changes; `present` says which documents are on disk now (for the first rescan). */
  record(changes, present) {
    const groups = /* @__PURE__ */ new Map();
    const fallback = this.history.empty ? SYSTEM : AGENT;
    const add = (who, restore, p, bytes, merge) => {
      const key = `${who.by}\0${who.user.id}\0${restore.restoredFrom ?? ""}\0${restore.restoredPart ? "part" : ""}`;
      let group = groups.get(key);
      if (!group) groups.set(key, group = { who, restore, files: /* @__PURE__ */ new Map(), merged: /* @__PURE__ */ new Map() });
      group.files.set(p, bytes);
      if (merge) group.merged.set(p, merge);
    };
    for (const c of changes) {
      if (!this.options.tracked(c.path)) continue;
      const by = this.pending.get(c.path);
      const restore = by?.restoredFrom !== void 0 ? { restoredFrom: by.restoredFrom, ...by.restoredPart ? { restoredPart: true } : {} } : {};
      add(by?.who ?? fallback, restore, c.path, c.data === null ? null : docBytes(c.data), by?.merge);
    }
    if (this.first) {
      this.first = false;
      for (const p of this.history.head().keys()) if (this.options.tracked(p) && !present(p) && !changes.some((c) => c.path === p)) add(fallback, {}, p, null);
    }
    const made = [];
    for (const group of groups.values()) {
      const overwrote = group.who.by !== "system" && group.restore.restoredFrom === void 0 ? this.overlaps(group.files, group.who, group.merged) : [];
      const version = this.history.record(group.files, group.who, { ...group.restore, ...overwrote.length ? { overwrote } : {} });
      if (!version) continue;
      made.push(version);
      if (group.who.by !== "human") {
        const what = group.who.by === "agent" ? "changed outside the page" : "the documents as they were";
        this.options.log(`history: version ${version.n} (${what}): ${[...group.files.keys()].join(", ")}`);
      }
    }
    return made;
  }
  /**
   * Whose values on these documents this change replaced. A merged write says (`merged`: path → its base and the values
   * it replaced; the notice goes to the person behind the document's last version, when that is someone else, and keeps
   * the base so bringing the lost values back leaves the rest; chosen when its person saw that version and saved over
   * it). Otherwise a guess, for a change another person made in
   * the last minute: part of it is gone when merging it (the document before it → theirs) into this one changes this
   * one. The document before it is the notice's base. Their change a deletion: it is gone when the document is back.
   */
  overlaps(files, who, merged) {
    const now = Date.now();
    const out = [];
    for (const [p, bytes] of files) {
      const last = this.history.lastChange(p);
      if (!last) continue;
      const v = last.version;
      if (v.by !== "human" || v.user.id === who.user.id || v.restoredFrom !== void 0) continue;
      if ((this.history.head().get(p) ?? null) !== last.sha) continue;
      const lost = { path: p, lost: last.sha, n: v.n, by: "human", user: { ...v.user }, soft: true };
      const merge = merged.get(p);
      if (merge) {
        if (!merge.conflicts.length) continue;
        const { soft: _soft, ...hard } = lost;
        const over = merge.chosen ? { ...hard, chosen: true } : lost;
        out.push(last.sha === null ? over : { ...over, base: this.history.put(docBytes(merge.base)) });
        continue;
      }
      if (now - Date.parse(v.at) > OVERLAP_MS) continue;
      if (last.sha === null) {
        if (bytes !== null) out.push(lost);
        continue;
      }
      const theirs = parse(this.history.read(last.sha));
      const was = parse(this.history.read(this.history.stateBefore(v.n).get(p) ?? "") ?? null) ?? {};
      const next = parse(bytes) ?? {};
      if (!theirs || same(mergeDoc(was, theirs, next).result, next)) continue;
      out.push({ ...lost, base: this.history.stateBefore(v.n).get(p) ?? this.history.put(docBytes({})) });
    }
    return out;
  }
  /** A restore (or a recovered notice): writes the documents as `who`'s; the rescan after records them. */
  apply(changes, who, extra) {
    const paths = [];
    try {
      for (const [p, bytes] of changes) {
        const data = bytes === null ? null : parse(bytes);
        if (bytes !== null && data === null) continue;
        this.pending.set(p, { who, ...extra.restoredFrom !== void 0 ? { restoredFrom: extra.restoredFrom, ...extra.restoredPart ? { restoredPart: true } : {} } : {} });
        paths.push(p);
        this.options.write(p, data);
      }
      this.options.rescan();
      const versions = this.history.versions();
      const newest = versions.at(-1);
      return newest && newest.user.id === who.user.id && newest.restoredFrom === extra.restoredFrom && paths.some((p) => p in newest.changes) ? newest : null;
    } finally {
      for (const p of paths) this.pending.delete(p);
    }
  }
  /**
   * On a version's page (?at=n): the documents as that version left them in place of the kept ones now, the page's
   * own as they are. null: there is no such version.
   */
  docsAt(n, current) {
    const state = this.history.stateAt(n);
    if (!state) return null;
    const out = /* @__PURE__ */ new Map();
    for (const [p, data] of current) if (!this.options.tracked(p)) out.set(p, data);
    for (const [p, sha] of state) {
      if (!this.options.tracked(p)) continue;
      const data = parse(this.history.read(sha));
      if (data) out.set(p, data);
    }
    return out;
  }
  /** window.__baoyuHistory for this person; `query` is the page's (?at=n on a version's page). */
  bootGlobal(viewer, query) {
    return this.host.bootGlobal(viewer, previewOf(query));
  }
};
function previewOf(query) {
  const at = query.get("at");
  return at !== null && /^\d{1,9}$/.test(at) ? Number(at) : void 0;
}
function textSides(_path, before, after) {
  const a = parse(before);
  const b = parse(after);
  const textOf2 = (d) => d && typeof d.text === "string" ? d.text : null;
  const rest = (d) => {
    if (!d) return null;
    const { text: _text, ...others } = d;
    return others;
  };
  const ta = textOf2(a);
  const tb = textOf2(b);
  if ((ta !== null || a === null) && (tb !== null || b === null) && (a === null || b === null || same2(rest(a), rest(b)))) {
    return [ta === null ? null : Buffer.from(ta), tb === null ? null : Buffer.from(tb)];
  }
  return [before, after];
}

var PEER_ID = /^[A-Za-z0-9_-]{8,64}$/;
function agentWhere(main2, count, label) {
  const where = main2 ? label(main2) : null;
  if (!where || count <= 1) return where;
  return { en: `${where.en} and ${count - 1} more`, zh: `${where.zh} \u7B49 ${count} \u5904` };
}
var AGENT_COLOR = "#d25f25";
var MAX_PEERS = 64;
var MAX_BODY_BYTES = 64 << 10;
var MAX_FIELDS = 12;
var MAX_PRESENCE_BYTES = 6 << 10;
var BROADCAST_MS = 50;
var EVENT_TOPIC = /^[a-z][a-z0-9_.-]{0,47}$/;
var MAX_EVENT_BYTES = 4096;
var EVENTS_PER_SECOND = 40;
var EVENT_BURST = 80;
var LEAVE_GRACE_MS = 4e3;
var AGENT_LINGER_MS = 2e4;
var AGENT_PEER = "agent-claude";
var PresenceHub = class {
  peers = /* @__PURE__ */ new Map();
  /** Every open stream, with the peer it belongs to ('' for one that hears the others but isn't on the list). */
  listeners = /* @__PURE__ */ new Map();
  agent = null;
  timer = null;
  /** Adds a page's stream; `send` writes one SSE frame to it. Returns what to call when the stream closes. */
  join(peer, viewer, send) {
    let entry = this.peers.get(peer);
    if (entry && entry.viewer.user.id !== viewer.user.id) {
      entry = void 0;
      peer = "";
    }
    if (peer && !entry && this.peers.size < MAX_PEERS) {
      entry = { viewer, presence: {}, updatedAt: Date.now(), streams: 0, budget: EVENT_BURST, toppedAt: Date.now() };
      this.peers.set(peer, entry);
    }
    if (entry) {
      entry.streams += 1;
      if (entry.leaving) clearTimeout(entry.leaving);
      entry.leaving = void 0;
    }
    this.listeners.set(send, entry ? peer : "");
    send(this.frame());
    this.schedule();
    let open2 = true;
    return () => {
      if (!open2) return;
      open2 = false;
      this.listeners.delete(send);
      if (!entry) return;
      entry.streams -= 1;
      if (entry.streams > 0) return;
      const leaving = entry;
      leaving.leaving = setTimeout(() => {
        if (this.peers.get(peer) === leaving && leaving.streams === 0) {
          this.peers.delete(peer);
          this.schedule();
        }
      }, LEAVE_GRACE_MS);
      leaving.leaving.unref?.();
    };
  }
  /** Merges a page's patch into its presence; false when the peer isn't this person's open page or the patch is bad. */
  update(peer, viewer, patch) {
    const entry = this.peers.get(peer);
    if (!entry || entry.viewer.user.id !== viewer.user.id) return false;
    if (typeof patch !== "object" || patch === null || Array.isArray(patch)) return false;
    const next = { ...entry.presence };
    for (const [key, value] of Object.entries(patch)) {
      if (value === null || value === void 0) delete next[key];
      else next[key] = value;
    }
    if (Object.keys(next).length > MAX_FIELDS || Buffer.byteLength(JSON.stringify(next)) > MAX_PRESENCE_BYTES) return false;
    entry.presence = next;
    entry.updatedAt = Date.now();
    this.schedule();
    return true;
  }
  /**
   * Sends a page's room events on to every other open page; false when the peer isn't this person's open page or an
   * event is bad (then none is sent). Those over the page's budget are dropped, as the room contract drops them.
   */
  relay(peer, viewer, events) {
    const entry = this.peers.get(peer);
    if (!entry || entry.viewer.user.id !== viewer.user.id || !Array.isArray(events)) return false;
    const frames = [];
    for (const event of events) {
      if (typeof event !== "object" || event === null || Array.isArray(event)) return false;
      const { topic, data } = event;
      if (typeof topic !== "string" || !EVENT_TOPIC.test(topic)) return false;
      if (data !== void 0 && Buffer.byteLength(JSON.stringify(data)) > MAX_EVENT_BYTES) return false;
      const message = { peer, by: entry.viewer.user.id, topic, ...data === void 0 ? {} : { data } };
      frames.push(`event: room
data: ${JSON.stringify(message)}

`);
    }
    const now = Date.now();
    entry.budget = Math.min(EVENT_BURST, entry.budget + (now - entry.toppedAt) / 1e3 * EVENTS_PER_SECOND);
    entry.toppedAt = now;
    for (const frame of frames) {
      if (entry.budget < 1) break;
      entry.budget -= 1;
      for (const [send, owner] of this.listeners) if (owner !== peer) send(frame);
    }
    return true;
  }
  /** The agent changed the artifact: it shows on the list (with `context`, where it worked) for a while. */
  agentActive(agent = {}) {
    if (this.agent) clearTimeout(this.agent.timer);
    const presence = { who: { n: agent.name ?? "Agent", c: AGENT_COLOR } };
    if (agent.context) presence.context = agent.context;
    if (agent.where) presence.where = agent.where;
    const timer = setTimeout(() => {
      this.agent = null;
      this.schedule();
    }, AGENT_LINGER_MS);
    timer.unref?.();
    this.agent = { presence, updatedAt: Date.now(), timer };
    this.schedule();
  }
  /** Everyone on the list now. */
  list() {
    const views = [];
    for (const [peer, entry] of this.peers) {
      const who = entry.presence.who;
      const presence = { ...entry.presence, who: { ...typeof who === "object" && who !== null && !Array.isArray(who) ? who : {}, n: entry.viewer.user.name } };
      views.push({ peer, by: entry.viewer.user.id, name: entry.viewer.user.name, role: entry.viewer.role, presence, updatedAt: entry.updatedAt });
    }
    if (this.agent) {
      const name = String(this.agent.presence.who.n ?? "Agent");
      views.push({ peer: AGENT_PEER, by: "agent", name, kind: "agent", presence: this.agent.presence, updatedAt: this.agent.updatedAt });
    }
    return views;
  }
  /** Answers POST `__presence` ({peer, patch?, events?}); GET gives the list. */
  async handle(request, response, viewer) {
    const method = request.method ?? "GET";
    if (method === "GET") return sendJson(response, 200, { peers: this.list() });
    if (method !== "POST") {
      request.resume();
      return sendJson(response, 405, { code: "method_not_allowed", message: "GET or POST" });
    }
    if (!sameOrigin(request)) {
      request.resume();
      return sendJson(response, 403, { code: "not_granted", message: "Cross-origin write refused." });
    }
    let body;
    try {
      body = JSON.parse((await readBody(request, MAX_BODY_BYTES)).toString("utf8"));
    } catch {
      return sendJson(response, 400, { code: "invalid_argument", message: `Expected {peer, patch?, events?} under ${MAX_BODY_BYTES} bytes.` });
    }
    const { peer, patch, events } = typeof body === "object" && body !== null ? body : {};
    if (typeof peer !== "string" || !PEER_ID.test(peer) || patch === void 0 && events === void 0) {
      return sendJson(response, 400, { code: "invalid_argument", message: "Expected {peer, patch?, events?}." });
    }
    const entry = this.peers.get(peer);
    if (!entry || entry.viewer.user.id !== viewer.user.id) return sendJson(response, 409, { code: "not_joined", message: "That page is not open here (its event stream is closed)." });
    if (events !== void 0 && !this.relay(peer, viewer, events)) {
      return sendJson(response, 400, { code: "invalid_argument", message: `Events are {topic, data}: a topic matching ${EVENT_TOPIC.source}, data at most ${MAX_EVENT_BYTES} bytes of JSON.` });
    }
    if (patch !== void 0 && !this.update(peer, viewer, patch)) return sendJson(response, 409, { code: "not_joined", message: "That patch was not applied (not an object, or the presence would be too big)." });
    response.writeHead(204, { "Cache-Control": "no-store" }).end();
  }
  /** Ends the timers (the server is closing). */
  close() {
    if (this.timer) clearTimeout(this.timer);
    if (this.agent) clearTimeout(this.agent.timer);
    for (const entry of this.peers.values()) if (entry.leaving) clearTimeout(entry.leaving);
    this.peers.clear();
    this.listeners.clear();
  }
  frame() {
    return `event: peers
data: ${JSON.stringify({ peers: this.list() })}

`;
  }
  schedule() {
    if (this.timer) return;
    this.timer = setTimeout(() => {
      this.timer = null;
      const frame = this.frame();
      for (const send of this.listeners.keys()) send(frame);
    }, BROADCAST_MS);
    this.timer.unref?.();
  }
};

async function shareCall(url, action, fail2) {
  const response = await fetch(new URL("__share", url), action ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(action) } : {});
  const body = await response.json().catch(() => ({}));
  if (!response.ok) fail2("SHARE_REFUSED", String(body.message ?? `the server answered ${response.status}`));
  return body;
}
function rolesOf(flags, key, fail2, owner = false) {
  const given = flags.get(key);
  if (given === void 0) return [];
  const roles = given === "all" || given === "true" ? [...GUEST_ROLES] : given.split(",").map((r) => r.trim());
  for (const role of roles) if (!isGuestRole(role) && !(owner && role === "owner")) fail2("INVALID_ROLE", `--${key}: ${owner ? "owner, " : ""}editor, commenter, viewer or all (got ${role}).`);
  return roles;
}
function guestRoles(flags, fail2) {
  const given = flags.get("role");
  if (given === void 0) return [];
  return given.split(",").map((pair) => {
    const [guest = "", role = ""] = pair.split("=").map((part) => part.trim());
    if (!guest || !isGuestRole(role)) fail2("INVALID_ROLE", `--role: <guest id>=editor|commenter|viewer, comma separated (got ${pair}).`);
    return { action: "role", guest, role };
  });
}
async function shareCommand(o) {
  const off = o.flags.has("off");
  const changes = [
    ...rolesOf(o.flags, "reset", o.fail, true).map((role) => ({ action: "reset", role })),
    ...rolesOf(o.flags, "enable", o.fail).map((role) => ({ action: "link", role, on: true })),
    ...rolesOf(o.flags, "disable", o.fail).map((role) => ({ action: "link", role, on: false })),
    ...guestRoles(o.flags, o.fail)
  ];
  const open2 = !off && changes.length === 0;
  let server = await o.running();
  if (!server) {
    const sharing = new Sharing(o.root);
    for (const change of changes) {
      if (change.action === "reset" && change.role === "owner") sharing.resetOwner();
      else if (change.action === "reset") sharing.resetLink(change.role);
      else if (change.action === "role") {
        if (!sharing.setRole(String(change.guest), change.role)) o.fail("SHARE_REFUSED", `No guest ${String(change.guest)}, or the ${String(change.role)} link is off.`);
      } else sharing.setLink(change.role, change.on === true);
    }
    if (off) {
      sharing.setLan(false);
      return { lan: false, message: "Not shared on the local network. Guests already in get their place back when it is shared again (unless their link was reset)." };
    }
    if (!open2 && !sharing.state.lan) {
      return {
        lan: false,
        links: Object.fromEntries(GUEST_ROLES.map((role) => [role, sharing.state.links[role].on ? "on" : "off"])),
        message: `Links changed. Not shared on the local network: ${NOT_SHARED_HINT}`
      };
    }
    server = await o.startShared();
    if (!server) o.fail("SERVER_FAILED", `The server did not start. Run ${o.serveCommand} in the foreground to see why.`);
  }
  let view = await shareCall(server.url, null, o.fail);
  for (const change of changes) view = await shareCall(server.url, change, o.fail);
  if (off || open2 && !view.lan) view = await shareCall(server.url, { action: "lan", on: !off }, o.fail);
  const links = view.links;
  const shown2 = (list) => Object.fromEntries(Object.entries(list).map(([role, link]) => [role, link.on ? link.url : "off"]));
  const tailnet = view.lan ? view.tailnet : void 0;
  const addresses = view.lan ? lanUrls(view) : [];
  const local = view.lan && Array.isArray(view.addresses) ? view.addresses.filter((a) => !isTailnet(String(a))) : [];
  const others = local.length > 1 ? " This computer is on more than one network (addresses): if a link does not open for someone on the same Wi-Fi or LAN, give them the same link with another of those addresses." : "";
  return {
    lan: view.lan,
    ...view.lan ? { addresses } : {},
    links: shown2(links),
    ...tailnet ? {
      tailscale: shown2(tailnet.links),
      tailscaleNote: `This computer has a Tailscale address (${tailnet.address}): the tailscale links open the same roles for people on your tailnet, from any network. Use the links above for people on this Wi-Fi or LAN.`
    } : {},
    guests: view.guests,
    ...view.lan ? {
      note: `Send the link for the role you want to give: editor edits, commenter comments, viewer reads. Anyone on this network with a link joins under a name they type. The owner (this computer) shares from the Share button too.${others}`,
      security: "It is plain http: others on the network can read what passes. A link is the permission: whoever has it gets its role, so send it only to the people meant to have it, and reset a role's link if it went further.",
      stop: o.offCommand
    } : { note: `Not shared on the network: the links work on this computer only. ${NOT_SHARED_HINT}` }
  };
}
var NOT_SHARED_HINT = "share <root> with no options shares it.";
var lanUrls = (view) => (Array.isArray(view.addresses) ? view.addresses : []).map((a) => `http://${String(a)}:${String(view.port)}${String(view.page ?? "/")}`);
async function remoteOn(url, flags, fail2, stopCommand) {
  const given = flags.get("remote");
  if (given === void 0) return {};
  const call = async (action) => {
    const response = await fetch(new URL("__share", url), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(action) });
    const body = await response.json().catch(() => ({}));
    if (response.ok) return body;
    if (response.status === 400 && /^action: /.test(String(body.message ?? ""))) {
      fail2("REMOTE_UNSUPPORTED", `The editor server running for this folder is of an earlier release and cannot open it to another device. Run ${stopCommand}, then open again.`);
    }
    return fail2("SHARE_REFUSED", String(body.message ?? `the server answered ${response.status}`));
  };
  if (given === "off") {
    await call({ action: "remote", on: false });
    return { remote: false };
  }
  const view = await call({ action: "remote", on: true, ...given && given !== "true" ? { host: given } : {} });
  const link = view.remoteLink;
  if (typeof link?.url !== "string") return fail2("SHARE_REFUSED", "The server did not give the owner's link.");
  return {
    remoteUrl: link.url,
    remoteNote: `remoteUrl opens the editor as its owner from another device that reaches this computer at ${String(link.address)} (an app reached remotely, a phone, a laptop on the same network or tailnet). It is the owner's own key, over plain http: open it only on your own devices and give it to nobody (to let others in, \`share\`). \`--remote=off\` closes it; \`share <root> --reset owner\` replaces it.`
  };
}
async function lanOn(url, flags, fail2) {
  if (!flags.has("lan")) return {};
  return { lan: lanUrls(await shareCall(url, { action: "lan", on: true }, fail2)) };
}

var COMMENTS_FILE = "comments.json";
var COMMENTS_VERSION = 1;
var LIMITS = { text: 1e4, label: 1e3, detail: 4e3, anchor: 2048, section: 200, name: 100 };
function sameAuthor(a, b) {
  return a.kind === "user" && b.kind === "user" && (a.principal ?? "") === (b.principal ?? "");
}
var AGENT_AUTHOR = { kind: "agent", name: "agent" };
var CommentsError = class extends Error {
  code;
  status;
  constructor(code, message, status = 400) {
    super(message);
    this.code = code;
    this.status = status;
  }
};
var emptyDoc = () => ({ version: COMMENTS_VERSION, threads: [] });
function randomHex(bytes) {
  const buf = new Uint8Array(bytes);
  globalThis.crypto.getRandomValues(buf);
  return Array.from(buf, (b) => b.toString(16).padStart(2, "0")).join("");
}
var newId = (prefix) => `${prefix}_${randomHex(5)}`;
var isRecord4 = (v) => typeof v === "object" && v !== null && !Array.isArray(v);
var isText = (v, max) => typeof v === "string" && v.length <= max;
function cleanText(v) {
  if (typeof v !== "string") return null;
  const text = v.replace(/\r\n?/g, "\n").trim();
  return text !== "" && text.length <= LIMITS.text ? text : null;
}
function readNewThread(body) {
  if (!isRecord4(body)) return null;
  const text = cleanText(body.text);
  if (text === null || !isText(body.anchor, LIMITS.anchor) || body.anchor === "" || !isText(body.label, LIMITS.label)) return null;
  if (body.detail !== void 0 && !isText(body.detail, LIMITS.detail)) return null;
  if (body.section !== void 0 && (!isText(body.section, LIMITS.section) || body.section === "")) return null;
  if (body.area !== void 0 && typeof body.area !== "boolean") return null;
  if (body.send !== void 0 && typeof body.send !== "boolean") return null;
  return {
    anchor: body.anchor,
    label: body.label.trim() || "Comment",
    ...body.detail ? { detail: body.detail } : {},
    ...body.area ? { area: true } : {},
    ...body.section ? { section: body.section } : {},
    text,
    ...body.send ? { send: true } : {}
  };
}
function readReply(body) {
  if (!isRecord4(body)) return null;
  const text = cleanText(body.text);
  if (text === null) return null;
  if (body.send !== void 0 && typeof body.send !== "boolean") return null;
  return { text, ...body.send ? { send: true } : {} };
}
var readEdit = readReply;
function readStatus(body) {
  return isRecord4(body) && (body.status === "open" || body.status === "resolved") ? body.status : null;
}
function readAgentRequest(body) {
  if (!isRecord4(body)) return null;
  const text = cleanText(body.text);
  if (text === null) return null;
  if (body.label !== void 0 && !isText(body.label, LIMITS.label)) return null;
  if (body.selection !== void 0 && !isText(body.selection, LIMITS.detail)) return null;
  const label = typeof body.label === "string" ? body.label.trim() : "";
  const selection = typeof body.selection === "string" ? body.selection.trim() : "";
  return { text, ...label ? { label } : {}, ...selection ? { selection } : {} };
}
function parseDoc(text) {
  const data = JSON.parse(text);
  if (!isRecord4(data) || data.version !== COMMENTS_VERSION || !Array.isArray(data.threads)) {
    throw new CommentsError("COMMENTS_FILE_INVALID", `not a version ${COMMENTS_VERSION} comments file (expected {"version": 1, "threads": [...]})`, 500);
  }
  const threads = data.threads.filter(
    (t) => isRecord4(t) && typeof t.id === "string" && typeof t.anchor === "string" && typeof t.label === "string" && (t.status === "open" || t.status === "resolved") && Array.isArray(t.messages) && t.messages.every((m) => isRecord4(m) && typeof m.text === "string" && isRecord4(m.author) && (m.author.kind === "user" || m.author.kind === "agent"))
  );
  for (const t of threads) {
    if (!isRecord4(t.location)) t.location = {};
    for (const m of t.messages) if (m.author.principal !== void 0 && typeof m.author.principal !== "string") delete m.author.principal;
  }
  return { version: COMMENTS_VERSION, threads };
}
var formatDoc = (doc) => `${JSON.stringify(doc, null, 2)}
`;
function addThread(doc, input, location, author, now) {
  const thread = {
    id: uniqueId(doc),
    anchor: input.anchor,
    label: input.label,
    ...input.detail ? { detail: input.detail } : {},
    location: { ...location, ...input.section ? { section: input.section } : {}, ...input.area ? { area: true } : {} },
    status: "open",
    createdAt: now,
    updatedAt: now,
    messages: [{ id: newId("m"), author, text: input.text, at: now }]
  };
  if (input.send) sendToAgent(thread, now);
  doc.threads.push(thread);
  return thread;
}
function uniqueId(doc) {
  for (; ; ) {
    const id = newId("c");
    if (!doc.threads.some((t) => t.id === id)) return id;
  }
}
function addMessage(thread, author, text, now) {
  const message = { id: newId("m"), author, text, at: now };
  thread.messages.push(message);
  thread.updatedAt = now;
  if (author.kind === "agent") {
    if (thread.agent) thread.agent = { ...thread.agent, status: "replied", repliedAt: now };
  } else if (thread.status === "resolved") {
    thread.status = "open";
    delete thread.resolvedAt;
  }
  return message;
}
function editMessage(thread, messageId, text, now, by) {
  const message = thread.messages.find((m) => m.id === messageId);
  if (!message) throw new CommentsError("MESSAGE_NOT_FOUND", `No message ${messageId} in ${thread.id}.`, 404);
  if (message.author.kind !== "user" || by && !sameAuthor(message.author, by)) throw new CommentsError("MESSAGE_NOT_EDITABLE", "Only your own messages can be edited.", 403);
  if (message.text !== text) {
    message.text = text;
    message.editedAt = now;
    thread.updatedAt = now;
  }
  return message;
}
function canSendToAgent(thread) {
  const last = thread.messages.at(-1);
  if (thread.status !== "open" || !last || last.author.kind !== "user") return false;
  return !thread.agent || (last.editedAt ?? last.at) > thread.agent.sentAt;
}
function sendToAgent(thread, now) {
  thread.agent = { status: "pending", sentAt: now };
  thread.updatedAt = now;
}
function markDelivered(thread, now, via) {
  if (thread.agent?.status !== "pending") return;
  thread.agent = { ...thread.agent, status: "delivered", deliveredAt: now, via };
}
function setStatus(thread, status, now) {
  if (thread.status === status) return;
  thread.status = status;
  thread.updatedAt = now;
  if (status === "resolved") thread.resolvedAt = now;
  else delete thread.resolvedAt;
}
function findThread(doc, ref) {
  const exact = doc.threads.find((t) => t.id === ref);
  if (exact) return exact;
  const matches = ref.length >= 3 ? doc.threads.filter((t) => t.id.startsWith(ref)) : [];
  if (matches.length === 1) return matches[0];
  throw new CommentsError(
    matches.length ? "AMBIGUOUS_COMMENT" : "COMMENT_NOT_FOUND",
    matches.length ? `${ref} matches ${matches.length} comments; give more of the id.` : `No comment ${ref}.`,
    404
  );
}
function openThreads(doc) {
  return doc.threads.filter((t) => t.status === "open").sort((a, b) => a.createdAt < b.createdAt ? -1 : a.createdAt > b.createdAt ? 1 : 0);
}
var pendingForAgent = (doc) => openThreads(doc).filter((t) => t.agent?.status === "pending");
function agentView(thread, n) {
  return {
    id: thread.id,
    ...n !== void 0 ? { n } : {},
    status: thread.status,
    ...thread.location.file ? { file: thread.location.file } : {},
    where: thread.label,
    ...thread.detail ? { detail: thread.detail } : {},
    location: thread.location,
    anchor: thread.anchor,
    ...thread.agent ? { agent: thread.agent } : {},
    messages: thread.messages.map((m) => ({ from: m.author.kind, name: m.author.name, text: m.text, at: m.at, ...m.editedAt ? { editedAt: m.editedAt } : {} }))
  };
}
function agentViews(doc, threads) {
  const open2 = openThreads(doc);
  return threads.map((t) => {
    const i = open2.indexOf(t);
    return agentView(t, i >= 0 ? i + 1 : void 0);
  });
}

import { spawn as spawn2 } from "node:child_process";
import fs9 from "node:fs";
import os5 from "node:os";

import fs8 from "node:fs";
import fsp3 from "node:fs/promises";
import path8 from "node:path";
var LOCK_STALE_MS = 1e4;
var LOCK_WAIT_MS = 5e3;
var LOCK_RETRY_MS = 20;
var commentsPath = (root) => path8.join(root, COMMENTS_FILE);
async function readComments(root) {
  let text;
  try {
    text = await fsp3.readFile(commentsPath(root), "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return emptyDoc();
    throw error;
  }
  if (text.trim() === "") return emptyDoc();
  try {
    return parseDoc(text);
  } catch (error) {
    if (error instanceof CommentsError) throw new CommentsError(error.code, `${commentsPath(root)}: ${error.message}`, 500);
    throw new CommentsError("COMMENTS_FILE_INVALID", `${commentsPath(root)} is not valid JSON: ${error.message}`, 500);
  }
}
async function lock(root) {
  const file = `${commentsPath(root)}.lock`;
  const deadline = Date.now() + LOCK_WAIT_MS;
  for (; ; ) {
    try {
      const handle = await fsp3.open(file, "wx");
      await handle.writeFile(`${process.pid}
`);
      await handle.close();
      return () => fsp3.rm(file, { force: true });
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
    }
    const info = await fsp3.stat(file).catch(() => null);
    if (info && Date.now() - info.mtimeMs > LOCK_STALE_MS) {
      await fsp3.rm(file, { force: true });
      continue;
    }
    if (Date.now() > deadline) throw new CommentsError("COMMENTS_LOCKED", `${file} is held by another process; try again (or delete it if nothing is running).`, 503);
    await new Promise((resolve) => setTimeout(resolve, LOCK_RETRY_MS));
  }
}
async function writeAtomic2(file, text) {
  const temp = path8.join(path8.dirname(file), `.${path8.basename(file)}.${process.pid}.${Date.now().toString(36)}.tmp`);
  await fsp3.writeFile(temp, text);
  try {
    await fsp3.rename(temp, file);
  } catch (error) {
    await fsp3.rm(temp, { force: true });
    throw error;
  }
}
async function updateComments(root, change) {
  const unlock = await lock(root);
  try {
    const doc = await readComments(root);
    const before = formatDoc(doc);
    const result = await change(doc);
    const after = formatDoc(doc);
    const exists = fs8.existsSync(commentsPath(root));
    if (after !== before && (exists || doc.threads.length > 0)) await writeAtomic2(commentsPath(root), after);
    return result;
  } finally {
    await unlock();
  }
}

var AGENT_GRACE_MS = 6e4;
var AGENT_BUSY_MS = 30 * 6e4;
var REQUEST_TTL_MS = 30 * 6e4;
var REQUESTS_KEPT = 32;
var WAIT_DEFAULT_S = 300;
var WAIT_MAX_S = 3600;
var PRESENCE_CHECK_MS = 5e3;
var SSE_KEEPALIVE_MS = 25e3;
var WATCH_DEBOUNCE_MS = 100;
var POLL_MS = 2e3;
var MAX_BODY_BYTES2 = 256 * 1024;
var TooLarge2 = class extends Error {
};
function sendJson2(response, status, body) {
  const text = JSON.stringify(body);
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(text),
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff"
  });
  response.end(text);
}
function readJson(request) {
  return new Promise((resolve, reject) => {
    if (!/^application\/json\b/i.test(request.headers["content-type"] ?? "")) {
      request.resume();
      reject(new CommentsError("INVALID_CONTENT", "expected application/json", 415));
      return;
    }
    const chunks = [];
    let size = 0;
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES2) {
        reject(new TooLarge2());
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "null"));
      } catch {
        reject(new CommentsError("INVALID_CONTENT", "malformed JSON", 400));
      }
    });
    request.on("error", reject);
  });
}
function defaultUserName() {
  try {
    return os5.userInfo().username.trim() || "you";
  } catch {
    return "you";
  }
}
function createCommentsService(options) {
  const { root, log, agentHook } = options;
  const userName = (options.userName ?? defaultUserName()).slice(0, 100);
  const owner = { author: { kind: "user", name: userName }, canComment: true, canSend: true, admin: true };
  const viewerOf = options.viewer ?? (() => owner);
  const allowWrite = options.allowWrite ?? (() => true);
  const clients = /* @__PURE__ */ new Map();
  const waiters = [];
  const hookRunning = /* @__PURE__ */ new Set();
  const requests = [];
  const requestFates = /* @__PURE__ */ new Map();
  let lastDoc = emptyDoc();
  let lastWaitEnded = 0;
  let lastSent = "";
  let lastPresence = "";
  let queue = Promise.resolve();
  let closed = false;
  const now = () => (/* @__PURE__ */ new Date()).toISOString();
  function presence() {
    const at = Date.now();
    const listening = waiters.length > 0;
    const busy = lastDoc.threads.some(
      (t) => t.status === "open" && t.agent?.status === "delivered" && at - Date.parse(t.agent.deliveredAt ?? t.agent.sentAt) < AGENT_BUSY_MS
    ) || [...requestFates.values()].some((f) => f.state === "working" && at - f.at < AGENT_BUSY_MS);
    const hook = Boolean(agentHook);
    return { available: listening || busy || hook || at - lastWaitEnded < AGENT_GRACE_MS, listening, busy, hook };
  }
  const meOf = (viewer) => ({
    name: viewer.author.name,
    ...viewer.author.principal ? { principal: viewer.author.principal } : {},
    canComment: viewer.canComment,
    canSend: viewer.canSend,
    admin: viewer.admin
  });
  async function shared() {
    lastDoc = await readComments(root);
    return { threads: lastDoc.threads, agent: presence() };
  }
  async function snapshot(viewer) {
    return { ...await shared(), me: meOf(viewer) };
  }
  const frame = (snap) => `event: comments
data: ${JSON.stringify(snap)}

`;
  function broadcast() {
    queue = queue.then(async () => {
      if (closed) return;
      let base;
      try {
        base = await shared();
      } catch (error) {
        log(`comments: reading ${COMMENTS_FILE} failed: ${error.message}`);
        return;
      }
      const text = JSON.stringify(base);
      lastPresence = JSON.stringify(base.agent);
      if (text === lastSent) return;
      lastSent = text;
      for (const [client, viewer] of clients) client.write(frame({ ...base, me: meOf(viewer) }));
    });
    return queue;
  }
  function finishWaiter(waiter, body) {
    if (waiter.done) return;
    waiter.done = true;
    clearTimeout(waiter.timer);
    const i = waiters.indexOf(waiter);
    if (i >= 0) waiters.splice(i, 1);
    if (!waiter.response.writableEnded) sendJson2(waiter.response, 200, body);
    lastWaitEnded = Date.now();
  }
  function setRequestState(id, state) {
    requestFates.delete(id);
    requestFates.set(id, { state, at: Date.now() });
    while (requestFates.size > REQUESTS_KEPT) requestFates.delete(requestFates.keys().next().value);
  }
  function dropStaleRequests() {
    const oldest = Date.now() - REQUEST_TTL_MS;
    while (requests.length > 0 && Date.parse(requests[0].sentAt) < oldest) {
      const dropped = requests.shift();
      setRequestState(dropped.id, "over");
      log(`comments: dropped request ${dropped.id}: no agent took it in ${REQUEST_TTL_MS / 6e4} minutes`);
    }
  }
  async function deliver() {
    if (closed) return;
    dropStaleRequests();
    const waiter = waiters[0];
    if (waiter) {
      const views = await updateComments(root, (doc) => {
        const pending = pendingForAgent(doc);
        const at = now();
        for (const t of pending) markDelivered(t, at, "wait");
        return agentViews(doc, pending);
      });
      const handed = requests.splice(0);
      if (views.length === 0 && handed.length === 0) return;
      if (waiter.done) {
        requests.unshift(...handed);
        if (views.length > 0) {
          await updateComments(root, (doc) => {
            for (const t of doc.threads) if (views.some((v) => v.id === t.id) && t.agent?.via === "wait") t.agent = { status: "pending", sentAt: t.agent.sentAt };
          });
        }
        return;
      }
      finishWaiter(waiter, { threads: views, ...handed.length > 0 ? { requests: handed } : {} });
      for (const request of handed) setRequestState(request.id, "working");
      log(`comments: sent to the agent (wait): ${[...views, ...handed].map((v) => v.id).join(", ")}`);
      await broadcast();
      return;
    }
    if (agentHook) await runHook(agentHook);
  }
  async function runHook(command) {
    if (typeof command !== "string") return runHandler(command);
    const doc = await readComments(root);
    for (const thread of pendingForAgent(doc)) {
      if (hookRunning.has(thread.id)) continue;
      hookRunning.add(thread.id);
      const view = agentViews(doc, [thread])[0];
      const child = spawn2(command, {
        shell: true,
        cwd: root,
        stdio: ["pipe", "ignore", "pipe"],
        env: { ...process.env, ARTIFACT_ROOT: root, COMMENT_ID: thread.id, COMMENTS_FILE: commentsPath(root) }
      });
      let stderr = "";
      child.stderr?.on("data", (chunk) => {
        stderr = (stderr + chunk.toString("utf8")).slice(-2e3);
      });
      child.stdin?.on("error", () => {
      });
      child.stdin?.end(`${JSON.stringify(view)}
`);
      child.on("error", (error) => {
        hookRunning.delete(thread.id);
        log(`comments: the agent hook failed to start: ${error.message}`);
      });
      child.on("exit", (code) => {
        if (code !== 0) {
          hookRunning.delete(thread.id);
          log(`comments: the agent hook exited with ${code} for ${thread.id}; the comment stays waiting${stderr ? `: ${stderr.trim()}` : ""}`);
          return;
        }
        void updateComments(root, (d) => {
          const t = d.threads.find((x) => x.id === thread.id);
          if (t) markDelivered(t, now(), "hook");
        }).finally(() => hookRunning.delete(thread.id)).then(() => {
          log(`comments: sent to the agent (hook): ${thread.id}`);
          return broadcast();
        }).catch((error) => log(`comments: ${error.message}`));
      });
    }
    for (const request of requests.splice(0)) {
      hookRunning.add(request.id);
      setRequestState(request.id, "working");
      const child = spawn2(command, {
        shell: true,
        cwd: root,
        stdio: ["pipe", "ignore", "pipe"],
        env: { ...process.env, ARTIFACT_ROOT: root, REQUEST_ID: request.id, COMMENTS_FILE: commentsPath(root) }
      });
      let stderr = "";
      child.stderr?.on("data", (chunk) => {
        stderr = (stderr + chunk.toString("utf8")).slice(-2e3);
      });
      child.stdin?.on("error", () => {
      });
      child.stdin?.end(`${JSON.stringify({ request })}
`);
      let settled = false;
      const failed = (why) => {
        if (settled) return;
        settled = true;
        hookRunning.delete(request.id);
        requests.unshift(request);
        setRequestState(request.id, "queued");
        log(`comments: the agent hook ${why} for ${request.id}; the request stays waiting${stderr ? `: ${stderr.trim()}` : ""}`);
      };
      child.on("error", (error) => failed(`failed to start (${error.message})`));
      child.on("exit", (code) => {
        if (code !== 0) return failed(`exited with ${code}`);
        settled = true;
        hookRunning.delete(request.id);
        log(`comments: sent to the agent (hook): ${request.id}`);
      });
    }
  }
  async function runHandler(handler) {
    for (const { id } of pendingForAgent(await readComments(root))) {
      if (hookRunning.has(id)) continue;
      hookRunning.add(id);
      try {
        const doc = await readComments(root);
        const thread = pendingForAgent(doc).find((t) => t.id === id);
        if (!thread) continue;
        try {
          await handler.thread(agentViews(doc, [thread])[0]);
        } catch (error) {
          log(`comments: the agent handler failed for ${id}; the comment stays waiting: ${error.message}`);
          continue;
        }
        await updateComments(root, (d) => {
          const t = d.threads.find((x) => x.id === id);
          if (t) markDelivered(t, now(), "hook");
        });
        log(`comments: sent to the agent (handler): ${id}`);
        await broadcast();
      } finally {
        hookRunning.delete(id);
      }
    }
    const failed = [];
    for (const request of requests.splice(0)) {
      setRequestState(request.id, "working");
      try {
        await handler.request(request);
        log(`comments: sent to the agent (handler): ${request.id}`);
      } catch (error) {
        failed.push(request);
        setRequestState(request.id, "queued");
        log(`comments: the agent handler failed for ${request.id}; the request stays waiting: ${error.message}`);
      }
    }
    requests.unshift(...failed);
  }
  let debounce;
  const changed = () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => void broadcast(), WATCH_DEBOUNCE_MS);
  };
  let watcher = null;
  try {
    watcher = fs9.watch(root, (_event, name) => {
      if (name === null || name === COMMENTS_FILE) changed();
    });
    watcher.on("error", () => {
      watcher?.close();
      watcher = null;
    });
  } catch {
    watcher = null;
  }
  let lastStat = "";
  const poll = setInterval(() => {
    fs9.stat(commentsPath(root), (error, info) => {
      const stat = error ? "none" : `${info.mtimeMs}:${info.size}`;
      if (stat !== lastStat) {
        const first = lastStat === "";
        lastStat = stat;
        if (!first) changed();
      }
    });
    if (JSON.stringify(presence()) !== lastPresence && clients.size > 0) void broadcast();
  }, Math.min(POLL_MS, PRESENCE_CHECK_MS));
  poll.unref?.();
  void broadcast();
  async function afterChange(sent) {
    await broadcast();
    if (sent) await deliver();
  }
  function need(allowed, message) {
    if (!allowed) throw new CommentsError("NOT_ALLOWED", message, 403);
  }
  const ONLY_OWNER_SENDS = "Only the owner can send comments to the agent.";
  async function create(request, response, viewer) {
    const input = readNewThread(await readJson(request));
    if (!input) throw new CommentsError("INVALID_COMMENT", "expected {anchor, label, text} with a non-empty text");
    need(!input.send || viewer.canSend, ONLY_OWNER_SENDS);
    let location = {};
    try {
      location = await options.locate?.(input) ?? {};
    } catch (error) {
      log(`comments: could not resolve where a comment points: ${error.message}`);
    }
    const created = await updateComments(root, (doc) => addThread(doc, input, location, viewer.author, now()));
    log(`comments: ${created.id} added on ${created.label}${location.file ? ` (${location.file})` : ""}${input.send ? ", sent to the agent" : ""}`);
    sendJson2(response, 201, { thread: created });
    await afterChange(Boolean(input.send));
  }
  function enqueue(input) {
    if (!presence().available) throw new CommentsError("AGENT_UNAVAILABLE", "no agent is waiting: copy the request for the chat instead", 409);
    const queued = { id: newId("r"), ...input, sentAt: now() };
    requests.push(queued);
    setRequestState(queued.id, "queued");
    log(`comments: request ${queued.id}${input.label ? ` (${input.label})` : ""} for the agent`);
    return queued;
  }
  async function ask(request, response) {
    const input = readAgentRequest(await readJson(request));
    if (!input) throw new CommentsError("INVALID_REQUEST", "expected {text} with a non-empty text");
    const queued = enqueue(input);
    sendJson2(response, 202, { request: queued });
    await deliver();
  }
  async function sendRequest(input) {
    const queued = enqueue(input);
    await deliver();
    return queued;
  }
  async function events(request, response, viewer) {
    response.writeHead(200, {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-store",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no"
    });
    response.write(": connected\n\n");
    response.write(frame(await snapshot(viewer)));
    clients.set(response, viewer);
    const keepAlive = setInterval(() => response.write(": ping\n\n"), SSE_KEEPALIVE_MS);
    keepAlive.unref?.();
    response.on("close", () => {
      clearInterval(keepAlive);
      clients.delete(response);
    });
  }
  async function wait(request, response, url) {
    const asked = Number(url.searchParams.get("timeout") ?? WAIT_DEFAULT_S);
    const seconds = Number.isFinite(asked) && asked > 0 ? Math.min(asked, WAIT_MAX_S) : WAIT_DEFAULT_S;
    const waiter = { response, done: false };
    waiters.push(waiter);
    for (const [id, fate] of requestFates) if (fate.state === "working") setRequestState(id, "over");
    waiter.timer = setTimeout(() => {
      finishWaiter(waiter, { threads: [] });
      void broadcast();
    }, seconds * 1e3);
    const gone = () => {
      if (waiter.done) return;
      finishWaiter(waiter, { threads: [] });
      void broadcast();
    };
    response.on("close", gone);
    await broadcast();
    await deliver();
  }
  async function handle(request, response, rest) {
    const method = request.method ?? "GET";
    const url = new URL(request.url ?? "/", "http://localhost");
    const parts = rest.split("/").filter(Boolean);
    const reading = method === "GET" || method === "HEAD";
    try {
      if (!reading && !allowWrite(request)) {
        request.resume();
        throw new CommentsError("NOT_ALLOWED", "cross-origin request", 403);
      }
      const viewer = viewerOf(request);
      if (!viewer) {
        request.resume();
        throw new CommentsError("NOT_ALLOWED", "not shared with you", 403);
      }
      const commenting = !reading && parts[0] !== "agent" && parts[1] !== "send";
      if (commenting && !viewer.canComment) {
        request.resume();
        throw new CommentsError("NOT_ALLOWED", "You can read the comments here, not add or change them.", 403);
      }
      if (parts.length === 0) {
        if (reading) return sendJson2(response, 200, await snapshot(viewer));
        if (method === "POST") return await create(request, response, viewer);
      } else if (parts.length === 1 && parts[0] === "events") {
        if (reading) return await events(request, response, viewer);
      } else if (parts.length === 2 && parts[0] === "agent" && parts[1] === "wait") {
        need(viewer.canSend, "Only the owner's agent waits for comments.");
        if (reading) return await wait(request, response, url);
      } else if (parts.length === 2 && parts[0] === "agent" && parts[1] === "send-all") {
        if (method === "POST") {
          request.resume();
          need(viewer.canSend, ONLY_OWNER_SENDS);
          const result = await updateComments(root, (doc) => {
            const open2 = doc.threads.filter((t) => t.status === "open" && t.messages.some((m) => m.author.kind === "user"));
            const sent = open2.filter(canSendToAgent);
            const at = now();
            for (const t of sent) sendToAgent(t, at);
            return { threads: sent, sent: { count: sent.length, open: open2.length } };
          });
          log(`comments: ${result.sent.count} of ${result.sent.open} open thread(s) sent to the agent`);
          sendJson2(response, 200, result);
          return await afterChange(result.sent.count > 0);
        }
      } else if (parts.length === 2 && parts[0] === "agent" && parts[1] === "requests") {
        need(viewer.canSend, ONLY_OWNER_SENDS);
        if (method === "POST") return await ask(request, response);
      } else if (parts.length === 1) {
        const id = parts[0];
        if (method === "PATCH") {
          const status = readStatus(await readJson(request));
          if (!status) throw new CommentsError("INVALID_STATUS", 'expected {status: "open" | "resolved"}');
          const t = await updateComments(root, (doc) => {
            const found = findThread(doc, id);
            setStatus(found, status, now());
            return found;
          });
          log(`comments: ${id} ${status === "resolved" ? "resolved" : "reopened"}`);
          sendJson2(response, 200, { thread: t });
          return await afterChange(false);
        }
        if (method === "DELETE") {
          await updateComments(root, (doc) => {
            const found = findThread(doc, id);
            const first = found.messages[0];
            need(viewer.admin || first !== void 0 && sameAuthor(first.author, viewer.author), "Only the person who started this comment, or the owner, can delete it.");
            doc.threads.splice(doc.threads.indexOf(found), 1);
          });
          log(`comments: ${id} deleted`);
          sendJson2(response, 200, { deleted: id });
          return await afterChange(false);
        }
      } else if (parts.length === 2 && parts[1] === "messages") {
        if (method === "POST") {
          const id = parts[0];
          const input = readReply(await readJson(request));
          if (!input) throw new CommentsError("INVALID_COMMENT", "expected {text} with a non-empty text");
          need(!input.send || viewer.canSend, ONLY_OWNER_SENDS);
          const t = await updateComments(root, (doc) => {
            const found = findThread(doc, id);
            addMessage(found, viewer.author, input.text, now());
            if (input.send) sendToAgent(found, now());
            return found;
          });
          log(`comments: reply on ${id}${input.send ? ", sent to the agent" : ""}`);
          sendJson2(response, 200, { thread: t });
          return await afterChange(Boolean(input.send));
        }
      } else if (parts.length === 3 && parts[1] === "messages") {
        if (method === "PATCH") {
          const id = parts[0];
          const messageId = parts[2];
          const input = readEdit(await readJson(request));
          if (!input) throw new CommentsError("INVALID_COMMENT", "expected {text} with a non-empty text");
          need(!input.send || viewer.canSend, ONLY_OWNER_SENDS);
          const t = await updateComments(root, (doc) => {
            const found = findThread(doc, id);
            editMessage(found, messageId, input.text, now(), viewer.author);
            if (input.send && canSendToAgent(found)) sendToAgent(found, now());
            return found;
          });
          log(`comments: message edited on ${id}${input.send ? ", sent to the agent" : ""}`);
          sendJson2(response, 200, { thread: t });
          return await afterChange(Boolean(input.send));
        }
      } else if (parts.length === 2 && parts[1] === "send") {
        if (method === "POST") {
          const id = parts[0];
          request.resume();
          need(viewer.canSend, ONLY_OWNER_SENDS);
          const t = await updateComments(root, (doc) => {
            const found = findThread(doc, id);
            if (!canSendToAgent(found)) throw new CommentsError("NOTHING_TO_SEND", "the agent already has everything in this comment", 409);
            sendToAgent(found, now());
            return found;
          });
          log(`comments: ${id} sent to the agent`);
          sendJson2(response, 200, { thread: t });
          return await afterChange(true);
        }
      } else {
        return sendJson2(response, 404, { code: "NOT_FOUND", message: "no such comments route" });
      }
      request.resume();
      sendJson2(response, 405, { code: "METHOD_NOT_ALLOWED", message: `${method} is not allowed here` });
    } catch (error) {
      if (response.headersSent) throw error;
      if (error instanceof CommentsError) return sendJson2(response, error.status, { code: error.code, message: error.message });
      if (error instanceof TooLarge2) return sendJson2(response, 413, { code: "TOO_LARGE", message: "request body is too large" });
      throw error;
    }
  }
  function close() {
    closed = true;
    clearInterval(poll);
    clearTimeout(debounce);
    watcher?.close();
    for (const waiter of [...waiters]) finishWaiter(waiter, { threads: [], closed: true });
    for (const client of clients.keys()) client.end();
    clients.clear();
  }
  function requestStates() {
    const states = {};
    for (const [id, fate] of requestFates) if (fate.state !== "over") states[id] = fate.state;
    return states;
  }
  return { handle, presence, deliver, sendRequest, requestStates, close };
}

var SCRIPT = fileURLToPath(import.meta.url);
var SKILL_DIR = path9.dirname(path9.dirname(SCRIPT));
var EDITOR_DIR = path9.join(path9.dirname(SCRIPT), "editor");
var KIND = "whiteboard";
var DEFAULT_PORT = 4770;
var NOUN = { en: "whiteboard", zh: "\u767D\u677F", zhThis: "\u8FD9\u5757\u767D\u677F" };
var MAX_DOC_BYTES = 204800;
var MAX_BOARD_BYTES = 2097152;
var MAX_DEPTH = 8;
var MAX_ELEMENTS = 800;
var MAX_TEXT = 4e3;
var MAX_POINTS = 4e3;
var MAX_DATA_URI = 102400;
var MAX_EMBED = 16384;
var MAX_STATE = 16384;
var MAX_LABEL = 200;
var MAX_BATCH_WRITES = 50;
var MAX_BATCH_BYTES = 1024 * 1024;
var MAX_UPLOAD_BYTES = 20 * 1024 * 1024;
var SEGMENT = /^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$/;
var ELEMENT_ID = /^(?!\.{1,40}$)[A-Za-z0-9_.~:@+-]{1,40}$/;
var LOCAL_USER_ID = "local";
var IDEA_PATH = `data/users/${LOCAL_USER_ID}/idea`;
var MAX_IDEA_BYTES = 64 * 1024;
var IDEA_FIELDS = /* @__PURE__ */ new Set(["says", "about", "read", "options"]);
var CLAIM_PATH = /^board\/claim-([a-z0-9]{8})$/;
var COLOR_HEX = /^#[0-9a-fA-F]{6}$/;
var BLOB_URL = /^\/?_blob\/([0-9a-f]{32})$/;
var BLOB_ID = /^[0-9a-f]{32}$/;
var RASTER_URI = /^data:image\/(webp|jpeg|png);base64,[A-Za-z0-9+/=]+$/;
var BOARD_COLLECTIONS = ["elements", "board", "comments"];
var AGENT_TYPES = ["shape", "container", "text", "stroke", "arrow", "image", "html", "table", "link"];
var PEOPLE_TYPES = ["note", "sticker"];
var SHAPE_KINDS = ["rect", "rounded", "ellipse", "diamond", "pill", "hexagon", "parallelogram", "database", "queue", "document", "cloud", "person"];
var FILLS = ["yellow", "peach", "pink", "green", "blue", "purple", "white"];
var INKS = ["ink", "terracotta", "blue", "green", "purple"];
var SIZES = ["small", "body", "large", "title", "huge"];
var SIDES = ["top", "right", "bottom", "left"];
var LINK_KINDS = ["slides", "motion", "doc", "design", "dashboard", "whiteboard"];
var LINK_HOSTS = ["claude.ai", "www.claude.ai", "preview.claude.ai", "claude-ai.staging.ant.dev"];
var LINK_PATH = /^\/(?:code\/)?artifact\/(?:[A-Za-z0-9_-]*-)?(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|([1-9A-HJ-NP-Za-km-z]{22}))$/;
var LINK_KEY = /^[A-Za-z0-9_-]{16,64}$/;
var BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
var MAX_HREF = 512;
var base58Fits = (id) => [...id].reduce((n, c) => n * 58n + BigInt(BASE58.indexOf(c)), 0n) <= (1n << 128n) - 1n;
function linkHref(href) {
  if (typeof href !== "string" || href.length > MAX_HREF || /[\s\p{Cc}]/u.test(href)) return null;
  const [base = "", ...rest] = (href.split("#")[0] ?? "").split("?");
  const [key = ""] = rest.join("?").split("&").filter((q) => q.startsWith("sk="));
  let url;
  try {
    url = new URL(base + (key && LINK_KEY.test(key.slice(3)) ? `?${key}` : ""));
  } catch {
    return null;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") return null;
  if (url.port || url.username || url.password) return null;
  const host = url.hostname.replace(/\.+$/, "").toLowerCase();
  if (!LINK_HOSTS.includes(host)) return null;
  const m = LINK_PATH.exec(url.pathname);
  if (!m || m[1] !== void 0 && !base58Fits(m[1])) return null;
  const out = `https://${host}${url.pathname}${url.search}`;
  return out.length <= MAX_HREF ? out : null;
}
var IMAGE_MIMES = ["image/png", "image/jpeg", "image/gif", "image/webp"];
var VIDEO_MIMES = ["video/mp4", "video/webm"];
var NOT_VIDEO_BRANDS = /* @__PURE__ */ new Set(["avif", "avis", "heic", "heix", "heim", "heis", "hevc", "hevx", "hevm", "hevs", "mif1", "mif2", "msf1", "miaf", "jp2 ", "jpx ", "jpm ", "mjp2", "crx ", "M4A ", "M4B ", "M4P ", "F4A ", "F4B "]);
var REPLACE_ONLY_DOCS = /* @__PURE__ */ new Set(["board/timer"]);
var CONTENT_TYPES = {
  html: "text/html; charset=utf-8",
  js: "text/javascript; charset=utf-8",
  css: "text/css; charset=utf-8",
  json: "application/json; charset=utf-8",
  svg: "image/svg+xml",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
  webp: "image/webp",
  woff2: "font/woff2"
};
var CliError = class extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
};
var isObject2 = (v) => typeof v === "object" && v !== null && !Array.isArray(v);
function storeBytes(value) {
  const text = JSON.stringify(value) ?? "";
  return Buffer.byteLength(text, "utf8") + 5 * (text.match(/[<>&]/g)?.length ?? 0) + 3 * (text.match(/[\u2028\u2029]/g)?.length ?? 0);
}
function depthOf(value, limit = 64) {
  if (typeof value !== "object" || value === null) return 0;
  let deepest = 0;
  for (const v of Array.isArray(value) ? value : Object.values(value)) {
    deepest = Math.max(deepest, depthOf(v, limit - 1));
    if (deepest >= limit) break;
  }
  return deepest + 1;
}
var kib = (n) => n >= 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(2)} MiB` : `${(n / 1024).toFixed(1)} KiB`;
var extOf = (name) => path9.extname(name).slice(1).toLowerCase();
var contentTypeOf = (name) => CONTENT_TYPES[extOf(name)] ?? "application/octet-stream";
var quote = (s) => /^[A-Za-z0-9_./:@%+=-]+$/.test(s) ? s : `'${s.replace(/'/g, `'\\''`)}'`;
var cmd = (name, ...args) => ["node", quote(SCRIPT), name, ...args.map(quote)].join(" ");
var chars = (s) => Array.from(s).length;
var isNum = (v) => typeof v === "number" && Number.isFinite(v);
var collectionOf = (p) => p.slice(0, p.lastIndexOf("/"));
function print(value, compact = false) {
  process.stdout.write(`${compact ? JSON.stringify(value) : JSON.stringify(value, null, 2)}
`);
}
var BARE_FLAGS = ["text", "json", "wait", "all", "resolve", "reopen", "lan", "remote", "off", "force"];
function parseArgs(argv) {
  const positional = [];
  const flags = /* @__PURE__ */ new Map();
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith("--")) {
      const eq = arg.indexOf("=");
      if (eq > 0) flags.set(arg.slice(2, eq), arg.slice(eq + 1));
      else if (i + 1 < argv.length && !argv[i + 1].startsWith("--") && !BARE_FLAGS.includes(arg.slice(2))) flags.set(arg.slice(2), argv[++i]);
      else flags.set(arg.slice(2), "true");
    } else positional.push(arg);
  }
  return { positional, flags };
}
function writeFileAtomic(file, data) {
  fs10.mkdirSync(path9.dirname(file), { recursive: true });
  const tmp = path9.join(path9.dirname(file), `.tmp-${process.pid}-${Date.now()}-${path9.basename(file)}`);
  fs10.writeFileSync(tmp, data);
  fs10.renameSync(tmp, file);
}
function resolveRoot(given, { create = false } = {}) {
  if (!given) throw new CliError("MISSING_ROOT", "Give the board folder (for example designs/<slug>).");
  const root = path9.resolve(given);
  const stat = fs10.statSync(root, { throwIfNoEntry: false });
  if (stat && !stat.isDirectory()) throw new CliError("NOT_A_FOLDER", `${given} is a file; the board is a folder.`);
  if (!stat) {
    if (!create) throw new CliError("NOT_FOUND", `${root} does not exist. Write the board first: ${cmd("write-db", given, "batch.json")}.`);
    fs10.mkdirSync(root, { recursive: true });
  }
  return root;
}
function splitPath(p, what) {
  const clean = String(p ?? "").replace(/^\/+|\/+$/g, "");
  const segs = clean === "" ? [] : clean.split("/");
  if (segs.length === 0 || segs.length > 16 || !segs.every((s) => SEGMENT.test(s))) {
    throw new CliError("INVALID_PATH", `${JSON.stringify(p)} is not a ${what} path: "/"-separated segments of letters, digits and _ - . ~ : @ +.`);
  }
  if (segs[0] === "data" && segs[1] === "users" && segs[2] === "me") segs[2] = LOCAL_USER_ID;
  return segs;
}
function docSegments(p) {
  const segs = splitPath(p, "document");
  if (segs.length % 2 !== 0) throw new CliError("INVALID_PATH", `${p} names a collection; a document path is collection/doc_id (for example elements/e1).`);
  return segs;
}
var docFile = (root, segs) => path9.join(root, "db", ...segs.slice(0, -1), `${segs.at(-1)}.json`);
function listDocFiles(root) {
  const out = /* @__PURE__ */ new Map();
  const base = path9.join(root, "db");
  const walk = (dir, rel) => {
    let entries;
    try {
      entries = fs10.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.name.startsWith(".")) continue;
      const full = path9.join(dir, e.name);
      if (e.isDirectory()) walk(full, [...rel, e.name]);
      else if (e.isFile() && e.name.endsWith(".json")) {
        const segs = [...rel, e.name.slice(0, -5)];
        if (segs.length % 2 !== 0 || !segs.every((s) => SEGMENT.test(s))) continue;
        out.set(segs.join("/"), { file: full });
      }
    }
  };
  walk(base, []);
  return out;
}
function readDoc(root, p) {
  const segs = docSegments(p);
  const file = docFile(root, segs);
  let text;
  try {
    text = fs10.readFileSync(file, "utf8");
  } catch {
    return { path: segs.join("/"), exists: false, file };
  }
  try {
    const data = JSON.parse(text);
    if (!isObject2(data)) throw new Error("not an object");
    return { path: segs.join("/"), exists: true, data, file, bytes: Buffer.byteLength(text) };
  } catch (error) {
    throw new CliError("DAMAGED_DOCUMENT", `${file} is not a JSON object (${error.message}). Rewrite it with set.`);
  }
}
function readAllDocs(root) {
  const docs = /* @__PURE__ */ new Map();
  const damaged = [];
  for (const [p, { file }] of listDocFiles(root)) {
    try {
      const data = JSON.parse(fs10.readFileSync(file, "utf8"));
      if (isObject2(data)) docs.set(p, data);
      else damaged.push(p);
    } catch {
      damaged.push(p);
    }
  }
  return { docs, damaged };
}
var isDeleteMarker = (v) => v === null || isObject2(v) && v.__delete__ === true && Object.keys(v).length === 1;
function mergePatch(target, patch) {
  const out = isObject2(target) ? { ...target } : {};
  for (const [k, v] of Object.entries(patch)) {
    if (k === "__proto__") continue;
    if (isDeleteMarker(v)) delete out[k];
    else if (isObject2(v)) out[k] = mergePatch(out[k], v);
    else out[k] = v;
  }
  return out;
}
function hasDeleteMarker(v) {
  if (Array.isArray(v)) return v.some(hasDeleteMarker);
  if (!isObject2(v)) return false;
  if (v.__delete__ === true) return true;
  return Object.values(v).some(hasDeleteMarker);
}
function imageSrcProblem(root, src) {
  if (typeof src !== "string" || src === "") return `src is an upload's url ("_blob/<id>", from upload) or a data:image/\u2026 URI.`;
  const blob = BLOB_URL.exec(src);
  if (blob) {
    if (!fs10.existsSync(blobFile(root, blob[1]))) return `${src} is not in this board's _blobs/. Upload the image first (${cmd("upload", root, "<file>")}) and use the url it prints.`;
    if (readBlobMeta(root, blob[1])?.contentType.startsWith("video/")) return `${src} is a video; src is the picture shown for it (its still), and the video goes in "video".`;
    return null;
  }
  if (src.startsWith("data:image/svg+xml")) {
    if (src.length > MAX_DOC_BYTES) return "the SVG is too large for one element.";
    if (src.startsWith("data:image/svg+xml,") && src.includes("#")) return 'a "#" in an SVG data URI ends it: write a colour as %23F6BD78 (and a lone % as %25).';
    const svg = svgText(src);
    if (svg === null) return "the SVG data URI does not decode.";
    if (!/^\s*<svg[\s>]/i.test(svg)) return "the SVG data URI holds no <svg> element.";
    return null;
  }
  if (src.startsWith("data:")) {
    if (!RASTER_URI.test(src)) return "an inline image is data:image/(webp|jpeg|png);base64,\u2026; a larger or other image is an upload.";
    if (src.length > MAX_DATA_URI) return `the inline image is ${kib(src.length)}; inline images are at most 100 KB. Upload it instead.`;
    return null;
  }
  return "src is this board's own _blob/<32 hex> (from upload) or a data:image/\u2026 URI; never an external URL.";
}
function svgText(src) {
  const comma = src.indexOf(",");
  if (comma < 0) return null;
  const head = src.slice(0, comma);
  const body = src.slice(comma + 1);
  try {
    return head.endsWith(";base64") ? Buffer.from(body, "base64").toString("utf8") : decodeURIComponent(body.replace(/[\t\n\r]/g, ""));
  } catch {
    return null;
  }
}
function videoProblem(root, video) {
  const blob = typeof video === "string" ? BLOB_URL.exec(video) : null;
  if (!blob) return 'video is an upload of this board ("_blob/<id>") holding a video; the page drops any other value. Keep it as the page wrote it.';
  if (!fs10.existsSync(blobFile(root, blob[1]))) return `video: ${video} is not in this board's _blobs/; the page shows the still alone.`;
  const type = readBlobMeta(root, blob[1])?.contentType;
  if (type !== void 0 && !type.startsWith("video/")) return `video: ${video} is a ${type}, not a video.`;
  return null;
}
var colorOk = (v, names) => v === void 0 || typeof v === "string" && (names.includes(v) || COLOR_HEX.test(v));
var endOk = (v) => typeof v === "string" && ELEMENT_ID.test(v) || Array.isArray(v) && v.length === 2 && v.every(isNum);
function elementProblem(root, data) {
  const type = data.type;
  if (typeof type !== "string") return 'needs a "type" (shape, container, text, stroke, arrow, image, html, table or link).';
  if ("id" in data) return `an element's id is its document id (elements/<id>); leave "id" out of its fields.`;
  if (type === "arrow") {
    if (!endOk(data.from) || !endOk(data.to)) return `an arrow's "from" and "to" are element ids, or a free end [x, y].`;
    if (JSON.stringify(data.from) === JSON.stringify(data.to)) return "an arrow joins two different ends.";
    for (const k of ["fromSide", "toSide"]) if (data[k] !== void 0 && !SIDES.includes(data[k])) return `${k} is one of ${SIDES.join(", ")}.`;
    if (data.label !== void 0 && (typeof data.label !== "string" || chars(data.label) > MAX_LABEL)) return `an arrow's label is text of at most ${MAX_LABEL} characters.`;
    if (data.bends !== void 0 && !(Array.isArray(data.bends) && (data.bends[0] === "h" || data.bends[0] === "v") && data.bends.length <= 13 && data.bends.slice(1).every(isNum))) return 'bends is ["h" | "v", then up to 12 numbers].';
    if (!colorOk(data.color, INKS)) return `an arrow's color is one of ${INKS.join(", ")} or #rrggbb.`;
    return null;
  }
  if (!isNum(data.x) || !isNum(data.y)) return `a ${type} needs numbers "x" and "y"; the page drops it without them.`;
  for (const k of ["w", "h"]) if (data[k] !== void 0 && !isNum(data[k])) return `${k} is a number.`;
  if (data.text !== void 0 && typeof data.text !== "string") return "text is a string.";
  if (typeof data.text === "string" && chars(data.text) > MAX_TEXT) return `its text is ${chars(data.text)} characters; at most ${MAX_TEXT}.`;
  if (data.size !== void 0 && !SIZES.includes(data.size)) return `size is one of ${SIZES.join(", ")}.`;
  switch (type) {
    case "shape":
      if (data.kind !== void 0 && !SHAPE_KINDS.includes(data.kind)) return `kind is one of ${SHAPE_KINDS.join(", ")}.`;
      if (!colorOk(data.color, FILLS)) return `a block's color is one of ${FILLS.join(", ")} or #rrggbb.`;
      if (!colorOk(data.stroke, INKS)) return `stroke is one of ${INKS.join(", ")} or #rrggbb.`;
      return null;
    case "container":
      return colorOk(data.color, FILLS) ? null : `a section's color is one of ${FILLS.join(", ")} or #rrggbb.`;
    case "text":
      if (data.wrap !== void 0 && !isNum(data.wrap)) return "wrap is the width it wraps at, a number.";
      return colorOk(data.color, INKS) ? null : `a text's color is one of ${INKS.join(", ")} or #rrggbb.`;
    case "stroke": {
      const pts = data.points;
      if (!Array.isArray(pts) || pts.length < 2 || pts.length % 2 !== 0 || !pts.every(isNum)) return "points is [x0, y0, x1, y1, \u2026], numbers relative to (x, y).";
      if (pts.length / 2 > MAX_POINTS) return `${pts.length / 2} points; a pen line holds at most ${MAX_POINTS} (the page drops the rest).`;
      return colorOk(data.color, INKS) ? null : `a pen line's color is one of ${INKS.join(", ")} or #rrggbb.`;
    }
    case "image": {
      const bad = imageSrcProblem(root, data.src);
      if (bad) return `image: ${bad}`;
      return data.video === void 0 ? null : videoProblem(root, data.video);
    }
    case "html":
      if (typeof data.html !== "string" || data.html === "") return 'an embed needs "html", the page it runs.';
      if (chars(data.html) > MAX_EMBED) return `its html is ${chars(data.html)} characters; past ${MAX_EMBED} the page cuts it off, script and all.`;
      if (data.state !== void 0 && (typeof data.state !== "string" || chars(data.state) > MAX_STATE)) return `state is JSON text in a string, at most ${MAX_STATE} characters (anything else is dropped).`;
      if (typeof data.state === "string" && data.state !== "") {
        try {
          JSON.parse(data.state);
        } catch {
          return "state is JSON text (what load() returns until someone saves).";
        }
      }
      return null;
    case "table":
      if (!isObject2(data.cols) || !isObject2(data.rows)) return 'a table is {"cols": {c1: {at: 1}, \u2026}, "rows": {r1: {at: 1, c1: "\u2026"}, \u2026}}.';
      return null;
    case "link":
      if (linkHref(data.href) === null) return "a link card's href is a claude.ai artifact link (https://claude.ai/artifact/<id>, or \u2026/code/artifact/<uuid>); the page drops any other address.";
      if (data.kind !== void 0 && !LINK_KINDS.includes(data.kind)) return `a link card's kind is one of ${LINK_KINDS.join(", ")}.`;
      return null;
    default:
      return null;
  }
}
function ideaProblem(data) {
  const p = "data/users/me/idea";
  const extra = Object.keys(data).filter((k) => !IDEA_FIELDS.has(k));
  if (extra.length) return `${p} holds says, about, read and options only (not ${extra.join(", ")}).`;
  if (typeof data.says !== "string" || !data.says.trim() || data.says.length > 160) return `${p}: says is one plain sentence, at most 160 characters.`;
  if (data.about !== void 0 && !(Array.isArray(data.about) && data.about.every((x) => typeof x === "string"))) return `${p}: about is [elementId, \u2026].`;
  if (data.read !== void 0 && !(Array.isArray(data.read) && data.read.every((x) => isObject2(x) && typeof x.id === "string"))) return `${p}: read is [the whole document of each element an edit changes or removes, with its id, \u2026].`;
  const options = data.options;
  if (!Array.isArray(options) || options.length < 2 || options.length > 4) return `${p}: options is 2 to 4 options.`;
  for (const [n, o] of options.entries()) {
    if (!isObject2(o) || typeof o.label !== "string" || !o.label.trim() || o.label.length > 60) return `${p}: options[${n}].label is at most 60 characters.`;
    if (o.why !== void 0 && (typeof o.why !== "string" || o.why.length > 160)) return `${p}: options[${n}].why is at most 160 characters.`;
    if (!Array.isArray(o.edits) || o.edits.length === 0 || o.edits.length > 60 || !o.edits.every((e) => isObject2(e) && typeof e.id === "string")) return `${p}: options[${n}].edits is 1 to 60 edits, each with an id.`;
    if (storeBytes(o.edits) > 24 * 1024) return `${p}: options[${n}].edits is over 24 KB.`;
  }
  if (storeBytes(data) > MAX_IDEA_BYTES) return `${p} is over 64 KB.`;
  return null;
}
function documentProblem(root, segs, data, { agent, strict = agent, before }) {
  const p = segs.join("/");
  const bytes = storeBytes(data);
  if (bytes > MAX_DOC_BYTES) return `${p} would be ${kib(bytes)}; the store refuses a document over 200 KB. Shorten its text or use a smaller image (an upload, not a data: URI).`;
  if (depthOf(data) > MAX_DEPTH) return `${p} nests deeper than ${MAX_DEPTH} levels; the store refuses it.`;
  const [collection, id] = segs;
  if (segs.length === 2 && collection === "elements") {
    if (!ELEMENT_ID.test(id)) return `${p}: an element id is 1\u201340 of A\u2013Z a\u2013z 0\u20139 _ . ~ : @ + -, not all dots; the page drops any other.`;
    if (agent) {
      if (PEOPLE_TYPES.includes(data.type) && before?.type !== data.type) return `${p}: a ${data.type} is people's; a note is a rounded yellow shape, and stickers are left as they are.`;
      if (before?.type === "image" && before.video !== void 0 && data.type === "image" && data.video === void 0) return `${p}: this image plays a video someone added; keep its "video" (move or resize it with update) or delete the element.`;
      if (!AGENT_TYPES.includes(data.type) && !PEOPLE_TYPES.includes(data.type)) return `${p}: type ${JSON.stringify(data.type)} is not one the agent writes (${AGENT_TYPES.join(", ")}).`;
    }
    if (agent || strict && AGENT_TYPES.includes(data.type)) {
      const bad = elementProblem(root, data);
      if (bad && !(agent && before && before.type === data.type && elementProblem(root, before) === bad)) return `${p}: ${bad}`;
    }
    return null;
  }
  if (p === "board/meta") {
    if (!strict) return null;
    if (data.v !== void 0 && !isNum(data.v)) return "board/meta: v is 1.";
    if (data.title !== void 0 && typeof data.title !== "string") return "board/meta: title is a string.";
    if (data.order !== void 0 && !(Array.isArray(data.order) && data.order.every((x) => typeof x === "string"))) return "board/meta: order is [elementId, \u2026], back to front.";
    if (agent && (typeof data.title !== "string" || data.v !== 1 || !Array.isArray(data.order))) return 'board/meta is {"v": 1, "title": "\u2026", "order": [elementId, \u2026]} (ids back to front).';
    return null;
  }
  if (!agent) return null;
  if (CLAIM_PATH.test(p)) {
    const area = ["x", "y", "w", "h"].every((k) => isNum(data[k])) && Object.keys(data).length === 4;
    const ids = Array.isArray(data.ids) && data.ids.length > 0 && data.ids.every((x) => typeof x === "string" && ELEMENT_ID.test(x)) && Object.keys(data).length === 1;
    return area || ids ? null : `${p}: a claim is {"x", "y", "w", "h"} (the ground you will fill) or {"ids": [...]} (what you will change).`;
  }
  if (collection === "board" && /^claim-/.test(id ?? "")) return `${p}: a claim is board/claim-<claim>, the claim from the view context (the context command prints it: 8 lowercase letters or digits).`;
  if (p === IDEA_PATH) return ideaProblem(data);
  if (p === "board/timer" || p === "board/inks" || collection === "comments" || collection === "data") return `${p} is the editor's own; leave it alone.`;
  return `${p}: the page reads board/meta, elements/<id> and the editor's own documents; nothing else.`;
}
function resolveFileRefs(value, where) {
  if (Array.isArray(value)) return value.map((v, i) => resolveFileRefs(v, `${where}[${i}]`));
  if (!isObject2(value)) return value;
  const keys = Object.keys(value);
  if (keys.length === 1 && keys[0] === "$file") {
    const file = path9.resolve(String(value.$file));
    try {
      return fs10.readFileSync(file, "utf8");
    } catch {
      throw new CliError("FILE_NOT_FOUND", `${where}: {"$file": ${JSON.stringify(value.$file)}} \u2014 no such file (paths are relative to ${process.cwd()}).`);
    }
  }
  return Object.fromEntries(keys.map((k) => [k, resolveFileRefs(value[k], `${where}.${k}`)]));
}
function applyWrites(root, writes, { agent = true } = {}) {
  if (!Array.isArray(writes) || writes.length === 0) throw new CliError("EMPTY_BATCH", "The batch has no writes.");
  if (writes.length > MAX_BATCH_WRITES) throw new CliError("BATCH_TOO_LARGE", `${writes.length} writes; a batch is at most ${MAX_BATCH_WRITES}. Split it.`);
  const planned = [];
  const seen = /* @__PURE__ */ new Set();
  let total = 0;
  writes.forEach((w, i) => {
    const where = `writes[${i}]`;
    if (!isObject2(w)) throw new CliError("INVALID_WRITE", `${where} is not an object.`);
    const op = w.op;
    if (!["set", "update", "delete"].includes(op)) throw new CliError("INVALID_WRITE", `${where}.op is ${JSON.stringify(op)}; use set, update or delete.`);
    const given = w.path ?? (w.collection !== void 0 && w.doc_id !== void 0 ? `${w.collection}/${w.doc_id}` : void 0);
    if (given === void 0) throw new CliError("INVALID_WRITE", `${where} names no document: give "path": "collection/doc_id" (or "collection" and "doc_id").`);
    let segs;
    try {
      segs = docSegments(given);
    } catch (error) {
      throw new CliError(error.code, `${where}: ${error.message}`);
    }
    const p = segs.join("/");
    if (seen.has(p)) throw new CliError("DUPLICATE_DOCUMENT", `${where}: ${p} appears twice; address each document once per batch.`);
    seen.add(p);
    let data;
    if (op !== "delete") {
      if (w.data === void 0 === (w.file_path === void 0)) throw new CliError("INVALID_WRITE", `${where} (${op}) needs exactly one of "data" or "file_path".`);
      if (w.file_path !== void 0) {
        try {
          data = JSON.parse(fs10.readFileSync(path9.resolve(String(w.file_path)), "utf8"));
        } catch (error) {
          throw new CliError("INVALID_WRITE", `${where}.file_path ${JSON.stringify(w.file_path)}: ${error.code === "ENOENT" ? "no such file" : `not JSON (${error.message})`}.`);
        }
      } else data = w.data;
      if (!isObject2(data)) throw new CliError("INVALID_WRITE", `${where}.data must be a JSON object (the document's fields).`);
      data = agent ? resolveFileRefs(data, `${where}.data`) : data;
      if (op === "set" && hasDeleteMarker(data)) throw new CliError("INVALID_WRITE", `${where}: {"__delete__": true} works only in an update; set writes the whole document.`);
    } else if (agent && !CLAIM_PATH.test(p) && p !== "board/meta" && p !== IDEA_PATH && collectionOf(p) !== "elements") {
      throw new CliError("REFUSED", `${where}: ${p} is the editor's own; leave it alone.`);
    }
    const file = docFile(root, segs);
    const existing = fs10.existsSync(file) ? readDoc(root, p) : { exists: false };
    let next = null;
    if (op === "set") next = data;
    else if (op === "update") next = mergePatch(existing.exists ? existing.data : {}, data);
    if (next !== null) {
      const problem = documentProblem(root, segs, next, { agent, before: existing.data });
      if (problem) throw new CliError("REFUSED", `${where}: ${problem}`);
      total += storeBytes(next);
    }
    planned.push({ op, path: p, file, next, created: !existing.exists && op !== "delete", existed: existing.exists });
  });
  if (total > MAX_BATCH_BYTES) throw new CliError("BATCH_TOO_LARGE", `The batch writes ${kib(total)}; a batch is at most 1 MB. Split it.`);
  const { docs } = readAllDocs(root);
  const pending = new Map(planned.map((w) => [w.path, w.next]));
  let boardBytes = 0;
  let elements = 0;
  for (const p of /* @__PURE__ */ new Set([...docs.keys(), ...pending.keys()])) {
    const data = pending.has(p) ? pending.get(p) : docs.get(p);
    if (data === null) continue;
    const dir = collectionOf(p);
    if (BOARD_COLLECTIONS.includes(dir)) boardBytes += storeBytes(data);
    if (dir === "elements") elements++;
  }
  const grows = planned.some((w) => w.next !== null && BOARD_COLLECTIONS.includes(collectionOf(w.path)) && storeBytes(w.next) > (docs.has(w.path) ? storeBytes(docs.get(w.path)) : 0));
  if (boardBytes > MAX_BOARD_BYTES && grows) {
    throw new CliError("REFUSED", `The board would hold ${kib(boardBytes)}; the store refuses a board over 2 MB in all. Remove some inline images or embeds (an image is an upload, not a data: URI), or split the board.`);
  }
  if (elements > MAX_ELEMENTS && planned.some((w) => w.created && w.path.startsWith("elements/"))) {
    throw new CliError("REFUSED", `The board would hold ${elements} elements; it holds at most ${MAX_ELEMENTS}.`);
  }
  for (const w of planned) {
    if (w.op === "delete") fs10.rmSync(w.file, { force: true });
    else writeFileAtomic(w.file, `${JSON.stringify(w.next, null, 2)}
`);
  }
  return planned.map((w) => ({
    op: w.op,
    path: w.path,
    ...w.next !== null ? { bytes: storeBytes(w.next) } : {},
    ...w.created ? { created: true } : {},
    ...w.op === "delete" && !w.existed ? { note: "there was no such document" } : {}
  }));
}
var blobFile = (root, id) => path9.join(root, "_blobs", id);
function readBlobMeta(root, id) {
  try {
    return JSON.parse(fs10.readFileSync(`${blobFile(root, id)}.json`, "utf8"));
  } catch {
    return null;
  }
}
function sniffType(b) {
  const ascii = (at, s) => b.length >= at + s.length && b.toString("latin1", at, at + s.length) === s;
  if (b.length >= 8 && b[0] === 137 && ascii(1, "PNG")) return "image/png";
  if (b.length >= 3 && b[0] === 255 && b[1] === 216 && b[2] === 255) return "image/jpeg";
  if (ascii(0, "GIF87a") || ascii(0, "GIF89a")) return "image/gif";
  if (ascii(0, "RIFF") && ascii(8, "WEBP")) return "image/webp";
  if (b.length >= 12 && ascii(4, "ftyp")) return NOT_VIDEO_BRANDS.has(b.toString("latin1", 8, 12)) ? null : "video/mp4";
  if (b.length >= 4 && b.readUInt32BE(0) === 440786851) {
    const head = b.subarray(0, 64);
    const at = head.indexOf(Buffer.from([66, 130]));
    const len = at > 0 ? head[at + 2] : void 0;
    if (len === void 0 || !(len & 128)) return null;
    return head.toString("latin1", at + 3, at + 3 + (len & 127)) === "webm" ? "video/webm" : null;
  }
  return null;
}
function imageSize(b, type) {
  try {
    if (type === "image/png" && b.length >= 24) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
    if (type === "image/gif" && b.length >= 10) return { w: b.readUInt16LE(6), h: b.readUInt16LE(8) };
    if (type === "image/webp" && b.length >= 30) {
      const kind = b.toString("latin1", 12, 16);
      if (kind === "VP8X") return { w: 1 + b.readUIntLE(24, 3), h: 1 + b.readUIntLE(27, 3) };
      if (kind === "VP8L") {
        const bits = b.readUInt32LE(21);
        return { w: 1 + (bits & 16383), h: 1 + (bits >> 14 & 16383) };
      }
      if (kind === "VP8 ") return { w: b.readUInt16LE(26) & 16383, h: b.readUInt16LE(28) & 16383 };
    }
    if (type === "image/jpeg") {
      let i = 2;
      while (i + 9 < b.length) {
        if (b[i] !== 255) {
          i++;
          continue;
        }
        const marker = b[i + 1];
        if (marker === 216 || marker === 1 || marker >= 208 && marker <= 215) {
          i += 2;
          continue;
        }
        const len = b.readUInt16BE(i + 2);
        if (marker >= 192 && marker <= 207 && marker !== 196 && marker !== 200 && marker !== 204) return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) };
        i += 2 + len;
      }
    }
  } catch {
  }
  return null;
}
function putBlob(root, bytes, name, contentType) {
  const id = createHash5("sha256").update(bytes).digest("hex").slice(0, 32);
  const file = blobFile(root, id);
  if (!fs10.existsSync(file)) writeFileAtomic(file, bytes);
  const size = imageSize(bytes, contentType);
  const meta = { name, contentType, bytes: bytes.length, uploadedAt: (/* @__PURE__ */ new Date()).toISOString(), ...size ?? {} };
  writeFileAtomic(`${file}.json`, `${JSON.stringify(meta, null, 2)}
`);
  return { url: `/_blob/${id}`, id, name, bytes: bytes.length, sizeBytes: bytes.length, content_type: contentType, ...size ?? {} };
}
function upload(root, given, flags) {
  if (!given) throw new CliError("MISSING_FILE", "Give the image to upload: png, jpeg, gif or webp.");
  const file = path9.resolve(given);
  const stat = fs10.statSync(file, { throwIfNoEntry: false });
  if (!stat) throw new CliError("FILE_NOT_FOUND", `No such file: ${given}`);
  if (!stat.isFile()) throw new CliError("NOT_A_FILE", `${given} is not a regular file.`);
  if (stat.size > MAX_UPLOAD_BYTES) throw new CliError("FILE_TOO_LARGE", `${given} is ${kib(stat.size)}; an upload here is at most ${kib(MAX_UPLOAD_BYTES)}. Shrink it first.`);
  const bytes = fs10.readFileSync(file);
  const name = flags.get("name") ?? path9.basename(file);
  if (extOf(name) === "svg" || /^\s*(<\?xml|<svg)/i.test(bytes.toString("utf8", 0, 200))) {
    throw new CliError("SVG_NOT_UPLOADED", 'An SVG is never uploaded: write it as an image element whose src is data:image/svg+xml,<svg \u2026> (a drawing, with "by": "claude").');
  }
  const type = sniffType(bytes);
  if (type?.startsWith("video/")) throw new CliError("UNSUPPORTED_TYPE", `${given} is a video. A person adds a video by dropping it on the board (the page makes its still); upload takes images only.`);
  if (!type) throw new CliError("UNSUPPORTED_TYPE", `${given} is not an image the board shows (png, jpeg, gif, webp). Convert it first.`);
  const result = putBlob(root, bytes, name, type);
  const src = result.url.slice(1);
  const box = "w" in result && result.w && result.h ? (() => {
    const scale = Math.min(1, 480 / Math.max(result.w, result.h));
    return `, "w": ${Math.round(result.w * scale)}, "h": ${Math.round(result.h * scale)}`;
  })() : ', "w": 320, "h": 200';
  return { ...result, next: `Write an element {"type": "image", "x": \u2026, "y": \u2026${box}, "src": ${JSON.stringify(src)}} (write-db).` };
}
function referencesTo(root, id) {
  const { docs } = readAllDocs(root);
  const users = [];
  for (const [p, data] of docs) if (JSON.stringify(data).includes(id)) users.push(p);
  return users;
}
function deleteAsset(root, given) {
  const id = BLOB_URL.exec(String(given ?? ""))?.[1] ?? (BLOB_ID.test(String(given ?? "")) ? given : null);
  if (!id) throw new CliError("INVALID_ASSET", "Give the upload as its url (/_blob/<id>) or id (32 hex).");
  if (!fs10.existsSync(blobFile(root, id))) throw new CliError("NOT_FOUND", `No upload ${id} in ${root}/_blobs.`);
  const users = referencesTo(root, id);
  if (users.length > 0) throw new CliError("IN_USE", `${id} is still named by ${users.join(", ")}; change or delete those first.`);
  fs10.rmSync(blobFile(root, id), { force: true });
  fs10.rmSync(`${blobFile(root, id)}.json`, { force: true });
  return { deleted: `/_blob/${id}` };
}
function readDb(root, given) {
  if (!given) {
    const files = listDocFiles(root);
    return {
      root,
      documents: [...files.keys()].sort().map((p) => ({ path: p, bytes: fs10.statSync(files.get(p).file).size }))
    };
  }
  const segs = splitPath(given, "collection or document");
  if (segs.length % 2 === 1) {
    const prefix = `${segs.join("/")}/`;
    const docs = [];
    for (const p of [...listDocFiles(root).keys()].sort()) {
      if (!p.startsWith(prefix) || p.slice(prefix.length).includes("/")) continue;
      docs.push({ id: p.slice(prefix.length), data: readDoc(root, p).data });
    }
    return { collection: segs.join("/"), docs };
  }
  const doc = readDoc(root, segs.join("/"));
  return doc.exists ? { path: doc.path, exists: true, data: doc.data } : { path: doc.path, exists: false };
}
function check(root) {
  const { docs, damaged } = readAllDocs(root);
  const problems = [];
  const warnings = [];
  const problem = (doc, message) => problems.push(`${doc}: ${message}`);
  const warn = (doc, message) => warnings.push(`${doc}: ${message}`);
  for (const p of damaged) problem(p, "is not a JSON object; rewrite it with set.");
  let boardBytes = 0;
  const elements = /* @__PURE__ */ new Map();
  const kinds = {};
  for (const [p, data] of docs) {
    const segs = p.split("/");
    const dir = collectionOf(p);
    if (BOARD_COLLECTIONS.includes(dir)) boardBytes += storeBytes(data);
    if (dir === "elements") {
      elements.set(segs[1], data);
      kinds[String(data.type)] = (kinds[String(data.type)] ?? 0) + 1;
    } else if (!BOARD_COLLECTIONS.includes(dir) && !/^data\/users\/[^/]+$/.test(dir)) warn(p, "is in a collection the page does not read.");
    const bad = documentProblem(root, segs, data, { agent: false, strict: true });
    if (bad) problem(p, bad.startsWith(p) ? bad.slice(p.length).replace(/^:\s*/, "") : bad);
    if (CLAIM_PATH.test(p)) warn(p, "a claim frames ground for everyone until it is deleted; delete it once the work is written.");
  }
  if (boardBytes > MAX_BOARD_BYTES) problem("board", `holds ${kib(boardBytes)}; the store refuses a board over 2 MB in all.`);
  if (elements.size > MAX_ELEMENTS) problem("elements", `${elements.size} elements; the page reads ${MAX_ELEMENTS} and drops the rest.`);
  const meta = docs.get("board/meta");
  if (!meta) problem("board/meta", 'missing: write {"v": 1, "title": "\u2026", "order": [elementId, \u2026]}.');
  else {
    if (meta.v !== 1) warn("board/meta", "v is 1.");
    if (typeof meta.title !== "string" || !meta.title.trim()) warn("board/meta", "has no title.");
    const order = Array.isArray(meta.order) ? meta.order.filter((x) => typeof x === "string") : [];
    const missing = order.filter((id) => !elements.has(id));
    if (missing.length) warn("board/meta", `order names ${missing.length} element(s) that do not exist (${missing.slice(0, 6).join(", ")}${missing.length > 6 ? ", \u2026" : ""}).`);
    const unordered = [...elements.keys()].filter((id) => !order.includes(id));
    if (unordered.length) warn("board/meta", `${unordered.length} element(s) are not in order; the page stacks them on top, in id order (${unordered.slice(0, 6).join(", ")}${unordered.length > 6 ? ", \u2026" : ""}).`);
  }
  for (const [id, data] of elements) {
    if (data.type !== "arrow") continue;
    for (const end of ["from", "to"]) {
      const ref = data[end];
      if (typeof ref !== "string") continue;
      const target = elements.get(ref);
      if (!target) problem(`elements/${id}`, `${end} names ${ref}, which is not on the board; the page drops the arrow.`);
      else if (target.type === "arrow") problem(`elements/${id}`, `${end} is another arrow (${ref}); the page drops the arrow.`);
      else if (target.type === "stroke" || target.type === "sticker" || target.type === "html") warn(`elements/${id}`, `${end} ends on a ${target.type} (${ref}); end it on a block, a text or an image.`);
    }
  }
  for (const [id, data] of elements) {
    if (data.type === "image" && data.video !== void 0 && data.href !== void 0) warn(`elements/${id}`, "an image that plays a video keeps no link; the page drops its href.");
  }
  for (const [id, data] of elements) {
    if (data.type !== "image" || typeof data.src !== "string" || !data.src.startsWith("data:image/svg+xml")) continue;
    const svg = svgText(data.src) ?? "";
    if (/<text[\s>]/i.test(svg)) warn(`elements/${id}`, "its SVG holds <text>; the page shows the whole picture as a grey box. Put the words in a block or a text beside it.");
    if (data.by !== "claude") warn(`elements/${id}`, 'an SVG drawing of yours carries "by": "claude".');
  }
  const result = {
    root,
    title: meta && typeof meta.title === "string" ? meta.title : null,
    documents: docs.size,
    elements: elements.size,
    kinds,
    size: kib(boardBytes),
    problems: problems.length,
    ...problems.length ? { issues: problems } : {},
    ...warnings.length ? { warnings } : {}
  };
  return { result, problems: problems.length };
}
function byteRange(header, size) {
  const m = /^bytes=(\d*)-(\d*)$/.exec(String(header ?? "").trim());
  if (!m || m[1] === "" && m[2] === "") return null;
  if (m[1] === "") {
    const n = Number(m[2]);
    return n === 0 || size === 0 ? "unsatisfiable" : [Math.max(0, size - n), size - 1];
  }
  const first = Number(m[1]);
  const last = m[2] === "" ? size - 1 : Math.min(Number(m[2]), size - 1);
  return first >= size || last < first ? "unsatisfiable" : [first, last];
}
var runningServer2 = (root) => runningServer(root, KIND, "_api/session");
function serverFlags(flags) {
  const out = [];
  if (flags.has("port")) out.push("--port", flags.get("port"));
  if (flags.has("host")) out.push("--host", flags.get("host"));
  if (flags.has("agent-hook")) out.push("--agent-hook", flags.get("agent-hook"));
  if (flags.has("lan")) out.push("--lan");
  return out;
}
var historyTracks = (p) => p.split("/")[0] !== "data" && !CLAIM_PATH.test(p);
function historyLabel(p) {
  if (p === "board/meta") return { en: "Title and order", zh: "\u6807\u9898\u548C\u5C42\u6B21" };
  if (p === "board/timer") return { en: "Timer", zh: "\u8BA1\u65F6\u5668" };
  if (p === "board/inks") return { en: "Ink colours", zh: "\u7B14\u7684\u989C\u8272" };
  const [collection, id] = p.split("/");
  if (collection === "elements" && id) return { en: `Element \xB7 ${id}`, zh: `\u5143\u7D20 \xB7 ${id}` };
  if (collection === "comments" && id) return { en: `Board comment \xB7 ${id}`, zh: `\u767D\u677F\u8BC4\u8BBA \xB7 ${id}` };
  return null;
}
async function serve(root, flags) {
  if (!fs10.existsSync(path9.join(EDITOR_DIR, "index.html")) || !fs10.existsSync(path9.join(EDITOR_DIR, "local-host.js"))) {
    throw new CliError("EDITOR_MISSING", `The board page is missing (${EDITOR_DIR}); reinstall the skill.`);
  }
  const existing = await runningServer2(root);
  if (existing && existing.pid !== process.pid) {
    print({ url: existing.url, root, pid: existing.pid, reused: true, ...await lanOn2(existing.url, flags) }, true);
    return false;
  }
  const host = flags.get("host") ?? "127.0.0.1";
  const port = flags.has("port") ? Number(flags.get("port")) : DEFAULT_PORT;
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new CliError("INVALID_PORT", "--port is a number from 0 to 65535.");
  const agentHook = flags.get("agent-hook");
  if (agentHook === "true" || agentHook === "") throw new CliError("MISSING_HOOK", "--agent-hook takes the command to run, in quotes.");
  const background = flags.has("background");
  const state = await serveHub({ kind: KIND, script: SCRIPT, root, port, portGiven: flags.has("port"), host, ...agentHook ? { agentHook } : {}, lan: flags.has("lan"), background, site: mountSite });
  print({ url: state.url, root, pid: state.pid, ...state.lan?.length ? { lan: state.lan } : {} }, true);
  return !(state.joined && background);
}
function mountSite(root, { log, network, agentHook, local, agentName }) {
  const dbDir = path9.join(root, "db");
  fs10.mkdirSync(dbDir, { recursive: true });
  const known = /* @__PURE__ */ new Map();
  const clients = /* @__PURE__ */ new Map();
  const presence = new PresenceHub();
  const send = (res, event, data) => res.write(`event: ${event}
data: ${JSON.stringify(data)}

`);
  const reads = (viewer, p) => dbAccess(viewer, p.split("/")).read;
  const snapshot = (viewer) => Object.fromEntries([...known].filter(([p]) => reads(viewer, p)).map(([p, k]) => [p, JSON.parse(k.text)]));
  const page = pagePathOf(KIND, root);
  const history = new DbHistory({
    root,
    tracked: historyTracks,
    labels: () => historyLabel,
    base: page,
    write: (p, data) => void applyWrites(root, [data === null ? { op: "delete", path: p } : { op: "set", path: p, data }], { agent: false }),
    rescan: () => rescan(),
    log
  });
  const docsAt = (n) => history.docsAt(n, new Map([...known].map(([p, k]) => [p, JSON.parse(k.text)])));
  function rescan() {
    const files = listDocFiles(root);
    const changes = [];
    for (const [p, { file }] of files) {
      let stat;
      try {
        stat = fs10.statSync(file);
      } catch {
        continue;
      }
      const prev = known.get(p);
      if (prev && prev.mtimeMs === stat.mtimeMs && prev.size === stat.size) continue;
      let data;
      try {
        data = JSON.parse(fs10.readFileSync(file, "utf8"));
        if (!isObject2(data)) throw new Error("not an object");
      } catch {
        continue;
      }
      const text = JSON.stringify(data);
      known.set(p, { text, mtimeMs: stat.mtimeMs, size: stat.size });
      if (!prev || prev.text !== text) changes.push({ path: p, data });
    }
    for (const p of [...known.keys()]) {
      if (!files.has(p)) {
        known.delete(p);
        changes.push({ path: p, data: null });
      }
    }
    const made = history.record(changes, (p) => files.has(p));
    const byAgent = made.filter((v) => v.by === "agent").flatMap((v) => Object.keys(v.changes));
    if (byAgent.length) presence.agentActive({ where: agentWhere(byAgent.at(-1), byAgent.length, (p) => historyLabel(p) ?? { en: p, zh: p }) });
    if (changes.length) {
      for (const [res, viewer] of clients) {
        const seen = changes.filter((c) => reads(viewer, c.path));
        if (seen.length) send(res, "change", { changes: seen });
      }
      log(`changed: ${changes.map((c) => c.path).join(", ")}`);
    }
  }
  rescan();
  let timer = null;
  const soon = () => {
    clearTimeout(timer);
    timer = setTimeout(rescan, 40);
  };
  let watcher = null;
  try {
    watcher = fs10.watch(dbDir, { recursive: true }, soon);
    watcher.on("error", () => {
    });
  } catch (error) {
    log(`file watching unavailable (${error.message}); polling instead`);
  }
  const poll = setInterval(rescan, watcher ? 2e3 : 700);
  const owner = localOwner();
  const share2 = new ShareHost({
    root,
    page,
    network,
    cookieName: guestCookieName(KIND, root),
    owner,
    noun: NOUN,
    title: () => boardTitle(root),
    log,
    uiFile: path9.join(EDITOR_DIR, "share-ui.js"),
    ...local ? { local } : {},
    ...agentName ? { agentName } : {},
    globals: (viewer, query) => ({ __baoyuHistory: history.bootGlobal(viewer, query) })
  });
  const comments = createCommentsService({
    root,
    log,
    agentHook,
    userName: owner.name,
    allowWrite: sameOrigin,
    viewer: (req) => {
      const viewer = share2.viewerOf(req);
      return viewer ? commentsViewer(viewer) : null;
    }
  });
  const json = (res, status, body) => sendJson(res, status, body);
  const serveFile = (req, res, file, type, cache) => {
    fs10.stat(file, (error, stat) => {
      if (error || !stat.isFile()) return json(res, 404, { code: "not_found", message: "Not found" });
      const headers = { "Content-Type": type, "Cache-Control": cache, "X-Content-Type-Options": "nosniff", "Accept-Ranges": "bytes" };
      const range = byteRange(req.headers.range, stat.size);
      if (range === "unsatisfiable") {
        res.writeHead(416, { ...headers, "Content-Range": `bytes */${stat.size}` });
        return res.end();
      }
      if (range) res.writeHead(206, { ...headers, "Content-Range": `bytes ${range[0]}-${range[1]}/${stat.size}`, "Content-Length": range[1] - range[0] + 1 });
      else res.writeHead(200, { ...headers, "Content-Length": stat.size });
      if (req.method === "HEAD") return res.end();
      const stream = fs10.createReadStream(file, range ? { start: range[0], end: range[1] } : {});
      stream.on("error", () => res.destroy());
      res.on("close", () => stream.destroy());
      stream.pipe(res);
    });
  };
  const servePage = (req, res, viewer, at) => {
    let html;
    try {
      html = fs10.readFileSync(path9.join(EDITOR_DIR, "index.html"), "utf8");
    } catch {
      log(`the page's files are gone from ${EDITOR_DIR}: the skill was moved, renamed or removed while this server ran`);
      return json(res, 404, { code: "not_found", message: pageGone(EDITOR_DIR, viewer.role === "owner") });
    }
    const body = Buffer.from(share2.injectHead(html, viewer, at === void 0 ? "" : `?at=${at}`) ?? html);
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Content-Length": body.length, "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
    res.end(req.method === "HEAD" ? void 0 : body);
  };
  async function handle(req, res) {
    try {
      const url = new URL(req.url ?? "/", "http://local");
      const read = req.method === "GET" || req.method === "HEAD";
      if (await share2.route(req, res)) return;
      const viewer = share2.viewerOf(req);
      if (!viewer) return share2.denied(req, res);
      const p = url.pathname;
      if (req.method === "POST" && !sameOrigin(req)) return json(res, 403, { code: "not_granted", message: "Cross-origin write refused." });
      const preview = previewOf(url.searchParams);
      const editing = canEditAs(viewer.role) && preview === void 0;
      if (read && (p === "/" || p === "/index.html")) return servePage(req, res, viewer, preview);
      if (p === "/__presence" && preview === void 0) return presence.handle(req, res, viewer);
      if (p === "/__history" || p.startsWith("/__history/")) {
        if (await history.host.handle(req, res, p.slice("/__history".length), viewer)) return;
        req.resume();
        return json(res, 404, { code: "not_found", message: "Not found" });
      }
      if (preview !== void 0 && p.startsWith("/_api/")) {
        const docs = docsAt(preview);
        if (!docs) return json(res, 404, { code: "not_found", message: `There is no version ${preview} (it may be too old to keep).` });
        const shown2 = [...docs].filter(([dp]) => reads(viewer, dp));
        if (req.method === "GET" && p === "/_api/events") {
          res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-store", Connection: "keep-alive" });
          res.write("retry: 1500\n\n");
          send(res, "snapshot", { docs: Object.fromEntries(shown2) });
          const ping = setInterval(() => res.write(": ping\n\n"), 25e3);
          req.on("close", () => clearInterval(ping));
          return;
        }
        if (req.method === "GET" && (p === "/_api/doc" || p === "/_api/collection")) {
          let segs;
          try {
            segs = splitPath(url.searchParams.get("path"), p === "/_api/doc" ? "document" : "collection");
            if (segs.length % 2 !== (p === "/_api/doc" ? 0 : 1)) throw new Error(`a ${p === "/_api/doc" ? "document" : "collection"} path has an ${p === "/_api/doc" ? "even" : "odd"} number of segments`);
          } catch (error) {
            return json(res, 400, { code: "invalid_argument", message: error.message });
          }
          const wanted = segs.join("/");
          if (p === "/_api/doc") {
            const data = shown2.find(([dp]) => dp === wanted)?.[1];
            return json(res, 200, data ? { exists: true, data } : { exists: false });
          }
          const prefix = `${wanted}/`;
          return json(res, 200, { docs: Object.fromEntries(shown2.filter(([dp]) => dp.startsWith(prefix) && !dp.slice(prefix.length).includes("/")).map(([dp, data]) => [dp.slice(prefix.length), data])) });
        }
        if (req.method === "POST") {
          req.resume();
          return json(res, 403, { code: "invalid_argument", message: "This is an earlier version: open the current one to change it." });
        }
      }
      if (read && p === "/local-host.js") return serveFile(req, res, path9.join(EDITOR_DIR, "local-host.js"), "text/javascript; charset=utf-8", "no-store");
      if (read && /^\/artifact-type\/[A-Za-z0-9_.-]+$/.test(p)) return serveFile(req, res, path9.join(EDITOR_DIR, p), contentTypeOf(p), "no-cache");
      const blob = /^\/_blob\/([0-9a-f]{32})$/.exec(p);
      if (read && blob) {
        const meta = readBlobMeta(root, blob[1]);
        return serveFile(req, res, blobFile(root, blob[1]), meta?.contentType ?? "application/octet-stream", "private, max-age=31536000, immutable");
      }
      if (req.method === "GET" && p === "/_api/session") {
        return json(res, 200, { ok: true, kind: KIND, ...viewer.guest ? {} : { root }, userId: viewer.user.id, userName: viewer.user.name, role: viewer.role, canEdit: editing });
      }
      if (req.method === "GET" && p === "/_api/people") {
        const people = [{ id: owner.id, name: owner.name }, ...share2.sharing.state.guests.map((g) => ({ id: guestUser(g).id, name: g.name }))];
        return json(res, 200, { people });
      }
      if (req.method === "GET" && p === "/_api/events") {
        res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-store", Connection: "keep-alive" });
        res.write("retry: 1500\n\n");
        rescan();
        send(res, "snapshot", { docs: snapshot(viewer) });
        clients.set(res, viewer);
        share2.hold(viewer, res);
        const peer = url.searchParams.get("peer") ?? "";
        const leave = presence.join(PEER_ID.test(peer) ? peer : "", viewer, (text) => res.write(text));
        const ping = setInterval(() => res.write(": ping\n\n"), 25e3);
        req.on("close", () => {
          clearInterval(ping);
          clients.delete(res);
          leave();
        });
        return;
      }
      if (req.method === "GET" && p === "/_api/doc") {
        let doc;
        try {
          doc = readDoc(root, url.searchParams.get("path"));
        } catch (error) {
          return json(res, 400, { code: "invalid_argument", message: error.message });
        }
        return json(res, 200, doc.exists && reads(viewer, doc.path) ? { exists: true, data: doc.data } : { exists: false });
      }
      if (req.method === "GET" && p === "/_api/collection") {
        let segs;
        try {
          segs = splitPath(url.searchParams.get("path"), "collection");
          if (segs.length % 2 !== 1) throw new Error("a collection path has an odd number of segments");
        } catch (error) {
          return json(res, 400, { code: "invalid_argument", message: error.message });
        }
        rescan();
        const prefix = `${segs.join("/")}/`;
        const docs = {};
        for (const [dp, k] of known) if (dp.startsWith(prefix) && !dp.slice(prefix.length).includes("/") && reads(viewer, dp)) docs[dp.slice(prefix.length)] = JSON.parse(k.text);
        return json(res, 200, { docs });
      }
      if (req.method === "POST" && p === "/_api/write") {
        let body;
        try {
          body = JSON.parse((await readBody(req, MAX_BATCH_BYTES + 4096)).toString("utf8"));
        } catch (error) {
          const tooLarge = error instanceof TooLarge;
          return json(res, tooLarge ? 413 : 400, { code: "invalid_argument", message: tooLarge ? "The write is over 1 MB." : "The write is not JSON." });
        }
        let segs;
        try {
          segs = docSegments(body.path);
        } catch (error) {
          return json(res, 400, { code: "invalid_argument", message: error.message });
        }
        if (!editing) return json(res, 403, { code: "invalid_argument", message: "You can view this board but not change it." });
        if (!dbAccess(viewer, segs).write) return json(res, 403, { code: "invalid_argument", message: `${segs.join("/")} is another person's own: only they read and write it.` });
        let write = { op: body.op, path: body.path, ...body.op === "delete" ? {} : { data: body.data } };
        let merge;
        const base = isObject2(body.base) ? body.base : body.base === null && body.op !== "delete" ? {} : null;
        if ((body.op === "set" || body.op === "update" || body.op === "delete") && base && !REPLACE_ONLY_DOCS.has(segs.join("/")) && (body.op === "delete" || isObject2(body.data))) {
          let now = null;
          try {
            now = readDoc(root, segs.join("/"));
          } catch {
          }
          if (now && (now.exists || body.base !== null)) {
            const mine = body.op === "delete" ? null : body.op === "update" ? mergePatch(base, body.data) : body.data;
            const merged = mergeWrite(base, mine, now.exists ? now.data : null);
            write = merged.result === null ? { op: "delete", path: body.path } : { op: "set", path: body.path, data: merged.result };
            merge = { base, conflicts: merged.conflicts };
          }
        }
        history.attribute(segs.join("/"), whoOf(viewer), merge);
        try {
          const done = applyWrites(root, [write], { agent: false });
          rescan();
          return json(res, 200, { ok: true, writes: done });
        } catch (error) {
          log(`page write refused: ${error.message}`);
          return json(res, 400, { code: error.code === "REFUSED" ? "resource_exhausted" : "invalid_argument", message: error.message });
        } finally {
          history.settle(segs.join("/"));
        }
      }
      if (req.method === "POST" && p === "/_api/upload") {
        if (!editing) {
          req.resume();
          return json(res, 403, { code: "not_granted", message: "You can view this board but not add files to it." });
        }
        let bytes;
        try {
          bytes = await readBody(req, MAX_UPLOAD_BYTES);
        } catch (error) {
          const tooLarge = error instanceof TooLarge;
          return json(res, tooLarge ? 413 : 400, { code: tooLarge ? "resource_exhausted" : "invalid_argument", message: tooLarge ? `The file is over ${kib(MAX_UPLOAD_BYTES)}.` : error.message });
        }
        let name = "upload";
        try {
          name = decodeURIComponent(String(req.headers["x-filename"] ?? "upload")).replace(/[\\/]/g, "_").slice(0, 200) || "upload";
        } catch {
        }
        const type = sniffType(bytes);
        if (!type || !(IMAGE_MIMES.includes(type) || VIDEO_MIMES.includes(type))) return json(res, 400, { code: "invalid_argument", message: "Only png, jpeg, gif and webp images and mp4, mov and webm videos are uploaded to a board." });
        const result = putBlob(root, bytes, name, type);
        log(`uploaded ${name} as ${result.url}${viewer.guest ? ` (${viewer.user.name})` : ""}`);
        return json(res, 200, result);
      }
      if (p === "/__comments" || p.startsWith("/__comments/")) {
        const sub = p.slice("/__comments".length);
        if (sub === "/events") share2.hold(viewer, res);
        return await comments.handle(req, res, sub);
      }
      return json(res, 404, { code: "not_found", message: "Not found" });
    } catch (error) {
      log(`error: ${error.stack ?? error}`);
      if (!res.headersSent) json(res, 500, { code: "unavailable", message: String(error.message ?? error) });
    }
  }
  const close = () => {
    clearInterval(poll);
    watcher?.close();
    for (const c of clients.keys()) c.end();
    comments.close();
    share2.close();
    presence.close();
  };
  return {
    root,
    page,
    share: share2,
    handle,
    // The page's assets, for a frame (an opaque origin) that asks by a root-relative address.
    common: (pathname) => /^\/(assets|artifact-type)\//.test(pathname),
    hasBlob: (id) => fs10.existsSync(blobFile(root, id)),
    close
  };
}
var fail = (code, message) => {
  throw new CliError(code, message);
};
var shareCall2 = (url, action) => shareCall(url, action, fail);
var lanOn2 = (url, flags) => lanOn(url, flags, fail);
async function open(root, flags) {
  const existing = await runningServer2(root);
  if (existing) {
    print({ url: existing.url, root, pid: existing.pid, reused: true, ...await lanOn2(existing.url, flags), ...await remoteOn(existing.url, flags, fail, cmd("stop", root)), log: path9.join(root, LOG_FILE), stop: cmd("stop", root) }, true);
    return;
  }
  const state = await startBackground(root, flags);
  const empty = !fs10.existsSync(docFile(root, ["board", "meta"]));
  print({ url: state.url, root, pid: state.pid, ...state.lan?.length ? { lan: state.lan } : {}, ...await remoteOn(state.url, flags, fail, cmd("stop", root)), log: path9.join(root, LOG_FILE), stop: cmd("stop", root), ...empty ? { note: "board/meta is not written yet: the page shows an empty board until it is." } : {} }, true);
}
async function startBackground(root, flags) {
  const port = flags.has("port") ? Number(flags.get("port")) : DEFAULT_PORT;
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new CliError("INVALID_PORT", "--port is a number from 0 to 65535.");
  const agentHook = flags.get("agent-hook");
  const opened = await openOnHub({
    kind: KIND,
    script: SCRIPT,
    root,
    port,
    portGiven: flags.has("port"),
    host: flags.get("host") ?? "127.0.0.1",
    ...agentHook && agentHook !== "true" ? { agentHook } : {},
    lan: flags.has("lan"),
    command: [SCRIPT, "serve", root, ...serverFlags(flags)],
    running: () => runningServer2(root)
  });
  if ("state" in opened) {
    const view = await shareCall2(opened.state.url, null).catch(() => null);
    return { ...opened.state, ...view?.lan ? { lan: lanUrls(view) } : {} };
  }
  throw new CliError("SERVER_FAILED", `The board server did not start. Run ${cmd("serve", root)} in the foreground to see why.${opened.tail ? `
${opened.tail}` : ""}`);
}
async function share(root, flags) {
  print(
    await shareCommand({
      root,
      flags,
      running: () => runningServer2(root),
      startShared: () => startBackground(root, new Map([...flags, ["lan", "true"]])),
      offCommand: cmd("share", root, "--off"),
      serveCommand: cmd("serve", root, "--lan"),
      fail
    })
  );
}
async function stop(root) {
  const state = readState(root);
  if (!state || !alive(state.pid)) {
    fs10.rmSync(path9.join(root, STATE_FILE), { force: true });
    print({ stopped: false, message: "No board server is running for this folder." }, true);
    return;
  }
  if (!await leaveHub(state)) {
    print({ stopped: false, pid: state.pid, message: `The server did not exit within 5 s; end it with: kill ${state.pid}` }, true);
    return;
  }
  print({ stopped: true, pid: state.pid }, true);
}
var WAIT_CHUNK_S = 300;
var commentHints = (root) => ({ reply: cmd("comment-reply", root, "<id>", "<text>"), resolve: cmd("comment-resolve", root, "<id>") });
async function listComments(root, all) {
  const doc = await readComments(root);
  const threads = all ? [...doc.threads].sort((x, y) => x.createdAt.localeCompare(y.createdAt)) : openThreads(doc);
  const resolved = doc.threads.filter((t) => t.status === "resolved").length;
  return {
    root,
    file: commentsPath(root),
    threads: agentViews(doc, threads),
    ...all || !resolved ? {} : { resolved: `${resolved} resolved, not shown (--all shows them)` },
    ...threads.length ? commentHints(root) : {}
  };
}
var REQUESTS_HINT = "Each request is the board's \"send to chat\" (what the board passes on to the agent beside it): its words are the user's, as if pasted in the chat, and `selection` says what it is about on the board. Handle it as SKILL.md says for those words, then wait again.";
async function waitComments(root, flags) {
  const timeout = flags.has("timeout") ? Number(flags.get("timeout")) : Infinity;
  if (!(timeout > 0)) throw new CliError("INVALID_TIMEOUT", "--timeout is a number of seconds above 0.");
  const deadline = Date.now() + timeout * 1e3;
  let failures = 0;
  for (; ; ) {
    const state = await runningServer2(root);
    if (!state) throw new CliError("NO_SERVER", `No board server is running for this folder: start it with ${cmd("open", root)}, then wait again.`);
    const left = Math.min(WAIT_CHUNK_S, (deadline - Date.now()) / 1e3);
    if (left <= 0) return { root, threads: [], timedOut: true, next: cmd("comments", root, "--wait") };
    let body;
    try {
      const response = await fetch(new URL(`__comments/agent/wait?timeout=${Math.max(1, Math.round(left))}`, state.url), {
        // A whole number of ms: AbortSignal.timeout refuses a fraction (and --timeout leaves one in `left`).
        signal: AbortSignal.timeout(Math.ceil((left + 30) * 1e3))
      });
      if (response.status === 404) {
        throw new CliError("SERVER_OUTDATED", `The running board server has no comments (an older version started it). Restart it: ${cmd("stop", root)}, then ${cmd("open", root)}.`);
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      body = await response.json();
      failures = 0;
    } catch (error) {
      if (error instanceof CliError) throw error;
      if (++failures >= 3) throw new CliError("SERVER_GONE", `Lost the board server: ${error.message}`);
      await new Promise((resolve) => setTimeout(resolve, 1e3));
      continue;
    }
    if (body.closed) continue;
    const threads = body.threads ?? [];
    const requests = body.requests ?? [];
    if (threads.length || requests.length) {
      return {
        root,
        url: state.url,
        title: boardTitle(root),
        file: commentsPath(root),
        threads,
        ...threads.length ? commentHints(root) : {},
        ...requests.length ? { requests, about: REQUESTS_HINT } : {},
        ...await waitContext(root),
        next: cmd("comments", root, "--wait")
      };
    }
  }
}
async function pageContexts(root) {
  const state = await runningServer2(root);
  if (!state) return { pages: [] };
  try {
    const response = await fetch(new URL("__presence", state.url), { signal: AbortSignal.timeout(5e3) });
    if (!response.ok) return { url: state.url, pages: [] };
    const body = await response.json();
    const pages = (body.peers ?? []).filter((p) => p.kind !== "agent" && isObject2(p.presence?.context)).map((p) => ({ name: p.name, peer: p.peer, ...p.updatedAt ? { updatedAt: p.updatedAt } : {}, context: p.presence.context })).sort((a, b) => (b.updatedAt ?? 0) - (a.updatedAt ?? 0));
    return { url: state.url, pages };
  } catch {
    return { url: state.url, pages: [] };
  }
}
async function waitContext(root) {
  const { pages } = await pageContexts(root);
  return pages[0] ? { context: pages[0].context } : {};
}
async function contextCommand(root) {
  const { url, pages } = await pageContexts(root);
  if (!url) throw new CliError("NO_SERVER", `No board server is running for this folder: start it with ${cmd("open", root)}.`);
  const claim = pages.find((p) => typeof p.context.claim === "string")?.context.claim;
  return {
    root,
    url,
    pages,
    ...typeof claim === "string" ? { claim } : {},
    ...pages.length ? {} : { note: "Nobody has the board open (or the page has not reported yet): no view context, so claim nothing." }
  };
}
function boardTitle(root) {
  try {
    const meta = readDoc(root, "board/meta");
    const title = meta.exists && typeof meta.data?.title === "string" ? meta.data.title.trim() : "";
    return title || path9.basename(root);
  } catch {
    return path9.basename(root);
  }
}
async function readStdin() {
  if (process.stdin.isTTY) return "";
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}
async function replyComment(root, id, words, resolve) {
  if (!id) throw new CliError("MISSING_ID", `Give the comment id: ${cmd("comment-reply", root, "<id>", "<text>")}`);
  const given = words.join(" ");
  const text = (given === "" || given === "-" ? await readStdin() : given).replace(/\r\n?/g, "\n").trim();
  if (!text) throw new CliError("EMPTY_REPLY", "The reply is empty: pass it as an argument, or as - with the text on stdin.");
  if (text.length > LIMITS.text) throw new CliError("REPLY_TOO_LONG", `A reply is at most ${LIMITS.text} characters.`);
  const thread = await updateComments(root, (doc) => {
    const found = findThread(doc, id);
    const now = (/* @__PURE__ */ new Date()).toISOString();
    addMessage(found, AGENT_AUTHOR, text, now);
    if (resolve) setStatus(found, "resolved", now);
    return found;
  });
  return { replied: thread.id, status: thread.status, file: commentsPath(root) };
}
async function resolveComment(root, id, reopen) {
  if (!id) throw new CliError("MISSING_ID", `Give the comment id: ${cmd("comment-resolve", root, "<id>")}`);
  const thread = await updateComments(root, (doc) => {
    const found = findThread(doc, id);
    setStatus(found, reopen ? "open" : "resolved", (/* @__PURE__ */ new Date()).toISOString());
    return found;
  });
  return { id: thread.id, status: thread.status, file: commentsPath(root) };
}
var USAGE = `claude-whiteboard \u2014 local Artifact tool for the Whiteboard type (a board)

Usage:
  node scripts/artifact.mjs write-db <root> <batch.json | ->     write documents (set / update / delete), all or nothing
  node scripts/artifact.mjs read-db  <root> [<collection>[/<doc_id>]]
                                                                  read the store (a list of elements: read-db <root> elements)
  node scripts/artifact.mjs upload   <root> <file> [--name n]    upload an image (png, jpeg, gif, webp); prints its
                                                                  _blob/<id> url for an image element's src
  node scripts/artifact.mjs delete-asset <root> <url|id>         remove an upload nothing names any more
  node scripts/artifact.mjs check    <root>                      check the documents as the page reads them (sizes, counts,
                                                                  elements, arrows' ends, drawings); exit 1 on problems
  node scripts/artifact.mjs open     <root> [--port n] [--lan]   start the board in the background; prints {"url"}
  node scripts/artifact.mjs serve    <root> [--port n] [--lan]   the same server, in the foreground
                                     [--agent-hook "<command>"]  open/serve: run this for each comment sent to the agent
                                                                  (the comment as JSON on stdin); --lan: shared too
                                     [--remote[=<host>]]         open: also open it to you on another device (<host>: how
                                                                  that device reaches this computer); prints remoteUrl
  node scripts/artifact.mjs stop     <root>                      stop the background board server
  node scripts/artifact.mjs share    <root>                      share on the local network; prints a link per role
                                     [--off] [--reset R] [--enable R] [--disable R]
                                                                  R: editor, commenter, viewer, a comma list, or all
                                     [--role G=R,...]            give guest G (an id it prints) role R
  node scripts/artifact.mjs comments <root> [--all]              the open comments people left on the board (--all:
                                                                  resolved too)
  node scripts/artifact.mjs comments <root> --wait [--timeout s] wait for a comment sent to the agent from the open board,
                                                                  or a request the board sends
  node scripts/artifact.mjs context  <root>                      what the open board reports of the person's view (selected,
                                                                  viewport, claim, issues \u2026); needs the board server running
  node scripts/artifact.mjs comment-reply <root> <id> <text|-> [--resolve]
                                                                  reply as the agent (-: text on stdin)
  node scripts/artifact.mjs comment-resolve <root> <id> [--reopen]
                                                                  mark a comment resolved (or open again)
  node scripts/artifact.mjs archive  <root> [--out file.zip|dir] the whole folder as one zip (backup, another computer,
                                                                  someone else); beside the folder unless --out says

<root> is the board's folder: documents at <root>/db/<collection>/<doc_id>.json, uploads in <root>/_blobs/,
comments in <root>/comments.json, the share links and guests in <root>/.sharing.json.
A batch is a JSON array (or {"writes": [...]}) of {op, path: "collection/doc_id" (or collection + doc_id), data | file_path};
in data, {"$file": "path"} is replaced by that file's text. update merges fields; null or {"__delete__": true} removes one.
Paths in a batch are relative to the current directory.
Limits: ${MAX_ELEMENTS} elements, 200 KB each, 2 MB in all; ${MAX_BATCH_WRITES} writes and 1 MB a batch.
Skill: ${SKILL_DIR}`;
async function main() {
  const [command, ...rest] = process.argv.slice(2);
  const { positional, flags } = parseArgs(rest);
  switch (command) {
    case "write-db": {
      const root = resolveRoot(positional[0], { create: true });
      const from = positional[1];
      if (!from) throw new CliError("MISSING_BATCH", "Give the batch: a JSON file, or - to read it from stdin.");
      let text;
      try {
        text = from === "-" ? fs10.readFileSync(0, "utf8") : fs10.readFileSync(path9.resolve(from), "utf8");
      } catch {
        throw new CliError("FILE_NOT_FOUND", `No such batch file: ${from}`);
      }
      let batch;
      try {
        batch = JSON.parse(text);
      } catch (error) {
        throw new CliError("INVALID_BATCH", `The batch is not JSON: ${error.message}`);
      }
      const writes = Array.isArray(batch) ? batch : Array.isArray(batch?.writes) ? batch.writes : isObject2(batch) && batch.op ? [batch] : null;
      if (!writes) throw new CliError("INVALID_BATCH", 'A batch is an array of writes, or {"writes": [...]}.');
      const written = applyWrites(root, writes);
      const server = readState(root);
      print({ root, written, ...server && alive(server.pid) ? { note: "The open board picks the change up by itself." } : {} });
      return 0;
    }
    case "read-db":
      print(readDb(resolveRoot(positional[0]), positional[1]));
      return 0;
    case "upload":
      print(upload(resolveRoot(positional[0], { create: true }), positional[1], flags));
      return 0;
    case "delete-asset":
      print(deleteAsset(resolveRoot(positional[0]), positional[1]));
      return 0;
    case "check": {
      const { result, problems } = check(resolveRoot(positional[0]));
      print(result);
      return problems > 0 ? 1 : 0;
    }
    case "open":
      await open(resolveRoot(positional[0], { create: true }), flags);
      return 0;
    case "serve":
      return await serve(resolveRoot(positional[0], { create: true }), flags) ? -1 : 0;
    case "stop":
      await stop(resolveRoot(positional[0]));
      return 0;
    case "share":
      await share(resolveRoot(positional[0]), flags);
      return 0;
    case "comments": {
      const root = resolveRoot(positional[0]);
      print(flags.has("wait") ? await waitComments(root, flags) : await listComments(root, flags.has("all")));
      return 0;
    }
    case "context":
      print(await contextCommand(resolveRoot(positional[0])));
      return 0;
    case "comment-reply":
      print(await replyComment(resolveRoot(positional[0]), positional[1], positional.slice(2), flags.has("resolve")));
      return 0;
    case "comment-resolve":
      print(await resolveComment(resolveRoot(positional[0]), positional[1], flags.has("reopen")));
      return 0;
    case "archive": {
      const made = await archiveCommand(resolveRoot(positional[0]), flags.get("out"));
      print({ ...made, open: `unzip it anywhere, then ${cmd("open", `<there>/${made.folder}`)}` });
      return 0;
    }
    case void 0:
    case "help":
    case "--help":
    case "-h":
      process.stdout.write(`${USAGE}
`);
      return command === void 0 ? 2 : 0;
    default:
      process.stderr.write(`Unknown command: ${command}

${USAGE}
`);
      return 2;
  }
}
if (typeof __BAOBOT_LIB__ === "undefined") main().then(
  (code) => {
    if (code >= 0) process.exitCode = code;
  },
  (error) => {
    process.stderr.write(`${JSON.stringify({ error: error.code ?? "ERROR", message: error.message })}
`);
    process.exitCode = 2;
  }
);
export {
  applyWrites,
  check,
  mountSite,
  readDb,
  upload
};

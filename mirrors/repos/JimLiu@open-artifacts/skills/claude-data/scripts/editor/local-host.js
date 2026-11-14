// claude-data local host: globalThis.claude for the Dashboard runtime (prebuilt; do not edit).
"use strict";
(() => {
  var isObject = (v) => typeof v === "object" && v !== null && !Array.isArray(v);
  var isDeleteMarker = (v, nullStored) => v === null && !nullStored || isObject(v) && v.__delete__ === true && Object.keys(v).length === 1;
  function patched(target, patch, nullStored) {
    const out = { ...target };
    for (const [k, v] of Object.entries(patch)) {
      if (k === "__proto__") continue;
      if (isDeleteMarker(v, nullStored)) delete out[k];
      else if (isObject(v)) out[k] = patched(isObject(out[k]) ? out[k] : {}, v, nullStored);
      else out[k] = v;
    }
    return out;
  }
  var EXPECT_MS = 3e4;
  function writeBases(store2, known = () => false, { nullStored = false } = {}) {
    const wrote = /* @__PURE__ */ new Map();
    const writing = /* @__PURE__ */ new Map();
    const expected = /* @__PURE__ */ new Map();
    return {
      begin(path, op, data) {
        const seen = store2.get(path);
        const told = expected.get(path);
        expected.delete(path);
        const fresh = told !== void 0 && Date.now() - told.at < EXPECT_MS;
        const from = fresh ? told.base : wrote.get(path);
        const base = from ?? (seen !== void 0 ? JSON.parse(seen) : known() ? null : void 0);
        const body = JSON.stringify({ op, path, data, base, ...fresh && told.chosen ? { chosen: true } : {} });
        const sent = JSON.parse(body);
        const after = !isObject(sent.data) ? void 0 : op === "set" ? sent.data : isObject(sent.base) ? patched(sent.base, sent.data, nullStored) : sent.base === null ? patched({}, sent.data, nullStored) : void 0;
        const before = wrote.get(path);
        if (after) wrote.set(path, after);
        else wrote.delete(path);
        writing.set(path, (writing.get(path) ?? 0) + 1);
        return {
          body,
          done(ok) {
            const left = (writing.get(path) ?? 1) - 1;
            if (left > 0) writing.set(path, left);
            else writing.delete(path);
            if (!ok && wrote.get(path) === after) {
              if (before) wrote.set(path, before);
              else wrote.delete(path);
            }
          }
        };
      },
      changed(path) {
        for (const p of path === void 0 ? [...wrote.keys()] : [path]) if (!writing.has(p)) wrote.delete(p);
      },
      expect(path, base, chosen) {
        if (isObject(base)) expected.set(path, { base: JSON.parse(JSON.stringify(base)), at: Date.now(), chosen: chosen === true });
      }
    };
  }

  var MAX_PRESENCE_BYTES = 4096;
  var EMPTY = Object.freeze([]);
  var EVENT_TOPIC = /^[a-z][a-z0-9_.-]{0,47}$/;
  var MAX_EVENT_BYTES = 4096;
  var EVENTS_PER_SECOND = 40;
  var EVENT_BURST = 80;
  var MAX_POST_BYTES = 48 << 10;
  var bytesOf = (value) => new TextEncoder().encode(JSON.stringify(value)).length;
  function plainJson(value) {
    let left = 16384;
    const stack = [[value, 0]];
    while (stack.length) {
      if (left-- <= 0) return false;
      const [item, depth] = stack.pop();
      if (item === null || typeof item !== "object") {
        if (typeof item === "function" || typeof item === "symbol" || typeof item === "bigint") return false;
        continue;
      }
      if (depth > 24) return false;
      if (Array.isArray(item)) {
        if (item.length > 4096) return false;
        for (const entry of item) stack.push([entry, depth + 1]);
        continue;
      }
      if (ArrayBuffer.isView(item)) return false;
      const proto = Object.getPrototypeOf(item);
      if (proto !== Object.prototype && proto !== null) return false;
      const keys = Object.keys(item);
      if (keys.length > 4096) return false;
      for (const key of keys) stack.push([item[key], depth + 1]);
    }
    return true;
  }
  function report(error) {
    try {
      if (typeof reportError === "function") reportError(error);
      else setTimeout(() => {
        throw error;
      }, 0);
    } catch {
    }
  }
  function createRoomClient(options) {
    const serverMe = options.serverMe ?? options.me;
    const local = (by) => by === serverMe ? options.me : by;
    const doFetch = options.fetch ?? ((...args) => fetch(...args));
    let views = [];
    let snapshot = EMPTY;
    let byPeer = /* @__PURE__ */ new Map();
    let heard = false;
    let open = false;
    const handlers = /* @__PURE__ */ new Set();
    const connectionListeners = /* @__PURE__ */ new Set();
    const pageListeners = /* @__PURE__ */ new Set();
    let published = {};
    let queued = null;
    let waiters = [];
    let outbox = [];
    let sending = false;
    let frame = false;
    let followHandler = null;
    const topics = /* @__PURE__ */ new Map();
    let budget = EVENT_BURST;
    let toppedAt = Date.now();
    let reportedLimit = false;
    const withinBudget = () => {
      const now = Date.now();
      budget = Math.min(EVENT_BURST, budget + Math.max(0, now - toppedAt) / 1e3 * EVENTS_PER_SECOND);
      toppedAt = now;
      if (budget < 1) {
        if (!reportedLimit) {
          reportedLimit = true;
          report(new Error("room: rate limit - dropping emits sent faster than the budget (about 40/s; the page keeps working; high-rate state belongs in presence; this is reported once per page load)"));
        }
        return false;
      }
      budget -= 1;
      return true;
    };
    const peerOf = (view, previous) => {
      const presence2 = view.peer === options.peer ? published : view.presence;
      const json = JSON.stringify(presence2);
      const isMe = view.kind !== "agent" && view.by === serverMe;
      if (previous && previous.json === json && previous.peer.isMe === isMe) return previous;
      const peer = Object.freeze({
        peer: view.peer,
        by: view.kind === "agent" ? null : local(view.by),
        isMe,
        sameTab: view.peer === options.peer,
        kind: view.kind === "agent" ? "agent" : "viewer",
        guest: false,
        presence: Object.freeze({ ...presence2 }),
        updatedAt: Date.now()
      });
      return { peer, json };
    };
    const rebuild = () => {
      const next = /* @__PURE__ */ new Map();
      let changed = views.length !== byPeer.size;
      for (const view of views) {
        const before = byPeer.get(view.peer);
        const entry = peerOf(view, before);
        if (entry !== before) changed = true;
        next.set(view.peer, entry);
      }
      byPeer = next;
      if (changed) snapshot = Object.freeze([...next.values()].map((e) => e.peer));
      return changed;
    };
    const deliver2 = () => {
      frame = false;
      for (const entry of handlers) {
        const before = entry.delivered;
        const now = new Map(snapshot.map((p) => [p.peer, p]));
        const joined = [];
        const updated = [];
        const left = [];
        for (const p of snapshot) {
          const was = before?.get(p.peer);
          if (!was) joined.push(p);
          else if (was !== p) updated.push(p);
        }
        if (before) {
          for (const [id, p] of before) if (!now.has(id)) left.push(p);
        }
        if (before && !joined.length && !updated.length && !left.length) continue;
        entry.delivered = now;
        entry.handler({ peers: snapshot, joined, left, updated });
      }
      for (const listener of pageListeners) listener();
    };
    const schedule = () => {
      if (frame) return;
      frame = true;
      nextFrame(deliver2);
    };
    const flush2 = async () => {
      if (sending || !queued && !outbox.length || !open) return;
      sending = true;
      const patch = queued;
      queued = null;
      let bytes = patch ? bytesOf(patch) : 0;
      let take = 0;
      while (take < outbox.length && (take === 0 || bytes + outbox[take].bytes <= MAX_POST_BYTES)) bytes += outbox[take++].bytes;
      const events = outbox.slice(0, take);
      outbox = outbox.slice(take);
      const done = [...waiters, ...events];
      waiters = [];
      try {
        const res = await doFetch(`${options.base}__presence`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            peer: options.peer,
            ...patch ? { patch } : {},
            ...events.length ? { events: events.map((e) => e.data === void 0 ? { topic: e.topic } : { topic: e.topic, data: e.data }) } : {}
          })
        });
        if (res.status === 409) {
          for (const w of done) w.resolve();
          return;
        }
        if (!res.ok) throw { code: "upstream_error", message: `presence: HTTP ${res.status}` };
        for (const w of done) w.resolve();
      } catch (error) {
        for (const w of done) w.reject(typeof error === "object" && error !== null && "code" in error ? error : { code: "upstream_error", message: String(error) });
      } finally {
        sending = false;
        if ((queued || outbox.length) && open) void flush2();
      }
    };
    const room2 = {
      presence(patch) {
        if (typeof patch !== "object" || patch === null || Array.isArray(patch)) {
          return Promise.reject({ code: "invalid_argument", message: "presence(patch) takes an object." });
        }
        const merged = { ...published };
        for (const [key, value] of Object.entries(patch)) {
          if (value === null || value === void 0) delete merged[key];
          else merged[key] = value;
        }
        if (bytesOf(merged) > MAX_PRESENCE_BYTES) {
          return Promise.reject({ code: "invalid_argument", message: `Presence is at most ${MAX_PRESENCE_BYTES} bytes of JSON.` });
        }
        published = merged;
        if (rebuild()) schedule();
        queued = { ...queued ?? {}, ...patch };
        if (!open) return Promise.resolve();
        const promise = new Promise((resolve, reject) => waiters.push({ resolve, reject }));
        void flush2();
        return promise;
      },
      peers: () => snapshot,
      onPeers(handler, _onError) {
        const entry = { handler, delivered: null };
        handlers.add(entry);
        if (heard) queueMicrotask(() => handlers.has(entry) && entry.delivered === null && schedule());
        return () => void handlers.delete(entry);
      },
      connected: () => open,
      onConnection(onChange) {
        connectionListeners.add(onChange);
        return () => void connectionListeners.delete(onChange);
      },
      emit(topic, data) {
        if (typeof topic !== "string" || !EVENT_TOPIC.test(topic)) {
          return Promise.reject({ code: "invalid_argument", message: "emit topic must match ^[a-z][a-z0-9_.-]{0,47}$ (colon-free)" });
        }
        let size = 0;
        let copy;
        if (data !== void 0) {
          try {
            if (!plainJson(data)) throw new Error("not plain");
            const json = JSON.stringify(data);
            size = new TextEncoder().encode(json).length;
            copy = JSON.parse(json);
          } catch {
            return Promise.reject({ code: "invalid_argument", message: "emit data must be plain JSON data" });
          }
          if (size > MAX_EVENT_BYTES) return Promise.reject({ code: "invalid_argument", message: `emit data serializes over ${MAX_EVENT_BYTES} bytes` });
        }
        if (!withinBudget() || !open) return Promise.resolve();
        return new Promise((resolve, reject) => {
          outbox.push({ topic, data: copy, bytes: size + topic.length + 32, resolve, reject });
          void flush2();
        });
      },
      on(topic, handler, onError) {
        if (typeof handler !== "function") throw new TypeError("room.on requires a handler function");
        const entry = { fn: handler, err: typeof onError === "function" ? onError : void 0, dead: false };
        if (typeof topic !== "string" || !EVENT_TOPIC.test(topic)) {
          queueMicrotask(() => {
            if (entry.dead) return;
            entry.dead = true;
            try {
              entry.err?.({ code: "invalid_argument", message: "on topic must match ^[a-z][a-z0-9_.-]{0,47}$ (colon-free)" });
            } catch (error) {
              report(error);
            }
          });
          return () => void (entry.dead = true);
        }
        let listeners = topics.get(topic);
        if (!listeners) topics.set(topic, listeners = /* @__PURE__ */ new Set());
        const set = listeners;
        set.add(entry);
        return () => {
          entry.dead = true;
          set.delete(entry);
          if (!set.size && topics.get(topic) === set) topics.delete(topic);
        };
      }
    };
    const page = {
      me: { peer: options.peer, by: serverMe },
      peers: () => views.map((v) => v.peer === options.peer ? { ...v, presence: published } : v),
      subscribe(onChange) {
        pageListeners.add(onChange);
        return () => void pageListeners.delete(onChange);
      },
      following() {
        if (!followHandler) return void 0;
        const follow = published.follow;
        return typeof follow === "object" && follow !== null && typeof follow.of === "string" ? follow.of : null;
      },
      follow(peer) {
        followHandler?.(peer);
      }
    };
    if (typeof window !== "undefined") {
      window.__baoyuPresence = page;
      window.dispatchEvent(new Event("baoyu-presence"));
    }
    const setOpen = (next) => {
      if (open === next) return;
      open = next;
      for (const listener of connectionListeners) listener(next);
      if (!next) {
        const dropped = outbox;
        outbox = [];
        for (const e of dropped) e.resolve();
      }
      if (next) {
        if (Object.keys(published).length) queued = { ...published };
        void flush2();
      }
    };
    return {
      room: room2,
      page,
      nameOf: (by) => views.find((v) => v.kind !== "agent" && local(v.by) === by)?.name,
      offerFollow(handler) {
        if (followHandler === null === (handler === null)) {
          followHandler = handler;
          return;
        }
        followHandler = handler;
        for (const listener of pageListeners) listener();
      },
      attach(source2) {
        source2.addEventListener("peers", (event) => {
          let list;
          try {
            const body = JSON.parse(event.data);
            if (!Array.isArray(body.peers)) return;
            list = body.peers.filter(
              (p) => typeof p === "object" && p !== null && typeof p.peer === "string" && typeof p.by === "string"
            );
          } catch {
            return;
          }
          views = list;
          heard = true;
          setOpen(true);
          rebuild();
          schedule();
        });
        source2.addEventListener("room", (event) => {
          let body;
          try {
            body = JSON.parse(event.data);
          } catch {
            return;
          }
          if (typeof body !== "object" || body === null || typeof body.peer !== "string" || typeof body.by !== "string" || typeof body.topic !== "string") return;
          const listeners = topics.get(body.topic);
          if (!listeners) return;
          const agent = body.kind === "agent";
          const message = Object.freeze({
            peer: body.peer,
            by: agent ? null : local(body.by),
            isMe: !agent && body.by === serverMe,
            sameTab: body.peer === options.peer,
            kind: agent ? "agent" : "viewer",
            guest: false,
            topic: body.topic,
            data: body.data
          });
          for (const entry of [...listeners]) {
            if (entry.dead) continue;
            try {
              entry.fn(message);
            } catch (error) {
              report(error);
            }
          }
        });
        source2.addEventListener("error", () => {
          if (source2.readyState !== EventSource.OPEN) setOpen(false);
        });
      }
    };
  }
  function shareIdentity() {
    const share = typeof window === "undefined" ? void 0 : window.__baoyuShare;
    if (!share || typeof share.id !== "string" || typeof share.name !== "string") return null;
    return { id: share.id, name: share.name, role: typeof share.role === "string" ? share.role : "" };
  }
  var onPreview = () => typeof window !== "undefined" && Boolean(window.__baoyuHistory?.preview);
  function pageRoom(base, peer) {
    const share = shareIdentity();
    if (!share || onPreview()) return null;
    return createRoomClient({ base, peer, me: share.id });
  }
  function nextFrame(run) {
    let done = false;
    const once = () => {
      if (done) return;
      done = true;
      run();
    };
    if (typeof requestAnimationFrame === "function" && typeof document !== "undefined" && document.visibilityState === "visible") requestAnimationFrame(once);
    setTimeout(once, typeof document !== "undefined" && document.visibilityState === "visible" ? 100 : 16);
  }
  function newPeerId() {
    const bytes = new Uint8Array(12);
    crypto.getRandomValues(bytes);
    return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  }

  var AT = /^\d{1,9}$/.test(new URLSearchParams(location.search).get("at") ?? "") ? new URLSearchParams(location.search).get("at") : null;
  var api = (route) => AT === null ? route : `${route}${route.includes("?") ? "&" : "?"}at=${AT}`;
  var UNAVAILABLE = Object.freeze({ available: false });
  var user = { id: "local", name: "You", canEdit: true, owner: true };
  var sessionReady = fetch(api("/_api/session"), { cache: "no-store" }).then((r) => r.ok ? r.json() : null).then((s) => {
    if (!s) return;
    if (typeof s.userId === "string" && s.userId) user.id = s.userId;
    if (typeof s.userName === "string" && s.userName) user.name = s.userName;
    if (typeof s.canEdit === "boolean") user.canEdit = s.canEdit;
    if (typeof s.role === "string") user.owner = s.role === "owner";
  }).catch(() => {
  });
  var clone = (v) => v === void 0 ? void 0 : JSON.parse(JSON.stringify(v));
  var dbError = (code, message) => Object.assign(new Error(message), { code, message });
  async function call(url, init) {
    let res;
    try {
      res = await fetch(url, { cache: "no-store", ...init });
    } catch {
      throw dbError("unavailable", "The local dashboard server is not running.");
    }
    const body = await res.json().catch(() => null);
    if (!res.ok) throw dbError(body && body.code || "unavailable", body && body.message || `HTTP ${res.status}`);
    return body;
  }
  var store = /* @__PURE__ */ new Map();
  var bases = writeBases(store, () => live, { nullStored: true });
  window.__baoyuWriteBase = (path, base, chosen) => bases.expect(path, base, chosen);
  var live = false;
  var subs = /* @__PURE__ */ new Set();
  var source = null;
  var PEER = newPeerId();
  var presence = AT === null ? pageRoom(new URL("./", location.href).href, PEER) : null;
  var parentOf = (path) => path.slice(0, path.lastIndexOf("/"));
  var idOf = (path) => path.slice(path.lastIndexOf("/") + 1);
  function deliver(sub, initial) {
    const changes = [];
    const seen = /* @__PURE__ */ new Set();
    for (const [path, text] of store) {
      if (parentOf(path) !== sub.collection) continue;
      seen.add(path);
      const before = sub.delivered.get(path);
      if (before === text) continue;
      sub.delivered.set(path, text);
      changes.push({ type: before === void 0 ? "added" : "modified", path, text });
    }
    for (const [path, text] of sub.delivered) {
      if (seen.has(path)) continue;
      sub.delivered.delete(path);
      changes.push({ type: "removed", path, text });
    }
    if (!initial && changes.length === 0) return;
    const docChanges = changes.map((c) => {
      const data = JSON.parse(c.text);
      return { type: c.type, doc: { id: idOf(c.path), data: () => clone(data) } };
    });
    try {
      sub.next({ docChanges: () => docChanges, metadata: { fromCache: false, hasPendingWrites: false } });
    } catch (error) {
      console.error("local host: snapshot listener threw", error);
    }
  }
  function flush() {
    for (const sub of subs) {
      const initial = !sub.started;
      sub.started = true;
      deliver(sub, initial);
    }
  }
  function connect() {
    if (source) return;
    source = new EventSource(api(presence ? `/_api/events?peer=${PEER}` : "/_api/events"));
    presence?.attach(source);
    source.addEventListener("snapshot", (event) => {
      const { docs } = JSON.parse(event.data);
      store.clear();
      for (const [path, data] of Object.entries(docs)) store.set(path, JSON.stringify(data));
      bases.changed();
      live = true;
      flush();
    });
    source.addEventListener("change", (event) => {
      const { changes } = JSON.parse(event.data);
      for (const { path, data } of changes) {
        if (data === null) store.delete(path);
        else store.set(path, JSON.stringify(data));
        bases.changed(path);
      }
      flush();
    });
    source.addEventListener("error", () => {
      if (!live) return;
      live = false;
      const failed = [...subs];
      subs.clear();
      for (const sub of failed) {
        try {
          sub.error(dbError("unavailable", "Lost the local dashboard server; retrying."));
        } catch {
        }
      }
    });
  }
  function collection(path) {
    const ref = {
      limit: () => ref,
      onSnapshot(next, error) {
        const sub = { collection: path, next, error: error || (() => {
        }), delivered: /* @__PURE__ */ new Map(), started: false };
        subs.add(sub);
        connect();
        if (live) setTimeout(() => subs.has(sub) && !sub.started && (sub.started = true, deliver(sub, true)), 0);
        return () => subs.delete(sub);
      }
    };
    return ref;
  }
  function doc(path) {
    const write = (op, data) => {
      const { body, done } = bases.begin(path, op, data);
      return call(api("/_api/write"), { method: "POST", headers: { "Content-Type": "application/json" }, body }).then(
        () => done(true),
        (error) => {
          done(false);
          throw error;
        }
      );
    };
    return {
      async get() {
        const body = await call(api(`/_api/doc?path=${encodeURIComponent(path)}`));
        const data = body.exists ? body.data : void 0;
        return { exists: body.exists === true, data: () => clone(data), metadata: { fromCache: false, hasPendingWrites: false } };
      },
      set: (data) => write("set", data),
      update: (data) => write("update", data),
      delete: () => write("delete")
    };
  }
  var db = { doc, collection };
  var assets = {
    async upload(file) {
      const name = file && typeof file.name === "string" && file.name || "upload";
      const res = await fetch(api("/_api/upload"), {
        method: "POST",
        headers: { "Content-Type": file && file.type || "application/octet-stream", "X-Filename": encodeURIComponent(name) },
        body: file
      });
      const body = await res.json().catch(() => null);
      if (!res.ok || !body) throw dbError(body && body.code || "unavailable", body && body.message || `Upload failed (HTTP ${res.status}).`);
      return { id: body.id, url: body.url };
    },
    // Uploads are content-addressed and small; the agent removes one with `artifact.mjs delete-asset`.
    async delete() {
    }
  };
  var EDIT_NAMES = /* @__PURE__ */ new Set(["data.write", "files.write", "assets.write"]);
  var users = {
    id: async () => (await sessionReady, user.id),
    name: async () => (await sessionReady, user.name),
    isOwner: async () => (await sessionReady, user.owner),
    // The owner and editors hold the db's `admin` level: they write the shared documents, the page and its files.
    canEdit: async () => (await sessionReady, user.canEdit),
    can: async (name) => (await sessionReady, EDIT_NAMES.has(name) && user.canEdit)
  };
  var downloads = {
    async save({ filename, data }) {
      const blob = data instanceof Blob ? data : new Blob([data]);
      const toFolder = globalThis.__baoyuSave;
      if (toFolder) {
        await toFolder(blob, filename || "download");
        return;
      }
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || "download";
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 6e4);
    }
  };
  var self = { publish: async () => ({}) };
  var agentRequests = globalThis.__baoyuAgentRequests;
  var REQUEST_LIMITS = { text: 1e4, label: 1e3, selection: 4e3 };
  var ABOUT_SELECTION = "About this part of the dashboard.";
  var room = {
    canSendToClaudeSession: async () => AT === null && (await sessionReady, user.owner) ? "available_if_opened" : "unavailable",
    async sendToClaudeSession(payload) {
      const words = typeof payload?.request === "string" ? payload.request.trim() : "";
      const label = typeof payload?.label === "string" ? payload.label.trim().slice(0, REQUEST_LIMITS.label) : "";
      const selection = typeof payload?.selectedText === "string" ? payload.selectedText.slice(0, REQUEST_LIMITS.selection) : "";
      const text = (words || (label || selection.trim() ? ABOUT_SELECTION : "")).slice(0, REQUEST_LIMITS.text);
      const sent = text !== "" && agentRequests !== void 0 && await agentRequests.send({ text, ...label ? { label } : {}, ...selection.trim() ? { selection } : {} });
      if (sent) return { to: "agent" };
      throw Object.assign(new Error("No agent is waiting for requests from this page."), { code: "claude_unavailable" });
    }
  };
  var capabilities = { db, assets, user: users, downloads, self, ...agentRequests ? { room } : {} };
  globalThis.claude = {
    ...capabilities,
    use: async (name) => {
      if (name === "assets" && !(await sessionReady, user.canEdit)) return UNAVAILABLE;
      return Object.hasOwn(capabilities, name) ? capabilities[name] : UNAVAILABLE;
    }
  };
  var NativeFontFace = globalThis.FontFace;
  if (typeof NativeFontFace === "function") {
    const LocalFontFace = function FontFace(family, src, descriptors) {
      if (typeof src === "string" && src.includes("/_runtime/")) {
        const face = new NativeFontFace(family, `local(${JSON.stringify(String(family))})`, descriptors);
        face.load = () => new Promise(() => {
        });
        return face;
      }
      return new NativeFontFace(family, src, descriptors);
    };
    LocalFontFace.prototype = NativeFontFace.prototype;
    globalThis.FontFace = LocalFontFace;
  }
})();

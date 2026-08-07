"use strict";

const $ = (id) => (typeof document === "undefined" ? null : document.getElementById(id));
const state = {
  project: null,
  files: [],
  visibleFiles: [],
  status: null,
  selected: null,
  version: null,
  dirty: false,
  saving: false,
  saveSequence: 0,
  loadSequence: 0,
  projectLoadSequence: 0,
  projectSwitching: false,
  apiBase: "",
  view: "preview",
  expandedGroups: new Set(),
};

const ROOT_ROLES = {
  inputs: "sources", "输入": "sources",
  development: "project", "项目开发": "project",
  bible: "bible", "设定集": "bible",
  episodes: "episodes", "剧集": "episodes",
};

const HIDDEN_ROOTS = new Set([
  ".short-drama", "creator-decisions", "创作者决策", "reviews", "审查",
  "delivery", "交付", "transactions", "事务",
]);

const HIDDEN_FILES = new Set([
  "short-drama.json", "manifest.json", "coverage.json", "delivery-containers.jsonl",
  "screenplay-index.jsonl",
]);

// Reading order inside one group: what the creator wrote, then what was built
// from it. Raw directory order otherwise buries the screenplay below the prompts.
const SECTION_ORDER = ["story", "project", "sources", "cast", "visual", "storyboard", "prompts", "other"];

const CONTENT_META = {
  sources: { label: "原始资料", description: "故事原稿与参考内容", icon: "稿" },
  project: { label: "项目设定", description: "故事方向与导演表达", icon: "案" },
  cast: { label: "人物场景", description: "角色、造型、场景与道具", icon: "角" },
  story: { label: "故事与剧本", description: "分集构思、节拍与台词", icon: "剧" },
  prompts: { label: "生成文案", description: "用于生成图片、关键帧与视频的文案", icon: "词" },
  visual: { label: "画面设计", description: "图片方案与视觉参考", icon: "画" },
  storyboard: { label: "分镜画面", description: "镜头、关键帧与运动", icon: "镜" },
  other: { label: "其他内容", description: "放在标准目录之外的创作文件", icon: "他" },
};

const INTERNAL_KEY_PARTS = [
  "hash", "sha", "path", "ref", "owner", "schema", "artifact", "authority",
  "lifecycle", "manifest", "checksum", "evidence", "transaction", "snapshot",
  "candidate", "reviewer", "verdict",
];

const INTERNAL_INLINE_VALUE_PATTERNS = [
  /\b[a-f0-9]{20,128}\b/gi,
  /\bshort-drama-[a-z0-9-]+\b/gi,
  /\b(?:[a-z][a-z0-9+.-]*:\/\/|file:)[^\s，。；、）》\]]*/gi,
  /(?:\.short-drama|剧集|设定集|项目开发|输入|创作者决策|审查|交付|事务|episodes|bible|development|inputs|creator-decisions|reviews|delivery|transactions)[\\/][^\s，。；、）》\]]*/gi,
  /(?:^|[\s(（])(?:[/\\~]|\.\.?[/\\]|[a-z]:[/\\])[^\s，。；、）》\]]*/gi,
];

const INTERNAL_WHOLE_VALUE_PATTERNS = [
  /^(?:[^\\/]+[\\/])+(?:[^\\/]+\.(?:md|txt|jsonl?|ya?ml|mp4|mov|webm|png|jpe?g|webp))$/i,
  /^(?:[^\s\\/]+\\){2,}[^\s\\/]+$/,
];

const INTERNAL_VALUE_TOKENS = new Set([
  "absent", "in_progress", "materialized", "not_run", "pass_with_warnings",
  "not_requested", "provisional", "approve_with_notes", "not_evaluated",
  "delivered", "blocked", "candidate", "artifact", "snapshot", "transaction",
  "accepted", "rejected", "approve", "ready", "pending", "revise", "stale",
  "failed", "fail", "pass",
]);

const INTERNAL_EXACT_KEYS = new Set([
  "build_state", "validation_state", "creator_acceptance", "independent_review",
  "delivery_gate", "active_transaction", "last_action", "project_root", "project_id",
]);

const FILE_LABELS = {
  "readme.md": "项目说明",
  "creative-brief.md": "创作简报",
  "story-engine.md": "故事引擎",
  "director-brief.md": "导演阐述",
  "adaptation-map.jsonl": "改编要点",
  "series-arc.json": "全剧走向",
  "episode-map.jsonl": "分集安排",
  "characters.jsonl": "人物设定",
  "looks.jsonl": "造型设定",
  "locations.jsonl": "场景设定",
  "location-views.jsonl": "场景视角",
  "props.jsonl": "关键道具",
  "prop-states.jsonl": "道具变化",
  "episode-card.json": "本集提要",
  "beats.jsonl": "剧情节拍",
  "screenplay.md": "剧本",
  "screenplay-index.jsonl": "场次索引",
  "voice-record-sheet.jsonl": "配音稿",
  "occurrences.jsonl": "出场安排",
  "decisions.jsonl": "画面选择",
  "continuity.jsonl": "连续性",
  "image-prompt-specs.jsonl": "图片生成方案",
  "image-prompts.md": "图片生成文案",
  "shots.jsonl": "镜头表",
  "keyframes.jsonl": "关键帧",
  "keyframe-prompts.md": "关键帧生成文案",
  "motion-specs.jsonl": "镜头运动",
  "video-prompts.md": "视频生成文案",
};

// The server speaks a fixed English protocol vocabulary. The workspace is
// creator-facing, so each known message gets a Chinese sentence that also says
// what to do next; anything unmapped passes through rather than being hidden.
const FAILURE_COPY = {
  "file changed since it was opened": "这份内容在别处已经更新，请重新打开后再修改。",
  "text file cannot be opened safely": "这份内容暂时无法打开，请刷新后重试。",
  "text file cannot be replaced safely": "这份内容暂时无法保存，请刷新后重试。",
  "media file cannot be opened safely": "这段画面暂时无法打开，请刷新后重试。",
  "file type is not editable text": "这种内容不能在工作台里直接修改。",
  "content exceeds file limit": "内容太长，无法保存。",
  "file exceeds preview limit": "内容太长，无法在这里展示。",
  "media exceeds preview limit": "这段画面太大，无法在这里预览。",
  "path is not a file": "找不到这份内容，可能已被移动。",
  "media path is not a file": "找不到这段画面，可能已被移动。",
  "project not found": "找不到这个项目。",
  "project path changed during the save": "项目位置在保存过程中发生变化，请重新打开。",
  "unsupported preview media": "这种画面格式无法在这里预览。",
  "request body is too large": "内容太长，无法提交。",
  "internal dashboard error": "工作台遇到问题，请刷新后重试。",
};

function friendlyFailure(message) {
  return FAILURE_COPY[String(message || "").trim()] || String(message || "");
}

// CSS.escape is unavailable in older WebKit; the group keys are our own
// ("project", "episode:EP001") so a conservative escape is enough.
function cssEscape(value) {
  return String(value).replace(/["\\]/g, "\\$&");
}

function creatorTitle(title) {
  return typeof title === "string" && title.trim() ? title.trim() : "未命名短剧";
}

function pathSegments(path) {
  return String(path || "").split("/").filter(Boolean);
}

function creatorSection(path) {
  const parts = pathSegments(path);
  const first = parts[0] || "";
  const lowerFirst = first.toLowerCase();
  const filename = (parts.at(-1) || "").toLowerCase();
  if (!parts.length || HIDDEN_ROOTS.has(first) || HIDDEN_ROOTS.has(lowerFirst)) return null;
  if (HIDDEN_FILES.has(filename)) return null;
  if (parts.length === 1) {
    return filename === "readme.md" ? "project" : "other";
  }
  const root = ROOT_ROLES[first] || ROOT_ROLES[lowerFirst];
  if (root === "sources" || root === "project") return root;
  if (root === "bible") return "cast";
  if (root !== "episodes") return "other";
  const area = (parts[2] || "").toLowerCase();
  if (/prompts?\.(?:md|jsonl?)$/i.test(filename) || filename.includes("prompt")) return "prompts";
  if (["assets", "资产"].includes(area)) return "visual";
  if (["storyboard", "分镜"].includes(area)) return "storyboard";
  return "story";
}

function creatorProjection(value) {
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (INTERNAL_VALUE_TOKENS.has(normalized) || INTERNAL_WHOLE_VALUE_PATTERNS.some((pattern) => pattern.test(value.trim()))) return undefined;
    let cleaned = value;
    for (const pattern of INTERNAL_INLINE_VALUE_PATTERNS) cleaned = cleaned.replace(pattern, "");
    cleaned = cleaned.replace(/\s{2,}/g, " ").replace(/\s+([，。；、])/g, "$1").trim();
    return cleaned || undefined;
  }
  if (value === null || typeof value !== "object") return value;
  if (Array.isArray(value)) {
    return value.map(creatorProjection).filter((item) => item !== undefined);
  }
  const projected = {};
  for (const [key, raw] of Object.entries(value)) {
    const normalized = String(key)
      .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fff]+/g, "_")
      .replace(/^_+|_+$/g, "");
    const keyParts = normalized.split("_").filter(Boolean);
    if (INTERNAL_EXACT_KEYS.has(normalized) || INTERNAL_KEY_PARTS.some((part) => keyParts.includes(part))) continue;
    const child = creatorProjection(raw);
    if (child !== undefined) projected[key] = child;
  }
  return projected;
}

function valueIs(axis, wanted) {
  if (typeof axis === "string") return axis === wanted;
  return Boolean(axis && typeof axis === "object" && Number(axis[wanted]) > 0);
}

function axisOnly(axis, allowed) {
  if (typeof axis === "string") return allowed.includes(axis);
  if (!axis || typeof axis !== "object") return false;
  const active = Object.entries(axis).filter(([, count]) => Number(count) > 0).map(([value]) => value);
  return active.length > 0 && active.every((value) => allowed.includes(value));
}

function creatorStatus(lifecycle, recovery = null) {
  if (!lifecycle || typeof lifecycle !== "object") return ["创作中", "neutral"];
  if (
    valueIs(lifecycle.build_state, "failed") ||
    valueIs(lifecycle.build_state, "fail") ||
    valueIs(lifecycle.validation_state, "failed") ||
    valueIs(lifecycle.validation_state, "fail") ||
    valueIs(lifecycle.creator_acceptance, "rejected") ||
    valueIs(lifecycle.independent_review, "rejected") ||
    valueIs(lifecycle.independent_review, "revise")
  ) return ["需要修改", "danger"];
  if (recovery?.needed) return ["需要更新", "warning"];
  if (valueIs(lifecycle.build_state, "stale")) return ["需要更新", "warning"];
  if (valueIs(lifecycle.creator_acceptance, "pending")) return ["待你确认", "warning"];
  const accepted = axisOnly(lifecycle.creator_acceptance, ["accepted"]);
  const reviewed = axisOnly(lifecycle.independent_review, ["approve", "approve_with_notes"]);
  const ready = axisOnly(lifecycle.delivery_gate, ["ready", "delivered"]);
  const built = lifecycle.build_state === undefined || axisOnly(lifecycle.build_state, ["materialized"]);
  const valid = lifecycle.validation_state === undefined || axisOnly(lifecycle.validation_state, ["pass", "pass_with_warnings"]);
  if (accepted && reviewed && ready && built && valid) return ["可以导出", "success"];
  const unfinished =
    valueIs(lifecycle.build_state, "absent") ||
    valueIs(lifecycle.build_state, "in_progress") ||
    valueIs(lifecycle.validation_state, "not_run") ||
    valueIs(lifecycle.independent_review, "not_requested") ||
    valueIs(lifecycle.independent_review, "provisional") ||
    valueIs(lifecycle.delivery_gate, "not_evaluated") ||
    valueIs(lifecycle.delivery_gate, "blocked");
  if (accepted && unfinished) return ["已采用", "neutral"];
  if (accepted) return ["已采用", "success"];
  return ["创作中", "neutral"];
}

function projectRecovery(status) {
  return { needed: Boolean(status?.recovery?.needed || status?.layout?.mode === "mixed") };
}

function collectEpisodes(files) {
  const episodes = new Map();
  for (const file of files || []) {
    const parts = pathSegments(file.path);
    const root = ROOT_ROLES[parts[0]] || ROOT_ROLES[(parts[0] || "").toLowerCase()];
    if (root !== "episodes" || !parts[1] || !creatorSection(file.path)) continue;
    if (!episodes.has(parts[1])) episodes.set(parts[1], []);
    episodes.get(parts[1]).push(file);
  }
  return [...episodes.entries()]
    .map(([id, episodeFiles]) => ({ id, files: episodeFiles }))
    .sort((left, right) => left.id.localeCompare(right.id, "zh-CN", { numeric: true }));
}

function savedContentIsCurrent(submitted, current) {
  return submitted === current;
}

function statusRefreshFailureMessage() {
  return "内容已保存，但状态刷新失败，请稍后重试";
}

function fileLabel(path) {
  const name = (pathSegments(path).at(-1) || "内容").toLowerCase();
  return FILE_LABELS[name] || name.replace(/\.(md|jsonl?|txt)$/i, "").replace(/[-_]/g, " ");
}

function episodeName(path) {
  const parts = pathSegments(path);
  const root = ROOT_ROLES[parts[0]] || ROOT_ROLES[(parts[0] || "").toLowerCase()];
  return root === "episodes" ? parts[1] : "";
}

function contentGroupKey(file) {
  const episode = episodeName(file?.path);
  return episode ? `episode:${episode}` : "project";
}

function creatorEditable(file) {
  // Mirrors the server's TEXT_EXTENSIONS. Structured files stay editable because
  // the server rejects invalid JSON on save, and subtitles are a shipped feature.
  return Boolean(file?.writable && /\.(md|txt|srt|ass|json|jsonl)$/i.test(file.path));
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(text, className, action) {
  const node = element("button", className, text);
  node.onclick = action;
  return node;
}

function statusPill(lifecycle, recovery = null) {
  const [label, tone] = creatorStatus(lifecycle, recovery);
  const pill = element("span", "status-pill", label);
  pill.dataset.tone = tone;
  return pill;
}

async function api(path, options) {
  const requestPath = state.apiBase && path.startsWith("/api/") ? `${state.apiBase}${path}` : path;
  const response = await fetch(requestPath, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

async function establishSession() {
  const hashValue = location.hash.startsWith("#") ? location.hash.slice(1) : "";
  const token = ["home", "creation", "tasks", "export"].includes(hashValue) ? "" : hashValue;
  const storageKey = "shortDramaApiBase";
  if (!token) {
    state.apiBase = sessionStorage.getItem(storageKey) || "";
    return;
  }
  const response = await fetch("/api/session", { method: "POST", headers: { "X-Short-Drama-Token": token } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  if (typeof data.apiBase !== "string" || !data.apiBase.startsWith("/_short_drama/")) throw new Error("本机会话响应无效");
  state.apiBase = data.apiBase;
  sessionStorage.setItem(storageKey, state.apiBase);
  history.replaceState(null, "", `${location.pathname}${location.search}`);
}

function flatten(nodes, out = []) {
  for (const node of nodes || []) {
    if (node.type === "directory") flatten(node.children, out);
    else out.push(node);
  }
  return out;
}

function setMessage(text, tone = "neutral") {
  $("message").textContent = text;
  $("message").dataset.tone = tone;
}

function showNotice(text, tone = "warning") {
  const notice = element("div", "notice", text);
  notice.dataset.tone = tone;
  $("notices").replaceChildren(notice);
}

function clearNotice() {
  $("notices").replaceChildren();
}

function renderProjectSummary() {
  $("workspaceStatus").replaceChildren(statusPill(state.status?.lifecycle, projectRecovery(state.status)));
}

function navigationItem(file) {
  const section = creatorSection(file.path);
  const meta = CONTENT_META[section] || CONTENT_META.project;
  const item = button("", "content-link", () => openFile(file, true));
  item.classList.toggle("active", state.selected?.path === file.path);
  if (state.selected?.path === file.path) item.setAttribute("aria-current", "true");
  const icon = element("span", "content-link-icon", file.type === "media" ? "▶" : meta.icon);
  const copy = element("span", "content-link-copy");
  copy.append(element("strong", "", fileLabel(file.path)), element("small", "", file.type === "media" ? "画面预览" : meta.label));
  item.append(icon, copy);
  return item;
}

function orderedForReading(files) {
  return [...files].sort((left, right) => {
    const rank = SECTION_ORDER.indexOf(creatorSection(left.path)) - SECTION_ORDER.indexOf(creatorSection(right.path));
    if (rank !== 0) return rank;
    return fileLabel(left.path).localeCompare(fileLabel(right.path), "zh-Hans-CN");
  });
}

function navigationGroup(title, files, groupKey, forceExpanded = false) {
  const group = element("section", "content-nav-group");
  const expanded = forceExpanded || state.expandedGroups.has(groupKey);
  const heading = button("", "content-nav-group-toggle", () => {
    // While searching, every group is force-expanded. Toggle the stored state to
    // match what the creator sees, so clearing the search cannot collapse the
    // group they just opened — or the one holding the open document.
    if (state.expandedGroups.has(groupKey)) state.expandedGroups.delete(groupKey);
    else state.expandedGroups.add(groupKey);
    renderContentList();
    // renderContentList replaces this button, so focus would fall to <body>.
    const restored = $("contentList")?.querySelector(`[data-group-key="${cssEscape(groupKey)}"]`);
    if (restored) restored.focus();
  });
  heading.dataset.groupKey = groupKey;
  heading.setAttribute("aria-expanded", String(expanded));
  heading.append(
    element("span", "content-nav-group-chevron", "›"),
    element("strong", "", title),
    element("span", "content-nav-group-count", `${files.length} 项`),
  );
  const list = element("div", "content-link-list");
  list.hidden = !expanded;
  for (const file of orderedForReading(files)) list.append(navigationItem(file));
  group.append(heading, list);
  return group;
}

function renderContentList() {
  const host = $("contentList");
  const term = $("search").value.trim().toLowerCase();
  const files = state.visibleFiles.filter((file) => `${fileLabel(file.path)} ${episodeName(file.path)}`.toLowerCase().includes(term));
  const groups = [];
  const projectFiles = files.filter((file) => !episodeName(file.path));
  if (projectFiles.length) groups.push(navigationGroup("全剧", projectFiles, "project", Boolean(term)));
  for (const episode of collectEpisodes(files)) {
    groups.push(navigationGroup(episode.id, episode.files, `episode:${episode.id}`, Boolean(term)));
  }
  if (!groups.length && term) groups.push(element("p", "empty-copy", "没有找到相关内容。"));
  host.replaceChildren(...groups);
}

function scrollBehavior() {
  return typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
}

function focusDocument() {
  $("documentPane").scrollIntoView({ behavior: scrollBehavior(), block: "start" });
}

function renderTaskSummary() {
  const host = $("taskSummary");
  const [label] = creatorStatus(state.status?.lifecycle, projectRecovery(state.status));
  host.replaceChildren();
  host.hidden = !["需要修改", "需要更新", "待你确认"].includes(label);
  if (host.hidden) return;
  const title = label === "待你确认" ? "有新版内容待确认" : label === "需要更新" ? "内容需要更新" : "当前内容需要修改";
  const description = label === "待你确认" ? "请确认是否采用当前版本。" : label === "需要更新" ? "请重新整理受影响的内容。" : "请处理当前版本中的问题。";
  host.append(element("span", "kicker", "待办"), element("h2", "", title), element("p", "", description));
}

function renderExportSummary() {
  const host = $("exportSummary");
  const [label] = creatorStatus(state.status?.lifecycle, projectRecovery(state.status));
  const scope = episodeName(state.selected?.path) || collectEpisodes(state.visibleFiles)[0]?.id || "当前短剧";
  host.replaceChildren();
  host.hidden = label !== "可以导出";
  if (host.hidden) return;
  host.append(
    element("span", "kicker", "导出"),
    element("h2", "", `${scope} 可以导出`),
    button("复制导出指令", "primary", () => copyExportRequest("完整制作资料", scope)),
  );
}

function updateAssistRow() {
  const visible = [$("taskSummary"), $("exportSummary")].filter((node) => !node.hidden).length;
  $("assistRow").hidden = visible === 0;
  $("assistRow").classList.toggle("single", visible === 1);
}

async function copyExportRequest(requestName, scope) {
  const request = `请导出 ${scope} 的${requestName}。`;
  try {
    await navigator.clipboard.writeText(request);
    showNotice(`已复制：${request}`, "success");
  } catch (_error) {
    showNotice(`请复制这句话发送给创作助手：${request}`, "warning");
  }
}

function renderWorkspace() {
  renderProjectSummary();
  renderContentList();
  renderTaskSummary();
  renderExportSummary();
  updateAssistRow();
}

function appendInlineText(node, text) {
  const tokens = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).filter(Boolean);
  for (const token of tokens) {
    if (token.startsWith("`") && token.endsWith("`")) node.append(element("code", "", token.slice(1, -1)));
    else if (token.startsWith("**") && token.endsWith("**")) node.append(element("strong", "", token.slice(2, -2)));
    else node.append(document.createTextNode(token));
  }
}

function renderMarkdown(content) {
  const fragment = document.createDocumentFragment();
  // `list` holds the open <ul>/<ol>; `listKind` tracks which, so a bullet block
  // followed by a numbered block does not get merged into one list.
  let list = null;
  let listKind = null;
  // A generated prompt is meant to be selected and copied as one block, so a
  // fenced run is captured verbatim instead of being re-parsed as Markdown.
  let fence = null;
  const closeList = () => { list = null; listKind = null; };
  for (const line of content.split("\n")) {
    if (fence !== null) {
      if (/^\s*```/.test(line)) {
        const pre = element("pre", "code-block");
        pre.append(element("code", "", fence.join("\n")));
        fragment.append(pre);
        fence = null;
      } else {
        fence.push(line);
      }
      continue;
    }
    if (/^\s*```/.test(line)) { closeList(); fence = []; continue; }
    const heading = /^(#{1,4})\s+(.+)$/.exec(line);
    if (heading) {
      closeList();
      const node = element(`h${heading[1].length}`);
      appendInlineText(node, heading[2]);
      fragment.append(node);
      continue;
    }
    const bullet = /^[-*]\s+(.+)$/.exec(line);
    const ordered = /^\d+[.)]\s+(.+)$/.exec(line);
    if (bullet || ordered) {
      const kind = bullet ? "ul" : "ol";
      if (!list || listKind !== kind) { list = element(kind); listKind = kind; fragment.append(list); }
      const node = element("li");
      appendInlineText(node, (bullet || ordered)[1]);
      list.append(node);
      continue;
    }
    closeList();
    if (!line.trim()) continue;
    const quote = /^>\s?(.*)$/.exec(line);
    const node = element(quote ? "blockquote" : "p");
    appendInlineText(node, quote ? quote[1] : line);
    fragment.append(node);
  }
  // An unterminated fence still renders as a block rather than vanishing.
  if (fence !== null && fence.length) {
    const pre = element("pre", "code-block");
    pre.append(element("code", "", fence.join("\n")));
    fragment.append(pre);
  }
  return fragment;
}

function parseJsonLines(content) {
  return content.split("\n").map((line, index) => ({ line: index + 1, text: line.trim() })).filter((row) => row.text).map((row) => {
    try { return JSON.parse(row.text); }
    catch (error) { throw new Error(`第 ${row.line} 项内容无法读取：${error.message}`); }
  });
}

// Preview must survive a half-written file: one truncated record from an
// interrupted agent run should not hide every valid record around it, because
// the creator has no other way to see the file.
function readJsonLines(content) {
  return content.split("\n").map((line, index) => ({ line: index + 1, text: line.trim() })).filter((row) => row.text).map((row) => {
    try { return { line: row.line, record: JSON.parse(row.text) }; }
    catch (error) { return { line: row.line, error: error.message, text: row.text }; }
  });
}

function validateStructuredText(path, content) {
  if (/\.json$/i.test(path)) JSON.parse(content);
  else if (/\.jsonl$/i.test(path)) parseJsonLines(content);
}

function friendlyKey(key) {
  const labels = {
    id: "编号", name: "名称", title: "标题", description: "说明", summary: "概要",
    character: "人物", character_id: "人物编号", location: "场景", location_id: "场景编号",
    dialogue: "台词", action: "动作", prompt: "生成文案", role: "作用", type: "类型",
    episode_id: "剧集", scene_id: "场次", shot_id: "镜头", beat_id: "剧情节拍",
    objective: "目标", conflict: "冲突", turn: "转折", emotion: "情绪", relationship: "关系",
    costume: "服装", prop: "道具", props: "道具", lighting: "光线", camera: "摄影",
    composition: "构图", duration: "时长", start_boundary: "开始画面", end_boundary: "结束画面",
    boundary_role: "画面位置", continuity_state: "连续性", notes: "备注", value: "内容",
  };
  const normalized = String(key).toLowerCase().replace(/-/g, "_");
  if (labels[normalized]) return labels[normalized];
  if (/[\u4e00-\u9fff]/.test(String(key))) return String(key).replace(/[_-]/g, " ");
  // An unknown key keeps its own name. Collapsing every unrecognized field to
  // one generic label makes all rows on a record read identically, so the
  // creator can no longer tell which value is the id and which is the source.
  return String(key).replace(/([a-z0-9])([A-Z])/g, "$1 $2").replace(/[_-]+/g, " ").trim() || "补充信息";
}

function appendStructuredValue(node, value) {
  if (Array.isArray(value)) {
    if (!value.length) { node.textContent = "—"; return; }
    const list = element("ul", "structured-list");
    for (const item of value) {
      const row = element("li");
      appendStructuredValue(row, item);
      list.append(row);
    }
    node.append(list);
    return;
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value);
    if (!entries.length) { node.textContent = "—"; return; }
    const list = element("dl", "structured-nested");
    for (const [key, child] of entries) {
      const term = element("dt", "", friendlyKey(key));
      const detail = element("dd");
      appendStructuredValue(detail, child);
      list.append(term, detail);
    }
    node.append(list);
    return;
  }
  node.textContent = value === null || value === "" ? "—" : String(value);
}

function structuredCard(value, index) {
  const card = element("article", "structured-card");
  const projected = creatorProjection(value);
  if (projected === undefined) {
    card.append(element("p", "", "暂无可展示内容"));
    return card;
  }
  if (projected === null || typeof projected !== "object") {
    card.append(element("p", "", String(projected)));
    return card;
  }
  if (index !== null) card.append(element("span", "record-number", `第 ${index + 1} 项`));
  const list = element("dl", "structured-fields");
  for (const [key, raw] of Object.entries(projected)) {
    const term = element("dt", "", friendlyKey(key));
    const detail = element("dd");
    appendStructuredValue(detail, raw);
    list.append(term, detail);
  }
  if (!list.childNodes.length) list.append(element("dt", "", "内容"), element("dd", "", "暂无可展示内容"));
  card.append(list);
  return card;
}

function renderPreview() {
  const preview = $("preview");
  const content = $("editor").value;
  const path = state.selected?.path || "";
  preview.replaceChildren();
  try {
    if (/\.md$/i.test(path)) preview.append(renderMarkdown(content));
    else if (/\.json$/i.test(path)) preview.append(structuredCard(JSON.parse(content), null));
    else if (/\.jsonl$/i.test(path)) {
      preview.append(...readJsonLines(content).map((row, index) => (
        row.error
          ? element("div", "preview-warning", `第 ${row.line} 项内容还不完整，暂时无法展示。`)
          : structuredCard(row.record, index)
      )));
    }
    else preview.append(element("div", "plain-copy", content));
  } catch (error) {
    preview.append(element("div", "preview-warning", "这份内容还不完整，暂时无法展示。"));
  }
}

function cleanupMedia() {
  const video = $("media").querySelector("video");
  if (video) { video.pause(); video.removeAttribute("src"); video.load(); }
  const image = $("media").querySelector("img");
  if (image) image.removeAttribute("src");
  $("media").replaceChildren();
}

function setView(view) {
  state.view = view;
  const media = state.selected?.type === "media";
  $("editor").hidden = media || view !== "edit";
  $("preview").hidden = media || view !== "preview";
  $("media").hidden = !media;
  $("editMode").setAttribute("aria-pressed", String(view === "edit"));
  $("editMode").textContent = view === "edit" ? "返回阅读" : "修改正文";
  if (!media && view === "preview") renderPreview();
}

function renderMedia(info) {
  cleanupMedia();
  const shell = element("div", "media-shell");
  const stage = element("div", "media-stage");
  const mediaNode = document.createElement(info.kind === "video" ? "video" : "img");
  mediaNode.src = info.contentUrl;
  mediaNode.setAttribute("aria-label", fileLabel(state.selected.path));
  if (info.kind === "video") { mediaNode.controls = true; mediaNode.preload = "metadata"; mediaNode.playsInline = true; }
  else mediaNode.alt = fileLabel(state.selected.path);
  mediaNode.onerror = () => setMessage("媒体加载失败或文件过大", "danger");
  stage.append(mediaNode);
  const facts = element("div", "media-facts");
  facts.append(statusPill(info.lifecycle), element("span", "", info.kind === "video" ? "视频预览" : "图片预览"));
  shell.append(stage, facts);
  $("media").replaceChildren(shell);
  setMessage("媒体预览已载入。", "success");
}

function warnLeave() {
  return !state.dirty || confirm("当前修改还没有保存，确认放弃吗？");
}

function setDirty(value) {
  state.dirty = value;
  $("save").disabled = state.projectSwitching || state.saving || !value || !creatorEditable(state.selected);
  $("save").textContent = state.saving ? "保存中…" : value ? "保存修改" : "已保存";
  document.title = `${value ? "● " : ""}短剧创作台`;
  $("fileMeta").textContent = state.dirty ? "有未保存修改" : "";
}

async function openFile(file, scrollToContent = false) {
  if (!warnLeave()) return;
  const sequence = ++state.loadSequence;
  cleanupMedia();
  state.selected = file;
  state.expandedGroups.add(contentGroupKey(file));
  state.version = null;
  $("editor").value = "";
  $("editor").disabled = true;
  $("preview").classList.add("empty-document");
  $("preview").replaceChildren();
  $("filename").textContent = fileLabel(file.path);
  $("fileKind").textContent = [episodeName(file.path), CONTENT_META[creatorSection(file.path)]?.label].filter(Boolean).join(" · ") || "创作内容";
  $("editMode").disabled = true;
  setDirty(false);
  setMessage("正在载入…");
  setView("preview");
  renderContentList();
  renderExportSummary();
  updateAssistRow();
  if (scrollToContent && matchMedia("(max-width: 860px)").matches) focusDocument();
  try {
    if (file.type === "media") {
      setView("preview");
      const info = await api(`/api/media?project=${encodeURIComponent(state.project)}&path=${encodeURIComponent(file.path)}`);
      if (sequence === state.loadSequence && state.selected?.path === file.path) renderMedia(info);
      return;
    }
    const data = await api(`/api/file?project=${encodeURIComponent(state.project)}&path=${encodeURIComponent(file.path)}`);
    if (sequence !== state.loadSequence || state.selected?.path !== file.path) return;
    state.version = data.version;
    $("editor").value = data.content;
    const editable = Boolean(data.writable && creatorEditable(file));
    $("editor").disabled = !editable;
    $("editMode").disabled = !editable;
    $("preview").classList.remove("empty-document");
    setView("preview");
    setMessage("内容已载入");
  } catch (error) {
    if (sequence !== state.loadSequence) return;
    state.view = "preview";
    $("editor").hidden = true;
    $("preview").hidden = false;
    $("media").hidden = true;
    $("editMode").disabled = true;
    $("editMode").setAttribute("aria-pressed", "false");
    $("editMode").textContent = "修改正文";
    $("preview").classList.add("empty-document");
    $("preview").replaceChildren(element("p", "preview-warning", "内容无法打开"));
    setMessage(friendlyFailure(error.message), "danger");
  }
}

async function selectProject(id, preferredPath = "") {
  if (!warnLeave()) { $("projects").value = state.project; return; }
  const previousProject = state.project;
  const sequence = ++state.projectLoadSequence;
  const controls = {
    contentListInert: $("contentList").inert,
    editorDisabled: $("editor").disabled,
    editModeDisabled: $("editMode").disabled,
  };
  let committed = false;
  state.projectSwitching = true;
  $("projects").disabled = true;
  $("contentList").inert = true;
  $("editor").disabled = true;
  $("editMode").disabled = true;
  $("documentPane").setAttribute("aria-busy", "true");
  setDirty(state.dirty);
  setMessage("正在切换项目…");
  clearNotice();
  try {
    const [tree, projectStatus] = await Promise.all([
      api(`/api/tree?project=${encodeURIComponent(id)}`),
      api(`/api/status?project=${encodeURIComponent(id)}`),
    ]);
    if (sequence !== state.projectLoadSequence) return;
    const files = flatten(tree.tree);
    cleanupMedia();
    ++state.loadSequence;
    committed = true;
    state.project = id;
    state.selected = null;
    state.expandedGroups.clear();
    state.version = null;
    state.dirty = false;
    state.files = files;
    state.visibleFiles = state.files.filter((file) => creatorSection(file.path));
    state.status = projectStatus;
    $("search").value = "";
    $("filename").textContent = "正在打开创作内容…";
    $("fileKind").textContent = "创作正文";
    $("preview").classList.add("empty-document");
    $("preview").replaceChildren(document.createTextNode("正在载入第一份创作内容…"));
    const selectedOption = $("projects").selectedOptions[0];
    if (selectedOption) selectedOption.textContent = creatorTitle(projectStatus.title);
    if (tree.warnings?.length) showNotice("部分内容暂时无法读取，已展示其余创作资料。", "warning");
    renderWorkspace();
    const initial = state.visibleFiles.find((file) => file.path === preferredPath) ||
      state.visibleFiles.find((file) => /(?:^|\/)screenplay\.md$/i.test(file.path)) ||
      state.visibleFiles.find((file) => file.path.toLowerCase() === "readme.md") ||
      state.visibleFiles[0];
    if (initial) {
      $("preview").classList.remove("empty-document");
      await openFile(initial);
    } else {
      $("filename").textContent = "暂无创作内容";
      $("editor").disabled = true;
      $("editMode").disabled = true;
      $("preview").replaceChildren();
    }
  } catch (error) {
    if (sequence !== state.projectLoadSequence) return;
    if (!committed) {
      $("projects").value = previousProject || "";
      setMessage(previousProject ? "项目未切换" : "项目无法打开", "danger");
    }
    showNotice(friendlyFailure(error.message), "danger");
  } finally {
    if (sequence === state.projectLoadSequence) {
      state.projectSwitching = false;
      $("projects").disabled = false;
      $("contentList").inert = controls.contentListInert;
      $("documentPane").removeAttribute("aria-busy");
      if (!committed) {
        $("editor").disabled = controls.editorDisabled;
        $("editMode").disabled = controls.editModeDisabled;
      }
      setDirty(state.dirty);
    }
  }
}

async function save() {
  if (state.projectSwitching || !state.dirty || !state.selected || state.saving) return;
  const snapshot = { sequence: ++state.saveSequence, project: state.project, path: state.selected.path, version: state.version, content: $("editor").value };
  state.saving = true;
  setDirty(true);
  try {
    validateStructuredText(snapshot.path, snapshot.content);
    const result = await api(`/api/file?project=${encodeURIComponent(snapshot.project)}&path=${encodeURIComponent(snapshot.path)}`, {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content: snapshot.content, expectedVersion: snapshot.version }),
    });
    if (snapshot.sequence !== state.saveSequence || state.project !== snapshot.project || state.selected?.path !== snapshot.path) return;
    state.version = result.version;
    state.selected.size = new TextEncoder().encode(snapshot.content).length;
    setDirty(!savedContentIsCurrent(snapshot.content, $("editor").value));
    setMessage(`已保存 · ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`, "success");
    try {
      const refreshed = await api(`/api/status?project=${encodeURIComponent(snapshot.project)}`);
      if (state.project !== snapshot.project) return;
      state.status = refreshed;
      renderWorkspace();
    } catch (_error) { setMessage(statusRefreshFailureMessage(), "warning"); }
  } catch (error) {
    if (
      snapshot.sequence === state.saveSequence &&
      state.project === snapshot.project &&
      state.selected?.path === snapshot.path
    ) setMessage(friendlyFailure(error.message), "danger");
  }
  finally { if (snapshot.sequence === state.saveSequence) { state.saving = false; setDirty(state.dirty); } }
}

async function boot() {
  try {
    await establishSession();
    const data = await api("/api/projects");
    const options = data.projects.map((project) => {
      const option = element("option", "", project.title || "未命名短剧");
      option.value = project.id;
      return option;
    });
    $("projects").replaceChildren(...options);
    if (data.projects.length) await selectProject(data.projects[0].id);
    else showNotice("还没有发现可打开的短剧项目。", "warning");
  } catch (error) { showNotice(friendlyFailure(error.message), "danger"); }
}

function start() {
  $("projects").onchange = (event) => selectProject(event.target.value);
  $("search").oninput = renderContentList;
  $("editor").oninput = () => setDirty(true);
  $("save").onclick = save;
  $("editMode").onclick = () => setView(state.view === "edit" ? "preview" : "edit");
  document.querySelector(".brand").onclick = (event) => {
    event.preventDefault();
    scrollTo({ top: 0, behavior: scrollBehavior() });
    $("mainContent").focus({ preventScroll: true });
  };
  addEventListener("beforeunload", (event) => { if (state.dirty) { event.preventDefault(); event.returnValue = ""; } });
  addEventListener("pagehide", cleanupMedia);
  addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") { event.preventDefault(); save(); }
  });
  boot();
}

if (typeof document !== "undefined") start();
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    collectEpisodes,
    creatorProjection,
    creatorSection,
    creatorStatus,
    creatorEditable,
    creatorTitle,
    friendlyFailure,
    friendlyKey,
    orderedForReading,
    readJsonLines,
    renderMarkdown,
    savedContentIsCurrent,
    statusRefreshFailureMessage,
  };
}

#!/usr/bin/env node
/**
 * 真实环境 E2E：HTTP 网关路由（manageGateway / queryGateway）
 *
 * 覆盖这次对齐 manager-node 5.9.1 新增的能力：
 *   1. upstreamResourceType=STORAGE（云存储上游）
 *   2. 路由级 EnableSafeDomain / PathRewrite / QPSPolicy 真实落库
 *   3. updateRoute 只改一个字段时，未传字段从线上记录带回（不被静默重置）
 *   4. disableRoute / enableRoute 重写整条路由时同样保留上述字段
 *   5. 缓存刷新：DIRECT 接入的域名被本地拒绝（不再发出假成功的刷新请求）
 *   6. 反向断言：改一条路由不会动同域名下的其它路由
 *
 * 实测的两条平台约束（脚本会断言，不是 MCP 缺陷）：
 *   - 默认域（*.{region}.app.tcloudbase.com）拒绝自定义响应头：
 *     "default domain ... does not support custom header settings"
 *   - 默认域是 DIRECT 接入，没有 CloudBase 托管的 CDN/EO 缓存：原样透传时
 *     PurgeHTTPServiceCache 会「成功」返回假 TaskId，DescribeHTTPServiceCachePurgeTask
 *     随后抛 "Third Service Error"。因此 MCP 侧按域名接入方式前置校验，直接拒绝。
 *     CDN/EO 域名的成功路径需要另找一台绑了 CDN 的环境验证。
 *
 * 前置：
 *   - mcp 已构建（dist/cli.cjs）
 *   - 本机有 CloudBase 登录态（~/.config/.cloudbase/auth.json，与 CLI 共用）
 *   - 或显式提供 TENCENTCLOUD_SECRETID / TENCENTCLOUD_SECRETKEY + CLOUDBASE_ENV_ID
 *
 * 运行：
 *   CLOUDBASE_RUN_GATEWAY_E2E=1 CLOUDBASE_ENV_ID=<envId> npm run test:gateway:cloud
 *
 * 安全：只有显式设置 CLOUDBASE_RUN_GATEWAY_E2E=1 才会写数据；
 *       测试路由使用唯一路径，结束时在 finally 里删除。
 *       域名级 Protocol / Extension 不测 —— 会改到共享域名下所有路径，风险不可接受。
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { existsSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const serverPath = join(__dirname, "..", "dist", "cli.cjs");

const RUN_FLAG = process.env.CLOUDBASE_RUN_GATEWAY_E2E;
/**
 * 只读模式：只校验 schema 暴露面 + 能读到一个可写域名，不创建/修改任何东西。
 * 用于先确认登录态与环境可用，再决定是否跑写用例。
 */
const READONLY = process.env.CLOUDBASE_GATEWAY_E2E_READONLY === "1";
const envId = process.env.CLOUDBASE_ENV_ID;
const storageInstance = process.env.CLOUDBASE_E2E_STORAGE_INSTANCE || "default";
const runId = Date.now().toString(36);
const testPath = `/e2e-gw-${runId}`;

let passed = 0;
const failures = [];
const skipped = [];

function log(step, message) {
  console.log(`[${step}] ${message}`);
}

function assert(condition, message) {
  if (condition) {
    passed += 1;
    console.log(`  ✓ ${message}`);
    return;
  }
  failures.push(message);
  console.error(`  ✗ ${message}`);
}

function parse(result) {
  const text = result?.content?.[0]?.text;
  if (typeof text !== "string") {
    throw new Error(`工具没有返回文本内容: ${JSON.stringify(result).slice(0, 300)}`);
  }
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`工具返回不是 JSON: ${text.slice(0, 300)}`);
  }
}

async function callTool(client, name, args) {
  const result = await client.callTool({ name, arguments: args });
  return parse(result);
}

function pickHttpServiceDomain(routes) {
  const candidates = routes.filter(
    (item) => item.DomainType === "HTTPSERVICE" && item.Domain && item.Domain !== "*",
  );
  const preferred = candidates.find((item) => item.IsDefault === true) ?? candidates[0];
  return preferred?.Domain;
}

async function main() {
  if (RUN_FLAG !== "1" && !READONLY) {
    console.log(
      "跳过：未设置 CLOUDBASE_RUN_GATEWAY_E2E=1。该脚本会真实创建/修改/删除路由与刷新缓存。",
    );
    process.exit(0);
  }
  if (!existsSync(serverPath)) {
    console.error(`找不到 ${serverPath}，先在 mcp/ 下执行 npm run build`);
    process.exit(1);
  }

  const client = new Client({ name: "gateway-e2e", version: "1.0.0" }, { capabilities: {} });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [serverPath],
    env: { ...process.env },
  });

  let routeCreated = false;
  let domain;

  try {
    await client.connect(transport);
    const tools = await client.listTools();
    const names = tools.tools.map((tool) => tool.name);
    assert(names.includes("manageGateway") && names.includes("queryGateway"), "MCP 暴露网关工具");

    const manageSchema = tools.tools.find((tool) => tool.name === "manageGateway").inputSchema;
    assert(
      manageSchema.properties?.upstreamResourceType?.enum?.includes("STORAGE"),
      "schema 的 upstreamResourceType 含 STORAGE",
    );
    assert(
      manageSchema.properties?.action?.enum?.includes("purgeCache"),
      "schema 的 action 含 purgeCache",
    );

    // ---- 0. 选一个可写的 HTTP 服务域名 ----
    const listed = await callTool(client, "queryGateway", { action: "listRoutes" });
    assert(listed.success === true, "listRoutes 成功");
    const beforeRoutes = listed.data.routes ?? [];
    domain = pickHttpServiceDomain(beforeRoutes);
    assert(Boolean(domain), `找到 HTTPSERVICE 域名：${domain}`);
    if (!domain) {
      throw new Error("没有可用的 HTTPSERVICE 域名，无法继续");
    }
    const baselineCount = beforeRoutes.length;
    log("0", `环境 ${envId ?? "(登录态默认)"}，域名 ${domain}，现有路由 ${baselineCount} 条`);

    // 写之前留一份完整快照：万一后端把 Routes 当成整体替换，可据此重建。
    const backupFile = join(process.cwd(), `gateway-route-backup-${runId}.json`);
    writeFileSync(backupFile, JSON.stringify(beforeRoutes, null, 2), "utf8");
    log("0", `变更前路由快照已存：${backupFile}`);

    if (READONLY) {
      const byType = beforeRoutes.reduce((acc, item) => {
        acc[item.UpstreamResourceType] = (acc[item.UpstreamResourceType] ?? 0) + 1;
        return acc;
      }, {});
      log("readonly", `上游类型分布 ${JSON.stringify(byType)}`);
      assert(true, "只读模式：schema 与读接口均正常，未写任何数据");
      return;
    }

    // ---- 1. 建一条 STORAGE 路由，同时带上 CORS/重写/限频 ----
    // 注：Extension.HeadersHandler 在默认域上会被后端拒绝
    //    （"default domain ... does not support custom header settings"），
    //    所以自定义头单独在步骤 6 里验证这条平台约束，不混进主用例。
    const created = await callTool(client, "manageGateway", {
      action: "createRoute",
      domain,
      path: testPath,
      targetName: storageInstance,
      upstreamResourceType: "STORAGE",
      enableSafeDomain: false,
      pathRewrite: { prefix: "/assets" },
      qpsPolicy: { total: 120, perClient: { limitBy: "ClientIP", limitValue: 12 } },
    });
    routeCreated = created.success === true;
    assert(created.success === true, `createRoute(STORAGE) 成功：${created.message?.slice(0, 80)}`);
    if (!created.success) {
      throw new Error(`createRoute 失败：${created.message}`);
    }

    // ---- 2. 回读：字段真的落库了 ----
    const readBack = await callTool(client, "queryGateway", { action: "getRoute", domain, path: testPath });
    const route = readBack.data?.route;
    assert(Boolean(route), "getRoute 能查到新建路由");
    assert(route?.UpstreamResourceType === "STORAGE", `落库上游类型 = STORAGE（实际 ${route?.UpstreamResourceType}）`);
    assert(route?.UpstreamResourceName === storageInstance, "落库上游名与入参一致");
    assert(route?.EnableSafeDomain === false, `落库 EnableSafeDomain=false（实际 ${route?.EnableSafeDomain}）`);
    assert(
      route?.PathRewrite?.Prefix === "/assets",
      `落库 PathRewrite.Prefix=/assets（实际 ${JSON.stringify(route?.PathRewrite)}）`,
    );
    assert(
      route?.QPSPolicy?.QPSTotal === 120 &&
        route?.QPSPolicy?.QPSPerClient?.LimitValue === 12,
      `落库 QPSPolicy 总计 120 / 单端 12（实际 ${JSON.stringify(route?.QPSPolicy)}）`,
    );

    // ---- 3. updateRoute 只改限频，其余字段必须保留 ----
    const updated = await callTool(client, "manageGateway", {
      action: "updateRoute",
      domain,
      path: testPath,
      targetName: storageInstance,
      upstreamResourceType: "STORAGE",
      qpsPolicy: { total: 60 },
    });
    assert(updated.success === true, `updateRoute 成功：${updated.message?.slice(0, 80)}`);
    const afterUpdate = await callTool(client, "queryGateway", { action: "getRoute", domain, path: testPath });
    const r2 = afterUpdate.data?.route;
    assert(r2?.QPSPolicy?.QPSTotal === 60, `限频已改为 60（实际 ${r2?.QPSPolicy?.QPSTotal}）`);
    assert(r2?.EnableSafeDomain === false, `未传的 EnableSafeDomain 被保留（实际 ${r2?.EnableSafeDomain}）`);
    assert(r2?.PathRewrite?.Prefix === "/assets", `未传的 PathRewrite 被保留（实际 ${JSON.stringify(r2?.PathRewrite)}）`);

    // ---- 4. disableRoute / enableRoute 不能把配置清掉 ----
    await callTool(client, "manageGateway", { action: "disableRoute", domain, path: testPath });
    const afterDisable = await callTool(client, "queryGateway", { action: "getRoute", domain, path: testPath });
    const r3 = afterDisable.data?.route;
    assert(r3?.Enable === false, `disableRoute 后 Enable=false（实际 ${r3?.Enable}）`);
    assert(r3?.EnableSafeDomain === false, "禁用后 EnableSafeDomain 仍在");
    assert(r3?.PathRewrite?.Prefix === "/assets", "禁用后 PathRewrite 仍在");
    assert(r3?.QPSPolicy?.QPSTotal === 60, "禁用后限频仍在");

    await callTool(client, "manageGateway", { action: "enableRoute", domain, path: testPath });
    const afterEnable = await callTool(client, "queryGateway", { action: "getRoute", domain, path: testPath });
    const r4 = afterEnable.data?.route;
    assert(r4?.Enable === true, `enableRoute 后 Enable=true（实际 ${r4?.Enable}）`);
    assert(r4?.QPSPolicy?.QPSTotal === 60, "启用后限频仍在");

    // ---- 5. 自定义头在默认域上应被拒绝（平台约束，不是 MCP 缺陷） ----
    const extensionAttempt = await callTool(client, "manageGateway", {
      action: "updateRoute",
      domain,
      path: testPath,
      targetName: storageInstance,
      upstreamResourceType: "STORAGE",
      extension: {
        headersHandler: {
          responseHeadersToAdd: [{ key: "X-E2E-Path", value: "storage-route" }],
        },
      },
    });
    const extensionMessage = String(extensionAttempt.message ?? "");
    assert(
      extensionAttempt.success === false && /custom header/i.test(extensionMessage),
      `默认域拒绝自定义头（平台约束）：${extensionMessage.slice(0, 90)}`,
    );

    // ---- 6. 改一条路由不能影响同域名下的其它路由 ----
    const afterAll = await callTool(client, "queryGateway", { action: "listRoutes" });
    const totalAfter = (afterAll.data.routes ?? []).length;
    assert(
      totalAfter === baselineCount + 1,
      `同域名其它路由未被删（基线 ${baselineCount} + 新增 1 = ${baselineCount + 1}，实际 ${totalAfter}）`,
    );

    // ---- 7. 缓存刷新：默认域是 DIRECT 接入，没有 CDN/EO 缓存，必须被本地拒绝 ----
    // 反向判据：不拦的话 PurgeHTTPServiceCache 会「成功」返回一个假 TaskId，
    // 随后 DescribeHTTPServiceCachePurgeTask 抛 Third Service Error。
    const purge = await callTool(client, "manageGateway", {
      action: "purgeCache",
      domain,
      purgeType: "PURGE_URL",
      targets: [`https://${domain}${testPath}/probe.txt`],
    });
    assert(
      purge.success === false && /CDN/i.test(String(purge.message ?? "")),
      `DIRECT 域拒绝缓存刷新并说明原因：${String(purge.message).split("\n")[0].slice(0, 80)}`,
    );
    assert(!purge.data?.taskId, "DIRECT 域不会返回假的 TaskId");

    const tasks = await callTool(client, "queryGateway", {
      action: "cachePurgeTask",
      domain,
    });
    assert(
      tasks.success === false && /CDN/i.test(String(tasks.message ?? "")),
      `DIRECT 域拒绝缓存任务查询：${String(tasks.message).split("\n")[0].slice(0, 80)}`,
    );
  } catch (error) {
    failures.push(`异常中断：${error instanceof Error ? error.message : String(error)}`);
    console.error(error);
  } finally {
    // ---- 7. 清理 ----
    if (routeCreated && domain) {
      try {
        const removed = await callTool(client, "manageGateway", {
          action: "deleteRoute",
          domain,
          path: testPath,
        });
        assert(removed.success === true, "清理：deleteRoute 成功");
        const afterCleanup = await callTool(client, "queryGateway", { action: "getRoute", domain, path: testPath });
        assert(!afterCleanup.data?.route, "清理：测试路由已不存在");
      } catch (error) {
        failures.push(`清理失败，请手动删除 ${domain}${testPath}：${error instanceof Error ? error.message : String(error)}`);
      }
    }
    await transport.close().catch(() => {});
  }

  console.log(`\n结果：${passed} 项通过，${failures.length} 项失败${skipped.length ? `，${skipped.length} 项跳过` : ""}`);
  skipped.forEach((item) => console.warn(`  ⚠ ${item}`));
  if (failures.length) {
    failures.forEach((item) => console.error(`  - ${item}`));
    process.exit(1);
  }
}

main();

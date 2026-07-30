import { z } from "zod";
import {
  getCloudBaseManager,
  getEnvId,
  logCloudBaseResult,
} from "../cloudbase-manager.js";
import { ExtendedMcpServer } from "../server.js";
import {
  rankGatewayAccessUrls,
  toAccessUrlEnvelope,
  type GatewayRouteUrlCandidate,
} from "../utils/gateway-access-urls.js";
import { jsonContent } from "../utils/json-content.js";

const QUERY_GATEWAY_ACTIONS = [
  "listRoutes",
  "getRoute",
  "listCustomDomains",
] as const;

const MANAGE_GATEWAY_ACTIONS = [
  "createRoute",
  "updateRoute",
  "deleteRoute",
  "bindCustomDomain",
  "deleteCustomDomain",
] as const;

const UPSTREAM_RESOURCE_TYPES = [
  "SCF",
  "WEB_SCF",
  "CBR",
  "STATIC_STORE",
  "LH",
] as const;

type QueryGatewayAction = (typeof QUERY_GATEWAY_ACTIONS)[number];
type ManageGatewayAction = (typeof MANAGE_GATEWAY_ACTIONS)[number];
type UpstreamResourceType = (typeof UPSTREAM_RESOURCE_TYPES)[number];

type GatewayToolEnvelope = {
  success: boolean;
  data: Record<string, unknown>;
  message: string;
  nextActions?: Array<{
    tool: string;
    action: string;
    reason: string;
  }>;
};

type QueryGatewayInput = {
  action: QueryGatewayAction;
  targetName?: string;
  routeId?: string;
  path?: string;
  domain?: string;
};

type ManageGatewayInput = {
  action: ManageGatewayAction;
  targetName?: string;
  path?: string;
  upstreamResourceType?: UpstreamResourceType;
  auth?: boolean;
  enablePathTransmission?: boolean;
  route?: {
    path?: string;
    serviceName?: string;
    upstreamResourceType?: UpstreamResourceType;
    auth?: boolean;
    enablePathTransmission?: boolean;
  };
  domain?: string;
  certificateId?: string;
};

type FlatRoute = {
  Domain: string;
  DomainType?: string;
  AccessType?: string;
  IsDefault?: boolean;
  Path?: string;
  UpstreamResourceType?: string;
  UpstreamResourceName?: string;
  EnableAuth?: boolean;
  RouteId?: string;
  [key: string]: unknown;
};

function normalizeAccessPath(path: string | undefined): string {
  if (!path) {
    return "/";
  }

  return path.startsWith("/") ? path : `/${path}`;
}

export function registerGatewayTools(server: ExtendedMcpServer) {
  const cloudBaseOptions = server.cloudBaseOptions;
  const getManager = () => getCloudBaseManager({ cloudBaseOptions });
  const resolveEnvId = () => getEnvId(cloudBaseOptions);

  const buildEnvelope = (
    data: Record<string, unknown>,
    message: string,
    nextActions?: GatewayToolEnvelope["nextActions"],
  ): GatewayToolEnvelope => ({
    success: true,
    data,
    message,
    ...(nextActions?.length ? { nextActions } : {}),
  });

  const buildErrorEnvelope = (error: unknown) => ({
    success: false,
    data: {},
    message: error instanceof Error ? error.message : String(error),
  });

  const withEnvelope = async (handler: () => Promise<GatewayToolEnvelope>) => {
    try {
      return jsonContent(await handler());
    } catch (error) {
      return jsonContent(buildErrorEnvelope(error));
    }
  };

  const listHttpServiceRoutes = async (domain?: string) => {
    const cloudbase = await getManager();
    const result = await cloudbase.env.describeHttpServiceRoute({
      EnvId: await resolveEnvId(),
      Limit: 1000,
      ...(domain
        ? {
            Filters: [
              {
                Name: "Domain",
                Values: [domain],
              },
            ],
          }
        : {}),
    });
    logCloudBaseResult(server.logger, result);
    return result;
  };

  const flattenRoutes = (result: {
    Domains?: Array<{
      Domain?: string;
      DomainType?: string;
      AccessType?: string;
      IsDefault?: boolean;
      Routes?: Array<object>;
    }>;
  }): FlatRoute[] =>
    (result.Domains ?? []).flatMap((domainItem) =>
      (domainItem.Routes ?? []).map((route) => ({
        Domain: domainItem.Domain ?? "",
        DomainType: domainItem.DomainType,
        AccessType: domainItem.AccessType,
        IsDefault: domainItem.IsDefault,
        ...(route as Record<string, unknown>),
      })),
    );

  const buildRouteUrls = (routes: FlatRoute[]) => {
    const candidates: GatewayRouteUrlCandidate[] = routes.map((route) => ({
      Domain: route.Domain,
      Path: route.Path,
      IsDefault: route.IsDefault,
      UpstreamResourceType: route.UpstreamResourceType,
      UpstreamResourceName: route.UpstreamResourceName,
    }));
    return rankGatewayAccessUrls(candidates).map((item) => item.url);
  };

  const buildAccessUrlFields = (routes: FlatRoute[]) => {
    const candidates: GatewayRouteUrlCandidate[] = routes.map((route) => ({
      Domain: route.Domain,
      Path: route.Path,
      IsDefault: route.IsDefault,
      UpstreamResourceType: route.UpstreamResourceType,
      UpstreamResourceName: route.UpstreamResourceName,
    }));
    const envelope = toAccessUrlEnvelope(rankGatewayAccessUrls(candidates));
    return {
      ...(envelope.accessUrl ? { accessUrl: envelope.accessUrl } : {}),
      accessUrls: envelope.accessUrls,
      ...(envelope.accessUrlSource
        ? { accessUrlSource: envelope.accessUrlSource }
        : {}),
    };
  };

  const resolveDefaultHttpDomain = async () => {
    const routeInfo = await listHttpServiceRoutes();
    const domains = routeInfo.Domains ?? [];
    const defaultCandidates = domains.filter(
      (item) => item.IsDefault === true && item.Domain,
    );
    const preferred =
      defaultCandidates.find(
        (item) => item.Enable !== false && item.Status === "SUCCESS",
      ) ??
      defaultCandidates.find((item) => item.Enable !== false) ??
      defaultCandidates[0];

    if (!preferred?.Domain) {
      throw new Error(
        "环境默认 HTTP 访问域名未就绪或未开通。请先在控制台开通 HTTP 访问服务，或用 queryGateway(action=\"listRoutes\") 确认 Domains 中是否存在 IsDefault=true 的域名；也可以显式传入 domain 后重试 createRoute/updateRoute/deleteRoute。",
      );
    }

    return preferred.Domain;
  };

  const resolveRouteDomain = async (preferredDomain?: string) => {
    if (preferredDomain) {
      return preferredDomain;
    }
    return resolveDefaultHttpDomain();
  };

  const resolveUpstreamResourceType = (input: {
    upstreamResourceType?: UpstreamResourceType;
    routeUpstreamResourceType?: UpstreamResourceType;
  }): UpstreamResourceType => {
    const resolved =
      input.routeUpstreamResourceType ?? input.upstreamResourceType;
    if (resolved) {
      return resolved;
    }

    throw new Error(
      "必须提供 upstreamResourceType（或 route.upstreamResourceType）：" +
        "WEB_SCF=HTTP云函数，SCF=Event云函数，CBR=云托管，STATIC_STORE=静态托管，LH=轻量应用服务器。" +
        "禁止仅凭 targetName/serviceName 推断上游类型。",
    );
  };

  const normalizeRoutePayload = async (
    input: ManageGatewayInput,
  ): Promise<{
    EnvId: string;
    Domain: {
      Domain: string;
      Routes: Array<{
        Path: string;
        UpstreamResourceType: UpstreamResourceType;
        UpstreamResourceName: string;
        EnableAuth?: boolean;
        EnablePathTransmission?: boolean;
      }>;
    };
    resolved: {
      domain: string;
      path: string;
      upstreamResourceType: UpstreamResourceType;
      upstreamResourceName: string;
      enableAuth?: boolean;
      enablePathTransmission?: boolean;
    };
  }> => {
    const upstreamResourceName =
      input.route?.serviceName ?? input.targetName;
    if (!upstreamResourceName) {
      throw new Error(
        "必须提供 targetName 或 route.serviceName 作为上游资源名称：" +
          "云函数名、云托管服务名，或静态托管实例名（常见为 staticstore）。",
      );
    }

    const upstreamResourceType = resolveUpstreamResourceType({
      upstreamResourceType: input.upstreamResourceType,
      routeUpstreamResourceType: input.route?.upstreamResourceType,
    });

    const path = normalizeAccessPath(
      input.route?.path ?? input.path ?? `/${upstreamResourceName}`,
    );
    const domain = await resolveRouteDomain(input.domain);
    const enableAuth =
      input.route?.auth !== undefined
        ? input.route.auth
        : input.auth !== undefined
          ? input.auth
          : undefined;
    const enablePathTransmission =
      input.route?.enablePathTransmission !== undefined
        ? input.route.enablePathTransmission
        : input.enablePathTransmission !== undefined
          ? input.enablePathTransmission
          : undefined;

    const route: {
      Path: string;
      UpstreamResourceType: UpstreamResourceType;
      UpstreamResourceName: string;
      EnableAuth?: boolean;
      EnablePathTransmission?: boolean;
    } = {
      Path: path,
      UpstreamResourceType: upstreamResourceType,
      UpstreamResourceName: upstreamResourceName,
      EnableAuth: enableAuth,
    };
    if (enablePathTransmission !== undefined) {
      route.EnablePathTransmission = enablePathTransmission;
    }

    return {
      EnvId: await resolveEnvId(),
      Domain: {
        Domain: domain,
        Routes: [route],
      },
      resolved: {
        domain,
        path,
        upstreamResourceType,
        upstreamResourceName,
        enableAuth,
        enablePathTransmission,
      },
    };
  };

  const routeMutationNextActions = (
    targetName: string,
  ): GatewayToolEnvelope["nextActions"] => [
    {
      tool: "queryGateway",
      action: "getRoute",
      reason: "等待 30 秒到 3 分钟后再确认访问入口是否已生效",
    },
    {
      tool: "queryPermissions",
      action: "getResourcePermission",
      reason:
        "确认函数安全规则是否允许预期访问方；网关 EnableAuth/auth=false 不等于函数已允许匿名访问",
    },
    {
      tool: "managePermissions",
      action: "updateResourcePermission",
      reason:
        "只有在确认需要匿名或浏览器直连访问时，才按实际安全要求更新函数权限",
    },
  ];

  const handleQueryGateway = async (
    input: QueryGatewayInput,
  ): Promise<GatewayToolEnvelope> => {
    switch (input.action) {
      case "listCustomDomains": {
        const result = await listHttpServiceRoutes();
        const customDomains = (result.Domains ?? []).filter(
          (item) => item.IsDefault !== true,
        );

        return buildEnvelope(
          {
            action: input.action,
            domains: customDomains,
            total: customDomains.length,
            raw: result,
          },
          `已获取 ${customDomains.length} 个自定义域名`,
        );
      }
      case "listRoutes": {
        const result = await listHttpServiceRoutes(input.domain);
        const routes = flattenRoutes(result);

        return buildEnvelope(
          {
            action: input.action,
            routes,
            urls: buildRouteUrls(routes),
            ...buildAccessUrlFields(routes),
            total: result.TotalCount ?? routes.length,
            raw: result,
          },
          `已获取 ${result.TotalCount ?? routes.length} 条 HTTP 路由`,
        );
      }
      case "getRoute": {
        if (!input.routeId && !input.targetName && !input.path) {
          throw new Error(
            "action=getRoute 时至少需要提供 routeId、targetName 或 path",
          );
        }

        const result = await listHttpServiceRoutes(input.domain);
        const normalizedPath = input.path
          ? normalizeAccessPath(input.path)
          : undefined;
        const matches = flattenRoutes(result).filter((item) => {
          if (input.routeId && item.RouteId !== input.routeId) {
            return false;
          }
          if (input.domain && item.Domain !== input.domain) {
            return false;
          }
          if (
            normalizedPath &&
            normalizeAccessPath(String(item.Path ?? "")) !== normalizedPath
          ) {
            return false;
          }
          if (
            input.targetName &&
            item.UpstreamResourceName !== input.targetName
          ) {
            return false;
          }
          return Boolean(input.routeId || input.targetName || normalizedPath);
        });

        const route = matches.length === 1 ? matches[0] : null;
        const urls = buildRouteUrls(matches);

        return buildEnvelope(
          {
            action: input.action,
            routeId: input.routeId ?? null,
            targetName: input.targetName ?? null,
            path: normalizedPath ?? null,
            domain: input.domain ?? null,
            route,
            routes: matches,
            total: matches.length,
            urls,
            ...buildAccessUrlFields(matches),
            raw: result,
          },
          matches.length === 0
            ? "未找到对应路由"
            : matches.length === 1
              ? "已获取路由详情"
              : `匹配到 ${matches.length} 条路由，请补充 path 或 domain 精确定位`,
          [
            {
              tool: "manageGateway",
              action: "createRoute",
              reason: "为该目标新增 Domain/Route 访问路径",
            },
          ],
        );
      }
      default:
        throw new Error(`不支持的操作类型: ${input.action}`);
    }
  };

  const handleManageGateway = async (
    input: ManageGatewayInput,
  ): Promise<GatewayToolEnvelope> => {
    switch (input.action) {
      case "createRoute": {
        const cloudbase = await getManager();
        const payload = await normalizeRoutePayload(input);
        let result;
        try {
          result = await cloudbase.env.createHttpServiceRoute({
            EnvId: payload.EnvId,
            Domain: payload.Domain,
          } as any);
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : String(err);
          if (message.includes("An error has occurred")) {
            let hint =
              "为目标资源配置访问路由失败（后端内部错误）。请确保：1) 目标云函数已成功创建并处于 Active 状态；2) 环境默认 HTTP 域名已完成初始化（IsDefault）；3) 该访问路径未被占用。";
            if (
              payload.resolved.upstreamResourceType === "WEB_SCF" ||
              payload.resolved.upstreamResourceType === "SCF"
            ) {
              hint +=
                "此外注意：HTTP 云函数必须用 upstreamResourceType=WEB_SCF，Event 云函数必须用 SCF；互标会导致此错误。";
            }
            throw new Error(`${hint} 原始错误：${message}`);
          }
          throw err;
        }
        logCloudBaseResult(server.logger, result);

        return buildEnvelope(
          {
            action: input.action,
            model: "httpServiceRoute",
            targetName: payload.resolved.upstreamResourceName,
            domain: payload.resolved.domain,
            path: payload.resolved.path,
            upstreamResourceType: payload.resolved.upstreamResourceType,
            upstreamResourceName: payload.resolved.upstreamResourceName,
            auth: payload.resolved.enableAuth ?? null,
            enablePathTransmission:
              payload.resolved.enablePathTransmission ?? null,
            accessUrl: `https://${payload.resolved.domain}${payload.resolved.path}`,
            accessUrls: [`https://${payload.resolved.domain}${payload.resolved.path}`],
            accessUrlSource:
              input.domain && input.domain === payload.resolved.domain
                ? "gateway.custom"
                : "gateway.default",
            raw: result,
          },
          `已为目标 ${payload.resolved.upstreamResourceName} 在域名 ${payload.resolved.domain} 创建路由 ${payload.resolved.path}（${payload.resolved.upstreamResourceType}）` +
            (payload.resolved.enablePathTransmission === true
              ? "；已开启路径透传（后端收到完整请求路径）"
              : payload.resolved.enablePathTransmission === false
                ? "；路径透传关闭（网关会剥掉触发路径前缀后再转发给后端）"
                : "；路径透传未显式设置（平台默认 false，会剥掉触发路径前缀）") +
            `。注意：路由配置传播通常需要等待 30 秒到 3 分钟，请勿立即访问。该操作只创建网关入口，不会自动放开上游权限；若上游是云函数且需要匿名或浏览器直接访问，请继续检查函数资源权限。`,
          routeMutationNextActions(payload.resolved.upstreamResourceName),
        );
      }
      case "updateRoute": {
        const cloudbase = await getManager();
        const payload = await normalizeRoutePayload(input);
        const result = await cloudbase.env.modifyHttpServiceRoute({
          EnvId: payload.EnvId,
          Domain: payload.Domain,
        } as any);
        logCloudBaseResult(server.logger, result);

        return buildEnvelope(
          {
            action: input.action,
            model: "httpServiceRoute",
            domain: payload.resolved.domain,
            path: payload.resolved.path,
            upstreamResourceType: payload.resolved.upstreamResourceType,
            upstreamResourceName: payload.resolved.upstreamResourceName,
            auth: payload.resolved.enableAuth ?? null,
            enablePathTransmission:
              payload.resolved.enablePathTransmission ?? null,
            accessUrl: `https://${payload.resolved.domain}${payload.resolved.path}`,
            accessUrls: [`https://${payload.resolved.domain}${payload.resolved.path}`],
            accessUrlSource:
              input.domain && input.domain === payload.resolved.domain
                ? "gateway.custom"
                : "gateway.default",
            raw: result,
          },
          `HTTP 路由更新成功（${payload.resolved.domain}${payload.resolved.path}` +
            (payload.resolved.enablePathTransmission === true
              ? "，路径透传=开启"
              : payload.resolved.enablePathTransmission === false
                ? "，路径透传=关闭"
                : "") +
            `）`,
          routeMutationNextActions(payload.resolved.upstreamResourceName),
        );
      }
      case "deleteRoute": {
        const routePath = input.route?.path ?? input.path;
        if (!routePath) {
          throw new Error("action=deleteRoute 时必须提供 route.path 或 path");
        }
        const cloudbase = await getManager();
        const domain = await resolveRouteDomain(input.domain);
        const normalizedPath = normalizeAccessPath(routePath);
        const result = await cloudbase.env.deleteHttpServiceRoute({
          EnvId: await resolveEnvId(),
          Domain: domain,
          Paths: [normalizedPath],
        } as any);
        logCloudBaseResult(server.logger, result);

        return buildEnvelope(
          {
            action: input.action,
            model: "httpServiceRoute",
            domain,
            path: normalizedPath,
            raw: result,
          },
          "HTTP 路由删除成功",
        );
      }
      case "bindCustomDomain": {
        if (!input.domain || !input.certificateId) {
          throw new Error(
            "action=bindCustomDomain 时必须提供 domain 和 certificateId",
          );
        }
        const cloudbase = await getManager();
        const result = await cloudbase.env.bindCustomDomain({
          EnvId: await resolveEnvId(),
          Domain: {
            Domain: input.domain,
            CertId: input.certificateId,
          },
        } as any);
        logCloudBaseResult(server.logger, result);

        return buildEnvelope(
          {
            action: input.action,
            domain: input.domain,
            certificateId: input.certificateId,
            raw: result,
          },
          "自定义域名绑定成功",
        );
      }
      case "deleteCustomDomain": {
        if (!input.domain) {
          throw new Error("action=deleteCustomDomain 时必须提供 domain");
        }
        const cloudbase = await getManager();
        const result = await cloudbase.env.deleteCustomDomain({
          EnvId: await resolveEnvId(),
          Domain: input.domain,
        });
        logCloudBaseResult(server.logger, result);

        return buildEnvelope(
          {
            action: input.action,
            domain: input.domain,
            raw: result,
          },
          "自定义域名删除成功",
        );
      }
      default:
        throw new Error(`不支持的操作类型: ${input.action}`);
    }
  };

  server.registerTool?.(
    "queryGateway",
    {
      title: "查询 CloudBase 网关",
      description:
        "CloudBase HTTP 网关统一只读入口（Domain/Route）。查询域名下路径路由及其上游：" +
        "WEB_SCF/SCF=云函数，CBR=云托管，STATIC_STORE=静态托管，LH=轻量应用服务器。" +
        "主键为 Domain + Path；listRoutes / getRoute / listCustomDomains。",
      inputSchema: {
        action: z
          .enum(QUERY_GATEWAY_ACTIONS)
          .describe("只读操作类型：listRoutes、getRoute、listCustomDomains"),
        targetName: z
          .string()
          .optional()
          .describe(
            "上游资源名过滤（UpstreamResourceName）：云函数名、云托管服务名，或静态托管实例名（常见 staticstore）。",
          ),
        routeId: z.string().optional().describe("路由 ID。getRoute 时可选"),
        path: z
          .string()
          .optional()
          .describe("路由路径。getRoute / listRoutes 过滤时可选"),
        domain: z
          .string()
          .optional()
          .describe("域名。getRoute / listRoutes 过滤时可选"),
      },
      annotations: {
        readOnlyHint: true,
        openWorldHint: true,
        category: "gateway",
      },
    },
    async (input: QueryGatewayInput) =>
      withEnvelope(() => handleQueryGateway(input)),
  );

  server.registerTool?.(
    "manageGateway",
    {
      title: "管理 CloudBase 网关",
      description:
        "CloudBase HTTP 网关统一写入口（Domain/Route）。createRoute/updateRoute/deleteRoute 把域名下的 path 转到上游；未传 domain 时用 IsDefault 默认域名。" +
        "上游类型只用一个参数 upstreamResourceType（也可写在 route.upstreamResourceType，route 优先）：" +
        "WEB_SCF=HTTP云函数，SCF=Event云函数，CBR=云托管，STATIC_STORE=静态托管，LH=轻量应用服务器；" +
        "配合 targetName 或 route.serviceName（云函数名/云托管服务名/静态托管实例名，常见 staticstore）。" +
        "createRoute 只建网关入口，不改上游权限。" +
        "enablePathTransmission：默认 false 剥触发路径前缀；true 透传完整路径（CBR 多路由、WEB_SCF 自管子路径常需 true；STATIC_STORE 自定义触发路径映射站点根通常 false）。" +
        "⚠️ SSL 自定义域名用 bindCustomDomain；CORS/安全域名用 envDomainManagement。",
      inputSchema: {
        action: z
          .enum(MANAGE_GATEWAY_ACTIONS)
          .describe(
            "写操作：createRoute/updateRoute/deleteRoute 管理路由；bindCustomDomain/deleteCustomDomain 管理自定义域名。" +
              "createRoute/updateRoute 必须提供 upstreamResourceType。",
          ),
        targetName: z
          .string()
          .optional()
          .describe(
            "上游资源名称（UpstreamResourceName），与 route.serviceName 二选一（route 优先）。" +
              "云函数=函数名；云托管=服务名；静态托管=实例名（常见 staticstore）。不会自动推断上游类型。",
          ),
        path: z
          .string()
          .optional()
          .describe(
            "触发路径（网关匹配前缀），默认 /{上游名}。例：云函数 /api/hello、云托管 /api、静态托管 / 或 /app。" +
              "只建网关入口；与 enablePathTransmission 共同决定上游实际收到的路径。",
          ),
        upstreamResourceType: z
          .enum(UPSTREAM_RESOURCE_TYPES)
          .optional()
          .describe(
            "上游类型（与 route.upstreamResourceType 二选一，route 优先）。" +
              "WEB_SCF=HTTP云函数，SCF=Event云函数，CBR=云托管，STATIC_STORE=静态托管，LH=轻量应用服务器。" +
              "createRoute/updateRoute 必填其一；勿把 manageFunctions 的 type=HTTP|Event 传到本字段。",
          ),
        auth: z
          .boolean()
          .optional()
          .describe(
            "网关路径鉴权（EnableAuth）。匿名/浏览器公网访问通常 false。" +
              "只控制网关入口；云函数安全规则、云托管鉴权、静态托管权限需各自工具另行配置。",
          ),
        enablePathTransmission: z
          .boolean()
          .optional()
          .describe(
            "路径透传（EnablePathTransmission），平台默认 false。例 path=/api 且请求 /api/users：" +
              "false→上游收到 /users；true→上游收到 /api/users。" +
              "CBR 云托管（Express 等自管子路由）与 WEB_SCF 多路径函数常需 true；" +
              "STATIC_STORE 把触发路径映射到站点根目录（如 /app → 托管 /）时通常 false；" +
              "单入口/根路径处理保持 false。也可用 route.enablePathTransmission（route 优先）。",
          ),
        route: z
          .object({
            path: z.string().optional(),
            serviceName: z
              .string()
              .optional()
              .describe(
                "上游实例名：云函数名 / 云托管服务名 / 静态托管实例名（常见 staticstore）/ LH 实例。优先于顶层 targetName。",
              ),
            upstreamResourceType: z
              .enum(UPSTREAM_RESOURCE_TYPES)
              .optional()
              .describe(
                "同顶层 upstreamResourceType。route 内设置时优先于顶层。",
              ),
            auth: z.boolean().optional(),
            enablePathTransmission: z
              .boolean()
              .optional()
              .describe(
                "同顶层 enablePathTransmission。route 内设置时优先于顶层。",
              ),
          })
          .optional()
          .describe(
            "路由对象（可选写法）。例：云函数 {upstreamResourceType:\"WEB_SCF\",serviceName:\"fn\",path:\"/api\"}；" +
              "云托管 {upstreamResourceType:\"CBR\",serviceName:\"svc\",path:\"/api\"}；" +
              "静态托管 {upstreamResourceType:\"STATIC_STORE\",serviceName:\"staticstore\",path:\"/\"}。",
          ),
        domain: z
          .string()
          .optional()
          .describe(
            "域名。省略时自动使用环境 IsDefault 默认 HTTP 域名；自定义域名场景请显式传入",
          ),
        certificateId: z
          .string()
          .optional()
          .describe("证书 ID。bindCustomDomain 时必填"),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: true,
        category: "gateway",
      },
    },
    async (input: ManageGatewayInput) =>
      withEnvelope(() => handleManageGateway(input)),
  );
}

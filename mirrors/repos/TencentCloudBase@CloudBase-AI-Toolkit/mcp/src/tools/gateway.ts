import { z } from "zod";
import {
  getCloudBaseManager,
  getEnvId,
  logCloudBaseResult,
} from "../cloudbase-manager.js";
import { ExtendedMcpServer } from "../server.js";
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
type GatewayTargetType = "function";
type UpstreamResourceType = (typeof UPSTREAM_RESOURCE_TYPES)[number];
type FunctionRouteType = "Event" | "HTTP";

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
  targetType?: GatewayTargetType;
  targetName?: string;
  routeId?: string;
  path?: string;
  domain?: string;
};

type ManageGatewayInput = {
  action: ManageGatewayAction;
  targetType?: GatewayTargetType;
  targetName?: string;
  path?: string;
  type?: FunctionRouteType;
  auth?: boolean;
  route?: {
    path?: string;
    serviceName?: string;
    upstreamResourceType?: UpstreamResourceType;
    auth?: boolean;
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

  const buildRouteUrls = (routes: FlatRoute[]) =>
    Array.from(
      new Set(
        routes
          .filter((route) => route.Domain && route.Path)
          .map(
            (route) =>
              `https://${route.Domain}${normalizeAccessPath(String(route.Path))}`,
          ),
      ),
    );

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

  const mapUpstreamResourceType = (input: {
    type?: FunctionRouteType;
    targetType?: GatewayTargetType;
    upstreamResourceType?: UpstreamResourceType;
    requiresFunctionType: boolean;
  }): UpstreamResourceType => {
    if (input.upstreamResourceType) {
      return input.upstreamResourceType;
    }

    if (input.type === "HTTP") {
      return "WEB_SCF";
    }
    if (input.type === "Event") {
      return "SCF";
    }

    if (input.requiresFunctionType || input.targetType === "function") {
      throw new Error(
        "为云函数创建/更新路由时必须显式提供 type（HTTP→WEB_SCF，Event→SCF）或 route.upstreamResourceType。省略会导致 HTTP 与 Event 函数互相误标，访问时可能返回 FUNCTION_PARAM_INVALID 或网关内部错误。",
      );
    }

    throw new Error(
      "必须提供 route.upstreamResourceType（SCF / WEB_SCF / CBR / STATIC_STORE / LH），或在函数场景提供 type=\"HTTP\"|\"Event\"。",
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
      }>;
    };
    resolved: {
      domain: string;
      path: string;
      upstreamResourceType: UpstreamResourceType;
      upstreamResourceName: string;
      enableAuth?: boolean;
    };
  }> => {
    const upstreamResourceName =
      input.route?.serviceName ?? input.targetName;
    if (!upstreamResourceName) {
      throw new Error(
        "必须提供 targetName 或 route.serviceName 作为上游资源名称（例如云函数名）",
      );
    }

    const isFunctionRoute =
      input.targetType === "function" ||
      input.type !== undefined ||
      input.route?.upstreamResourceType === "SCF" ||
      input.route?.upstreamResourceType === "WEB_SCF" ||
      (!input.route?.upstreamResourceType && Boolean(input.targetName));

    const upstreamResourceType = mapUpstreamResourceType({
      type: input.type,
      targetType: input.targetType,
      upstreamResourceType: input.route?.upstreamResourceType,
      requiresFunctionType: isFunctionRoute,
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

    return {
      EnvId: await resolveEnvId(),
      Domain: {
        Domain: domain,
        Routes: [
          {
            Path: path,
            UpstreamResourceType: upstreamResourceType,
            UpstreamResourceName: upstreamResourceName,
            EnableAuth: enableAuth,
          },
        ],
      },
      resolved: {
        domain,
        path,
        upstreamResourceType,
        upstreamResourceName,
        enableAuth,
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
            if (input.type === "HTTP") {
              hint +=
                "此外注意：如果目标函数最初是作为 Event 函数创建的，这里 type 仍必须传 Event（UpstreamResourceType=SCF）；误传 HTTP/WEB_SCF 会导致此错误。";
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
            targetType: input.targetType ?? null,
            targetName: payload.resolved.upstreamResourceName,
            domain: payload.resolved.domain,
            path: payload.resolved.path,
            upstreamResourceType: payload.resolved.upstreamResourceType,
            upstreamResourceName: payload.resolved.upstreamResourceName,
            auth: payload.resolved.enableAuth ?? null,
            raw: result,
          },
          `已为目标 ${payload.resolved.upstreamResourceName} 在域名 ${payload.resolved.domain} 创建路由 ${payload.resolved.path}（${payload.resolved.upstreamResourceType}）。注意：路由配置传播通常需要等待 30 秒到 3 分钟，请勿立即访问。该操作只创建网关入口，不会自动放开函数安全规则；若需要匿名或浏览器直接访问，请继续检查函数资源权限。`,
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
            raw: result,
          },
          `HTTP 路由更新成功（${payload.resolved.domain}${payload.resolved.path}）`,
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
        "CloudBase 网关统一只读入口（Domain/Route 模型）。通过 listRoutes / getRoute / listCustomDomains 查询域名与路由；主键为 Domain + Path，上游类型为 SCF / WEB_SCF / CBR / STATIC_STORE / LH。",
      inputSchema: {
        action: z
          .enum(QUERY_GATEWAY_ACTIONS)
          .describe("只读操作类型：listRoutes、getRoute、listCustomDomains"),
        targetType: z
          .enum(["function"])
          .optional()
          .describe("目标资源类型。当前支持 function"),
        targetName: z
          .string()
          .optional()
          .describe("上游资源名称。getRoute 时可按云函数名过滤"),
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
        "CloudBase 网关统一写入口（Domain/Route 模型）。为已存在的 HTTP 云函数补默认域名访问时，使用 createRoute，并提供 targetType=\"function\"、targetName、type=\"HTTP\"（映射 WEB_SCF）与期望 path；Event 函数传 type=\"Event\"（映射 SCF）。未传 domain 时自动解析 IsDefault 默认域名。注意 createRoute 只创建网关入口，不会自动修改函数资源权限。更新鉴权用 updateRoute；删除用 deleteRoute（Domain+Path）。⚠️ 绑定带 SSL 证书的自定义域名用 bindCustomDomain；CORS/安全域名请使用 envDomainManagement。",
      inputSchema: {
        action: z
          .enum(MANAGE_GATEWAY_ACTIONS)
          .describe(
            "写操作类型。为已有函数补默认域名访问入口时使用 createRoute；函数场景必须显式提供 type（HTTP→WEB_SCF，Event→SCF）或 route.upstreamResourceType。",
          ),
        targetType: z
          .enum(["function"])
          .optional()
          .describe("目标资源类型。当前支持 function"),
        targetName: z
          .string()
          .optional()
          .describe("目标资源名称。createRoute 到云函数时填写函数名"),
        path: z
          .string()
          .optional()
          .describe(
            "访问路径，默认 /{targetName}。例如为 HTTP 函数暴露 /api/hello 时传 /api/hello。该参数只创建网关入口，不会自动放开函数资源权限。",
          ),
        type: z
          .enum(["Event", "HTTP"])
          .optional()
          .describe(
            "目标函数运行时类型，不是接入协议。HTTP 云函数传 HTTP（UpstreamResourceType=WEB_SCF）；Event 函数传 Event（SCF）。误标会导致 FUNCTION_PARAM_INVALID 或网关错误。函数路由场景必须显式提供 type 或 route.upstreamResourceType。",
          ),
        auth: z
          .boolean()
          .optional()
          .describe(
            "是否开启网关路径鉴权（EnableAuth）。若要走默认域名做匿名或浏览器访问，通常设为 false；该开关仅控制网关入口本身，不会修改函数资源权限。",
          ),
        route: z
          .object({
            path: z.string().optional(),
            serviceName: z.string().optional(),
            upstreamResourceType: z.enum(UPSTREAM_RESOURCE_TYPES).optional(),
            auth: z.boolean().optional(),
          })
          .optional()
          .describe(
            "HTTP 路由配置。upstreamResourceType 可选 SCF / WEB_SCF / CBR / STATIC_STORE / LH",
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

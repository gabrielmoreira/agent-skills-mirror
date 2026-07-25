import { beforeEach, describe, expect, it, vi } from "vitest";
import { registerGatewayTools } from "./gateway.js";
import type { ExtendedMcpServer } from "../server.js";

const {
  mockDescribeHttpServiceRoute,
  mockCreateHttpServiceRoute,
  mockModifyHttpServiceRoute,
  mockDeleteHttpServiceRoute,
  mockBindCustomDomain,
  mockDeleteCustomDomain,
  mockGetCloudBaseManager,
  mockLogCloudBaseResult,
  mockGetEnvId,
} = vi.hoisted(() => ({
  mockDescribeHttpServiceRoute: vi.fn(),
  mockCreateHttpServiceRoute: vi.fn(),
  mockModifyHttpServiceRoute: vi.fn(),
  mockDeleteHttpServiceRoute: vi.fn(),
  mockBindCustomDomain: vi.fn(),
  mockDeleteCustomDomain: vi.fn(),
  mockGetCloudBaseManager: vi.fn(),
  mockLogCloudBaseResult: vi.fn(),
  mockGetEnvId: vi.fn(),
}));

vi.mock("../cloudbase-manager.js", () => ({
  getCloudBaseManager: mockGetCloudBaseManager,
  logCloudBaseResult: mockLogCloudBaseResult,
  getEnvId: mockGetEnvId,
}));

function createMockServer() {
  const tools: Record<
    string,
    {
      meta: any;
      handler: (args: any) => Promise<any>;
    }
  > = {};

  const server: ExtendedMcpServer = {
    cloudBaseOptions: { envId: "env-test", region: "ap-guangzhou" },
    logger: vi.fn(),
    registerTool: vi.fn(
      (name: string, meta: any, handler: (args: any) => Promise<any>) => {
        tools[name] = { meta, handler };
      },
    ),
  } as unknown as ExtendedMcpServer;

  registerGatewayTools(server);

  return {
    server,
    tools,
  };
}

describe("gateway tools", () => {
  let tools: ReturnType<typeof createMockServer>["tools"];

  beforeEach(() => {
    vi.clearAllMocks();

    mockGetEnvId.mockResolvedValue("env-test");
    mockDescribeHttpServiceRoute.mockResolvedValue({
      OriginDomain: "origin.service.tcloudbase.com",
      TotalCount: 1,
      Domains: [
        {
          Domain: "env-test.service.tcloudbase.com",
          IsDefault: true,
          Enable: true,
          Status: "SUCCESS",
          Routes: [
            {
              RouteId: "route-1",
              Path: "/api/hello",
              UpstreamResourceType: "WEB_SCF",
              UpstreamResourceName: "helloFn",
              EnableAuth: false,
            },
          ],
        },
        {
          Domain: "api.example.com",
          IsDefault: false,
          Enable: true,
          Status: "SUCCESS",
          CertId: "cert-1",
          Routes: [],
        },
      ],
      RequestId: "req-route-list",
    });
    mockCreateHttpServiceRoute.mockResolvedValue({
      RequestId: "req-route-create",
    });
    mockModifyHttpServiceRoute.mockResolvedValue({
      RequestId: "req-route-update",
    });
    mockDeleteHttpServiceRoute.mockResolvedValue({
      RequestId: "req-route-delete",
    });
    mockBindCustomDomain.mockResolvedValue({
      RequestId: "req-domain-bind",
    });
    mockDeleteCustomDomain.mockResolvedValue({
      RequestId: "req-domain-delete",
    });
    mockGetCloudBaseManager.mockResolvedValue({
      env: {
        describeHttpServiceRoute: mockDescribeHttpServiceRoute,
        createHttpServiceRoute: mockCreateHttpServiceRoute,
        modifyHttpServiceRoute: mockModifyHttpServiceRoute,
        deleteHttpServiceRoute: mockDeleteHttpServiceRoute,
        bindCustomDomain: mockBindCustomDomain,
        deleteCustomDomain: mockDeleteCustomDomain,
      },
    });

    ({ tools } = createMockServer());
  });

  it("schema should expose Domain/Route actions only", () => {
    const queryActions = tools.queryGateway.meta.inputSchema.action._def.values;
    const manageActions = tools.manageGateway.meta.inputSchema.action._def.values;

    expect(queryActions).toEqual(["listRoutes", "getRoute", "listCustomDomains"]);
    expect(manageActions).toEqual([
      "createRoute",
      "updateRoute",
      "deleteRoute",
      "bindCustomDomain",
      "deleteCustomDomain",
    ]);
    expect(queryActions).not.toContain("getAccess");
    expect(queryActions).not.toContain("listDomains");
    expect(manageActions).not.toContain("createAccess");
    expect(manageActions).not.toContain("deleteAccess");
    expect(manageActions).not.toContain("updatePathAuth");
  });

  it("manageGateway schema should explain createRoute for HTTP functions", () => {
    const schema = tools.manageGateway.meta.inputSchema;

    expect(tools.manageGateway.meta.description).toContain("createRoute");
    expect(tools.manageGateway.meta.description).toContain("WEB_SCF");
    expect(schema.action.description).toContain("createRoute");
    expect(schema.targetName.description).toContain("填写函数名");
    expect(schema.path.description).toContain("/api/hello");
    expect(schema.type.description).toContain("HTTP");
    expect(schema.type.description).toContain("WEB_SCF");
    expect(schema.auth.description).toContain("通常设为 false");
  });

  it("manageGateway(action=createRoute) should map HTTP to WEB_SCF on default domain", async () => {
    const result = await tools.manageGateway.handler({
      action: "createRoute",
      targetType: "function",
      targetName: "helloFn",
      path: "api/hello",
      type: "HTTP",
      auth: false,
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockDescribeHttpServiceRoute).toHaveBeenCalled();
    expect(mockCreateHttpServiceRoute).toHaveBeenCalledWith({
      EnvId: "env-test",
      Domain: {
        Domain: "env-test.service.tcloudbase.com",
        Routes: [
          {
            Path: "/api/hello",
            UpstreamResourceType: "WEB_SCF",
            UpstreamResourceName: "helloFn",
            EnableAuth: false,
          },
        ],
      },
    });
    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "createRoute",
        model: "httpServiceRoute",
        domain: "env-test.service.tcloudbase.com",
        path: "/api/hello",
        upstreamResourceType: "WEB_SCF",
        upstreamResourceName: "helloFn",
      },
      nextActions: [
        expect.objectContaining({
          tool: "queryGateway",
          action: "getRoute",
        }),
        expect.objectContaining({
          tool: "queryPermissions",
          action: "getResourcePermission",
        }),
        expect.objectContaining({
          tool: "managePermissions",
          action: "updateResourcePermission",
        }),
      ],
    });
    expect(payload.message).toContain("30 秒到 3 分钟");
  });

  it("manageGateway(action=createRoute) should map Event to SCF and default path", async () => {
    const result = await tools.manageGateway.handler({
      action: "createRoute",
      targetType: "function",
      targetName: "helloFn",
      type: "Event",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockCreateHttpServiceRoute).toHaveBeenCalledWith({
      EnvId: "env-test",
      Domain: {
        Domain: "env-test.service.tcloudbase.com",
        Routes: [
          {
            Path: "/helloFn",
            UpstreamResourceType: "SCF",
            UpstreamResourceName: "helloFn",
            EnableAuth: undefined,
          },
        ],
      },
    });
    expect(payload).toMatchObject({
      success: true,
      data: {
        path: "/helloFn",
        upstreamResourceType: "SCF",
      },
    });
  });

  it("manageGateway(action=createRoute) should reject missing type for function routes", async () => {
    const result = await tools.manageGateway.handler({
      action: "createRoute",
      targetType: "function",
      targetName: "helloFn",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockCreateHttpServiceRoute).not.toHaveBeenCalled();
    expect(payload).toMatchObject({
      success: false,
      message: expect.stringContaining("必须显式提供 type"),
    });
    expect(payload.message).toContain("FUNCTION_PARAM_INVALID");
  });

  it("manageGateway(action=createRoute) should not use OriginDomain as public domain", async () => {
    mockDescribeHttpServiceRoute.mockResolvedValueOnce({
      OriginDomain: "origin.service.tcloudbase.com",
      TotalCount: 0,
      Domains: [],
      RequestId: "req-empty",
    });

    const result = await tools.manageGateway.handler({
      action: "createRoute",
      targetType: "function",
      targetName: "helloFn",
      type: "HTTP",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockCreateHttpServiceRoute).not.toHaveBeenCalled();
    expect(payload.success).toBe(false);
    expect(payload.message).toContain("默认 HTTP 访问域名未就绪");
    expect(payload.message).not.toContain("origin.service.tcloudbase.com");
  });

  it("manageGateway(action=updateRoute) should modify route auth", async () => {
    const result = await tools.manageGateway.handler({
      action: "updateRoute",
      domain: "api.example.com",
      targetName: "helloFn",
      path: "/api/hello",
      type: "HTTP",
      auth: true,
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockModifyHttpServiceRoute).toHaveBeenCalledWith({
      EnvId: "env-test",
      Domain: {
        Domain: "api.example.com",
        Routes: [
          {
            Path: "/api/hello",
            UpstreamResourceType: "WEB_SCF",
            UpstreamResourceName: "helloFn",
            EnableAuth: true,
          },
        ],
      },
    });
    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "updateRoute",
        domain: "api.example.com",
        auth: true,
      },
    });
  });

  it("manageGateway(action=deleteRoute) should delete by domain and path", async () => {
    const result = await tools.manageGateway.handler({
      action: "deleteRoute",
      domain: "env-test.service.tcloudbase.com",
      path: "/api/hello",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockDeleteHttpServiceRoute).toHaveBeenCalledWith({
      EnvId: "env-test",
      Domain: "env-test.service.tcloudbase.com",
      Paths: ["/api/hello"],
    });
    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "deleteRoute",
        domain: "env-test.service.tcloudbase.com",
        path: "/api/hello",
      },
    });
  });

  it("queryGateway(action=getRoute) should return urls for matching function", async () => {
    const result = await tools.queryGateway.handler({
      action: "getRoute",
      targetType: "function",
      targetName: "helloFn",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockDescribeHttpServiceRoute).toHaveBeenCalledWith({
      EnvId: "env-test",
      Limit: 1000,
    });
    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "getRoute",
        targetName: "helloFn",
        total: 1,
        urls: ["https://env-test.service.tcloudbase.com/api/hello"],
        route: expect.objectContaining({
          UpstreamResourceName: "helloFn",
          UpstreamResourceType: "WEB_SCF",
        }),
      },
      nextActions: [
        expect.objectContaining({
          tool: "manageGateway",
          action: "createRoute",
        }),
      ],
    });
  });

  it("queryGateway(action=listRoutes) should list gateway routes", async () => {
    const result = await tools.queryGateway.handler({
      action: "listRoutes",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "listRoutes",
        routes: [expect.objectContaining({ RouteId: "route-1" })],
        total: 1,
      },
    });
  });

  it("queryGateway(action=listCustomDomains) should exclude default domain", async () => {
    const result = await tools.queryGateway.handler({
      action: "listCustomDomains",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "listCustomDomains",
        total: 1,
        domains: [expect.objectContaining({ Domain: "api.example.com" })],
      },
    });
  });

  it("manageGateway(action=createRoute) should accept explicit upstreamResourceType", async () => {
    const result = await tools.manageGateway.handler({
      action: "createRoute",
      domain: "api.example.com",
      route: {
        path: "/api/run",
        serviceName: "my-service",
        upstreamResourceType: "CBR",
      },
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockCreateHttpServiceRoute).toHaveBeenCalledWith({
      EnvId: "env-test",
      Domain: {
        Domain: "api.example.com",
        Routes: [
          {
            Path: "/api/run",
            UpstreamResourceType: "CBR",
            UpstreamResourceName: "my-service",
            EnableAuth: undefined,
          },
        ],
      },
    });
    expect(payload.success).toBe(true);
  });

  it("manageGateway(action=bindCustomDomain) should bind custom domain", async () => {
    const result = await tools.manageGateway.handler({
      action: "bindCustomDomain",
      domain: "api.example.com",
      certificateId: "cert-1",
    });

    const payload = JSON.parse(result.content[0].text);

    expect(mockBindCustomDomain).toHaveBeenCalledWith({
      EnvId: "env-test",
      Domain: {
        Domain: "api.example.com",
        CertId: "cert-1",
      },
    });
    expect(payload).toMatchObject({
      success: true,
      data: {
        action: "bindCustomDomain",
        domain: "api.example.com",
      },
    });
  });
});

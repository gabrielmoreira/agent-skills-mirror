import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fs from 'fs';
import path from 'path';

const { mockGetCloudBaseManager, mockGetEnvId } = vi.hoisted(() => ({
  mockGetCloudBaseManager: vi.fn(),
  mockGetEnvId: vi.fn(),
}));

vi.mock("../cloudbase-manager.js", () => ({
  getCloudBaseManager: mockGetCloudBaseManager,
  getEnvId: mockGetEnvId,
}));

type RegisteredTool = { meta: any; handler: (args: any) => Promise<any> };

async function createCloudRunTools() {
  const tools: Record<string, RegisteredTool> = {};
  const server: any = {
    cloudBaseOptions: {},
    ide: "CodeBuddy",
    server: {
      sendLoggingMessage: vi.fn(),
    },
    registerTool: vi.fn((name: string, meta: any, handler: (args: any) => Promise<any>) => {
      tools[name] = { meta, handler };
    }),
  };
  const { registerCloudRunTools } = await import("./cloudrun.js");
  registerCloudRunTools(server);
  return { tools, server };
}

function parseToolResult(res: any) {
  const text = res.content[0].text;
  return JSON.parse(text);
}

type ManagerMock = {
  commonService: ReturnType<typeof vi.fn>;
  cloudrun: {
    deploy: ReturnType<typeof vi.fn>;
    detail: ReturnType<typeof vi.fn>;
    getDeployRecords?: ReturnType<typeof vi.fn>;
  };
};

function makeManager(options: {
  envStatus?: "normal" | "creating" | "unopened";
  detailImpl?: (params: { serverName: string }) => Promise<any>;
  deployImpl?: (params: any) => Promise<any>;
} = {}): ManagerMock {
  const {
    envStatus = "normal",
    detailImpl = async () => {
      throw new Error("ResourceNotFound.ServerNotFound");
    },
    deployImpl = async () => ({}),
  } = options;
  return {
    commonService: vi.fn().mockReturnValue({
      call: async (req: any) => {
        if (req.Action === "DescribeEnvBaseInfo") {
          if (envStatus === "unopened") {
            return { EnvBaseInfo: {}, IsExist: false };
          }
          return {
            EnvBaseInfo: { EnvId: "env-test", Status: envStatus, PackageType: "Trial" },
            IsExist: true,
          };
        }
        return {};
      },
    }),
    cloudrun: {
      deploy: vi.fn(deployImpl),
      detail: vi.fn(detailImpl),
    },
  };
}

describe("manageCloudRun deploy imageUrl branch", () => {
  let tmpSourceDir: string;
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetEnvId.mockResolvedValue("env-configured");
    tmpSourceDir = fs.mkdtempSync(path.join(process.cwd(), ".tmp-cloudrun-src-"));
  });
  afterEach(() => {
    if (tmpSourceDir) {
      fs.rmSync(tmpSourceDir, { recursive: true, force: true });
    }
  });

  it("forwards imageUrl to SDK deploy params (DeployType=image) and allows omitting targetPath", async () => {
    const manager = makeManager();
    mockGetCloudBaseManager.mockReturnValue(manager);
    const { tools } = await createCloudRunTools();

    const res = await tools.manageCloudRun.handler({
      action: "deploy",
      serverName: "hermes-agent",
      imageUrl: "ccr.ccs.tencentyun.com/ns/hermes:v1",
      serverConfig: {
        OpenAccessTypes: ["PUBLIC"],
        Cpu: 0.5,
        Mem: 1,
        MinNum: 1,
        MaxNum: 3,
      },
    });
    const parsed = parseToolResult(res);
    expect(parsed.success).toBe(true);
    expect(parsed.data.deployType).toBe("image");
    expect(parsed.data.imageUrl).toBe("ccr.ccs.tencentyun.com/ns/hermes:v1");
    expect(parsed.data.serverType).toBe("container");
    expect(parsed.data.deployPath).toBeUndefined();
    expect(parsed.data.cloudbasercGenerated).toBe(false);

    const deployCall = manager.cloudrun.deploy.mock.calls[0][0];
    expect(deployCall.imageUrl).toBe("ccr.ccs.tencentyun.com/ns/hermes:v1");
    expect(deployCall.serverName).toBe("hermes-agent");
    expect(deployCall.serverType).toBe("container");
    expect(deployCall.serverConfig).toEqual({
      OpenAccessTypes: ["PUBLIC"],
      Cpu: 0.5,
      Mem: 1,
      MinNum: 1,
      MaxNum: 3,
    });
    // 镜像部署未传 targetPath 时应保持 undefined，交给 SDK 走 DeployType=image 分支。
    expect(deployCall.targetPath).toBeUndefined();
  });

  it("fails with guidance when imageUrl deploy targets an unopened CloudRun env", async () => {
    const manager = makeManager({ envStatus: "unopened" });
    mockGetCloudBaseManager.mockReturnValue(manager);
    const { tools } = await createCloudRunTools();

    const promise = tools.manageCloudRun.handler({
      action: "deploy",
      serverName: "hermes-agent",
      imageUrl: "ccr.ccs.tencentyun.com/ns/hermes:v1",
    });
    await expect(promise).rejects.toThrow(/initEnv/);
    await expect(promise).rejects.toThrow(/尚未初始化云托管/);
    expect(manager.cloudrun.deploy).not.toHaveBeenCalled();
  });

  it("keeps source-build behavior when imageUrl is absent (targetPath required)", async () => {
    const manager = makeManager();
    mockGetCloudBaseManager.mockReturnValue(manager);
    const { tools } = await createCloudRunTools();

    const res = await tools.manageCloudRun.handler({
      action: "deploy",
      serverName: "my-svc",
      targetPath: tmpSourceDir,
      serverConfig: {
        OpenAccessTypes: ["PUBLIC"],
      },
    });
    const parsed = parseToolResult(res);
    expect(parsed.success).toBe(true);
    expect(parsed.data.deployType).toBe("source");
    expect(parsed.data.imageUrl).toBeUndefined();

    const deployCall = manager.cloudrun.deploy.mock.calls[0][0];
    expect(deployCall.imageUrl).toBeUndefined();
    expect(deployCall.targetPath).toBe(tmpSourceDir);
  });

  it("rejects deploy when neither targetPath nor imageUrl is provided", async () => {
    const manager = makeManager();
    mockGetCloudBaseManager.mockReturnValue(manager);
    const { tools } = await createCloudRunTools();

    await expect(
      tools.manageCloudRun.handler({
        action: "deploy",
        serverName: "my-svc",
      }),
    ).rejects.toThrow(/targetPath.*imageUrl|imageUrl.*targetPath/);
    expect(manager.cloudrun.deploy).not.toHaveBeenCalled();
  });
});

describe("extractCloudRunImageInfo", () => {
  it("returns undefined when no image fields exist", async () => {
    const { extractCloudRunImageInfo } = await import("./cloudrun.js");
    expect(
      extractCloudRunImageInfo({ ServerConfig: { Cpu: 0.5 }, BaseInfo: { Status: "normal" } }, {}),
    ).toBeUndefined();
  });

  it("extracts ImageUrl from latest deploy record (image deploy)", async () => {
    const { extractCloudRunImageInfo } = await import("./cloudrun.js");
    const latestDeploy = {
      Status: "creating",
      DeployType: "image",
      ImageUrl: "ccr.ccs.tencentyun.com/ns/hermes:v1",
    };
    expect(extractCloudRunImageInfo({}, latestDeploy)).toEqual({
      imageUrl: "ccr.ccs.tencentyun.com/ns/hermes:v1",
      deployType: "image",
    });
  });

  it("extracts ImageUrl from ServiceDetail.ServerConfig when present", async () => {
    const { extractCloudRunImageInfo } = await import("./cloudrun.js");
    const detail = {
      ServerConfig: { ImageUrl: "ccr.ccs.tencentyun.com/ns/other:v2" },
    };
    expect(extractCloudRunImageInfo(detail)).toEqual({
      imageUrl: "ccr.ccs.tencentyun.com/ns/other:v2",
    });
  });
});

import { describe, expect, it } from "vitest";
import { detectCloudRunDbNetworkRisk } from "./cloudrun.js";

describe("detectCloudRunDbNetworkRisk", () => {
  it("returns null when EnvParams has no DB signals", () => {
    expect(
      detectCloudRunDbNetworkRisk({
        envParams: JSON.stringify({ NODE_ENV: "production", PORT: "3000" }),
      }),
    ).toBeNull();
  });

  it("returns null when VpcConf is complete even if DATABASE_URL is set", () => {
    expect(
      detectCloudRunDbNetworkRisk({
        envParams: JSON.stringify({
          DATABASE_URL: "postgres://user:pass@10.0.0.3:5432/app",
        }),
        vpcConf: { VpcId: "vpc-abc", SubnetId: "subnet-def" },
      }),
    ).toBeNull();
  });

  it("flags DATABASE_URL without VpcConf", () => {
    const risk = detectCloudRunDbNetworkRisk({
      envParams: JSON.stringify({
        DATABASE_URL: "postgres://user:pass@10.0.0.3:5432/app",
      }),
    });
    expect(risk?.code).toBe("MISSING_VPC_FOR_DB_ENV");
    expect(risk?.matchedKeys).toContain("DATABASE_URL");
  });

  it("flags MYSQL_* keys without VpcConf", () => {
    const risk = detectCloudRunDbNetworkRisk({
      envParams: JSON.stringify({
        MYSQL_HOST: "10.0.0.8",
        MYSQL_PORT: "3306",
      }),
    });
    expect(risk?.code).toBe("MISSING_VPC_FOR_DB_ENV");
    expect(risk?.matchedKeys).toEqual(
      expect.arrayContaining(["MYSQL_HOST", "MYSQL_PORT"]),
    );
  });

  it("flags connection URL embedded in a non-standard key", () => {
    const risk = detectCloudRunDbNetworkRisk({
      envParams: JSON.stringify({
        APP_DSN: "mysql://root:x@192.168.1.2:3306/demo",
      }),
    });
    expect(risk?.code).toBe("MISSING_VPC_FOR_DB_ENV");
    expect(risk?.matchedKeys).toContain("APP_DSN");
  });

  it("flags incomplete VpcConf the same as missing VpcConf", () => {
    const risk = detectCloudRunDbNetworkRisk({
      envParams: JSON.stringify({ REDIS_URL: "redis://10.0.0.9:6379" }),
      vpcConf: { VpcId: "vpc-only" },
    });
    expect(risk?.code).toBe("MISSING_VPC_FOR_DB_ENV");
  });
});

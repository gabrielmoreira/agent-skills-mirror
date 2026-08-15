import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { readProjectConfig } from "./project-config.js";

describe("readProjectConfig", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "cloudbase-project-config-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should return undefined when .cloudbase/project.json does not exist", () => {
    expect(readProjectConfig(tempDir)).toBeUndefined();
  });

  it("should parse valid project config", () => {
    const dir = join(tempDir, "demo");
    mkdirSync(join(dir, ".cloudbase"), { recursive: true });
    writeFileSync(
      join(dir, ".cloudbase", "project.json"),
      JSON.stringify({ site: "intl", region: "ap-singapore", envId: "booker-ai-i0gygeljs622ffd23" }),
      "utf-8",
    );

    expect(readProjectConfig(dir)).toEqual({
      site: "intl",
      region: "ap-singapore",
      envId: "booker-ai-i0gygeljs622ffd23",
    });
  });

  it("should return undefined on malformed JSON without throwing", () => {
    const dir = join(tempDir, "broken");
    mkdirSync(join(dir, ".cloudbase"), { recursive: true });
    writeFileSync(join(dir, ".cloudbase", "project.json"), "{invalid", "utf-8");

    expect(readProjectConfig(dir)).toBeUndefined();
  });
});

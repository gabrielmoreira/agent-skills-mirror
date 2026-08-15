import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import type { ProjectConfig } from "./site-map.js";

/**
 * 读取项目级配置 `.cloudbase/project.json`。
 *
 * 该文件是 site/region/envId 的可选持久化来源，让"打开项目即连对服务"
 * （对齐 Vercel `.vercel/project.json` 的三级回退）。读取失败/文件不存在
 * 返回 undefined，不阻塞调用方。
 */
export function readProjectConfig(cwd?: string): ProjectConfig | undefined {
  try {
    const projectRoot = cwd ?? process.env.WORKSPACE_FOLDER_PATHS ?? process.cwd();
    const configPath = join(projectRoot, ".cloudbase", "project.json");
    if (!existsSync(configPath)) {
      return undefined;
    }
    const raw = readFileSync(configPath, "utf-8");
    const parsed = JSON.parse(raw) as ProjectConfig;
    if (!parsed || typeof parsed !== "object") {
      return undefined;
    }
    return parsed;
  } catch {
    return undefined;
  }
}

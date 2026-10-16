#!/usr/bin/env node

// 来源分类规则：优先读取工程内 03-处理状态/来源规则.json，缺失时使用通用默认值。
// dirs 是相对 01-原始素材区 的目录；code 用于来源注册表编号，留空表示不进入注册表编号。

const fs = require("fs");
const path = require("path");

const RULES_RELATIVE_PATH = path.join("03-处理状态", "来源规则.json");

const DEFAULT_SOURCE_RULES = [
  { category: "短视频", sourceType: "短视频", code: "VIDEO", dirs: ["短视频/文稿"] },
  { category: "公众号", sourceType: "公众号文章", code: "WX", dirs: ["公众号"] },
  { category: "观点与概念", sourceType: "观点与概念", code: "CON", dirs: ["观点与概念"] },
  { category: "爆款文稿", sourceType: "爆款文稿", code: "BK", dirs: ["爆款文稿"] },
  { category: "推文", sourceType: "推文素材", code: "POST", dirs: ["推文"] },
  { category: "其他作者", sourceType: "外部研究素材", code: "EXT", dirs: ["其他作者"] },
  { category: "本人内容", sourceType: "本人内容", code: "USER", dirs: ["本人内容"] },
  { category: "完整副本", sourceType: "完整副本", code: "", dirs: ["完整副本"] },
];

function validateRules(rules, file) {
  if (!Array.isArray(rules) || rules.length === 0) {
    throw new Error(`${file} 必须是非空数组`);
  }
  for (const [index, rule] of rules.entries()) {
    const where = `${file} 第 ${index + 1} 条`;
    if (!rule || typeof rule.category !== "string" || !rule.category) throw new Error(`${where} 缺少 category`);
    if (typeof rule.sourceType !== "string" || !rule.sourceType) throw new Error(`${where} 缺少 sourceType`);
    if (!Array.isArray(rule.dirs) || rule.dirs.length === 0 || rule.dirs.some((dir) => typeof dir !== "string" || !dir)) {
      throw new Error(`${where} 的 dirs 必须是非空字符串数组`);
    }
    if (rule.code !== undefined && typeof rule.code !== "string") throw new Error(`${where} 的 code 必须是字符串`);
  }
  return rules.map((rule) => ({ ...rule, code: rule.code || "" }));
}

function loadSourceRules(root) {
  const file = path.join(root, RULES_RELATIVE_PATH);
  if (!fs.existsSync(file)) return DEFAULT_SOURCE_RULES.map((rule) => ({ ...rule }));
  return validateRules(JSON.parse(fs.readFileSync(file, "utf8")), file);
}

function ruleMatchesPath(rule, relPath) {
  const normalized = relPath.split("\\").join("/");
  return rule.dirs.some((dir) => dir.split("/").every((segment) => normalized.includes(segment)));
}

module.exports = { DEFAULT_SOURCE_RULES, RULES_RELATIVE_PATH, loadSourceRules, ruleMatchesPath };

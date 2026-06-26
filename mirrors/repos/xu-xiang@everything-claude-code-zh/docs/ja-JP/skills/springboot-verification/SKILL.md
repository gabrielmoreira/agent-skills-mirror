---
name: springboot-verification
description: Spring Boot 项目的验证循环：构建、静态分析、带有覆盖率的测试、安全扫描以及发布或 PR 前的差异审查。
---

# Spring Boot 验证循环

在提交 PR、发生重大变更后或部署前执行。

## 阶段 1：构建

```bash
mvn -T 4 clean verify -DskipTests
# 或者
./gradlew clean assemble -x test
```

如果构建失败，请停止并修复问题。

## 阶段 2：静态分析

Maven（常用插件）：
```bash
mvn -T 4 spotbugs:check pmd:check checkstyle:check
```

Gradle（如果已配置）：
```bash
./gradlew checkstyleMain pmdMain spotbugsMain
```

## 阶段 3：测试 + 覆盖率

```bash
mvn -T 4 test
mvn jacoco:report   # 确认覆盖率是否达到 80% 以上
# 或者
./gradlew test jacocoTestReport
```

报告内容：
- 测试总数、通过/失败数
- 覆盖率 %（行/分支）

## 阶段 4：安全扫描

```bash
# 依赖项 CVE 漏洞扫描
mvn org.owasp:dependency-check-maven:check
# 或者
./gradlew dependencyCheckAnalyze

# 敏感信息/密钥扫描（git）
git secrets --scan  # 如果已配置
```

## 阶段 5：Lint/格式化（可选门禁）

```bash
mvn spotless:apply   # 如果使用了 Spotless 插件
./gradlew spotlessApply
```

## 阶段 6：差异审查 (Diff Review)

```bash
git diff --stat
git diff
```

检查清单：
- 无残留的调试日志（如 `System.out`、无级别保护的 `log.debug`）
- 具有明确语义的错误信息和 HTTP 状态码
- 在必要位置包含了事务（Transaction）和校验（Validation）
- 配置变更已记录在文档中

## 输出模板

```
验证报告
===================
构建:       [通过/未通过]
静态分析:   [通过/未通过] (spotbugs/pmd/checkstyle)
测试:       [通过/未通过] (X/Y 通过, Z% 覆盖率)
安全:       [通过/未通过] (发现 CVE: N)
差异:       [X 个文件变更]

整体状态:   [就绪 / 未完成]

需要修复的问题：
1. ...
2. ...
```

## 持续模式

- 发生重大变更或在长会话中，每 30~60 分钟重新运行一次各阶段。
- 保持短循环：通过 `mvn -T 4 test` + spotbugs 获取快速反馈。

**注意**：及时的反馈优于迟来的意外。请保持门禁（Gates）严格，并在生产系统中将警告视为缺陷。

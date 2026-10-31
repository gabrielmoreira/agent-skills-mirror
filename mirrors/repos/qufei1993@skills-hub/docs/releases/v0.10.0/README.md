# Skills Hub v0.10.0

v0.10.0 的重点是在多台设备间安全同步已托管的 Skill 库。本版本还新增独立本机回收站、韩文界面和 ZCode 内置适配，并加强 Skill 生命周期安全与管理体验。

## 主要功能

### 多设备 Skill 库同步

通过 GitHub、GitLab 或 Gitee 仓库同步 Skill 文件、描述、标签、Git 历史和设备记录。三方比较会自动合并独立修改，并将真实冲突限制在对应 Skill；凭据、本机来源绑定、工具目标、项目路径和应用设置始终留在当前设备。

### 独立回收站

删除的 Skill 会在当前设备保留 30 天。恢复时会还原文件及已保存的描述、标签、启用状态、来源信息和可恢复的工具关系；应用启动时及运行期间每天清理过期项目。

### 更安全的管理、更多语言与工具

存储迁移、自动更新、删除及工具副本刷新会保护本地原始来源和被独立修改的文件。My Skills 使用更紧凑的范围筛选，并确保批量操作只处理当前可见选择。界面支持英文、简体中文和韩文；内置工具增加到 48 个，并新增 ZCode 的全局及项目级 Skill 同步。

## Issue 与 PR

| 范围 | Issue | 主 PR | 相关 PR |
| --- | --- | --- | --- |
| 多设备 Skill 库同步 | [#56](https://github.com/qufei1993/skills-hub/issues/56) | [#127](https://github.com/qufei1993/skills-hub/pull/127) | [#134](https://github.com/qufei1993/skills-hub/pull/134)、[#136](https://github.com/qufei1993/skills-hub/pull/136)、[#137](https://github.com/qufei1993/skills-hub/pull/137)、[#139](https://github.com/qufei1993/skills-hub/pull/139) |
| 独立回收站 | — | [#140](https://github.com/qufei1993/skills-hub/pull/140) | [#137](https://github.com/qufei1993/skills-hub/pull/137) |
| 韩文界面 | — | [#135](https://github.com/qufei1993/skills-hub/pull/135) | — |
| My Skills 筛选与布局 | — | [#133](https://github.com/qufei1993/skills-hub/pull/133) | — |
| 嵌套 Git Skill 发现 | [#129](https://github.com/qufei1993/skills-hub/issues/129) | [#131](https://github.com/qufei1993/skills-hub/pull/131) | — |
| 筛选安装 | — | [#132](https://github.com/qufei1993/skills-hub/pull/132) | [#124](https://github.com/qufei1993/skills-hub/pull/124) |
| 存储与替换安全 | [#123](https://github.com/qufei1993/skills-hub/issues/123) | [#125](https://github.com/qufei1993/skills-hub/pull/125) | [#127](https://github.com/qufei1993/skills-hub/pull/127)、[#128](https://github.com/qufei1993/skills-hub/pull/128) |
| 来源缺失时的 Skill 详情 | — | [#138](https://github.com/qufei1993/skills-hub/pull/138) | — |
| Kimi Code CLI 路径与图标 | [#122](https://github.com/qufei1993/skills-hub/issues/122) | [#126](https://github.com/qufei1993/skills-hub/pull/126) | — |
| Windows/MSVC Rust 构建 | [#142](https://github.com/qufei1993/skills-hub/issues/142) | [#143](https://github.com/qufei1993/skills-hub/pull/143) | — |
| ZCode 工具适配 | [#144](https://github.com/qufei1993/skills-hub/issues/144) | [#146](https://github.com/qufei1993/skills-hub/pull/146) | — |

[PR #130](https://github.com/qufei1993/skills-hub/pull/130) 仅包含测试环境清理，因此不列入面向用户的更新日志。

## 详细文档

### 设备同步

- [多设备同步架构与最终行为](device-sync-architecture.md)：Issue #56 的需求背景，以及产品决策、同步模型、仓库格式、模块设计和最终安全边界。
- [设备同步可靠性与安全修复](device-sync-reliability.md)：三方合并、来源归属、文件保留、工具分发、凭据访问、历史记录和设备页面的最终实现。
- [Gitee 手动 Token 同步修复](gitee-manual-token-sync.md)：在浏览器授权不可用时，通过用户主动加载仓库识别可见性并完成首次同步。

### 回收站与 Skill 生命周期

- [独立回收站设计](standalone-recycle-bin.md)：30 天保留、恢复、清理、错误处理和本机存储边界。
- [Skills 存储路径与移除安全修复](bugfix-safe-skill-storage-and-removal.md)：Issue #123、目录重叠保护、自动替换、回滚和删除确认。

### 管理与安装

- [Skill 与工具管理体验改进](management-experience.md)：My Skills 筛选、批量操作、安装候选、异常提示、详情布局和 ZCode 内置适配。
- [嵌套 Git Skill 发现修复](bugfix-nested-skill-discovery.md)：Issue #129 的问题、扫描边界和验证。

### 发布构建

- [发布构建与平台兼容性](release-build-compatibility.md)：正式安装包的 OAuth Client ID 检查，以及 Windows/MSVC Rust 测试目标编译修复。

## 更新日志

- [中文更新日志](../../CHANGELOG.zh.md)
- [英文更新日志](../../../CHANGELOG.md)

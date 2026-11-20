# Motion 效果扩展的职责边界

参考视频转模板（`openmotion-video-to-template`）交付可复用模板。Agent 自行决定并记录常规创作取舍，不询问创作偏好。需要付费生成且计划批次尚未获授权时，在提交请求前集中确认一次。已有模板的修改由 `openmotion-template-to-video` 处理，缺少用户才能提供的事实或素材时可以提问。

普通参考视频复刻由 `openmotion-recreate` 交付成片和可编辑工程。两种参考视频流程沿用共用的参考片分析和测量方法。模板沿用 HyperFrames，随包携带源码、素材、预览和编辑说明。技术检查与视觉验收分别记录。

## 当前分发与接口

- 五个正式入口均随一期插件和四宿主适配器分发。`openmotion-template-to-video` 使用 `openmotion://workflow/template/start`，`openmotion-video-to-template` 使用 `openmotion://workflow/video-to-template/start`；短 workflow ID 保持兼容，读取不会启动服务或创建工程。
- Phase one exposes [eighteen registered public Tool names](mcp-phase1-tools.md), including one asset compatibility alias. Use `openmotion_get_project` for project/file/job reads, `openmotion_edit_project` for managed source changes, `openmotion_import_assets` for batch imports and `openmotion_export_request` for export and technical verification.
- The two public catalog Tools provide the local template index and individual template details/instructions. Older standalone comparison, workflow-reading and template-management handlers remain internal compatibility only; Skills must not require those hidden calls. Existing private template files are preserved.
- 下载/分析参考、CLI 检查、原片对照视频与 ZIP 打包由宿主可用能力完成；工具不足须记录缺口。技术检查不代表人类视觉验收。

## 不改底座

插件名、MCP 服务名、安装脚本、用户数据目录和 Studio 端口沿用研发主干，本扩展不修改。安装路径、端口和数据目录变化必须独立验证，不能由内容 Skill 隐式修改。

## 验证边界

- 默认入口保持薄路由，模板专业入口指向真实 Skill；增加用户模板文件不得改变默认目录结果。
- 两条模板 Skill 均可发现并读取全部参考；历史模板文件保持可读取。比较 handler 的存在不代表一期公开可调用。
- 模板入口接入与视频转模板职责分开验证，不以既有视频外观结果代替新版本的运行验证；普通视频复刻由 openmotion-recreate 实现，各版本的实际验证范围单列，不自动认证融合版本。
- 不修改实验成品、生成素材或用户工程；扩展的合入沿用仓库 PR 与 CI 流程。

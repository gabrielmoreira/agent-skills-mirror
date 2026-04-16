# Smart Notes — 智能笔记生成器

输入链接，自动生成结构化学习笔记。支持抖音视频、微信公众号文章。

## 支持的平台

| 平台 | 链接格式 | 提取内容 |
|------|---------|---------|
| 抖音 | 标准链接、短链接、搜索链接、分享文本 | 视频 · 音频 · 语音转文字 · 评论 · 视频元数据 |
| 微信公众号 | `mp.weixin.qq.com/s/xxx` | 文章正文 · 作者 · 发布时间 |

## 安装

### 方式一：在线安装（需访问 GitHub）

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s smart-notes
```

### 方式二：手动安装

将 `smart-notes` 文件夹完整复制到你的工作目录下即可。

## 运行

### Claude Code 用户

安装后直接对 Claude 说：

```
帮我总结 https://v.douyin.com/xxx
```

Claude 会自动触发 smart-notes，提取内容并生成笔记，无需配置 AI API。

### 命令行

```bash
./smart-notes/run.sh "链接"
```

脚本会自动识别平台并执行对应的提取流程。首次运行会自动创建 Python 环境并安装依赖。

## 运行过程

```
自动识别平台（抖音 / 微信 / ...）
    ↓
自动提取内容（视频转文字 / 文章正文）
    ↓
询问：是否登录获取更多信息？（抖音评论等，可跳过，Cookie 仅保存在本地）
    ↓
询问：是否配置 AI 生成总结？（可跳过，填错可重试）
    ↓
生成结果
```

## 输出

```
output/内容标题/
├── raw/            原始内容（文字 · 音频 · 视频 · 评论）
├── supplements/    补充信息（可手动添加）
└── output/         v1.md（AI 总结的笔记）
```

- 重复执行同一个链接，自动生成新版本（v2、v3...）
- 在 `supplements/extra.md` 中添加额外信息，重新执行会纳入总结

## 常见问题

**提示找不到 Python 或 ffmpeg？**

```bash
brew install python@3.12
brew install ffmpeg
```

## 免责声明

本工具仅供个人学习使用。内容版权归原创作者所有，生成的笔记不得用于商业用途或公开传播。所有操作在本地完成，不存储、不转发任何原始内容。

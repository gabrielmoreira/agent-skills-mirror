# GitHub issue

`gh` 已安装并已认证时就用 `gh`；它处理认证、限流和 JSON。退而求其次用 curl 调公开 API，
再不行就给出一个让你的伙伴自己打开的 URL。

本 fork 的会话问题先提到 jnMetaCode/superpowers-zh；维护者确认与翻译无关、是上游行为时再转报 obra/superpowers。

## 搜索

```bash
gh search issues --repo jnMetaCode/superpowers-zh --limit 10 "<terms>" \
  --json number,state,title --jq '.[] | "\(.number)\t\(.state)\t\(.title)"'
```

没有 `gh` 时（未认证，每分钟 10 次请求）：

```bash
curl -s -H "Accept: application/vnd.github+json" \
  "https://api.github.com/search/issues?q=repo:jnMetaCode/superpowers-zh+is:issue+<url-encoded terms>&per_page=10" \
  | jq -r '.items[] | "\(.number)\t\(.state)\t\(.title)"'
```

没有 curl 时，交给对方 `https://github.com/jnMetaCode/superpowers-zh/issues?q=<terms>`。

## 提交

把填好的 `templates/issue.md` 写入工作区并展示确切文本。获得批准后：

```bash
gh issue create --repo jnMetaCode/superpowers-zh --title "<title>" --body-file <path> \
  --label bug --label automated-issue-report
```

提交者没有推送权限时，GitHub 会静默丢弃标签，所以只有协作者提交时标签才会生效；
模板页脚仍会标明这条 issue 是由技能提交的。`gh` 不能附加文件：issue 创建后，
把打包材料的路径给你的伙伴，让他们通过浏览器附上。

没有 `gh` 时，给出一个基于 `diagnosis_report.md` 模板的预填链接，这个模板对任何
提交者都会加上两个标签：

```
https://github.com/jnMetaCode/superpowers-zh/issues/new?template=diagnosis_report.md&title=<url-encoded title>&body=<url-encoded body>
```

GitHub 会拒绝超过约 8,000 个字符的 URL；超过时，只带标题发送链接，并告诉你的伙伴
从文件里粘贴正文。

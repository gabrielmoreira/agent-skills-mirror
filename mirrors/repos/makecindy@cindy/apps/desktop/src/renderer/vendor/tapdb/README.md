# tapdb-web-sdk (vendored)

未发布到 npm 的官方 SDK,直接 vendor 进仓库以避免运行时拉取。

- **来源**: `git@git.example.com:tapdb/web/tapdb-sdk-web.git`
- **版本**: `1.0.0` (取自源仓 `package.json` / `release/npm_js/package.json`)
- **License**: Apache-2.0 (见同目录 `LICENSE`)

## 更新方式

```bash
git -C <somewhere> clone git@git.example.com:tapdb/web/tapdb-sdk-web.git
cp <somewhere>/tapdb-sdk-web/release/tapdb.esm.min.{js,d.ts} ./
cp <somewhere>/tapdb-sdk-web/LICENSE ./
```

## 不要直接 import 这个目录

业务方一律走 `@/analytics/tapdbClient`,它封装了配置注入、生命周期和登录态绑定。

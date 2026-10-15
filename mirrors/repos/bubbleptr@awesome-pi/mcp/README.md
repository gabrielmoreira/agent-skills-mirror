# Pi Index MCP

Read-only [Model Context Protocol](https://modelcontextprotocol.io) server for [Pi Index](https://piindex.dev), the curated directory of [Pi Coding Agent](https://pi.dev) extensions.

Agents can search the directory the same way the site's `?q=` box does, open a package's description, install command, repository and npm links, and the stars and downloads snapshot, and list categories and guides. Every result includes a `piindexUrl` on piindex.dev. The server does not install packages, submit listings, or record searches.

Registry name: `io.github.bubbleptr/piindex`. npm package: `piindex-mcp`. Transport: stdio.

## Tools

| Tool | What it returns |
| --- | --- |
| `search_packages` | Keyword search. Every whitespace-separated term must match, case-insensitive, across the name, English and Chinese description, category, kind, and install command. Optional `category` uses the same ids as `?category=`. |
| `get_package` | One resource by catalog name or stable `id`: descriptions, categories, project / repository / npm links, install command, stars and weekly downloads, and guide links when Pi Index has published any. |
| `list_categories` | Kinds and categories, with counts and piindex.dev URLs. |
| `list_packages` | Resources in one category or kind (`subagents`, `themes`, `all`, …). |
| `list_guides` | Topic pages, category comparison guides, and package guides. |

`piindexUrl` is the package guide when one exists (`https://piindex.dev/packages/…/`), and otherwise the directory search for that name. `guideUrl` is set only for a package guide. Topic and category guides that mention the package are listed on `guides`.

## Install

Requires Node.js 18 or newer. The process speaks MCP over stdin and stdout.

### Cursor

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "piindex": {
      "command": "npx",
      "args": ["-y", "piindex-mcp"]
    }
  }
}
```

### Claude Desktop

`claude_desktop_config.json` uses the same `mcpServers` entry.

### VS Code

`.vscode/mcp.json`:

```json
{
  "servers": {
    "piindex": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "piindex-mcp"]
    }
  }
}
```

### Pi

`~/.pi/agent/mcp.json`, or a project `.mcp.json`, using the `mcpServers` shape documented for Pi's MCP adapter:

```json
{
  "mcpServers": {
    "piindex": {
      "command": "npx",
      "args": ["-y", "piindex-mcp"]
    }
  }
}
```

## Data

Each session loads `https://piindex.dev/catalog.json`. The site builds that file from the same README catalog and stats snapshot as the website, so a directory update is visible after the site deploy without republishing this package. The document is cached in memory for 15 minutes. If the site cannot be reached, the server uses the catalog snapshot bundled in the package.

The only network request is that GET. Queries stay in the process. There is no account, no write tool, and no analytics.

Optional environment variables:

| Variable | Default | Effect |
| --- | --- | --- |
| `PIINDEX_CATALOG_URL` | `https://piindex.dev/catalog.json` | Catalog document to fetch. |
| `PIINDEX_CATALOG_FILE` | unset | Read this JSON file instead of the network. |
| `PIINDEX_CATALOG_TTL_MS` | `900000` | How long a loaded catalog is reused. |

## Develop

From a checkout of [bubbleptr/awesome-pi](https://github.com/bubbleptr/awesome-pi):

```bash
cd site && bun install && bun run export-catalog
cd ../mcp && npm install && npm test
```

`bun run export-catalog` rewrites `mcp/catalog.snapshot.json` from the README catalog. Refresh it when the directory changes. Weekly stats updates do not require a new snapshot; the live `catalog.json` carries those.

## Publish

Do this from the `mcp/` directory after the `catalog.json` page is deployed. Publishing is manual: nothing in this repo publishes to npm or the MCP Registry.

```bash
cd mcp
npm login
npm publish
```

`npm publish` refreshes the bundled snapshot with Bun (`site` dependencies installed) and runs the tests before uploading. The package name `piindex-mcp` is unscoped, so it is public without `--access public`.

Then, authenticated as the GitHub account that owns `bubbleptr`:

```bash
# https://modelcontextprotocol.io/registry/quickstart
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
sudo mv mcp-publisher /usr/local/bin/
mcp-publisher login github
mcp-publisher publish
```

`server.json` `name` and `package.json` `mcpName` are both `io.github.bubbleptr/piindex`, which matches GitHub authentication for that account. Confirm the listing:

```bash
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.bubbleptr/piindex"
```

There is no hosted streamable-HTTP endpoint. Pi Index is a static site, and a remote MCP transport would need a server runtime on each request.

## 中文

Pi Index MCP 是一个只读 MCP 服务，用来查询 [Pi Index](https://piindex.dev) 收录的 Pi Coding Agent 扩展、主题与相关工具。

各客户端都通过 stdio 启动，配置相同：

```json
{
  "mcpServers": {
    "piindex": {
      "command": "npx",
      "args": ["-y", "piindex-mcp"]
    }
  }
}
```

工具：`search_packages`（与网站 `?q=` 相同的关键词搜索，中英文都可匹配）、`get_package`（简介、分类、仓库与 npm 链接、安装命令、Star 与每周下载量、已有的指南页）、`list_categories`、`list_packages`、`list_guides`。每条结果都包含 `piindexUrl`，请把用户链回 piindex.dev。

服务不写入目录、不需要登录，也不会记录查询。数据来自网站构建时发布的 `https://piindex.dev/catalog.json`；站点暂时不可达时，使用安装包内的目录快照。

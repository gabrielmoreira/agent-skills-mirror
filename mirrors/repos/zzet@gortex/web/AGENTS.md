<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Data flow

**Pages must consume data through `lib/hooks.ts` only.** Do not import
seed fixtures or call `fetch` directly from a component. The hook layer
maps every page to a typed `/v1/*` endpoint:

| Hook                | Endpoint                       | Backed by                              |
|---------------------|--------------------------------|-----------------------------------------|
| `useDashboard`      | `/v1/dashboard`                | `graph.Stats` + `analyze` + `get_processes` |
| `useRepos`          | `/v1/repos`                    | `graph.RepoStats`                       |
| `useGraph`          | `/v1/graph`                    | full brief-node + brief-edge dump (optionally `?project`/`?repo`) |
| `useProcesses`      | `/v1/processes`                | `get_processes` MCP tool                |
| `useContracts`      | `/v1/contracts`                | `contracts` MCP tool (action=list)      |
| `useCommunities`    | `/v1/communities`              | `get_communities` MCP tool              |
| `useGuards`         | `/v1/guards`                   | `check_guards` MCP tool                 |
| `useCaveats`        | `/v1/caveats`                  | `analyze` (hotspots/dead_code/cycles) + `check_guards` |
| `useActivity`       | `/v1/activity`                 | server's in-memory event ring buffer    |
| `useProcessDetail`  | `/v1/tools/get_processes`      | single-process detail (step IDs + files)|
| `useSymbolSource`   | `/v1/tools/get_symbol_source`  | source text for one node ID             |
| `useSymbolSearch`   | `/v1/tools/search_symbols`     | BM25 search over the indexed graph      |
| `useUsages`         | `/v1/tools/find_usages`        | reverse-edge walk                       |
| `useDependencies`   | `/v1/tools/get_dependencies`   | forward-edge walk                       |
| `useRecentSearches` | localStorage (`gortex:recents`)| user-local search history, no server    |

If a page needs data that no endpoint exposes, **add the endpoint** in
`internal/server/dashboard.go` (or a new file in `internal/server/`) —
do not push the gap into the frontend with a fixture.

## No mocked data

Every page now reads real data from `/v1/*`. `lib/seed.ts` has been
deleted — sparklines, investigation fixtures, and the aspirational
Sankey view went with it.

- **Dashboard / Communities**: per-repo sparklines are gone. We don't
  store a time-series of `Stats()` snapshots, so there is no honest
  line to draw. Reintroduce only when `/v1/timeline?repo=<id>` exists.

- **Investigations page**: the top-scoring process from
  `useProcesses()` is the flow, `useProcessDetail()` supplies the
  ordered step IDs, `useSymbolSource()` renders the selected step's
  source, and `useActivity()` drives the recent-edits timeline. A
  dropdown in the header lets the user pick any other process. There
  is no persistence yet — that's the next step if investigations need
  to be named / hypothesised / pinned.

- **Graph views**: Constellation and three 3D subviews
  (Galaxies, Strata, City) render real nodes and edges from
  `/v1/graph` via `useGraph()`. Galaxies uses `@react-three/fiber`
  with `OrbitControls` (pan/zoom/rotate/pick); Strata and City
  are still SVG and will be migrated to three-fiber next.
  Positions are laid out deterministically from repo buckets + degree.

If you discover any mocked data in a page, it is a bug — file an
issue or wire it to `/v1/*`.

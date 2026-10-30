---
name: architecture-diagram-author
description: >
  Create and maintain editable drawio architecture diagrams and matching
  self-contained SVG and PNG exports. Use for architecture diagrams, technical
  schematics, drawio updates, crossing arrows, overlapping labels, and Microsoft
  service icons. Apply logical columns, dedicated routing lanes, square-cornered
  colored rectangles, and synchronization with existing documentation or decks.
   Find accurate Microsoft icons across MsiconsCollections, Microsoft Learn Azure
   and Power Platform packs, az-icons.com, and DamoBird365/microsoft-cloud-icons.
   Verify provenance and current product identity. Project-agnostic: discover paths, labels, identifiers, architecture,
  and rendering tools from the current repository rather than assuming a stack.
---

# Architecture Diagram Author (drawio + SVG/PNG)

## Goal and project discovery
Maintain one editable `.drawio` source (mxGraph XML) and two generated exports:
a self-contained SVG with embedded icons and a PNG rasterized from that SVG.
Keep all three consistent with the architecture actually implemented.

Before editing, read the current repository instructions, existing diagram, relevant
code/IaC, and its rendering commands. Discover output paths and consumers rather
than assuming a directory layout, cloud provider, framework, or presentation tool.
If no convention exists, propose source/export paths with a shared descriptive basename.
Use labels and stable IDs from the current system; never carry over customer names,
agent names, resource IDs, coordinates, or workstation paths from another project.
Keep temporary tools and downloads in the repository's designated temporary directory
and clean them up after validation. Do not commit or push without user authorization.

## Layout rules
1. **Containers represent actual domains or boundaries**, not an assumed service list.
   Use colored dashed borders and square corners (`rounded=0` / `rx=0`).
2. **Order columns by flow**, for example client -> API -> processing -> storage.
   Place components that communicate across containers near the facing boundary.
3. **Use colored component rectangles**, a coherent palette per domain, and readable
   text in both light and dark documentation contexts.
4. **No edge may cross an unrelated box or label.** Reserve routing corridors first.

## Routing recipe
Do not rely on `orthogonalEdgeStyle` to avoid every intermediate obstacle. Pin long
edges using explicit `exitX/exitY/exitDx/exitDy`, `entryX/entryY/entryDx/entryDy`, and
`<Array as="points"><mxPoint x=".." y=".."/></Array>` inside `mxGeometry`.

- Reserve upper and lower corridors for long horizontal connections.
- Start with inter-container gutters of at least **80 px**, widening them for lane count.
- Reserve internal column gutters for edges that skip intermediate components.
- Offset entry/exit anchors sharing a border, for example `entryY=0.42` and `0.52`.
- Derive all coordinates from the current layout; do not reuse another diagram's values.

### Lane discipline: no crossings or overlaps
1. **One lane per edge.** Keep parallel segments at least **16 px** apart wherever
   their spans overlap, except for an explicitly modeled shared bus. Maintain a lane
   registry while routing. Disjoint spans may reuse the same coordinate.
2. **Prefer the shortest clear route.** Exit through the side facing the target and
   use a straight segment when it is unobstructed.
3. **Separate opposing directions.** Use distinct horizontal lanes and vertical
   approaches so elbows do not coincide.
4. **Check geometry before rendering.** Expand waypoints into actual orthogonal
   segments; check box intersections, perpendicular edge intersections, collinear
   overlaps, and parallel clearances. Waypoint comparisons alone miss crossings.
5. **Inspect the rendered PNG.** Any accidental X or overlapping/doubled stroke is
   a failure, even outside containers. Reroute and render again.

If the graph cannot be drawn without crossings in one view, split it into clearly
linked views or introduce labeled continuation connectors without losing relationships.
Do not hide a dependency merely to pass the layout check.
Generated SVG paths must preserve the source routing using orthogonal `M`/`L` segments,
arrow markers, and movable groups such as `<g transform="translate()">`.

## Microsoft icons: priority source and fallback
**For each component, follow this search order:**

1. **Priority source — [az-icons.com](https://az-icons.com/).** Search the Microsoft
   icon matching the service and use its SVG. Verify the real download link the site
   provides; never invent an icon path. az-icons.com is a community catalog (not a
   Microsoft publisher) mirroring the Azure architecture pack, so confirm the exact
   service and current branding for the asset you select.
2. **Fallback — this skill's bundled references below**, drawn from
   [MsiconsCollections](https://aka.ms/MsiconsCollections) (Azure / Fabric / Entra /
   Microsoft 365 / Power Platform), when the priority source lacks a suitable icon or
   is unreachable. Resolve and verify the real asset path before use.

The other approved catalogs below remain valid for verification and for products not
covered by the two sources above. Verify the identity and provenance of each selected
asset; multiple sources may appear in one diagram.

| Source | Use and provenance |
| --- | --- |
| [az-icons.com](https://az-icons.com/) | **Priority source.** Community catalog of Azure SVG/PNG assets sourced from the Azure architecture pack; search by service, use the real download link it exposes, and verify the exact service and current branding. |
| [MsiconsCollections](https://aka.ms/MsiconsCollections) | **Fallback.** Broad collection behind this skill's bundled path references (Azure / Fabric / Entra / Microsoft 365 / Power Platform); resolve the link and verify the selected pack and asset. |
| [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/icons/) | Microsoft-published Azure SVG pack, update history, and usage terms; authoritative reference to confirm Azure service icons. |
| [Power Platform icons](https://learn.microsoft.com/en-us/power-platform/guidance/icons) | Microsoft-published Power Platform SVG pack, update history, and usage terms; preferred reference for these products. |
| [DamoBird365/microsoft-cloud-icons](https://github.com/DamoBird365/microsoft-cloud-icons/tree/master) | Community-curated Microsoft Cloud product SVG/PNG collection; use its `icons.json` index and verify the asset, revision, and trademark notice. |

Do not use FontAwesome, unverified built-in mxGraph service icons, arbitrary images,
or hand-drawn replacement logos to stand in for Microsoft products.
Plain labeled rectangles and connectors are diagram primitives, not substitute icons.

- Resolve download links from the selected source rather than guessing filenames or
   freezing a pack version or icon count into the workflow. For MsiconsCollections,
   its previously used asset base is
  `https://tomkiljo.github.io/ms-icons/icons/`; verify that it still belongs to the
   linked collection before using it. Official archives and raw asset URLs linked by
   the approved sources are valid download endpoints.
- Search by exact product/service name and current or former names. Start at the
   priority source (az-icons.com); if it lacks the correct icon or is unreachable,
   use this skill's bundled MsiconsCollections references, then the other relevant
   approved sources before declaring it missing. Prefer semantic accuracy and current
   branding over matching a pack's style.
   Resolve conflicting variants against the current Microsoft product guidance.
- Record the source page, asset path, resolved download URL, and pack version or commit
   (where available). Record the retrieval date when no version is exposed. For community
   assets, verify their claimed Microsoft origin against official guidance where possible;
   do not treat a repository description as proof for every file.
- Reuse cached assets only with known provenance. If relevant sources are unavailable
   or no verified match exists, disclose which checks failed and use a labeled rectangle
   without an icon. Never silently substitute another product's logo.
- Follow the source's usage terms and Microsoft trademark guidance. Keep the product
   name near the icon; preserve its colors, shape, and aspect ratio. Do not crop, flip,
   rotate, distort, or use a Microsoft icon to represent a custom product.
- In drawio, use `shape=image;image=<URL>` or a label node with
  `image=<URL>;imageAlign=left;imageVerticalAlign=middle`.
- Verify the selected source and asset meaning. Do not relabel a generic Microsoft
  logo as a dedicated Microsoft 365, Teams, or Graph product logo. Building glyphs such
  as `office01..14` are not Office product logos.

### Fallback reference: MsiconsCollections paths (non-exhaustive)
These bundled paths are the fallback lookup candidates when az-icons.com lacks the
icon or is unreachable; they are not a claim of current availability or an instruction
to add these services, and they do not limit discovery to this collection.
Verify each selected path before use and check newer packs for renamed products.

```text
# Historical base: https://tomkiljo.github.io/ms-icons/icons/
# Verify that it is still linked by https://aka.ms/MsiconsCollections before use.
Function Apps        Azure_Public_Service_Icons/Icons/compute/10029-icon-service-Function-Apps.svg
Storage Accounts     Azure_Public_Service_Icons/Icons/storage/10086-icon-service-Storage-Accounts.svg
Managed Identities   Azure_Public_Service_Icons/Icons/identity/10227-icon-service-Managed-Identities.svg
Application Insights  Azure_Public_Service_Icons/Icons/management%20+%20governance/00012-icon-service-Application-Insights.svg
AI Studio / Foundry  Azure_Public_Service_Icons/Icons/ai%20+%20machine%20learning/03513-icon-service-AI-Studio.svg
Azure OpenAI         Azure_Public_Service_Icons/Icons/ai%20+%20machine%20learning/03438-icon-service-Azure-OpenAI.svg
Cognitive Search     Azure_Public_Service_Icons/Icons/ai%20+%20machine%20learning/10044-icon-service-Cognitive-Search.svg
Cognitive Services   Azure_Public_Service_Icons/Icons/ai%20+%20machine%20learning/10162-icon-service-Cognitive-Services.svg
Entra ID (color)     Microsoft_Entra_architecture_icons/Microsoft%20Entra%20color%20icons%20SVG/Microsoft%20Entra%20ID%20color%20icon.svg
Microsoft logo      Azure_UX_Patterns_icons/microsoft.svg
Microsoft squares   Azure_UX_Patterns_icons/microsoft-square.svg
Copilot             Azure_UX_Patterns_icons/copilot.svg
Fabric (general)    Microsoft_Fabric_icons/general/<lakehouse_64_item|sql_database_64_item|data_warehouse_64_item|event_house_64_item|power_bi_32_color|notebook_64_item|one_lake_48_color|function_64_item|copilot_48_color|app_development_48_color|fabric_48_color|data_factory_48_color>.svg
Teams Bot            Microsoft_365_Content_Icons/Teams%20Purple/48x48%20Dark%20Purple%20Icon/Bot.svg
Teams Chat (client)  Microsoft_365_Content_Icons/Teams%20Purple/48x48%20Dark%20Purple%20Icon/Chat.svg
Person              Microsoft_365_Content_Icons/Microsoft%20Blue/48x48%20Dark%20Blue%20Icon/Person.svg
Container Registry   Azure_Public_Service_Icons/Icons/containers/10105-icon-service-Container-Registries.svg
Container Apps Env   Azure_Public_Service_Icons/Icons/other/02989-icon-service-Container-Apps-Environments.svg
Worker Container App Azure_Public_Service_Icons/Icons/other/02884-icon-service-Worker-Container-App.svg
Service Bus          Azure_Public_Service_Icons/Icons/integration/10836-icon-service-Azure-Service-Bus.svg
Cosmos DB            Azure_Public_Service_Icons/Icons/databases/10121-icon-service-Azure-Cosmos-DB.svg
PostgreSQL Flexible  Azure_Public_Service_Icons/Icons/databases/10131-icon-service-Azure-Database-PostgreSQL-Server.svg
Azure Maps           Azure_Public_Service_Icons/Icons/iot/10185-icon-service-Azure-Maps-Accounts.svg
Log Analytics        Azure_Public_Service_Icons/Icons/analytics/00009-icon-service-Log-Analytics-Workspaces.svg
Virtual Networks     Azure_Public_Service_Icons/Icons/networking/10061-icon-service-Virtual-Networks.svg
Subnet               Azure_Public_Service_Icons/Icons/networking/02742-icon-service-Subnet.svg
NAT Gateway          Azure_Public_Service_Icons/Icons/networking/10310-icon-service-NAT.svg
Public IP            Azure_Public_Service_Icons/Icons/networking/10069-icon-service-Public-IP-Addresses.svg
Private Endpoints    Azure_Public_Service_Icons/Icons/other/02579-icon-service-Private-Endpoints.svg
DNS Zones           Azure_Public_Service_Icons/Icons/networking/10064-icon-service-DNS-Zones.svg
Browser (SPA/client) Azure_Public_Service_Icons/Icons/general/10783-icon-service-Browser.svg
Globe (external API) Azure_Public_Service_Icons/Icons/general/10808-icon-service-Globe-Success.svg
Keys                Azure_Public_Service_Icons/Icons/menu/00787-icon-service-Keys.svg
Azure Bot Service   Azure_Public_Service_Icons/Icons/ai%20+%20machine%20learning/10165-icon-service-Bot-Services.svg
Fabric Copilot      Microsoft_Fabric_icons/general/copilot_48_color.svg
Policy              Azure_Public_Service_Icons/Icons/management%20+%20governance/10316-icon-service-Policy.svg
```
Preserve URL encoding in paths (for example `%20` for spaces); avoid double encoding.
The Fabric alternatives above describe individual filenames, not one literal URL.

## Foundry pattern (only when present)
Apply this pattern only when the implementation actually uses a Foundry project and
Agent Service. Application agents, development assistants, and Azure Bot Service are
not interchangeable with Foundry-hosted agents.

1. Show the project as a dedicated square-cornered dashed frame with a short title and
   a small verified Foundry icon. Use the current diagram palette, not a fixed theme.
2. Place each actual agent near its dependencies, with enough room around its edges.
   Use a titled rectangle with an internal icon for long names rather than a caption
   that overflows into neighboring components. Show the actual agent count if useful.
3. Distinguish **model**, **knowledge**, and **tool** connections where they exist.
   Use solid lines for model/knowledge and dashed lines for tools, with a legend or
   short labels. Connect to the real deployment, data source, or API. Do not invent
   any of these connections; ordinary retrieval is not automatically Foundry IQ.
4. Keep external resources outside the project ownership boundary, even when a project
   connection points to them. Distinguish integration from resource ownership.
5. Verify current icon availability across the relevant approved sources, including the
   current Azure pack for Foundry Projects, Models, and Agent Service. If there is no dedicated
   Agent Service icon, use the verified Foundry platform icon with an explicit label.
   Do not substitute the Azure Bot Service icon for a Foundry agent.
6. Show a Teams or other publication surface only when it is implemented, using an
   accurately labeled asset from an approved source or an icon-free rectangle.

## Prevent label overlaps
- For 48 px icons with two-line captions, start with at least **150 px** center spacing;
  measure the rendered text and widen, shorten, wrap, or stack nodes as necessary.
- Never place an edge label over an icon, another label, or a routing corridor.
  Open a gutter of at least **40 px** and use a short label that fits, or remove the
  edge label (`value=""`) and put the connection type in the target caption or legend.
- Verify the actual renderer's handling of `verticalLabelPosition`, `align`, wrapping,
  and offsets. Do not assume all exporters honor the same mxGraph styles.
- Keep routing corridors clear of every box and caption, including container titles.

## Rendering and validation
The `.drawio` file is the **single source of truth**. Generate SVG and PNG from it;
do not hand-edit exports independently.

1. Reuse the repository's renderer or an available drawio exporter. Do not assume
   headless Chrome, a CLI, Node.js, or a particular script path is installed.
2. If no exporter is available, state the limitation and agree on a fallback. A Node
   mxGraph-to-SVG converter plus `@resvg/resvg-js` is an option, but must support the
   source's styles, text, parent offsets, and routing; do not silently drop features.
3. Prefer SVG assets from the approved sources and inline them as nested `<svg>`
   elements with `viewBox`. If only a verified PNG is available, embed it as a data URI
   without upscaling beyond usable resolution; do not invent a vector replacement.
   Prefix IDs per instance and update references to gradients, masks, and clip paths.
   Remove scripts and external asset references; do not load fonts, CSS, or images
   over the network. XML namespace URIs and local `url(#id)` references are allowed.
4. Default omitted numeric coordinates to zero when parsing mxGraph. Derive orthogonal
   elbows from anchors and waypoints rather than connecting waypoints diagonally.
5. Parse both XML files, run available geometry checks, rasterize the SVG at the
   consumer's required resolution, then inspect the PNG and its documentation embedding.
   Report unavailable checks instead of claiming they passed.

### Arrowheads
- End each arrow perpendicular to, and touching, the target boundary.
- Keep the final approach segment at least **15 px** long to avoid unstable orientation.
- Set `entryX/entryY` explicitly on the intended border.
- Verify marker support in the selected renderer. For end markers, `orient="auto"`
  is a useful fallback when `auto-start-reverse` renders incorrectly. Inspect upward,
  downward, leftward, and rightward arrows wherever those directions occur.

## Update triggers and consumer synchronization
Update the source and regenerate its exports when a change affects the architecture
depicted: components, dependencies, runtime agents, networks, identity, ingress, or
deployment boundaries. Discover relevant IaC/code paths rather than hardcoding them.
A formatting-only IaC edit or a development-assistant instruction change does not by
itself require a runtime diagram update.

Find existing references to the diagram in documentation and presentations. Update
paths, captions, copies, and rendered decks **only where those consumers exist**.
Do not assume a video directory, slide framework, or deck is present, and do not
create one solely to satisfy this skill. Keep updates together in the proposed change;
respect repository commit rules and publish only when authorized.

## Verification checklist
Mark conditional items not applicable with a reason rather than inventing components.

- [ ] Paths, labels, stable IDs, dependencies, and boundaries reflect the current project.
- [ ] Icons were sought at the priority source (az-icons.com) first, then the bundled
   MsiconsCollections fallback and other approved sources; discovery was not limited to
   the inherited MsiconsCollections path list.
- [ ] Each icon's product identity, current variant, provenance, source/download URLs,
   version or retrieval date, and usage terms are checked; community catalogs are not mislabeled as Microsoft publishers.
- [ ] Missing matches were sought in other relevant approved sources before using
   labeled rectangles without substitute logos; unavailable sources and verification gaps are disclosed.
- [ ] Logical columns, square corners, facing boundary placement, and readable colors are preserved.
- [ ] If Foundry is present: actual agents and existing typed connections are shown;
      ownership is distinct from integration. Otherwise the Foundry pattern is not applicable.
- [ ] No icon, box, edge label, caption, or container title overlaps another or a routing corridor.
- [ ] Drawio and SVG XML parse successfully; SVG and PNG were generated from the same source.
- [ ] No edge crosses an unrelated box; no accidental edge crossing or overlapping stroke exists,
      including outside containers. Shared buses are explicit; overlapping parallel spans are 16 px apart.
- [ ] Geometry checks cover full segments, not just waypoints; rendered PNG was visually inspected.
- [ ] Arrowheads touch target borders perpendicularly, with at least 15 px final approaches;
      every direction present in the diagram was checked in the rendered output.
- [ ] SVG contains embedded verified icons, unique IDs, and no external asset dependencies;
   icon appearance and aspect ratios are preserved.
- [ ] Existing documentation/deck consumers are synchronized and their image links resolve;
      absent consumers are marked not applicable.
- [ ] Temporary artifacts are cleaned up; unavailable checks are disclosed; no unauthorized commit or push.
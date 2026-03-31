import { registryCategories } from "@/registry/registry-categories"
import { registryCollections } from "@/registry/registry-collections"
import blocksMetadata from "@/registry/__blocks__.json"

const BASE_URL = "https://www.creative-tim.com/ui"

type BlockMeta = {
  name: string
  description: string
  categories: string[]
}

export async function GET() {
  const blocks = blocksMetadata as BlockMeta[]

  // Group blocks by category slug
  const byCategory: Record<string, BlockMeta[]> = {}
  for (const block of blocks) {
    for (const cat of block.categories) {
      if (!byCategory[cat]) byCategory[cat] = []
      byCategory[cat].push(block)
    }
  }

  const lines: string[] = []

  lines.push("# Creative Tim UI — Blocks & Components Library")
  lines.push(
    "> 390+ ready-to-use React/Next.js UI blocks built on shadcn/ui and Tailwind CSS."
  )
  lines.push(
    "> Built by Creative Tim — 300+ open source UI products used by 2.8 million developers over the last decade."
  )
  lines.push(
    "> Docs: https://www.creative-tim.com/ui/docs"
  )
  lines.push(
    "> API key required for PRO blocks — get one at: https://www.creative-tim.com/ui/pricing"
  )
  lines.push("")

  lines.push("## Installation")
  lines.push("")
  lines.push("### Option 1 — Creative Tim CLI (recommended)")
  lines.push("```bash")
  lines.push("# Add a block by name")
  lines.push("npx @creative-tim/ui@latest add banner-01")
  lines.push("")
  lines.push("# Add multiple blocks")
  lines.push("npx @creative-tim/ui@latest add banner-01 hero-01 navbar-with-search")
  lines.push("```")
  lines.push("")
  lines.push("### Option 2 — shadcn CLI with full registry URL")
  lines.push("```bash")
  lines.push("# Add a block via the shadcn CLI")
  lines.push(
    "npx shadcn@latest add https://www.creative-tim.com/ui/r/banner-01.json"
  )
  lines.push("```")
  lines.push("")
  lines.push(
    "Replace `banner-01` with any block name listed below."
  )
  lines.push("")

  lines.push("## AI Agent Skill")
  lines.push("")
  lines.push(
    "An agent skill is available for Claude Code, Cursor, Cline, and 40+ other AI coding agents."
  )
  lines.push(
    "It encodes Creative Tim's design philosophy, all install commands, PRO API key setup, and design rules — so agents generate blocks consistently without being told each time."
  )
  lines.push("")
  lines.push("```bash")
  lines.push("npx skills add creativetimofficial/ui")
  lines.push("```")
  lines.push("")
  lines.push(
    "Skill source: https://github.com/creativetimofficial/ui/tree/main/skills/creative-tim-ui"
  )
  lines.push(
    "Skill page: https://skills.sh/creativetimofficial/ui/creative-tim-ui"
  )
  lines.push("")

  lines.push("## Collections")
  lines.push("")
  for (const collection of registryCollections) {
    lines.push(
      `- [${collection.name}](${BASE_URL}/blocks/${collection.slug}): ${collection.description}`
    )
  }
  lines.push("")

  lines.push("## Categories & Blocks")
  lines.push("")

  const visibleCategories = registryCategories.filter((c) => !c.hidden)

  for (const category of visibleCategories) {
    const categoryBlocks = byCategory[category.slug] ?? []
    if (categoryBlocks.length === 0) continue

    // Find which collection this category belongs to
    const collection = registryCollections.find((col) =>
      col.categories.includes(category.slug)
    )
    const browsePath = collection
      ? `${BASE_URL}/blocks/${collection.slug}/${category.slug}`
      : `${BASE_URL}/blocks`

    lines.push(`### ${category.name}`)
    lines.push(`> ${category.description}`)
    lines.push(`> Browse: ${browsePath}`)
    lines.push("")

    for (const block of categoryBlocks) {
      lines.push(
        `- [${block.name}](${BASE_URL}/r/${block.name}.json): ${block.description}`
      )
    }
    lines.push("")
  }

  lines.push("## Full Registry")
  lines.push("")
  lines.push(
    `Machine-readable registry JSON: ${BASE_URL}/r/registry.json`
  )

  const text = lines.join("\n")

  return new Response(text, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
    },
  })
}

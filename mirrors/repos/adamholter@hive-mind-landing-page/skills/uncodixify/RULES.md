# Uncodixify

Use this ruleset to remove default AI-UI habits and replace them with deliberate, grounded frontend decisions.

## Core stance

- Treat the first viewport as one composition, not a pile of modules.
- Preserve the existing design system when one already exists.
- Prefer restraint over filler. If an element does not improve interaction, clarity, or brand presence, remove it.
- Use visual hierarchy and motion to create presence, not noise.

## Composition rules

- Build one clear job per section: one purpose, one headline, usually one short supporting sentence.
- Keep the first viewport focused. Do not turn it into a dashboard unless the product is actually a dashboard.
- For landing pages and promotional surfaces, use a full-bleed hero by default.
- Use one dominant visual anchor in the hero. Decorative gradients alone do not count as the main idea.
- Do not place stats, schedules, address blocks, event listings, promos, metadata rows, or secondary marketing content in the first viewport.

## Brand rules

- Make the brand or product name a hero-level signal on branded pages.
- Do not let a generic marketing headline overpower the brand.
- Apply the brand test: if the first viewport could belong to another brand after removing the nav, the branding is too weak.

## Hero rules

- Keep the hero budget tight: brand, one headline, one short supporting sentence, one CTA group, and one dominant image.
- Use edge-to-edge hero media or a dominant background plane by default.
- Do not use inset hero images, side-panel hero media, rounded media cards, tiled collages, or floating image blocks unless the existing system clearly requires them.
- Do not place detached labels, floating badges, promo stickers, info chips, or callout boxes on top of hero media.
- Do not use cards in the hero.

## Card rules

- Default to no cards.
- Only use a card when it is clearly the container for a user interaction.
- If removing a border, shadow, background, or radius does not hurt understanding or interaction, it should not be a card.
- Avoid repeated rounded rectangles across the whole interface.

## Typography rules

- Use expressive, purposeful fonts.
- Avoid default stacks and overused UI fonts such as `Inter`, `Roboto`, `Arial`, and generic system defaults unless the product already uses them.
- Avoid eyebrow labels, decorative pre-headings, and tiny uppercase support labels above headlines.
- Keep hierarchy clear and direct. Do not use copy that sounds like placeholder startup marketing.

## Color and background rules

- Define CSS variables for the palette.
- Choose a clear visual direction instead of timid balanced color use.
- Avoid purple-on-white defaults and generic dark SaaS blue-black gradients.
- Do not rely on a flat single-color background when atmosphere matters; use gradients, imagery, textures, or subtle patterns with intent.

## Motion rules

- Ship at least two or three intentional motions for visually led work.
- Use motion to establish hierarchy, load-in presence, and focus.
- Avoid hover gimmicks, bouncy transforms, and motion that exists only to decorate.

## Clutter rules

- Remove pill clusters, stat strips, icon rows, boxed promos, schedule snippets, and competing text blocks unless they are essential.
- Avoid fake charts, filler metrics, and decorative product meta.
- Do not add “live”, “focus”, “operator”, or similar labels unless they are true product language.

## Red flags

- Hero sections inside internal dashboards without a real product reason.
- Floating glass panels, frosted shells, glow-heavy cards, or generic “premium SaaS” styling.
- Overpadded layouts, dead space used to fake sophistication, or mobile layouts that just stack the desktop design into a long bland column.
- Rounded spans, badge clutter, or repeated pills as a styling crutch.

## Decision rule

- If a UI move feels like a default AI-generated choice, reject it and choose the cleaner, more specific option.

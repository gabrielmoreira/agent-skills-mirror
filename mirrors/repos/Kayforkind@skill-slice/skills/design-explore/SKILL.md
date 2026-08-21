---
name: design-explore
description: "Generates multiple standalone HTML design explorations of one UI component, each in a different company design language, then adapts the winner into the real theme. Use when the user wants design options, a design sprint, or to compare UI approaches for a self-contained component. Not for implementing an already-specified restyle (hex/fonts/spacing), full-page redesigns, or design-system token architecture without exploration."
version: 1.0.1
---

## When to Use
Use this skill for interface design, UX review, accessibility, responsive layouts, design systems, mobile/web UI, component behavior, interaction states, visual hierarchy, usability improvements, and frontend implementation guidance.

This skill fits when:
- The codebase has a real theme system (CSS variables, light/dark) and standalone HTML can mirror it.
- The feature is a self-contained component (panel, toggle, picker, thread, card) not a whole page.
- The user wants creative range, not a precise restyle.

## Prerequisites
- Windows host is primary (PowerShell). Ensure paths use Windows conventions (e.g., `~\agent-skills\library\design-explore\`).
- The codebase must have a real theme system (CSS variables, light/dark) that standalone HTML can mirror.

## Procedure

### 1. Gather Inputs
Parse the user's request for:
- **Feature description**: what UI component or interaction to redesign (REQUIRED, ask if unclear).
- **Companies**: comma-separated list of company names (OPTIONAL, defaults to: GitHub, Linear, Raycast, Vercel, Monzo).
- **File/selector**: a specific file and CSS selector or code region to focus on (OPTIONAL, ask if not provided).

### 2. Identify the feature
If the feature isn't clear, ask what component or interaction is being explored and where it is currently implemented.
Read the current implementation. Identify:
- The **HTML structure** (what elements, what classes)
- The **CSS** (what styles, what theme variables are used)
- The **JS behavior** (interactions, state, events)
- The **theme system** (what CSS custom properties exist, light/dark support)

### 3. Create the base HTML
Build a standalone HTML file that reproduces the current component in isolation:
1. Extract the relevant CSS custom properties from the theme system (both dark and light values).
2. Include a theme toggle (Dark/Light buttons, fixed top-right).
3. Show the component in multiple states (e.g., collapsed, expanded, with short content, with long content, with code content).
4. Include a normal/non-affected variant for visual comparison.
5. Mark the redesign zone with comments: `/* THIS IS THE PART TO REDESIGN */` and `/* END REDESIGN ZONE */`.

Save to: `.design-exploration/{feature-slug}/base.html`

**Show the user the base HTML path and ask them to open it in a browser to verify it matches the current implementation before proceeding.**

### 4. Show the user the plan
Before dispatching agents, present:
- The list of companies and a 2-3 sentence brief for each.
- Confirm the user is happy with the selection.

The briefs should be open-ended, describing the company's design philosophy and asking the agent to research and apply it. Do NOT prescribe specific UI patterns (no "add an icon", "use a left border", etc.). Let each agent discover the right UX through research.

### 5. Dispatch design agents
Spawn one agent per company, **all in parallel**, each with `run_in_background: true` if the harness supports it.

Each agent gets the same prompt structure:

```text
You are a world-class designer. Your task is to redesign [FEATURE DESCRIPTION] in [PRODUCT CONTEXT].

**Context**: [2-3 sentences explaining what the feature does, what problem it solves, who uses it]

**Starting point**: Copy the file at [BASE HTML PATH] to a new file at [OUTPUT PATH]. The base file contains the current implementation with theme toggle (dark/light). The section between `/* THIS IS THE PART TO REDESIGN */` and `/* END REDESIGN ZONE */` is what you're reimagining but you're free to change any part of the component if the UX calls for it.

**The current theme palette**: [LIST KEY COLORS FROM BOTH DARK AND LIGHT THEMES backgrounds, text, accents, borders, warnings]. You can extend the palette with new CSS variables if your design calls for it define them for both dark and light themes.

**Constraints**: Single HTML file, vanilla CSS/JS only, must work in both themes. [ANY ADDITIONAL CONSTRAINTS e.g., XSS safety, accessibility requirements]. Beyond that, be creative with both the visual design AND the interaction design.

You are a world-class designer at **[COMPANY]**. Research [COMPANY]'s design philosophy [OPEN-ENDED BRIEF ABOUT THE COMPANY'S AESTHETIC AND APPROACH]. Study how [COMPANY] handles [RELEVANT PATTERN]. Then apply that thinking to this feature. [OPEN-ENDED QUESTION ABOUT THE KEY DESIGN TENSION].
```

Output paths: `.design-exploration/{feature-slug}/{company-slug}.html`

The company-specific brief must:
- Ask the agent to **research** the company's design language first.
- Reference specific product areas to study (not specific UI patterns to copy).
- Pose an open-ended design question relevant to the feature.
- NOT prescribe solutions (no "use a chevron", "add a border", "put an icon").

### 6. Report results
As each agent completes, briefly report:
- Company name
- Key UX decisions they made (from the agent's summary)
- File path

When all agents are done, present a comparison table:

| File | Key UX idea |
|-------------------|------------------------------------------------|
| github.html | [one-line summary] |
| linear.html | [one-line summary] |
| ... | ... |

Tell the user: "Open these from `.design-exploration/{feature-slug}/` each has a dark/light toggle. Pick the one you like and I'll adapt it to the actual codebase."

### 7. Adapt the winner
When the user picks a design:
1. Read the winning HTML file.
2. Read the current implementation in the actual codebase.
3. Adapt the winning design to use the project's real theme variables (not the standalone file's simplified palette).
4. Update the actual source files (JS, CSS, and theme CSS if new variables are needed).
5. Build and verify.

Do NOT blindly copy the standalone HTML into the codebase. The standalone file may have simplified the theme, used different variable names, or changed non-redesign-zone code. Adapt intelligently.

### 8. Cleanup
The `.design-exploration/` directory and its files are ephemeral; they exist for comparison only. The dot-prefix signals "local working files, don't commit." If the project doesn't already ignore it, add `.design-exploration/` to `.gitignore`. Don't clean them up automatically (the user may want to reference past explorations later).

## Pitfalls
- **Wrong tool**: If the user gave exact specs (hex codes, fonts, spacing), that's an implementation request; just implement it.
- **Heavy framework**: If the component lives inside a heavy framework with no easy standalone reproduction (e.g., a deeply-nested React component bound to a design system), adapt the approach or skip.
- **Full page**: If the feature is a full page, not a component, it's too much surface for parallel exploration.
- **Blind copying**: Do not blindly copy the standalone HTML into the codebase. The standalone file may have simplified the theme, used different variable names, or changed non-redesign-zone code.
- **Prescriptive briefs**: Do not prescribe specific UI patterns (no "add an icon", "use a left border", etc.) in the agent briefs. Let each agent discover the right UX through research.
- **Accessibility conflicts**: If requirements conflict, prioritize usability, accessibility, and product fit over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant.

## Verification
- Verify the base HTML matches the current implementation by opening it in a browser.
- Verify each generated HTML file works in both dark and light themes.
- Verify the winning design is adapted to use the project's real theme variables.
- Run the project's build and verify the adapted component works correctly.
- Check accessibility: semantic structure, labels, keyboard flow, focus, contrast, target size, and reduced motion.
- Test with real content, longest labels, mobile/desktop, zoom, dark/light modes, and interaction paths.

## References
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

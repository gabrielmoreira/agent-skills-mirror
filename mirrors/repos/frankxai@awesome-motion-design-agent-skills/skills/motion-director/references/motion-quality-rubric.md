# Motion Quality Rubric

Score each category 0-3.

| Category | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Purpose | Decorative noise | Slightly related | Supports comprehension | Makes the interface clearer or more memorable |
| Timing | Jerky or slow | Inconsistent | Mostly smooth | Crisp, intentional, and responsive |
| Hierarchy | Competes with content | Distracts | Guides attention | Choreographs attention elegantly |
| Brand Fit | Generic | Weakly aligned | Recognizable | Ownable motion language |
| Accessibility | Ignores reduced motion | Partial fallback | Has reduced-motion path | Reduced-motion path is designed, not just disabled |
| Performance | Drops frames | Heavy on mobile | Acceptable | Smooth on target devices |
| Implementation | Fragile hacks | Works but brittle | Maintainable | Tokenized, reusable, and testable |

## Pass Bar

- 15+ for public demos.
- 18+ for brand/product launches.
- 20+ for premium Arcanea/Starlight surfaces.

## Anti-Patterns

- Animating everything just because we can.
- Long delays before usable content.
- Text that moves while the user is trying to read it.
- Scroll hijacking that breaks expected browser behavior.
- No `prefers-reduced-motion` handling.
- Decorative 3D that slows the page without explaining anything.

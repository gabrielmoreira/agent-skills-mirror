---
name: interactive-portfolio
version: 1.1.1
description: "Shapes job-seeking personal sites: thirty-second hero, outcome-led case studies, hybrid home-plus-project routes, and frictionless contact CTAs, with heavy motion that degrades on mobile. Use for developer, designer, or creative portfolio work. Not a SaaS marketing landing page and not a WebGL engine tutorial."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use
- User mentions or implies: portfolio, personal website, showcase work, developer portfolio, designer portfolio, or creative portfolio.
- User needs help structuring projects, case studies, or hero sections for a personal site.
- User wants to improve conversion rates (CTAs, contact methods) on an existing portfolio.
- User is planning interactive elements (animations, 3D, scroll effects) for a portfolio.

## Prerequisites
- Basic understanding of frontend technologies (HTML/CSS/JS, React/Next.js) if implementing the portfolio directly.
- 3-5 completed projects or case studies ready to be showcased.

## Procedure

### 1. Portfolio Architecture
Structure the portfolio to pass the "30-Second Test". In 30 seconds, visitors should know:
1. Who you are.
2. What you do (Your unique value proposition).
3. Your best work (Proof of competence).
4. How to contact you (Clear path to conversion).

**Essential Sections**
| Section | Purpose | Priority | 2026 Best Practice |
|---------|---------|----------|----------------------|
| Hero | Hook + identity | Critical | High-impact visual + clear UVP |
| Work/Projects | Prove skills | Critical | Quality over quantity; focus on outcomes |
| About | Personality + story | Important | Humanize the developer/designer |
| Contact | Convert interest | Critical | Frictionless contact (Calendly/Email/LinkedIn) |
| Testimonials | Social proof | Nice to have | Verified LinkedIn screenshots or quotes |
| Blog/Writing | Thought leadership | Optional | Proof of communication & deep thinking |

**Navigation Patterns**
- **Single page scroll**: Best for designers, creatives, junior devs. Works well with animations (GSAP/Framer Motion). Mobile friendly, linear storytelling.
- **Multi-page**: Best for senior roles, extensive project lists. Individual case study pages (Better for SEO/Deep dives). Professional, structured feel.
- **Hybrid (Recommended)**: Main sections on one page (Home). Detailed case studies on separate routes (`/project/name`). Best of both worlds: Quick scan + deep dive.

**Hero Section Formula**
```
[Your name]
[What you do in one line - e.g., "Frontend Engineer specializing in High-Performance Web Apps"]
[One line that differentiates you - e.g., "Bridging the gap between complex backend logic and pixel-perfect UI"]
[CTA: View Work / Get in Touch]
```

### 2. Project Showcase
Present work effectively using structured project cards and case studies.

**Project Card Elements**
| Element | Purpose | 2026 Standard |
|---------|---------|----------------|
| Thumbnail | Visual hook | High-res WebP/AVIF or short looping video |
| Title | What it is | Descriptive and clear |
| One-liner | What you did | Action-oriented (e.g., "Architected the API for...") |
| Tech/tags | Quick scan | Modern stack (e.g., Next.js 15, TypeScript, Tailwind) |
| Results | Proof of impact | Quantifiable metric (e.g., "Reduced load time by 40%") |

**Case Study Structure**
1. Hero image/video (The "Money Shot")
2. Project overview (2-3 sentences: Goal, Role, Outcome)
3. The challenge (The problem you were solving)
4. Your role (Specific contributions in a team)
5. Process highlights (Wireframes, logic flow, architectural diagrams)
6. Key decisions (Why you chose X over Y - shows seniority)
7. Results/impact (Metrics, user feedback, business value)
8. Learnings (What you'd do differently next time)
9. Links (Live site, GitHub, Case study PDF)

**Showing Impact**
| Instead of | Write |
|------------|-------|
| "Built a website" | "Increased conversion rate by 40% via A/B testing" |
| "Designed UI" | "Reduced user drop-off by 25% by simplifying checkout" |
| "Developed features" | "Shipped a feature used by 50K+ monthly active users" |
| "Used React" | "Optimized rendering performance, reducing LCP by 1.2s" |

**Visual Presentation**
- Device mockups (Responsive views)
- Before/after comparisons (Slider components)
- Process artifacts (Figma screenshots, whiteboard sketches)
- Video walkthroughs (Loom or short clips for complex work)
- Micro-interactions (Hover effects that reveal details)

### 3. Developer Portfolio Specifics
Hiring managers look for code quality, real-world projects, problem-solving ability, communication skills, and technical depth.

**Must-Haves**
- GitHub profile link (Pinned repos, active contributions)
- Live project links (Deployed via Vercel/Netlify/AWS)
- Tech stack for each project (Explicitly listed)
- Your specific contribution (Crucial for team projects)

**Project Selection**
| Include | Avoid |
|---------|-------|
| Real problems solved | Tutorial clones (Todo lists, Weather apps) |
| Side projects with actual users | Incomplete "Coming Soon" projects |
| Open source contributions | Basic CRUD apps without a unique twist |
| Technical challenges solved | Generic portfolio templates |

**Technical Showcase**
Show code snippets that demonstrate clean architecture, custom hooks, memoization, and typing:
```typescript
import { useState, useCallback, useMemo, useEffect } from 'react';

interface UseDebounceStateOptions<T> {
  delay?: number;
  onDebounceUpdate?: (value: T) => void;
}

export function useDebounceState<T>(
  initialValue: T,
  options: UseDebounceStateOptions<T> = {}
) {
  const { delay = 300, onDebounceUpdate } = options;
  const [value, setValue] = useState<T>(initialValue);
  const [debouncedValue, setDebouncedValue] = useState<T>(initialValue);
  const [isPending, setIsPending] = useState<boolean>(false);

  useEffect(() => {
    setIsPending(true);
    const handler = setTimeout(() => {
      setDebouncedValue(value);
      setIsPending(false);
      if (onDebounceUpdate) {
        onDebounceUpdate(value);
      }
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay, onDebounceUpdate]);

  const set = useCallback((newValue: T) => {
    setValue(newValue);
  }, []);

  return useMemo(
    () => ({
      value,
      debouncedValue,
      isPending,
      set,
    }),
    [value, debouncedValue, isPending, set]
  );
}
```

### 4. Portfolio Interactivity
Add memorable interactive elements while balancing creativity with usability.

**Levels of Interactivity**
| Level | Example | Risk |
|-------|---------|------|
| Subtle | Hover effects, smooth scroll, fade-ins | Low |
| Medium | Scroll animations, page transitions, dark mode | Medium |
| High | 3D (Three.js), games, custom cursors, WebGL | High |

**High-Impact, Low-Risk**
- Custom cursor (Desktop only)
- Smooth page transitions (Framer Motion/View Transitions API)
- Project card hover effects (Scale, glow, or detail reveal)
- Scroll-triggered reveals (Intersection Observer)
- Dark/light mode toggle (System preference detection)

**Creative Ideas**
- Terminal-style interface (For backend/systems devs)
- OS desktop metaphor (Interactive windows/icons)
- Game-like navigation (Character movement or quest-based)
- Interactive timeline (Scroll-based career progression)
- 3D workspace scene (Spline/Three.js)
- Generative art background (Canvas/p5.js)

**The Balance**
- Creativity shows skill, but usability wins jobs.
- Mobile must work perfectly (Disable heavy animations on mobile).
- Don't hide content behind interactions (Accessibility first).
- Provide a "Skip Intro" or "Simple View" option for recruiters.

### 5. Conversion & CTAs
Ensure visitors know what to do next.

**Primary CTAs**
| Goal | CTA |
|------|-----|
| Get hired | "Let's work together" |
| Freelance | "Start a project" |
| Network | "Say hello" |
| Specific role | "Hire me for [X]" |

**CTA Placement**
- Hero section: Main CTA (Immediate)
- After projects: Secondary CTA (After proof of skill)
- Footer: Final CTA (Last chance)
- Floating: Optional persistent CTA (Always available)

**Making Contact Easy**
- Email link (`mailto:`)
- LinkedIn (opens in new tab)
- Calendar link (Calendly/TidyCal)
- Simple contact form (with validation)
- "Copy email to clipboard" button

## Pitfalls

### Portfolio more complex than actual work
**Severity:** MEDIUM
**Situation:** Spent 6 months on portfolio, have 2 projects to show.
**Why this breaks:** Procrastination disguised as work. Portfolio IS a project, but not THE project. Diminishing returns on polish.
**Fix:** Right-size your portfolio. Start with an MVP (Hero, 3-4 Projects, About, Contact). Time budget: 4 weeks max. Ship it when core pages work on mobile, 3-4 solid projects are showcased, contact works, and it loads in < 3 seconds. Better projects > better portfolio.

### Portfolio looks great on desktop, broken on mobile
**Severity:** HIGH
**Situation:** Recruiters check on phone, everything breaks.
**Why this breaks:** Built desktop-first. Didn't test on real devices. Complex interactions don't translate to touch. Forgot about thumb zones.
**Fix:** Adopt mobile-first design. 60%+ traffic is mobile. Ensure readable text (16px+), tappable links (min 44x44px), working navigation, fast loading, and sticky CTA. Test on iPhone Safari, Android Chrome, tablets, and slow 3G. Use graceful degradation for hover effects:
```css
@media (hover: none) {
  .hover-effect {
    opacity: 1;
  }
}
```

### Visitors don't know what to do next
**Severity:** MEDIUM
**Situation:** Great portfolio, zero contacts.
**Why this breaks:** No clear CTA. Contact buried at the bottom. Multiple competing actions (Analysis paralysis). Assuming visitors will figure it out.
**Fix:** Add prominent contact CTAs in hero and after projects section. Avoid contact forms as the only option. Don't hide contact info or list too many social options.

### Portfolio shows old or irrelevant work
**Severity:** MEDIUM
**Situation:** Best work is 3 years old, newer work not shown.
**Why this breaks:** Haven't updated in years. Newer work is "not ready" (Perfectionism). Scared to remove old favorites. Portfolio drift.
**Fix:** Update copy every 6 months, tech every 1-2 years. Prune projects if embarrassed by code/design, tech is obsolete, or not relevant to goals. Archive instead of delete if showing growth.

### Hard Rules: Do Not Use
- **Do not use** heavy 3D/WebGL without a fallback or "Skip" option.
- **Do not use** custom cursors on mobile devices.
- **Do not use** "Coming Soon" placeholders (Remove the section entirely).
- **Do not use** PDF resumes as the only way to see your experience.
- **Do not use** non-standard navigation that confuses the user.
- **Do not use** autoplaying audio or intrusive pop-ups.

## Verification

Run through these validation checks before launching:

1. **No Clear Contact CTA (HIGH):** Is there a prominent contact CTA in the hero and after projects section?
2. **Missing Mobile Viewport (HIGH):** Does the HTML include `<meta name='viewport' content='width=device-width, initial-scale=1'>`?
3. **Unoptimized Portfolio Images (MEDIUM):** Are images using WebP/AVIF, lazy loading, and `srcset` for responsive sizes?
4. **Projects Missing Live Links (MEDIUM):** Do projects have live demo URLs or GitHub links?
5. **Projects Missing Impact/Results (LOW):** Do project descriptions include metrics, outcomes, or testimonials?

**Final Checklist**
- [ ] Does the hero section clearly state who the user is and what they do?
- [ ] Are there at least 3 projects with live links or GitHub repos?
- [ ] Does every project include a "Result" or "Impact" statement?
- [ ] Is the site fully responsive and tested on a real mobile device?
- [ ] Is there a clear, frictionless way to contact the user?
- [ ] Does the site load in under 3 seconds (Lighthouse/PageSpeed Insights)?
- [ ] Are images optimized (WebP/AVIF) and lazy-loaded?
- [ ] Is the navigation intuitive and accessible (Keyboard/Screen reader)?

## Related Skills
Works well with: `scroll-experience`, `3d-web-experience`, `landing-page-design`, `personal-branding`, `frontend`, `seo`

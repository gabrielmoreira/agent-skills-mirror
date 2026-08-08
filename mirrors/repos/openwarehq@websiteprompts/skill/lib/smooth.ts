// Continuous inertial scrolling.
//
// The native scrollbar stays real — the page keeps its true height on <body>
// and the browser scrolls it normally. What changes is that the content is
// translated by a value that *chases* window.scrollY instead of matching it,
// so motion is unbroken rather than stepped to the wheel's notches. Nothing
// snaps, nothing sections, and there is no cut anywhere on the page.
//
// Under prefers-reduced-motion none of this runs: the wrapper is left in normal
// flow and the browser scrolls it directly.

export interface Smooth {
  /** current eased scroll position in px */
  y(): number;
  destroy(): void;
}

export function startSmooth(wrap: HTMLElement, ease = 0.085): Smooth {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let current = window.scrollY;
  let raf = 0;
  let ro: ResizeObserver | null = null;

  const setHeight = () => {
    // body carries the real height so the scrollbar and anchor links behave
    document.body.style.height = `${wrap.scrollHeight}px`;
  };

  if (reduced) {
    // leave the browser to it; still report position for the reveal maths
    const onScroll = () => { current = window.scrollY; };
    window.addEventListener('scroll', onScroll, { passive: true });
    return { y: () => current, destroy: () => window.removeEventListener('scroll', onScroll) };
  }

  wrap.style.position = 'fixed';
  wrap.style.top = '0';
  wrap.style.left = '0';
  wrap.style.width = '100%';
  wrap.style.willChange = 'transform';

  setHeight();
  ro = new ResizeObserver(setHeight);
  ro.observe(wrap);
  window.addEventListener('resize', setHeight);

  const tick = () => {
    raf = requestAnimationFrame(tick);
    const target = window.scrollY;
    current += (target - current) * ease;
    // settle exactly, or sub-pixel drift keeps the compositor awake forever
    if (Math.abs(target - current) < 0.06) current = target;
    wrap.style.transform = `translate3d(0, ${-current}px, 0)`;
  };
  raf = requestAnimationFrame(tick);

  return {
    y: () => current,
    destroy() {
      cancelAnimationFrame(raf);
      ro?.disconnect();
      window.removeEventListener('resize', setHeight);
      document.body.style.height = '';
      wrap.removeAttribute('style');
    },
  };
}

/**
 * Continuous 0→1 reveal for an element, from its real position on screen.
 *
 * Deliberately not IntersectionObserver: that fires once at a threshold and
 * hands off to a CSS transition, which is a small animation that runs on its
 * own clock. Reading the rect every frame keeps every element tied to the same
 * scroll value, so a fast flick moves everything together instead of leaving a
 * trail of half-finished transitions.
 */
export function revealAmount(el: Element, startAt = 0.92, endAt = 0.62) {
  const r = el.getBoundingClientRect();
  const h = window.innerHeight;
  const from = h * startAt;
  const to = h * endAt;
  const t = (from - r.top) / (from - to);
  return t < 0 ? 0 : t > 1 ? 1 : t;
}

export const clamp = (v: number, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
export const seg = (p: number, a: number, b: number) => clamp((p - a) / (b - a));

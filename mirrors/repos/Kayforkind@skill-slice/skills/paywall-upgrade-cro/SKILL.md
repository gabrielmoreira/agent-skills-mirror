---
name: paywall-upgrade-cro
version: 1.1.1
description: "Designs in-app paywalls and upgrade flows (feature gates, usage-limit walls, trial-expiration, expansion nudges) so the ask lands after value is already banked. Use when converting free users to paid or moving seats up a tier inside the product. Not for public marketing or pricing pages, and not for first-run onboarding before any aha moment."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Paywall and Upgrade Screen CRO

You are an expert in in-app paywalls and upgrade flows. Your goal is to convert free users to paid, or upgrade users to higher tiers, at moments when they've experienced enough value to justify the commitment.

The throughline: a paywall is not a tollbooth, it is a *handoff*. You are asking someone to trade money for a capability they already want. That trade only feels fair when the want is real and present. Most of the principles, components, and code in this skill exist to make sure the ask lands at the moment the user is already leaning in — and to make sure that when they say no, they still trust you enough to say yes later.

Throughout this skill the examples use one concrete running product — **Tasklane**, a project-management SaaS — so the copy, prices, and code are realistic rather than abstract:

- **Free**: 3 projects, 1 seat, no scheduled exports.
- **Pro**: $12/mo or $108/yr (25% off), unlimited projects, scheduled exports.
- **Team**: $10/seat/mo, shared projects, admin controls.
- **Trial**: 14-day full-access Pro trial, opt-in (no card required).

Swap these for the real product's economics; the structure transfers directly.

## When to Use

Use this skill when you are designing, auditing, or optimizing any in-product moment that asks a user to pay or move up a tier:

- **Feature gates** — user clicks a paid-only feature.
- **Usage-limit walls** — user hits a free-tier ceiling.
- **Trial-expiration screens** — trial winds down.
- **Soft upgrade nudges** — time-based or context-triggered prompts.
- **Solo-to-team prompts** — a solo user exhibiting team-shaped behavior.

Reach for it when conversion or expansion revenue is the goal and you have enough product context — the free/paid boundary, the aha moment, and the current conversion rate — to place the ask where value has already landed.

**Do NOT use this skill for:**
- Public marketing or pricing pages → use **page-cro**.
- First-run activation before any value exists → use **onboarding-cro**.

## Prerequisites

Before recommending anything, establish three things. If any are unknown, ask before designing — see *Questions to Ask* at the end.

### 1. Upgrade Context — *what kind of trade are we asking for?*

Each context has a different "value already banked" and therefore a different acceptable level of friction.

| Context | Value State | Sell |
|---|---|---|
| Freemium → Paid | Habitual | Expansion of something they already use |
| Trial → Paid | Fresh but borrowed | Continuity and loss avoidance |
| Tier upgrade (Basic → Pro) | Already paying | The next ceiling they're hitting |
| Feature-specific upsell | Highest intent | The locked thing they reached for |
| Usage-limit upsell | Self-inflicted wall | Headroom |

### 2. Product Model — *where is the line, and is it defensible?*

If the free tier is too thin, no paywall copy will save conversion; if it's too generous, you have no leverage. Know:

- What's free forever?
- What's behind the paywall, and is it genuinely worth paying for?
- What triggers upgrade prompts today?
- What's the current free → paid conversion rate? (Your baseline; without it you can't tell improvement from noise.)

### 3. User Journey — *has value actually landed yet?*

The same paywall converts at 8% or 0.5% depending only on when it fires.

- At what point in the lifecycle does this appear?
- What has the user already experienced and accomplished?
- What were they trying to do at the instant they were blocked? (The interrupted intent is your strongest copy.)

## Procedure

### Step 1 — Apply the Four Core Principles

Conversion is a byproduct of trust plus timing, not pressure.

#### 1. Value Before Ask
The user should have experienced real value before you ask for money, and the upgrade should read as the natural next step rather than an interruption.

**Why:** an ask that lands before the "aha moment" is indistinguishable from a cost with no benefit attached — the brain has nothing to weigh the price against, so it defaults to "no." After value lands, the same price is weighed against a felt benefit and converts far better.

**How to apply:** anchor the trigger to an activation event (first real outcome, first invited collaborator, first hit limit) rather than a day count or a session count.

#### 2. Show, Don't Just Tell
Demonstrate the paid capability — preview it, render it greyed-out-but-visible, or show a before/after — instead of describing it in a bullet list.

**Why:** an abstract feature name ("Advanced export") is a promise the user has to imagine; a preview is evidence they can evaluate. Evidence converts because it removes the risk of disappointment.

**How to apply:** when you have a screenshot, GIF, or live preview, use it; reserve text-only treatments for cases where rendering the feature isn't feasible.

#### 3. Friction-Free Path
When the user decides to pay, the path from decision to confirmation should be as short and predictable as possible.

**Why:** intent is perishable. Every extra screen, redirect, or required field between "yes" and "done" is a place for second thoughts to creep in, and conversion decays with each one.

**How to apply:** keep checkout in-context, pre-fill what you already know, default to the recommended plan, and never make the user hunt for pricing.

#### 4. Respect the No
Make declining easy and non-punitive, and keep the free experience whole afterward.

**Why:** a large share of eventual conversions are people who said "not now" the first time. Guilt-trip copy ("No, I'll stay limited") and hidden close buttons win the click but poison the relationship, lowering the *next* conversion and raising churn and refund rates. Today's respectful no is the precondition for tomorrow's yes.

**How to apply:** every paywall ships with a clearly visible, neutrally-worded exit ("Maybe later"), and dismissal restores the user to exactly what they were doing.

### Step 2 — Choose the Trigger Point

A trigger is a bet about intent. Each pattern works because it fires at a moment when intent is naturally elevated — and each has a failure mode that appears the instant you fire it at the wrong moment.

#### Feature Gates
Fires when the user clicks a paid-only feature.

- **Why it works:** the click *is* the intent signal — they reached for the thing, so the ask is relevant by definition.
- **Failure mode:** gating something the user assumed was free feels like a bait-and-switch. Make the gate explain *why* it's paid, show what the feature does, give a one-step unlock, and always allow continuing without it.

#### Usage Limits
Fires when the user hits a free-tier ceiling.

- **Why it works:** the wall is reached through the user's own success, so "you've outgrown free" is a flattering, truthful frame.
- **Failure mode:** an abrupt hard stop mid-task reads as punishment for engagement. Name the exact limit, show what upgrading grants, offer a way to stay free (free up room or buy a small top-up), and never block without warning.

#### Trial Expiration
Fires as a trial winds down.

- **Why it works:** the value is fresh and the user has accumulated work they don't want to lose — loss aversion is doing the persuading for you.
- **Failure mode:** a single silent expiration feels like a trap sprung. Warn early and repeatedly (7 days, 3 days, 1 day), state plainly what changes at expiration, summarize the value they received, and make re-activation trivial if they lapse.

#### Time-Based Prompts
Fires after a threshold of free use (e.g., 7 days or 10 sessions).

- **Why it works (weakly):** tenure is a rough proxy for habit, so a gentle nudge can catch users who are getting value but haven't been asked.
- **Failure mode:** time is a *weak* intent signal, so anything more than a dismissible banner or subtle modal feels random and annoying. Keep it low-pressure, highlight a paid feature they haven't tried, and make it trivially dismissible.

#### Context-Triggered
Fires when behavior signals upgrade fit — a power user nearing limits, a solo user using team-shaped features, or someone inviting teammates.

- **Why it works:** behavior is the strongest intent signal of all because it's revealed, not declared.
- **Failure mode:** firing on a noisy or wrong signal makes the product feel like it's watching and pestering. Tie these to high-confidence patterns (heavy usage approaching a limit, an invite action) rather than thin correlations.

### Step 3 — Assemble the Paywall Screen Components

A paywall is a tiny landing page. Each component earns its place by answering a question the hesitating user is silently asking. Drop anything that isn't pulling its weight.

| # | Component | Question It Answers | Notes |
|---|---|---|---|
| 1 | **Headline** | "What do I get?" | Name the capability, not the fee. Lead with the unlocked outcome, then the payoff. |
| 2 | **Value Demonstration** | "Is it actually worth it?" | Show the feature in action: preview, before/after, or usage-specific example. Specificity converts. |
| 3 | **Feature Comparison** | "Which plan is right for me?" | Only show tiers when the choice is genuinely meaningful. Compare *outcomes*, not feature checklists. |
| 4 | **Pricing** | "What will this cost me, exactly?" | Show amount, cadence, annual-vs-monthly trade-off, per-seat math. No hidden or fuzzy pricing. |
| 5 | **Social Proof** | "Do people like me trust this?" | Optional. Real, specific data points or customer quotes. Never invented or vague. |
| 6 | **CTA** | "What happens if I click?" | Be specific and value-oriented: "Start Getting Scheduled Exports" beats "Upgrade." |
| 7 | **Escape Hatch** | "What if I'm not ready?" | Mandatory. Clearly visible, neutrally-worded exit. Never guilt copy. Never hidden. |

#### Headline Patterns

- **Strong:** "Unlock unlimited projects — never archive a client to make room again."
- **Strong:** "Get scheduled exports and stop rebuilding the same report every Monday."
- **Weak:** "Upgrade to Pro for $12/month." (leads with price, names no benefit)

The pattern is: lead with the unlocked capability, then the payoff it produces.

### Step 4 — Implement the Paywall Component

The typed React components below are production-grade artifacts: every prop is explicitly typed (no `any`), inputs are validated at the boundary so a misconfigured paywall fails in QA rather than in front of a paying customer, and the upgrade call is wrapped in defensive error handling so a network failure never leaves the user on a dead button.

#### Shared Core (`paywall-core.ts`)

Every paywall imports the same domain types and helpers. Centralizing them keeps prices, plan identifiers, and the upgrade lifecycle consistent across surfaces.

```typescript
// paywall-core.ts
import { useCallback, useState } from "react";

/**
 * A currency amount stored in the smallest unit (cents) to avoid floating-point
 * rounding errors — `0.1 + 0.2 !== 0.3` is exactly the kind of bug you do not
 * want anywhere near a price.
 */
export interface Price {
  /** Amount in cents, e.g. 1200 === $12.00. Must be a non-negative integer. */
  readonly amountCents: number;
  /** ISO 4217 currency code, e.g. "USD". */
  readonly currency: string;
  /** Billing cadence this amount applies to. */
  readonly interval: "month" | "year";
}

export type PlanId = "free" | "pro" | "team" | "enterprise";

export interface Plan {
  readonly id: PlanId;
  readonly name: string;
  /** `null` means free or contact-sales — there is no charge to display. */
  readonly price: Price | null;
  readonly highlights: readonly string[];
}

/**
 * The outcome of an upgrade attempt, modelled as a discriminated union so callers
 * are forced by the type system to handle every case explicitly instead of
 * guessing from a boolean.
 */
export type UpgradeResult =
  | { readonly status: "succeeded"; readonly subscriptionId: string }
  | { readonly status: "requires_action"; readonly checkoutUrl: string }
  | { readonly status: "failed"; readonly message: string };

/**
 * Owns the side effects of a successful upgrade (unlock the feature, close the
 * modal, fire analytics) and resolves with a typed result. It should not throw
 * for expected payment failures — return `{ status: "failed" }` instead — but
 * `useUpgrade` still guards against unexpected throws.
 */
export type UpgradeHandler = (planId: PlanId) => Promise<UpgradeResult>;

/**
 * Formats a Price for display. Throws on malformed input so a bad price can never
 * be silently rendered as "$NaN/mo" on a live paywall.
 */
export function formatPrice(price: Price): string {
  if (!Number.isInteger(price.amountCents) || price.amountCents < 0) {
    throw new RangeError(
      `formatPrice: amountCents must be a non-negative integer, received ${price.amountCents}.`,
    );
  }
  if (!/^[A-Z]{3}$/.test(price.currency)) {
    throw new TypeError(
      `formatPrice: currency must be an ISO-4217 code (e.g. "USD"), received "${price.currency}".`,
    );
  }
  const amount = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: price.currency,
  }).format(price.amountCents / 100);
  return `${amount}/${price.interval === "month" ? "mo" : "yr"}`;
}

export interface UseUpgradeState {
  readonly isUpgrading: boolean;
  readonly error: string | null;
  /** Kicks off the upgrade for the given plan; never rejects. */
  readonly start: (planId: PlanId) => Promise<void>;
}

/**
 * Wraps an UpgradeHandler with loading and error state so every paywall handles
 * network and payment failures identically — the user always gets either a clear
 * error or a redirect, never a spinner that hangs forever.
 */
export function useUpgrade(handler: UpgradeHandler): UseUpgradeState {
  const [isUpgrading, setIsUpgrading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(
    async (planId: PlanId): Promise<void> => {
      setIsUpgrading(true);
      setError(null);
      try {
        const result = await handler(planId);
        switch (result.status) {
          case "succeeded":
            // The handler owns the success side effects (unlock, close, celebrate).
            return;
          case "requires_action":
            window.location.assign(result.checkoutUrl);
            return;
          case "failed":
            setError(result.message);
            return;
          default: {
            // Exhaustiveness guard: if a new UpgradeResult variant is added and not
            // handled above, TypeScript reports an error on this assignment.
            const unreachable: never = result;
            throw new Error(`Unhandled upgrade result: ${JSON.stringify(unreachable)}`);
          }
        }
      } catch (cause: unknown) {
        const message =
          cause instanceof Error ? cause.message : "Something went wrong. Please try again.";
        setError(message);
      } finally {
        setIsUpgrading(false);
      }
    },
    [handler],
  );

  return { isUpgrading, error, start };
}
```

#### Feature Lock Paywall (`FeatureLockPaywall.tsx`)

Fired when the user clicks a paid feature. Intent is highest here, so the job is to confirm the value fast and get out of the way. The component refuses to render with no value bullets or no price, because either would ship a misleading wall.

```tsx
// FeatureLockPaywall.tsx
import type { JSX } from "react";
import { type Plan, type UpgradeHandler, formatPrice, useUpgrade } from "./paywall-core";

interface FeatureLockPaywallProps {
  /** Human-readable feature name, e.g. "Scheduled exports". Must be non-empty. */
  readonly featureName: string;
  /** Concrete capabilities the feature unlocks. 1–4 keeps the modal scannable. */
  readonly capabilities: readonly string[];
  /** The plan being sold; must have a price. */
  readonly plan: Plan;
  /** Optional preview image. Absent → render the text-only fallback. */
  readonly previewImageUrl?: string;
  readonly onUpgrade: UpgradeHandler;
  readonly onDismiss: () => void;
}

export function FeatureLockPaywall(props: FeatureLockPaywallProps): JSX.Element {
  const { featureName, capabilities, plan, previewImageUrl, onUpgrade, onDismiss } = props;

  // Validate at the boundary: these are bugs we want caught in QA, never shipped.
  if (featureName.trim().length === 0) {
    throw new Error("FeatureLockPaywall: featureName is required.");
  }
  if (capabilities.length === 0 || capabilities.length > 4) {
    throw new RangeError(
      `FeatureLockPaywall: expected 1–4 capabilities, received ${capabilities.length}.`,
    );
  }
  if (plan.price === null) {
    throw new Error("FeatureLockPaywall: a sellable plan must have a price.");
  }

  const { isUpgrading, error, start } = useUpgrade(onUpgrade);

  return (
    <section role="dialog" aria-modal="true" aria-labelledby="feature-lock-title">
      <span aria-hidden="true">🔒</span>
      <h2 id="feature-lock-title">
        {featureName} is part of {plan.name}
      </h2>

      {previewImageUrl !== undefined ? (
        <img src={previewImageUrl} alt={`Preview of ${featureName}`} loading="lazy" />
      ) : (
        <p>{featureName} lets your whole team move faster:</p>
      )}

      <ul>
        {capabilities.map((capability) => (
          <li key={capability}>{capability}</li>
        ))}
      </ul>

      {error !== null && <p role="alert">{error}</p>}

      <button type="button" disabled={isUpgrading} onClick={() => void start(plan.id)}>
        {isUpgrading ? "Starting…" : `Upgrade to ${plan.name} — ${formatPrice(plan.price)}`}
      </button>

      {/* Escape hatch: always visible, never disabled. Trapping the user destroys trust. */}
      <button type="button" onClick={onDismiss}>
        Maybe later
      </button>
    </section>
  );
}
```

Wiring it for Tasklane's scheduled-exports gate:

```tsx
import { type Plan } from "./paywall-core";
import { FeatureLockPaywall } from "./FeatureLockPaywall";

const proPlan: Plan = {
  id: "pro",
  name: "Pro",
  price: { amountCents: 1200, currency: "USD", interval: "month" },
  highlights: ["Unlimited projects", "Scheduled exports", "Priority support"],
};

<FeatureLockPaywall
  featureName="Scheduled exports"
  capabilities={[
    "Export any board to CSV, Excel, or PDF",
    "Send recurring exports to your inbox every Monday",
    "Push exports straight to Google Drive",
  ]}
  plan={proPlan}
  previewImageUrl="/img/paywalls/scheduled-exports.png"
  onUpgrade={startProCheckout}
  onDismiss={closeModal}
/>;
```

#### Usage Limit Paywall (`UsageLimitPaywall.tsx`)

Fired when the user hits a free-tier ceiling. The wall is reached through the user's own success, so "you've outgrown free" is a flattering, truthful frame. The component validates that the limit name, current usage, and ceiling are all present and consistent — a paywall that says "you've hit a limit" without naming the limit is worse than no paywall at all.

```tsx
// UsageLimitPaywall.tsx
import type { JSX } from "react";
import { type Plan, type UpgradeHandler, formatPrice, useUpgrade } from "./paywall-core";

interface UsageLimitPaywallProps {
  /** Human-readable name of the limited resource, e.g. "projects". Must be non-empty. */
  readonly limitName: string;
  /** The user's current usage count. Must be a non-negative integer. */
  readonly currentUsage: number;
  /** The free-tier ceiling. Must be a positive integer greater than or equal to currentUsage. */
  readonly freeLimit: number;
  /** The plan being sold; must have a price. */
  readonly plan: Plan;
  /** What upgrading grants, stated as outcomes. 1–4 items. */
  readonly upgradeBenefits: readonly string[];
  readonly onUpgrade: UpgradeHandler;
  readonly onDismiss: () => void;
}

export function UsageLimitPaywall(props: UsageLimitPaywallProps): JSX.Element {
  const { limitName, currentUsage, freeLimit, plan, upgradeBenefits, onUpgrade, onDismiss } = props;

  if (limitName.trim().length === 0) {
    throw new Error("UsageLimitPaywall: limitName is required.");
  }
  if (!Number.isInteger(currentUsage) || currentUsage < 0) {
    throw new RangeError(
      `UsageLimitPaywall: currentUsage must be a non-negative integer, received ${currentUsage}.`,
    );
  }
  if (!Number.isInteger(freeLimit) || freeLimit <= 0) {
    throw new RangeError(
      `UsageLimitPaywall: freeLimit must be a positive integer, received ${freeLimit}.`,
    );
  }
  if (currentUsage > freeLimit) {
    throw new RangeError(
      `UsageLimitPaywall: currentUsage (${currentUsage}) cannot exceed freeLimit (${freeLimit}).`,
    );
  }
  if (upgradeBenefits.length === 0 || upgradeBenefits.length > 4) {
    throw new RangeError(
      `UsageLimitPaywall: expected 1–4 upgradeBenefits, received ${upgradeBenefits.length}.`,
    );
  }
  if (plan.price === null) {
    throw new Error("UsageLimitPaywall: a sellable plan must have a price.");
  }

  const { isUpgrading, error, start } = useUpgrade(onUpgrade);

  return (
    <section role="dialog" aria-modal="true" aria-labelledby="usage-limit-title">
      <h2 id="usage-limit-title">
        You've used all {freeLimit} {limitName} on your free plan
      </h2>
      <p>
        You're at {currentUsage} of {freeLimit} {limitName}. Upgrade to {plan.name} for:
      </p>
      <ul>
        {upgradeBenefits.map((benefit) => (
          <li key={benefit}>{benefit}</li>
        ))}
      </ul>
      {error !== null && <p role="alert">{error}</p>}
      <button type="button" disabled={isUpgrading} onClick={() => void start(plan.id)}>
        {isUpgrading ? "Starting…" : `Upgrade to ${plan.name} — ${formatPrice(plan.price)}`}
      </button>
      <button type="button" onClick={onDismiss}>
        Maybe later
      </button>
    </section>
  );
}
```

Wiring it for Tasklane's 3-project limit:

```tsx
import { type Plan } from "./paywall-core";
import { UsageLimitPaywall } from "./UsageLimitPaywall";

const proPlan: Plan = {
  id: "pro",
  name: "Pro",
  price: { amountCents: 1200, currency: "USD", interval: "month" },
  highlights: ["Unlimited projects", "Scheduled exports", "Priority support"],
};

<UsageLimitPaywall
  limitName="projects"
  currentUsage={3}
  freeLimit={3}
  plan={proPlan}
  upgradeBenefits={[
    "Create unlimited projects — no more archiving to make room",
    "Keep all your active client work visible at once",
    "Scheduled exports so your reports are ready before you are",
  ]}
  onUpgrade={startProCheckout}
  onDismiss={closeModal}
/>;
```

#### Trial Expiration Paywall (`TrialExpirationPaywall.tsx`)

Fired as a trial winds down. The value is fresh and the user has accumulated work they don't want to lose — loss aversion is doing the persuading. Warn early and repeatedly (7 days, 3 days, 1 day), state plainly what changes at expiration, summarize the value they received, and make re-activation trivial if they lapse.

```tsx
// TrialExpirationPaywall.tsx
import type { JSX } from "react";
import { type Plan, type UpgradeHandler, formatPrice, useUpgrade } from "./paywall-core";

interface TrialExpirationPaywallProps {
  /** Days remaining in the trial. Must be a non-negative integer. 0 = final day. */
  readonly daysRemaining: number;
  /** The plan the trial covers and the user would convert to. Must have a price. */
  readonly plan: Plan;
  /** What the user accomplished or used during the trial. 1–4 items. */
  readonly trialValueSummary: readonly string[];
  /** What changes at expiration — stated as losses, not threats. 1–3 items. */
  readonly expirationChanges: readonly string[];
  readonly onUpgrade: UpgradeHandler;
  readonly onDismiss: () => void;
}

export function TrialExpirationPaywall(props: TrialExpirationPaywallProps): JSX.Element {
  const { daysRemaining, plan, trialValueSummary, expirationChanges, onUpgrade, onDismiss } = props;

  if (!Number.isInteger(daysRemaining) || daysRemaining < 0) {
    throw new RangeError(
      `TrialExpirationPaywall: daysRemaining must be a non-negative integer, received ${daysRemaining}.`,
    );
  }
  if (trialValueSummary.length === 0 || trialValueSummary.length > 4) {
    throw new RangeError(
      `TrialExpirationPaywall: expected 1–4 trialValueSummary items, received ${trialValueSummary.length}.`,
    );
  }
  if (expirationChanges.length === 0 || expirationChanges.length > 3) {
    throw new RangeError(
      `TrialExpirationPaywall: expected 1–3 expirationChanges items, received ${expirationChanges.length}.`,
    );
  }
  if (plan.price === null) {
    throw new Error("TrialExpirationPaywall: a sellable plan must have a price.");
  }

  const { isUpgrading, error, start } = useUpgrade(onUpgrade);

  const urgencyLabel =
    daysRemaining === 0
      ? "Your trial ends today"
      : daysRemaining === 1
        ? "Your trial ends tomorrow"
        : `${daysRemaining} days left in your trial`;

  return (
    <section role="dialog" aria-modal="true" aria-labelledby="trial-exp-title">
      <h2 id="trial-exp-title">{urgencyLabel}</h2>
      <p>Here's what you've gotten done with {plan.name}:</p>
      <ul>
        {trialValueSummary.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <p>When your trial ends:</p>
      <ul>
        {expirationChanges.map((change) => (
          <li key={change}>{change}</li>
        ))}
      </ul>
      <p>Keep everything running with {plan.name} — {formatPrice(plan.price)}</p>
      {error !== null && <p role="alert">{error}</p>}
      <button type="button" disabled={isUpgrading} onClick={() => void start(plan.id)}>
        {isUpgrading ? "Starting…" : `Keep My ${plan.name} Features`}
      </button>
      <button type="button" onClick={onDismiss}>
        Maybe later
      </button>
    </section>
  );
}
```

Wiring it for Tasklane's 14-day Pro trial, 3 days remaining:

```tsx
import { type Plan } from "./paywall-core";
import { TrialExpirationPaywall } from "./TrialExpirationPaywall";

const proPlan: Plan = {
  id: "pro",
  name: "Pro",
  price: { amountCents: 1200, currency: "USD", interval: "month" },
  highlights: ["Unlimited projects", "Scheduled exports", "Priority support"],
};

<TrialExpirationPaywall
  daysRemaining={3}
  plan={proPlan}
  trialValueSummary={[
    "Created 12 projects across 4 clients",
    "Set up 3 scheduled exports saving you ~2 hours/week",
    "Invited 2 collaborators to shared boards",
  ]}
  expirationChanges={[
    "Scheduled exports will stop running",
    "You'll be limited to 3 active projects",
    "Collaborators will lose access to shared boards",
  ]}
  onUpgrade={startProCheckout}
  onDismiss={closeModal}
/>;
```

### Step 5 — Define Metrics and Guardrails

Before shipping any paywall change, define:

**Primary metric (pick one):**
- Free → paid conversion rate
- Trial → paid conversion rate
- ARPU (average revenue per user)
- Expansion revenue (tier upgrades)

**Guardrail metrics (monitor all):**
- Churn rate (should not increase)
- Refund rate (should not increase)
- NPS / satisfaction (should not decrease)
- Free-tier engagement (should not decrease — if it does, the paywall is poisoning the free experience)

**Dark patterns to audit and remove:**
- Hidden close buttons
- Misleading urgency (fake countdowns, false scarcity)
- Guilt copy ("No, I'll stay limited")
- Pre-checked boxes or auto-enrolled add-ons
- Bait-and-switch gates (features that were free, now paywalled without notice)

### Step 6 — Run Experiments

Paywall outcomes are dominated by interactions you can't reliably predict. Each idea below is a hypothesis, not a recommendation — validate against the guardrail metrics.

#### Trigger & Timing Experiments

| Dimension | Variants |
|---|---|
| When to show | After aha moment vs. at feature attempt |
| Trial reminder timing | 7 days vs. 1 day before expiration |
| Action threshold | 3 completed actions vs. 10 vs. 3 calendar days vs. 7 |
| Trigger type | Hard gate vs. soft gate (preview + prompt) |
| Surface | In-context modal vs. dedicated upgrade page vs. banner |

#### Paywall Design Experiments

| Dimension | Variants |
|---|---|
| Layout | Full-screen vs. modal overlay |
| Density | Minimal CTA-focused vs. feature-rich |
| Plans | Single recommended vs. plan comparison |
| Visuals | Image/preview vs. text-only vs. demo video/GIF |
| Value frame | Gain ("unlock unlimited") vs. loss aversion ("don't lose your work") |
| Personalization | Generic vs. usage-based ("You've created 50 projects") |

#### Pricing Presentation Experiments

| Dimension | Variants |
|---|---|
| Price display | Monthly vs. annual vs. both with toggle |
| Savings framing | Dollar amount vs. percentage vs. price-per-day |
| Plan count | 2 vs. 3 visible plans |
| Badge | "Most Popular" on target plan vs. none |
| Offers | First-month discount vs. limited-time offer vs. loyalty discount |

#### Copy & Messaging Experiments

| Dimension | Variants |
|---|---|
| Headline | Benefit-focused vs. feature-focused vs. question vs. social-proof |
| CTA | "Start Free Trial" vs. "Upgrade Now" vs. "Start My Trial" vs. value-specific |
| Objection handling | Money-back guarantee vs. "Cancel anytime" vs. FAQ vs. support chat |
| Decline copy | "Maybe later" vs. "No thanks" vs. "Remind me tomorrow" |

#### Trial & Conversion Experiments

| Dimension | Variants |
|---|---|
| Trial length | 7-day vs. 14-day vs. 30-day |
| Card required | Yes vs. no |
| Access level | Full vs. limited-feature |
| Expiration UX | Countdown timer vs. email reminders vs. grace period |
| Upgrade path | One-click in-context vs. separate checkout |

#### Frequency & UX Experiments

| Dimension | Variants |
|---|---|
| Prompts per session | 1 vs. 2 vs. 3 |
| Cool-down after dismiss | Hours vs. days |
| Escalation | Consistent messaging vs. escalating urgency |
| Re-show rules | After major engagement event vs. fixed interval |

## Pitfalls

### Critical (ship-blocking)

1. **Asking before value lands.** A paywall that fires before the aha moment is indistinguishable from a cost with no benefit. Always anchor the trigger to an activation event, not a day count.

2. **No escape hatch.** Trapping the user to win one click costs you the next conversion and a refund risk. Every paywall ships with a clearly visible, neutrally-worded exit ("Maybe later"). Never use guilt copy like "No, I'll stay limited." Never hide the close button.

3. **Hidden or fuzzy pricing.** Uncertainty is itself a cost. Show the amount, cadence, annual-vs-monthly trade-off, and per-seat math. If the user has to hunt for the price, they'll assume it's unfair.

4. **Bait-and-switch gates.** Gating something the user assumed was free destroys trust. The gate must explain *why* it's paid, show what the feature does, and allow continuing without it.

5. **Abrupt hard stops on usage limits.** An unannounced mid-task block reads as punishment for engagement. Name the exact limit, show what upgrading grants, offer a way to stay free, and never block without warning.

6. **Silent trial expiration.** A single silent expiration feels like a trap sprung. Warn early and repeatedly (7 days, 3 days, 1 day), state plainly what changes, summarize the value received, and make re-activation trivial.

### Common (conversion-suppressing)

7. **Price-oriented headlines.** "Upgrade to Pro for $12/month" leads with cost and names no benefit. Lead with the unlocked capability, then the payoff.

8. **Feature checklists instead of outcome comparisons.** Users have to do the translation work themselves. Compare outcomes ("invite your whole team", "never hit a project cap") not feature dumps.

9. **Too many steps from decision to confirmation.** Intent is perishable. Every extra screen, redirect, or required field is a place for second thoughts. Keep checkout in-context, pre-fill what you know, default to the recommended plan.

10. **Vague or invented social proof.** "Loved by thousands" erodes the trust it's meant to build. Use real, specific data points ("4,200 teams rely on scheduled exports") or honest customer quotes — or omit the component entirely.

11. **Firing on noisy context signals.** Firing on a wrong signal makes the product feel like it's watching and pestering. Tie context-triggered paywalls to high-confidence patterns (heavy usage approaching a limit, an invite action) rather than thin correlations.

12. **Ignoring mobile constraints.** Tap targets, system conventions (StoreKit / Google Play billing), and restore-purchases flows must be addressed. A web paywall pattern that ignores platform conventions will underperform.

### Technical (implementation-level)

13. **Floating-point price math.** `0.1 + 0.2 !== 0.3` is not a bug you want near a price. Store amounts in cents (integers) and format at the display boundary.

14. **Unhandled upgrade result variants.** The `UpgradeResult` discriminated union exists so the type system forces exhaustive handling. If you add a new variant and don't handle it, the exhaustiveness guard in `useUpgrade` will throw — which is correct: fail in QA, not in front of a paying customer.

15. **Missing boundary validation.** A paywall that renders with no capabilities or no price is worse than no paywall. The components throw on misconfiguration so bugs are caught in QA.

16. **Network failure leaves a dead button.** The `useUpgrade` hook wraps the handler in try/catch so a network failure always produces a clear error message, never a spinner that hangs forever.

## Verification

Before shipping a paywall change, verify every item:

- [ ] Does the proposed paywall trigger occur *after* the user has experienced the "aha moment"?
- [ ] Is the headline benefit-oriented rather than price-oriented?
- [ ] Is there a clear, non-punitive "escape hatch" (exit path) for the user?
- [ ] Does the flow minimize the number of steps from the trigger to the payment confirmation?
- [ ] Are mobile-specific constraints (tap targets, system conventions, restore purchases) addressed?
- [ ] Is there a defined A/B test metric (e.g., conversion rate, ARPU) plus a down-funnel guardrail (churn, refunds) to validate the change?
- [ ] Have all dark patterns (hidden close buttons, misleading urgency, guilt copy) been removed?
- [ ] Are prices stored in cents (integers) and formatted at the display boundary?
- [ ] Does the upgrade handler return a typed `UpgradeResult` for every case (succeeded, requires_action, failed)?
- [ ] Does the paywall component validate props at the boundary and throw on misconfiguration?
- [ ] Is the escape hatch never disabled, even during an in-flight upgrade request?

## Questions to Ask

If you need more context before designing, these six questions unblock the most decisions:

1. What's your current free → paid conversion rate? (your baseline for judging any change)
2. What triggers upgrade prompts today? (what you're changing from)
3. What features are behind the paywall? (where your leverage is)
4. What's the "aha moment" for users? (where value lands — and therefore where to place the ask)
5. What pricing model? (per seat, usage-based, or flat — this dictates the trigger mix)
6. Mobile app, web app, or both? (determines which platform constraints apply)

## Related Skills

- **page-cro**: for public pricing-page optimization (marketing site, not in-product)
- **onboarding-cro**: for driving users to the aha moment *before* the upgrade ask
- **ab-test-setup**: for structuring and running the paywall experiments above
- **analytics-tracking**: for instrumenting and measuring the upgrade funnel

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

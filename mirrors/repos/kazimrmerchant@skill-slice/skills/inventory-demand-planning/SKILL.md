---
name: inventory-demand-planning
description: "Chooses retailer forecast families (moving average, Holt-Winters, causal, LightGBM), safety stock under lead-time risk, reorder/EOQ/min-max, and promo lift with cannibalization and post-promo dip. Trigger on demand forecast, safety stock, replenishment, or promo lift across stores and SKUs. Not for factory MRP, 3PL slotting, or warehouse WMS build-out."
version: 1.0.1
risk: safe
source: https://github.com/ai-evos/agent-skills
date_added: '2026-02-27'
---

## When to Use
Use this skill when you need to forecast demand and shape inventory policy across SKUs, stores, and vendors:
- Selecting and tuning forecasting methods, safety stock policies, and reorder logic for different demand patterns.
- Planning promotions, seasonal transitions, markdowns, and end-of-life strategies while balancing service, cash, and margin.
- Investigating chronic stockouts, excess inventory, or forecast bias and redesigning the planning process with clearer decision frameworks.

## Prerequisites
- **Context:** Senior demand planner at a multi-location retailer (40–200 stores, 300–800 active SKUs).
- **Systems:** Demand planning suite (Blue Yonder, Oracle Demantra, Kinaxis), ERP (SAP, Oracle), WMS, POS data feeds, and vendor portals.

## Procedure

### 1. Forecasting Method Selection
1. **Moving Averages:** Use for stable-demand, low-variability items. A 4-week simple moving average works for commodity staples. Weighted moving averages work better for slight drift. Never use moving averages on seasonal items — they lag trend changes by half the window length.
2. **Exponential Smoothing:** Single (SES, alpha 0.1–0.3) for stationary demand. Double (Holt's) for consistent growth/decline. Triple (Holt-Winters) for seasonal cycles. Optimize parameters on holdout data, never on fitting data.
3. **Seasonal Decomposition:** Use STL, classical, or X-13ARIMA-SEATS to isolate trend, seasonal, and residual components. Use when seasonal patterns shift year over year or before building promotional lift estimates.
4. **Causal/Regression Models:** Use when external factors drive demand. Encode promo flags with depth, display type, and media support. Regularize aggressively (Lasso/Ridge) and validate on out-of-time data.
5. **Machine Learning:** Justified for 1,000+ SKUs with 2+ years of weekly history. LightGBM/XGBoost outperforms simpler methods by 10–20% WAPE on promotional/intermittent items. Requires quarterly retraining minimum.
*Load `references/decision-frameworks.md` when you need detailed method selection trees, optimization models, or mapping demand patterns to primary/fallback methods.*

### 2. Safety Stock Calculation
1. **Standard Formula:** `SS = Z × σ_d × √(LT + RP)` (Z = service level z-score, σ_d = demand std dev, LT = lead time, RP = review period). Works only for normally distributed, stationary demand.
2. **Lead Time Variability:** `SS = Z × √(LT_avg × σ_d² + d_avg² × σ_LT²)`. Use when vendor lead times are uncertain (CV > 0.3).
3. **Lumpy/Intermittent Demand:** Use Croston's method for forecasting. Compute safety stock using a bootstrapped demand distribution.
4. **New Products:** Use analogous item profiling (3–5 most similar items). Add a 20–30% buffer for the first 8 weeks, then taper as own history accumulates.

### 3. Reorder Logic
1. **Inventory Position:** `IP = On-Hand + On-Order − Backorders − Committed`. Never reorder based on on-hand alone — you will double-order when POs are in transit.
2. **Min/Max:** Min = average demand during lead time + safety stock. Max = Min + EOQ. Order up to Max when IP drops to Min.
3. **Reorder Point / EOQ:** ROP = average demand during lead time + safety stock. EOQ = √(2DS/H). Round EOQ to vendor case packs, layer quantities, or pallet tiers.
4. **Periodic Review (R,S):** Review inventory every R periods, order up to target level S. Set R by vendor delivery schedule.
5. **Vendor Tier Frequencies:** A-vendors (top 10 by spend) get weekly review cycles. B-vendors (next 20) get bi-weekly. C-vendors get monthly.

### 4. Promotional Planning
1. **Baseline Separation:** Strip promotional volume from history before fitting baseline models. Keep a separate "promotional lift" layer that applies multiplicatively on top of the baseline.
2. **Lift Estimation:** Use YoY comparison, cross-elasticity models, or analogous item lift. Typical lifts: 15–40% for TPR only, 80–200% for TPR + display + circular, 300–500%+ for doorbusters.
3. **Cannibalization:** Estimate cannibalization at 10–30% of lifted volume for close substitutes.
4. **Post-Promo Dip:** Expect 1–3 weeks of below-baseline demand. Dip magnitude is typically 30–50% of incremental lift, concentrated 60/30/10 across the three post-promo weeks.

### 5. ABC/XYZ Classification
1. **ABC (Value):** A = top 20% of SKUs driving 80% of margin. B = next 30% driving 15%. C = bottom 50% driving 5%. Classify on margin contribution, not revenue.
2. **XYZ (Predictability):** X = CV < 0.5. Y = CV 0.5–1.0. Z = CV > 1.0. Compute on de-seasonalized, de-promoted demand.
3. **Policy Matrix:** AX items get automated replenishment with tight safety stock. AZ items need human review every cycle. CX items get automated replenishment with generous review periods. CZ items are candidates for discontinuation.

### 6. Seasonal Transition Management
1. **Buy Timing:** Commit 12–20 weeks before selling season. Allocate 60–70% of expected demand in initial buy, reserving 30–40% for reorder based on early-season sell-through.
2. **Markdown Timing:** Begin markdowns when sell-through drops below 60% of plan at season midpoint. Early shallow markdowns (20–30% off) recover more margin than late deep markdowns.
3. **Season-End Liquidation:** Set a hard cutoff date 2–3 weeks before next season's product arrives. Do not hold seasonal product into the next year.

### 7. Communication Patterns
- **Vendor routine reorder:** Transactional, brief, PO-reference-driven.
- **Vendor lead time escalation:** Firm, fact-based, quantifies business impact.
- **Internal stockout alert:** Urgent, actionable, leads with customer impact and estimated revenue at risk.
- **Markdown recommendation:** Data-driven, includes margin impact. Frame as "sell-through pace requires price action", not "we bought too much".
*Load `references/communication-templates.md` when you need full templates with variables and tone guidance for vendor or internal communications.*

## Pitfalls
1. **Overfitting causal models:** Overfitting on sparse promo history is the single biggest pitfall. Validate on out-of-time data.
2. **Low-volume MAPE:** MAPE breaks on low-volume items (division by near-zero). Use WMAPE instead.
3. **Moving Averages on seasonal items:** They lag trend changes by half the window length.
4. **Ignoring post-promo dip:** Failing to forecast the dip leads to excess inventory and markdowns.
5. **Classifying ABC on revenue:** Overinvests in high-revenue low-margin items. Use margin contribution.
6. **Holding seasonal product into next year:** Style items date, and warehousing cost erodes margin recovery.
7. **Slow-mover lingering:** Consumes shelf space, warehouse slots, and working capital. Set a hard exit date 8 weeks from first markdown.
8. **Viral social media spike:** Do not chase. Capture from existing inventory, issue allocation rules. Revise baseline only if sustained 4+ weeks post-spike.
9. **Supplier lead time doubling:** Recalculate SS immediately. Place emergency order for the delta, negotiate partial shipments.
10. **Phantom inventory:** Suspect when service level drops despite "adequate" on-hand. Conduct cycle counts.
11. **Vendor MOQ conflicts:** Consolidate with other items, negotiate lower MOQ, or accept overage if holding cost is lower than alternative supplier.
12. **Holiday calendar shift:** Align forecasts to "weeks relative to holiday" rather than calendar weeks.
13. **Demand pattern regime change:** Old model will fail silently. Monitor tracking signal weekly — when it exceeds ±4 for two consecutive periods, trigger model re-selection.
*Load `references/edge-cases.md` for the comprehensive edge case library with full resolution playbooks.*

## Verification
Track weekly and trend monthly to verify planning health:

| Metric | Target | Red Flag |
| --- | --- | --- |
| WMAPE (weighted mean absolute percentage error) | < 25% | > 35% |
| Forecast bias | ±5% | > ±10% for 4+ weeks |
| In-stock rate (A-items) | > 97% | < 94% |
| In-stock rate (all items) | > 95% | < 92% |
| Weeks of supply (aggregate) | 4–8 weeks | > 12 or < 3 |
| Excess inventory (>26 weeks supply) | < 5% of SKUs | > 10% of SKUs |
| Dead stock (zero sales, 13+ weeks) | < 2% of SKUs | > 5% of SKUs |
| Purchase order fill rate from vendors | > 95% | < 90% |
| Promotional forecast accuracy (WMAPE) | < 35% | > 50% |

**Escalation Triggers:**
- Projected stockout on A-item within 7 days: Alert demand planning manager + category merchant within 4 hours.
- Vendor confirms lead time increase > 25%: Notify supply chain director; recalculate all open POs within 1 business day.
- Promotional forecast miss > 40%: Post-promo debrief with merchandising and vendor within 1 week.
- Excess inventory > 26 weeks of supply on any A/B item: Markdown recommendation to merchandising VP within 1 week.
- Forecast bias exceeds ±10% for 4 consecutive weeks: Model review and re-parameterization within 2 weeks.
- New product sell-through < 40% of plan after 4 weeks: Assortment review with merchandising within 1 week.
- Service level drops below 90% for any category: Root cause analysis and corrective plan within 48 hours.

**Escalation Chain:**
Level 1 (Demand Planner) → Level 2 (Planning Manager, 24 hours) → Level 3 (Director of Supply Chain Planning, 48 hours) → Level 4 (VP Supply Chain, 72+ hours or any A-item stockout at enterprise customer).

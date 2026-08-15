---
name: energy-procurement
description: "Scores commercial and industrial power and gas purchases from interval load and bill anatomy: fixed versus index supply, demand-charge and capacity-tag risk, physical versus virtual PPAs, and RFP scoring. Use when a facility buyer must choose contracts, hedge ratios, or stacked battery and demand-response value. Not for residential tariff shopping, crypto-miner hosting, or HVAC equipment design. Never treat this chair as counsel or a live ISO tariff filing."
version: 1.0.1
risk: safe
source: https://github.com/ai-evos/agent-skills
date_added: '2026-02-27'
---

## When to Use
Use this skill when you need to design, audit, or optimise an energy procurement strategy for commercial or industrial facilities. Trigger keywords: energy procurement, electricity tariff, demand charge, PPA, VPPA, capacity tag, load factor, block-and-index, RFP, RECs, Scope 2 emissions.

## Prerequisites
- Access to facility interval data (15-minute kWh/kW) and utility bills.
- Access to energy market data (ICE, CME, Platts) or forward curves.
- Understanding of the facility's market structure (regulated vs. deregulated).

## Procedure

1. **Analyze Load Profile and Bill Anatomy**
   - Break down the utility bill into independent components: Energy charges (40-55% of bill), Demand charges (20-40%), Capacity charges, T&D, and Riders.
   - Calculate load factor: `Load factor = (Total kWh) / (Peak kW × Hours in period)`.
   - Identify base vs. variable load. High load factor (>0.75) benefits from around-the-clock block purchases. Low load factor (<0.50) benefits from shaped/TOU products.
   - Download 15-minute interval data and identify the top 10 peak intervals per month. Look for common root causes (e.g., simultaneous startup of large loads between 6:00-9:00 AM).

2. **Select Procurement Strategy**
   - Evaluate the company's tolerance for budget variance. If >5% variance triggers a review, lean fixed. If 15-20% is tolerable, consider index or block-and-index.
   - Check market position: If forward curves are in the bottom third of the 5-year range, lock in fixed. If in the top third, keep index exposure. If uncertain, use layered procurement (buying in tranches over 12-24 months).
   - If issuing an RFP, issue to 5-8 qualified retail energy providers (REPs). Include 36 months of interval data, load factor, site addresses, utility account numbers, and sustainability requirements.
   - Evaluate RFP responses on total cost, supplier credit quality (S&P/Moody's), contract flexibility, and value-added services.

3. **Evaluate Renewable Energy Options**
   - Compare Physical PPA, Virtual PPA (VPPA), Unbundled RECs, and On-site generation based on sustainability targets (RE100, SBTi) and economics.
   - For PPAs, evaluate: Project economics vs forward curve, Basis risk (require 5+ years of historical basis data), Curtailment exposure, and Credit requirements (e.g., $5-10M LC for a $50M VPPA).
   - Load `references/decision-frameworks.md` when modeling PPA strike prices, comparing VPPA vs Physical PPA structures, or calculating hedge ratios.

4. **Implement Demand Charge Management**
   - Evaluate load shifting for discretionary loads (batch processes, charging, thermal storage). A 500 kW shift can save $5,000-$12,500/month.
   - Evaluate peak shaving with batteries. Calculate ROI using total stacked value: Demand charges + Capacity tag reduction + TOU energy arbitrage + DR program revenue. If simple payback < 5 years with stacked value, it is typically justified.
   - Check the tariff for demand ratchet clauses (billed demand cannot fall below 60-80% of prior 11-month peak) before any facility modification.
   - Evaluate Demand Response (DR) programs (e.g., PJM Economic DR, ERCOT ERS) for 1 MW curtailment capability ($15K-$80K/year revenue).

5. **Manage Risk and Sustainability**
   - Determine hedge ratio. Most sophisticated C&I buyers land on 60-80% hedged, 20-40% index.
   - Map procurement to Scope 2 emissions: Location-based (grid average) vs Market-based (reflects RECs/PPAs).
   - Load `references/communication-templates.md` when drafting RFPs, PPA negotiations, rate case interventions, or internal stakeholder reports.

## Pitfalls

- **Demand Ratchet Clauses:** A single accidental peak (e.g., 6 MW when normal is 4 MW) can lock in billing demand of 3.6-4.8 MW for 11 months. Always check tariff provisions.
- **Capacity Tag (PLC) Spikes:** In PJM/ISO-NE, your PLC is set by load during prior year's 5 coincident peak hours. Running backup generators during a heat wave can spike capacity charges 20-40% the following delivery year.
- **Negative LMP Pricing:** During high-wind/solar periods, wholesale prices can go negative. Under some PPA structures, you owe the developer the settlement difference on these intervals.
- **Behind-the-meter Solar Cannibalizing DR:** Solar reduces average consumption but may not reduce peak (peaks often on cloudy afternoons). This lowers your DR baseline, reducing DR curtailment capacity and revenue.
- **Utility Rate Case Mid-Contract:** Fixed-price supply contracts cover energy, but T&D and rider charges flow through. A rate case can add $0.012/kWh to delivery charges, causing unexpected cost increases.
- **Index Pricing Tail Risk:** Full exposure to price spikes (e.g., ERCOT Winter Storm Uri hitting $9,000/MWh) can cause single-week bills to exceed $1.5M for a 5 MW load. Requires active risk management.
- **Supplier Credit Risk:** A supplier bankruptcy mid-contract forces you into utility default service at tariff rates. Always check S&P/Moody's ratings.
- **Deregulated Market Re-regulation:** State legislative action after a price spike can void competitively procured contracts, reverting you to utility tariff rates.

## Verification

- Verify that the chosen strategy aligns with the company's budget variance tolerance and sustainability targets (RE100/SBTi).
- Check that all PPA evaluations include basis risk modeling and curtailment exposure caps.
- Ensure demand charge ROI calculations include stacked value (demand charges + capacity + arbitrage + DR), not just direct $/kW savings.
- Confirm that RFP packages include complete 36-month interval data and load profiles to prevent suppliers from padding margins.
- Load `references/edge-cases.md` to verify the proposed strategy against historical edge cases (e.g., Winter Storm Uri, rate case filings, negative LMP events).

## Additional Resources

- `references/decision-frameworks.md`: Detailed frameworks for procurement strategy, PPA evaluation, hedging, and multi-facility optimization. Load when making complex procurement decisions or modeling financial hedges.
- `references/edge-cases.md`: Comprehensive edge case library with full analysis. Load to stress-test a proposed strategy against market anomalies.
- `references/communication-templates.md`: Templates for RFPs, PPA negotiations, rate cases, and internal reporting. Load when drafting external or internal communications.

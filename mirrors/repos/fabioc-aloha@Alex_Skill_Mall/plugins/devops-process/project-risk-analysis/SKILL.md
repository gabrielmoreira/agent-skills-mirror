---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-risk-analysis
description: Systematic methodology for identifying, categorizing, and mitigating software project risks before implementation
tier: standard
applyTo: '**/*project*,**/*risk*,**/*analysis*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Domain Knowledge: Project Risk Analysis Methodology


**Domain**: Software Project Risk Management & Strategic Planning
**Version**: 1.0.0 UNUNNILIUM (un-un-nil-ium)
**Mastery Level**: Foundational
**Created**: January 1, 2026
**Source**: ChessCoach comprehensive risk analysis (16 risks identified)
**Research Foundation**: Software engineering risk management, project failure analysis, startup validation frameworks

---

## 📚 Overview

**Domain Purpose**: Systematic methodology for identifying, categorizing, and mitigating project risks before implementation begins. Prevents common failure modes: over-documentation without validation, premature optimization, technical debt from poor architectural decisions, and resource exhaustion from scope creep.

**Key Insight**: **Documentation without implementation is planning theater** - Risk analysis must identify "analysis paralysis" patterns where extensive documentation substitutes for user validation and proof-of-concept development.

**Core Value Proposition**: Early risk identification reduces total project cost by 50-70% compared to discovering risks during implementation (Boehm's cost escalation research). Pre-implementation risk analysis enables informed go/no-go decisions before significant resource commitment.

---

## 🎯 Risk Assessment Framework (6 Categories)

### 1. Technical Risks

**Definition**: Risks arising from technology choices, architectural decisions, integration complexity, or performance uncertainty.

**Common Patterns**:

- **Zero Implementation Code** - Extensive planning without proof of concept validation
- **Untested Performance Assumptions** - Cost/scalability estimates without benchmarking
- **External Dependency Uncertainty** - Reliance on third-party services/libraries with unclear availability
- **Integration Complexity** - Multiple systems with undocumented interaction patterns

**Identification Questions**:

- Does proof of concept exist for critical path components?
- Are performance claims validated with benchmarks?
- What happens if external dependencies become unavailable?
- Can the architecture handle 10× projected load?

### 2. Security & Compliance Risks

**Definition**: Risks related to data protection, authentication, regulatory compliance, and vulnerability management.

**Common Patterns**:

- **Incomplete Compliance Documentation** - Security requirements acknowledged but not implemented
- **Authentication Gaps** - Secrets in code, weak password policies, missing MFA
- **Data Protection Deficiencies** - Unencrypted sensitive data, inadequate access controls
- **Regulatory Uncertainty** - GDPR, HIPAA, SOC 2 requirements unclear for deployment region

**Identification Questions**:

- Are all security requirements implemented (not just documented)?
- Is managed identity (MSI) used for all inter-service authentication?
- Are encryption at rest and in transit enforced?
- What's the data breach notification timeline?

### 3. Financial Risks

**Definition**: Risks of cost overruns, pricing model failures, or resource exhaustion before revenue generation.

**Common Patterns**:

- **Cost Assumption Gaps** - Usage estimates without real-world validation (e.g., "50 messages/user/month")
- **Hidden Scaling Costs** - Linear cost increase with user growth (database, LLM, compute)
- **Budget Buffer Exhaustion** - No financial runway for unexpected expenses
- **Pricing Model Untested** - Willingness-to-pay assumptions without user surveys

**Identification Questions**:

- What happens if usage is 4× projections?
- Is there 3-6 months financial runway for zero revenue?
- Are all cost drivers documented with worst-case scenarios?
- Has pricing model been validated with 50+ target users?

### 4. Legal Risks

**Definition**: Risks arising from licensing conflicts, intellectual property issues, or terms of service violations.

**Common Patterns**:

- **GPL License Contamination** - Viral copyleft licenses (GPL-3.0) affect proprietary codebase
- **Incompatible License Mixing** - MIT + GPL-3.0 dependencies = license conflict
- **Terms of Service Violations** - Web scraping, API usage beyond rate limits
- **Patent Infringement** - Using patented algorithms without license (e.g., chess engine techniques)

**Identification Questions**:

- Are all dependency licenses compatible with project license?
- Does SaaS deployment trigger GPL distribution requirements?
- Are data collection practices compliant with source terms of service?
- Is patent freedom-to-operate confirmed for core algorithms?

### 5. Operational Risks

**Definition**: Risks related to deployment, monitoring, incident response, and day-to-day system operations.

**Common Patterns**:

- **No CI/CD Pipeline** - Manual deployment leads to human error and downtime
- **Missing Observability** - No logs, metrics, or error tracking for debugging
- **Single Point of Failure** - Critical component without redundancy (database, API)
- **Insufficient Monitoring** - Cannot detect performance degradation or security incidents

**Identification Questions**:

- Can the system be deployed automatically from Git repository?
- Are error rates, latency, and resource usage monitored?
- What's the mean time to detect (MTTD) for critical failures?
- Is there on-call rotation or incident response plan?

### 6. Strategic Risks

**Definition**: Risks to product-market fit, competitive positioning, or business model viability.

**Common Patterns**:

- **No User Validation** - Building features without confirming user demand
- **Premature Scaling** - Architecting for 1000 users before validating 10 users
- **Competitor Blindness** - Ignoring established players (Lichess, Chess.com)
- **Market Timing** - Late to market or too early for technology adoption

**Identification Questions**:

- Have 50+ target users confirmed willingness to pay?
- What makes this defensible against competitors with 100× resources?
- Is there a clear go-to-market strategy?
- What assumptions must be true for product to succeed?

---

## 🔍 Risk Identification Methodology

### Phase 1: Documentation Review (30-60 minutes)

**Objective**: Scan all project documentation for explicit and implicit risks.

**Process**:

1. **File Inventory Audit**: List all files, identify missing artifacts
   - ✅ Expected: README, docs/, src/, tests/, CI/CD config, LICENSE
   - 🚨 Red Flag: Extensive documentation but no src/ directory
2. **Assumption Extraction**: Highlight all numerical estimates, performance claims, cost projections
   - Example: "10 concurrent users", "$18/mo LLM costs", "500 messages/month"
3. **Dependency Mapping**: List all external services, libraries, APIs with availability/licensing notes
   - Example: PostgreSQL (10 connection limit), Azure AI Foundry (rate limits), Stockfish (GPL-3.0)
4. **Gap Analysis**: Compare planned vs implemented features
   - Example: "Chess coaching with Maia" planned, "Zero Maia integration code" implemented

**Deliverable**: List of 20-30 potential risks with supporting evidence from documentation.

### Phase 2: Risk Categorization (20-30 minutes)

**Objective**: Organize identified risks into 6 categories with probability/impact assessment.

**Risk Matrix**:

| Probability | Critical Impact | High Impact | Medium Impact | Low Impact |
|-------------|----------------|-------------|---------------|------------|
| **High** | 🔴 **Critical** | 🟠 **High** | 🟡 **Medium** | 🟢 **Low** |
| **Medium** | 🟠 **High** | 🟡 **Medium** | 🟡 **Medium** | 🟢 **Low** |
| **Low** | 🟡 **Medium** | 🟡 **Medium** | 🟢 **Low** | 🟢 **Low** |

**Probability Scale**:

- **High (75-100%)**: Current state or inevitable without action
- **Medium (25-75%)**: Likely if conditions persist
- **Low (0-25%)**: Requires multiple failures or unlikely event

**Impact Scale**:

- **Critical**: Project failure or 6+ month delay
- **High**: 50%+ budget increase or major scope reduction
- **Medium**: 1-2 month delay or 20% budget increase
- **Low**: Minor inconvenience, easily mitigated

**Categorization Example**:

```
Risk: "Zero Implementation Code"
Category: Technical / Timeline
Probability: HIGH (100% - current state)
Impact: CRITICAL (6-month+ delay, cannot validate assumptions)
Severity: 🔴 CRITICAL
```

### Phase 3: Mitigation Strategy Development (40-60 minutes)

**Objective**: Define actionable mitigation plans with clear owners and timelines.

**Mitigation Template**:

```markdown
### Risk: [Risk Name]
**Risk Category**: [Category]
**Probability**: [High/Medium/Low]
**Impact**: [Critical/High/Medium/Low]

**Description**: [2-3 sentence explanation]

**Consequences**:
- [Bullet list of specific negative outcomes]

**Mitigation**:
1. **Immediate Action** (0-24 hours): [First step to reduce probability]
2. **Short-term** (1-7 days): [Tactical fixes]
3. **Long-term** (1-4 weeks): [Strategic solutions]

**Priority**: 🔴/🟠/🟡/🟢 [Severity level]
```

**Mitigation Strategies by Type**:

- **Risk Avoidance**: Eliminate risk by changing approach (e.g., avoid GPL by using MIT-licensed alternatives)
- **Risk Reduction**: Decrease probability or impact (e.g., user validation survey reduces "no demand" risk)
- **Risk Transfer**: Shift risk to third party (e.g., managed database service = Azure owns availability)
- **Risk Acceptance**: Acknowledge risk but proceed (e.g., accept 10-user limit for MVP)

### Phase 4: Priority Ranking & Action Plan (20-30 minutes)

**Objective**: Convert risk analysis into executable action items with dependencies and timelines.

**Prioritization Framework**:

1. **🔴 Critical Blockers**: Must resolve before ANY implementation work
   - Example: Tech stack decision, GPL license resolution, user validation
2. **🟠 High Priority**: Address during MVP development (Phases 1-2)
   - Example: CI/CD pipeline, monitoring setup, connection pooling
3. **🟡 Medium Priority**: Defer to post-MVP optimization (Phase 3-4)
   - Example: Advanced caching, performance tuning, multi-region deployment
4. **🟢 Low Priority**: Accept or monitor, no active mitigation needed
   - Example: Azure outages (99.95% SLA acceptable), model availability (Cornell has maintained repo for 4+ years)

**Action Plan Template**:

```markdown
## Immediate Actions Required (Pre-Development)
1. **[Action Name]** - [Description] ([Time estimate], [Priority])
   - Owner: [Who]
   - Deliverable: [What]
   - Dependencies: [Blockers]
   - Success Criteria: [How to validate completion]
```

---

## 📊 ChessCoach Risk Analysis Case Study

### Context

**Project**: AI-powered chess coaching with human behavior alignment
**Phase**: Pre-Implementation (Planning Complete, Zero Code)
**Documentation**: 3,500+ lines across 8 files
**Timeline**: 3 weeks planning, 0 hours implementation
**Budget**: $59/mo Azure (10 concurrent users max)

### Risk Identification Results (16 Risks)

#### 🔴 Critical Risks (4 BLOCKERS)

1. **Zero Implementation Code** (Technical)
   - 3,500+ lines documentation, 0 lines implementation
   - Tech stack undecided (Python vs Node.js)
   - No proof of concept to validate architecture
   - **Mitigation**: Tech stack decision + 4-6 hour POC before MVP

2. **10-User Hard Constraint** (Scalability)
   - PostgreSQL 10 connection limit = architectural ceiling
   - Scaling requires $200+/mo (3.4× cost increase)
   - Viral growth scenarios cause immediate failure
   - **Mitigation**: Define growth strategy OR accept beta constraint

3. **Maia Integration Uncertainty** (Technical/Legal)
   - "Maia-inspired" marketing but zero Maia code
   - GPL-3.0 license viral implications unclear
   - Models may become unavailable (Cornell controls repo)
   - **Mitigation**: Decide Maia models vs statistical analysis + GPL resolution

4. **No User Validation** (Strategic)
   - Zero surveys/interviews with target users
   - Willingness-to-pay untested
   - Feature priorities based on assumptions
   - **Mitigation**: Survey 50+ chess players before implementation

#### 🟠 High Risks (4)

5. **LLM Cost Overrun** (Financial) - $18→$144/mo possible (8× baseline)
2. **Stockfish Performance** (Technical) - B1 tier untested, may need $61/mo upgrade
3. **GPL-3.0 License Contamination** (Legal) - Viral license affects entire codebase
4. **No Market Research** (Strategic) - Competitive positioning undefined

#### 🟡 Medium Risks (5)

9. **WebSocket Scalability** - Sticky sessions prevent horizontal scaling
2. **PostgreSQL Connection Exhaustion** - 10 connections, no pooling configured
3. **Redis Cache Insufficient** - 250 MB may fill if TTL too long
4. **No CI/CD Pipeline** - Manual deployment, no automated testing
5. **No Observability** - Zero logging, monitoring, error tracking

#### 🟢 Low Risks (4)

14. **Maia Model Availability** - Cornell repo stable 4+ years
2. **Azure Service Outages** - 99.95% SLA acceptable for MVP
3. **GDPR Compliance** - Block EU users initially
4. **API Rate Limits** - Well within Azure quotas

### Key Insight: "Analysis Paralysis Pattern"

**Finding**: Project exhibits classic "analysis paralysis" failure mode:

- Extensive planning substitutes for user validation
- Perfect architecture designed for unvalidated user needs
- Cost optimization for unknown usage patterns
- Risk analysis performed AFTER 3 weeks planning (should be first step)

**Lesson**: **Risk analysis should be Phase 0, not Phase 7**. Identifying "zero implementation code" risk earlier would have triggered proof of concept + user validation before comprehensive planning.

### Action Plan Generated

**Critical Path** (Must complete before any implementation):

1. **User Validation Survey** (1 week) - 50+ chess players, willingness-to-pay
2. **Tech Stack Decision** (2 hours) - Python + FastAPI recommended
3. **GPL License Resolution** (3-5 days) - Legal consultation or GPL acceptance
4. **Maia Strategy** (1 day) - Models vs statistical analysis
5. **Load Testing Plan** (1 day) - Performance benchmark definitions

**Go/No-Go Decision Criteria**:

- Proceed if >50% positive user intent in survey
- Otherwise: Pivot or pause project

---

## 🎓 Best Practices & Lessons Learned

### When to Perform Risk Analysis

**Optimal Timing**: **Before significant resource commitment** (ideal: after 1-week exploration, before 1-month planning)

**Risk Analysis Checkpoints**:

- ✅ **Week 1**: Initial concept exploration → Identify top 5 risks before proceeding
- ✅ **Before Planning**: Strategic risks (user demand, competition) → Go/no-go decision
- ✅ **Before Implementation**: Technical/financial/legal risks → Architecture validation
- ✅ **Monthly During Development**: Operational risks (performance, costs, security)
- ✅ **Pre-Launch**: All risk categories → Production readiness assessment

### Common Anti-Patterns to Avoid

#### 1. **Documentation Theater**

**Pattern**: Extensive planning documentation without user validation or proof of concept.
**Detection**: Lines of documentation >> lines of implementation code after 2+ weeks.
**Impact**: Wasted planning effort on features users don't want.
**Fix**: User validation before planning, proof of concept before architecture.

#### 2. **Premature Optimization**

**Pattern**: Architecting for 1000 users before validating 10 users.
**Detection**: Multi-environment setup (dev/staging/prod) for pre-launch MVP.
**Impact**: Increased complexity and cost before product-market fit confirmed.
**Fix**: Single production environment + local dev until PMF validated.

#### 3. **Assumption-Driven Estimates**

**Pattern**: Cost/performance estimates without benchmarks or validation.
**Detection**: Precise numbers ("$18/mo LLM") without supporting data.
**Impact**: Budget overruns or performance failures in production.
**Fix**: Benchmark critical path with realistic data before finalizing estimates.

#### 4. **License Blindness**

**Pattern**: Using GPL-3.0 dependencies in MIT-licensed projects without legal review.
**Detection**: Mixed licenses in package.json/requirements.txt.
**Impact**: Forced relicensing or removal of core functionality.
**Fix**: License audit in Week 1, legal consultation before implementation.

#### 5. **Risk Analysis Too Late**

**Pattern**: Performing risk analysis after 3+ weeks of planning.
**Detection**: Risk analysis document created AFTER architecture/infrastructure docs.
**Impact**: Discovering blockers after significant planning investment.
**Fix**: Risk analysis as Phase 0, before detailed planning begins.

### Risk Analysis Quality Checklist

**Pre-Analysis Validation**:

- [ ] All project documentation reviewed (README, planning, architecture)
- [ ] File inventory audit completed (identify missing artifacts)
- [ ] Dependency licenses catalogued
- [ ] Cost estimates extracted with assumptions documented

**Analysis Quality Metrics**:

- [ ] 10-20 risks identified across 6 categories
- [ ] Each risk has probability/impact assessment
- [ ] Mitigation strategies defined for all 🔴/🟠 risks
- [ ] Critical path blockers identified (risks preventing any progress)
- [ ] Action plan with owners, timelines, and success criteria

**Post-Analysis Actions**:

- [ ] Risk analysis document committed to version control
- [ ] Critical blockers communicated to stakeholders
- [ ] Go/no-go decision made based on risk assessment
- [ ] Monthly risk review scheduled (calendar reminder)

---

## 🛠️ Implementation Guidance

### Creating a Risk Analysis Document

**Step 1: Document Structure** (use this template)

```markdown
# [Project Name] - Comprehensive Risk Analysis

**Generated**: [Date]
**Status**: [Project Phase]
**Risk Assessment Framework**: Technical, Security, Financial, Legal, Operational, Strategic

---

## 🔴 CRITICAL RISKS (High Impact, High Probability)
[List 2-5 blockers that prevent any progress]

## 🟠 HIGH RISKS (High Impact, Medium Probability)
[List 3-6 significant risks requiring mitigation during MVP]

## 🟡 MEDIUM RISKS (Medium Impact, Medium Probability)
[List 4-8 risks to address during optimization phases]

## 🟢 LOW RISKS (Low Impact or Low Probability)
[List 3-5 risks accepted or deferred with monitoring plan]

---

## Risk Matrix Summary
[Table showing all risks by probability × impact]

---

## Immediate Actions Required (Pre-Development)
[Numbered list of 3-7 critical action items with timelines]

---

## Monthly Risk Review Checklist
[Template for ongoing risk monitoring]
```

**Step 2: Risk Identification Workshop** (90-120 minutes)

1. **Documentation Review** (30 min): Read all docs, extract assumptions
2. **Brainstorming Session** (30 min): Generate 30-50 potential risks (quantity over quality)
3. **Categorization** (20 min): Organize into 6 categories
4. **Probability/Impact Assessment** (20 min): Use risk matrix
5. **Prioritization** (10 min): Identify top 5 critical blockers

**Step 3: Mitigation Planning** (60-90 minutes per critical risk)

- Research best practices for similar projects
- Consult domain experts (legal for licensing, DevOps for infrastructure)
- Define 3 mitigation options (avoid, reduce, transfer, accept)
- Estimate cost and timeline for each option
- Recommend approach with rationale

**Step 4: Stakeholder Communication** (30-60 minutes)

- Present critical risks with visual risk matrix
- Explain go/no-go decision criteria
- Propose action plan with resource requirements
- Get approval for mitigation budget (time/money)
- Schedule monthly risk review meetings

### Integrating Risk Analysis into Development Workflow

**Continuous Risk Monitoring**:

```markdown
## Monthly Risk Review Template (15-30 minutes)

### Financial Risks
- [ ] Review Azure spending vs budget ($59 baseline)
- [ ] Check LLM token usage (target: 500/month, alert: >750/month)
- [ ] Validate user count (max: 10, alert: >8 concurrent)

### Technical Risks
- [ ] Check Stockfish response times (target: <2s, alert: >3s)
- [ ] Monitor PostgreSQL connection usage (max: 10, alert: >8)
- [ ] Review error rates (target: <1%, alert: >5%)

### User Feedback Risks
- [ ] Survey active users (NPS score, feature requests)
- [ ] Track engagement metrics (sessions/week, retention)
- [ ] Analyze support tickets (common issues, feature gaps)

### Legal Compliance Risks
- [ ] Audit GPL dependency usage (quarterly)
- [ ] Review privacy policy updates (GDPR, CCPA)
- [ ] Check Azure security center recommendations
```

**Risk Escalation Protocol**:

1. **Green Status**: All metrics within targets → No action
2. **Yellow Status**: Approaching alert thresholds → Prepare mitigation plan
3. **Red Status**: Exceeding thresholds → Execute mitigation immediately
4. **Black Status**: Multiple red metrics → Escalate to leadership, consider pause/pivot

---

## 🔗 Cross-Domain Connections

### Relationship to Bootstrap Learning

- **Risk identification** = Active learning about project unknowns through systematic questioning
- **Mitigation planning** = Knowledge acquisition from domain experts and research
- **Monthly reviews** = Spaced repetition for risk awareness and pattern recognition

### Relationship to Empirical Validation

- **Evidence-based risk assessment** requires research foundation (e.g., GPL license implications)
- **Cost estimates** must be validated with benchmarks, not assumptions
- **User validation surveys** = Empirical research before product development

### Relationship to Meta-Cognitive Awareness

- **Analysis paralysis detection** = Meta-cognitive awareness of learning vs. action balance
- **Risk analysis quality checklist** = Meta-cognitive monitoring of analysis completeness
- **Blind spot identification** = Recognizing what risks were missed and why

### Relationship to Worldview Integration

- **Ethical risk assessment** (e.g., GPL licensing) requires constitutional AI principles
- **User validation** respects human autonomy and beneficence (don't waste user time)
- **Privacy compliance** (GDPR) aligns with dignity and justice foundations

---

## 📊 Metrics & Success Criteria

### Risk Analysis Effectiveness Metrics

- **Pre-Implementation Risk Discovery Rate**: % of production issues identified during pre-implementation analysis (target: 70%+)
- **Cost Variance**: Actual costs vs risk-adjusted estimates (target: <20% variance)
- **Timeline Accuracy**: Actual timeline vs risk-adjusted estimates (target: <30% variance)
- **User Validation Accuracy**: % of features with >50% user demand (target: 80%+)

### Project Health Indicators

- **Documentation-to-Code Ratio**: Lines of documentation / lines of implementation (healthy: 0.1-0.5, analysis paralysis: >1.0)
- **Implementation Velocity**: Features completed per week (accelerating = good, stagnant = risk)
- **User Engagement**: Active users / total registered users (target: >40% monthly active)
- **Financial Runway**: Months remaining at current burn rate (minimum: 6 months)

### Risk Monitoring Dashboard (Example)

```
ChessCoach Risk Dashboard - January 1, 2026
============================================

🔴 CRITICAL RISKS
- Zero Implementation Code: BLOCKED (Tech stack decision required)
- No User Validation: HIGH (Survey scheduled Week 2)

🟠 HIGH RISKS
- LLM Costs: $0/month (baseline: $18, alert: $50, crisis: $91)
- GPL License: UNRESOLVED (Legal consultation scheduled)

🟡 MEDIUM RISKS
- CI/CD Pipeline: NOT IMPLEMENTED (defer to Phase 2)
- Observability: NOT IMPLEMENTED (defer to Phase 2)

🟢 LOW RISKS
- Azure Availability: 99.97% uptime (target: 99.95%)
- Model Availability: STABLE (no changes to Maia repo)

📊 PROJECT HEALTH
- Doc/Code Ratio: INFINITE (3,500 lines doc, 0 lines code) ⚠️
- Financial Runway: UNLIMITED (within $150 MSDN credit)
- User Validation: 0% (0/50 survey responses)
```

---

## 🎓 Continuous Learning

### Areas for Future Enhancement

- **Quantitative Risk Modeling**: Monte Carlo simulation for cost/timeline distributions
- **Risk Correlation Analysis**: How technical risks cascade into financial risks
- **Industry-Specific Frameworks**: Healthcare (HIPAA), Finance (SOC 2), Education (FERPA)
- **AI-Specific Risks**: Model drift, bias detection, LLM hallucinations, prompt injection

### Research Papers for Deeper Mastery

- Boehm, B. W. (1991). "Software Risk Management: Principles and Practices"
- Charette, R. N. (1989). "Software Engineering Risk Analysis and Management"
- Jones, C. (1994). "Assessment and Control of Software Risks"
- Ries, E. (2011). "The Lean Startup" (user validation methodology)

### Practical Experience Building

- Complete 5+ project risk analyses (document patterns)
- Track actual vs predicted risks for calibration
- Interview 10+ project managers about risk failure modes
- Build automated risk monitoring dashboard (Azure dashboards, Grafana)

---

**Version History**:

- **v1.0.0 (January 1, 2026)**: Initial domain knowledge creation from ChessCoach risk analysis experience

**Maintenance Notes**:

- Update with new project case studies (target: 1 per quarter)
- Refine risk categorization framework based on empirical outcomes
- Add industry-specific risk templates (healthcare, finance, education)
- Integrate automated risk detection tools (linters, license scanners, cost monitors)

# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 1 | The proposal ignores NordFrame's actual stated problem—unifying spreadsheet and legacy data across 6 regional warehouses—and instead dismisses their scope as 'NordFrame deserves more than a simple dashboard', aggressively pushing an unsolicited AI and database migration suite. This fails to address NordFrame's operational bottleneck. |
| Scope & Deliverables Clarity | 1 | Fundamentally non-compliant: directly violates hard constraint REQ-004 by proposing a mandatory proprietary cloud migration away from PostgreSQL, while completely omitting RBAC requirements (REQ-005, REQ-006), onboarding plans (REQ-007), and support SLAs (REQ-008). Reaching a score of 2 would require respecting core technical constraints and establishing baseline RBAC scope. |
| Pricing Clarity | 2 | The pricing gives a single lump sum of €98,000 meeting REQ-010 and mentions Year 1 support inclusion (REQ-011), but it provides zero cost breakdown or commercial assumptions for the unsolicited AI modules versus core implementation. Compared to benchmark medium/strong standards that itemize setup, licenses, and support, this is a bare single-figure quote. |
| Timeline Clarity | 1 | Provides no discernible milestone schedule, completely ignoring the mandatory 3-month pilot requirement (REQ-012) and 6-month phased rollout (REQ-013). An unsubstantiated blanket claim of '8 weeks' across migration and multiple AI systems lacks credibility and operational feasibility, aligning with the overpromise benchmark without necessary milestone gating. |
| Completeness vs RFP Requirements | 2 | The proposal violates hard constraint REQ-004, contradicts REQ-003, completely omits REQ-005, REQ-006, REQ-007, REQ-009, and REQ-012, and leaves REQ-002, REQ-008, and REQ-013 vague. Achieving a score of 2 would require addressing the missing governance and RBAC requirements without directly breaching core mandatory constraints. |
| Tone & Persuasiveness | 1 | The tone is patronizing and sales-heavy, brushing aside the client's practical requirements with buzzwords and unverified capabilities. Asserting that complex proprietary database migrations, custom AI demand models, and multi-site rollouts will complete in 8 weeks destroys credibility, matching the overpromise benchmark anti-patterns. |
| Risk/Assumptions Transparency | 1 | The proposal is entirely silent regarding project assumptions, database dependencies, or deployment risks, in direct contravention of REQ-009. Unlike strong benchmark examples that clearly delineate data prerequisite boundaries and risk mitigations, this proposal discloses zero technical limitations. |

**Overall: 1.3 / 5 — Needs significant revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **Automated low-stock alerts sent to warehouse managers when items fall below a configurable threshold.**
> The proposal lists 'Real-time alerts across all locations simultaneously' but fails to address configurable thresholds or targeting alerts specifically to warehouse managers.
> Proposal: "Real-time alerts across all locations simultaneously."
> **Suggested fix:** Revise to: 'Automated low-stock alerts dispatched via email/SMS to individual warehouse managers whenever stock levels cross user-configurable thresholds per SKU/location.'
>

> 🚫 Contradicted: **Integration with existing PostgreSQL inventory database.**
> The RFP mandates integrating directly with the existing PostgreSQL inventory database, whereas the proposal insists on migrating away from it.
> Proposal: "migrating away from your current PostgreSQL database to our proprietary cloud data platform"
> **Suggested fix:** Replace the database migration proposal with: 'Direct, read-optimized integration connecting our application layer directly to your existing PostgreSQL inventory database without schema alteration.'
>

> 🚫 Contradicted: **No migration to a new database.**
> Directly violates a hard constraint by explicitly proposing a migration away from PostgreSQL to a proprietary cloud data platform.
> Proposal: "Full platform migration: we recommend migrating away from your current PostgreSQL database to our proprietary cloud data platform for best performance and scalability."
> **Suggested fix:** Delete all mentions of proprietary cloud platform migration and explicitly confirm: 'In strict accordance with RFP constraints, we commit to no database migration; all operations will query and integrate with your existing PostgreSQL database.'
>

> ❌ Missing: **Role-based access restricting warehouse managers so they only see their own site.**
> The proposal makes no mention of role-based access control or site-level data restriction for warehouse managers.
> **Suggested fix:** Add: 'Role-based access control (RBAC) enforces strict site-level isolation, ensuring regional warehouse managers can view and manage data solely for their assigned warehouse.'
>

> ❌ Missing: **Role-based access allowing HQ staff to see all sites.**
> The proposal does not specify role-based permissions allowing central/HQ staff to view consolidated inventory across all locations.
> **Suggested fix:** Add: 'HQ staff accounts are provisioned with global administrative visibility to view consolidated and comparative inventory across all 6 warehouse sites.'
>

> ❌ Missing: **A data migration / onboarding plan for rolling this out across all 6 sites with minimal disruption.**
> While proprietary data platform migration is mentioned, there is no phased onboarding or data migration plan addressing zero/minimal business disruption across the 6 operating sites.
> **Suggested fix:** Include a section outlining: 'A phased, zero-downtime site onboarding plan detailing step-by-step rollout across the 6 regional locations without interrupting ongoing logistics operations.'
>

> ⚠️ Vague: **Support & maintenance terms after go-live, including response times and SLAs.**
> The proposal mentions 'one year of support' in the pricing section, but omits all terms, SLA targets, support hours, and incident response times.
> Proposal: "including the data platform migration, all AI modules, and one year of support."
> **Suggested fix:** Define support terms: 'Includes Year 1 SLA-backed maintenance featuring 24/7 critical incident response (<1 hour response time) and standard business hours support for minor issues.'
>

> ❌ Missing: **Clear documentation of any assumptions, limitations, or risks, since inventory decisions will be made based on this system.**
> The proposal omits all assumptions, delivery risks, and operational limitations despite the client's explicit instruction regarding mission-critical inventory decisions.
> **Suggested fix:** Add an 'Assumptions and Risk Management' section detailing dependencies on existing PostgreSQL connectivity, data cleanliness expectations, and technical fallbacks.
>

> ❌ Missing: **Working pilot at one warehouse within 3 months.**
> The proposal offers a generic 8-week total delivery but fails to define, schedule, or commit to a working pilot at one warehouse within 3 months.
> **Suggested fix:** Insert milestone: 'Phase 1 Pilot: Deploy a fully functional working pilot at one designated warehouse site within 8 weeks, validating core dashboard workflows before broad rollout.'
>

> ⚠️ Vague: **Full rollout to all 6 sites within 6 months.**
> An unphased '8 weeks' total delivery claim is made, but it lacks any detailed milestone breakdown or site-by-site rollout schedule covering the 6 warehouses.
> Proposal: "we are confident we can deliver the complete suite — including the platform migration and all analytics modules — within 8 weeks"
> **Suggested fix:** Provide a detailed schedule showing: 'Phase 1: Pilot site go-live at Month 2; Phase 2: Sequential rollout across remaining 5 sites completed by Month 5, comfortably within the 6-month deadline.'
>

## Verdict

The proposal is non-compliant and poses immediate disqualification risk due to directly violating hard constraint REQ-004 by proposing migration away from the client's PostgreSQL database. Additionally, it fails to specify role-based access control (REQ-005/006), onboarding procedures (REQ-007), support SLAs (REQ-008), risk documentation (REQ-009), or a phased pilot schedule (REQ-012). The response must be fundamentally realigned to integrate directly with NordFrame's existing database architecture and structured around realistic, client-specified delivery milestones.

# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 1 | The proposal dismisses NordFrame's core operational requirement ('NordFrame deserves more than a simple dashboard') and introduces unrequested AI capabilities while contradicting mandatory technical constraints like database preservation. To move to a score of 2, it would need to accurately acknowledge NordFrame's fragmented tracking across spreadsheets and the legacy PostgreSQL database without deflecting to unrelated scope. |
| Scope & Deliverables Clarity | 1 | The proposal directly breaches the mandatory hard constraint against database migration (REQ-004) by insisting on migrating away from PostgreSQL, completely omits role-based access control (REQ-005, REQ-006) and onboarding plans (REQ-007), and introduces unrequested scope creep (demand forecasting, supplier scoring). Due to the contradiction of a hard constraint and multiple missing core deliverables, this cannot exceed 1. |
| Pricing Clarity | 2 | The commercial offer states a single fixed figure (€98,000) that aligns with REQ-010 and incorporates year-one support per REQ-011. However, it lacks any itemized breakdown of labor, licenses, AI modules, or support costs, resembling benchmark weak/medium samples. To reach a score of 3, the proposal must break down costs between discovery, software development, data integration, and post-launch maintenance. |
| Timeline Clarity | 1 | The timeline consists of an unsupported blanket promise of 8 weeks for the entire project, omitting the mandatory 3-month single-site pilot (REQ-012) and failing to delineate phased deployment milestones across the 6 warehouses (REQ-013). To achieve a score of 2, it must break down delivery into distinct phases and explicitly schedule the pilot. |
| Completeness vs RFP Requirements | 2 | The submission fails across most RFP requirements: it contradicts two technical requirements (REQ-003, REQ-004 including a hard constraint), omits role-based access (REQ-005, REQ-006), onboarding (REQ-007), risk documentation (REQ-009), and the pilot milestone (REQ-012). To reach a score of 2, the bid must eliminate contradictions with client constraints and supply basic responses to the omitted requirements. |
| Tone & Persuasiveness | 1 | The tone is condescending and overpromising, explicitly dismissing the client's stated scope ('NordFrame deserves more than a simple dashboard') while asserting an ungrounded 8-week completion for complex AI and platform migrations. To achieve a score of 2, the text must adopt a grounded, client-focused tone that respects the client's articulated business problem instead of peddling generic AI hyperbole. |
| Risk/Assumptions Transparency | 1 | The proposal completely omits any assumptions, operational boundaries, or risk factors, directly violating REQ-009. To move to a score of 2, the document must at least list standard project assumptions regarding PostgreSQL schema accessibility and warehouse user engagement. |

**Overall: 1.3 / 5 — Needs significant revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **A web-based dashboard showing real-time inventory levels across all 6 warehouses.**
> The proposal mentions a 'Real-time dashboard across all 6 warehouses', but fails to specify that it is a web-based interface or explain how real-time inventory levels will be displayed.
> Proposal: "Real-time dashboard across all 6 warehouses, plus predictive analytics on top."
> **Suggested fix:** Deliver a responsive, web-based dashboard accessible via modern web browsers displaying live inventory counts across all 6 regional warehouse facilities.
>

> ⚠️ Vague: **Automated low-stock alerts sent to warehouse managers when items fall below a configurable threshold.**
> The proposal mentions 'Real-time alerts across all locations simultaneously' but omits automated low-stock triggers, configurable thresholds, and targeting warehouse managers.
> Proposal: "Real-time alerts across all locations simultaneously."
> **Suggested fix:** Implement automated low-stock email and in-dashboard notifications delivered directly to warehouse managers whenever SKU stock levels breach user-configurable minimum thresholds.
>

> 🚫 Contradicted: **Integration with existing PostgreSQL inventory database.**
> The RFP explicitly requests integration with the existing PostgreSQL database, but the proposal advocates migrating away from PostgreSQL to a proprietary platform.
> Proposal: "we recommend migrating away from your current PostgreSQL database to our proprietary cloud data platform for best performance and scalability."
> **Suggested fix:** Connect directly to NordFrame's existing PostgreSQL inventory database using standard, read-optimized database connectors without altering the underlying schema.
>

> 🚫 Contradicted: **No migration to a new database.**
> The proposal directly violates the hard constraint 'no migration to a new database' by recommending a complete platform migration away from PostgreSQL.
> Proposal: "Full platform migration: we recommend migrating away from your current PostgreSQL database to our proprietary cloud data platform for best performance and scalability."
> **Suggested fix:** Retain the existing PostgreSQL database as the sole system of record; no data migration to an external database will take place.
>

> ❌ Missing: **Role-based access restricting warehouse managers so they only see their own site.**
> The proposal makes no mention of role-based access control or restricting warehouse managers to their assigned warehouse facility.
> **Suggested fix:** Enforce server-side role-based access control (RBAC) ensuring warehouse managers can view and manage inventory data solely for their designated warehouse site.
>

> ❌ Missing: **Role-based access allowing HQ staff to see all sites.**
> The proposal does not address access permissions for HQ personnel to view aggregated data across all 6 sites.
> **Suggested fix:** Configure an HQ role granting corporate stakeholders unrestricted visibility and consolidated reporting across all 6 warehouse locations.
>

> ❌ Missing: **A data migration / onboarding plan for rolling this out across all 6 sites with minimal disruption.**
> No data onboarding or multi-site rollout plan is provided to transition the 6 warehouses with minimal disruption.
> **Suggested fix:** Provide a phased onboarding plan detailing data reconciliation from legacy sources, user training schedules, and site-by-site transition steps designed to ensure zero operational downtime.
>

> ⚠️ Vague: **Support & maintenance terms after go-live, including response times and SLAs.**
> While the pricing section mentions 'one year of support', there are no defined terms, response time targets, or SLA commitments.
> Proposal: "including the data platform migration, all AI modules, and one year of support."
> **Suggested fix:** Include formal SLA terms for the 12-month support period, such as 2-hour response times for critical severity incidents during operating hours (08:00–18:00 CET).
>

> ❌ Missing: **Clear documentation of any assumptions, limitations, or risks, since inventory decisions will be made based on this system.**
> The proposal contains no documentation of technical assumptions, operational limitations, or project risks.
> **Suggested fix:** Add an 'Assumptions and Risk Management' section documenting system prerequisites, network dependencies, and data-accuracy boundaries.
>

> ❌ Missing: **Working pilot at one warehouse within 3 months.**
> The proposal fails to offer a single-warehouse pilot within 3 months, instead promising a full big-bang delivery in 8 weeks.
> **Suggested fix:** Structure the timeline to introduce a 3-month pilot phase at a single warehouse to validate functionality and user adoption prior to regional rollout.
>

> ⚠️ Vague: **Full rollout to all 6 sites within 6 months.**
> The 8-week timeline technically falls under 6 months, but it compresses the entire implementation into an unrealistic window without defining the rollout across the 6 locations.
> Proposal: "within 8 weeks, well ahead of typical industry timelines."
> **Suggested fix:** Establish a structured 6-month delivery schedule defining discovery, pilot testing, and sequential rollout milestones across all 6 locations.
>

## Verdict

This proposal is non-compliant and fundamentally disqualifying because it directly violates a mandatory hard constraint by insisting on migrating away from NordFrame's existing PostgreSQL database. Furthermore, critical requirements—such as role-based access control, the 3-month pilot, the 6-site onboarding plan, and risk documentation—are omitted in favor of unrequested AI scope creep. Finally, the ungrounded 8-week delivery timeline lacks credibility and fails to provide the structured milestones requested by the client.

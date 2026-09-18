# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 2 | The proposal correctly identifies that NordFrame operates six warehouses relying on spreadsheets and a legacy system, but it merely restates the background section from the RFP in two sentences ('NordFrame's six warehouses currently rely on spreadsheets and a legacy system...'). It fails to elaborate on specific operational implications, such as inventory reconciliation bottlenecks, stockout impacts across regional distribution points, or data integrity hurdles. To achieve a higher score, the proposal must connect the proposed solution directly to operational logistics workflows and quantifiable inventory accuracy outcomes. |
| Scope & Deliverables Clarity | 3 | Core technical scope items (REQ-001 through REQ-006) are clearly acknowledged, including PostgreSQL integration without migration and role-based permissions. However, REQ-007 (onboarding/migration plan) is described only in a single vague sentence ('onboard warehouses in phases'), and REQ-008 (support terms, SLAs, response times) is entirely missing. To reach a score of 4, the proposal must define an actionable site-by-site onboarding approach and provide defined post-launch support commitments with response time tiers. |
| Pricing Clarity | 2 | The proposal provides an indicative bracket of €70,000 to €110,000 but defers the actual commitment by stating 'We will provide a firm quote after discovery'. Furthermore, it completely omits confirmation of first-year support inclusion (REQ-011). As illustrated in the benchmark references, an uncommitted range without a line-item breakdown or clear statement of inclusions falls into the weak-to-medium category. To achieve a score of 3 or higher, the proposal must commit to a binding commercial figure and itemize implementation against first-year support. |
| Timeline Clarity | 2 | The timeline fails to present concrete milestones, stating only that they will 'aim to complete full rollout within the timeframe you've outlined' and deferring exact schedules to discovery ('Exact scheduling will be confirmed once we begin discovery'). It neither binds itself to the 3-month single-site pilot (REQ-012) nor the 6-month full rollout (REQ-013). To progress to a score of 3, the proposal must explicitly schedule the pilot delivery at month 3 and full rollout across all 6 warehouses at month 6. |
| Completeness vs RFP Requirements | 3 | While the core software features and database constraints (REQ-001 to REQ-006) are met, significant gaps exist across operational and commercial requirements: post-go-live SLAs (REQ-008), risk and assumptions documentation (REQ-009), and first-year support inclusion (REQ-011) are missing, while the rollout plan (REQ-007), budget commitment (REQ-010), and timeline milestones (REQ-012, REQ-013) remain vague. To achieve a score of 4, the draft must close the omitted support and risk sections and convert the vague commercial/schedule ranges into firm commitments. |
| Tone & Persuasiveness | 2 | The tone is courteous but unsubstantiated. The qualification in 'Why Clarion' is generic marketing boilerplate ('Clarion has delivered inventory and logistics dashboards for several mid-size distribution companies across the DACH region') without citing case studies, metrics, or client evidence. Crucially, non-committal language such as 'aim to complete' and deferring quotes and dates until after discovery undermines credibility. To reach a score of 3, the proposal needs specific proof points and authoritative commitments rather than conditional statements. |
| Risk/Assumptions Transparency | 1 | The proposal completely ignores REQ-009, containing zero documentation of technical assumptions, data dependencies, operational limitations, or delivery risks. Given that the RFP explicitly notes that operational inventory decisions will be made using this platform, omitting risks regarding data validation, network latency, or PostgreSQL access is a major failure. To reach a score of 2 or 3, the proposal must introduce an Assumptions and Risks section addressing database dependencies and mitigation plans. |

**Overall: 2.1 / 5 — Needs revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **A data migration / onboarding plan for rolling this out across all 6 sites with minimal disruption.**
> The proposal only mentions onboarding warehouses in phases to reduce disruption, omitting any detailed data migration/reconciliation plan, site sequence, or onboarding operational procedures.
> Proposal: "Rollout approach: we will onboard warehouses in phases rather than all at once, to reduce disruption during the transition."
> **Suggested fix:** Replace the bullet with: 'Rollout approach: We will execute a phased onboarding plan starting with site 1 as a validation baseline, followed by sequential onboarding of sites 2–6 in pairs. Each site transition includes legacy spreadsheet reconciliation, data validation runs, manager training workshops, and parallel operations to ensure zero operational downtime.'
>

> ❌ Missing: **Support & maintenance terms after go-live, including response times and SLAs.**
> The proposal contains no mention of support and maintenance terms, response times, or SLAs post-go-live.
> **Suggested fix:** Add a dedicated section: '## Support & Maintenance: Includes 12 months of post-go-live support covering business hours (08:00–18:00 CET). Critical severity incidents (system outage/dashboard down) receive response within 2 hours; non-critical issues receive response within 1 business day, backed by guaranteed SLA escalation paths.'
>

> ❌ Missing: **Clear documentation of any assumptions, limitations, or risks, since inventory decisions will be made based on this system.**
> The proposal provides no documentation of assumptions, limitations, or technical/delivery risks, despite inventory decisions relying on system accuracy.
> **Suggested fix:** Add a section: '## Assumptions, Limitations & Risks: We assume read-only credentials to the PostgreSQL database with stable network connectivity across all 6 sites. Dashboard reporting relies on existing transaction logging accuracy; corrupted legacy spreadsheet data must be reconciled prior to site onboarding. Mitigation strategies include quarantine logs for malformed inventory records.'
>

> ⚠️ Vague: **Total project budget of €80,000–€120,000.**
> Pricing is presented as an uncommitted, non-binding range of €70,000–€110,000 with a firm quote deferred until after discovery.
> Proposal: "Our typical packages for a project of this scope range from €70,000 to €110,000 depending on final integration complexity. We will provide a firm quote after discovery."
> **Suggested fix:** Replace with a fixed-fee breakdown: 'Fixed Project Investment: €95,000 total (Discovery & PostgreSQL integration: €25,000; Dashboard & Alerting implementation: €35,000; Phased 6-site onboarding: €20,000; 12 months comprehensive support: €15,000). All deliverables are included within this firm price.'
>

> ❌ Missing: **Inclusion of the first year of support within the total budget.**
> The proposal does not mention whether post-go-live support or the first year of support is included in the stated pricing range.
> **Suggested fix:** Add explicit confirmation: 'The fixed total investment includes comprehensive Level 2/3 maintenance and support for the full first year following go-live.'
>

> ⚠️ Vague: **Working pilot at one warehouse within 3 months.**
> The proposal mentions a 'pilot phase' but fails to commit to the required 3-month milestone or identify the pilot scope.
> Proposal: "followed by a pilot phase, and aim to complete full rollout within the timeframe you've outlined. Exact scheduling will be confirmed once we begin discovery."
> **Suggested fix:** Update timeline to state: 'Month 1–3: Discovery, PostgreSQL integration, and delivery of a fully functioning single-warehouse pilot within 3 months of project kickoff.'
>

> ⚠️ Vague: **Full rollout to all 6 sites within 6 months.**
> The proposal states it will 'aim to complete full rollout within the timeframe you've outlined' and defers exact scheduling to discovery, rather than committing to rollout across all 6 sites within 6 months.
> Proposal: "aim to complete full rollout within the timeframe you've outlined. Exact scheduling will be confirmed once we begin discovery."
> **Suggested fix:** Update timeline to state: 'Month 4–6: Phased expansion across the remaining five regional facilities, completing full 6-warehouse rollout and handover within 6 months of kickoff.'
>

## Verdict

The proposal successfully addresses the core software capabilities and database constraints (real-time visibility, PostgreSQL integration, and role-based access), but it fails to provide binding commercial and schedule commitments. Most critically, post-launch support terms (REQ-008), first-year support cost inclusion (REQ-011), and risk/assumptions documentation (REQ-009) are entirely absent. Additionally, the budget and timeline defer fixed commitments until post-discovery, which must be resolved into firm fixed pricing and explicit 3-month pilot and 6-month full rollout milestones before submission.

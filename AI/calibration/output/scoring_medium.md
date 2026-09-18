# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 2 | Under 'Our Understanding', the proposal merely paraphrases the RFP background statement ('relies on spreadsheets and a legacy system') without providing any insight into operational impacts such as stockout rates, cross-warehouse transfer friction across Germany and Austria, or inventory discrepancies. To achieve a score of 3, the proposal must elaborate on NordFrame's specific multi-site logistics challenges rather than offering a minimal two-sentence restatement. |
| Scope & Deliverables Clarity | 3 | Core functional requirements (REQ-001 through REQ-006) are clearly agreed to, including PostgreSQL preservation and role-based permissions. However, REQ-008 (support terms, SLAs, response times) is entirely missing, and REQ-007 provides only a one-sentence rollout statement ('onboard warehouses in phases'). To achieve a score of 4, the vendor must provide explicit SLA parameters and detailed onboarding and data migration deliverables. |
| Pricing Clarity | 2 | While the indicative range of €70,000 to €110,000 aligns roughly with NordFrame's budget (REQ-010), the proposal explicitly defers commitment ('firm quote after discovery') and completely omits the mandatory inclusion of Year 1 support (REQ-011). To achieve a score of 3, Clarion must offer a firm, itemized price and explicitly confirm whether the first year of support and maintenance is included in the quoted figure. |
| Timeline Clarity | 2 | The timeline fails to make binding commitments for the 3-month pilot (REQ-012) or the 6-month full rollout (REQ-013), relying on non-committal phrasing ('aim to complete') and stating that exact scheduling will only be confirmed after discovery. To achieve a score of 3, the proposal must establish explicit milestone dates for Month 3 pilot acceptance and Month 6 full rollout across all 6 warehouses. |
| Completeness vs RFP Requirements | 3 | Out of 13 RFP requirements, only 6 are met. Three requirements are completely missing (REQ-008 Support SLAs, REQ-009 Risks/Assumptions, REQ-011 Support in budget) and four are vague (REQ-007 Onboarding plan, REQ-010 Pricing commitment, REQ-012 3-month pilot, REQ-013 6-month rollout). Because more than half of the requirements are deficient or absent, the proposal falls squarely under score anchor 2. To reach a score of 3, the proposal must resolve the omitted support, SLA, risk, and budgeting items. |
| Tone & Persuasiveness | 2 | The proposal uses non-committal hedging language ('aim to complete', 'typical packages', 'firm quote after discovery') and generic qualifications in 'Why Clarion' without citing specific client cases, metrics, or technologies. To achieve a score of 3, the proposal must replace tentative phrasing with contractual commitments and substantiate its DACH regional experience with concrete references or outcomes. |
| Risk/Assumptions Transparency | 1 | The proposal does not identify any assumptions, dependencies, technical limitations, or operational risks, completely failing REQ-009 despite the RFP emphasizing that critical inventory decisions depend on this system. To achieve a score of 2, the proposal must at minimum list key technical dependencies (such as PostgreSQL access rights, schema stability, and legacy spreadsheet data cleanliness). |

**Overall: 2.1 / 5 — Needs revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **A data migration / onboarding plan for rolling this out across all 6 sites with minimal disruption.**
> The proposal mentions onboarding in phases to minimize disruption, but provides no migration methodology, site sequence, training plan, or legacy cutover process.
> Proposal: "Rollout approach: we will onboard warehouses in phases rather than all at once, to reduce disruption during the transition."
> **Suggested fix:** Replace with: 'Rollout Plan: We will execute a 3-stage phased rollout. Phase 1 deploys the pilot at Warehouse 1 with automated data ingestion from legacy spreadsheets into PostgreSQL. Phase 2 rolls out to Warehouses 2–4 with dedicated local staff training. Phase 3 completes Warehouses 5–6, ensuring continuous operational continuity without downtime.'
>

> ❌ Missing: **Support & maintenance terms after go-live, including response times and SLAs.**
> The proposal does not contain any post go-live support terms, response times, or SLA definitions.
> **Suggested fix:** Add a 'Support & Maintenance' section: 'Clarion provides 12 months of post go-live support, covering Monday–Friday 08:00–18:00 CET. Critical incidents (Severity 1) carry a 1-hour response SLA and 4-hour target resolution; standard queries carry a 4-hour response SLA.'
>

> ❌ Missing: **Clear documentation of any assumptions, limitations, or risks, since inventory decisions will be made based on this system.**
> The proposal contains no section or mention of assumptions, operational limitations, or project risks, which is critical for an inventory decision system.
> **Suggested fix:** Add an 'Assumptions & Risks' section: 'Assumptions & Risks: (1) NordFrame will provide read access to the PostgreSQL database by Week 2; (2) Data format inconsistencies in legacy spreadsheets will be cleansed during discovery; (3) Real-time sync latency depends on existing warehouse network connectivity, mitigated by local caching.'
>

> ⚠️ Vague: **Total project budget of €80,000–€120,000.**
> The proposal quotes a non-binding range of €70,000–€110,000 and states a firm quote will only be provided after discovery, leaving the final commitment uncertain.
> Proposal: "Our typical packages for a project of this scope range from €70,000 to €110,000 depending on final integration complexity. We will provide a firm quote after discovery."
> **Suggested fix:** Replace with: 'Fixed Pricing: Total implementation cost is €95,000 fixed fee, falling directly within NordFrame’s €80,000–€120,000 budget, broken down into €75,000 for development/rollout and €20,000 for Year 1 support.'
>

> ❌ Missing: **Inclusion of the first year of support within the total budget.**
> The proposal does not specify whether the indicative fee includes the first year of support required by the RFP.
> **Suggested fix:** Add: 'The total project fee includes comprehensive Year 1 post go-live support and maintenance at no additional charge.'
>

> ⚠️ Vague: **Working pilot at one warehouse within 3 months.**
> The proposal mentions a pilot phase but fails to commit to the required 3-month timeline, deferring exact scheduling to post-discovery.
> Proposal: "We will begin with discovery and design, followed by a pilot phase, and aim to complete full rollout within the timeframe you've outlined. Exact scheduling will be confirmed once we begin discovery."
> **Suggested fix:** Replace with: 'Milestone 1: Discovery, configuration, and a fully functional pilot deployment at Warehouse 1 will be completed within 3 months of contract kickoff.'
>

> ⚠️ Vague: **Full rollout to all 6 sites within 6 months.**
> The proposal merely states it will 'aim to complete full rollout within the timeframe' rather than committing to the mandatory 6-month deadline across all 6 sites.
> Proposal: "aim to complete full rollout within the timeframe you've outlined. Exact scheduling will be confirmed once we begin discovery."
> **Suggested fix:** Replace with: 'Milestone 2: Following the pilot, rollout across the remaining 5 warehouses will complete within 6 months from project kickoff.'
>

## Verdict

The proposal successfully covers the core functional software requirements and database constraints (REQ-001 to REQ-006), but it is severely undermined by missing commercial and operational sections. Crucial RFP mandates regarding post go-live support SLAs (REQ-008), risk/assumption documentation (REQ-009), and first-year support budget inclusion (REQ-011) are entirely omitted. Furthermore, the timeline and pricing commitments remain non-binding and vague, requiring substantial revision before the proposal can be considered competitive.

# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 1 | The proposal demonstrates virtually no understanding of NordFrame's operational context. It reduces a multi-site logistics tracking challenge split across legacy tools and spreadsheets to a generic two-sentence statement: 'NordFrame needs better visibility into warehouse inventory.' |
| Scope & Deliverables Clarity | 1 | Deliverables are reduced to three superficial bullet points. The proposal omits the core PostgreSQL integration constraint (REQ-003), fails to detail RBAC site isolation (REQ-004, REQ-005), and provides no rollout plan (REQ-006) or support SLA terms (REQ-007). |
| Pricing Clarity | 1 | No commercial figures, cost model, or inclusions are presented. By stating 'Pricing will be provided upon further discussion', the proposal directly fails the RFP budget requirements (REQ-009, REQ-010) and falls far below benchmark standards for commercial clarity. |
| Timeline Clarity | 1 | There is no schedule, milestone breakdown, or calendar. Vague statements like 'deliver the solution in a timely manner' ignore the RFP's specific gates for a 3-month single-site pilot (REQ-011) and 6-month full rollout (REQ-012). |
| Completeness vs RFP Requirements | 1 | The response is fundamentally incomplete. Multiple mandatory requirements and hard constraints—including PostgreSQL integration, RBAC segmentation, onboarding methodology, SLA commitments, and budget compliance—are omitted or deferred. |
| Tone & Persuasiveness | 1 | The response relies on unsubstantiated boilerplate marketing phrases ('modern, scalable cloud architecture and industry best practices', 'talented team of engineers passionate about solving real business problems') with zero client-specific technical depth or persuasive rigor. |
| Risk/Assumptions Transparency | 1 | The proposal contains zero transparency regarding assumptions, limitations, dependencies, or operational risks, completely failing REQ-008. |

**Overall: 1.0 / 5 — Needs significant revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **Provide a web-based dashboard showing real-time inventory levels across all 6 warehouses.**
> The proposal mentions building a real-time dashboard, but omits any reference to multi-warehouse visibility across the 6 regional sites.
> Proposal: "We will build a cloud-based dashboard that displays inventory data in real time."
> **Suggested fix:** Expand the Approach and Features sections to explicitly commit: 'We will deliver a web-based dashboard providing real-time, consolidated and site-by-site inventory tracking across all 6 regional warehouses in Germany and Austria.'
>

> ⚠️ Vague: **Provide automated low-stock alerts sent to warehouse managers when items fall below a configurable threshold.**
> The proposal lists 'Notifications for low stock' as a feature bullet without mentioning automated delivery to warehouse managers or configurable alert thresholds.
> Proposal: "Notifications for low stock"
> **Suggested fix:** Replace the bullet with: 'Automated low-stock alert engine that triggers email/system notifications to designated warehouse managers whenever SKU quantities breach user-configurable minimum thresholds.'
>

> ❌ Missing: **Integrate with existing PostgreSQL inventory database with no migration to a new database.**
> The proposal does not mention integrating with NordFrame's existing PostgreSQL inventory database or commit to avoiding database migration, violating a mandatory constraint.
> **Suggested fix:** Add a dedicated Technical Architecture section stating: 'The solution will connect directly to NordFrame’s existing PostgreSQL inventory database via a secure, read-only/read-write connector with zero migration to a new database engine.'
>

> ⚠️ Vague: **Provide role-based access such that warehouse managers only see their own site.**
> The proposal lists 'Secure login for different users' but fails to define site-specific role-based access control restricting warehouse managers to their own facility.
> Proposal: "Secure login for different users"
> **Suggested fix:** Update the bullet to: 'Role-based access control (RBAC) configured so warehouse managers are strictly restricted to data, alerts, and inventory views for their specific facility.'
>

> ❌ Missing: **Provide role-based access such that HQ staff can see all sites.**
> There is no mention of HQ staff roles or enterprise-wide consolidated visibility across all warehouses.
> **Suggested fix:** Add explicit role definition: 'HQ staff accounts are provisioned with multi-site permissions to monitor and report across all 6 warehouse locations simultaneously.'
>

> ❌ Missing: **Deliver a data migration / onboarding plan for rolling out across all 6 sites with minimal disruption.**
> The proposal provides no data onboarding, rollout, or migration plan for deploying across the 6 regional locations without operational disruption.
> **Suggested fix:** Add an 'Onboarding and Rollout Plan' detailing phased data ingestion, validation against current spreadsheets/legacy systems, and site-by-site onboarding procedures designed to ensure zero downtime.
>

> ❌ Missing: **Provide support & maintenance terms after go-live, including response times and SLAs.**
> Post-go-live support and maintenance terms, response times, and SLA definitions are entirely omitted.
> **Suggested fix:** Include a 'Support & Maintenance' section: 'Year 1 post-go-live support includes 24/7 incident monitoring, a 1-hour response time for critical P1 outages, and 99.9% application uptime SLAs.'
>

> ❌ Missing: **Provide clear documentation of any assumptions, limitations, or risks.**
> The proposal completely lacks a risks, assumptions, or technical limitations section despite inventory decisions depending on system fidelity.
> **Suggested fix:** Insert an 'Assumptions and Risk Management' section documenting dependencies on PostgreSQL network connectivity, schema documentation, and data quality reconciliation risks.
>

> ⚠️ Vague: **Total project pricing must fall within €80,000–€120,000.**
> Pricing is entirely deferred rather than providing a fixed commercial offer within the mandated €80,000–€120,000 window.
> Proposal: "Pricing will be provided upon further discussion of detailed requirements, and will depend on final scope."
> **Suggested fix:** Provide a fixed-fee milestone breakdown totalling between €80,000 and €120,000 (e.g., discovery & integration €25,000; dashboard development & RBAC €45,000; testing & rollout €15,000; Year 1 support €15,000; Total €100,000 ex. VAT).
>

> ❌ Missing: **The total budget must include the first year of support.**
> No inclusion or pricing for first-year support is articulated.
> **Suggested fix:** Explicitly confirm within the pricing schedule: 'The total commercial fee is fully inclusive of 12 months of post-go-live software support and maintenance.'
>

> ⚠️ Vague: **Deliver a working pilot at one warehouse within 3 months.**
> The proposal gives generic timeline generalities without committing to a single-warehouse working pilot delivered within 3 months.
> Proposal: "We will begin work shortly after contract signing and aim to deliver the solution in a timely manner, with regular updates along the way."
> **Suggested fix:** Define Phase 1: 'Phase 1 delivers an operational pilot at one designated warehouse within 3 months of contract award, including integration testing and initial manager review.'
>

> ❌ Missing: **Deliver full rollout to all 6 sites within 6 months.**
> The proposal contains no delivery milestone or schedule committing to full 6-site rollout within 6 months.
> **Suggested fix:** Define Phase 2: 'Phase 2 scales deployment across the remaining 5 warehouses, achieving full go-live across all 6 sites within 6 months of contract kickoff.'
>

## Level 3 — Detected client priority

> No explicit evaluation weighting or priority is stated in the RFP; operational continuity and data boundary constraints appear critical based on Requirements 3 and 4.
> *(User confirms/adjusts this before scoring proceeds.)*

## Verdict

This proposal is non-compliant and would be eliminated during initial screening. It completely defers pricing, omits all timeline milestones, and ignores critical hard constraints including PostgreSQL database integration and site-specific role-based access control. To become competitive, the proposal requires comprehensive technical and commercial elaboration aligning to all twelve RFP requirements rather than generic marketing placeholders.

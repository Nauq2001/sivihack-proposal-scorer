# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 2 | The proposal correctly identifies NordFrame's general need by writing that 'NordFrame needs better visibility into warehouse inventory', but it only restates the objective thinly with zero contextual detail regarding the 6 regional facilities in Germany and Austria, the split spreadsheet tracking, or legacy system constraints. To achieve a score of 3, the proposal would need to elaborate specifically on NordFrame's current multi-site operational challenges rather than providing a one-sentence restatement. |
| Scope & Deliverables Clarity | 2 | Some high-level scope items are listed under Features (such as 'Real-time inventory dashboard' and 'Notifications for low stock'), but all relevant requirements are vague or missing. Crucially, the mandatory hard constraint for PostgreSQL database integration (REQ-003) is omitted entirely, and role-based permissions (REQ-004, REQ-005) are reduced to 'Secure login for different users'. To reach a score of 3, the proposal must explicitly describe architectural boundaries, PostgreSQL integration without migration, and specific onboarding deliverables. |
| Pricing Clarity | 1 | The proposal is fundamentally non-compliant regarding commercials. It provides no costs, no fee structure, and no budget range, stating instead: 'Pricing will be provided upon further discussion of detailed requirements, and will depend on final scope.' It completely fails to satisfy REQ-009 (€80k–€120k budget) and REQ-010 (first-year support inclusion). To achieve a score of 2, the proposal would at minimum need to present an indicative price range or commercial model addressing the RFP parameters. |
| Timeline Clarity | 1 | The proposal offers no tangible timeline or milestones, stating only that BrightPath will 'aim to deliver the solution in a timely manner, with regular updates along the way.' It ignores the explicit milestones in REQ-011 (3-month pilot at one warehouse) and REQ-012 (full 6-site rollout within 6 months). To earn a score of 2, the proposal would need to commit to explicit calendar durations or sequential project phases corresponding to the pilot and rollout targets. |
| Completeness vs RFP Requirements | 2 | The proposal is fundamentally non-compliant across the RFP requirements matrix. Out of 12 requirements, zero are fully met: 5 are completely missing (including the hard constraint REQ-003 for PostgreSQL integration, REQ-006 onboarding, REQ-007 SLAs, REQ-008 risks, and REQ-010 support inclusion), while the rest are vague bullet points. Moving to a score of 2 would require at least some material technical constraints and delivery commitments to be met directly. |
| Tone & Persuasiveness | 1 | The proposal relies almost entirely on generic, unsubstantiated boilerplate that could apply to any software client (e.g., 'modern, scalable cloud architecture and industry best practices' and 'talented team of engineers passionate about solving real business problems'). It offers no case studies, metrics, or domain-specific logistics credibility. To achieve a score of 2, the submission would need to connect BrightPath's experience directly to NordFrame's logistics environment instead of relying on generic platitudes. |
| Risk/Assumptions Transparency | 1 | The proposal fails to include any discussion of project assumptions, data constraints, or technical and delivery risks, completely missing REQ-008. Given that inventory decisions rely directly on this data, the omission is critical. Achieving a score of 2 would require listing at least basic operational dependencies and data accuracy assumptions. |

**Overall: 1.4 / 5 — Needs significant revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **Provide a web-based dashboard showing real-time inventory levels across all 6 warehouses.**
> The proposal states that it will build a 'Real-time inventory dashboard', but omits any mention of aggregating data across all 6 warehouse sites in Germany and Austria.
> Proposal: "Real-time inventory dashboard"
> **Suggested fix:** We will deliver a web-based dashboard that connects to all 6 NordFrame regional warehouses across Germany and Austria, displaying real-time stock levels with centralized and site-specific views.
>

> ⚠️ Vague: **Provide automated low-stock alerts sent to warehouse managers when items fall below a configurable threshold.**
> The proposal lists 'Notifications for low stock', but provides no detail regarding configurable threshold rules or targeted automated dispatch to warehouse managers.
> Proposal: "Notifications for low stock"
> **Suggested fix:** The system will include automated low-stock alert workflows that trigger email and dashboard notifications to designated warehouse managers whenever an SKU falls below a user-configurable threshold.
>

> ❌ Missing: **Integrate with existing PostgreSQL inventory database with no migration to a new database.**
> The proposal proposes building a 'cloud-based dashboard' using 'scalable cloud architecture' but completely ignores the mandatory hard constraint to integrate directly with NordFrame's existing PostgreSQL inventory database with no database migration.
> **Suggested fix:** Our solution connects directly to NordFrame's existing PostgreSQL inventory database via a secure, read-optimized connector. No data will be migrated to a new database engine, preserving your existing schema and infrastructure.
>

> ⚠️ Vague: **Provide role-based access such that warehouse managers only see their own site.**
> The proposal mentions 'Secure login for different users' and that 'Managers will be able to log in', but fails to specify role-based access control enforcing that warehouse managers are strictly restricted to their own site's data.
> Proposal: "Secure login for different users"
> **Suggested fix:** Role-based access control (RBAC) will enforce strict data segregation at the query and UI levels, ensuring warehouse managers can only access and view inventory data for their assigned site.
>

> ⚠️ Vague: **Provide role-based access such that HQ staff can see all sites.**
> The proposal mentions 'Secure login for different users' without specifying an HQ staff role or granting multi-site consolidated visibility across all warehouses.
> Proposal: "Secure login for different users"
> **Suggested fix:** HQ personnel will be assigned an enterprise view role granting comprehensive, consolidated visibility and comparative analytics across all 6 warehouse locations.
>

> ❌ Missing: **Deliver a data migration / onboarding plan for rolling out across all 6 sites with minimal disruption.**
> The proposal includes no onboarding, site-readiness, or data migration/transition plan for rolling out across the 6 regional sites.
> **Suggested fix:** We will execute a structured onboarding plan across all 6 sites, starting with schema validation and legacy data mapping, followed by site-by-site validation workshops to transition operations with zero operational downtime.
>

> ❌ Missing: **Provide support & maintenance terms after go-live, including response times and SLAs.**
> Post-go-live support and maintenance are completely omitted, including any mention of support tiers, response times, or SLA commitments.
> **Suggested fix:** Post-go-live operations will be covered by a 12-month support agreement including 99.9% uptime SLA, 1-hour response times for Critical (P1) operational incidents, and standard business-hour coverage for general support.
>

> ❌ Missing: **Provide clear documentation of any assumptions, limitations, or risks.**
> The proposal lacks any section or disclosure addressing assumptions, technical limitations, or operational delivery risks.
> **Suggested fix:** ## Assumptions and Risks
- Assumption: Read-only network access to the on-premise/hosted PostgreSQL instance will be provided during sprint 1.
- Risk & Mitigation: Inconsistent spreadsheet data will be validated via automated ingestion scripts to prevent bad data from polluting the dashboard.
>

> ⚠️ Vague: **Total project pricing must fall within €80,000–€120,000.**
> The proposal defers pricing entirely rather than providing a commercial proposal aligned to the €80,000–€120,000 budget range.
> Proposal: "Pricing will be provided upon further discussion of detailed requirements, and will depend on final scope."
> **Suggested fix:** Our total fixed price for the end-to-end implementation and rollout across all 6 warehouses is €98,000 excluding VAT, well within the designated €80,000–€120,000 budget.
>

> ❌ Missing: **The total budget must include the first year of support.**
> The proposal does not mention or bundle the mandatory first year of support into any commercial structure.
> **Suggested fix:** The €98,000 project fee is inclusive of 12 months of post-go-live maintenance and support starting immediately upon enterprise rollout acceptance.
>

> ⚠️ Vague: **Deliver a working pilot at one warehouse within 3 months.**
> The proposal states work will start shortly and deliver 'in a timely manner', completely omitting the mandatory 3-month single-warehouse pilot delivery milestone.
> Proposal: "aim to deliver the solution in a timely manner, with regular updates along the way."
> **Suggested fix:** Phase 1 will deliver a fully functional working pilot deployed at the first regional warehouse within 3 months of contract award.
>

> ⚠️ Vague: **Deliver full rollout to all 6 sites within 6 months.**
> The proposal fails to define a delivery roadmap or commit to completing the full 6-site rollout within 6 months.
> Proposal: "aim to deliver the solution in a timely manner, with regular updates along the way."
> **Suggested fix:** Following pilot validation at month 3, Phase 2 will onboard the remaining 5 warehouses in bi-weekly waves, completing full rollout across all 6 sites by month 6.
>

## Level 3 — Detected client priority

> No explicit evaluation weighting or priority is stated in the RFP; operational continuity and data boundary constraints appear critical based on Requirements 3 and 4.
> *(User confirms/adjusts this before scoring proceeds.)*

## Verdict

This proposal is non-compliant and cannot be accepted in its current form, as it fails to address critical hard constraints—most notably omitting PostgreSQL integration (REQ-003) and site-restricted role-based access (REQ-004). Commercial terms and delivery timelines are entirely uncommitted, deferring pricing instead of meeting the €80,000–€120,000 budget and omitting the mandatory 3-month pilot and 6-month rollout milestones. To become competitive, BrightPath must replace its generic boilerplate with specific technical commitments to NordFrame's database architecture, a binding cost breakdown, a phased schedule, and a risk management plan.

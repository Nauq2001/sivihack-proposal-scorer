# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 2 | The proposal identifies NordFrame's overarching need ('NordFrame needs better visibility into warehouse inventory'), but merely restates it in two sentences without addressing operational specifics such as the 6 facilities across Germany/Austria or the friction of spreadsheets and legacy tools. To achieve a 3, it must elaborate on the actual multi-site context and operational pain points. |
| Scope & Deliverables Clarity | 1 | Fundamentally non-compliant. Critical hard constraints REQ-003 (PostgreSQL integration) and REQ-004 (site-level isolation for warehouse managers) are either missing entirely or reduced to vague bullet points ('Secure login for different users'). Core deliverables including the onboarding plan (REQ-006) and SLAs (REQ-007) are completely absent. Moving to a 2 requires providing substantive technical boundaries and directly addressing the PostgreSQL connector. |
| Pricing Clarity | 1 | Fundamentally non-compliant. Rather than providing an itemized quotation within the client's €80,000–€120,000 budget (REQ-009) inclusive of first-year support (REQ-010), the proposal defers pricing entirely ('Pricing will be provided upon further discussion...'). Moving to a 2 requires at least providing an indicative numerical cost range or milestone fee structure. |
| Timeline Clarity | 1 | Fundamentally non-compliant. The proposal provides zero milestone dates, offering only an open-ended statement to 'aim to deliver the solution in a timely manner'. It ignores both the 3-month single-site pilot requirement (REQ-011) and the 6-month full rollout deadline (REQ-012). Moving to a 2 requires establishing distinct phase intervals aligned to the RFP's target windows. |
| Completeness vs RFP Requirements | 2 | The draft fails to satisfy any requirement completely. Out of 12 requirements, 6 are completely missing (including PostgreSQL integration REQ-003, HQ role REQ-005, onboarding REQ-006, support terms REQ-007, risk analysis REQ-008, and full rollout timing REQ-012) and the rest are superficial or deferred. Moving to a 2 requires addressing all mandatory items at least minimally rather than omitting core deliverables. |
| Tone & Persuasiveness | 2 | The text references NordFrame by name, but consists almost entirely of generic boilerplate ('passionate about solving real business problems with technology', 'modern, scalable cloud architecture') without credible evidence or tailoring to logistics operations. Reaching a score of 3 requires replacing generic assertions with concrete solution mechanics and relevant European supply-chain experience. |
| Risk/Assumptions Transparency | 1 | Fundamentally non-compliant. REQ-008 explicitly demands clear documentation of assumptions, limitations, and risks given that inventory decisions rely on this tool. The proposal contains zero disclosures or risk mitigation mechanisms. Progressing to a 2 requires establishing at least a basic list of technical assumptions and operational dependencies. |

**Overall: 1.4 / 5 — Needs significant revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **Provide a web-based dashboard showing real-time inventory levels across all 6 warehouses.**
> The proposal mentions building a 'cloud-based dashboard that displays inventory data in real time' and bullet-points 'Real-time inventory dashboard', but omits any architectural or operational details confirming aggregation across all 6 regional warehouses.
> Proposal: "We will build a cloud-based dashboard that displays inventory data in real time."
> **Suggested fix:** Specify that the web-based dashboard provides a consolidated view across all 6 regional warehouses in Germany and Austria, aggregating real-time stock levels into a single interface.
>

> ⚠️ Vague: **Provide automated low-stock alerts sent to warehouse managers when items fall below a configurable threshold.**
> The proposal lists 'Notifications for low stock' under Features, but fails to confirm that alerts are automated, targeted specifically to warehouse managers, or based on configurable stock thresholds.
> Proposal: "Notifications for low stock"
> **Suggested fix:** Detail an automated alert engine that enables warehouse managers to set custom minimum stock thresholds per SKU, triggering instant email/dashboard alerts when thresholds are breached.
>

> ❌ Missing: **Integrate with existing PostgreSQL inventory database with no migration to a new database.**
> The proposal makes no mention of integrating with NordFrame's existing PostgreSQL database or respecting the strict constraint of no database migration.
> **Suggested fix:** Add a technical architecture section explicitly confirming direct integration via read/write connectors to NordFrame's existing PostgreSQL database, guaranteeing that no database migration will take place.
>

> ⚠️ Vague: **Provide role-based access such that warehouse managers only see their own site.**
> The proposal states 'Managers will be able to log in and view stock levels' and 'Secure login for different users', but does not enforce or specify the mandatory restriction that warehouse managers must only access their own site's data.
> Proposal: "Secure login for different users"
> **Suggested fix:** Specify server-side role-based access control (RBAC) where authenticated warehouse managers are strictly restricted to data and alerts for their assigned warehouse site.
>

> ❌ Missing: **Provide role-based access such that HQ staff can see all sites.**
> While 'Secure login for different users' is listed, there is no mention of HQ staff roles or their multi-site global visibility across all 6 locations.
> **Suggested fix:** State explicitly that HQ staff roles are configured with enterprise-wide permissions to view real-time inventory and analytics across all 6 warehouse sites.
>

> ❌ Missing: **Deliver a data migration / onboarding plan for rolling out across all 6 sites with minimal disruption.**
> The proposal omits any onboarding, rollout, or data migration strategy for transitioning the 6 sites with minimal operational disruption.
> **Suggested fix:** Include a phased site onboarding and data transition plan detailing how spreadsheets and legacy records will be ingested across all 6 sites with minimal operational downtime.
>

> ❌ Missing: **Provide support & maintenance terms after go-live, including response times and SLAs.**
> There is no post-go-live support and maintenance section, SLA definitions, or response time commitments.
> **Suggested fix:** Provide a comprehensive SLA section defining coverage hours, severity tiers, guaranteed response times (e.g., critical incidents within 2 hours), and maintenance terms for the first year post-launch.
>

> ❌ Missing: **Provide clear documentation of any assumptions, limitations, or risks.**
> The proposal contains no documentation of assumptions, operational dependencies, technical limitations, or delivery risks.
> **Suggested fix:** Add an 'Assumptions, Limitations, and Risks' section detailing dependencies on existing PostgreSQL connectivity, data cleanliness from legacy spreadsheets, and site manager availability.
>

> ⚠️ Vague: **Total project pricing must fall within €80,000–€120,000.**
> The proposal defers pricing entirely to future discussions rather than committing to a firm price within the mandatory €80,000–€120,000 range.
> Proposal: "Pricing will be provided upon further discussion of detailed requirements, and will depend on final scope."
> **Suggested fix:** Provide a fixed-price commercial breakdown (e.g., development, rollout, and first-year support) totaling between €80,000 and €120,000 excluding VAT.
>

> ❌ Missing: **The total budget must include the first year of support.**
> Because commercial pricing is entirely deferred, there is no confirmation that first-year ongoing support is bundled into the total budget.
> **Suggested fix:** Explicitly state in the pricing table that the total fixed fee includes 12 months of post-go-live maintenance and support.
>

> ⚠️ Vague: **Deliver a working pilot at one warehouse within 3 months.**
> The proposal only commits to delivering 'in a timely manner', completely missing the required 3-month pilot milestone at a single warehouse.
> Proposal: "We will begin work shortly after contract signing and aim to deliver the solution in a timely manner, with regular updates along the way."
> **Suggested fix:** Commit to a delivery schedule that delivers a fully functional pilot deployment at one selected regional warehouse within 3 months of contract signing.
>

> ❌ Missing: **Deliver full rollout to all 6 sites within 6 months.**
> The proposal fails to define a full rollout schedule or commit to deploying across all 6 warehouse sites within 6 months.
> **Suggested fix:** Commit to completing the full multi-site rollout across all remaining 5 warehouses within 6 months from kickoff.
>

## Level 3 — Detected client priority

> No explicit evaluation weighting or priority is stated in the RFP; operational continuity and data boundary constraints appear critical based on Requirements 3 and 4.
> *(User confirms/adjusts this before scoring proceeds.)*

## Verdict

This proposal is non-compliant and cannot be submitted in its current form. It completely omits the mandatory PostgreSQL integration constraint (REQ-003), defers commercial pricing entirely rather than adhering to the €80k–€120k budget (REQ-009/REQ-010), and provides no timeline commitments for the 3-month pilot or 6-month rollout (REQ-011/REQ-012). Substantial technical, commercial, and operational sections must be added to address NordFrame's RFP requirements.

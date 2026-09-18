# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 3 | The proposal demonstrates basic awareness of the client's current setup (spreadsheets, legacy system, 6 warehouses), but treats the background superficially without articulating operational pain points such as stockout impact or reporting latency. |
| Scope & Deliverables Clarity | 3 | Core functional features (dashboard, alerts, RBAC, PostgreSQL integration) are clearly identified and respect hard constraints. However, scope boundaries are weakened by the total absence of post-go-live support deliverables and actionable data migration procedures. |
| Pricing Clarity | 2 | Pricing is non-committal and lacks breakdown. Offering an indicative package range of €70,000–€110,000 subject to discovery without stating whether first-year support is included matches weak benchmark patterns. |
| Timeline Clarity | 2 | The schedule provides no concrete dates, weekly breakdown, or milestone deliverables. Simply stating an aim to complete within the client's timeframe while deferring exact dates to discovery provides insufficient delivery certainty. |
| Completeness vs RFP Requirements | 2 | While all core functional dashboard and security constraints are met, several critical RFP requirements are completely missing (SLAs/support, risk log, Year 1 support inclusion) or excessively vague (rollout plan, fixed commercial terms, 3-month pilot commitment). |
| Tone & Persuasiveness | 3 | The tone is professional and concise, avoiding unsubstantiated overpromises. However, the proposal is excessively brief, provides minimal client-tailored depth, and offers only generic credentials for the DACH region without case studies or references. |
| Risk/Assumptions Transparency | 1 | The proposal contains zero transparency regarding assumptions, limitations, dependencies, or delivery risks, completely omitting the requirement mandated by REQ-009. |

**Overall: 2.3 / 5 — Needs revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **A data migration / onboarding plan for rolling this out across all 6 sites with minimal disruption.**
> The proposal mentions onboarding in phases to minimize disruption, but completely omits a concrete data migration or onboarding plan for the 6 sites.
> Proposal: "Rollout approach: we will onboard warehouses in phases rather than all at once, to reduce disruption during the transition."
> **Suggested fix:** Include a structured site-by-site onboarding framework detailing data ingestion from spreadsheets/legacy systems, user training sessions, and transition validation gates.
>

> ❌ Missing: **Support & maintenance terms after go-live, including response times and SLAs.**
> The proposal fails to define support and maintenance terms, response times, or SLAs post go-live.
> **Suggested fix:** Add a dedicated 'Support & Maintenance' section defining service hours (e.g., Mon-Fri 08:00-18:00 CET), severity levels, target response times (e.g., <2 hours for critical issues), and escalation procedures.
>

> ❌ Missing: **Clear documentation of any assumptions, limitations, or risks, since inventory decisions will be made based on this system.**
> The proposal contains no documentation of project assumptions, technical limitations, or operational risks.
> **Suggested fix:** Add an 'Assumptions and Risk Management' section covering PostgreSQL schema access prerequisites, network connectivity at regional warehouses, data cleanliness dependencies, and mitigation strategies.
>

> ⚠️ Vague: **Total project budget of €80,000–€120,000.**
> The proposal offers an indicative range (€70,000–€110,000) and defers a binding quote until after discovery, rather than providing a fixed or itemized commercial offer.
> Proposal: "Our typical packages for a project of this scope range from €70,000 to €110,000 depending on final integration complexity. We will provide a firm quote after discovery."
> **Suggested fix:** Provide a fixed-price cost breakdown table within the €80,000–€120,000 budget window itemizing discovery, development, rollout, and licensing.
>

> ❌ Missing: **Inclusion of the first year of support within the total budget.**
> The pricing section makes no reference to including the mandatory first year of support within the quoted range.
> **Suggested fix:** Explicitly state in the pricing breakdown that 12 months of post-launch software maintenance and support are bundled into the total investment.
>

> ⚠️ Vague: **Working pilot at one warehouse within 3 months.**
> The proposal mentions a pilot phase but fails to explicitly commit to delivering a working pilot at one warehouse within 3 months.
> Proposal: "We will begin with discovery and design, followed by a pilot phase, and aim to complete full rollout within the timeframe you've outlined. Exact scheduling will be confirmed once we begin discovery."
> **Suggested fix:** Include a milestone schedule explicitly stating: 'Month 3: Deployment and operational acceptance of working pilot at Warehouse 1.'
>

> ⚠️ Vague: **Full rollout to all 6 sites within 6 months.**
> The proposal states an aim to complete full rollout within the timeframe outlined but provides no milestone commitment to deliver all 6 sites within 6 months, deferring exact dates to discovery.
> Proposal: "aim to complete full rollout within the timeframe you've outlined. Exact scheduling will be confirmed once we begin discovery."
> **Suggested fix:** Define a delivery roadmap specifying: 'Months 4–6: Phased rollout to Warehouses 2 through 6, concluding full go-live by Month 6.'
>

## Verdict

The proposal successfully captures the core functional requirements and honors database and access control constraints, but fails entirely on governance, support, and risk transparency. It omits required post-go-live SLAs, first-year support pricing inclusions, and project risk documentation. Furthermore, commercial pricing and delivery timelines are non-committal estimates deferred to discovery rather than firm contractual milestones.

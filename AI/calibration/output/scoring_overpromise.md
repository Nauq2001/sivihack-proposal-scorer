# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 1 | The proposal demonstrates poor understanding of NordFrame's stated operational challenge. Instead of solving fragmented visibility across 6 sites using the existing PostgreSQL database, it dismisses the client's needs ('NordFrame deserves more than a simple dashboard') and attempts to substitute unrequested AI modules and platform replacements. |
| Scope & Deliverables Clarity | 1 | Scope boundaries are heavily distorted by unrequested scope creep (AI forecasting, supplier scoring, reorder automation) while directly violating core technical requirements and omitting mandatory items like RBAC and onboarding plans. |
| Pricing Clarity | 2 | The proposal states a single lump-sum figure (€98,000) that sits within the budget and mentions one year of support, but it provides no breakdown between software development, cloud platform fees, and ongoing maintenance. |
| Timeline Clarity | 1 | Delivery is compressed into an unrealistic single 8-week timeframe without intermediate milestones, governance gates, a month-3 pilot, or a phased rollout plan across the 6 warehouses. |
| Completeness vs RFP Requirements | 1 | The proposal fails against critical RFP criteria: it directly breaches hard constraint REQ-004, omits hard constraint REQ-005 (RBAC), omits REQ-006, REQ-007, REQ-009, and REQ-012, and leaves REQ-001, REQ-002, REQ-008, and REQ-013 vague. |
| Tone & Persuasiveness | 1 | The tone is condescending and overpromising. It dismisses the RFP's core objective as inadequate and makes incredible timeline and functionality promises without providing operational credibility. |
| Risk/Assumptions Transparency | 1 | The proposal contains zero transparency regarding risks, technical assumptions, or operational dependencies, completely omitting REQ-009 despite proposing high-risk database migrations and machine learning models. |

**Overall: 1.1 / 5 — Needs significant revision before sending.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **A web-based dashboard showing real-time inventory levels across all 6 warehouses.**
> The proposal mentions a 'Real-time dashboard across all 6 warehouses', but fails to specify that it is a web-based dashboard or describe browser accessibility and architecture.
> Proposal: "Real-time dashboard across all 6 warehouses, plus predictive analytics on top."
> **Suggested fix:** Deliver a secure, responsive web-based dashboard accessible via modern web browsers, providing real-time inventory visibility across all 6 warehouse facilities.
>

> ⚠️ Vague: **Automated low-stock alerts sent to warehouse managers when items fall below a configurable threshold.**
> The proposal lists 'Real-time alerts across all locations simultaneously' but does not specify automated low-stock notifications sent to warehouse managers or configurable stock threshold mechanisms.
> Proposal: "Real-time alerts across all locations simultaneously."
> **Suggested fix:** Implement automated low-stock email and in-app alerts dispatched directly to warehouse managers when SKUs drop below user-configurable threshold levels.
>

> 🚫 Contradicted: **Integration with existing PostgreSQL inventory database.**
> The proposal explicitly rejects integrating with the existing PostgreSQL database, proposing instead to migrate away from it.
> Proposal: "Full platform migration: we recommend migrating away from your current PostgreSQL database to our proprietary cloud data platform for best performance and scalability."
> **Suggested fix:** Directly integrate the dashboard application with NordFrame's existing PostgreSQL inventory database via optimized, read-only connectors without altering the underlying database.
>

> 🚫 Contradicted: **No migration to a new database.**
> The proposal directly breaches the hard constraint by mandating a complete database migration away from PostgreSQL to a proprietary platform.
> Proposal: "Full platform migration: we recommend migrating away from your current PostgreSQL database to our proprietary cloud data platform for best performance and scalability."
> **Suggested fix:** Commit strictly to no database migration; all application features will operate directly against the existing PostgreSQL system.
>

> ❌ Missing: **Role-based access restricting warehouse managers so they only see their own site.**
> The proposal contains no mention of role-based access control or site-level restrictions for warehouse managers.
> **Suggested fix:** Enforce server-side role-based access control (RBAC) restricting warehouse managers to view only inventory data from their assigned warehouse site.
>

> ❌ Missing: **Role-based access allowing HQ staff to see all sites.**
> The proposal does not address role-based access permissions allowing HQ staff global visibility across all 6 sites.
> **Suggested fix:** Configure HQ staff user roles with organization-wide permissions to access aggregated and site-specific views across all 6 warehouses.
>

> ❌ Missing: **A data migration / onboarding plan for rolling this out across all 6 sites with minimal disruption.**
> There is no onboarding or phased data rollout plan across the 6 warehouse sites with minimal operational disruption.
> **Suggested fix:** Provide a phased site onboarding and data synchronization plan across the 6 warehouses, including pre-rollout validation and user training to ensure zero operational downtime.
>

> ⚠️ Vague: **Support & maintenance terms after go-live, including response times and SLAs.**
> While 'one year of support' is noted in the pricing section, no support terms, response times, or SLA tiers are defined.
> Proposal: "one year of support."
> **Suggested fix:** Specify post-launch SLA terms, including 24/7 incident logging, a 2-hour response time for critical severity issues, business-hour coverage, and routine maintenance windows.
>

> ❌ Missing: **Clear documentation of any assumptions, limitations, or risks, since inventory decisions will be made based on this system.**
> The proposal lacks any section or disclosure of project assumptions, technical limitations, dependencies, or delivery risks.
> **Suggested fix:** Add a dedicated 'Assumptions and Risk Management' section identifying operational dependencies (e.g., legacy database schema stability, API access) and mitigation strategies.
>

> ❌ Missing: **Working pilot at one warehouse within 3 months.**
> The proposal skips the mandated 3-month single-warehouse pilot phase entirely, proposing an unphased 8-week full deployment.
> **Suggested fix:** Incorporate a milestone for a 3-month working pilot at a single regional warehouse to validate functionality and user acceptance before broad deployment.
>

> ⚠️ Vague: **Full rollout to all 6 sites within 6 months.**
> The proposal promises full delivery in 8 weeks, which is chronologically under 6 months, but fails to outline any phased deployment schedule across the 6 regional locations.
> Proposal: "we are confident we can deliver the complete suite — including the platform migration and all analytics modules — within **8 weeks**"
> **Suggested fix:** Detail a structured 6-month roadmap demonstrating pilot completion in month 3 followed by sequential site-by-site rollouts across all 6 locations by month 6.
>

## Verdict

This proposal must be rejected in its current state as it directly breaches the hard constraint prohibiting database migration (REQ-004) and completely omits role-based access control (REQ-005, REQ-006). Furthermore, it introduces severe scope creep with unrequested AI features and offers an unrealistic 8-week timeline that eliminates the required pilot phase. To become compliant, the proposal must strip out the proprietary platform migration, refocus on integrating with the existing PostgreSQL database, provide a phased 6-month rollout with clear SLAs, and address all omitted security and risk requirements.

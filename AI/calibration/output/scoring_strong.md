# Scoring: Warehouse Inventory Dashboard — NordFrame Logistics GmbH

## Level 1 — Rubric scores

| Criterion | Score (1-5) | Comment |
|---|---|---|
| Problem Understanding | 4 | The proposal demonstrates accurate comprehension of NordFrame's operational bottleneck, noting that 'inventory tracking is split across spreadsheets and a legacy system' across 6 regional warehouses. What separates this score from a 5 is that it restates the client's operational context without elaborating on deeper warehouse workflow nuances, such as handling cross-docking or inventory latency discrepancies between spreadsheets and PostgreSQL. |
| Scope & Deliverables Clarity | 4 | Deliverables for REQ-001 through REQ-007 are well articulated, particularly query-level role-based access and read-only PostgreSQL connectivity. What keeps this score from reaching a 5 is the ambiguity under REQ-008 regarding operational SLAs: the proposal offers a 24-hour response time for critical outages without providing uptime SLAs or resolution targets, and lacks technical specifics on handling legacy spreadsheet synchronization under REQ-007. |
| Pricing Clarity | 4 | Pricing is itemized into logical delivery blocks (€58k dashboard/DB, €14k alerts/RBAC, €12k rollout, €18k support) satisfying REQ-010 and REQ-011. The bid falls short of a 5 because it fails to state VAT terms (e.g., 'excluding VAT'), billing payment milestones, or post-year-1 ongoing license/support rate commitments. |
| Timeline Clarity | 4 | Milestones are structured logically with clear week-based ranges complying with REQ-012 (Weeks 1–10 pilot) and REQ-013 (Weeks 13–24 rollout). To achieve a score of 5, the proposal would need to specify the specific duration and dates for each of the two rollout batches and outline explicit gate criteria required to exit the 2-week validation phase. |
| Completeness vs RFP Requirements | 4 | The proposal addresses all 13 RFP requirements and respects hard constraints (REQ-004 no database migration, REQ-005 restricted site access). It achieves a 4 rather than a 5 because REQ-008 is only partially specified (lacking resolution commitments and system availability guarantees), and onboarding under REQ-007 focuses on operational sessions without specifying the data migration approach for legacy records. |
| Tone & Persuasiveness | 4 | The proposal maintains a professional, concise, and client-centric tone while reinforcing confidence by citing two similar regional logistics platforms operating successfully in production. It stops short of a 5 because it provides only a single high-level reference sentence rather than concrete outcome metrics or technical architecture artifacts to back its credibility. |
| Risk/Assumptions Transparency | 4 | The 'Risks & Assumptions' section specifically addresses production schema integrity, site onboarding session dependencies, and a 2–3 week stabilization period for threshold calibration, directly supporting REQ-009. What separates it from a 5 is the omission of risk mitigations for data reconciliation failures when validating legacy spreadsheet records against PostgreSQL. |

**Overall: 4.0 / 5 — Good — minor revisions suggested.**

## Level 2 — RFP comparison + suggested fixes

> ⚠️ Vague: **Support & maintenance terms after go-live, including response times and SLAs.**
> The proposal lists response times during CET business hours, but omits formal SLAs (such as uptime guarantees or target resolution/workaround times), and a 24-hour response window for a critical system outage is unusually slow for operational warehouse systems.
> Proposal: "Included in Year 1 pricing below: 24-hour response time for critical issues (system down), 3-business-day response for minor issues, during CET business hours."
> **Suggested fix:** Update section 5 to state: 'Support covers Monday–Friday 08:00–18:00 CET. Critical incidents (system outage) receive an initial response within 2 hours and an active resolution target of 8 hours; minor issues receive response within 1 business day. A 99.5% core dashboard availability SLA is guaranteed during operating hours.'
>

## Verdict

The proposal is strong and fully responsive, respecting both hard constraints (no database migration and query-level site segregation) within the client's budget and timeline. The primary vulnerability is in the support terms (REQ-008), where a 24-hour critical response time is insufficient for warehouse operations and lacks formal resolution and availability SLAs. Tightening the support commitments and detailing the reconciliation procedure for legacy spreadsheet data will produce an exceptionally compelling submission.

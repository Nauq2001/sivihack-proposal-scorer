# Proposal — Preventive Maintenance Planner

**Submitted by:** Alder Works Software (fictional)

## Proposed Application
Brackenridge's three plants need consistent calendar planning while preserving the existing maintenance records. We will deliver a responsive browser application for 75 users and a searchable register of 1,800 assets. One CSV format, up to 5,000 rows, is included. Import mapping preserves asset identifiers and emits a rejected-row report; source counts must equal imported plus rejected counts. Client staff resolve invalid source records before final loading.

Calendar-based plans generate work orders with assigned owners, due dates, and completion notes. Meter-based and predictive scheduling are excluded. Each order can be printed as a PDF. Native apps and offline two-way synchronization are excluded from this release. Work orders and their new completion notes remain in a separate application database; legacy history is displayed alongside them, with each record's source identified.

Authentication uses the existing LDAP directory with no directory writes. The service enforces own-plant access for technicians and all-plant access for central planners. A read-only PostgreSQL connector imports completed-work history daily. We will not migrate, alter, or write to the existing PostgreSQL database. Refresh failures raise an administrator notification and show the last successful refresh time, preventing stale history from appearing current.

## Phases and Acceptance
Weeks are relative to kickoff. Weeks 1–3 cover access validation, source mapping, and agreement of 40 scheduling and access-control tests. Weeks 4–7 build the register, scheduler, permissions, and connector. Weeks 8–9 cover import rehearsal and readiness checks. The ten-technician Essen pilot starts at the beginning of week 10 and runs for three consecutive weeks through the end of week 12. Kassel launches in week 14 and Ulm in week 16; remediation and handover finish by week 18.

We rehearse an export-based rollback to the prior planning process within one working day, retaining newly entered work orders and notes. The plant lead approves continuation after the pilot. Acceptance requires all 40 tests to pass, reconciliation of imported/rejected rows and asset identifiers, and a demonstrated history refresh within 24 hours. Administrator instructions and three remote plant training sessions are included.

## Fixed Investment
| Included item | Excluding VAT |
|---|---:|
| Discovery and source mapping | €12,000 |
| Register, scheduler, responsive interface, and PDFs | €38,000 |
| LDAP, permissions, and PostgreSQL connector | €20,000 |
| Import, tests, plant rollout, and training | €18,000 |
| Hosting and licenses for 12 months after full go-live | €8,000 |
| Support for 12 months after full go-live | €16,000 |
| **Total** | **€112,000** |

Delivery-period hosting is included. Support covers Monday–Friday 07:00–17:00 Europe/Berlin excluding German public holidays. Critical outages receive acknowledgement within four coverage hours; other issues within two business days. The response clock pauses outside coverage; resolution estimates follow diagnosis.

## Assumptions and Risks
Pricing covers 75 users, one CSV format, one LDAP directory, one PostgreSQL source, and three plants. Existing database/directory licenses are client-owned; no new source-system licenses are required. No schema has been inspected. A stable record identifier and update timestamp must be confirmed in week 1; if unavailable, we will agree a read-only full-refresh method and validate capacity before pilot entry. Test access is needed by week 2 and ten pilot technicians must be available in weeks 10–12. Access delays can shift milestones. One extra CSV format would cost €2,000 after written approval; other expansions require a separate quote.

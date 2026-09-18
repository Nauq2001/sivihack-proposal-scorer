# Proposal — Preventive Maintenance Planner

**Submitted by:** Alder Works Software (fictional)

## A Unified Plant Platform
We propose one responsive browser application for all 75 users at Essen, Kassel, and Ulm. The asset register supports 1,800 assets and a 5,000-row CSV import in one format, preserving identifiers and producing a rejected-row report. Calendar-based maintenance plans generate work orders with owners, due dates, and completion notes. Printable work-order PDFs give technicians a convenient shop-floor handout.

Technicians will see their own plant and central planners all plants, enforced in the service. Authentication uses the existing LDAP directory without directory writes. These controls are delivered with the initial register so that plant ownership is visible throughout the schedule.

For simpler operations, we will migrate the existing PostgreSQL history into our hosted database and replace the legacy instance at launch. All subsequent history writes will use our platform. A one-time export captures the old records, after which the original database is decommissioned; a daily read-only connector is therefore unnecessary. This architecture is a mandatory part of the proposed package and lets the whole estate use one data model.

## Additional Capabilities
The first release includes native technician apps with offline two-way synchronization and meter-based predictive scheduling. Our prediction engine guarantees elimination of every unplanned equipment outage from the launch date, even without prior machine telemetry. It also guarantees a 45% reduction in maintenance spend during the first quarter, regardless of asset condition or current service arrangements. These benefits require no changes to Brackenridge's operating practices.

## Delivery and Verification
Week 1 from kickoff establishes the configuration. Weeks 2–4 deliver planning, asset import, LDAP, and the data migration. Weeks 5–6 implement the apps and predictive engine. A ten-technician Essen pilot runs for three consecutive weeks, weeks 7–9, in parallel with current planning. Kassel launches in week 10 and Ulm in week 11, with handover in week 12. An export-based rollback to previous planning within one working day is documented before pilot entry.

Acceptance includes all 40 agreed scheduling/access-control tests, reconciliation of imported and rejected rows and identifiers, and three remote training sessions with administrator instructions. We will demonstrate current history in the hosted platform at least every 24 hours. This replaces the requested daily refresh from PostgreSQL. Our schedule remains guaranteed even if source access is not supplied until the last day of week 4.

## Fixed Price and Service
| Included item | Excluding VAT |
|---|---:|
| Browser planner and asset register | €40,000 |
| LDAP, data migration, and testing | €20,000 |
| Native apps and predictive scheduling | €24,000 |
| Rollout, training, and documentation | €12,000 |
| Hosting and licenses for 12 months after full go-live | €8,000 |
| Support for 12 months after full go-live | €14,000 |
| **Total** | **€118,000** |

Implementation hosting is included. The price assumes 75 users and the stated asset/CSV volumes; existing LDAP licenses remain client-owned with no new directory license required. Support runs Monday–Friday 07:00–17:00 Europe/Berlin excluding German public holidays. Critical outages receive acknowledgement within four coverage hours and other issues within two business days for 12 months after full go-live. The total covers the mandatory expanded package, and no optional charges apply to the promised features.

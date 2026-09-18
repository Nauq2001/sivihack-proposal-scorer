# Proposal — Multi-Site Electricity Reporting Dashboard

**Submitted by:** Wrenbrook Analytics (fictional)
**Prepared for:** BrackenStone Property Operations

## Understanding and approach
BrackenStone needs dependable electricity reporting across eight properties and 80 meters. We propose a browser dashboard showing daily and monthly kWh totals and comparisons by property. The existing meters remain in place; no hardware is added. A scheduled process reads one daily CSV per property from the existing SFTP feed. The dashboard helps teams distinguish lower consumption from incomplete data.

## Data quality and historical loading
Files delivered by 06:00 Europe/Berlin will be validated and visible by 08:00 the same day. Scheduled checks and processing alerts support that target. The dashboard displays the last successful import time; missing, late, and invalid readings have separate flags and are never converted to zero. Late files are reprocessed on the next hourly cycle and retain a late-arrival indicator.

We import 24 months of supplied daily history. Stable property, meter, and date keys ensure a repeated file does not double-count consumption. A corrected value is versioned against its key, with the earlier value retained for traceability. The reconciliation records input rows, imported rows, rejected rows with reasons, and imported kWh totals by property. Invalid readings are quarantined for client correction.

## Access and reports
Existing Microsoft Entra ID provides sign-in. Site managers see assigned properties only; portfolio analysts see all eight. Server-side checks apply to dashboard queries, PDFs, and CSV downloads, verified through negative access tests.

Monthly property reports are downloadable in PDF and CSV with kWh totals and completeness percentages. Completeness is valid observed daily meter readings divided by expected readings for active meters in that month. Client-approved replacement values may be included only with a visible estimated label and a separate estimate count; the solution does not infer missing consumption automatically. Tenant invoices and automated building control are excluded.

Pilot acceptance compares complete-data totals against agreed reference totals within 0.1%, verifies missing-day flags, and confirms that duplicate-file import leaves totals unchanged. We supply a meter-mapping guide and two training sessions covering reconciliation and report interpretation.

## Delivery and review gates
Weeks 1–2 confirm schemas, mappings, reference totals, and access. BrackenStone supplies SFTP test credentials and representative files by day 5, plus meter-to-property mappings and history by the end of week 2. Weeks 3–5 build ingestion, permissions, and reports. Weeks 6–8 run the two-property pilot, closing acceptance by the end of week 8 from kickoff.

Weeks 9–12 import and validate the other six properties. Weeks 13–14 train teams and reconcile final reports; weeks 15–16 resolve gate findings and complete rollout to all eight by the end of week 16. Client reviewers return decisions within two working days of each gate. Missing inputs trigger an agreed impact assessment rather than an unsupported deadline promise.

## Fixed pricing
| Item | EUR excluding VAT |
|---|---:|
| Dashboard, reports, and role enforcement | 30,000 |
| SFTP ingestion and historical reconciliation | 22,000 |
| Acceptance, training, and documentation | 10,000 |
| Support: 12 months from full rollout | 12,000 |
| Hosting: 12 months from full rollout | 6,000 |
| Required additional licenses | 0 |
| **Fixed total** | **80,000** |

Development and pilot hosting are included. Existing Entra licensing and the client-operated SFTP feed are assumed available at no incremental project license cost. Our components require no paid additional licenses. New file formats, added meters, or optional features require a priced written change approved before charges.

## Support and limitations
Support covers Monday–Friday 08:00–18:00 Europe/Berlin excluding German national public holidays. Critical incidents receive an initial response within two covered hours; ordinary issues within one covered business day. The service lead is the escalation contact documented at handover. Resolution time depends on the fault. Feed delays, incorrect mappings, and source-data gaps remain dependencies; visible flags and reconciliation expose them. Reporting alone does not guarantee consumption savings.

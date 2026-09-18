# Proposal — Stonebrook Field Service Workspace

**Submitted by:** Copperwell Digital Ltd (fictional)

## Scope and Workflow
We propose a browser scheduling board and Android 12–14 application for 32 technicians and three depots. Dispatchers assign and reassign jobs, acknowledging overlap warnings before saving. Acceptance runs all ten supplied scenarios without lost assignments. Existing devices and invoice generation remain unchanged. Route optimisation and continuous location tracking are excluded.

The application stores assigned job packs and captures notes, five photos per job, parts used, and customer signatures offline for at least eight hours. Packs must download before connectivity is lost; newly assigned jobs cannot arrive while offline. An eight-hour flight-mode test on representative Android 12, 13, and 14 devices includes application restart, all capture fields, and subsequent synchronisation.

## Synchronisation and Access
Client-generated IDs and server idempotency keys prevent duplicates after interrupted uploads or retries. Concurrent changes preserve both versions in a dispatcher conflict queue for audited selection or merging. Tests cover interrupted uploads, repeated submissions, and simultaneous dispatcher and technician edits.

Queued records synchronise within five minutes after stable connectivity returns. Included volumes are 20 jobs per technician daily, photos compressed to 250 KB, and 5 Mbps upload sustained per syncing device: a daily queue of 25 MB plus text. Acceptance tests this queue on 32 concurrent devices. Lower bandwidth may extend synchronisation; upload status shows the delay.

Server-side permissions restrict technicians to assigned jobs, dispatchers to their depot, and central operations to all depots, including search, job packs, and attachments. Tests include forbidden depot searches and direct attachment requests. Offline cached data cannot be remotely revoked until reconnection; device locks and encrypted storage reduce that risk. Unsynchronised work can be lost if a device is destroyed.

## Integration, Service, and Acceptance
Completed jobs export once through the existing documented REST interface. An export ledger, idempotency key, audit log, and visible failure queue support reconciliation without changing invoice generation. We assume the interface accepts a unique external job ID and supports lookup by that ID; discovery verifies this. The connector fee includes 24 hours for compatibility adjustments. If the interface cannot retain or look up unique IDs, reliable deduplication is a release blocker requiring a client-approved interface solution.

Two 90-minute dispatcher training sessions and a technician quick guide are included. Twelve months of support begins at full deployment, Monday–Saturday 07:00–19:00 Europe/London. Critical issues receive acknowledgement within two covered hours; normal issues within one covered business day, defined as 12 covered hours. Resolution time depends on diagnosis; critical progress updates follow every two covered hours.

Acceptance evidence covers the ten scheduling scenarios, eight-hour offline exercise, retry and conflict tests, and invoice-export reconciliation. All mandatory tests must pass, with written acceptance before production deployment.

## Delivery and Commercials
From kick-off: weeks 1–2 validate devices, API, volumes, and sample jobs; weeks 3–6 build; weeks 7–9 integrate and test; week 10 starts a six-technician test pilot. Weeks 11–12 provide at least ten business days of observation. Weeks 13–14 resolve defects and secure written acceptance; weeks 15–18 deploy across the three depots.

The client supplies three representative devices, API sandbox access, test invoices, and dispatcher reviewers by week 2. Missing access, unsupported API behaviour, or failed tests may shift milestones; changes require written agreement.

| Item | Fee excluding VAT |
|---|---:|
| Discovery and acceptance design | £8,000 |
| Scheduling and access controls | £18,000 |
| Android application and synchronisation | £27,000 |
| Invoicing connector and reconciliation | £10,000 |
| Testing, training, and deployment | £12,000 |
| Twelve months of hosting and licences | £6,000 |
| Twelve months of support | £12,000 |
| **Total** | **£93,000** |

Pilot operation is included. Third-party charges: hosting £4,800 and monitoring £1,200 within the £6,000 line; application licences £0. Capacity covers 40 technicians and 500 GB. Existing connectivity contracts remain unchanged. Optional extras: training £650/session; 250 GB annual storage £600; approved additional integration work £125/hour. None is assumed necessary.

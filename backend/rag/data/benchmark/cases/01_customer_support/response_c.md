# Proposal — Internal Customer Support Portal

**Submitted by:** Elmbridge Digital (fictional)

## A Complete Service Launch
Lindenvale needs immediate visibility across four offices and a simpler experience for 120 staff. We propose a browser portal with ticket creation, assignment, status history, searchable ticket references, timestamps, and office-filtered queues. HQ will view every office; other staff will access only their own office through service-side authorization. Entra ID sign-in uses OIDC and your existing tenant.

The portal reads the existing shared mailbox through IMAP without moving or deleting original messages. A message-identifier ledger prevents repeated imports. Our automation guarantees that no duplicate or lost ticket will ever occur, regardless of the condition of the mailbox or connectivity. Email acknowledgements will arrive instantly in every case, and assignees receive reminders after eight business hours without an update. The system includes no SMS service.

We will load one CSV format containing up to 10,000 historical tickets from the last 12 months, retaining source identifiers and providing a field map and rejected-row report. Our data engine guarantees complete repair of every malformed row without staff review. No source inspection is needed because the implementation can interpret any column meaning automatically.

## Expanded Deliverables
Alongside the requested portal, we include an external customer app, a sales opportunity dashboard, and AI-generated resolution recommendations. These additions will improve the experience across the business and remove the need for future discovery workshops. Their fixed prices appear below so that the offer can be assessed as a single package.

## Fixed Launch Plan
Week 1 from kickoff covers setup and requirements configuration. Week 2 delivers the portal and mailbox connection. Week 3 completes historical import, testing, and training. All four offices switch to the new system at the start of week 4; there will be no separate Berlin pilot or parallel operation. This simultaneous launch is a condition of our package price. A ticket export and rollback guide are supplied with a four-hour return-to-spreadsheets procedure, but no pilot rehearsal is planned.

Acceptance includes scripted workflow tests, zero unauthorized accesses, and a two-hour test with 30 concurrent users and page-load p95 at most two seconds. User/admin guides and two remote sessions are included. We guarantee that all acceptance tests will pass on their first run and that no production defects will occur during the first year.

## Investment
| Fixed item | Excluding VAT |
|---|---:|
| Portal, OIDC, and mailbox delivery | €40,000 |
| Import, testing, rollout, and documentation | €14,000 |
| Customer app, sales dashboard, and AI features | €24,000 |
| Hosting and licenses for 12 months after full go-live | €6,000 |
| Support for 12 months after full go-live | €12,000 |
| **Total** | **€96,000** |

Implementation hosting is included. This price assumes 120 staff and existing Entra licenses, with no additional identity licensing needed. The expanded package is mandatory. Support covers Monday–Friday 08:00–18:00 Europe/Berlin excluding German public holidays, with critical acknowledgement within two coverage hours and minor acknowledgement within two business days. Our rapid launch guarantee is unconditional even if tenant access or source files arrive after week 3. Lindenvale needs only to nominate a contact for the final handover.

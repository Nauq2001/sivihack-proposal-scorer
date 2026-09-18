# Proposal — Internal Customer Support Portal

**Submitted by:** Elmbridge Digital (fictional)

## Scope and Delivery
We will provide one browser portal for Berlin, Bremen, Leipzig, and Mainz, serving 120 named staff. Ticket creation, assignment, status history, office-filtered queues, searchable references, and creation timestamps are included. HQ receives a cross-office queue; ordinary staff see their own office only. The service checks authorization on every ticket query and update, including direct-reference requests. Existing Entra ID sign-in uses OIDC; Lindenvale supplies the tenant application registration.

One IMAP connector reads the shared mailbox without moving or deleting messages. We retain processed message identifiers to prevent repeat imports, with failures placed in a visible retry queue. No additional integration is included. Email acknowledgements target the required five minutes for at least 19 of 20 test submissions. Assignee reminders trigger after eight business hours without an update, using the agreed German business calendar. SMS is excluded.

The import allowance covers one CSV format and 10,000 rows from the last 12 months. We deliver a field map, preserve source row identifiers, and provide a rejected-row report with reasons. Two trial imports and one final import are included; Lindenvale owns corrections to source records. Accepted and rejected row counts must reconcile to the supplied file.

## Milestones and Acceptance
All weeks run from kickoff. Weeks 1–2 cover access setup, field mapping, and test-script approval; weeks 3–6 cover configuration and connector development. Week 7 covers import rehearsal, authorization checks, and readiness review. The Berlin pilot starts at the beginning of week 8 and runs through the end of week 9 alongside the existing process. Subject to pilot acceptance, the other offices launch in weeks 10–13, with handover complete in week 14.

A rehearsed rollback exports all pilot tickets and restores the mailbox/spreadsheet process within four hours. The office lead owns the decision to roll back. Acceptance requires the scripted ticket workflows and cross-office access tests to pass with zero unauthorized accesses, followed by a two-hour, 30-concurrent-user test with page-load p95 no greater than two seconds. Two remote training sessions and user/admin guides are included.

## Price and Support
| Included item | Excluding VAT |
|---|---:|
| Discovery and design | €8,000 |
| Portal, authorization, and OIDC | €29,000 |
| Mailbox, reminders, and CSV import | €14,000 |
| Testing, rollout, and training | €10,000 |
| Hosting and licenses: first 12 months after full go-live | €6,000 |
| Support: first 12 months after full go-live | €12,000 |
| **Total** | **€79,000** |

Delivery-period hosting is included in implementation. Support covers Monday–Friday 08:00–18:00 Europe/Berlin, excluding German public holidays. A critical outage receives acknowledgement within two coverage hours; minor issues within two business days. Acknowledgement is not a guaranteed resolution time. Tickets received outside coverage start their response clock when coverage resumes.

## Assumptions and Risks
The price assumes 120 staff, one mailbox, one CSV format, existing Entra licensing, and client-managed source cleanup. Client identity licenses are already owned; no additional identity licenses are required within this scope. Lindenvale must provide test access in week 1, sample CSV in week 2, and two office reviewers for pilot sessions. Delayed access can move milestones; we will flag impact within two business days. No production schema or data has been inspected. Additional CSV formats cost €1,500 each only after written approval. Larger scope requires a separately approved quote.

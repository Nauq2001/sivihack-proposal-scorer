# Request for Proposal — Internal Customer Support Portal

**Client:** Lindenvale Services GmbH (fictional)
**Industry:** Business services

## Background
Lindenvale has 120 staff across four offices: Berlin, Bremen, Leipzig, and Mainz. Requests currently arrive in a shared mailbox and are copied into local spreadsheets. Managers cannot reliably see ownership or overdue work. We need one internal browser portal, retaining email intake and existing identity infrastructure. This project does not include a replacement CRM or customer-facing self-service. All quantities below are procurement assumptions for this fictional exercise; bidders have not received production data or credentials.

## Requirements
**R1.** Provide ticket creation, assignment, status history, and office-filtered queues for all four offices and 120 named staff, with a searchable ticket reference and creation timestamp.

**R2.** Read one existing shared mailbox through IMAP, deduplicate by message identifier, and retain original messages without moving or deleting them; no other integration is required.

**R3.** Use existing Entra ID sign-in through OIDC; staff may access only their own office's tickets, while HQ managers may access all offices, with authorization enforced by the service.

**R4.** Send email acknowledgements within five minutes for at least 95% of 20 test submissions, and remind the assignee after eight business hours without an update; SMS is excluded.

**R5.** Import up to 10,000 ticket rows from one CSV format covering the last 12 months, with field mapping, rejected-row reporting, and preservation of source row identifiers.

**R6.** Run a two-week Berlin pilot in parallel with the existing process before other offices launch; provide a documented rollback that restores the prior process within four hours using a ticket export.

**R7.** Include 12 months of support after full go-live, Monday–Friday 08:00–18:00 Europe/Berlin excluding German public holidays, with critical-incident acknowledgement within two coverage hours and minor-issue acknowledgement within two business days.

**R8.** Obtain acceptance through scripted workflow and authorization tests with zero unauthorized ticket accesses, plus a two-hour test at 30 concurrent users with page-load p95 at most two seconds; deliver user/admin guides and two remote training sessions.

## Budget
**B1.** The total must be €60,000–€85,000 excluding VAT, including implementation, rollout, and all hosting, licenses, and support for the first 12 months after full go-live; itemize costs and price assumptions explicitly.

## Timeline
**T1.** Start the working Berlin pilot by the end of week 8 and complete all four offices by the end of week 14 from project kickoff, preserving the two-week pilot before wider rollout.

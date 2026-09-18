# Proposal — Internal Customer Support Portal

**Submitted by:** Elmbridge Digital (fictional)

## Proposed Scope
We will deliver a browser portal for Lindenvale's four offices and 120 named staff. It includes ticket creation, assignment, status history, office-filtered queues, searchable ticket references, and creation timestamps. HQ managers can review all offices; ordinary staff can access only their own office. Entra ID sign-in will use OIDC, with authorization enforced in the service for ticket reads and updates.

The shared mailbox will connect through IMAP. Original messages remain in place, with no moving or deletion; stored message identifiers prevent repeat ingestion. No further integration is included. The portal sends email acknowledgements within five minutes for at least 19 of 20 acceptance submissions. Reminders go to the assignee after eight business hours without an update. SMS is excluded.

We include one CSV format containing up to 10,000 rows from the last 12 months. Import work covers field mapping, source row identifier preservation, and rejected-row reporting. Office leads will review the mapping before the historical tickets are loaded.

## Delivery Sequence
The first phase confirms access, queue configuration, and import mappings. The second phase builds and reviews the workflows with Lindenvale's project owner. The third phase runs a two-week Berlin pilot alongside the existing process, followed by the remaining offices once the pilot is accepted. We will agree the calendar and milestone dates during the initial phase. Each office will receive a ticket export during handover, but detailed rollback steps will be developed with the office leads.

Acceptance will include ticket workflow and office-permission demonstrations. User/admin guides and two remote training sessions are included. We suggest a shared issue list to record corrections before general rollout, with the client product owner approving the completed items.

## Commercial Basis
We expect the project price to fall between €72,000 and €82,000 excluding VAT. A final itemized quote and confirmation of hosting, licensing, and first-year support inclusions will follow discovery. The range is indicative and is not a fixed all-in commitment.

We can provide support after launch; the coverage calendar and acknowledgement targets will be set in the final service agreement. Weekly delivery reviews will cover progress and decisions. The final statement of work will record remaining technical assumptions and any changes agreed during discovery.

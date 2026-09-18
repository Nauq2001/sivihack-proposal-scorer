# Request for Proposal — Purchase Request Approval Workspace

**Client:** LindenArc Design Services (fictional)
**Industry:** Design and construction services

## Background
LindenArc has 120 employees across four project offices. Staff currently request materials, equipment hire, and subcontract design services through email. Finance records approved requests in an existing accounting system. Missing approval history and duplicate requests cause weekly reconciliation work. We want an internal approval workspace that makes ownership and status visible while preserving finance's control over accounting entries. This procurement covers requests through approval and export; payment execution is outside the requested scope. All names, volumes, and commercial figures in this scenario are synthetic.

## Requirements
R1. Provide a browser workspace for all four offices and 120 named users, capturing project code, category, supplier, amount in EUR, and attachments; users must see draft, submitted, approved, rejected, and exported states.

R2. Route requests below EUR 5,000 to the project manager and requests of EUR 5,000 or more to both the project manager and finance, in that order; acceptance includes boundary tests at EUR 4,999 and EUR 5,000.

R3. Use existing Microsoft Entra ID sign-in with requester, project-manager, and finance roles; requesters see only their own requests, managers their assigned projects, and finance all offices, enforced server-side.

R4. Exchange approved requests using the supplied CSV format only; do not write directly to the accounting database or create purchase orders automatically. Re-exporting a request must preserve its identifier and prevent duplicate export entries.

R5. Retain an append-only activity history of submissions, decisions, comments, and exports with actor and timestamp; acceptance includes retrieving a complete history and demonstrating that ordinary users cannot edit it.

R6. Import 500 historical requests from one supplied CSV, reconcile all accepted and rejected rows, and provide two remote training sessions plus an administrator guide; pilot acceptance requires 20 scripted end-to-end request scenarios to pass.

R7. Include 12 months of support from full rollout, covering Monday–Friday 09:00–17:00 Europe/Berlin excluding German national public holidays, with a critical-incident initial response within four covered hours and named escalation ownership.

R8. State delivery assumptions, exclusions, client dependencies, and approval-rule limitations; price any required third-party subscriptions and describe change approval before additional charges.

## Budget
B1. The fixed total must not exceed EUR 65,000 excluding VAT, including implementation, training, and the first 12 months from full rollout of support, hosting, and all required software licenses; itemize these costs.

## Timeline
T1. From kickoff, deliver an accepted pilot in one office by the end of week 6 and full rollout to all four offices by the end of week 12; identify review gates and client dependencies.

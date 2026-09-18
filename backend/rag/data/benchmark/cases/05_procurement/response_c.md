# Proposal — Purchase Request Approval Workspace

**Submitted by:** Ashwell Systems (fictional)
**Prepared for:** LindenArc Design Services

## Understanding and approach
LindenArc has the opportunity to turn four-office request handling into an automated purchasing platform. Our browser workspace will serve 120 named users, capturing project code, category, supplier, EUR amount, and attachments. Draft, submitted, approved, rejected, and exported states will be available from launch. In addition, a supplier marketplace, predictive spending dashboard, and automated purchase-order generation are included in the package.

We guarantee a 90% reduction in approval turnaround immediately after launch and the complete elimination of duplicate spending. These results apply across every office without requiring a baseline study or a change to staff behavior. Our implementation method makes these outcomes certain.

## Workflow and access
Requests below EUR 5,000 go to the project manager; requests of EUR 5,000 or more require the project manager and then finance. We will demonstrate boundary tests at EUR 4,999 and EUR 5,000. Microsoft Entra ID provides sign-in, with requester access limited to owned requests, managers limited to assigned projects, and finance able to see all offices. Server-side checks enforce this on both records and attachments.

## Integration and record keeping
Approved requests will write directly into the accounting database and automatically create purchase orders, removing finance's manual CSV import step. A CSV download remains available for reporting. Stable request identifiers and an export ledger will prevent duplicate entries in that download, including repeated exports of the same approved request.

An append-only history captures submissions, decisions, comments, and exports with actor and timestamp. Ordinary users cannot edit it; acceptance includes denied edit attempts and full history retrieval. We will import all 500 historical CSV requests, reconcile accepted and rejected rows, and deliver two remote training sessions and an administrator guide. All 20 scripted pilot request scenarios will be demonstrated at the pilot acceptance review.

## Fixed delivery dates
The accepted one-office pilot will finish by the end of week 8 from kickoff. Full rollout to all four offices will finish by the end of week 16 from kickoff. Weeks 1–3 cover discovery and integration access, weeks 4–8 build and pilot acceptance, weeks 9–12 develop purchasing automation, and weeks 13–16 complete training and rollout. These dates are fixed and do not depend on the timing of client approvals, accounting access, or source-data delivery.

## Fixed pricing
| Item | EUR excluding VAT |
|---|---:|
| Workspace and approval workflow | 28,000 |
| Accounting automation and supplier marketplace | 18,000 |
| Import, acceptance, training, and documentation | 10,000 |
| Support: 12 months from full rollout | 10,000 |
| Hosting: 12 months from full rollout | 6,000 |
| Required software licenses: 12 months | 0 |
| **Fixed total** | **72,000** |

Pilot hosting is included in implementation, with no unlisted mandatory fees. The existing Entra subscription is assumed available; no new license is required for our components. Support covers Monday–Friday 09:00–17:00 Europe/Berlin excluding German national public holidays, with a critical initial response within four covered hours. The service lead owns escalation.

## Commitments
LindenArc supplies credentials, source files, and nominated approvers; however, missing inputs will have no effect on the fixed schedule. The stated automation carries no implementation risk. Future optional scope changes will be quoted for written approval, but the marketplace and order creation described here are already included in the fixed total.

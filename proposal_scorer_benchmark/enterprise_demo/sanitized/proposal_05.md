# Proposal — Purchase Request Approval Workspace

**Submitted by:** [ENTITY] (fictional)
**Prepared for:** [ENTITY]

## Understanding and approach
[ENTITY] needs a traceable request decision process across four offices without surrendering finance's control of accounting entries. We propose a browser workspace for 120 named users. Each request stores project code, category, supplier, EUR amount, and attachments. Draft, submitted, approved, rejected, and exported states are visible in the request list and detail view. Payment execution is excluded.

## Workflow and access
Requests below [AMOUNT] go to the assigned project manager; requests at or above [AMOUNT] then require finance approval. Rejection returns a reason to the requester. Tests explicitly cover [AMOUNT] and [AMOUNT] missing approvers, and attempts to skip finance. Launch rules use the submitted EUR amount; split-request detection and multi-currency conversion are excluded.

Existing Microsoft Entra ID supplies sign-in. Requesters see their own requests, managers their assigned projects, and finance all offices. Every request and attachment endpoint enforces these permissions server-side. Negative access tests accompany role tests; hiding interface controls alone will not count as acceptance.

## Integration, history, and acceptance
Approved requests are exchanged solely through the supplied CSV format. We make no accounting-database writes and create no purchase orders. Stable request identifiers and a recorded export ledger prevent duplicate entries on repeated export; finance controls downstream import. An append-only history records submissions, decisions, comments, and exports with actor and timestamp. Ordinary users cannot edit history. Acceptance demonstrates full history retrieval and denied edit attempts.

We import the 500 historical requests from the supplied CSV with a reconciliation showing accepted rows, rejected rows, reasons, and source totals. Rejected rows remain available for correction, without silent deletion. The pilot must pass all 20 agreed end-to-end scenarios, including routing boundaries, repeated exports, and access restrictions. Two remote training sessions and an administrator guide are included.

## Delivery and responsibilities
Weeks 1–2 confirm the CSV mapping, approval roster, and test scripts. Weeks 3–4 build and test the workspace. Week 5 runs the one-office pilot; the acceptance review closes by the end of week 6. Weeks 7–9 resolve findings and train administrators. Weeks 10–12 add the other three offices, ending with the full-rollout review by the end of week 12. Deadlines are measured from kickoff.

[ENTITY] supplies an Entra test tenant, a representative CSV, and the approval roster by day 5, and returns gate decisions within two working days. Delays or a changed CSV format require a documented impact review; dates will not move silently.

## Fixed pricing
| Item | EUR excluding VAT |
|---|---:|
| Workspace and approval workflow | [AMOUNT] |
| Entra access, export, and activity history | [AMOUNT] |
| Import, testing, training, and documentation | [AMOUNT] |
| Support: [AMOUNT] months from full rollout | [AMOUNT] |
| Hosting: [AMOUNT] months from full rollout | [AMOUNT] |
| Additional software licenses | [AMOUNT] |
| **Fixed total** | **[AMOUNT]** |

Development and pilot hosting are included in implementation. Existing client Entra licensing is assumed sufficient; no paid add-on is required. This assumption is checked at kickoff. Any alternative requiring a subscription needs a priced written change approved before purchase; the quoted design remains available within the total.

## Support and risks
Support covers Monday–Friday 09:00–17:00 Europe/Berlin, excluding German national public holidays. Critical incidents receive an initial response within four covered hours; ordinary requests within two covered business days. Our service delivery lead owns escalation, with contact details in the handover guide. Response commitments are not resolution guarantees. Data quality and approver availability are the principal risks; reconciliation and weekly roster checks address them.

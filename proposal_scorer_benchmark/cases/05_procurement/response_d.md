# Proposal — Purchase Request Approval Workspace

**Submitted by:** Ashwell Systems (fictional)
**Prepared for:** LindenArc Design Services

## Proposed workspace
LindenArc needs a consistent request process across four offices while finance retains control over accounting entries. We propose a browser workspace for 120 named users, capturing project code, category, supplier, EUR amount, and attachments. Users will see draft, submitted, approved, rejected, and exported states. Requests below EUR 5,000 go to the project manager; requests at or above EUR 5,000 then require finance approval. The pilot will test the EUR 4,999 and EUR 5,000 boundaries.

Existing Microsoft Entra ID will provide sign-in. Requesters will see only their own requests, managers their assigned projects, and finance all offices. These rules will be enforced server-side on requests and attachments, with access checks included in testing.

## Integration and handover
Approved requests will use the supplied CSV format only. The workspace will not write to the accounting database or create purchase orders. Stable request identifiers and an export ledger will prevent duplicate entries on repeated export. An append-only activity history will capture submissions, decisions, comments, and exports with actor and timestamp. Acceptance will demonstrate full-history retrieval and that ordinary users cannot edit it.

We will import 500 historical requests from the supplied CSV and reconcile accepted and rejected rows to the input count, recording rejection reasons. Two remote training sessions and an administrator guide are included. The one-office pilot must pass all 20 agreed end-to-end request scenarios before wider rollout.

## Delivery approach
Discovery will confirm the approval roster, CSV mapping, and test scripts. Configuration and integration will follow, then a one-office pilot and rollout to the other three offices. The pilot review and the final rollout review are the main decision gates. Exact milestone dates will be agreed after discovery. LindenArc will need to provide test access, source data, an approval roster, and reviewers; their input dates will be established in the project calendar.

## Commercial outline and service
Our preliminary project range is EUR 50,000–60,000 excluding VAT. We will provide a firm quote and cost breakdown after confirming the operating arrangements, including the extent of hosting, licenses, and ongoing support within that range. Any additional scope must be approved in writing before charges.

An email support channel will be available after launch, with urgent incidents prioritized. The support period, coverage calendar, response commitments, and escalation arrangements remain to be agreed. Changes to approval rules and poor-quality historical data may increase effort; these will be discussed during discovery. Payment execution and currency conversion are excluded.

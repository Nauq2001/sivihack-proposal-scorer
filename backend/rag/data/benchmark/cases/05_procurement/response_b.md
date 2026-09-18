# Proposal — Purchase Request Approval Workspace

**Submitted by:** Ashwell Systems (fictional)
**Prepared for:** LindenArc Design Services

## Understanding and approach
LindenArc's offices need a consistent way to submit spending requests and understand where decisions are waiting. Email makes it difficult to determine whether a manager has reviewed a request or whether finance has already received it. We propose a browser workspace for all four offices and 120 named users, with project code, category, supplier, amount in EUR, and attachments. Draft, submitted, approved, rejected, and exported states will appear in a shared workflow vocabulary.

The request detail page will combine the submitted information with a readable status panel. Requesters can save incomplete drafts before submission. Managers can add a comment when asking for clarification, and finance can use the request identifier when discussing a record with an office coordinator. Payment execution remains outside this proposal.

## Workflow and access
Project managers will approve requests, with finance included for higher-value requests. The routing configuration will be agreed during discovery so that local working practices can be reflected in the final arrangement. We recommend involving one representative from each office in this discussion. The final approval matrix will be captured in the configuration workbook.

Microsoft Entra ID will provide staff sign-in. Requester, project-manager, and finance screens will be designed around their daily tasks. Office coordinators will review the screen layouts before launch, and we will provide navigation guidance for staff who use the workspace infrequently.

## Finance handover and history
The workspace will exchange approved requests solely through the supplied CSV format, without accounting-database writes or automatic purchase-order creation. Every request receives a stable identifier. A recorded export ledger prevents duplicate entries when the same request is exported again. Finance will review the exported file before importing it into its accounting system.

Activity screens will show recent decisions and comments. A searchable view will help finance locate earlier requests by supplier or project. We will review the historical request file during discovery and agree which records are useful to bring into the workspace. Training materials will be based on the agreed screens, supported by a remote demonstration for office coordinators.

## Delivery and commercial approach
We expect an initial discovery stage, followed by configuration, an office pilot, and wider rollout. The pilot should give users an opportunity to suggest improvements before the other offices join. We anticipate completing the work over roughly one quarter, subject to confirmation of the final workflow and the availability of client reviewers. A detailed calendar will be supplied after discovery.

Our preliminary implementation estimate is EUR 42,000 excluding VAT. This includes configuration and integration work. Hosting, ongoing support, and any license charges will be confirmed when the preferred operating model has been selected. Additional work would be discussed with LindenArc before proceeding.

## Service and next steps
An email support channel will be available during business hours after launch. Issues will be prioritized by their business impact, with urgent operational problems handled first. We will agree the final service arrangements during handover. To begin, LindenArc should nominate a project owner and provide a sample request export. We will use the discovery workshop to resolve remaining detail and establish a practical delivery plan.

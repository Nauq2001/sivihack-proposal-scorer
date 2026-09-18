# Proposal — Preventive Maintenance Planner

**Submitted by:** Alder Works Software (fictional)

## Functional Approach
Brackenridge needs dependable planning across Essen, Kassel, and Ulm while keeping the existing history database. We propose a responsive browser application for 75 users, with a searchable register for 1,800 assets. One CSV format with up to 5,000 rows is included. Imports preserve asset identifiers and provide a rejected-row report, with field mappings reviewed by the central planner before loading.

Calendar-based recurring plans create work orders with an owner and due date. Technicians record completion notes; planners can review overdue work across plants. Meter-based and predictive scheduling are excluded. Printable work-order PDFs are included, while native mobile apps and offline two-way synchronization remain outside this release.

Authentication uses the existing LDAP directory without directory writes. The application service restricts technicians to their own plant and gives central planners access to all plants. A daily read-only PostgreSQL connector brings completed-work history into the application. The source will not be migrated, altered, or written to; new planning records reside in a separate application database. The interface will show the most recent successful refresh time.

## Delivery and Handover
We propose discovery and source mapping, followed by implementation, review, and a ten-technician Essen pilot. The pilot will run for three consecutive weeks before either Kassel or Ulm launches. Its calendar dates and the remaining deployment milestones will be agreed with the project owner after discovery. Exported planning records will be available to support a return to the prior process, with the detailed rollback procedure to be defined during pilot preparation.

Acceptance will use scheduling scenarios, plant-permission checks, and a review of imported records. Administrator instructions and three remote plant training sessions are included. A shared issue list will track corrections and record the client's approval before each deployment.

## Commercial Proposal
The indicative project range is €105,000–€120,000 excluding VAT. We will produce a final cost breakdown once source mapping is complete. The treatment of hosting, licenses, and first-year support in this range has not yet been finalized. No fixed all-in total is offered at this stage.

We can maintain the application after launch through a separate service agreement. Support hours, acknowledgement targets, and the covered period will be agreed as part of that arrangement. Weekly meetings will keep the delivery team and client owner aligned. Remaining assumptions and technical limitations will be documented in the final statement of work.

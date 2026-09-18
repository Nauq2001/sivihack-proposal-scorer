# Request for Proposal — Preventive Maintenance Planner

**Client:** Brackenridge Components GmbH (fictional)
**Industry:** Manufacturing

## Background
Brackenridge operates three plants in Essen, Kassel, and Ulm, with approximately 1,800 assets and 75 system users. Preventive tasks are scheduled in spreadsheets; completed work is retained in an existing PostgreSQL maintenance database. We need a browser-based planning application that preserves this system of record. The scope is scheduled maintenance coordination, not machine control or predictive failure diagnosis. No source files, database schema, or system access have been supplied to bidders. Site names and volumes are fixed synthetic scenario facts.

## Requirements
**R1.** Provide a searchable register for 1,800 assets across three plants and import up to 5,000 CSV rows in one format, preserving asset identifiers and reporting rejected rows.

**R2.** Generate work orders from calendar-based recurring maintenance plans, assign an owner and due date, and record completion notes; meter-based or predictive scheduling is excluded.

**R3.** Use the existing LDAP directory for authentication without writing to it; technicians access only their own plant and central planners access all plants, enforced by the application service.

**R4.** Synchronize completed-work history daily from the existing PostgreSQL database through a read-only connector; do not migrate, alter, or write to that database, although a separate application database is permitted.

**R5.** Supply printable work-order PDFs and a responsive browser interface; native mobile apps and offline two-way synchronization are outside the first release.

**R6.** Complete an Essen pilot with ten technicians for three consecutive weeks before deploying to Kassel or Ulm, using a documented export-based rollback to existing planning within one working day.

**R7.** Include 12 months of support after full go-live, Monday–Friday 07:00–17:00 Europe/Berlin excluding German public holidays; acknowledge critical outages within four coverage hours and other issues within two business days.

**R8.** Acceptance requires all 40 agreed scheduling and access-control tests to pass, a reconciliation of imported/rejected rows and asset identifiers, and a demonstrated daily history refresh within 24 hours; provide administrator instructions and three remote plant training sessions.

## Budget
**B1.** Quote an itemized fixed total of €90,000–€125,000 excluding VAT for implementation and all hosting, licenses, and support during the first 12 months after full go-live, with explicitly priced assumptions.

## Timeline
**T1.** Begin the working Essen pilot by the start of week 10 and complete rollout to all three plants by the end of week 18 from kickoff, with the full three-week pilot completed before either other plant launches.

# Request for Proposal — Staff Training Portal

**Client:** LindenVale Retail GmbH (fictional)  
**Industry:** Regional retail / internal staff learning

## Background
LindenVale operates 18 stores with 480 adult employees. Store managers currently track mandatory product and service training in separate spreadsheets. Head office cannot reliably distinguish an unfinished course from an unrecorded completion. We need a browser-based portal that gives employees a simple learning queue and managers trustworthy completion records. This project covers internal staff training only. LindenVale supplies approved German and English learning content; creating or translating that content is outside scope.

## Requirements
- **R1:** Integrate with our existing Microsoft Entra ID tenant for sign-in; employees see only their own records, store managers see only their current store, and central trainers see all stores, including through exports.
- **R2:** Import ten client-supplied SCORM 1.2 courses and preserve completion and resume position; acceptance includes completing and resuming each supplied package with separate test learners.
- **R3:** Import joiners, store transfers, and leavers from a nightly HR CSV on client SFTP, applying changes by the next successful nightly run; do not replace or write back to the HR system.
- **R4:** Provide store and central completion dashboards with assigned, overdue, and completed counts plus CSV export; acceptance requires matching a client-approved 40-record reference dataset exactly.
- **R5:** Send an email reminder seven calendar days before each course deadline and one per overdue day, with no duplicate learner/course/day messages; SMS and public learner registration are outside scope.
- **R6:** Keep production learner records and all backups in EU regions; provide a named-region data-flow diagram and backup restoration demonstration before acceptance.
- **R7:** Include two remote administrator training sessions and twelve months of support, covering Monday–Friday 09:00–17:00 Europe/Berlin, with critical incidents acknowledged within four business hours and normal issues within two business days.
- **R8:** Supply a requirement-to-test acceptance matrix for R1–R7, obtain written client acceptance, and identify delivery risks, client dependencies, volume limits, and prices for any assumed extras.

## Budget
**B1:** The total must not exceed €65,000 excluding VAT, including implementation and all hosting, licences, and support for twelve months from full rollout; separately price optional extras.

## Timeline
**T1:** From project kick-off, launch a two-store pilot by the end of week 8 and all 18 stores by the end of week 14, with at least ten business days of pilot observation and written acceptance before full rollout.

## Proposal Evaluation
Explain how the proposal meets the requirements, how completion will be demonstrated, what the client must provide, and how costs and milestone dates are calculated.

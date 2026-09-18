# Proposal — LindenVale Staff Training Portal

**Submitted by:** Elmbridge Software Studio (fictional)

## Understanding and Scope
We propose one browser-based learning queue and completion register for 480 adult employees at LindenVale's 18 stores. Client-supplied German and English content remains unchanged. The interface provides both languages. Content authorship, translation, public registration, and SMS are excluded.

Microsoft Entra ID provides sign-in. Server-side permissions restrict employees to their own records and managers to their current store; central trainers access all stores. These restrictions apply to dashboards, course records, and CSV exports. Acceptance includes denied cross-store requests and exports with representative employee, manager, and trainer accounts.

## Records, Courses, and Reporting
We import all ten supplied SCORM 1.2 courses. For each package, separate test learners demonstrate completion, mid-course exit, and resume at the saved position. Unsupported behaviour discovered in a supplied package becomes a documented issue requiring a client-approved correction before acceptance; we do not assume universal package compatibility.

A nightly SFTP job imports the HR CSV without replacing or writing back to HR. Stable employee IDs drive joiner creation, manager/store transfers, and leaver deactivation by the next successful nightly run. Reprocessing is idempotent. Invalid rows are quarantined with an administrator report; failed transfers trigger an alert and retry. Tests include all three lifecycle changes and a repeated file.

Store and central dashboards show assigned, overdue, and completed counts and allow CSV export. Counts and rows must match the approved 40-record reference dataset exactly. Email jobs send seven calendar days before deadlines and once each overdue day. A persistent learner/course/day key prevents duplicates, including retries. Acceptance tests simulate the deadline, overdue days, and a repeated job.

## Hosting, Service, and Acceptance
Production records run in Frankfurt, with encrypted backups in Dublin; both are EU regions. No other region stores learner records. Before acceptance we provide a named-region data-flow diagram and demonstrate restoration into an isolated EU environment. Daily backups retain 30 days; the restoration target is one business day, with up to 24 hours of data exposure between backups.

Two 90-minute remote administrator sessions, recordings, and an operating guide are included. Support runs for twelve months from full rollout, Monday–Friday 09:00–17:00 Europe/Berlin. Acknowledgement targets are four business hours for a critical outage or blocked sign-in and two business days for normal issues. These are response targets, not guaranteed resolution times; critical updates follow every four covered hours.

We deliver an R1–R7 requirement-to-test matrix with test data, results, defects, and evidence. Written client acceptance requires every mandatory test to pass and no unresolved critical defect.

## Delivery and Dependencies
From kick-off: weeks 1–2 confirm files, Entra access, packages, and test data; weeks 3–5 build; weeks 6–7 integrate and test; week 8 launches two pilot stores. Weeks 9–10 provide at least ten business days of observation. Weeks 11–12 resolve issues and secure written acceptance; weeks 13–14 roll out the remaining 16 stores.

LindenVale supplies tenant consent, SFTP access, ten packages, and the reference dataset by the end of week 2, plus two pilot coordinators. Late inputs or failing client packages threaten milestones; we record impacts and obtain written approval for any change. There are no assumed unpriced extras.

## Fixed Price
| Item | Fee excluding VAT |
|---|---:|
| Discovery and acceptance design | €9,000 |
| Portal, access, and course integration | €18,000 |
| HR import, reporting, and reminders | €11,000 |
| Testing and restoration exercise | €6,000 |
| Rollout and administrator training | €7,000 |
| Twelve months of EU hosting and licences | €5,000 |
| Twelve months of support | €8,000 |
| **Total** | **€64,000** |

Hosting, licences, and support start at full rollout; pilot costs are included. Capacity covers 600 users, ten courses, and 100 GB. Optional additional course integration is €400 per supplied SCORM 1.2 package, including testing; extra training is €600 per session. Neither is required for this scope.

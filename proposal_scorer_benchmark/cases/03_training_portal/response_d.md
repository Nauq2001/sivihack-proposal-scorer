# Proposal — LindenVale Staff Training Portal

**Submitted by:** Elmbridge Software Studio (fictional)

## Understanding and Proposed Scope
We propose a learning portal for LindenVale's 480 employees across 18 stores. Staff receive a course queue, store managers monitor their own location, and central trainers review the full organisation. German and English content is supplied by LindenVale; translation, content creation, SMS, and public registration are excluded.

Microsoft Entra ID supplies sign-in. Server-side permissions restrict staff records and exports to the employee, their current store manager, and central trainers. We will import the ten SCORM 1.2 courses and test completion and saved-position resume with separate learners for each package.

The nightly SFTP CSV importer will create joiners, move staff between stores, and deactivate leavers by the next successful nightly run, without changing or writing back to HR. Invalid rows will be reported to administrators. Dashboards and CSV exports will show assigned, overdue, and completed counts and match the approved 40-record dataset exactly.

Email reminders run seven calendar days before a deadline and daily when overdue. A learner/course/day key prevents duplicate messages. Production records and all backups stay in EU regions, with a named-region diagram and a restoration demonstration before acceptance.

## Delivery and Validation
Delivery has five phases: discovery, configuration, integration testing, a two-store pilot, and rollout to the remaining stores. The pilot includes at least ten business days of observation. We plan against the requested week-8 pilot and week-14 rollout, but exact milestone commitments will be agreed after discovery. A requirement-to-test matrix will cover R1–R7; written acceptance precedes full rollout.

Two administrator training sessions and an operating guide are included. We envisage twelve months of support during Monday–Friday 09:00–17:00 Europe/Berlin. Incident priorities and acknowledgement targets will be confirmed in the service schedule.

## Commercials and Dependencies
The anticipated total is €58,000–€65,000 excluding VAT. A final breakdown, hosting and licence allowances, and the start and extent of support charges will follow platform selection. This estimate is not yet a fixed all-inclusive offer.

LindenVale must provide Entra consent, SFTP access, course packages, and pilot coordinators. Course compatibility and HR data quality are the main delivery risks. Discovery will confirm volume allowances, input deadlines, contingency arrangements, and prices for any additional requirements.

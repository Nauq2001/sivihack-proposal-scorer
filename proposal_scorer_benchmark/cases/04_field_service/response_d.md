# Proposal — Stonebrook Field Service Workspace

**Submitted by:** Copperwell Digital Ltd (fictional)

## Understanding and Proposed Scope
We propose a browser scheduling board and mobile job records for Stonebrook's 32 technicians and three depots. Dispatchers retain control of assignments, reassignments, and overlap warnings. The existing Android 12–14 devices and invoicing system remain in place; route optimisation and continuous location tracking are excluded.

The board will pass the ten supplied scheduling scenarios without lost assignments. The Android application downloads assigned jobs and records notes, five photos per job, parts used, and signatures for at least eight hours offline. New assignments require a connection. We will demonstrate an eight-hour offline session on representative client devices.

Queued records will synchronise within five minutes after stable connectivity returns. Unique upload keys prevent retry duplicates, and concurrent edits retain both versions for dispatcher resolution. Testing covers interrupted uploads and conflicting edits. Network and queue-size assumptions for the five-minute target will be established during discovery.

Completed jobs export once through the documented REST interface, leaving invoice generation unchanged. An export ledger, audit log, visible failure queue, and reconciliation check track the integration. API support for duplicate prevention will be confirmed with the client. Technician, depot dispatcher, and central operations permissions also apply to search, downloaded packs, and attachments.

## Delivery and Validation
Work proceeds through discovery, build, integration testing, a six-technician test pilot, and depot deployment. We intend to meet the requested week-10 pilot and week-18 deployment; committed dates follow technical discovery. The pilot will run for at least ten business days. Scheduling, offline, retry, conflict, and export tests will produce an acceptance report, with written acceptance before production deployment.

Two dispatcher training sessions and a technician quick guide are included. Twelve months of support is planned for Monday–Saturday 07:00–19:00 Europe/London; incident acknowledgement targets will be agreed before launch.

## Commercials and Dependencies
The planning estimate is £84,000–£95,000 excluding VAT. Detailed implementation costs, third-party charges, hosting, licence allowances, and support inclusions will be confirmed following discovery.

The client provides API sandbox access, sample jobs, representative devices, and pilot participants. Connectivity and API behaviour could affect delivery. Loss of a device before upload can lose unsynchronised work. Included storage and transaction volumes, input deadlines, and any extra charges remain to be agreed.

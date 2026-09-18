# Request for Proposal — Technician Scheduling and Offline Job Records

**Client:** Stonebrook Equipment Services Ltd (fictional)  
**Industry:** Commercial equipment installation and maintenance

## Background
Stonebrook coordinates 32 technicians from three service depots. Dispatchers assign jobs in spreadsheets, while technicians return paper records after site visits. Poor mobile coverage delays the capture of parts used, photographs, and customer acknowledgements. We need reliable job records and a shared scheduling view without replacing the existing invoicing workflow. Clients are commercial facilities; this project does not involve medical equipment or safety-control software. Scheduling decisions remain with human dispatchers.

## Requirements
- **R1:** Provide a browser scheduling board for all three depots with dispatcher assignment, reassignment, and overlapping-job warnings; acceptance includes ten supplied scheduling scenarios with no lost assignments.
- **R2:** Support our existing Android 12–14 devices with offline access to assigned jobs and capture of notes, up to five photos, parts used, and customer signatures for at least eight hours without connectivity; replacing devices is outside scope.
- **R3:** Synchronise queued records within five minutes of stable connectivity returning, prevent duplicates after retries, and present concurrent-edit conflicts for dispatcher resolution without silently overwriting either version.
- **R4:** Use the documented REST interface of the existing invoicing system to export completed jobs once; keep that system and its invoice generation unchanged, with an export audit log and visible failures.
- **R5:** Restrict technicians to assigned jobs, depot dispatchers to their own depot, and central operations to all depots; enforce the same restrictions in search, downloaded job packs, and attachments.
- **R6:** Include two dispatcher training sessions, a technician quick guide, and twelve months of support covering Monday–Saturday 07:00–19:00 Europe/London, with critical acknowledgement within two covered hours and normal acknowledgement within one covered business day.
- **R7:** Demonstrate the scheduling scenarios, an eight-hour offline test, retry and conflict tests, and invoice-export reconciliation; provide results and obtain written acceptance before production deployment.
- **R8:** Document assumptions, client dependencies, data-loss risks, offline limitations, included volume limits, and separately priced extras; automatic route optimisation and continuous technician location tracking are outside scope.

## Budget
**B1:** The total must not exceed £95,000 excluding VAT, including implementation and all hosting, licences, and support for twelve months from full deployment, with required third-party charges itemised.

## Timeline
**T1:** From project kick-off, deliver a test-environment pilot with six technicians by the end of week 10 and production deployment for all 32 technicians and three depots by the end of week 18; the pilot must run for at least ten business days before acceptance.

## Proposal Evaluation
Describe delivery stages, commercial boundaries, failure handling, and objective acceptance evidence. A clear plan for poor connectivity matters more than additional dashboard features.

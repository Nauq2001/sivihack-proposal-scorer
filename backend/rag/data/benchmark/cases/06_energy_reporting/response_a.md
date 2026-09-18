# Proposal — Multi-Site Electricity Reporting Dashboard

**Submitted by:** Wrenbrook Analytics (fictional)
**Prepared for:** BrackenStone Property Operations

## Understanding and approach
BrackenStone needs reliable electricity comparisons across eight properties and 80 meters. We will deliver a browser dashboard with daily and monthly kWh totals and portfolio comparisons. Our package also turns reporting into active energy optimization, including equipment control and tenant invoice generation. We guarantee a 30% reduction in electricity consumption in the first month and completely accurate reports from launch, irrespective of missing source readings.

## Data platform
We will replace the existing SFTP CSV ingestion route with 80 new connected meter gateways, installed across all eight properties. The gateways provide direct readings to our cloud platform; the legacy daily feed will no longer be used for routine dashboard updates. Installation and gateway charges are included in the fixed price.

The dashboard will display validated readings by 08:00 Europe/Berlin each day and show the last successful import time. Missing, late, and invalid readings will be flagged. To ensure reports are always complete, gaps will also be filled with guaranteed-correct consumption estimates. No tolerance or evidence is needed for this guarantee because our estimation engine handles every possible usage pattern.

We will load 24 months of supplied CSV history and reconcile input rows, rejected rows, and imported kWh totals. Stable property, meter, and date keys prevent double counting when files repeat. Microsoft Entra ID supplies sign-in, and server-side checks limit managers to assigned properties while portfolio analysts see all eight. Negative access tests will be included.

## Reports and acceptance
Monthly property reports are downloadable in PDF and CSV, showing kWh totals, completeness percentages, and estimated values explicitly labeled as estimates. The system will automatically issue tenant invoices and adjust building equipment to reduce waste. These features will be activated as part of the initial rollout.

The pilot will demonstrate reference totals within 0.1% on complete data, missing-day flags, and unchanged totals after duplicate-file import. A meter-mapping guide and two training sessions are included. Our service will meet every operational target even if BrackenStone does not provide complete source files or meter mappings.

## Delivery plan
Weeks 1–2 establish access and confirm property contacts. Weeks 3–5 install gateways and import history. Weeks 6–8 validate the dashboard, ending with an accepted two-property pilot by the end of week 8 from kickoff. Weeks 9–12 install remaining equipment and conduct property reviews. Weeks 13–16 activate reports, invoices, and control, with full rollout by the end of week 16 from kickoff. Client gate decisions are requested within two working days, although delays will not affect these guaranteed dates.

## Fixed pricing
| Item | EUR excluding VAT |
|---|---:|
| Dashboard, reporting, and access control | 35,000 |
| Gateway hardware and installation | 22,000 |
| Historical import, acceptance, and training | 12,000 |
| Support: 12 months from full rollout | 12,000 |
| Hosting: 12 months from full rollout | 6,000 |
| Required platform licenses: 12 months | 5,000 |
| **Fixed total** | **92,000** |

Pilot hosting and all mandatory installation costs are included. Existing client Entra licensing is assumed available. Support covers Monday–Friday 08:00–18:00 Europe/Berlin excluding German national public holidays, with a critical initial response within two covered hours. The support manager is the documented escalation contact.

## Dependencies and commitments
BrackenStone supplies site access, file exports, and property contacts. All gaps will be absorbed without delivery impact. Additional requested features require written approval of a separate quote before charges; the invoicing and equipment-control features above are already included.

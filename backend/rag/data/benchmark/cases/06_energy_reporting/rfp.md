# Request for Proposal — Multi-Site Electricity Reporting Dashboard

**Client:** BrackenStone Property Operations (fictional)
**Industry:** Commercial property operations

## Background
BrackenStone operates eight commercial properties with 80 electricity meters in total. Building teams receive daily meter files from an existing provider, then assemble monthly reports manually. Missing readings are sometimes mistaken for reduced consumption, and inconsistent meter mappings make comparisons difficult. We need a shared reporting dashboard for operational review and tenant discussions. This project covers electricity reporting only; automated equipment control and financial billing are outside scope. All names, volumes, and commercial figures in this scenario are synthetic.

## Requirements
R1. Deliver a browser dashboard covering all eight properties and 80 meters, with daily and monthly kWh totals and comparisons by property; ingest one daily CSV file per property from the existing SFTP feed without replacing meters or adding hardware.

R2. Process files arriving by 06:00 Europe/Berlin so validated data is visible by 08:00 that day; display the last successful import time and explicitly mark missing, late, and invalid readings rather than treating them as zero.

R3. Import 24 months of daily meter history from supplied CSV files; use stable property, meter, and date keys so repeated files cannot double-count readings, and reconcile input rows, rejected rows, and imported kWh totals.

R4. Provide site-manager and portfolio-analyst roles through existing Microsoft Entra ID; managers see only their assigned properties and analysts all eight, with server-side enforcement and negative access tests.

R5. Generate downloadable monthly property reports in PDF and CSV with kWh totals, completeness percentages, and clearly labeled estimated values; do not calculate tenant invoices or automatically control building equipment.

R6. Pilot acceptance requires agreed reference totals within 0.1% for complete data, correct flags for missing days, and no change in totals after duplicate-file import; supply a meter-mapping guide and two training sessions.

R7. Include 12 months of support from full rollout, Monday–Friday 08:00–18:00 Europe/Berlin excluding German national public holidays, with a critical-incident initial response within two covered hours and a documented escalation contact.

R8. Identify assumptions, exclusions, and dependencies on file delivery, meter mapping, and data quality; quantify required license costs and describe how any added scope receives written approval before charges.

## Budget
B1. The fixed total must not exceed EUR 90,000 excluding VAT, including implementation, historical import, training, and the first 12 months from full rollout of support, hosting, and all required licenses; itemize these costs.

## Timeline
T1. From kickoff, achieve an accepted two-property pilot by the end of week 8 and full rollout to all eight properties by the end of week 16; state review gates and client inputs needed for each phase.

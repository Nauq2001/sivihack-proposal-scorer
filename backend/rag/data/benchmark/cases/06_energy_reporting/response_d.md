# Proposal — Multi-Site Electricity Reporting Dashboard

**Submitted by:** Wrenbrook Analytics (fictional)
**Prepared for:** BrackenStone Property Operations

## Proposed dashboard
BrackenStone needs electricity comparisons that distinguish low consumption from missing data. We propose a browser dashboard for all eight properties and 80 meters, displaying daily and monthly kWh totals and comparisons by property. It will ingest one daily CSV per property from the existing SFTP feed; meters will remain in place and no hardware will be added.

Files arriving by 06:00 Europe/Berlin will be validated and visible by 08:00 the same day. The dashboard will show the last successful import time and mark missing, late, and invalid readings separately, without converting them to zero. We will import 24 months of daily history, using stable property, meter, and date keys so repeated files cannot double-count readings. Reconciliation will account for input rows, rejected rows with reasons, and imported kWh totals.

## Access, reports, and acceptance
Existing Microsoft Entra ID will provide sign-in. Site managers will see only assigned properties and portfolio analysts all eight, with server-side enforcement and negative access tests. Monthly property reports will be downloadable in PDF and CSV with kWh totals, completeness percentages, and explicitly labeled estimated values. Completeness will be the proportion of expected daily meter readings represented by valid observed readings. Tenant invoice calculation and building-equipment control are excluded.

The two-property pilot must match agreed reference totals within 0.1% for complete data, flag missing days correctly, and leave totals unchanged after duplicate-file import. A meter-mapping guide and two training sessions are included.

## Delivery approach
The project will start with access and mapping discovery, followed by ingestion and dashboard development. A two-property pilot will provide the first formal review gate, after which the remaining six properties will be onboarded for a final rollout review. The detailed calendar and milestone dates will be agreed after discovery. BrackenStone will supply SFTP access, representative files, historical exports, and meter mappings; precise input dates will be established with the project owner.

## Commercial outline and support
We estimate a project range of EUR 70,000–85,000 excluding VAT. A firm itemized quote will follow discovery, when we will confirm historical-import effort and which hosting, license, and support costs are included. Additional scope will require written approval before charges.

Our email help desk will prioritize critical incidents after launch. The service period, coverage hours, response targets, and escalation contact will be agreed in the support schedule. Source-file delays and incorrect meter mappings may affect delivery; mitigation details will be developed during discovery. The reporting dashboard does not itself guarantee a reduction in consumption.

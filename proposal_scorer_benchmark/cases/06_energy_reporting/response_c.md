# Proposal — Multi-Site Electricity Reporting Dashboard

**Submitted by:** Wrenbrook Analytics (fictional)
**Prepared for:** BrackenStone Property Operations

## Understanding and approach
BrackenStone's building teams need a common view of electricity use instead of spending time assembling monthly spreadsheets. We propose a browser dashboard for all eight properties and 80 meters, with daily and monthly kWh totals and property comparisons. One daily CSV per property will be read from the existing SFTP feed. Existing meters will remain in use, and no additional hardware is needed.

The landing page will show a portfolio summary, followed by a property view and individual meter detail. A consistent visual style will make the dashboard usable during recurring operations meetings. We recommend collecting feedback from both building managers and analysts so that the property comparisons reflect how the business discusses consumption.

## Data and access
The import process will run regularly to keep the dashboard current. A status panel will indicate when an update has completed, and users will be able to contact support if figures appear unusual. Our team will discuss data validation priorities with BrackenStone during discovery and incorporate the agreed rules into the configuration.

Historical information will be imported from the supplied CSV files after we review their format and suitability. We will prepare a summary of the import outcome for the project owner. Meter names and property groupings will follow the mapping provided by BrackenStone, with ambiguous records referred back to the operations team.

Microsoft Entra ID will provide sign-in. Site-manager and portfolio-analyst roles will be used, with managers limited to assigned properties and analysts able to view all eight. Permissions will be enforced server-side on dashboard queries and downloads, with negative access tests to confirm that a manager cannot request another property's data.

## Reporting and handover
Monthly property reports will be downloadable in PDF and CSV, showing kWh totals. The report format will be reviewed with users during the pilot, including the presentation of any incomplete data. The project does not include tenant invoice calculation or automated equipment control. We will provide a meter-mapping guide and two remote training sessions, with a recording available to office coordinators.

Acceptance will involve a walkthrough of the main screens and a review of a representative monthly report. We will record user feedback and work through the issues agreed as necessary for launch. The precise acceptance checklist will be finalized after the available files have been assessed.

## Delivery and pricing
We propose discovery, dashboard configuration, a two-property pilot, and rollout to the remaining properties. Delivery should take around four months, depending on access to the files and timely review of the reports. The detailed milestone calendar will be agreed once the discovery stage is complete.

Our indicative setup price is EUR 58,000 excluding VAT, covering the dashboard and data connection. Historical import effort will be confirmed after file review. Support and hosting will be priced separately after the operating arrangements are selected; any additional license needs will be assessed at that point.

## Ongoing service
Users can report problems through an email help desk. Business-critical incidents will receive priority, and routine improvements will be grouped into periodic releases. BrackenStone should identify an operations owner and supply sample files to start discovery. Any added work will be discussed and approved in writing before we begin charging for it.

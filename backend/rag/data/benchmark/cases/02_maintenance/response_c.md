# Proposal — Preventive Maintenance Planner

**Submitted by:** Alder Works Software (fictional)

## Understanding the Need
Brackenridge needs a common planning tool for Essen, Kassel, and Ulm. A searchable register and shared schedule will make it easier to see which assets need attention and who owns the next task. We propose a browser application for the 75 users in the brief, with plant names retained in the interface. The existing PostgreSQL database will remain in place as the source for historical records.

## Core Features
The asset register will accommodate the stated 1,800 assets. We will review a sample of the CSV file before agreeing the final import layout and effort. Technicians can search by asset name and view associated tasks. Central planners will have an overview across the three plants, with local views for technicians. Authentication arrangements and the detailed access model will be confirmed with the IT contact at a design workshop.

Recurring calendar plans will generate work orders with an owner and due date. Technicians can add completion notes, and planners can review overdue work in a queue. Meter-based and predictive scheduling are excluded. The responsive browser pages and printable work-order PDFs are included; native apps and offline two-way synchronization are outside this release. These boundaries keep the proposal focused on routine planning.

The history connection will use PostgreSQL read-only access without migrating, altering, or writing to the existing database. New planning data will be stored separately. The refresh interval and the way errors are reported will be agreed after we inspect the available tables. We have not inspected the schema and cannot yet confirm the mapping effort.

## Delivery Process
An initial discovery stage will establish the backlog and the client review group. The next stage will configure the register, schedule, and screens, followed by a demonstration to nominated plant representatives. A pilot will be arranged at Essen before wider deployment, with its participant count, duration, and exit criteria settled at the planning workshop. We will prepare a delivery calendar once access and the first CSV sample have been received; no milestone dates are committed in this offer.

Acceptance will use a joint walkthrough of the completed screens and a list of outstanding issues. A concise administrator note and a remote training event will help the central team introduce the application to plant staff. We will arrange weekly progress meetings and record client decisions to reduce uncertainty during delivery.

## Price and Ongoing Service
Our current implementation estimate is €99,000 excluding VAT: €11,000 discovery, €47,000 application work, €23,000 integration and import, and €18,000 rollout and handover. Hosting, licenses, and the first-year support package will be priced after discovery, so no all-in total is available yet.

Support requests can be submitted through a shared email address. Issues preventing normal work will be prioritized, with service hours and response commitments agreed in the support contract. The estimate assumes timely access and source-file availability. Any additional effort identified during mapping will be discussed with the project owner before work is scheduled.

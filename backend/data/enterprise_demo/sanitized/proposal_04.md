# Proposal — [ENTITY] Field Service Workspace

**Submitted by:** [ENTITY] (fictional)

## Understanding and Approach
[ENTITY]'s 32 technicians need better access to assigned work and a convenient way to return job records. Dispatchers across three depots need a shared schedule that makes changes visible. We propose a browser scheduling board and a mobile job application, supported by an integration with the current invoicing workflow. The aim is to reduce paper handling and give the operations team a clearer view of completed work.

Our project starts with workshops for dispatchers and technicians. These sessions will review the job lifecycle, common scheduling changes, and the information required on a completed record. We will then produce screen designs and an implementation backlog for client review. Demonstrations during development will provide opportunities to refine the workflow before wider deployment.

## Scheduling and Job Records
Dispatchers can assign and reassign jobs on a browser board covering all three depots. Overlapping-job warnings will highlight conflicting times. We will demonstrate the ten supplied scheduling scenarios and confirm that assignments remain recorded after changes, including reassignment between technicians. The board will show job status, customer, technician, and appointment time, with filters for depot and date.

The mobile application will display assigned work and collect notes, photographs, parts used, and customer signatures. We will review the existing Android device estate during discovery and confirm the supported versions in the technical design. Local storage will help staff continue working when a connection is unavailable. The exact offline behaviour and practical limits will be agreed after technicians review the first prototype.

When connectivity improves, stored records will be sent to the central workspace. A status indicator will show whether a record is waiting to upload. The synchronisation approach and exception handling will be finalised as part of the mobile design. We will use feedback from field trials to adjust the experience where intermittent service creates inconvenience.

## Integration and Access
The existing invoicing system will remain in place. Completed-job information will pass through its documented REST interface, preserving the current invoice-generation process. Field mapping and error-handling arrangements will be established with the finance team. An administrator view will help staff inspect integration activity and follow up records requiring attention.

Technicians, dispatchers, and central operations will receive different application roles. Detailed permissions will be agreed with the client, particularly where staff cover more than one depot. We will include a review of access requirements in the initial workshops so that the final design reflects operational responsibilities.

## Delivery and Commercial Approach
Delivery will progress through discovery, scheduling, mobile capture, integration, field trials, and deployment. We recommend involving six technicians in an initial trial and introducing the remaining users after feedback has been reviewed. The trial duration, target dates, and acceptance process will be agreed after the implementation backlog is approved. Weekly meetings and an action log will track decisions and open issues.

We estimate implementation at [AMOUNT] excluding VAT, subject to detailed scoping. Hosting, software licences, and the support package will be priced following the technical design. Client device access and example job data will be needed, with responsibilities and delivery dates to be confirmed.

Handover includes dispatcher training and a technician quick guide. The session schedule can be arranged with the client. A helpdesk will handle post-launch enquiries under a service plan agreed before deployment. We will prepare a user-testing checklist with the project lead and use the trial feedback to identify outstanding work before broader adoption.

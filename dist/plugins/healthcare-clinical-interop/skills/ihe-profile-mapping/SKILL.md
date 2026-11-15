---
name: ihe-profile-mapping
description: 'Map a healthcare workflow to IHE integration profiles, actors, options and transactions (ITI: XDS.b, XCA, PIX/PDQ, PIXm/PDQm, MHD, ATNA, XUA, CT; RAD: SWF/SWF.b, PIR, XDS-I.b, IOCM, WIA/WIC) and pin the Technical Framework revision plus underlying HL7/DICOM/FHIR versions. Use for architecture, RFPs, Integration Statements and Connectathon prep.'
license: MIT
metadata:
  version: "1.0"
---

# IHE Profile Mapping

## Steps
1. Describe the workflow and systems; resolve ITI/RAD TF revisions from the profile (`ihe.iti_revision`, `ihe.rad_revision`) or ask.
2. Pick profiles using [references/profile-map.md](references/profile-map.md); note superseded profiles but support the installed base.
3. For each system, list actors and required options; for each actor pair list transactions with **underlying standard + version** (e.g. RAD-4 Procedure Scheduled in SWF.b = HL7 v2.5.1 OMI).
4. Produce: actor diagram (Mermaid), transaction table, Integration Statement draft, gaps vs vendor Integration Statements.

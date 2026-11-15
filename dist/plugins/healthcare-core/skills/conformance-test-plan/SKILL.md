---
name: conformance-test-plan
description: 'Create version-parameterised conformance and integration test plans for healthcare interfaces (HL7 v2, FHIR, DICOM/DICOMweb, C-CDA, IHE transactions, X12, NCPDP), including fixture layout per version, pinned validators and CI wiring. Use when preparing releases, onboarding a trading partner, or for Connectathon/certification readiness.'
license: MIT
metadata:
  version: "1.0"
---

# Conformance Test Plan

## Steps
1. Build the **version matrix** from `healthcare-profile.yml` (every interface version, FHIR core + IG versions, DICOM edition + peer SOP/TS sets, TR3s).
2. Fill [assets/test-plan-template.md](assets/test-plan-template.md).
3. Create synthetic fixtures under `fixtures/<standard>/<version>/...`.
4. Pin validators to each version (examples):
   - FHIR: `java -jar validator_cli.jar <files> -version 4.0.1 -ig <ig-id>#<ig-version>`
   - DICOM: `dciodvfy file.dcm` (dicom3tools; note the edition the tool build reflects)
   - C-CDA: schema + Schematron of the target release
   - HL7 v2: conformance profile for the partner version (e.g. NIST/IGAMT-generated)
   - X12: TR3 validator for the GS08 version
5. Wire a CI job per version so a change for one partner cannot break another.

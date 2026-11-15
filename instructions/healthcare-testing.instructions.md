---
description: 'Testing conventions for healthcare integrations: version-parameterised tests, synthetic fixtures per version, conformance validators pinned to the target version, and negative/edge cases common in real interfaces.'
applyTo: '**/test/**, **/tests/**, **/*.test.*, **/*_test.*, **/*Test.*, **/*.spec.*, **/fixtures/**'
---

# Healthcare Integration Testing

- **Parameterise by version.** If a component supports multiple versions (e.g. HL7 v2.3.1 and v2.5.1 inbound), run the same test matrix against fixtures for each declared version in `healthcare-profile.yml`.
- **Fixtures are synthetic** and live under a folder that names the version: `fixtures/hl7v2/2.3.1/adt_a01.hl7`, `fixtures/fhir/R4/patient.json`, `fixtures/dicom/2024e/ct.dcm`, `fixtures/x12/005010X222A1/837p.edi`.
- **Pin validators** to the target version (FHIR validator with the matching core + IG packages; C-CDA Schematron of the target release; DICOM `dciodvfy`/dicom3tools against the target edition; X12 TR3 validator for the GS08 version).
- **Cover real-world mess:** missing optional segments, extra repetitions, unknown Z-segments, wrong line endings, mixed character sets, truncated MLLP frames, duplicate control IDs, retired transfer syntaxes, unknown codes.
- **Assert on semantics, not just syntax:** e.g. patient merge (A40) actually merges; 835 balances; DICOM study is retrievable after STOW.

---
name: phi-deidentification
description: 'Plan and implement de-identification / pseudonymisation of healthcare data for test fixtures, analytics and AI: DICOM PS3.15 Annex E profiles and options (including pixel data and private tags), HL7 v2 field-level masking, FHIR resource scrubbing, C-CDA and X12 handling, and HIPAA Safe Harbor/Expert Determination framing. Use before sharing or committing any healthcare sample data.'
license: MIT
metadata:
  version: "1.0"
---

# PHI De-identification

## Steps
1. Resolve purpose, jurisdiction and required method (HIPAA Safe Harbor vs Expert Determination are legal concepts — involve the privacy officer), and the **DICOM edition** whose PS3.15 Annex E table you will apply.
2. Choose the profile/options (e.g. Basic Application Level Confidentiality Profile + Retain Longitudinal Temporal Information with Modified Dates, Retain Patient Characteristics, Clean Pixel Data, Clean Descriptors). Record them in `healthcare-profile.yml`.
3. Apply per format — see [references/field-checklist.md](references/field-checklist.md).
4. Generate consistent pseudonyms (keyed HMAC per project, key outside the repo) so longitudinal links survive; replace UIDs consistently.
5. Verify: automated scan for residual identifiers (names, MRNs, dates, phone, email, addresses, free text, burned-in text via OCR) and a manual sample review.
6. Prefer synthetic data generation (e.g. Synthea) over de-identifying real data for test fixtures.

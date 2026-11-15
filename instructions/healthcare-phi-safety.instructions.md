---
description: 'PHI/PII safety rules for healthcare code, test data, logs and prompts: synthetic data only, minimum necessary, no PHI in logs, encryption and audit expectations. Jurisdiction-aware (HIPAA, GDPR, others) without giving legal advice.'
applyTo: '**'
---

# Healthcare PHI / PII Safety

These rules apply to every file, regardless of which standard or version is in use.

## Data in the repository
- Use **synthetic data only** in samples, fixtures, tests, docs and prompts (e.g. Synthea output, obviously fake names like `TEST^PATIENT^ONE`, MRNs prefixed `TEST`, dates shifted, SSNs in the never-issued `000-`/`666-`/`9xx-` ranges).
- Never paste real patient messages, images, documents or claims into code, issues, commits or chat. If a user supplies one, recommend de-identification first (`phi-deidentification` skill) and avoid echoing identifiers back.
- DICOM samples must be de-identified per PS3.15 Annex E **including pixel data** (burned-in annotations) and private tags.

## Code
- Do not log full messages, resources, documents or claims at INFO level. Log message control IDs, resource ids, correlation ids — not names, identifiers, dates of birth, addresses, free text.
- Mask identifiers in exceptions and error responses (`OperationOutcome`, ACK `ERR`, 999/277CA narrative).
- Encrypt PHI in transit (TLS 1.2+ for MLLP-over-TLS, DICOM TLS profiles in PS3.15, HTTPS for FHIR/DICOMweb) and at rest.
- Emit security audit events for PHI access (IHE ATNA / DICOM audit messages / FHIR `AuditEvent`, per the target version).
- Enforce least privilege and "minimum necessary" in queries (e.g. FHIR `_elements`/`_summary`, QIDO `includefield`), and validate authorization scopes (SMART on FHIR scopes per the SMART version in use).

## Regulatory framing
- HIPAA, GDPR, UK-GDPR, India DPDP, etc. are **legal** frameworks. Explain engineering controls that support compliance; flag when something needs a privacy officer or legal review. Do not state that a design "is HIPAA compliant".
- Resolve the jurisdiction from `healthcare-profile.yml` (`context.jurisdiction`); do not assume US.

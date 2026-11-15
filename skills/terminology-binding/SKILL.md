---
name: terminology-binding
description: 'Select, validate and bind clinical codes (SNOMED CT, LOINC, RxNorm, ICD-10-CM/PCS, ICD-11, UCUM, CPT/HCPCS, DICOM CIDs) with explicit code system versions, binding strength and licensing checks, and build version-aware concept maps. Use when coding observations, diagnoses, medications, units or imaging procedures, or mapping local codes.'
license: MIT
metadata:
  version: "1.0"
---

# Terminology Binding

## Steps
1. Resolve code system **versions/editions** (profile `terminology`, `Coding.version`, CWE-7, date of service). ICD-10-CM fiscal year matters for claims dates; SNOMED CT edition matters for national extensions.
2. Never invent codes. Validate via a terminology server (`$validate-code`, `$lookup`) or the official browser for that version; if not possible, mark codes as *unverified*.
3. Bind with explicit strength and value set version in the target FHIR version/IG; in HL7 v2 populate CWE-3 (coding system) and CWE-7 (version) where agreed.
4. Units: UCUM case-sensitive codes; map device MDC units to UCUM.
5. Maps: use ConceptMap (`equivalence` in R4, `relationship` in R5); document unmappable concepts.
6. Licensing: SNOMED CT affiliate licence, CPT (AMA), LOINC/RxNorm terms — never commit licensed tables into repositories without rights.

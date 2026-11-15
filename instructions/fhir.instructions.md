---
description: 'HL7 FHIR engineering guidance (resources, REST, profiles, IGs, FSH) that adapts to the resolved FHIR core version (DSTU2/STU3/R4/R4B/R5/R6) and each Implementation Guide version independently.'
applyTo: '**/*.fsh, **/sushi-config.yaml, **/*fhir*/**, **/StructureDefinition*.json, **/*.fhir.json, **/*.fhir.xml, **/ig.ini'
---

# FHIR Engineering

Follow `healthcare-version-resolution.instructions.md` first. Resolve **core version** and **each IG version** separately (e.g. US Core 9.0.0 is R4; IHE MHD 4.2.5 is R4).

## Version discipline
- Use the right packages/libraries for the core version: `hl7.fhir.r4.core` vs `hl7.fhir.r5.core`; HAPI `FhirContext.forR4()`/`forR4B()`/`forR5()`; .NET `Hl7.Fhir.R4`/`R5`; Python `fhir.resources` sub-packages by version.
- Before using an element, confirm it exists in the target version. Common R4 ↔ R5 traps (non-exhaustive — verify):
  - `MedicationRequest.medication[x]` (R4) → `medication` as `CodeableReference` (R5).
  - `Encounter.class` (Coding, R4) → `CodeableConcept` list (R5); `Encounter.period` → `actualPeriod`.
  - `DeviceUseStatement` (R4) → `DeviceUsage` (R5).
  - Subscriptions: channel-based in R4; topic-based in R5 (use the Subscriptions Backport IG on R4/R4B).
- Need a newer element on an older server? Use a cross-version extension or a published backport — never silently emit the newer shape.
- `meta.profile` canonicals should include `|version` when the programme requires a specific IG version.

## REST & search
- Read `CapabilityStatement` (`GET [base]/metadata`) to discover supported interactions, search params and `fhirVersion` — don't assume.
- Return `OperationOutcome` with appropriate issue codes; never leak PHI in diagnostics.
- Use conditional create/update and `If-Match` ETags for concurrency where supported.

## Profiling (FSH / StructureDefinition)
- Set `fhirVersion` and dependency versions explicitly in `sushi-config.yaml`.
- Prefer binding to published value sets with explicit version where stability matters.
- Validate with the official validator pinned to the same core version and IG packages.

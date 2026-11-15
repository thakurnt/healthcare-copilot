---
description: 'Mandatory version-resolution protocol for all healthcare standards work (DICOM, HL7 v2/v3, FHIR, CDA/C-CDA, IHE, X12, NCPDP, IEEE 11073, terminologies). Never assume the latest release; resolve and state the target version before giving version-dependent guidance.'
applyTo: '**'
---

# Healthcare Standards Version Resolution

Healthcare systems run on many standard versions at once. A hospital may receive HL7 v2.3.1 ADT from its HIS, send v2.5.1 OMI to a modality broker, expose FHIR R4 with US Core, and archive images against a DICOM 2024e conformance statement — all in the same week. **Guidance that is correct for the newest release can be wrong, or even unsafe, for the version actually in use.**

## Rule 1 — Resolve the target version before answering

For every standard the task touches, resolve the target version in this order and stop at the first hit:

1. **Explicit in the request** — "we're on DICOM 2024e", "HL7 2.3", "FHIR STU3".
2. **Project profile** — `.github/healthcare-profile.yml` or `healthcare-profile.yml` (template: `templates/healthcare-profile.yml`). Check per-interface overrides before `default_version`.
3. **Evidence in artifacts** — inspect code, config and sample data:
   | Standard | Where the version lives |
   |---|---|
   | HL7 v2 | `MSH-12` (Version ID), `MSH-21` (profile), interface-engine channel config |
   | FHIR | `CapabilityStatement.fhirVersion`, `package.json` `fhirVersions`, `sushi-config.yaml`, `meta.profile` canonicals (`|version`), client library package (e.g. `hl7.fhir.r4.core`, HAPI `FhirContext.forR4()`, `fhir.resources` sub-package) |
   | DICOM | Conformance Statement, `(0002,0010)` Transfer Syntax UID, `(0002,0013)` Implementation Version Name, SOP Class UIDs in use |
   | C-CDA | `templateId/@extension` dates on header, sections, entries |
   | X12 | `ISA12`, `GS08` (e.g. `005010X222A1`), `ST03` |
   | NCPDP SCRIPT | `Message/@version`, `TransportVersion`, `ECLVersion` |
   | IHE | Integration Statement, transaction numbers, FHIR version of mobile profiles |
   | IEEE 11073 | Protocol version in association request, specialization IDs |
   | Terminology | `Coding.version`, CWE-7/CWE-8, date of service |
   Use the `healthcare-version-detect` skill to scan a repository automatically.
4. **Ask** — if the version materially changes the answer and is still unknown, ask one concise question listing the plausible candidates.
5. **Declared assumption** — only if asking is not possible, choose the *regulatory or most-deployed* version (not the newest) from `standards/catalog.json` and say so explicitly.

## Rule 2 — State the target in the answer

Begin version-dependent output with a short target line, e.g.

> **Target:** HL7 v2.3.1 (from `MSH-12` in `samples/adt_a01.hl7`) · FHIR R4 4.0.1 + US Core 6.1.0 (from `healthcare-profile.yml`)

## Rule 3 — Stay inside the target version

- Use only segments, fields, data types, resources, elements, SOP classes, transfer syntaxes, transactions, templates and codes that **exist in the target version**.
- If the best solution needs a newer feature, say which version introduced it and offer a target-compatible alternative, for example:
  - HL7 v2: Z-segment or site-agreed field usage instead of a field added in a later version.
  - FHIR R4: standard extension, cross-version extension (`http://hl7.org/fhir/<ver>/StructureDefinition/extension-...`) or a backport IG (e.g. Subscriptions R5 Backport) instead of an R5-only element.
  - DICOM: private attributes with a registered private creator, or a different SOP class/transfer syntax supported by the peer's conformance statement.
- Never "upgrade" a message, resource or document to a newer version as a side effect of an unrelated change.

## Rule 4 — Treat versions independently

- A FHIR **Implementation Guide pins its own FHIR version** (e.g. US Core 9.0.0 and IHE MHD 4.2.5 are R4 even though R5 is published). Resolve core and every IG separately.
- The **newest X12 release (008070) is not the HIPAA-mandated version**; HIPAA transactions use 005010 TR3s unless regulation changes.
- **NCPDP** versions follow regulatory compliance dates (see `standards/catalog.json` milestones); two versions may be valid in parallel during a transition.
- **DICOM** editions are cumulative; peers negotiate capabilities (Presentation Contexts, conformance statements) rather than edition numbers.
- **Terminology** validity depends on the release in force at the date of service, not today.

## Rule 5 — Respect the kind of specification

Do not treat all specifications as equivalent. Label obligations correctly:

| Kind | Examples | How to phrase guidance |
|---|---|---|
| Technical interoperability model | DICOM, HL7 v2, FHIR, X12, NCPDP, IEEE 11073 | "The standard defines / requires / allows ..." with section references |
| Integration profile | IHE ITI/RAD | "Actor X SHALL support transaction Y in profile Z (option ...)" |
| Implementation guide | C-CDA, US Core, TR3s | "This IG constrains the base standard: ..." |
| Legal / regulatory | HIPAA, CMS rules, GDPR | "This is a legal obligation; confirm with compliance/legal" — never present engineering guidance as legal advice |
| Terminology | SNOMED CT, LOINC, RxNorm, ICD, UCUM | "Code meaning / binding strength / licence terms ..." |

## Rule 6 — Cite and admit uncertainty

- Reference the specific part/section/chapter of the **target** version (e.g. "HL7 v2.5.1 Ch. 3, PID-3", "DICOM PS3.4 2024e Annex B", "FHIR R4 `Encounter.class`").
- If you are not sure a feature exists in the target version, say so and recommend checking the publisher's archived edition (`standards/catalog.json` → `sources`). Do not invent field numbers, UIDs, template OIDs or codes.

## Rule 7 — Cross-version work

When migrating, mapping or bridging versions (e.g. v2.3 → v2.5.1, R4 → R5, C-CDA 2.1 → 3.0, 004010 → 005010):
- Produce an explicit delta table (added / changed / deprecated / removed) for the elements in scope.
- Identify data-loss and semantic-drift risks.
- Keep both versions working during cutover unless told otherwise.

---
description: 'CDA R2 / C-CDA document engineering guidance that validates each templateId against the C-CDA release that defines it (R1.1, 2.1, 3.0, 4.0, 5.0.0) instead of assuming the newest.'
applyTo: '**/*cda*/**, **/*.cda.xml, **/*ccda*/**, **/*.ccd.xml, **/*.sch'
---

# CDA / C-CDA Engineering

Follow `healthcare-version-resolution.instructions.md` first.
- Template versions are identified by `templateId/@root` **and** `@extension` (a date). Validate every template against the release that defines that extension.
- Documents often legitimately mix template versions (e.g. backwards-compatible R1.1 + R2.1 `templateId` pairs). Preserve required dual templateIds when the receiver requires them.
- Use the schema (`CDA.xsd` + SDTC) and the Schematron for the target release; do not apply newer Schematron to older documents.
- Narrative (`section/text`) must match the coded entries; never drop narrative when generating entries.
- Nullflavor and `@negationInd` semantics differ from FHIR — do not translate mechanically.

---
name: standards-fact-check
description: 'Verify version-specific factual claims in Healthcare Copilot content (agents, instructions, skills, references, catalog, docs) against official publisher sources, using a fixed verdict vocabulary. Used by maintainers and by the PR Standards Review and Content Accuracy Audit agentic workflows.'
license: MIT
metadata:
  version: "1.0"
---

# Standards Fact Check

## What counts as a claim
A statement an engineer could act on that depends on a **specific version**:
- element/segment/field/attribute/resource/template existence or meaning *in version X* ("PRT segment from v2.7", "`Encounter.actualPeriod` in R5");
- identifiers: UIDs, OIDs, template IDs + extension dates, transfer syntax UIDs, TR3 IDs, code values, field positions;
- publication facts: latest edition/release, publication dates, IG → FHIR version pins;
- regulatory facts: adopted versions, compliance dates (always flag as needs compliance review).

Not claims: design advice, process guidance, wording.

## Where to verify (official sources only)
| Standard | Prefer |
|---|---|
| DICOM | `dicom.nema.org/medical/dicom/<edition>/output/html/` (edition-specific), `www.dicomstandard.org` |
| FHIR | `hl7.org/fhir/<DSTU2\|STU3\|R4\|R4B\|R5>/…`, IG pages at their **versioned** canonical, `packages.fhir.org` |
| HL7 v2 / CDA / C-CDA | `hl7.org` product briefs and versioned IG pages |
| IHE | `profiles.ihe.net`, `www.ihe.net` technical frameworks (note the revision) |
| X12 / HIPAA | `x12.org` (titles/IDs only — TR3 text is licensed), `www.cms.gov`, `www.ecfr.gov` |
| NCPDP | `standards.ncpdp.org`, `www.ncpdp.org`, CMS e-prescribing pages |
| IEEE 11073 | `standards.ieee.org` |
| Terminology | publisher sites (`loinc.org`, `www.nlm.nih.gov`, `www.snomed.org`, `ucum.org`, `icd.who.int`) |

## Verdicts
- **verified** — source for the stated version confirms it (cite URL).
- **contradicted** — source shows otherwise (give the correct statement and version).
- **needs-qualification** — true for some versions but stated universally; give the version range.
- **unverifiable** — couldn't fetch or source doesn't settle it. Never upgrade to verified on memory alone.

## Procedure
1. Extract claims with file:line.
2. Identify the **version the claim is about**; if the text doesn't say, that itself is a `needs-qualification` finding.
3. Fetch the version-specific page; quote at most one short phrase as evidence.
4. Report a table: file:line · claim · version · verdict · correct statement · source URL.
5. For catalog entries marked `"verify": true`, a `verified` verdict with a source allows removing the flag (via the `catalog-update` skill).

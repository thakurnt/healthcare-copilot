# Version strategy

Healthcare Copilot is **release-agnostic**: it must work for a team on DICOM 2024e, HL7 v2.3.1, FHIR STU3/R4 or X12 005010 just as well as for one on the newest publications.

## Three separate concepts

| Concept | Where it lives | Who changes it |
|---|---|---|
| **Published** — what exists | `standards/catalog.json` (`latestPublished`, `knownVersions`, `milestones`) | Maintainers, via the *Standards Baseline Watch* workflow + review |
| **Mandated** — what regulation requires on a date | `standards/catalog.json` (`regulatoryDefault`, `adoptedTransactionStandards`, `milestones`) evaluated against `context.as_of_date` | Maintainers, with compliance review |
| **Targeted** — what *this* project implements | `.github/healthcare-profile.yml` in the consuming project | The project team |

Agents and skills **always** answer for the *targeted* version. The newest publication is never a silent default.

## Resolution order (summarised from `instructions/healthcare-version-resolution.instructions.md`)

1. Explicit in the user's request
2. Project profile (`healthcare-profile.yml`, per-interface overrides first)
3. Evidence in artifacts (MSH-12, `fhirVersion`, `templateId/@extension`, `GS08`, transfer syntaxes…) — `healthcare-version-detect` skill
4. Ask the user
5. Declared assumption using the regulatory / most-deployed version (never "latest")

## Why per-interface and per-IG versions
- One hospital commonly runs several HL7 v2 versions (one per partner).
- FHIR IGs pin their own core version (US Core 9.0.0 → R4, IHE MHD 4.2.5 → R4) even though R5 is published and R6 is in development.
- X12 008070 is published but HIPAA transactions use 005010.
- NCPDP versions switch on regulatory dates (RTPB 13 / F&B 60 from 2027-01-01; SCRIPT 2023011 from 2028-01-01 for applicable use cases).

## Writing version-aware content (contributors)
- Phrase version facts as "introduced in / removed in / changed in vX" — never "the standard says" without a version.
- Put version deltas in `skills/<skill>/references/*` tables so they can be updated without touching agent prompts.
- Prefer "verify in <version> <part/chapter>" over a confident guess.
- Add synthetic examples for **old and new** versions in `examples/`.

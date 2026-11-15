---
name: healthcare-version-detect
description: 'Detect which healthcare standard versions a project actually uses (HL7 v2 MSH-12, FHIR core/IG versions, DICOM edition and transfer syntaxes, C-CDA template versions, X12 ISA12/GS08, NCPDP SCRIPT version) using the agent''s built-in search tools, and draft a healthcare-profile.yml. Use before any version-dependent healthcare work, when the user says "which version are we on", "set up healthcare profile", or when no profile exists.'
license: MIT
compatibility: 'No dependencies: works with built-in search/read tools (GitHub Copilot, Claude Code). Optional accelerator script needs Python 3.8+ (standard library only).'
metadata:
  version: "1.1"
---

# Healthcare Version Detect

Establishes the **target versions** that every other agent and skill must honour. Healthcare projects commonly run older releases (DICOM 2024e, HL7 v2.3.1, FHIR R4, X12 005010) — the goal is to find what is actually in use, not what is newest.

## Step 1 — Existing profile
Look for `.github/healthcare-profile.yml` or `healthcare-profile.yml`. If present and complete, use it and stop.

## Step 2 — Collect evidence with built-in search (default)

Use your own search tools (Copilot: text/regex search and codebase search; Claude Code: Grep and Glob). Run the regex searches in [references/search-recipes.md](references/search-recipes.md), one standard at a time, only for standards that plausibly apply (check file types first with a glob such as `**/*.{hl7,er7,edi,x12,dcm,json,xml,fsh,yaml}`).

**PHI-safe search rules — mandatory:**
- Search for the **version marker only** and record the matched value + file path. Use "only matching"/output-limited modes where available.
- **Do not open** whole HL7 messages, claims, C-CDA documents, SCRIPT messages or DICOM files to "have a look". If you must read a file to disambiguate, read only its first lines (e.g. the `MSH` or `ISA`/`GS` segment) and do not repeat identifiers in your answer.
- Skip `node_modules/`, `.git/`, build output and vendored dependencies.
- Cap the work: when a pattern matches many files, sample up to ~20 per folder and report counts.

## Optional script (alternative to Step 2)
If `python3` is available and running commands is allowed, the bundled scanner gives the same evidence in one deterministic pass, including DICOM binary headers (which text search usually skips), and never prints message content:
```bash
python3 <skill-dir>/scripts/detect_versions.py .          # human-readable
python3 <skill-dir>/scripts/detect_versions.py . --json   # machine-readable
```
Prefer it for very large repositories or folders full of DICOM files. If it is unavailable, do not ask the user to install Python — use Step 2.

## Step 3 — Interpret
Conflicting values are normal (e.g. two HL7 v2 versions = two interfaces). Group by folder / sending system / trading partner.

| Evidence | Meaning |
|---|---|
| HL7 v2 `MSH-12` | v2 version per interface |
| FHIR `fhirVersion` / `fhirVersions` / sushi `fhirVersion` | FHIR core version of server or IG |
| `hl7.fhir.rX.core`, `FhirContext.forRX()`, `Hl7.Fhir.RX`, `fhir.resources.RX` | Version the code is built against |
| IG package dependencies, `meta.profile|x.y.z` | IG versions — each has its own FHIR version |
| DICOM transfer syntax / SOP Class UIDs | What peers send; retired syntaxes flag legacy devices |
| DICOM edition text (e.g. `2024e`) | Edition of the conformance statement |
| C-CDA US Realm Header `@extension` | C-CDA release of documents |
| X12 `ISA12`, `GS08` | X12 release and TR3 (e.g. `005010X222A1`) |
| NCPDP `TransportVersion` / `version` | SCRIPT version |

Evidence is not intent: a fixture in `tests/legacy/` may be deliberately old. Confirm with the user before treating a single file as the target.

## Step 4 — Ask about gaps
Ask only about gaps that change the work (e.g. "No DICOM edition found — which edition is your conformance statement written against?").

## Step 5 — Draft the profile
Draft `.github/healthcare-profile.yml` from [assets/healthcare-profile.yml](assets/healthcare-profile.yml), filling detected values and leaving `# TODO confirm` comments on anything inferred. Show it to the user before writing.

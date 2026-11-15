---
name: 'Healthcare Version Drift'
description: 'For projects that use Healthcare Copilot: weekly comparison of the versions declared in .github/healthcare-profile.yml with version evidence found by searching code, config and samples (MSH-12, fhirVersion, IG packages, GS08, DICOM transfer syntaxes, C-CDA template dates); opens one issue when they diverge. Needs no scripts or Python.'
on:
  schedule: weekly
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  copilot-requests: write
tools:
  github:
    toolsets: [repos, issues]
  bash: ["cat", "ls", "head", "find", "sort", "uniq", "wc", "grep", "rg"]
timeout-minutes: 15
safe-outputs:
  create-issue:
    title-prefix: "[version-drift] "
    labels: [healthcare-versions]
    max: 1
    close-older-issues: true
  noop:
---

# Healthcare Version Drift

Self-contained: works whether the team installed Healthcare Copilot as a plugin or copied it into the repo. Only prerequisite: `.github/healthcare-profile.yml` (or `healthcare-profile.yml`).

## 1. Read the declared versions
Read the profile. If it is missing, create an issue asking the team to add one (template: https://github.com/thakurnt/healthcare-copilot/blob/main/templates/healthcare-profile.yml) and stop.

## 2. Collect evidence with search (PHI-safe)
Use `grep -rEno` (or `rg -no`) so only the **matched version marker** and file path are printed. Exclude `.git`, `node_modules`, `dist`, `build`, `target`, vendored folders. Never print whole messages, claims or documents; never `cat` sample data files. When a pattern matches many files, report counts per folder.

Patterns are POSIX extended regexes for `grep -rEno` (`|` means "or"; `\|` means a literal pipe).

- **HL7 v2 `MSH-12`** (`*.hl7`, `*.er7`, `*.txt`, fixtures): `MSH\|[^|]*\|([^|]*\|){9}[0-9]\.[0-9](\.[0-9])?` — the version is the trailing `2.x.y`.
- **FHIR core** (JSON/XML, `sushi-config.yaml`): `"fhirVersion" *: *"[^"]+"` · `<fhirVersion value="[^"]+"` · `^fhirVersion: *[^ ]+`
- **FHIR packages/libraries** (build files, source): `hl7\.fhir\.(r2|r3|r4|r4b|r5|r6)\.core` · `FhirContext\.for(Dstu2|Dstu3|R4B?|R5)` · `Hl7\.Fhir\.(STU3|R4B?|R5)` · `fhir\.resources\.(STU3|R4B?|R5)`
- **FHIR IGs** (`package.json`, sushi config, CapabilityStatement): `"(hl7|ihe)\.[a-z0-9.-]+" *: *"[^"]+"` · `/StructureDefinition/[^"|]+\|[0-9][^"]*`
- **DICOM**: transfer syntaxes in config `1\.2\.840\.10008\.1\.2(\.[0-9]+)*`; for `*.dcm` files run `grep -a -o -E '1\.2\.840\.10008\.1\.2(\.[0-9]+)*' FILE | head -1` per file (sample ≤ 20); edition `20[0-9]{2}[a-e]` near "DICOM" in docs.
- **C-CDA** (`*.xml`): `templateId root="2\.16\.840\.1\.113883\.10\.20\.22\.1\.1"( extension="[^"]+")?`
- **X12** (`*.edi`, `*.x12`, `*.837` …): `GS(\*[^*~]*){7}\*[0-9A-Z]+` (GS08); for ISA12 read the first 106 characters of files starting with `ISA` (`head -c 106`) and take element 12.
- **NCPDP SCRIPT** (`*.xml`): `TransportVersion[=">]+[0-9.]+` · `DatatypesVersion="[^"]+"`

## 3. Compare declared vs observed
- HL7 v2: every observed `MSH-12` should match `hl7v2.default_version` or an `interfaces[].version`.
- FHIR: core packages/`fhirVersion` and IG dependency versions vs `fhir.core`, `fhir.release`, `fhir.implementation_guides`.
- DICOM: observed transfer syntaxes should be in `dicom.transfer_syntaxes`; flag retired ones (e.g. `1.2.840.10008.1.2.2`); edition mentions vs `dicom.edition`.
- C-CDA header extension vs `cda.ccda_release`; X12 `GS08` vs `x12.transactions[].tr3`; NCPDP vs `ncpdp.script`.
- Ignore evidence under folders that are clearly legacy fixtures if the profile or folder name says so.
- If everything matches, call `noop`.

## 4. Issue
Table: standard · declared · observed · where (folders/files, counts) · suggested action (update profile **or** fix code). Never suggest moving to a newer release just because it exists — the profile states what the project intends to support.

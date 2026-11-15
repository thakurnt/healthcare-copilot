---
name: 'Healthcare Version Drift'
description: 'For projects that use Healthcare Copilot: weekly comparison of the versions declared in .github/healthcare-profile.yml with version evidence in code, config and samples (MSH-12, fhirVersion, IG packages, GS08, DICOM transfer syntaxes, C-CDA template dates); opens one issue when they diverge.'
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
  bash: ["cat", "ls", "grep", "head", "find", "python3 .github/skills/healthcare-version-detect/scripts/detect_versions.py:*"]
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

Prerequisites in the repository running this workflow: `.github/healthcare-profile.yml` and the `healthcare-version-detect` skill under `.github/skills/` (installed by `scripts/install.py` from healthcare-copilot).

## Steps

1. Read `.github/healthcare-profile.yml` (or `healthcare-profile.yml`). If missing, create an issue asking the team to add one and stop.
2. Run `python3 .github/skills/healthcare-version-detect/scripts/detect_versions.py . --json`.
3. Compare declared vs observed, per standard:
   - HL7 v2: every observed `MSH-12` should match the `default_version` or an `interfaces[].version`.
   - FHIR: observed core packages/`fhirVersion` and IG dependency versions vs `fhir.core`, `fhir.release`, `fhir.implementation_guides`.
   - DICOM: observed transfer syntaxes should be in `dicom.transfer_syntaxes`; flag retired syntaxes; edition references vs `dicom.edition`.
   - C-CDA, X12 (`GS08` vs `x12.transactions[].tr3`), NCPDP SCRIPT.
4. Ignore evidence under paths that are clearly legacy test fixtures if the profile or folder name says so.
5. If everything matches, call `noop`.

## Issue

Table: standard · declared · observed · where (files) · suggested action (update profile **or** fix code). Never suggest moving to a newer release just because it exists — the profile states what the project intends to support.

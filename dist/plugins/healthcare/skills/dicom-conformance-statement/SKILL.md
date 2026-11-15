---
name: dicom-conformance-statement
description: 'Draft, review or compare DICOM Conformance Statements (PS3.2) for a declared DICOM edition (e.g. 2024e): SOP classes, roles, transfer syntaxes, association policies, character sets, security, and peer-to-peer compatibility analysis. Use when onboarding a modality/PACS/viewer, writing your product conformance statement, or diagnosing association failures.'
license: MIT
metadata:
  version: "1.0"
---

# DICOM Conformance Statement

## Steps
1. Resolve the **edition** the statement is written against (profile → document → ask). Do not assume the latest edition.
2. **Drafting:** follow the PS3.2 structure for that edition (outline in [references/outline.md](references/outline.md)). Populate from code/config: AE titles, SOP classes (UID + name per PS3.6 of that edition), SCU/SCP roles, transfer syntaxes, extended negotiation, character sets, security profiles, DICOMweb services.
3. **Peer compatibility:** build a matrix of *our SCU proposals × their SCP acceptances* per SOP class and transfer syntax; flag empty intersections, retired syntaxes, missing Storage Commitment/MPPS, character-set mismatches.
4. **Review:** check that every claimed SOP class exists in the declared edition, UIDs are correct, and private attributes are documented.

## Output
Target edition line, then the statement or a compatibility matrix with actionable gaps.

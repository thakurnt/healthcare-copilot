---
name: healthcare-version-detect
description: 'Detect which healthcare standard versions a project actually uses (HL7 v2 MSH-12, FHIR core/IG versions, DICOM transfer syntaxes and edition references, C-CDA template versions, X12 ISA12/GS08, NCPDP SCRIPT version) and draft a healthcare-profile.yml. Use before any version-dependent healthcare work, when the user says "which version are we on", "set up healthcare profile", or when no profile exists.'
license: MIT
compatibility: 'Python 3.8+ standard library only. Read-only; prints version metadata, never message content.'
metadata:
  version: "1.0"
---

# Healthcare Version Detect

Establishes the **target versions** that every other agent and skill must honour. Healthcare projects commonly run older releases (DICOM 2024e, HL7 v2.3.1, FHIR R4, X12 005010) — the goal is to find what is actually in use, not what is newest.

## Steps

1. Look for an existing profile: `.github/healthcare-profile.yml` or `healthcare-profile.yml`. If present and complete, use it and stop.
2. Run the scanner from the project root:
   ```bash
   python3 <skill-dir>/scripts/detect_versions.py . 
   python3 <skill-dir>/scripts/detect_versions.py . --json   # machine-readable
   ```
3. Interpret the evidence (see table). Conflicting values are normal — e.g. two HL7 v2 versions means two interfaces; record both.
   | Finding | Meaning |
   |---|---|
   | `hl7v2.MSH-12` | v2 version per message sample; group by sending system |
   | `fhir.fhirVersion` / `fhir.package.fhirVersions` / `fhir.sushi.fhirVersion` | FHIR core version of server/IG |
   | `fhir.core_package`, `fhir.hapi_context`, `fhir.dotnet_package`, `fhir.python_package` | Version the code is compiled against |
   | `fhir.ig_dependencies` | IG versions — each has its own FHIR version |
   | `dicom.transfer_syntax`, `dicom.sop_class` | What peers actually send; retired syntaxes flag legacy devices |
   | `dicom.edition_reference` | Edition named in docs / conformance statement |
   | `ccda.us_realm_header` | C-CDA release (extension date) of documents |
   | `x12.ISA12`, `x12.GS08` | X12 release and TR3 (e.g. `005010X222A1`) |
   | `ncpdp.script_version` | SCRIPT version in sample messages |
4. Ask the user only about gaps that change the work (e.g. "No DICOM edition found — which edition is your conformance statement written against?").
5. Draft `.github/healthcare-profile.yml` from [assets/healthcare-profile.yml](assets/healthcare-profile.yml), filling detected values and leaving `# TODO confirm` comments on anything inferred. Show the diff to the user before writing.

## Notes
- The scanner skips `node_modules`, `.git`, build folders and files > 2 MB.
- It reads the DICOM Part 10 meta header only (group 0002) — no pixel data or patient attributes.
- Evidence is not intent: a fixture in `tests/legacy/` may be deliberately old. Confirm with the user before treating a single file as the target.

---
description: 'DICOM / DICOMweb engineering guidance (IODs, DIMSE, transfer syntaxes, conformance statements, PS3.15 security) that adapts to the resolved DICOM edition (e.g. 2024e) and the peer conformance statement.'
applyTo: '**/*dicom*/**, **/*dcm*/**, **/*.dcm, **/*pacs*/**, **/*dicomweb*/**, **/*wado*/**, **/*.dcm.json'
---

# DICOM Engineering

Follow `healthcare-version-resolution.instructions.md` first. The target is the edition your **Conformance Statement** is written against plus whatever each peer's conformance statement supports.

## Edition discipline
- Only use SOP Classes, Transfer Syntaxes, attributes, Context Groups (CIDs) and DICOMweb parameters that exist in the target edition. If a newer edition adds what you need (e.g. a newer compression transfer syntax), say so and propose a negotiable fallback.
- Retired items (e.g. Explicit VR Big Endian) may still arrive from legacy devices: accept on read if the conformance statement says so; do not emit.

## Implementation rules
- Negotiate, don't assume: propose multiple presentation contexts; fall back to Explicit/Implicit VR Little Endian.
- Respect `(0008,0005)` Specific Character Set; handle multi-valued sets and ISO 2022 escapes.
- UIDs: generate under your organisation's registered root (≤ 64 chars, no leading zeros in components); never reuse UIDs across de-identified copies.
- Treat Type 1/1C/2/2C/3 attribute requirements per the IOD module tables of the target edition.
- Private attributes need a Private Creator element; document them in the conformance statement.
- DICOMweb: use correct media types (`application/dicom`, `application/dicom+json`, `multipart/related; type=...`), honour `Accept` negotiation, and paginate QIDO with `limit`/`offset`.

## Security (PS3.15)
- Use the TLS secure transport profile your edition and peers support; emit audit messages (DICOM/ATNA).
- De-identify per PS3.15 Annex E profile + options declared in `healthcare-profile.yml`, including burned-in pixel data review.

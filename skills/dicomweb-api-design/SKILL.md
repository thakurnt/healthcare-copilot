---
name: dicomweb-api-design
description: 'Design, implement or debug DICOMweb (PS3.18) services and clients — QIDO-RS search, WADO-RS retrieve (instances, frames, bulkdata, rendered, thumbnail), STOW-RS store, UPS-RS worklist — constrained to the DICOM edition and capabilities declared for the project. Use for PACS/VNA web APIs, viewers and cloud imaging integrations.'
license: MIT
metadata:
  version: "1.0"
---

# DICOMweb API Design

## Steps
1. Resolve the DICOM edition and the services the server actually supports (profile → server conformance statement → capability probing). Features vary by edition and vendor; never assume rendered/thumbnail/UPS-RS exist.
2. Map each use case to resources:
   | Use case | Service | Example |
   |---|---|---|
   | Find studies | QIDO-RS | `GET /studies?PatientID=TEST0001&includefield=StudyDescription&limit=50` |
   | Metadata | WADO-RS | `GET /studies/{study}/series/{series}/metadata` (`application/dicom+json`) |
   | Pixel frames | WADO-RS | `GET .../instances/{sop}/frames/1` (`multipart/related; type="application/octet-stream"` or compressed types) |
   | Store | STOW-RS | `POST /studies` (`multipart/related; type="application/dicom"`) |
   | Worklist | UPS-RS | `/workitems` |
3. Specify media types and transfer-syntax parameters explicitly in `Accept`; handle 406 and fallbacks.
4. Specify paging (`limit`/`offset`), `fuzzymatching`, `includefield`, error handling (STOW response `FailedSOPSequence`/`WarningReason`), auth (OAuth2/SMART where applicable), CORS and audit.
5. Provide example requests and a test plan with synthetic, de-identified studies.

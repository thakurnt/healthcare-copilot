# Standards landscape

Healthcare Copilot organises standards into six engineering domains and distinguishes the **kind** of each specification — they are not equivalent.

| Domain | Standards & frameworks | Primary responsibility | Kind |
|---|---|---|---|
| Medical imaging | DICOM, DICOMweb (PS3.18), DICOM Security (PS3.15) | Images, metadata, storage and exchange | Technical model |
| Clinical interoperability | HL7 v2, HL7 v3, FHIR, CDA, C-CDA | Clinical information exchange | Technical model / implementation guide |
| Enterprise interoperability | IHE ITI (XDS.b, PIX, PDQ, ATNA, XUA, MHD, XCA), IHE RAD (SWF.b, XDS-I.b, PIR…) | End-to-end workflows | Integration profile |
| Healthcare administration | HIPAA, ASC X12, NCPDP SCRIPT/Telecom | Privacy, claims, eligibility, pharmacy | Legal (HIPAA) / technical (X12, NCPDP) |
| Medical device interoperability | ISO/IEEE 11073 (PHD, SDC), IHE PCD | Device data and communication | Technical model / integration profile |
| Cross-cutting terminology | SNOMED CT, LOINC, RxNorm, ICD, UCUM, DICOM CIDs | Clinical semantics | Terminology |

## Businesses supported → plugins

| Business | Typical systems | Plugin(s) |
|---|---|---|
| Medical imaging | PACS, RIS, VNA, modalities, DICOM gateways, viewers | `healthcare-imaging` |
| Hospital systems | HIS, EMR/EHR, LIS, RIS, pharmacy | `healthcare-clinical-interop` |
| Healthcare interoperability | FHIR servers, HL7 interfaces, HIE, MPI, document exchange | `healthcare-clinical-interop` |
| Healthcare insurance | Claims, eligibility, prior auth, remittance | `healthcare-revenue-cycle` |
| Medical devices | Patient monitoring, POC devices, connectivity | `healthcare-devices` |
| Healthcare platforms | Portals, mobile apps, analytics, clinical data platforms | `healthcare-clinical-interop` + `healthcare-core` |

`healthcare-core` (version resolution, architecture, security/privacy, terminology, testing) is always installed.

See [README.standards.md](README.standards.md) for the generated catalog view.

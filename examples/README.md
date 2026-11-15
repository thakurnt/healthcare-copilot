# Examples (synthetic only)

Deliberately spans **old and new** versions so agents and scripts are exercised beyond the latest release.

| Path | Standard / version |
|---|---|
| `hl7v2/2.3.1/adt_a01.hl7` | HL7 v2.3.1 ADT^A01 |
| `hl7v2/2.5.1/omi_o23.hl7` | HL7 v2.5.1 OMI^O23 (IHE SWF.b style) |
| `fhir/R4/` | FHIR R4 4.0.1 + US Core 6.1.0 + IHE MHD 4.2.5 |
| `fhir/R5/` | FHIR R5 5.0.0 IG config |
| `ccda/2.1/ccd.xml` | C-CDA 2.1 CCD skeleton |
| `x12/005010X222A1/837p.edi` | X12 005010 837P envelope |
| `ncpdp/2017071/newrx.xml` | NCPDP SCRIPT 2017071 header |
| `dicom/2024e/sc_test.dcm` | DICOM Part 10 header-only object |

All identifiers contain TEST markers. Never add real data here.

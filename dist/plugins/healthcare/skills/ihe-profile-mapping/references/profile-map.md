# IHE profile quick map (verify against the target TF revision)

| Need | Profile(s) | Underlying standards (typical) |
|---|---|---|
| Patient identity cross-reference | PIX (HL7 v2), PIXv3 (HL7 v3), PIXm (FHIR) | v2.3.1/2.5 ADT/QBP; HL7 v3; FHIR R4 |
| Patient demographics query | PDQ, PDQv3, PDQm | v2.5 QBP/RSP; HL7 v3; FHIR R4 |
| Document sharing in an affinity domain | XDS.b (+XDS-I.b for imaging) | ebRS/ebRIM SOAP; DICOM KOS for imaging manifests |
| Cross-community query/retrieve | XCA (+XCA-I) | SOAP |
| Mobile document access | MHD (FHIR R4 in MHD 4.x), MHDS | FHIR R4 |
| Audit & node authentication | ATNA | TLS; syslog; DICOM audit schema / FHIR AuditEvent (by option) |
| Consistent time | CT | NTP |
| User assertion | XUA | SAML |
| Radiology scheduled workflow | SWF (legacy, v2.3.1) → SWF.b (v2.5.1) | HL7 v2 ADT/OMI/OMG; DICOM MWL, MPPS, Storage, Storage Commitment |
| Patient info reconciliation | PIR | HL7 v2 ADT/OMI updates; DICOM |
| Imaging object change mgmt | IOCM | DICOM KOS (rejection notes) |
| Reporting workflow | RWF / RWF.b | HL7 v2, DICOM SR/UPS |
| Web image access | WIA, WIC | DICOMweb |

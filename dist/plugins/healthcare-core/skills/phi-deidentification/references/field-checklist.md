# De-identification field checklist (starting point — not exhaustive)

## DICOM (apply the Annex E table of the target edition)
- Patient module: (0010,0010) Name, (0010,0020) ID, (0010,0030) Birth Date, (0010,1000) Other IDs, (0010,1040) Address, (0010,2154) Telephone.
- Study/visit: (0008,0050) Accession Number, (0008,0080/0081) Institution Name/Address, (0008,0090) Referring Physician, (0008,1050) Performing Physician, (0020,0010) Study ID.
- Dates/times per chosen temporal option; all UIDs remapped consistently ((0020,000D), (0020,000E), (0008,0018), referenced UIDs in sequences).
- Private tags: remove unless whitelisted by private creator.
- Pixel data: burned-in annotations ((0028,0301) Burned In Annotation is not reliable on its own); secondary capture and ultrasound especially.
- Structured reports and free-text descriptors.

## HL7 v2
PID-3/5/6/7/11/13/14/18/19/20, PD1, NK1, GT1, IN1/IN2, PV1-7/8/9/17 (providers if required), MRG, OBX free text (TX/FT/ED), NTE, MSH-10 if it encodes identifiers.

## FHIR
Patient, RelatedPerson, Practitioner (if required), identifiers on all resources, `text.div` narrative, Attachment data, extensions with addresses, `Reference.display`, dates (shift consistently).

## C-CDA
recordTarget, author, custodian, informant, participants, narrative blocks, `originalText`.

## X12
NM1 (patient/subscriber), N3/N4, DMG, REF identifiers, CLM01 if meaningful, dates (DTP).

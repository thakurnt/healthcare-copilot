# Conformance Statement outline (follow PS3.2 of the target edition)

1. Overview — one-page summary of network services, media services, transfer syntaxes.
2. Table of contents / Introduction — revision history, audience, remarks, terms, references (**state the DICOM edition**).
3. Networking
   - Implementation model: application data flow, functional definition of AEs, sequencing.
   - AE specifications: SOP classes (UID, name, SCU/SCP), association policies (max PDU, number of associations, async ops), implementation class UID / version name.
   - Association initiation/acceptance policies per real-world activity; presentation context tables (abstract syntax × transfer syntax × role × extended negotiation).
   - SOP-specific conformance: status codes returned/handled, attributes used for matching/return keys.
   - Network interfaces, configuration (AE titles, ports), DICOMweb services and media types.
4. Media interchange (if any) — application profiles.
5. Support of character sets.
6. Security — TLS profile(s), audit trail, de-identification profile/options, digital signatures.
7. Annexes — IOD contents (created SOP instances, Type usage), data dictionary of private attributes, coded terminology/templates, grayscale/color, standard extended/specialized/private SOP classes.

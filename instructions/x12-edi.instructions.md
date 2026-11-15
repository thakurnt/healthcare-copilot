---
description: 'ASC X12 healthcare EDI guidance (837/835/270/271/276/277/278/834/820, 999/TA1) that targets the HIPAA-adopted 005010 TR3s by default and recognises newer X12 releases (e.g. 008070) as non-mandated unless the profile says otherwise.'
applyTo: '**/*.x12, **/*.edi, **/*.837, **/*.835, **/*.270, **/*.271, **/*.276, **/*.277, **/*.278, **/*.834, **/*x12*/**, **/*edi*/**'
---

# ASC X12 Healthcare EDI

Follow `healthcare-version-resolution.instructions.md` first.
- Version is in `ISA12` (e.g. `00501`) and `GS08` (e.g. `005010X222A1`). Use the TR3 that `GS08` names, including errata (A1/A2).
- **Do not migrate to a newer X12 release because it is published.** HIPAA-covered transactions use the adopted version (currently 005010) until regulation changes; newer releases may be used only by trading-partner agreement for non-HIPAA flows.
- Read delimiters from the ISA segment (element separator = ISA char 4, component = ISA16, segment terminator = char after ISA16, repetition = ISA11 in 5010).
- Validate loops, situational rules and code lists per the TR3; honour payer companion guides.
- Generate correct envelopes (ISA/IEA, GS/GE, ST/SE counts and control numbers) and acknowledge with 999/TA1 (and 277CA where applicable).
- Claims contain PHI: follow `healthcare-phi-safety.instructions.md`.

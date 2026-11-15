---
name: x12-transaction-analyzer
description: 'Analyse ASC X12 healthcare EDI files (837P/I/D, 835, 270/271, 276/277, 278, 834, 820, 999, TA1): detect delimiters, ISA12/GS08 version and TR3, validate envelopes and loops against the correct 005010 TR3 (or an agreed newer release), and explain rejections. Works with built-in read/search tools; optional script for envelope summaries. Use for claims, remittance, eligibility and prior-auth EDI work.'
license: MIT
compatibility: 'No dependencies. Optional script needs Python 3.8+ (standard library only).'
metadata:
  version: "1.1"
---

# X12 Transaction Analyzer

## Steps
1. **Envelope summary — read only the envelope.** Read the first ~120 characters (the fixed-length `ISA`) and search for `GS`/`ST`/`SE`/`GE`/`IEA` segments; do not echo `NM1`, `N3`/`N4`, `DMG` or `REF` member data.
   - Delimiters from `ISA`: element separator = 4th character, repetition = `ISA11`, component = `ISA16`, segment terminator = character after `ISA16`.
   - `ISA12` = interchange version (e.g. `00501`); `GS08` = TR3 (e.g. `005010X222A1`); `ST01`/`ST03` = transaction set and implementation convention.
   - Patterns (separator `*`): `ISA(?:\*[^*]*){11}\*([0-9]{5})`, `GS(?:\*[^*~]*){7}\*([0-9A-Z]+)`, `ST\*([0-9]{3})\*([^*~]*)`.
2. **Resolve the TR3 from GS08.** HIPAA 5010 TR3s: 837P `005010X222A1`, 837I `005010X223A2`, 837D `005010X224A2`, 835 `005010X221A1`, 270/271 `005010X279A1`, 276/277 `005010X212`, 278 `005010X217`, 834 `005010X220A1`, 820 `005010X218`, 999 `005010X231A1`. **HIPAA-covered transactions use 005010**; X12 008070 (March 2026) is a publication, not a mandate. If GS08 names another release, confirm a trading-partner agreement.
3. **Validate** loops/segments/situational rules against that TR3 and the payer companion guide; check counts and control numbers (`SE01` = segments in set, `ST02` = `SE02`, `GE01`/`IEA01` counts, `GS06` = `GE02`, `ISA13` = `IEA02`).
4. **Rejections:** 999 `IK3`/`IK4` (segment/element errors) or 277CA `STC` codes → map back to the segment.
5. **835:** check balancing (CLP, SVC, CAS, PLB vs BPR).

## Optional script
If `python3` is available, the envelope summary is one command and prints metadata only:
```bash
python3 <skill-dir>/scripts/x12_inspect.py claim.edi
```
Otherwise use step 1. Use synthetic data only.

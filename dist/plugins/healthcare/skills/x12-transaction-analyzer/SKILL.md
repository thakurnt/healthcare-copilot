---
name: x12-transaction-analyzer
description: 'Analyse ASC X12 healthcare EDI files (837P/I/D, 835, 270/271, 276/277, 278, 834, 820, 999, TA1): detect delimiters, ISA12/GS08 version and TR3, validate envelopes and loops against the correct 005010 TR3 (or an agreed newer release), and explain rejections. Use for claims, remittance, eligibility and prior-auth EDI work.'
license: MIT
compatibility: 'Python 3.8+ standard library only.'
metadata:
  version: "1.0"
---

# X12 Transaction Analyzer

## Steps
1. Envelope summary: `python3 <skill-dir>/scripts/x12_inspect.py claim.edi` (prints metadata only).
2. Resolve the TR3 from GS08. **HIPAA-covered transactions use 005010 TR3s**; X12 008070 (March 2026) is a publication, not a mandate. If GS08 names a newer release, confirm a trading-partner agreement exists.
3. Validate loops/segments/situational rules against that TR3 and the payer companion guide; check ST/SE, GS/GE, ISA/IEA counts and control numbers.
4. For rejections, read the 999 (IK3/IK4 segment/element errors) or 277CA (STC status codes) and map back to the segment.
5. For 835, check balancing (CLP, SVC, CAS, PLB vs BPR).
Use synthetic data only.

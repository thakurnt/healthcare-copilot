---
name: hl7v2-message-inspector
description: 'Inspect HL7 v2 messages (ADT, ORM/OML/OMI, ORU, SIU, ACK…): report MSH-12 version, structure and version-specific issues against a target version (2.1–2.9.1) while keeping PHI out of the output. Works with built-in read/search tools; an optional script adds deterministic checks and automatic PHI masking. Use when debugging an HL7 v2 interface, reviewing sample messages, or checking a message against an older/newer partner version.'
license: MIT
compatibility: 'No dependencies. Optional script needs Python 3.8+ (standard library only).'
metadata:
  version: "1.1"
---

# HL7 v2 Message Inspector

## Steps
1. **Resolve the target version** (user → `healthcare-profile.yml` interface entry → `MSH-12`).
2. **Read the message structure, not the patient.** Read the message, then work only with segment IDs, `MSH` fields and field *positions*. In everything you write back:
   - never repeat values from `PID`, `PD1`, `NK1`, `GT1`, `IN1`, `IN2`, `MRG`, `PV1` or free-text `OBX`/`NTE` — refer to them as `PID-5 (masked)`;
   - if the user pasted the message, say they should use synthetic or de-identified data next time.
3. **Parse correctly:**
   - segments end with `\r` (files may show `\n`); the field separator is the character after `MSH`; encoding characters are `MSH-2`;
   - in `MSH`, field numbering starts with `MSH-1` = the separator, so the first `|`-split element after `MSH` is `MSH-2`;
   - components split on `MSH-2[0]` (normally `^`), repetitions on `MSH-2[1]` (`~`).
4. **Check against the target version** using [references/version-notes.md](references/version-notes.md). Minimum checks:
   | Check | Rule |
   |---|---|
   | `MSH-12` empty or ≠ target | Ask which applies to this interface |
   | 5 encoding characters in `MSH-2` | Truncation character is defined from v2.7 |
   | `MSH-9.3` present | Message structure component exists from v2.3.1 |
   | `OMI`/`OML`/`OMG` on a pre-2.5 target | Not available — use `ORM^O01` or confirm the version |
   | `ORM` on a 2.5+ target | Legacy; keep only if the partner spec requires it |
   | `SFT` (< 2.5), `PRT`/`UAC` (< 2.7) | Segment not defined in the target |
   | `PID-2`/`PID-4` populated on 2.5+ | Backward-compatibility fields — prefer `PID-3` |
   | Z-segments | Validate against the site interface spec |
5. **Report:** Target line → structure summary (segment list, `MSH-9`, `MSH-10`, `MSH-12`) → issues (severity, segment-field, version reference) → fixes valid **in the target version**.

## Optional script
If `python3` is available, the bundled inspector runs the checks above deterministically and masks PHI segments automatically — recommended for real-looking data and for repeatable results:
```bash
python3 <skill-dir>/scripts/hl7v2_inspect.py message.hl7 --target-version 2.3.1
python3 <skill-dir>/scripts/hl7v2_inspect.py message.hl7 --json
```
`--show-phi` disables masking — synthetic data only. If Python isn't available, don't ask the user to install it; follow the steps above.

## Limits
Neither path replaces a full conformance-profile validator; say "verify in v<x> chapter <n>" for anything not covered.

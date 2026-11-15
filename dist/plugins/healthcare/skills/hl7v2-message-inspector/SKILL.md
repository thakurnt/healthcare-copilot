---
name: hl7v2-message-inspector
description: 'Parse and inspect HL7 v2 messages (ADT, ORM/OML/OMI, ORU, SIU, ACK…), report MSH-12 version, structure and version-specific warnings against a target version (2.1–2.9.1), with PHI masked by default. Use when debugging an HL7 v2 interface, reviewing sample messages, or checking whether a message is valid for an older/newer partner version.'
license: MIT
compatibility: 'Python 3.8+ standard library only.'
metadata:
  version: "1.0"
---

# HL7 v2 Message Inspector

## Steps
1. Resolve the target version (user → `healthcare-profile.yml` interface entry → `MSH-12`).
2. Run:
   ```bash
   python3 <skill-dir>/scripts/hl7v2_inspect.py message.hl7 --target-version 2.3.1
   python3 <skill-dir>/scripts/hl7v2_inspect.py message.hl7 --json
   ```
   PHI segments (PID, PD1, NK1, GT1, IN1, IN2, MRG, PV1) are masked unless `--show-phi` is passed — use that only for synthetic data.
3. Combine the script's warnings with [references/version-notes.md](references/version-notes.md) and the partner specification.
4. Report: **Target** line, structure summary, issues (severity, segment-field, version reference), suggested fix that is valid **in the target version**.

## Limits
The script encodes a small, conservative rule set. It does not replace a full conformance-profile validator; say "verify in v<x> chapter <n>" for anything it does not cover.

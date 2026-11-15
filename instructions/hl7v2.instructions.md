---
description: 'HL7 v2.x message and interface engineering guidance that adapts to the target v2 version (2.1 through 2.9.1) resolved from MSH-12 or the project profile.'
applyTo: '**/*.hl7, **/*.er7, **/*hl7*/**, **/*mllp*/**, **/*.v2.txt'
---

# HL7 v2 Engineering

Follow `healthcare-version-resolution.instructions.md` first. The version comes from `MSH-12` or the interface entry in `healthcare-profile.yml`; **different interfaces in the same product often use different versions**.

## Encoding
- Segment terminator is `<CR>` (`\r`), not `\n`. Normalise line endings in fixtures.
- Read delimiters from `MSH-1`/`MSH-2`; never hard-code `|^~\&`. From v2.7, `MSH-2` may contain a 5th character (truncation `#`).
- Handle escape sequences (`\F\ \S\ \T\ \R\ \E\`, `\Xhh\`, `\.br\`) and character set (`MSH-18`).
- MLLP framing: `<VT>` (0x0B) … `<FS><CR>` (0x1C 0x0D).

## Version-sensitive patterns (verify against the target chapter)
- **Data types:** `CE` → `CWE`/`CNE`, `TS` → `DTM`, `CN`/`CM` changes happen across releases (CE/TS withdrawn by v2.7). Use what the target version defines.
- **Orders:** `ORM^O01` is the classic order message (common in 2.3.x/2.4); later versions favour `OML`/`OMI`/`OMG` (IHE SWF.b uses `OMI^O23` on v2.5.1).
- **Message structure:** `MSH-9.3` (message structure, e.g. `ADT_A01`) exists from v2.3.1; older versions only have type^event.
- **Patient identifiers:** `PID-3` is the identifier list; `PID-2`/`PID-4` are retained for backward compatibility only — do not populate them for new interfaces on v2.5+ unless the partner spec requires it.
- **Acknowledgements:** original vs enhanced mode via `MSH-15`/`MSH-16`; `ERR` segment structure changed in v2.5 (ERR-1 vs ERR-2..). Build ACKs for the sender's version and echo `MSH-10` into `MSA-2`.

## Practice
- Treat the partner implementation spec (and Z-segments) as authoritative over the base standard; document deviations.
- Be liberal on read (tolerate extra fields/components/repetitions) and strict on write.
- Validate with a version-specific conformance profile where available.
- Never invent field positions — if unsure, say "verify in v<x> chapter <n>".

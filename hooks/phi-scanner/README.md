---
name: 'PHI Scanner'
description: 'Scans files modified during an agent session for likely PHI (SSNs, MRN-like identifiers, real-looking HL7 PID segments, DICOM files with patient names, X12 NM1 member data) and warns or blocks before commit.'
tags: ['healthcare', 'phi', 'privacy', 'security', 'session-end']
---

# PHI Scanner Hook

Healthcare repositories must contain **synthetic data only**. This hook scans files changed in the session (git diff + untracked) at `sessionEnd` and reports suspicious content.

## What it checks
- US SSN patterns (excluding never-issued `000`, `666`, `9xx` area numbers used for test data)
- HL7 v2 `PID` segments whose names do not look synthetic (no `TEST`/`DEMO`/`SYNTH`/`ZZ` marker)
- DICOM Part 10 files (reports them so a human confirms they are de-identified)
- X12 `NM1*IL` / `NM1*QC` segments without a synthetic marker
- Email addresses and phone numbers in fixtures

## Configuration
| Env | Default | Meaning |
|---|---|---|
| `SCAN_MODE` | `warn` | `warn` prints findings; `block` exits non-zero |
| `SYNTHETIC_MARKERS` | `TEST,DEMO,SYNTH,ZZ,FAKE,SAMPLE` | Tokens that mark data as synthetic |

## Install
Copy this folder to `.github/hooks/phi-scanner/` in your project and make the script executable (`chmod +x scan-phi.sh`).

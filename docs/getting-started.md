# Getting started

## 1. Install into your project

```bash
git clone https://github.com/<owner>/healthcare-copilot.git
cd healthcare-copilot

# GitHub Copilot (VS Code / Copilot CLI / coding agent)
python3 scripts/install.py ../my-pacs --tool copilot --plugin healthcare-imaging

# Claude Code
python3 scripts/install.py ../my-pacs --tool claude --plugin healthcare-imaging

# Both, everything, preview only
python3 scripts/install.py ../my-pacs --tool both --plugin all --dry-run
```

`healthcare-core` is always included. Existing files are kept unless you pass `--force`.

## 2. Declare your versions

Edit `.github/healthcare-profile.yml` in your project (created from `templates/healthcare-profile.yml`). Declare what you **use**, e.g. DICOM `2024e`, HL7 v2 `2.3.1` for the ADT feed, FHIR `R4` + US Core `6.1.0`, X12 `005010`.

Not sure? Ask the agent: *"Detect which healthcare standard versions this repo uses"* — it runs the `healthcare-version-detect` skill and drafts the profile.

## 3. Use it

- Copilot Chat: pick an agent (e.g. **DICOM Imaging Engineer**) from the agent dropdown.
- Claude Code: agents appear as sub-agents (`/agents`); skills load automatically when relevant.
- Every version-dependent answer starts with a **Target:** line showing which versions were used and where they came from. If it's wrong, correct it in the profile.

## Example prompts
- "Our modality sends Explicit VR Big Endian to our 2024e PACS — what should we do?"
- "Map this HL7 v2.3.1 ADT^A08 to FHIR R4 Patient for US Core 6.1.0."
- "Is this 837P valid for 005010X222A1? Explain the 999 rejection."
- "Design SWF.b integration between our RIS and PACS; the HIS only speaks HL7 2.3."

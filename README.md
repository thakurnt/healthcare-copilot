# 🏥 Healthcare Copilot

**A reusable, version-aware healthcare interoperability engineering framework for GitHub Copilot, Claude Code and other agent tools.**

Agents, instructions, skills, hooks and plugins that help developers, architects, testers, integration engineers and security engineers understand healthcare requirements, design integrations, generate implementation artifacts, troubleshoot interoperability issues and validate conformance — across **DICOM, DICOMweb, HL7 v2/v3, FHIR, CDA/C-CDA, IHE, HIPAA, ASC X12, NCPDP, IEEE 11073 and clinical terminologies**.

Structure and conventions follow [github/awesome-copilot](https://github.com/github/awesome-copilot).

---

## The core principle: you choose the version, not the newest release

Real healthcare systems run old and new releases side by side: a DICOM **2024e** PACS, an **HL7 v2.3.1** ADT feed, a **v2.5.1** order interface, a **FHIR R4** API with **US Core 6.1.0**, **X12 005010** claims. Guidance that is right for the newest release can be wrong for yours.

Every resource here:

1. **Resolves the target version** — from your request → your project's `healthcare-profile.yml` → evidence in your artifacts (MSH-12, `fhirVersion`, `templateId/@extension`, GS08, transfer syntaxes…) → asking you. Never defaults to "latest".
2. **States it** — answers begin with `Target: HL7 v2.3.1 (from MSH-12) · FHIR R4 4.0.1 + US Core 6.1.0 (from profile)`.
3. **Stays inside it** — only uses features of that version; offers compatible alternatives (Z-segments, cross-version extensions, backport IGs, negotiable transfer syntaxes) when a newer feature would be needed.
4. **Tracks versions independently** — per interface, per FHIR IG, per regulatory date.

➡️ [docs/version-strategy.md](docs/version-strategy.md) · [instructions/healthcare-version-resolution.instructions.md](instructions/healthcare-version-resolution.instructions.md)

---

## Quick start

### Install as a GitHub Copilot plugin

```bash
copilot plugin marketplace add thakurnt/healthcare-copilot
copilot plugin install healthcare-core@healthcare-copilot
copilot plugin install healthcare-imaging@healthcare-copilot   # or: healthcare-clinical-interop, healthcare-revenue-cycle, healthcare-devices
```

VS Code: add `"chat.plugins.marketplaces": ["thakurnt/healthcare-copilot"]` to settings, then run **Chat: Plugins**.
Full guide (VS Code, updates, instructions & hooks, troubleshooting): **[docs/installing-plugins.md](docs/installing-plugins.md)**

### Or copy into your repository (Copilot coding agent, Claude Code)

```bash
git clone https://github.com/thakurnt/healthcare-copilot.git
python3 healthcare-copilot/scripts/install.py ../your-project --tool copilot --plugin healthcare-imaging
python3 healthcare-copilot/scripts/install.py ../your-project --tool claude  --plugin healthcare-clinical-interop
```

### Then declare your versions

Create `your-project/.github/healthcare-profile.yml` ([template](templates/healthcare-profile.yml)) — or ask an agent: *"Detect which healthcare standard versions this repo uses."*

More: [docs/getting-started.md](docs/getting-started.md)

---

## What's inside

| Resource | Count | Index |
|---|---|---|
| 🤖 Agents | 12 | [docs/README.agents.md](docs/README.agents.md) |
| 📋 Instructions | 8 | [docs/README.instructions.md](docs/README.instructions.md) |
| 🎯 Skills | 11 | [docs/README.skills.md](docs/README.skills.md) |
| 🪝 Hooks | 1 | [docs/README.hooks.md](docs/README.hooks.md) |
| ⚡ Workflows | 1 | [docs/README.workflows.md](docs/README.workflows.md) |
| 🔌 Plugins | 5 | [docs/README.plugins.md](docs/README.plugins.md) |
| 📚 Standards catalog | 15 | [docs/README.standards.md](docs/README.standards.md) |

### Plugins by healthcare business

| Plugin | For | Highlights |
|---|---|---|
| `healthcare-core` | Everyone (always installed) | Interop architect, security & privacy reviewer, terminology specialist, conformance tester, version detection, PHI de-identification, PHI scanner hook |
| `healthcare-imaging` | PACS, RIS, VNA, modalities, gateways, viewers | DICOM engineer, IHE advisor, conformance statements, DICOMweb design |
| `healthcare-clinical-interop` | HIS/EMR/EHR/LIS, FHIR servers, HIE, MPI, platforms | HL7 v2, FHIR, C-CDA engineers; HL7 v2 inspector, FHIR version compatibility, C-CDA review |
| `healthcare-revenue-cycle` | Payers, clearinghouses, providers' billing, pharmacy | X12 EDI and NCPDP engineers, X12 analyzer |
| `healthcare-devices` | Patient monitoring, POC, device connectivity | IEEE 11073 / IHE PCD engineer |

### Standards domains

| Domain | Standards | Kind |
|---|---|---|
| Medical imaging | DICOM, DICOMweb, DICOM Security | Technical model |
| Clinical interoperability | HL7 v2, HL7 v3, FHIR, CDA, C-CDA | Technical model / IG |
| Enterprise interoperability | IHE ITI & RAD (XDS.b, XDS-I.b, SWF.b, PIX, PDQ, ATNA, MHD…) | Integration profile |
| Healthcare administration | HIPAA, ASC X12, NCPDP | Legal / technical |
| Medical devices | IEEE 11073 | Technical model |
| Terminology | SNOMED CT, LOINC, RxNorm, ICD, UCUM, DICOM CIDs | Terminology |

The **kind** matters: DICOM and FHIR define technical models; IHE defines integration profiles; HIPAA defines legal obligations; terminologies define concepts. Agents phrase guidance accordingly. See [docs/standards-landscape.md](docs/standards-landscape.md).

---

## Research baseline (15 November 2026)

Publication baselines — **not** default targets. Maintained in [standards/catalog.json](standards/catalog.json) and refreshed by the [Standards Baseline Watch](workflows/standards-baseline-watch.md) workflow.

| Standard | Latest published | Watch out for |
|---|---|---|
| DICOM / DICOMweb / PS3.15 | 2026d | Your conformance statement edition (e.g. 2024e) and peer capabilities govern |
| HL7 v2 | 2.9.1 (2024) | 2.3.x / 2.5.1 dominate production; versions differ per interface |
| FHIR | R5; R6 in development | R6 ≠ R5; US Core 9.0.0 and IHE MHD 4.2.5 are **R4** |
| C-CDA | 5.0.0 (June 2026) | Receivers/programmes may require 2.1 |
| IHE ITI / RAD | ITI 20.2 (Nov 2025) / RAD 23.0 (Aug 2025) | SWF superseded by SWF.b |
| ASC X12 | 008070 (Mar 2026) | HIPAA transactions remain **005010** |
| NCPDP | SCRIPT 2023011 | RTPB 13 & F&B 60 from 2027-01-01; SCRIPT 2023011 from 2028-01-01 (applicable use cases) |
| IEEE 11073-20601 | 2026 (13 Nov 2026) | Devices in the field run older revisions |

---

## Repository layout

```
agents/        instructions/   skills/      hooks/      workflows/   plugins/
standards/     templates/      examples/    docs/       scripts/     .schemas/
dist/plugins/  (generated, installable)     .github/plugin/marketplace.json (generated)
```

See [AGENTS.md](AGENTS.md) for authoring rules. Validate with:

```bash
python3 .github/scripts/build.py          # validate + regenerate docs
python3 .github/scripts/build.py --check  # CI
```

## Roadmap

- MCP servers: terminology lookup (`$validate-code` against your chosen editions), FHIR validator wrapper, DICOM association tester
- Skills: MLLP troubleshooting, HL7 v2 → FHIR mapping (per v2-to-FHIR IG version), NCPDP SCRIPT inspector, IEEE 11073 nomenclature mapping, SMART on FHIR app review
- More synthetic examples for legacy versions (HL7 2.2/2.4, FHIR STU3, DICOM 2019–2023, X12 004010 migration)
- Non-US regulatory packs (GDPR/UK, India ABDM/DPDP, Australia, Canada)

## Safety

Synthetic data only — never PHI. Engineering guidance, not legal or clinical advice. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)

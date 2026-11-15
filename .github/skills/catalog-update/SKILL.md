---
name: catalog-update
description: 'Apply changes to standards/catalog.json (new editions, releases, IG versions, regulatory milestones, verify flags) and propagate them consistently to README, docs, references and plugin versions without changing any target-version guidance. Use when acting on Standards Baseline Watch or Catalog Impact Analysis issues.'
license: MIT
metadata:
  version: "1.0"
---

# Catalog Update

## Principles
- The catalog records **published** and **mandated** facts. It never sets a project's **target**. Examples and templates that use older versions (DICOM 2024e, HL7 v2.3.1, FHIR R4, X12 005010) are intentional — do not "upgrade" them.
- Every changed value needs a source URL (in `sources` of that entry) and, if not verified against the publisher, `"verify": true`.
- Regulatory changes (HIPAA adopted standards, CMS/NCPDP compliance dates) need a human with compliance context to approve the PR.

## Steps
1. Edit `standards/catalog.json`:
   - `latestPublished`, `knownVersions` (append; never delete old versions — users still target them),
   - `implementationGuides[]` (with the IG's own `fhirVersion`),
   - `milestones[]` / `adoptedTransactionStandards[]` / `regulatoryDefault`,
   - `researchBaseline` → today's date when you've reviewed all entries.
2. Propagate:
   - README "Research baseline" table and `docs/standards-landscape.md` if they restate the value.
   - Version-delta references (e.g. `skills/fhir-version-compatibility/references/version-map.md`, `skills/hl7v2-message-inspector/references/version-notes.md`) — add a row for the new release; keep old rows.
   - `templates/agent-version-protocol.md` only if a rule changes (e.g. HIPAA adopts a new X12 version).
3. Run:
   ```bash
   python3 .github/scripts/build.py
   python3 .github/scripts/content_lint.py
   python3 -m unittest discover -s tests
   ```
4. Bump `version` in `plugins/healthcare/plugin.json` when packaged content changed (CI enforces this), then rebuild.
5. PR title: `catalog: <standard> <change>`; link the source issue.

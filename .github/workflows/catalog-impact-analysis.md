---
name: Catalog Impact Analysis
description: When standards/catalog.json changes on main, finds agents, instructions, skills, docs and examples whose content is now inconsistent with the catalog and opens one issue with a checklist of required edits.
on:
  push:
    branches: [main]
    paths:
      - "standards/catalog.json"
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  copilot-requests: write
checkout:
  fetch-depth: 2
tools:
  github:
    toolsets: [repos, issues]
  bash: ["cat", "ls", "grep", "head", "jq", "git diff:*", "git log:*", "git show:*"]
timeout-minutes: 20
safe-outputs:
  create-issue:
    title-prefix: "[catalog-impact] "
    labels: [catalog-impact, needs-review]
    max: 1
  noop:
---

# Catalog Impact Analysis

`standards/catalog.json` is the single source of truth for **published** and **mandated** versions. When it changes, other content must stay consistent with it.

## Steps

1. Run `git diff HEAD~1 HEAD -- standards/catalog.json` and list each changed standard id and field.
2. For each change, search with `grep -rn` (exclude `dist/` and generated `docs/README.*.md`) for content that restates the old value or now conflicts:
   - `README.md` (research baseline table), `docs/*.md`
   - `agents/`, `instructions/`, `skills/**` (especially `references/` version tables)
   - `templates/healthcare-profile.yml` comments, `templates/agent-version-protocol.md`
   - `examples/` (only if an example claims to represent a version that changed status, e.g. retired)
3. Classify each hit:
   - **Must update** — states the old latest/mandated value as current fact.
   - **Review** — guidance that may need a new version delta row (e.g. a new FHIR or DICOM release adds/changes elements).
   - **OK** — mentions an older version deliberately as a *target example* (that is fine and must not be "upgraded").
4. If nothing needs changing, call `noop`.

## Issue

Title: `Catalog changed in <short sha> — content alignment`

- What changed in the catalog (table).
- Checklist grouped by file: `- [ ] path:line — what to change (must update / review)`.
- Reminder: run `python3 .github/scripts/build.py`, bump the `version` in `plugins/healthcare/plugin.json`.

---
name: Standards Baseline Watch
description: Monthly check of official publisher pages for new editions, releases, IG versions and regulatory milestones; opens one issue proposing standards/catalog.json updates and resolutions for verify:true entries, without changing any project's target versions.
on:
  schedule: monthly
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  copilot-requests: write
imports:
  - shared/standards-sources.md
tools:
  github:
    toolsets: [repos, issues]
  bash: ["cat", "ls", "grep", "head", "jq"]
timeout-minutes: 30
safe-outputs:
  create-issue:
    title-prefix: "[standards-watch] "
    labels: [standards-catalog, needs-review]
    max: 1
    close-older-issues: true
  noop:
---

# Standards Baseline Watch

You maintain the **published / mandated** facts in `standards/catalog.json` for this healthcare repository. Read `.github/skills/catalog-update/SKILL.md` and follow its rules.

## Tasks

1. Read `standards/catalog.json` (read the file, or use `jq` to list ids, `latestPublished` and `verify` flags). For every standard, fetch its `sources` and determine whether there is a newer publication, edition, release, IG version or regulatory milestone than recorded in `latestPublished`, `knownVersions`, `implementationGuides`, `milestones` or `adoptedTransactionStandards`.
2. For every entry or sub-entry with `"verify": true`, try to confirm or correct it from an official source.
3. Check open issues labelled `standards-catalog` so you don't re-propose something already tracked.

## Rules

- The catalog records what is **published** and what is **mandated**; projects choose their **targets** in `healthcare-profile.yml`. Never recommend that resources or users move to a newer version just because it exists.
- Regulatory items (HIPAA adopted standards, CMS/NCPDP compliance dates) go in a separate section marked **needs compliance review**.
- Only report changes you can cite with a URL and a publication date.
- If nothing changed and no `verify:true` item can be resolved, call `noop`.

## Issue format

Title: `Catalog update proposals — <YYYY-MM>`

1. **Summary** — counts of proposed changes, resolved verifications, regulatory items.
2. **Proposed catalog edits** — table: standard id · JSON field · current · proposed · source URL · publication date.
3. **verify:true resolutions** — table: standard id · claim · verdict (confirmed / corrected / still unverifiable) · source.
4. **Regulatory (needs compliance review)** — same table format.
5. **Likely affected resources** — files that mention the changed standard (use `grep -ril <keyword> agents instructions skills docs README.md`).
6. A task list for the maintainer: "- [ ] Apply with the `catalog-update` skill".

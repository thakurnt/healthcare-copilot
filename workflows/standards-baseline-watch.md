---
name: 'Standards Baseline Watch'
description: 'Monthly agentic workflow that checks publisher pages listed in standards/catalog.json for new editions, releases or regulatory milestones and opens an issue proposing catalog updates — without changing project targets.'
on:
  schedule: monthly
  workflow_dispatch:
permissions:
  contents: read
  issues: read
safe-outputs:
  create-issue:
    title-prefix: "[standards-watch] "
    labels: [standards-catalog, needs-review]
tools:
  web-fetch:
---

# Standards Baseline Watch

Read `standards/catalog.json`. For each standard, fetch the URLs in `sources` and determine whether a newer publication, edition, release, IG version or regulatory milestone exists than `latestPublished` / `milestones`.

Rules:
- Only report changes you can cite with a URL and a publication date.
- Never propose changing any project's target version: the catalog records what is **published**; projects declare what they **use** in `healthcare-profile.yml`.
- Flag regulatory items (HIPAA adopted standards, CMS/NCPDP compliance dates) separately, marked "needs compliance review".
- If nothing changed, do not create an issue.

Create one issue summarising proposed catalog edits as a table: standard id, field, current value, proposed value, source URL, notes.

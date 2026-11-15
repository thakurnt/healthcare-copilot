---
name: Resource Staleness Report
description: Monthly report of agents, instructions and skills that have not been substantively updated since the standards they cover changed in the catalog, with a deeper review of the five most at-risk resources.
on:
  schedule: monthly
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  copilot-requests: write
checkout:
  fetch-depth: 0
tools:
  github:
    toolsets: [repos, issues]
  bash: ["cat", "ls", "grep", "head", "date", "find", "git log:*", "git show:*"]
timeout-minutes: 25
safe-outputs:
  create-issue:
    title-prefix: "[staleness] "
    labels: [staleness]
    max: 1
    close-older-issues: true
  noop:
---

# Resource Staleness Report

In this repository age alone is not the risk — **drift from the standards catalog** is.

## Steps

1. For each resource (`agents/*.agent.md`, `instructions/*.instructions.md`, `skills/*/` folders), find the date of the last substantive change: `git log -1 --format="%H %ai" --diff-filter=AM -- <path>`. Ignore commits whose messages indicate formatting, renames or regenerated output.
2. Map each resource to the catalog standard ids it covers (by its name/description/body keywords: dicom, dicomweb, hl7v2, fhir, cda, ccda, ihe, x12, hipaa, ncpdp, ieee11073, terminology).
3. Find when the catalog entry for each of those standards last changed: `git log -1 --format="%ai" -S'"id": "<id>"' -- standards/catalog.json` plus `git log -1 --format=%ai -- standards/catalog.json`.
4. Classify:
   - 🔴 **Drifted** — the resource has not changed since a catalog change to a standard it covers.
   - 🟡 **Aging** — no substantive change in more than 180 days.
   - Otherwise omit.
5. For the **five** most at-risk resources, read them and judge: *materially outdated*, *needs version-delta additions*, or *still accurate*; list concrete issues.
6. If nothing is drifted or aging, call `noop`.

## Issue

Title: `Resource staleness — <YYYY-MM>` with sections: Summary counts · Drifted table (resource · standards · resource last changed · catalog last changed) · Aging table · Deep review (5 items with verdict and actions).

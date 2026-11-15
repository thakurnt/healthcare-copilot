---
name: Content Accuracy Audit
description: Weekly rotating fact-check of three agents/skills/instructions; verifies version-specific claims against official publisher sources using the standards-fact-check skill and opens one issue with contradicted or unverifiable claims.
on:
  schedule: weekly
  workflow_dispatch:
    inputs:
      paths:
        description: "Optional space-separated resource paths to audit instead of the weekly rotation"
        required: false
permissions:
  contents: read
  issues: read
  copilot-requests: write
imports:
  - shared/standards-sources.md
tools:
  github:
    toolsets: [repos, issues]
  bash: ["cat", "ls", "grep", "head", "sed", "wc", "date", "find", "sort"]
timeout-minutes: 40
safe-outputs:
  create-issue:
    title-prefix: "[accuracy] "
    labels: [content-accuracy, needs-review]
    max: 1
  noop:
---

# Content Accuracy Audit

You audit healthcare engineering guidance for factual accuracy. Follow `.github/skills/standards-fact-check/SKILL.md` exactly — it defines what a claim is, how to verify it and the verdict vocabulary.

## Select resources

- If the `paths` input was provided, audit exactly those.
- Otherwise list the files with `find agents instructions skills -type f \( -name '*.agent.md' -o -name '*.instructions.md' -o -name 'SKILL.md' -o -path '*/references/*.md' \) | sort` and number them from 0 to N-1. Take the ISO week number `W` (`date +%V`) and audit the items at indexes `(3W) mod N`, `(3W+1) mod N`, `(3W+2) mod N` (do the arithmetic yourself). This rotation covers the whole repository over time.

## Audit

For each selected file, extract **version-specific factual claims** (e.g. "X was introduced in v2.5", "R5 renamed Encounter.period to actualPeriod", "TR3 005010X222A1 is the 837P guide", template IDs, UIDs, transfer syntax UIDs, compliance dates). Verify up to 8 claims per file, prioritising those most likely to mislead an engineer working on an **older** version.

Also flag:
- statements that apply a newer version's behaviour to all versions without qualification;
- invented-looking identifiers (OIDs, UIDs, codes, field numbers) that you cannot find in the cited version.

## Output

If every checked claim is **verified**, call `noop` with a one-line summary.

Otherwise create one issue titled `Accuracy audit — week <W>`:

1. **Resources audited** — list with claim counts.
2. **Findings** — table: file:line · claim (short quote) · verdict (`contradicted` / `unverifiable` / `needs-qualification`) · correct statement for which version(s) · source URL.
3. **Suggested edits** — minimal diff-style suggestions per file (do not rewrite whole sections).
4. A task list so maintainers can tick items off.

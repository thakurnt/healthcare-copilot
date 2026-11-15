# Repository automation

How healthcare-copilot keeps its content **aligned** (consistent with the standards catalog and itself), **verified** (facts checked against official sources) and **validated** (structure, rules and scripts tested), and how this design maps to [github/awesome-copilot](https://github.com/github/awesome-copilot).

## 1. How awesome-copilot automates itself (analysis, Nov 2026)

awesome-copilot uses three layers:

| Layer | What it is | Examples in awesome-copilot |
|---|---|---|
| **Deterministic CI** (GitHub Actions YAML, action SHAs pinned) | Hard gates on structure and generated output | `validate-skills.yml`, `validate-plugins.yml`, `validate-readme.yml`, `check-plugin-structure.yml`, `check-line-endings.yml`, `codespell.yml`, `publish.yml` (materialises plugins to a `marketplace` branch) |
| **Agentic workflows** ([gh-aw](https://github.github.com/gh-aw)) — `.github/workflows/*.md` compiled to `*.lock.yml` | AI judgement, **advisory only**, read-only permissions + `copilot-requests: write`, all writes via `safe-outputs` (`create-issue` with `close-older-issues`, `add-comment` with `hide-older-comments`, `noop`) | `resource-staleness-report.md` (weekly), `duplicate-resource-detector.md` (weekly), `pr-quality-signal.md` (PR advisory), `pr-duplicate-check.md`, `learning-hub-updater.md`, content-sync workflows |
| **Maintainer tooling for agents** | Customisations the maintainers' Copilot uses on the repo itself | `.github/agents/agentic-workflows.md` (gh-aw dispatcher; loads `.github/aw/instructions.md` overlay), `.github/skills/` (`agentic-workflows`, `code-review`), `copilot-setup-steps.yml` (installs gh-aw for the coding agent), `.github/aw/actions-lock.json` |
| **Review policy** | Risk routing for a large contributor base | `risk-tiers.yml`, `review-routing.yml`, `submission-gate.yml`, CODEOWNERS |

Key patterns adopted here: deterministic gates block, AI only advises; one issue per report with `close-older-issues`; `noop` when nothing to say; shared skills used by both humans and workflows; generated artifacts checked for drift in CI; pinned action SHAs.

Patterns **not** adopted (yet): risk tiers/submission gate (single-maintainer repo — CODEOWNERS is enough), a separate `marketplace` publishing branch (we commit `dist/` on `main` so `copilot plugin marketplace add` works directly), website generation.

## 2. What we added for healthcare content

Healthcare content has a risk awesome-copilot doesn't: **factual errors about specific standard versions** (wrong field, wrong release, wrong mandate) that mislead engineers working on older systems. So the AI layer focuses on *verification against official publishers*, and the deterministic layer enforces *version-awareness rules*.

### Deterministic (blocking)

| Workflow | Trigger | Checks |
|---|---|---|
| `validate.yml` → `validate` | PR, push to main | `build.py --check` (frontmatter, names, plugin refs, generated docs / `dist/plugins` / marketplace in sync) · `content_lint.py` (HC001–HC007, see below) · JSON well-formed · `unittest` suite for skill scripts, installer and tooling |
| `validate.yml` → `plugin-versions` | PR | Packaged plugin content changed ⇒ `version` bumped (`check_plugin_versions.py`); `build.py` also fails if any agent/skill is missing from the `healthcare` plugin |
| `source-link-check.yml` | Weekly, PR touching catalog | Every catalog `sources` URL reachable (`check_sources.py`), table in job summary |
| `copilot-setup-steps.yml` | Manual / on change | Python + gh-aw CLI for the Copilot coding agent |

Content lint rules (`.github/scripts/content_lint.py`):

| Code | Rule |
|---|---|
| HC001 | Every agent has a "Version first" section |
| HC002 | Relative Markdown links resolve |
| HC003 | Skills/agents referenced by agents exist |
| HC004 | No "use/target/assume the latest release" guidance |
| HC005 | Skill/hook scripts import only the standard library |
| HC006 | Examples carry synthetic markers (HL7 PID, X12 member, DICOM PatientName) |
| HC007 | Catalog sources are https |
| HC008 | Skills are tool-first: a bundled script is optional (`## Optional script`, compatibility says so) |
| HC101/102 | Warnings: catalog baseline age, remaining `verify:true` entries |

### Agentic (advisory, gh-aw)

| Workflow | Trigger | Output | Purpose |
|---|---|---|---|
| `standards-baseline-watch.md` | Monthly + manual | 1 issue (`standards-catalog`), closes older | New editions/releases/IG versions/regulatory milestones; resolves `verify:true` |
| `catalog-impact-analysis.md` | Push to main touching `standards/catalog.json` | 1 issue (`catalog-impact`) | Checklist of content now inconsistent with the catalog |
| `content-accuracy-audit.md` | Weekly rotation (3 resources) + manual `paths` | 1 issue (`content-accuracy`) | Fact-checks version-specific claims with sources |
| `pr-standards-review.md` | PRs touching content | 1 advisory comment + labels | Version-awareness, fact spot-checks, PHI, spec-kind labelling |
| `resource-staleness-report.md` | Monthly | 1 issue (`staleness`), closes older | Resources not updated since their standards changed in the catalog |

All import `shared/standards-sources.md` where web access is needed: `web-fetch` restricted by `network.allowed` to official publishers (DICOM/NEMA, HL7, IHE, X12, CMS, eCFR, NCPDP, IEEE, SNOMED, LOINC, NLM, UCUM, WHO).

Consumer-facing workflow (in `workflows/`, for projects that *use* Healthcare Copilot): `healthcare-version-drift.md` compares a project's `healthcare-profile.yml` with version evidence in its code.

### Maintainer agent & skills

| Resource | Used by |
|---|---|
| `.github/agents/healthcare-content-maintainer.agent.md` | Maintainers in Copilot Chat / coding agent — triages automation issues into PRs |
| `.github/skills/standards-fact-check` | Maintainers **and** `pr-standards-review`, `content-accuracy-audit` |
| `.github/skills/catalog-update` | Maintainers **and** `standards-baseline-watch` |
| `.github/skills/resource-authoring` (+ `new_resource.py` scaffold) | Maintainers adding resources |
| `.github/aw/instructions.md` | Overlay rules when authoring gh-aw workflows |

## 3. The loop

```
 publisher sites ──▶ Standards Baseline Watch ──▶ issue ──▶ maintainer agent + catalog-update ──▶ PR
                                                                          │
 PR ──▶ validate (blocking) + PR Standards Review (advisory) ──▶ merge ──▶ Catalog Impact Analysis ──▶ issue ──▶ PR
                                                                          │
 weekly ──▶ Content Accuracy Audit ──▶ issue ──▶ PR          monthly ──▶ Staleness Report ──▶ issue ──▶ PR
```

Issues can be assigned to **Copilot** (coding agent) to draft the fix PR; the `healthcare-content-maintainer` agent and `copilot-setup-steps.yml` give it the right context and tools.

## 4. One-time setup

```bash
# 1. GitHub CLI + gh-aw extension
brew install gh            # or see https://cli.github.com
gh auth login
gh extension install github/gh-aw

# 2. Compile agentic workflows (creates .github/workflows/*.lock.yml) and commit them
gh aw compile
git add .github/workflows && git commit -m "Compile agentic workflows" && git push

# 3. Verify
gh aw status
gh aw run content-accuracy-audit      # manual trial run
```

Then in the repository settings:

- **Copilot / AI engine auth** — follow the gh-aw docs for the Copilot engine on your plan (the workflows request `copilot-requests: write`; if your setup requires a token secret instead, add it as the docs describe and re-run `gh aw compile`).
- **Actions → General → Workflow permissions**: allow GitHub Actions to create issues and pull request comments (safe-outputs need this).
- **Branch protection on `main`**: require the `validate` and `plugin-versions` checks and CODEOWNERS review.
- **Labels** are created on first use: `standards-catalog`, `needs-review`, `catalog-impact`, `content-accuracy`, `staleness`, `needs-fact-check`, `version-awareness`, `phi-risk`, `catalog-change`.

## 5. Local commands

```bash
python3 .github/scripts/build.py              # regenerate docs, dist/plugins, marketplace
python3 .github/scripts/content_lint.py       # content rules
python3 -m unittest discover -s tests -v      # tests
python3 .github/scripts/check_sources.py      # catalog link check
python3 .github/scripts/check_plugin_versions.py --base origin/main
python3 .github/skills/resource-authoring/scripts/new_resource.py skill my-skill "Use when ..."
```

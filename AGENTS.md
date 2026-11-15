# AGENTS.md

## Project overview

**Healthcare Copilot** is a reusable healthcare interoperability engineering framework for GitHub Copilot, Claude Code and other agent tools that support agents, instructions and [Agent Skills](https://agentskills.io/specification). It follows the structure of [github/awesome-copilot](https://github.com/github/awesome-copilot).

Its defining rule: **every resource is version-aware**. Nothing assumes the newest standard release; targets are resolved per project (`healthcare-profile.yml`), per interface and per implementation guide. See `docs/version-strategy.md`.

## Repository structure

```
.
├── agents/        # Custom agents (*.agent.md)
├── instructions/  # Scoped guidance (*.instructions.md, applyTo globs)
├── skills/        # Agent Skills (<name>/SKILL.md + scripts/, references/, assets/)
├── hooks/         # Session hooks (<name>/README.md + hooks.json + scripts)
├── workflows/     # GitHub Agentic Workflows (*.md)
├── plugins/       # plugins/healthcare/plugin.json — the single installable plugin (source)
├── standards/     # catalog.json — published / mandated versions (NOT targets)
├── templates/     # healthcare-profile.yml for consuming projects
├── examples/      # Synthetic sample artifacts across old and new versions
├── docs/          # Strategy docs + generated README.*.md indexes
├── scripts/       # install.py (Copilot / Claude Code installer)
├── dist/plugins/  # GENERATED installable plugins (do not edit)
├── .schemas/      # JSON Schemas (profile, catalog)
└── .github/scripts/build.py  # validate + generate docs
```

## Setup commands

```bash
python3 .github/scripts/build.py          # validate + regenerate docs, dist/plugins and .github/plugin/marketplace.json
python3 .github/scripts/build.py --check  # CI mode
python3 skills/healthcare-version-detect/scripts/detect_versions.py examples
```

Repository tooling needs Python 3.8+ (standard library only). **Skills must not**: users may have no Python, so every skill works with the agent's built-in search/read tools and bundled scripts are optional accelerators.

## Resource requirements

- **Agents** (`agents/*.agent.md`): `description` required; `name` and `tools` recommended; kebab-case file names. Body must include a "Version first" step.
- **Instructions** (`instructions/*.instructions.md`): `description` and `applyTo` required.
- **Skills** (`skills/<name>/SKILL.md`): `name` equals folder name (≤64 chars, kebab-case); `description` 10–1024 chars; reference bundled assets from SKILL.md. Tool-first: the default procedure uses built-in search/read tools; a bundled script is optional, documented under an `## Optional script` section, stdlib-only, and must not print PHI (HC008).
- **Hooks**: `README.md` with `name`, `description`, `tags`; `hooks.json`.
- **Workflows**: `name`, `description`, gh-aw frontmatter.
- **Plugins**: `plugin.json` with `$schema`, `name` (= folder), `description`, `version`; content under `extensions.com.github.awesome-copilot`.
- **Catalog**: every new standard needs `versioning`, `versionDetection` and `sources`; mark unverified facts `"verify": true`.

## Content rules

1. Version-specific statements name the version ("in v2.5+", "R4 only", "from DICOM 2023 editions").
2. Never invent field numbers, UIDs, OIDs, template IDs or codes.
3. Distinguish technical standards, integration profiles, IGs, legal obligations and terminologies.
4. Synthetic data only — no PHI anywhere (the `phi-scanner` hook helps).
5. No licensed content (SNOMED CT, CPT, full X12/NCPDP specs) committed.

## Before a PR

```bash
python3 .github/scripts/build.py           # regenerate docs, dist/plugins, marketplace
python3 .github/scripts/content_lint.py    # HC001-HC007 content rules
python3 -m unittest discover -s tests      # script + tooling tests
```

Bump `version` in `plugins/healthcare/plugin.json` when packaged content changed (CI enforces it). Every agent and skill must be listed there (the build fails otherwise).

## Maintainer automation

- Maintainer agent: `.github/agents/healthcare-content-maintainer.agent.md`; skills in `.github/skills/` (`standards-fact-check`, `catalog-update`, `resource-authoring`).
- Agentic workflows (gh-aw): `.github/workflows/*.md` → run `gh aw compile` after editing and commit the `.lock.yml`. Rules: `.github/aw/instructions.md`.
- Full description: `docs/maintainers/automation.md`.

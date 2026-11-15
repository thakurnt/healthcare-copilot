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
├── plugins/       # Installable bundles (<name>/plugin.json) by business domain
├── standards/     # catalog.json — published / mandated versions (NOT targets)
├── templates/     # healthcare-profile.yml for consuming projects
├── examples/      # Synthetic sample artifacts across old and new versions
├── docs/          # Strategy docs + generated README.*.md indexes
├── scripts/       # install.py (Copilot / Claude Code installer)
├── .schemas/      # JSON Schemas (profile, catalog)
└── .github/scripts/build.py  # validate + generate docs
```

## Setup commands

```bash
python3 .github/scripts/build.py          # validate + regenerate docs/README.*.md
python3 .github/scripts/build.py --check  # CI mode
python3 skills/healthcare-version-detect/scripts/detect_versions.py examples
```

No third-party dependencies (Python 3.8+ standard library only).

## Resource requirements

- **Agents** (`agents/*.agent.md`): `description` required; `name` and `tools` recommended; kebab-case file names. Body must include a "Version first" step.
- **Instructions** (`instructions/*.instructions.md`): `description` and `applyTo` required.
- **Skills** (`skills/<name>/SKILL.md`): `name` equals folder name (≤64 chars, kebab-case); `description` 10–1024 chars; reference bundled assets from SKILL.md; scripts must be stdlib-only and must not print PHI.
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

Run `python3 .github/scripts/build.py`, commit regenerated docs, and test any script against `examples/`.

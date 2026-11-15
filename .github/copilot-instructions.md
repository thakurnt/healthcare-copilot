This repository authors healthcare Copilot resources. Follow AGENTS.md and use the `Healthcare Content Maintainer` agent (.github/agents) for repository maintenance.

Key rules: every agent/skill resolves the target standard version (never assume latest); version facts live in references tables and standards/catalog.json; synthetic data only; never hand-edit generated files (docs/README.*.md, dist/, .github/plugin/marketplace.json).

Before finishing: `python3 .github/scripts/build.py && python3 .github/scripts/content_lint.py && python3 -m unittest discover -s tests`, and bump plugin versions for changed plugins.

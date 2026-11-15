# Contributing

Thanks for helping make healthcare engineering safer and faster.

1. Read [AGENTS.md](AGENTS.md) and [docs/version-strategy.md](docs/version-strategy.md).
2. Add your resource in the right folder with valid frontmatter.
3. Make it **version-aware**: a "Version first" step, version deltas in `references/`, synthetic examples for at least one older and one newer version where relevant.
4. Run `python3 .github/scripts/build.py` and commit the regenerated `docs/README.*.md`.
5. Open a PR using the template.

Catalog updates (`standards/catalog.json`) need a source URL and publication date. Regulatory items need a reviewer with compliance context.

# Repository overlay for agentic workflow authoring (gh-aw)

Applies when creating or editing `.github/workflows/*.md` in healthcare-copilot.

- **Read-only by default.** `permissions` stay read-only (+ `copilot-requests: write`). All writes go through `safe-outputs` with `max` set; prefer `create-issue` (with `close-older-issues` for recurring reports) or `add-comment` with `hide-older-comments`.
- **Always `noop`** when there is nothing to report — no empty issues.
- **Fact-checking workflows** must `import: shared/standards-sources.md` (official publisher allowlist + source policy) and follow `.github/skills/standards-fact-check/SKILL.md`. Do not widen `network.allowed` in individual workflows.
- **Never** let a workflow change target-version guidance or "upgrade" examples; the catalog records published/mandated facts only.
- **Never** emit PHI or licensed specification text in outputs.
- **Tool-first.** Workflows use the agent's built-in tools — GitHub MCP toolsets, `web-fetch`, and read-only shell commands (`grep`/`rg`, `find`, `cat`, `head`, `jq`, `git log/diff/show`). Don't run repository Python scripts or `python3 -c` from an agentic workflow, and don't add the `python` network ecosystem (HC009).
- **Don't duplicate CI.** Deterministic checks (build, lint, tests) run in Actions YAML; an agentic workflow reads their results through the `actions` toolset instead of re-running them.
- **Self-contained for consumers.** Workflows in `workflows/` run in other teams' repos, which may have installed Healthcare Copilot as a plugin (no `.github/skills/` files) — embed the patterns they need.
- Patterns in workflow bodies go in lists, not Markdown tables (table escaping turns `|` into `\|` and breaks regexes).
- After editing: `gh aw compile` and commit both the `.md` and generated `.lock.yml`.

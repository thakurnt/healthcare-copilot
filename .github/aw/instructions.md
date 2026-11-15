# Repository overlay for agentic workflow authoring (gh-aw)

Applies when creating or editing `.github/workflows/*.md` in healthcare-copilot.

- **Read-only by default.** `permissions` stay read-only (+ `copilot-requests: write`). All writes go through `safe-outputs` with `max` set; prefer `create-issue` (with `close-older-issues` for recurring reports) or `add-comment` with `hide-older-comments`.
- **Always `noop`** when there is nothing to report — no empty issues.
- **Fact-checking workflows** must `import: shared/standards-sources.md` (official publisher allowlist + source policy) and follow `.github/skills/standards-fact-check/SKILL.md`. Do not widen `network.allowed` in individual workflows.
- **Never** let a workflow change target-version guidance or "upgrade" examples; the catalog records published/mandated facts only.
- **Never** emit PHI or licensed specification text in outputs.
- Narrow `bash` allowlists to the repository's scripts and read-only commands.
- After editing: `gh aw compile` and commit both the `.md` and generated `.lock.yml`.

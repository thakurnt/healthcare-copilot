---
name: resource-authoring
description: 'Create a new Healthcare Copilot agent, instruction or skill that follows repository conventions and the version-awareness contract, using the bundled scaffold script, then wire it into plugins and regenerate packaged output. Use when adding or substantially reworking a resource.'
license: MIT
compatibility: 'Python 3.8+ standard library only.'
metadata:
  version: "1.0"
---

# Resource Authoring

## Scaffold
```bash
python3 .github/skills/resource-authoring/scripts/new_resource.py agent  ncpdp-script-inspector "One-sentence description …"
python3 .github/skills/resource-authoring/scripts/new_resource.py skill  mllp-troubleshooting  "Use when …"
python3 .github/skills/resource-authoring/scripts/new_resource.py instruction ncpdp-script "…" --apply-to '**/*ncpdp*/**'
```

## Version-awareness contract (CI-enforced where possible)
- Agents: a `## Version first` section that resolves the target version per `instructions/healthcare-version-resolution.instructions.md` (HC001).
- Never direct readers to "use the latest" release (HC004).
- Version facts live in `references/*.md` tables with explicit version columns; phrase as "introduced/changed/removed in vX".
- Scripts: stdlib-only (HC005), read-only, never print message content/PHI by default.
- Examples: synthetic, with TEST markers (HC006), in a folder named for the version (`examples/<standard>/<version>/`). Add at least one **older** version example when relevant.
- Distinguish technical standard / integration profile / IG / legal / terminology.

## Wire up
1. Add the resource to `plugins/healthcare/plugin.json` (`extensions.com.github.awesome-copilot.agents|skills`) and bump its `version` (the build fails if an agent or skill is in no plugin).
2. `python3 .github/scripts/build.py && python3 .github/scripts/content_lint.py && python3 -m unittest discover -s tests`.
3. If you added a script, add a test in `tests/test_tooling.py`.
4. Use the `standards-fact-check` skill on your own claims before opening the PR.

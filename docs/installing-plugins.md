# Installing Healthcare Copilot plugins (GitHub Copilot)

This repository is a **Copilot plugin marketplace** named `healthcare-copilot`. The manifest is
[`.github/plugin/marketplace.json`](../.github/plugin/marketplace.json); the packaged plugins live in
[`dist/plugins/`](../dist/plugins).

## One plugin: `healthcare`

A single plugin installs **all 12 agents and 11 skills**, covering imaging (DICOM/DICOMweb/PACS), clinical interop (HL7 v2, FHIR, CDA/C-CDA), IHE, revenue cycle (X12, NCPDP, HIPAA), medical devices (IEEE 11073), terminology, security/privacy and conformance testing. See [README.agents.md](README.agents.md) and [README.skills.md](README.skills.md).

---

## Option 1 — GitHub Copilot CLI

**Prerequisite:** a current [Copilot CLI](https://docs.github.com/copilot/how-tos/set-up/install-copilot-cli) and a Copilot subscription.

```bash
# 1. Register the marketplace (once per machine)
copilot plugin marketplace add thakurnt/healthcare-copilot

# 2. Install everything
copilot plugin install healthcare@healthcare-copilot
```

Inside an interactive `copilot` session you can also browse:

```
/plugin marketplace browse healthcare-copilot
```

**Update** later (pulls the latest `main`):

```bash
copilot plugin marketplace update healthcare-copilot
copilot plugin update healthcare@healthcare-copilot
```

**Remove:**

```bash
copilot plugin uninstall healthcare@healthcare-copilot
```

> Run `copilot plugin --help` if a sub-command differs in your CLI version — plugin commands are still evolving.

## Option 2 — VS Code (Copilot Chat agent plugins)

1. Add the marketplace in **settings.json**:
   ```jsonc
   "chat.plugins.marketplaces": [
     "thakurnt/healthcare-copilot"
   ]
   ```
2. Open the Extensions view and search `@agentPlugins`, **or** run **Chat: Plugins** from the Command Palette.
3. Install `healthcare`.
4. Pick an agent (e.g. *DICOM Imaging Engineer*) from the agent dropdown in Copilot Chat.

> Agent plugins in VS Code may require a recent VS Code / Copilot Chat version and, in organisations, an admin policy that allows plugins. If the setting name differs in your build, search settings for "plugins marketplaces".

## Option 3 — Copy into a repository (works everywhere, incl. Copilot coding agent)

Use this when plugins aren't available or allowed in your environment, or when you want the resources **versioned with your project** (they then apply to everyone on the team and to the Copilot coding agent).

```bash
git clone https://github.com/thakurnt/healthcare-copilot.git
python3 healthcare-copilot/scripts/install.py /path/to/your-project --tool copilot
```

This writes `.github/agents/`, `.github/instructions/`, `.github/skills/`, `.github/hooks/` and a starter
`.github/healthcare-profile.yml`. Add `--dry-run` to preview, `--tool both` to also set up Claude Code.

---

## After installing — required steps

### 1. Declare your versions (important)

Plugins don't decide which standard versions you target — **your project does**. Create
`.github/healthcare-profile.yml` in your project:

- Ask in Copilot Chat: **"Detect which healthcare standard versions this repo uses and draft a healthcare profile"** —
  the `healthcare-version-detect` skill scans your code and samples and drafts the file from its bundled template, or
- copy [`templates/healthcare-profile.yml`](../templates/healthcare-profile.yml) and edit it.

Example: DICOM `2024e`, HL7 v2 `2.3.1` (ADT feed) and `2.5.1` (orders), FHIR `R4` + US Core `6.1.0`, X12 `005010`.
Every version-dependent answer starts with a `Target:` line — if it is wrong, fix the profile.

### 2. (Optional) Add the instructions

Plugins carry **agents and skills**. Each packaged agent already embeds the version-resolution protocol, but plain Copilot Chat
(without selecting an agent) and file-scoped guidance come from **instructions**, which plugins don't install. To add them:

```bash
mkdir -p .github/instructions
cp healthcare-copilot/instructions/*.instructions.md .github/instructions/
```

(or use Option 3, which does this for you).

### 3. (Optional) Add the PHI scanner hook

Hooks are installed per repository, not via plugins:

```bash
mkdir -p .github/hooks
cp -R healthcare-copilot/hooks/phi-scanner .github/hooks/
chmod +x .github/hooks/phi-scanner/scan-phi.sh
```

Commit it to your default branch; it runs at the end of Copilot coding agent sessions. Set `SCAN_MODE=block` in
`hooks.json` to fail the session on findings.

---

## What gets installed

| Included in plugins | Not included (install per repo) |
|---|---|
| Agents (with embedded version-resolution protocol) | Instructions (`*.instructions.md`) |
| Skills with their scripts, references and assets | Hooks (`phi-scanner`) |
| | Your `healthcare-profile.yml` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `marketplace not found` / `unknown marketplace` | Run `copilot plugin marketplace add thakurnt/healthcare-copilot` first; use the `@healthcare-copilot` suffix. |
| You installed the earlier domain plugins (`healthcare-core`, `healthcare-imaging`, …) | Uninstall them (`copilot plugin uninstall healthcare-imaging@healthcare-copilot`, etc.), run `copilot plugin marketplace update healthcare-copilot`, then install `healthcare`. |
| Plugin installs but agents don't show | Restart the Copilot CLI session / reload VS Code; check `copilot plugin list`. |
| Answers assume the latest version | Add or fix `.github/healthcare-profile.yml`; mention the version in your prompt. |
| Skill scripts fail | They need Python 3.8+ on `PATH` (standard library only). |
| Corporate environment blocks plugins | Use Option 3 (copy into the repository). |

## For maintainers — publishing changes

Plugins are packaged from the source folders (`agents/`, `skills/`, `plugins/*/plugin.json`):

```bash
python3 .github/scripts/build.py      # regenerates dist/plugins/ and .github/plugin/marketplace.json
git add -A && git commit -m "..." && git push
```

Bump `version` in `plugins/healthcare/plugin.json` when content changes so users get the update. CI (`build.py --check`) fails if
`dist/` is out of date.

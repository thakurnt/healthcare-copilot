#!/usr/bin/env python3
"""Install Healthcare Copilot resources into a target project for GitHub Copilot,
Claude Code, or both.

    python3 scripts/install.py /path/to/project --tool copilot
    python3 scripts/install.py /path/to/project --tool claude
    python3 scripts/install.py /path/to/project --tool both --dry-run

Installs everything in the single `healthcare` plugin (all agents, skills, instructions, hooks).

Layout written
  copilot: .github/agents/*.agent.md, .github/instructions/*.instructions.md,
           .github/skills/<skill>/, .github/hooks/<hook>/
  claude : .claude/agents/<agent>.md (name/description frontmatter),
           .claude/skills/<skill>/, .claude/healthcare/instructions/*.md
           + a managed import block in CLAUDE.md
  both   : also copies templates/healthcare-profile.yml to .github/healthcare-profile.yml
           if the project has no profile yet.
Existing files are only overwritten with --force.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ALWAYS_INSTRUCTIONS = ["healthcare-version-resolution", "healthcare-phi-safety"]
BEGIN, END = "<!-- healthcare-copilot:begin -->", "<!-- healthcare-copilot:end -->"


def plugin_contents(names: list[str]) -> dict[str, set[str]]:
    out = {"agents": set(), "skills": set(), "hooks": set()}
    pdir = os.path.join(ROOT, "plugins")
    if names == ["all"]:
        names = sorted(os.listdir(pdir))
    for n in names:
        meta = json.load(open(os.path.join(pdir, n, "plugin.json")))
        comp = meta["extensions"]["com.github.awesome-copilot"]
        for k in out:
            out[k].update(os.path.normpath(p) for p in comp.get(k, []))
    return out


def copy(src: str, dst: str, force: bool, dry: bool) -> None:
    if os.path.exists(dst) and not force:
        print(f"  skip (exists) {dst}")
        return
    print(f"  write {dst}")
    if dry:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def write(dst: str, text: str, force: bool, dry: bool) -> None:
    if os.path.exists(dst) and not force:
        print(f"  skip (exists) {dst}")
        return
    print(f"  write {dst}")
    if not dry:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "w", encoding="utf-8").write(text)


def to_claude_agent(path: str) -> str:
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm, body = m.group(1), m.group(2)
    desc = re.search(r"^description:\s*(.*)$", fm, re.M).group(1).strip().strip("'\"")
    name = os.path.basename(path)[: -len(".agent.md")]
    desc = desc.replace('"', "'")
    return f'---\nname: {name}\ndescription: "{desc}"\n---\n{body}'


def all_instructions() -> list[str]:
    """All instruction files are small and scoped by applyTo, so every plugin installs them all."""
    return sorted(f[: -len(".instructions.md")] for f in os.listdir(os.path.join(ROOT, "instructions")))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--tool", choices=["copilot", "claude", "both"], default="copilot")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    plugins = ["all"]
    c = plugin_contents(plugins)
    instr = all_instructions()
    tools = ["copilot", "claude"] if a.tool == "both" else [a.tool]
    print(f"Installing Healthcare Copilot for {tools} into {proj}")

    for tool in tools:
        if tool == "copilot":
            for p in sorted(c["agents"]):
                copy(os.path.join(ROOT, p), os.path.join(proj, ".github", "agents", os.path.basename(p)), a.force, a.dry_run)
            for i in instr:
                f = f"{i}.instructions.md"
                copy(os.path.join(ROOT, "instructions", f), os.path.join(proj, ".github", "instructions", f), a.force, a.dry_run)
            for s in sorted(c["skills"]):
                copy(os.path.join(ROOT, s), os.path.join(proj, ".github", "skills", os.path.basename(s)), a.force, a.dry_run)
            for h in sorted(c["hooks"]):
                copy(os.path.join(ROOT, h), os.path.join(proj, ".github", "hooks", os.path.basename(h)), a.force, a.dry_run)
        else:
            for p in sorted(c["agents"]):
                name = os.path.basename(p)[: -len(".agent.md")]
                write(os.path.join(proj, ".claude", "agents", f"{name}.md"), to_claude_agent(os.path.join(ROOT, p)), a.force, a.dry_run)
            for s in sorted(c["skills"]):
                copy(os.path.join(ROOT, s), os.path.join(proj, ".claude", "skills", os.path.basename(s)), a.force, a.dry_run)
            for i in instr:
                f = f"{i}.instructions.md"
                copy(os.path.join(ROOT, "instructions", f), os.path.join(proj, ".claude", "healthcare", "instructions", f), a.force, a.dry_run)
            imports = "\n".join(
                f"@.claude/healthcare/instructions/{i}.instructions.md" for i in ALWAYS_INSTRUCTIONS
            )
            scoped = "\n".join(
                f"- `.claude/healthcare/instructions/{i}.instructions.md` (read when working on matching files)"
                for i in instr if i not in ALWAYS_INSTRUCTIONS
            )
            block = (
                f"{BEGIN}\n## Healthcare Copilot\n\nAlways follow these (they decide which standard version to target):\n\n"
                f"{imports}\n\nScoped guidance:\n{scoped}\n\nProject versions: `.github/healthcare-profile.yml`\n{END}\n"
            )
            cm = os.path.join(proj, "CLAUDE.md")
            existing = open(cm, encoding="utf-8").read() if os.path.exists(cm) else ""
            new = re.sub(re.escape(BEGIN) + ".*?" + re.escape(END) + "\n?", "", existing, flags=re.S).rstrip()
            new = (new + "\n\n" if new else "") + block
            print(f"  update {cm} (managed block)")
            if not a.dry_run:
                open(cm, "w", encoding="utf-8").write(new)

    prof_paths = [os.path.join(proj, ".github", "healthcare-profile.yml"), os.path.join(proj, "healthcare-profile.yml")]
    if not any(os.path.exists(p) for p in prof_paths):
        copy(os.path.join(ROOT, "templates", "healthcare-profile.yml"), prof_paths[0], False, a.dry_run)
        print("  -> edit .github/healthcare-profile.yml to declare the versions you actually use")
    return 0


if __name__ == "__main__":
    sys.exit(main())

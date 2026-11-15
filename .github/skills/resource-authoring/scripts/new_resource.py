#!/usr/bin/env python3
"""Scaffold a version-aware agent, skill or instruction.

Usage:
  new_resource.py agent NAME "DESCRIPTION"
  new_resource.py skill NAME "DESCRIPTION"
  new_resource.py instruction NAME "DESCRIPTION" --apply-to '**/*.hl7'
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

AGENT = """---
description: '{desc}'
name: '{title}'
tools: ['codebase', 'search', 'usages', 'problems', 'edit/editFiles', 'runCommands', 'web/fetch', 'findTestFiles']
---

# {title}

## Version first
- Resolve the target version of every standard in scope: request → `.github/healthcare-profile.yml` → artifact evidence → ask. Never assume the newest release.
- State it: *Target: <standard> <version> (from <source>)*.
- Only use features of that version; if a newer feature is needed, name the version that added it and give a compatible alternative.

## Expertise
- TODO

## Workflow
1. TODO

Use skills: `healthcare-version-detect`.
"""

SKILL = """---
name: {name}
description: '{desc}'
license: MIT
metadata:
  version: "1.0"
---

# {title}

## Steps
1. Resolve the target version(s) (profile → artifacts → ask). Do not assume the latest release.
2. TODO — use built-in search/read tools; give regex patterns. (If you add a script, document it under "## Optional script" and mark Python optional in `compatibility`.)
3. Report with a **Target** line first.

## Version notes
See [references/version-notes.md](references/version-notes.md).
"""

REF = """# {title} — version notes

> Orientation only — confirm each row in the publication for the target version.

| Version | Change relevant to this skill | Source |
|---|---|---|
| | | |
"""

INSTR = """---
description: '{desc}'
applyTo: '{apply_to}'
---

# {title}

Follow `healthcare-version-resolution.instructions.md` first.

- TODO (phrase version-specific rules as "in vX+ …")
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("type", choices=["agent", "skill", "instruction"])
    ap.add_argument("name")
    ap.add_argument("description")
    ap.add_argument("--apply-to", default="**")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.name) or len(a.name) > 64:
        sys.exit("name must be kebab-case, <= 64 chars")
    if not 10 <= len(a.description) <= 1024:
        sys.exit("description must be 10-1024 chars")
    title = " ".join(w.upper() if w in {"hl7", "fhir", "dicom", "x12", "ihe", "cda", "phi", "mllp"} else w.capitalize() for w in a.name.split("-"))
    desc = a.description.replace("'", "''")
    if a.type == "agent":
        out = {f"agents/{a.name}.agent.md": AGENT.format(desc=desc, title=title)}
    elif a.type == "skill":
        out = {f"skills/{a.name}/SKILL.md": SKILL.format(name=a.name, desc=desc, title=title),
               f"skills/{a.name}/references/version-notes.md": REF.format(title=title)}
    else:
        out = {f"instructions/{a.name}.instructions.md": INSTR.format(desc=desc, title=title, apply_to=a.apply_to)}
    for rel, text in out.items():
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            sys.exit(f"exists: {rel}")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(text)
        print(f"created {rel}")
    print("next: fill TODOs, add to plugins/*/plugin.json, run python3 .github/scripts/build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate repository resources and generate docs/README.*.md indexes.

Standard library only.
    python3 .github/scripts/build.py           # validate + regenerate docs
    python3 .github/scripts/build.py --check   # validate + fail if docs are stale (CI)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
errors: list[str] = []


def frontmatter(path: str) -> dict[str, str]:
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{rel(path)}: missing frontmatter")
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            data[km.group(1)] = km.group(2).strip().strip("'\"")
    return data


def rel(p: str) -> str:
    return os.path.relpath(p, ROOT)


def kebab(name: str) -> bool:
    return re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) is not None


def files(folder: str, suffix: str) -> list[str]:
    d = os.path.join(ROOT, folder)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(suffix))


def dirs(folder: str) -> list[str]:
    d = os.path.join(ROOT, folder)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if os.path.isdir(os.path.join(d, f)))


def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(c.replace("|", "\\|") for c in r) + " |" for r in rows]
    return "\n".join(out)


def collect() -> dict[str, str]:
    docs: dict[str, str] = {}

    rows = []
    for p in files("agents", ".agent.md"):
        fm = frontmatter(p)
        base = os.path.basename(p)[: -len(".agent.md")]
        if not kebab(base):
            errors.append(f"{rel(p)}: file name must be kebab-case")
        if not fm.get("description"):
            errors.append(f"{rel(p)}: missing description")
        rows.append([f"[{fm.get('name', base)}](../{rel(p)})", fm.get("description", "")])
    docs["agents"] = table(["Agent", "Description"], rows)

    rows = []
    for p in files("instructions", ".instructions.md"):
        fm = frontmatter(p)
        base = os.path.basename(p)[: -len(".instructions.md")]
        if not kebab(base):
            errors.append(f"{rel(p)}: file name must be kebab-case")
        for k in ("description", "applyTo"):
            if not fm.get(k):
                errors.append(f"{rel(p)}: missing {k}")
        rows.append([f"[{base}](../{rel(p)})", fm.get("description", ""), f"`{fm.get('applyTo', '')}`"])
    docs["instructions"] = table(["Instruction", "Description", "applyTo"], rows)

    rows = []
    for d in dirs("skills"):
        name = os.path.basename(d)
        sk = os.path.join(d, "SKILL.md")
        if not os.path.exists(sk):
            errors.append(f"{rel(d)}: missing SKILL.md")
            continue
        fm = frontmatter(sk)
        if fm.get("name") != name:
            errors.append(f"{rel(sk)}: name '{fm.get('name')}' must match folder '{name}'")
        if len(name) > 64 or not kebab(name):
            errors.append(f"{rel(sk)}: invalid skill name")
        desc = fm.get("description", "")
        if not 10 <= len(desc) <= 1024:
            errors.append(f"{rel(sk)}: description must be 10-1024 chars (is {len(desc)})")
        assets = sorted(
            os.path.relpath(os.path.join(r, f), d)
            for r, _, fs in os.walk(d) for f in fs if f != "SKILL.md"
        )
        rows.append([f"[{name}](../{rel(d)}/SKILL.md)", desc, "<br>".join(f"`{a}`" for a in assets) or "—"])
    docs["skills"] = table(["Skill", "Description", "Bundled assets"], rows)

    rows = []
    for d in dirs("hooks"):
        readme, hj = os.path.join(d, "README.md"), os.path.join(d, "hooks.json")
        fm = frontmatter(readme) if os.path.exists(readme) else {}
        if not fm.get("name") or not fm.get("description"):
            errors.append(f"{rel(d)}: README.md needs name and description")
        events = []
        try:
            events = list(json.load(open(hj))["hooks"].keys())
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel(hj)}: invalid hooks.json ({exc})")
        rows.append([f"[{fm.get('name', '')}](../{rel(d)}/README.md)", fm.get("description", ""), ", ".join(events)])
    docs["hooks"] = table(["Hook", "Description", "Events"], rows)

    rows = []
    for p in files("workflows", ".md"):
        fm = frontmatter(p)
        if not fm.get("name") or not fm.get("description"):
            errors.append(f"{rel(p)}: needs name and description")
        rows.append([f"[{fm.get('name', '')}](../{rel(p)})", fm.get("description", "")])
    docs["workflows"] = table(["Workflow", "Description"], rows)

    rows = []
    for d in dirs("plugins"):
        name = os.path.basename(d)
        pj = os.path.join(d, "plugin.json")
        try:
            meta = json.load(open(pj))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel(pj)}: {exc}")
            continue
        if meta.get("name") != name:
            errors.append(f"{rel(pj)}: name must match folder")
        for k in ("description", "version", "$schema"):
            if not meta.get(k):
                errors.append(f"{rel(pj)}: missing {k}")
        comp = meta.get("extensions", {}).get("com.github.awesome-copilot", {})
        for kind in ("agents", "skills", "hooks"):
            for ref in comp.get(kind, []):
                if not os.path.exists(os.path.join(ROOT, ref)):
                    errors.append(f"{rel(pj)}: {kind} reference not found: {ref}")
        counts = ", ".join(f"{len(comp.get(k, []))} {k}" for k in ("agents", "skills", "hooks") if comp.get(k))
        rows.append([f"[{name}](../{rel(d)}/plugin.json)", meta.get("description", ""), counts])
    docs["plugins"] = table(["Plugin", "Description", "Contents"], rows)

    cat = json.load(open(os.path.join(ROOT, "standards", "catalog.json")))
    rows = []
    required = ("id", "name", "domain", "kind", "publisher", "versioning", "latestPublished", "versionDetection", "sources")
    for s in cat["standards"]:
        for k in required:
            if k not in s:
                errors.append(f"standards/catalog.json: {s.get('id', '?')} missing {k}")
        rows.append([s["id"], s["name"], s["domain"], s["kind"], s["latestPublished"] + (" ⚠️ verify" if s.get("verify") else "")])
    docs["standards"] = table(["Id", "Standard", "Domain", "Kind", "Latest published (not a default target)"], rows)
    return docs


TITLES = {
    "agents": ("Agents", "Custom agents (`*.agent.md`). Each one resolves the target standard version before answering."),
    "instructions": ("Instructions", "File-pattern scoped coding standards (`*.instructions.md`)."),
    "skills": ("Skills", "Agent Skills folders (`SKILL.md` + bundled scripts/references), following the Agent Skills specification."),
    "hooks": ("Hooks", "Session hooks (`README.md` + `hooks.json`)."),
    "workflows": ("Workflows", "GitHub Agentic Workflows (`.md`)."),
    "plugins": ("Plugins", "Installable bundles grouping agents, skills and hooks by healthcare business domain."),
    "standards": ("Standards catalog", f"Generated from `standards/catalog.json`. Research baseline shown is a publication baseline only — see [version-strategy.md](version-strategy.md)."),
}


def render(kind: str, body: str) -> str:
    title, intro = TITLES[kind]
    return f"<!-- Generated by .github/scripts/build.py. Do not edit by hand. -->\n# {title}\n\n{intro}\n\n{body}\n"


REPO_URL = "https://github.com/thakurnt/healthcare-copilot"
MARKETPLACE = "healthcare-copilot"


def tree_files(src: str, dst_prefix: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for r, _, fs in os.walk(src):
        for f in fs:
            if f.endswith(".pyc") or "__pycache__" in r:
                continue
            p = os.path.join(r, f)
            out[os.path.join(dst_prefix, os.path.relpath(p, src))] = open(p, "rb").read()
    return out


def generated_files() -> dict[str, bytes]:
    """Every generated (non-docs) file: synced assets, packaged plugins, marketplace manifest."""
    out: dict[str, bytes] = {}
    template = open(os.path.join(ROOT, "templates", "healthcare-profile.yml"), "rb").read()
    out["skills/healthcare-version-detect/assets/healthcare-profile.yml"] = template
    protocol = open(os.path.join(ROOT, "templates", "agent-version-protocol.md"), encoding="utf-8").read()

    entries = []
    for d in dirs("plugins"):
        name = os.path.basename(d)
        meta = json.load(open(os.path.join(d, "plugin.json")))
        comp = meta.get("extensions", {}).get("com.github.awesome-copilot", {})
        base = f"dist/plugins/{name}"
        served = {k: v for k, v in meta.items() if k != "extensions"}
        served.update({"repository": REPO_URL, "license": "MIT"})
        out[f"{base}/plugin.json"] = (json.dumps(served, indent=2) + "\n").encode()
        for ref in comp.get("agents", []):
            src = os.path.join(ROOT, ref)
            agent = os.path.basename(src)[: -len(".agent.md")]
            text = open(src, encoding="utf-8").read().rstrip() + "\n" + protocol
            out[f"{base}/com.github.copilot/agents/{agent}.md"] = text.encode()
        skills_in_plugin = []
        for ref in comp.get("skills", []):
            skill = os.path.basename(os.path.normpath(ref))
            skills_in_plugin.append(skill)
            files = tree_files(os.path.join(ROOT, ref), f"{base}/skills/{skill}")
            if skill == "healthcare-version-detect":
                files[f"{base}/skills/{skill}/assets/healthcare-profile.yml"] = template
            out.update(files)
        agents = [os.path.basename(a)[: -len(".agent.md")] for a in comp.get("agents", [])]
        hooks = [os.path.basename(os.path.normpath(h)) for h in comp.get("hooks", [])]
        readme = [f"# {name}", "", meta["description"], "",
                  f"Install: `copilot plugin install {name}@{MARKETPLACE}` (see the repository README).", "",
                  "## Agents", *[f"- `{a}`" for a in agents], "", "## Skills", *[f"- `{s}`" for s in skills_in_plugin], ""]
        if hooks:
            readme += ["## Hooks (install manually)", *[f"- `{h}`: copy `hooks/{h}/` from the repository to `.github/hooks/{h}/`" for h in hooks], ""]
        readme += ["Generated by `.github/scripts/build.py` — edit sources in the repository root, not here.", ""]
        out[f"{base}/README.md"] = "\n".join(readme).encode()
        entries.append({"name": name, "source": base, "description": meta["description"], "version": meta["version"]})

    market = {
        "name": MARKETPLACE,
        "metadata": {"description": "Version-aware healthcare interoperability plugins (DICOM, HL7 v2, FHIR, C-CDA, IHE, X12, NCPDP, IEEE 11073)", "version": "1.0.0"},
        "owner": {"name": "Healthcare Copilot contributors", "url": REPO_URL},
        "plugins": entries,
    }
    out[".github/plugin/marketplace.json"] = (json.dumps(market, indent=2) + "\n").encode()
    return out


def sync_generated(check: bool) -> list[str]:
    stale: list[str] = []
    want = generated_files()
    dist = os.path.join(ROOT, "dist")
    have = {os.path.relpath(p, ROOT) for p in (os.path.join(r, f) for r, _, fs in os.walk(dist) for f in fs)} if os.path.isdir(dist) else set()
    for extra in sorted(have - set(want)):
        if check:
            stale.append(extra)
        else:
            os.remove(os.path.join(ROOT, extra))
            print(f"removed {extra}")
    for path, data in sorted(want.items()):
        full = os.path.join(ROOT, path)
        current = open(full, "rb").read() if os.path.exists(full) else None
        if current == data:
            continue
        if check:
            stale.append(path)
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "wb").write(data)
        if data.startswith(b"#!"):
            os.chmod(full, 0o755)
    if not check:
        print(f"synced {len(want)} generated files (dist/plugins, marketplace.json, skill assets)")
    return stale


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    collect()  # validate first; generation only runs on a valid tree
    stale: list[str] = []
    if not errors:
        stale += sync_generated(a.check)
    errors.clear()
    docs = collect()
    for kind, body in docs.items():
        path = os.path.join(ROOT, "docs", f"README.{kind}.md")
        content = render(kind, body)
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if current != content:
            if a.check:
                stale.append(rel(path))
            else:
                open(path, "w", encoding="utf-8").write(content)
                print(f"wrote {rel(path)}")
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    for s in stale:
        print(f"STALE {s} (run python3 .github/scripts/build.py)", file=sys.stderr)
    if errors or stale:
        return 1
    print("OK: all resources valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())

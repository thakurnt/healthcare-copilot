#!/usr/bin/env python3
"""Content lint for Healthcare Copilot: enforces the repository's content rules
that the structural build (build.py) does not cover.

Errors (exit 1):
  HC001  agent has no "Version first" section
  HC002  relative markdown link does not resolve
  HC003  agent references a skill/agent that does not exist
  HC004  text tells the reader to target/assume the latest/newest release
  HC005  skill script imports a non-standard-library module
  HC006  synthetic example contains an HL7 PID / X12 member / DICOM name without a TEST marker
  HC007  catalog source URL is not https
  HC008  skill bundles a script but has no '## Optional script' section / does not mark Python optional
  HC009  agentic workflow runs Python/repository scripts or allows the python network ecosystem (must be tool-first)
Warnings:
  HC101  catalog researchBaseline older than --max-baseline-age days
  HC102  catalog entries still marked verify:true

Usage: python3 .github/scripts/content_lint.py [--max-baseline-age 180] [--github]
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKIP_DIRS = {".git", "dist", "node_modules", "__pycache__"}
MARKERS = re.compile(r"TEST|DEMO|SYNTH|FAKE|SAMPLE|ZZ", re.I)
LATEST_RE = re.compile(r"\b(use|target|assume|default to|pick|choose|upgrade to)\s+(the\s+)?(latest|newest|most recent)\b", re.I)
NEGATION_RE = re.compile(r"\b(never|not|don't|do not|rather than|instead of|isn't|is not|without)\b", re.I)
FENCE_RE = re.compile(r"```.*?```", re.S)
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

findings: list[tuple[str, str, str, int, str]] = []  # level, code, path, line, msg


def add(level: str, code: str, path: str, line: int, msg: str) -> None:
    findings.append((level, code, os.path.relpath(path, ROOT), line, msg))


def walk(exts: tuple[str, ...]):
    for r, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if d not in SKIP_DIRS]
        for f in fs:
            if f.endswith(exts):
                yield os.path.join(r, f)


def body_of(text: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def names(folder: str, suffix: str = "") -> set[str]:
    d = os.path.join(ROOT, folder)
    if not os.path.isdir(d):
        return set()
    if suffix:
        return {f[: -len(suffix)] for f in os.listdir(d) if f.endswith(suffix)}
    return {f for f in os.listdir(d) if os.path.isdir(os.path.join(d, f))}


def line_no(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def check_agents() -> None:
    skills, agents = names("skills"), names("agents", ".agent.md")
    known = skills | agents | names("plugins") | names("hooks") | names("instructions", ".instructions.md")
    for folder in ("agents", ".github/agents"):
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(d, f)
            text = open(p, encoding="utf-8").read()
            if folder == "agents" and not re.search(r"^#+\s.*\bversion\b.*\bfirst\b", text, re.I | re.M):
                add("error", "HC001", p, 1, "agent must contain a 'Version first' step (see AGENTS.md)")
            prose = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), body_of(text))
            for m in re.finditer(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", prose):
                tok = m.group(1)
                line = prose[prose.rfind("\n", 0, m.start()) + 1: prose.find("\n", m.end())]
                if re.search(r"skill|agent|hand .* to|delegate", line, re.I) and tok not in known:
                    add("error", "HC003", p, line_no(text, text.find(m.group(0))), f"unknown skill/agent reference `{tok}`")


def check_links_and_latest() -> None:
    for p in walk((".md",)):
        text = open(p, encoding="utf-8").read()
        prose = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
        no_code = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), prose)  # regexes in `code` aren't links
        for m in LINK_RE.finditer(no_code):
            target = m.group(1).split("#")[0]
            if not target or re.match(r"^[a-z]+:", target) or "<" in target or target.startswith("#"):
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(p), target))
            if not os.path.exists(resolved):
                add("error", "HC002", p, line_no(prose, m.start()), f"broken relative link: {m.group(1)}")
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(("agents/", "instructions/", "skills/", "templates/")):
            for i, line in enumerate(prose.splitlines(), 1):
                if LATEST_RE.search(line) and not NEGATION_RE.search(line):
                    add("error", "HC004", p, i, "do not direct users to the latest/newest release; resolve the target version instead")


def check_script_imports() -> None:
    stdlib = getattr(sys, "stdlib_module_names", None)
    if stdlib is None:  # Python < 3.10: skip rather than guess
        return
    for base in ("skills", ".github/skills", "hooks"):
        d = os.path.join(ROOT, base)
        if not os.path.isdir(d):
            continue
        for r, _, fs in os.walk(d):
            for f in fs:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(r, f)
                tree = ast.parse(open(p, encoding="utf-8").read())
                for node in ast.walk(tree):
                    mods = []
                    if isinstance(node, ast.Import):
                        mods = [a.name for a in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        mods = [node.module]
                    for mod in mods:
                        top = mod.split(".")[0]
                        if top not in stdlib and top != "__future__":
                            add("error", "HC005", p, node.lineno, f"non-stdlib import '{mod}' (skill scripts must be stdlib-only)")


def check_skill_tool_first() -> None:
    """Users may not have Python: skills must work with built-in tools; scripts are optional."""
    d = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(d)):
        scripts = os.path.join(d, name, "scripts")
        if not os.path.isdir(scripts) or not any(f.endswith(".py") for f in os.listdir(scripts)):
            continue
        p = os.path.join(d, name, "SKILL.md")
        text = open(p, encoding="utf-8").read()
        if not re.search(r"^##\s+Optional script", text, re.M):
            add("error", "HC008", p, 1, "skill bundles a script: add an '## Optional script' section and a default procedure using built-in search/read tools")
        m = re.search(r"^compatibility:\s*(.*)$", text, re.M)
        if not m or "optional" not in m.group(1).lower():
            add("error", "HC008", p, 1, "compatibility must state that Python/script is optional")


def check_workflows_tool_first() -> None:
    """Agentic workflows (gh-aw .md) use built-in tools only; deterministic checks live in Actions YAML."""
    for folder in (".github/workflows", "workflows"):
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(d, f)
            text = open(p, encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            if not m or not re.search(r"^on:", m.group(1), re.M):
                continue
            fm = m.group(1)
            for i, line in enumerate(fm.splitlines(), 2):
                if re.match(r"\s*bash:", line) and re.search(r"python|\.github/scripts/", line):
                    add("error", "HC009", p, i, "agentic workflow bash allowlist runs Python/repo scripts; use built-in tools and read CI results instead")
                if re.match(r"\s*-\s*python\s*$", line):
                    add("error", "HC009", p, i, "agentic workflow allows the 'python' network ecosystem; not needed for tool-first workflows")


def check_examples() -> None:
    d = os.path.join(ROOT, "examples")
    if not os.path.isdir(d):
        return
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            raw = open(p, "rb").read()
            if raw[128:132] == b"DICM":
                idx = raw.find(b"\x10\x00\x10\x00PN")
                if idx != -1:
                    ln = int.from_bytes(raw[idx + 6: idx + 8], "little")
                    if not MARKERS.search(raw[idx + 8: idx + 8 + ln].decode("latin-1")):
                        add("error", "HC006", p, 1, "DICOM PatientName lacks a synthetic marker")
                continue
            text = raw.decode("utf-8", "replace")
            for i, line in enumerate(re.split(r"\r\n|\r|\n", text), 1):
                if (line.startswith("PID|") or re.match(r"NM1\*(IL|QC)\*", line)) and not MARKERS.search(line):
                    add("error", "HC006", p, i, "patient/member data lacks a synthetic marker (TEST/DEMO/SYNTH/...)")


def check_catalog(max_age: int) -> None:
    p = os.path.join(ROOT, "standards", "catalog.json")
    cat = json.load(open(p))
    base = dt.date.fromisoformat(cat["researchBaseline"])
    age = (dt.date.today() - base).days
    if age > max_age:
        add("warning", "HC101", p, 1, f"researchBaseline {base} is {age} days old; run the Standards Baseline Watch workflow")
    verify = [s["id"] for s in cat["standards"] if s.get("verify")]
    if verify:
        add("warning", "HC102", p, 1, f"{len(verify)} entries still marked verify:true: {', '.join(verify)}")
    text = open(p).read()
    for s in cat["standards"]:
        for url in s.get("sources", []):
            if not url.startswith("https://"):
                add("error", "HC007", p, line_no(text, text.find(url)), f"{s['id']}: source must be https: {url}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-baseline-age", type=int, default=180)
    ap.add_argument("--github", action="store_true", help="emit GitHub Actions annotations")
    a = ap.parse_args()
    check_agents()
    check_links_and_latest()
    check_script_imports()
    check_skill_tool_first()
    check_workflows_tool_first()
    check_examples()
    check_catalog(a.max_baseline_age)
    errors = 0
    for level, code, path, line, msg in findings:
        errors += level == "error"
        if a.github:
            print(f"::{level} file={path},line={line},title={code}::{msg}")
        else:
            print(f"{level.upper():7} {code} {path}:{line} {msg}")
    print(f"content-lint: {errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fail if a packaged plugin's content changed but its version was not bumped.

Usage (in a PR): python3 .github/scripts/check_plugin_versions.py --base origin/main
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()
    changed = git("diff", "--name-only", f"{a.base}...HEAD", "--", "dist/plugins").split()
    plugins = sorted({p.split("/")[2] for p in changed if p.count("/") >= 3})
    bad = []
    for name in plugins:
        src = f"plugins/{name}/plugin.json"
        old_raw = git("show", f"{a.base}:{src}")
        if not old_raw:
            print(f"new plugin {name}: ok")
            continue
        old_v = json.loads(old_raw)["version"]
        new_v = json.load(open(os.path.join(ROOT, src)))["version"]
        if old_v == new_v:
            bad.append(name)
            print(f"::error file={src},title=Plugin version not bumped::{name} content changed but version is still {new_v}")
        else:
            print(f"{name}: {old_v} -> {new_v} ok")
    if not plugins:
        print("no packaged plugin changes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

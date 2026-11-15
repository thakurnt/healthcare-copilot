#!/usr/bin/env python3
"""Check that every source URL in standards/catalog.json is reachable.

Writes a Markdown table to $GITHUB_STEP_SUMMARY when available.
Exit 1 on hard failures (404/410/5xx/DNS); 401/403/429 are reported as warnings
because publisher sites often block automated clients.
"""
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UA = "healthcare-copilot-link-check/1.0 (+https://github.com/thakurnt/healthcare-copilot)"


def probe(url: str) -> tuple[str, str]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return "ok", str(r.status)
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            if e.code in (401, 403, 429):
                return "warn", str(e.code)
            return "fail", str(e.code)
        except Exception as e:  # noqa: BLE001
            if method == "HEAD":
                continue
            return "fail", type(e).__name__
    return "fail", "unknown"


def main() -> int:
    cat = json.load(open(os.path.join(ROOT, "standards", "catalog.json")))
    rows, fails = [], 0
    for s in cat["standards"]:
        for url in s.get("sources", []):
            state, code = probe(url)
            fails += state == "fail"
            icon = {"ok": "✅", "warn": "⚠️", "fail": "❌"}[state]
            rows.append(f"| {s['id']} | {url} | {icon} {code} |")
            print(f"{state:4} {code:>4} {s['id']:15} {url}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write("## Catalog source links\n\n| Standard | URL | Status |\n|---|---|---|\n" + "\n".join(rows) + "\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

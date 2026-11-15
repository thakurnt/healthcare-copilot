#!/usr/bin/env python3
"""Inspect an HL7 v2 message: structure, version, and version-aware warnings.

Standard library only. By default identifiers in PID/NK1/GT1/IN1 are masked
in the output so the tool is safe to use on real-looking data.

Usage:
    python3 hl7v2_inspect.py FILE [--target-version 2.5.1] [--show-phi] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys

PHI_SEGMENTS = {"PID", "PD1", "NK1", "GT1", "IN1", "IN2", "MRG", "PV1"}

# version tuple helpers -------------------------------------------------------
def vt(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))

# fields[n] == field n for every segment (MSH-1 is the field separator).
# Minimal, conservative knowledge base. Each rule: (applies_if, message).
# Keep rules verifiable; when unsure, phrase as "verify".
def version_warnings(msg: dict, target: str) -> list[str]:
    w: list[str] = []
    t = vt(target)
    msh = msg["segments"][0]["fields"] if msg["segments"] else []
    enc = msg["encoding"]
    seg_ids = [s["id"] for s in msg["segments"]]
    msh9 = msh[9] if len(msh) > 9 else ""

    if len(enc) == 5 and t < (2, 7):
        w.append(f"MSH-2 has 5 encoding characters (truncation char) which is defined from v2.7; target is {target}.")
    if msh9.count(enc[0]) >= 2 and t < (2, 3, 1):
        w.append(f"MSH-9 includes a message structure component (MSH-9.3) which exists from v2.3.1; target is {target}.")
    if msh9.startswith("ORM") and t >= (2, 5):
        w.append("ORM is the legacy order message; for v2.5+ partners consider OML/OMI/OMG per the partner spec (IHE SWF.b uses OMI^O23). Keep ORM if the partner requires it.")
    if msh9.startswith(("OMI", "OML", "OMG")) and t < (2, 5):
        w.append(f"{msh9.split(enc[0])[0]} is not defined in v{target} (introduced in later releases); use ORM^O01 or confirm the version.")
    if "SFT" in seg_ids and t < (2, 5):
        w.append(f"SFT segment is defined from v2.5; target is {target}.")
    if "UAC" in seg_ids and t < (2, 7):
        w.append(f"UAC segment is defined from v2.7; target is {target}.")
    if "PRT" in seg_ids and t < (2, 7):
        w.append(f"PRT segment is defined from v2.7; target is {target}.")
    for s in msg["segments"]:
        if s["id"] == "PID":
            f = s["fields"]
            if t >= (2, 5) and ((len(f) > 2 and f[2]) or (len(f) > 4 and f[4])):
                w.append("PID-2/PID-4 are populated; they are retained for backward compatibility only from v2.3.1+ — prefer PID-3 identifier list unless the partner requires them.")
    if any(s["id"].startswith("Z") for s in msg["segments"]):
        w.append("Z-segments present: validate against the site interface specification, not the base standard.")
    return w


def parse(raw: str) -> dict:
    raw = raw.replace("\x0b", "").replace("\x1c", "")
    segs = [s for s in re.split(r"\r\n|\r|\n", raw) if s.strip()]
    if not segs or not segs[0].startswith("MSH"):
        raise ValueError("Message must start with an MSH segment")
    fs = segs[0][3]
    enc_end = segs[0].find(fs, 4)
    enc = segs[0][4:enc_end if enc_end != -1 else None]
    out = {"field_separator": fs, "encoding": enc, "segments": []}
    for s in segs:
        parts = s.split(fs)
        if parts[0] == "MSH":
            # make index == field number: MSH-1 is the separator itself
            fields = ["MSH", fs] + parts[1:]
        else:
            fields = parts
        out["segments"].append({"id": parts[0], "fields": fields})
    return out


def mask(value: str) -> str:
    return re.sub(r"[A-Za-z0-9]", "*", value) if value else value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--target-version", help="version to check against (default: MSH-12)")
    ap.add_argument("--show-phi", action="store_true", help="do not mask PHI segments (synthetic data only!)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with open(a.file, encoding="utf-8", errors="replace") as fh:
        msg = parse(fh.read())
    msh = msg["segments"][0]["fields"]
    comp = msg["encoding"][0] if msg["encoding"] else "^"
    declared = msh[12].split(comp)[0] if len(msh) > 12 else ""
    target = a.target_version or declared or "2.5.1"
    summary = {
        "declared_version_MSH12": declared or None,
        "target_version": target,
        "message_type_MSH9": msh[9] if len(msh) > 9 else None,
        "control_id_MSH10": msh[10] if len(msh) > 10 else None,
        "processing_id_MSH11": msh[11] if len(msh) > 11 else None,
        "encoding_characters": msg["encoding"],
        "segments": [s["id"] for s in msg["segments"]],
        "warnings": version_warnings(msg, target),
    }
    if declared and a.target_version and declared != a.target_version:
        summary["warnings"].insert(0, f"MSH-12 declares {declared} but target is {a.target_version}: confirm which applies to this interface.")
    if not declared:
        summary["warnings"].insert(0, "MSH-12 is empty: version unknown — ask the user or check the interface spec.")

    if a.json:
        json.dump(summary, sys.stdout, indent=2)
        print()
        return 0
    print(f"Declared version (MSH-12): {summary['declared_version_MSH12']}")
    print(f"Target version:            {target}")
    print(f"Message type (MSH-9):      {summary['message_type_MSH9']}")
    print(f"Control ID (MSH-10):       {summary['control_id_MSH10']}")
    print(f"Segments: {' '.join(summary['segments'])}\n")
    for s in msg["segments"]:
        for i, val in enumerate(s["fields"][1:], start=1):
            if not val or (s["id"] == "MSH" and i <= 2):
                continue
            shown = mask(val) if (s["id"] in PHI_SEGMENTS and not a.show_phi) else val
            print(f"  {s['id']}-{i}: {shown}")
    print("\nWarnings:" if summary["warnings"] else "\nNo version warnings.")
    for x in summary["warnings"]:
        print(f"  - {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

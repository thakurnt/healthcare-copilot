#!/usr/bin/env python3
"""Scan a project for evidence of healthcare standard versions.

Standard library only. Reads files; never modifies them. Prints only version
metadata (never message content) so it is safe to run on folders that might
contain PHI.

Usage:
    python3 detect_versions.py [PATH] [--json] [--max-files N]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
from collections import defaultdict

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "target", ".idea", ".vscode"}
MAX_BYTES = 2_000_000

FHIR_RELEASES = {
    "1.0.2": "DSTU2", "3.0.1": "STU3", "3.0.2": "STU3", "4.0.0": "R4", "4.0.1": "R4",
    "4.1.0": "R4B-ballot", "4.3.0": "R4B", "5.0.0": "R5",
}
FHIR_PKG_RE = re.compile(r"hl7\.fhir\.(r2|r3|r4|r4b|r5|r6)\.core")
HAPI_CTX_RE = re.compile(r"FhirContext\.for(Dstu2|Dstu3|R4B|R4|R5)")
DOTNET_FHIR_RE = re.compile(r"Hl7\.Fhir\.(STU3|R4B|R4|R5)")
PY_FHIR_RE = re.compile(r"fhir\.resources\.(STU3|R4B|R4|R5)", re.I)
CCDA_TEMPLATE_RE = re.compile(r'<templateId\s+root="(2\.16\.840\.1\.113883\.10\.20\.22\.[0-9.]+)"(?:\s+extension="([^"]+)")?')
SCRIPT_VER_RE = re.compile(r'<Message[^>]*\bversion="([^"]+)"|<TransportVersion>([^<]+)<|<ECLVersion>([^<]+)<|TransactionDomain="SCRIPT"[^>]*TransactionVersion="([^"]+)"')
EDITION_RE = re.compile(r"\bDICOM\s+(?:PS\s?3(?:\.\d+)?\s+)?(20[0-9]{2}[a-e])\b")

TS_NAMES = {
    "1.2.840.10008.1.2": "Implicit VR Little Endian",
    "1.2.840.10008.1.2.1": "Explicit VR Little Endian",
    "1.2.840.10008.1.2.1.99": "Deflated Explicit VR Little Endian",
    "1.2.840.10008.1.2.2": "Explicit VR Big Endian (RETIRED)",
    "1.2.840.10008.1.2.4.50": "JPEG Baseline",
    "1.2.840.10008.1.2.4.57": "JPEG Lossless",
    "1.2.840.10008.1.2.4.70": "JPEG Lossless SV1",
    "1.2.840.10008.1.2.4.80": "JPEG-LS Lossless",
    "1.2.840.10008.1.2.4.81": "JPEG-LS Near-Lossless",
    "1.2.840.10008.1.2.4.90": "JPEG 2000 Lossless",
    "1.2.840.10008.1.2.4.91": "JPEG 2000",
    "1.2.840.10008.1.2.5": "RLE Lossless",
}


class Findings:
    def __init__(self) -> None:
        self.items: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    def add(self, standard: str, value: str, path: str) -> None:
        self.items[standard][value].add(path)

    def as_dict(self) -> dict:
        return {s: {v: sorted(p) for v, p in vals.items()} for s, vals in sorted(self.items.items())}


def read_text(path: str) -> str | None:
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, "rb") as fh:
            raw = fh.read()
        if b"\x00" in raw[:4096]:
            return None
        return raw.decode("utf-8", errors="replace")
    except OSError:
        return None


def scan_dicom_part10(path: str, f: Findings) -> bool:
    """Parse only the Part 10 file meta group (0002). Returns True if DICOM."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(132)
            if len(head) < 132 or head[128:132] != b"DICM":
                return False
            data = fh.read(8192)
    except OSError:
        return False
    pos = 0
    while pos + 8 <= len(data):
        group, elem = struct.unpack_from("<HH", data, pos)
        if group != 0x0002:
            break
        vr = data[pos + 4:pos + 6].decode("ascii", "replace")
        if vr in ("OB", "OW", "OF", "SQ", "UT", "UN", "UC", "UR", "OD", "OL", "OV", "SV", "UV"):
            if pos + 12 > len(data):
                break
            length = struct.unpack_from("<I", data, pos + 8)[0]
            vpos = pos + 12
        else:
            length = struct.unpack_from("<H", data, pos + 6)[0]
            vpos = pos + 8
        value = data[vpos:vpos + length].rstrip(b"\x00 ").decode("ascii", "replace")
        if (group, elem) == (0x0002, 0x0010):
            f.add("dicom.transfer_syntax", f"{value} ({TS_NAMES.get(value, 'see PS3.6 Table A-1')})", path)
        elif (group, elem) == (0x0002, 0x0002):
            f.add("dicom.sop_class", value, path)
        elif (group, elem) == (0x0002, 0x0013):
            f.add("dicom.implementation_version_name", value, path)
        pos = vpos + length
    return True


def scan_text(path: str, text: str, f: Findings) -> None:
    name = os.path.basename(path).lower()

    # HL7 v2: MSH-12 (normalise \n and \r\n to \r)
    if "MSH" in text:
        for seg in re.split(r"\r\n|\r|\n", text):
            seg = seg.lstrip("\x0b")
            if seg.startswith("MSH") and len(seg) > 8:
                fs = seg[3]
                fields = seg.split(fs)
                # fields[0]='MSH', fields[1]=encoding chars => MSH-n is fields[n-1]
                if len(fields) > 11:
                    ver = fields[11].split(seg[4] if len(seg) > 4 else "^")[0]
                    if re.fullmatch(r"2\.\d(\.\d)?", ver):
                        f.add("hl7v2.MSH-12", ver, path)
                if len(fields) > 8 and fields[8]:
                    f.add("hl7v2.message_types", fields[8], path)

    # X12: ISA12 / GS08
    if text.lstrip().startswith("ISA") and len(text.lstrip()) > 106:
        isa = text.lstrip()
        es = isa[3]
        parts = isa[:106].split(es)
        if len(parts) > 12:
            f.add("x12.ISA12", parts[12], path)
        seg_term = isa[105] if len(isa) > 105 else "~"
        for seg in isa.split(seg_term):
            seg = seg.strip()
            if seg.startswith("GS" + es):
                gs = seg.split(es)
                if len(gs) > 8:
                    f.add("x12.GS08", gs[8], path)

    # FHIR
    if name.endswith((".json", ".xml", ".yaml", ".yml", ".ini")) or "fhir" in name:
        for m in re.finditer(r'"fhirVersion"\s*:\s*"([^"]+)"|<fhirVersion value="([^"]+)"', text):
            v = m.group(1) or m.group(2)
            f.add("fhir.fhirVersion", f"{v} ({FHIR_RELEASES.get(v, '?')})", path)
        for m in re.finditer(r'"fhirVersions"\s*:\s*\[([^\]]*)\]', text):
            for v in re.findall(r'"([^"]+)"', m.group(1)):
                f.add("fhir.package.fhirVersions", f"{v} ({FHIR_RELEASES.get(v, '?')})", path)
        if name in ("sushi-config.yaml", "sushi-config.yml"):
            for m in re.finditer(r"^fhirVersion:\s*([\w.\-]+)", text, re.M):
                f.add("fhir.sushi.fhirVersion", m.group(1), path)
            for m in re.finditer(r"^\s{2}([a-z0-9.\-]+):\s*([0-9][\w.\-]*)\s*$", text, re.M):
                f.add("fhir.ig_dependencies", f"{m.group(1)}#{m.group(2)}", path)
        if name == "package.json":
            for m in re.finditer(r'"((?:hl7|ihe)\.[a-z0-9.\-]+)"\s*:\s*"([^"]+)"', text):
                f.add("fhir.ig_dependencies", f"{m.group(1)}#{m.group(2)}", path)
        for m in re.finditer(r'"(http[^"|]+/StructureDefinition/[^"|]+)\|([^"]+)"', text):
            f.add("fhir.meta.profile_versioned", f"{m.group(1)}|{m.group(2)}", path)
    for rx, label in ((FHIR_PKG_RE, "fhir.core_package"), (HAPI_CTX_RE, "fhir.hapi_context"),
                      (DOTNET_FHIR_RE, "fhir.dotnet_package"), (PY_FHIR_RE, "fhir.python_package")):
        for m in rx.finditer(text):
            f.add(label, m.group(0), path)

    # C-CDA templates
    if "ClinicalDocument" in text:
        for root, ext in CCDA_TEMPLATE_RE.findall(text):
            if root == "2.16.840.1.113883.10.20.22.1.1":
                f.add("ccda.us_realm_header", ext or "(no extension = R1.1)", path)
            else:
                f.add("ccda.template_extensions", ext or "(none)", path)

    # NCPDP SCRIPT
    if "<Message" in text and ("NewRx" in text or "ncpdp" in text.lower()):
        for m in SCRIPT_VER_RE.finditer(text):
            v = next(g for g in m.groups() if g)
            f.add("ncpdp.script_version", v, path)

    # DICOM edition references in docs/config
    for m in EDITION_RE.finditer(text):
        f.add("dicom.edition_reference", m.group(1), path)

    # Existing profile
    if name in ("healthcare-profile.yml", "healthcare-profile.yaml"):
        f.add("profile", "healthcare-profile present", path)


def walk(root: str, max_files: int) -> Findings:
    f = Findings()
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            count += 1
            if count > max_files:
                return f
            if scan_dicom_part10(path, _Rel(f, rel)):
                continue
            text = read_text(path)
            if text:
                scan_text(rel, text, f)
    return f


class _Rel:
    """Adapter so DICOM findings record relative paths."""
    def __init__(self, f: Findings, rel: str) -> None:
        self.f, self.rel = f, rel

    def add(self, standard: str, value: str, _path: str) -> None:
        self.f.add(standard, value, self.rel)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--max-files", type=int, default=50_000)
    args = ap.parse_args()

    result = walk(os.path.abspath(args.path), args.max_files).as_dict()
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
        return 0
    if not result:
        print("No healthcare standard version evidence found. Ask the user, then create healthcare-profile.yml.")
        return 0
    for standard, values in result.items():
        print(f"\n## {standard}")
        for value, paths in values.items():
            shown = ", ".join(paths[:3]) + (f" (+{len(paths) - 3} more)" if len(paths) > 3 else "")
            print(f"  - {value}  <- {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

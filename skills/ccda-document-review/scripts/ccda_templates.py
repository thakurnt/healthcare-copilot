#!/usr/bin/env python3
"""Inventory templateIds (root + extension) in a CDA/C-CDA document.

Standard library only; prints structure, never clinical content.
Usage: python3 ccda_templates.py document.xml
"""
import sys
import xml.etree.ElementTree as ET

NS = {"cda": "urn:hl7-org:v3"}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = ET.parse(sys.argv[1]).getroot()
    print("Document-level templateIds:")
    for t in root.findall("cda:templateId", NS):
        print(f"  {t.get('root')}  ext={t.get('extension') or '(none)'}")
    print("\nSections:")
    for sec in root.iter("{urn:hl7-org:v3}section"):
        code = sec.find("cda:code", NS)
        tids = [f"{t.get('root')}@{t.get('extension') or '-'}" for t in sec.findall("cda:templateId", NS)]
        label = code.get("code") if code is not None else "?"
        print(f"  LOINC {label}: {', '.join(tids) or '(no templateId)'}")
    exts = sorted({t.get("extension") for t in root.iter("{urn:hl7-org:v3}templateId") if t.get("extension")})
    print("\nDistinct template extensions (release dates):", ", ".join(exts) or "(none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

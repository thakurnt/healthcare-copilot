#!/usr/bin/env python3
"""Summarise an X12 interchange: delimiters, ISA12, GS08 (TR3), ST sets, counts.

Standard library only; prints envelope metadata only (no claim/member data).
Usage: python3 x12_inspect.py file.edi
"""
import sys

HIPAA_5010 = {
    "005010X222A1": "837P", "005010X223A2": "837I", "005010X224A2": "837D",
    "005010X221A1": "835", "005010X279A1": "270/271", "005010X212": "276/277",
    "005010X217": "278", "005010X220A1": "834", "005010X218": "820", "005010X231A1": "999",
}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    data = open(sys.argv[1], encoding="ascii", errors="replace").read().lstrip()
    if not data.startswith("ISA") or len(data) < 106:
        print("Not an X12 interchange (missing ISA)")
        return 1
    es, rep, comp, term = data[3], data[82], data[104], data[105]
    isa = data[:106].split(es)
    print(f"Element sep '{es}'  repetition '{rep}'  component '{comp}'  segment term {term!r}")
    print(f"ISA12 (interchange version): {isa[12]}   ISA15 usage: {isa[15]}")
    segs = [s.strip() for s in data.split(term) if s.strip()]
    st_count = 0
    for s in segs:
        e = s.split(es)
        if e[0] == "GS":
            gs08 = e[8] if len(e) > 8 else ""
            label = HIPAA_5010.get(gs08, "not a known HIPAA 5010 TR3 - check partner agreement")
            print(f"GS: functional id {e[1]}  GS08 {gs08}  -> {label}")
        elif e[0] == "ST":
            st_count += 1
            print(f"  ST {e[1]} control {e[2]}" + (f"  ST03 {e[3]}" if len(e) > 3 else ""))
    print(f"Transaction sets: {st_count}")
    if isa[12] != "00501":
        print("NOTE: ISA12 is not 00501. HIPAA-covered transactions currently use 005010; confirm this is a non-HIPAA or agreed flow.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# PHI scanner for files changed in the working tree.
# Prints file:line and rule only, never the matched value.
set -uo pipefail
MODE="${SCAN_MODE:-warn}"
MARKERS="${SYNTHETIC_MARKERS:-TEST,DEMO,SYNTH,ZZ,FAKE,SAMPLE}"
MARKER_RE="$(echo "$MARKERS" | sed 's/,/|/g')"

files=$( { git diff --name-only HEAD 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null; } | sort -u )
[ -z "$files" ] && exit 0

scan_file() {
  local f="$1"
  if [ "$(head -c 132 "$f" 2>/dev/null | tail -c 4)" = "DICM" ]; then
    echo "PHI-SCAN [dicom-file: confirm PS3.15 de-identification incl. pixel data] $f"
    return
  fi
  grep -Iq . "$f" 2>/dev/null || return
  grep -nE '(^|[^0-9])[0-8][0-9]{2}-[0-9]{2}-[0-9]{4}([^0-9]|$)' "$f" \
    | grep -vE '(^|[^0-9])(000|666)-' | cut -d: -f1 \
    | sed "s|^|PHI-SCAN [ssn-pattern] $f:|"
  tr '\r' '\n' < "$f" | grep -nE '^PID\|' | grep -viE "$MARKER_RE" | cut -d: -f1 \
    | sed "s|^|PHI-SCAN [hl7-pid-not-synthetic] $f:|"
  grep -nE 'NM1\*(IL|QC)\*' "$f" | grep -viE "$MARKER_RE" | cut -d: -f1 \
    | sed "s|^|PHI-SCAN [x12-member-not-synthetic] $f:|"
}

out=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  out+="$(scan_file "$f")"$'\n'
done <<< "$files"
out="$(printf '%s' "$out" | sed '/^$/d')"

if [ -n "$out" ]; then
  echo "$out" >&2
  echo "PHI-SCAN: review the findings above. Use synthetic data only (see instructions/healthcare-phi-safety.instructions.md)." >&2
  [ "$MODE" = "block" ] && exit 1
fi
exit 0

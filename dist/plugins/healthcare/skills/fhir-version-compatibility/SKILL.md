---
name: fhir-version-compatibility
description: 'Determine FHIR core and Implementation Guide versions, check whether resources/elements/operations exist in the target version (DSTU2, STU3, R4, R4B, R5, R6 ballot), and plan cross-version mapping using extensions or backport IGs. Use when writing FHIR code/profiles for a specific server version, migrating R4↔R5, or when an IG pins an older FHIR version.'
license: MIT
metadata:
  version: "1.0"
---

# FHIR Version Compatibility

## Steps
1. **Resolve versions** — core (`CapabilityStatement.fhirVersion`, packages, `sushi-config.yaml`) and every IG (with the FHIR version each IG is built on). Record e.g. `R4 4.0.1 · US Core 6.1.0 (R4) · IHE MHD 4.2.5 (R4)`.
2. **Check element existence** in the target version's spec page (`https://hl7.org/fhir/<R4|R4B|R5|STU3|DSTU2>/<resource>.html`). Use [references/version-map.md](references/version-map.md) for known traps.
3. **If the requirement needs a newer feature**:
   - Prefer a published backport IG (e.g. Subscriptions R5 Backport for R4/R4B).
   - Else a cross-version extension: `http://hl7.org/fhir/<sourceVersion>/StructureDefinition/extension-<Resource>.<element>` (check availability for the version pair).
   - Else a project extension with a documented canonical URL.
4. **Migrations**: produce a per-resource delta table (element, R-old, R-new, transform, data-loss risk) and test both versions during cutover.
5. **Validation**: run the HL7 validator pinned to the core version with exact IG packages, e.g. `java -jar validator_cli.jar file.json -version 4.0.1 -ig hl7.fhir.us.core#6.1.0`.

## Output
Target line → compatibility findings table → recommended approach per finding → validation command.

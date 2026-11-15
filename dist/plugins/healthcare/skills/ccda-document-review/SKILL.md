---
name: ccda-document-review
description: 'Review or generate CDA R2 / C-CDA documents against the correct C-CDA release by inventorying templateId root+extension pairs (with built-in search or an optional script), then validating with the Schematron of that release. Use for CCD, discharge summary, referral and other C-CDA documents, including legacy R1.1/2.1 documents.'
license: MIT
compatibility: 'No dependencies. Optional script needs Python 3.8+ (standard library only).'
metadata:
  version: "1.1"
---

# C-CDA Document Review

## Steps
1. **Inventory templates** with search — structure only, no clinical content:
   - US Realm Header: `templateId root="2\.16\.840\.1\.113883\.10\.20\.22\.1\.1"(?:\s+extension="([^"]+)")?`
   - All C-CDA templates: `templateId root="(2\.16\.840\.1\.113883\.10\.20\.22\.[0-9.]+)"(?:\s+extension="([^"]+)")?`
   - Section codes: `<section>` → `<code code="([0-9-]+)"` (LOINC section codes).
   Do not quote `recordTarget`, narrative `<text>` or entry values back to the user.
2. **Map extensions to releases** using the C-CDA release's template list (do not guess OIDs). No extension on the header ⇒ R1.1 era; `2015-08-01` ⇒ 2.1 era; later dates ⇒ later releases (verify). Mixed releases are allowed when the target release permits.
3. **Resolve the required release** from the profile or receiver/programme; compare.
4. **Validate** with schema + the Schematron for that release (not a newer one).
5. **Report by section:** template, release, errors/warnings, narrative/entry consistency, nullFlavor misuse, code system/version issues.

## Optional script
If `python3` is available:
```bash
python3 <skill-dir>/scripts/ccda_templates.py doc.xml
```
prints the same inventory (document templates, sections with LOINC code and templateIds, distinct extensions). Otherwise use step 1.

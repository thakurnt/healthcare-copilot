---
name: ccda-document-review
description: 'Review or generate CDA R2 / C-CDA documents against the correct C-CDA release by inventorying templateId root+extension pairs, then validating with the Schematron of that release. Use for CCD, discharge summary, referral and other C-CDA documents, including legacy R1.1/2.1 documents.'
license: MIT
compatibility: 'Python 3.8+ standard library only.'
metadata:
  version: "1.0"
---

# C-CDA Document Review

## Steps
1. Inventory templates: `python3 <skill-dir>/scripts/ccda_templates.py doc.xml`.
2. Map the US Realm Header extension and section/entry extensions to C-CDA releases (consult the C-CDA release's template list; do not guess OIDs). Mixed releases are allowed when the target release permits.
3. Resolve the **required** release from the profile or receiver/programme; compare.
4. Validate with schema + the Schematron for that release (not a newer one).
5. Report by section: template, release, errors/warnings, narrative/entry consistency, nullFlavor misuse, code system/version issues.

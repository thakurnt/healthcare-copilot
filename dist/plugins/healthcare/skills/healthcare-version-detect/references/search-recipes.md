# Version evidence — search recipes

Regexes are written for ripgrep / most IDE regex search (PCRE-like). Escape `|` as `\|`. Record **only the captured value and the file path**.

## HL7 v2 — `MSH-12`
- Files: `**/*.{hl7,er7,txt,msg}`, interface-engine channel exports, test fixtures.
- Pattern (default delimiters): `MSH\|[^|]*\|(?:[^|]*\|){9}([0-9]\.[0-9](?:\.[0-9])?)`
  - Field 1 is the `|` itself, field 2 the encoding characters, so 9 more fields precede `MSH-12`.
  - Segments end with `\r`; IDE search may show a whole message as one line — the pattern still matches from `MSH|`.
- Non-default field separator: the character right after `MSH` is the separator; adapt the pattern.
- Also useful: `MSH-9` message type `MSH\|[^|]*\|(?:[^|]*\|){6}([^|]*)`; interface engine config keys such as `version`, `hl7Version`.

## FHIR
| Look for | Pattern | Where |
|---|---|---|
| Core version in JSON | `"fhirVersion"\s*:\s*"([^"]+)"` | CapabilityStatement, ImplementationGuide, fixtures |
| Core version in XML | `<fhirVersion value="([^"]+)"` | |
| Package versions | `"fhirVersions"\s*:\s*\[([^\]]*)\]` | `package.json` of IGs |
| SUSHI | `^fhirVersion:\s*(\S+)` | `sushi-config.yaml` |
| Core package / libs | `hl7\.fhir\.(r2\|r3\|r4\|r4b\|r5\|r6)\.core` · `FhirContext\.for(Dstu2\|Dstu3\|R4B?\|R5)` · `Hl7\.Fhir\.(STU3\|R4B?\|R5)` · `fhir\.resources\.(STU3\|R4B?\|R5)` | `pom.xml`, `build.gradle`, `*.csproj`, `package.json`, `requirements*.txt`, source |
| IG dependencies | `"((?:hl7\|ihe)\.[a-z0-9.\-]+)"\s*:\s*"([^"]+)"` | `package.json`, `sushi-config.yaml` dependencies |
| Versioned profiles | `/StructureDefinition/[^"\|]+\|([0-9][^"]*)` | `meta.profile`, `supportedProfile` |

Version labels: 1.0.2 = DSTU2, 3.0.x = STU3, 4.0.x = R4, 4.3.0 = R4B, 5.0.0 = R5.

## DICOM
- Edition text: `\b(20[0-9]{2}[a-e])\b` near "DICOM" in `docs/`, conformance statements, README, config.
- Transfer syntaxes in code/config: `1\.2\.840\.10008\.1\.2(?:\.[0-9]+)*` (e.g. `...1.2.1` Explicit VR LE, `...1.2.4.90` JPEG 2000 Lossless, `...1.2.2` retired Explicit VR Big Endian).
- SOP classes in config: `1\.2\.840\.10008\.5\.1\.4\.1\.1\.[0-9.]+`.
- `.dcm` / extension-less DICOM files are **binary**; built-in text search usually skips them. Count them with a glob (`**/*.dcm`) and either use the optional script or rely on the conformance statement. If a shell is allowed, `grep -a -o '1\.2\.840\.10008\.1\.2[0-9.]*' file.dcm | head -1` reads the transfer syntax from the file meta header without exposing patient data.
- Toolkit hints: `pydicom`, `pynetdicom`, `dcmtk`, `fo-dicom`, `dcm4che` versions in dependency files.

## C-CDA
- `templateId root="2\.16\.840\.1\.113883\.10\.20\.22\.1\.1"(?:\s+extension="([^"]+)")?` — US Realm Header; no extension ⇒ R1.1 era, `2015-08-01` ⇒ 2.1 era; newer extension dates indicate later releases (verify in the release's template list).
- Section/entry templates: `templateId root="(2\.16\.840\.1\.113883\.10\.20\.22\.[0-9.]+)"\s+extension="([^"]+)"`.

## ASC X12
- Files: `**/*.{edi,x12,837,835,270,271,276,277,278,834,820,txt}`.
- The element separator is the **4th character** of the file (`ISA*` ⇒ `*`). With `*`:
  - `ISA12`: `ISA(?:\*[^*]*){11}\*([0-9]{5})` (e.g. `00501`)
  - `GS08`: `GS(?:\*[^*~]*){7}\*([0-9A-Z]+)` (e.g. `005010X222A1`)
  - `ST03`: `ST\*[0-9]{3}\*[^*~]*\*([0-9A-Z]+)`
- If another separator is used, substitute it.

## NCPDP SCRIPT
- `TransportVersion="?>?([0-9.]+)` · `DatatypesVersion="([^"]+)"` · `<Message[^>]*\bversion="([^"]+)"` · `TransactionVersion="([^"]+)"`

## Existing declarations
- `healthcare-profile\.ya?ml`, and interface specs in `docs/` mentioning "HL7 v2.x", "FHIR R4", "C-CDA R2.1", "005010", "SCRIPT 2017071".

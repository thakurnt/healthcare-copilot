# HL7 v2 version notes (engineering quick reference)

> Orientation only — confirm every item in the chapter of the **target** version. HL7 v2 is designed for backward compatibility: later versions add fields at the end, deprecate ("B" = backward compatible) and eventually withdraw ("W") elements.

| Release | Notable for integration engineers |
|---|---|
| 2.1 / 2.2 | Legacy ADT/ORM/ORU still found in older lab and billing systems. No MSH-9 structure component. |
| 2.3 | Very widely deployed baseline (ADT, ORM, ORU, SIU, MDM, DFT). PID-3 used as repeating patient identifier list. |
| 2.3.1 | MSH-9.3 message structure ID introduced; PID-2/PID-4 retained for backward compatibility. Basis for IHE SWF (legacy). Extremely common in production. |
| 2.4 | Conformance/message profiles (MSH-21) formalised; additional query patterns. |
| 2.5 / 2.5.1 | SFT segment; revised ERR segment structure; OML/OMI/OMG order messages; 2.5.1 widely required by public-health and IHE (e.g. SWF.b, lab profiles). |
| 2.6 | Data type refinements (path toward CWE/CNE and DTM). |
| 2.7 / 2.7.1 | CE and TS withdrawn in favour of CWE/CNE and DTM; truncation character added to MSH-2; PRT (participation) and UAC segments. |
| 2.8 – 2.8.2 | Incremental; further deprecations and new trigger events. |
| 2.9 / 2.9.1 | Current publications (2.9.1 published 2024). Few production partners require it yet. |

## Interop rules of thumb
- **Receive liberally:** accept extra fields/components and unknown Z-segments; don't fail on later-version fields you don't need.
- **Send conservatively:** emit only what the partner's version and spec define.
- **ACK in the sender's version**, echoing MSH-10 into MSA-2; choose ERR layout by version.
- **Translation between versions** (e.g. 2.3.1 → 2.5.1): map CE → CWE, TS → DTM where crossing 2.7; move PID-2/PID-4 content into PID-3 repetitions with identifier type codes; check repetition and length limits.

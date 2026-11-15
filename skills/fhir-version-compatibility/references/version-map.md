# FHIR version map (orientation — verify on hl7.org/fhir/<version>)

| Label | Version | Package | Notes |
|---|---|---|---|
| DSTU2 | 1.0.2 | hl7.fhir.r2.core | Legacy; some older EHR APIs (e.g. early Argonaut). |
| STU3 | 3.0.2 | hl7.fhir.r3.core | Still in some deployments and older IGs. |
| R4 | 4.0.1 | hl7.fhir.r4.core | First normative content; the dominant production version; most regulatory IGs (US Core, IPS R4 editions, IHE mobile profiles) build on it. |
| R4B | 4.3.0 | hl7.fhir.r4b.core | R4-compatible normative parts; changes mostly in medication definition / evidence resources and SubscriptionTopic. |
| R5 | 5.0.0 | hl7.fhir.r5.core | Published; breaking changes vs R4 in several resources. |
| R6 | ballot | — | Development track; not interchangeable with R5. Only target when explicitly requested. |

## Common R4 → R5 traps (non-exhaustive)
| Area | R4 | R5 |
|---|---|---|
| MedicationRequest / MedicationStatement | `medication[x]` (CodeableConcept \| Reference) | `medication` (CodeableReference) |
| Encounter | `class` Coding; `period`; `hospitalization` | `class` CodeableConcept[]; `actualPeriod`; `admission` |
| Device use | `DeviceUseStatement` | `DeviceUsage` |
| Subscriptions | channel/criteria-based `Subscription` | topic-based (`SubscriptionTopic`, `SubscriptionStatus`); use Backport IG on R4/R4B |
| ConceptMap | `equivalence` | `relationship` |
| AuditEvent | `type`/`subtype` Coding, `agent.requestor` | restructured (`code`, `category`, `agent.who`) |

Always confirm details on the R5 "Changes from R4" section of each resource page.

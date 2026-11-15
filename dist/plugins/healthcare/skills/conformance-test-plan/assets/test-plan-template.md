# Conformance Test Plan — <system / interface>

**Target versions** (from healthcare-profile.yml):
| Standard | Version / IG / TR3 | Peer | Source |
|---|---|---|---|
| | | | |

## Scope
- In scope actors / transactions / messages / resources / SOP classes:
- Out of scope:

## Test matrix
| ID | Requirement / profile ref (versioned) | Version | Type (positive/negative/edge) | Fixture | Validator | Expected |
|---|---|---|---|---|---|---|

## Edge cases checklist
- [ ] Unknown Z-segments / extensions / private tags tolerated
- [ ] Wrong line endings / encoding / character set
- [ ] Duplicate control IDs / idempotency
- [ ] Older-version message to newer receiver and vice versa
- [ ] Retired transfer syntax / deprecated elements
- [ ] Large payloads (multi-frame, bulk export, big batches)
- [ ] Security: TLS failure, invalid token/scope, audit emitted

## Environment & data
- Synthetic data source:
- Validators and their pinned versions:

## Exit criteria

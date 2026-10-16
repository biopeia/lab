# Lab Request and Target-Authority Boundary v1

**Document type:** Design proposal  
**Lifecycle:** Proposed — not ratified  
**Related issue:** [Lab #330](https://github.com/biopeia/lab/issues/330)  
**Implementation authorization:** Not granted  
**Evidence baseline:** current-main snapshot verified 2026-10-16; exact revisions listed in §9. Historical operation details are identified as historical, not current capability.

## 1. Purpose and limits

This proposal describes the responsibilities and failure boundaries for a Lab-originated request to a Biopeia domain. It does not define an API, schema, wire format, authentication mechanism, permission model, datastore, transport, or executable workflow.

The proposal is subordinate to accepted Biopeia authority and causal contracts. It does not authorize experiments or generalize any existing operation. It exists to identify what a future bounded operation contract must specify and who is competent to decide it.

## 2. Governing distinction

These concepts are not interchangeable:

```text
scientific provenance  != authenticated principal
request identity       != authorization
request acceptance     != owner adoption
owner adoption         != World commit
World commit           != scientific admission of evidence
Observation publication != command or intervention path
```

An intent or request object may record caller-declared context. Unless a separately approved security contract establishes otherwise, its identifiers are descriptive inputs, not proof of identity, authority, membership, or permission.

Run, study, protocol, logical-intervention, per-action, World-transition, and authenticated-principal identities serve different purposes. They must not be aliased or inferred from one another. In particular, a request's `requested_by`/operator label is not authentication; `experiment_id` is not `run_id`; an intervention may have multiple causal actions; and each committed action must correlate to its own World transition under the applicable contract.

## 3. Responsibility boundary

| Participant | Responsibility in a future authorized operation | Must not assume |
|---|---|---|
| Lab | Define the scientific request/protocol context, submit an explicitly scoped request through an approved path, and preserve Lab-owned provenance/evidence. | Authority over target-domain state, target acceptance, authentication, or World commit. |
| Target domain | Validate the request against its own identity, state, revisions, capability, and domain contract; construct and explicitly accept/reject its own state candidate; make authoritative state visible only under the applicable owner/World commit contract. | That caller declarations establish identity, permission, scientific validity, or a committed transition. |
| World | Coordinate required causal participants and ordering; validate the applicable participant/checkpoint references; commit or reject the shared causal transition and coordinate recovery. | Semantic ownership of Lab, Environment, Embodiment, or Organism state; arbitrary execution of a request; deep-copy/adoption of another owner's truth. |
| Observation | Passively project or deliver authorized publications according to its approved contracts. | Dispatch, validate, authorize, or execute an intervention. |
| Frontend | Out of scope for this request contract. | Operational or causal authority. |

The exact validation and adoption interfaces are domain-owned decisions. This proposal does not prescribe a universal target-owner API.

## 4. Conceptual operation lifecycle

The following is a responsibility sequence, not a frozen runtime protocol:

```text
Lab records a proposed request and its scientific provenance
    ↓
an approved security/operational boundary authenticates and authorizes, if required
    ↓
the target authority independently validates applicability and current owner state
    ↓
the target authority accepts or rejects a candidate transition (preparation alone is not authoritative state)
    ↓
World and participating owners apply the operation-specific commit/recovery contract;
owner adoption and the committed cut must not be represented as separate
successful outcomes unless that contract explicitly defines their relationship
    ↓
one coherent committed causal cut is recorded, or no successful new cut results
    ↓
Lab records outcome/provenance; Observation may passively project committed publications
```

No step may be inferred from a prior step. A request being well-formed is not authorization; authorization is not target acceptance; acceptance is not owner adoption; and candidate creation is not World commit. This proposal does not assert a universal order or atomicity model for owner adoption and World commit. Before any operation is executable, its owners must specify whether adoption is staged, transactionally coupled to commit, or recoverable, and what exact record distinguishes committed from uncommitted owner state. Until then, candidate artifacts are non-authoritative and the design makes no claim that an owner mutation before the World record is durable or accepted.

### Rejection and interruption

- **Rejected before causal preparation:** the target owner records or returns rejection according to its approved contract; there is no committed causal transition.
- **Rejected during owner validation/adoption:** the owner rejects or discards the candidate under its approved operation contract. World must not publish a successful next cut for that candidate; any prepared state not bound to a committed cut remains non-authoritative.
- **Interrupted after preparation begins:** the applicable World recovery contract determines the last authoritative committed cut and whether recovery is required. Temporary candidate artifacts are not committed history.
- **Committed:** the causal result is established by World’s committed record plus the required owner references/adoptions, not by a Lab-side success flag.

The concrete durable record, retry/idempotency rules, and evidence for rejected or interrupted attempts remain owner decisions. Do not infer them from timestamps or transport delivery.

## 5. Provenance, authorization, and evidence

Lab provenance answers questions such as which study, protocol, run, request, and action were intended, what configuration was used, and what evidence Lab retained. Authentication establishes a principal through a separately approved security mechanism. Authorization evaluates that principal's permitted operation and scope. These records may be correlated, but none substitutes for another.

Lab is custodian of its scientific/evidence records. Target owners remain authorities for their state and decision evidence. World remains authority for committed causal ordering and cut references. Observation is not the evidence custodian merely because it transports or buffers publications.

Successful technical execution does not establish scientific validity, method equivalence, or admission of evidence. Those remain subject to the designated Lab/scientific review.

## 6. Existing paths and their limits

The following are source observations at the evidence pins in §9, not an approval of new capabilities:

| Existing path | What is present | What it does not establish |
|---|---|---|
| `Lab.InterventionRequest` and `apply_material_transfer` | **Current status at the §9 Lab revision:** the operation fails closed with `MaterialTransferAuthorizationUnsupported` before inspecting owner state, writing checkpoints, or entering World; no verified authorization source is configured. At the historical pre-#344 implementation inspected for this proposal, one specific scalar transfer kept `intervention_id`, `intervention_action_id`, `transition_id`, and optional `run_id` distinct and called owner/World checkpoint paths. That historical path treated operator identity as caller-declared, not authentication. | Current executable material transfer, general Lab-to-domain dispatch, an authentication/authorization contract, or a universal owner-validation interface. The historical path is not a supported executable template; the precise domain-owner adoption boundary remains operation-specific and unresolved. |
| `ExperimentIntent` in Lab PR #329 at reviewed HEAD `97960bc5d643cedcfd6f18c7d55079b8be74487f` | A descriptive, non-executing intent prototype; independent review bounded its identifiers and requester field as caller-declared values. | Authentication, authorization, target-owner acceptance, dispatch, durable provenance, or experiment execution. |
| World durable causal runtime | Coordinates causal cuts, participant/checkpoint references, commit, and recovery under World contracts. | Target-domain semantic ownership or automatic permission to execute a Lab request. |
| Observation in-process publication | Passive bounded publication/projection surfaces and post-commit integration evidence exist. | Durable searchable history, browser access, a command path, or authorization. |

The material-transfer operation is a narrow implementation precedent only. Do not generalize its operation, quantities, local validation, or request fields into a universal Biopeia contract by similarity.

## 7. Open decisions and accountable authority

| Open question | Competent authority | Bounded trigger / required result |
|---|---|---|
| Which principals may request which operations, and how identity is authenticated? | Security/governance owner with the affected domain owners | Before any executable consumer; approve a threat model and explicit authorization contract. No mechanism is selected here. |
| What operation-specific request and validation contract is valid? | Target domain owner; Lab owner for scientific request meaning | For each requested operation, identify accepted state/revision preconditions, rejection cases, and owner adoption evidence. |
| Which participants and durable references are required for the causal transition? | World owner plus each participating state owner | Before implementing a new cross-owner operation; reconcile with current World commit/recovery contracts. |
| What evidence is retained for rejected, interrupted, and committed requests? | Lab owner for Lab evidence; each state owner for its own records; World owner for causal journal | Before an operation becomes executable; preserve provenance without claiming scientific admission. |
| May the current material-transfer implementation be treated as conforming to the proposed generic boundary? | Independent high-risk reviewer, then Lab and affected domain owners | Review the exact source/diff and trace candidate creation, owner validation/adoption, and commit. Until then, treat it only as a bounded existing path, not a template. |

Each future operation needs a separate bounded issue if it requires new executable behavior. A design gap is not itself permission to implement.

## 8. Required adversarial review before implementation

An independent reviewer must inspect the exact proposal and attempt to falsify at least these claims:

1. A caller-controlled identity cannot be mistaken for authenticated authority.
2. Lab provenance/run identifiers cannot silently become authorization or causal identity.
3. A target owner, not Lab or World, controls acceptance and adoption of its semantic state.
4. A failed/rejected candidate cannot be represented as a committed causal cut.
5. Observation remains passive and cannot become a hidden command route.
6. Existing material-transfer behavior is not being generalized beyond its evidenced contract.

Review outcomes and any disagreement must be preserved. A green test suite alone does not satisfy this review.

## 9. Evidence baseline

The following exact `main` revisions were read for this refresh on 2026-10-16. They are independent current-source snapshots, not a compatible-release set or lockfile.

| Repository | Revision inspected |
|---|---|
| Lab | `a057307a6cc49a6dc086f87e11246f13b9376ae1` |
| Observation | `2c506900aa5ad0864eef7f0ce0ed70d7e8e4ea07` |
| World | `2432ea86cb2959b114c9cda0345ff66438f81f1a` |
| Environment | `4eb1f8c3393a7cdbabcfaf35b8630aaf57de20c1` |
| Embodiment | `5019b94fc79ae5672eeee09ba308e382860af931` |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` |
| Organism | `01c788b5844c7dc05b05160392fa9d860eb6fdd3` |

The cross-domain pins are an inspection baseline, not a compatible-release set or an implementation lockfile. Revalidate them before any later implementation.

## 10. Non-goals and non-claims

This proposal does not authorize or implement:

- experiments, interventions, user actions, or automatic dispatch;
- a general authorization or authentication system;
- a schema, API, transport, datastore, browser integration, or deployment;
- durable Observation storage or historical queries;
- generalization of the scalar material-transfer operation;
- scientific claims, equivalence, efficacy, or evidence admission;
- legacy compatibility or Symbiont behavior.

**Design status:** Proposed. The issue remains blocked until the exact proposal receives the required independent adversarial review and competent owners resolve any operation-specific authority conflicts. No implementation is authorized by this document.

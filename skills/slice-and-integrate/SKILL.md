---
name: slice-and-integrate
description: Build a larger feature through independently owned vertical slices and integrate them under one contract. Use when several agents can implement separate end-to-end user behaviors without sharing hot files, and the result needs narrow per-slice proof, one integration owner, batched broad validation, and independent integrated-state review.
---

# Slice And Integrate

Build independently useful end-to-end slices in parallel, then converge them
through one integrator and one final contract.

## Rules

- Assign one lead/integrator to own shared contracts, merge order, seam decisions,
  broad validation, and the final answer.
- Split by user-visible vertical behavior, not architectural layers. Each slice
  must cross the layers it needs and have a narrow independent proof.
- Give every slice explicit file ownership. Never let two owners edit the same
  file or hot lines concurrently.
- Freeze shared contracts while slices run. Route every shared-contract change
  to the integrator; slice owners must not silently redefine a seam.
- Preserve the user's mutation boundary. Review-only or planning agents must not
  implement, merge, publish, or change external state.
- Run the smallest useful proof per slice. Batch broad validation once after
  integration unless a high-risk seam makes an earlier broad check the narrowest
  meaningful proof.
- Require one independent review of the integrated state.

## Workflow

### 1. Define the integration contract

State the complete user behavior in one sentence. Map:

- vertical slices and user-visible outcomes
- shared interfaces, data, and invariants
- dependency and integration order
- files owned by each slice and files reserved for the integrator
- narrow proof per slice
- final cross-slice journey and batched integration gate
- mutation, merge, and publication authority

Reject a proposed split when a slice cannot produce independently testable
behavior or when safe file ownership is impossible.

### 2. Prove the tracer slice

Integrate the smallest end-to-end slice first. Use it to prove the shared seam,
test harness, integration path, and contract assumptions before widening.

If the tracer fails twice on the same path, stop. Classify whether the blocker is
product, harness/bootstrap, transport/environment, or hosted/infra, then revise
the contract or proof surface before assigning more slices.

### 3. Assign slice owners

Give each owner:

- one user-visible slice and acceptance behavior
- exclusive file ownership and read-only shared files
- the current shared contract and prohibited changes
- the narrow proof command or artifact
- required handoff: changes, evidence, assumptions, risks, and validation not run
- a stop condition and route for seam questions

Run slices in parallel only when ownership and contracts isolate them safely.
Schedule waves when capacity is limited. While owners work, let the integrator
prepare seam checks or inspect only unowned areas.

### 4. Prove and integrate each slice

Require each owner to run its narrow proof before handoff. The integrator must
inspect the diff and evidence, reject unauthorized or cross-owned edits, and
merge in dependency order.

Resolve contract drift centrally. After two collisions on the same seam or hot
file, serialize the affected work under the integrator instead of retrying
parallel edits.

### 5. Run the integration gate

After all accepted slices are integrated:

1. test the cross-slice user journey and failure/recovery seams
2. run one batched broad validation gate
3. distinguish slice-local failures from integration or environment blockers
4. record exact commands, results, proof not run, and residual risks

Do not duplicate the broad gate in every slice unless isolation requires it.

### 6. Review the integrated state

Give one fresh reviewer the user goal, integrated artifacts, contracts, diffs,
and validation evidence without the integrator's preferred verdict. Ask for
missed requirements, contract drift, unsafe ownership, cross-slice regressions,
and proof gaps.

Triage findings. If an accepted Blocker or High issue exists, fix it through the
appropriate owner or integrator, rerun the narrow affected proof and integration
gate as needed, then use the full `$second-round` fix/re-review loop.

## Degraded Path

If safe file isolation, worktrees, or concurrency is unavailable, serialize the
slices while preserving vertical boundaries, ownership records, and narrow proof.
If an independent reviewer is unavailable, use a separate CLI or session; as a
last resort perform a clearly separated local review and label it lower confidence.

Never degrade into concurrent editing of shared files or skip the integrated-state
review.

## Stop Conditions

Stop when every accepted slice passes its narrow proof, the integrated user
journey and batched gate pass, and the independent review has no unresolved
Blocker or High finding.

Stop earlier with a classified blocker when the feature cannot be safely sliced,
the tracer cannot prove the contract, required authority is unavailable, or
integration proof cannot run. Do not use this workflow for fully dependent
pipeline stages or contributors jointly writing one canonical artifact.

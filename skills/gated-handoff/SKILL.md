---
name: gated-handoff
description: Transfer dependent work between agents through receiver-owned acceptance gates. Use when running a two-agent handoff or a multi-stage research, design, implementation, review, or verification pipeline where downstream work must inspect raw artifacts and proof before accepting upstream claims.
---

# Gated Handoff

Advance dependent work only when the next owner accepts the incoming artifact
and evidence. Treat producing an artifact and accepting it as separate acts.

## Rules

- Assign one lead to define stages, resolve repeated rejection, and own the final
  outcome.
- Preserve user authority at every stage. A sender cannot grant a receiver more
  permission than the user granted; mark each stage as read-only, advisory, or
  mutation-authorized before work starts.
- Give the receiver sole ownership of acceptance. The sender may claim readiness
  but must not mark its own handoff accepted.
- Give receivers raw artifacts and proof, not only summaries.
- Require a precise acceptance behavior. Run mutating proof or fixes only when
  authorized; otherwise inspect non-mutating evidence and report the unverified
  condition.
- Route rejection back one stage. Do not skip a failed gate or let downstream
  work hide an upstream gap.

## Workflow

### 1. Design the gates

State the end behavior in one sentence. For every stage, define:

- owner and permitted actions
- required input and raw artifacts
- output contract
- narrow acceptance proof
- receiver and acceptance authority
- rejection and rollback path

Use independent parallel work only inside a stage when its parts do not depend
on one another. Keep the stage transitions sequential.

### 2. Produce the handoff packet

Require the sender to provide:

- goal and current state
- artifacts, changed files, and exact commands
- evidence already collected and proof not run
- decisions, assumptions, and failed paths
- open risks and the next narrow proof
- mutation or external-action authority that remains

Preserve exact error signatures and links or paths to raw evidence. Do not claim
completion merely because the packet exists.

### 3. Let the receiver accept or reject

Have the receiver inspect the raw artifacts and run the narrow acceptance proof
when authorized. The receiver must return one result:

- `Accept`: cite the proof and state the next owned action.
- `Accept with risk`: cite the proof, name the bounded residual risk, and confirm
  that the stage contract permits it.
- `Reject`: name the exact missing or failed condition and route it back.
- `Blocked`: classify the blocker and identify the unavailable proof or authority.

Permit one clarification exchange for ambiguous evidence. Do not let the sender
argue a failed proof into acceptance.

### 4. Repair rejected gates

Return a rejection to the sender or previous responsible stage. Keep repairs
scoped to the failed condition and rerun the same acceptance behavior.

After the same gate rejects twice for the same reason, stop repeating the path.
Classify the blocker and redesign the contract, evidence surface, or stage
boundary before another attempt.

### 5. Close the pipeline

After all stage gates pass, have the final receiver run one end-to-end integration
gate. Report accepted stages, proof run, proof not run, residual risks, and any
authority that prevented stronger validation.

## Degraded Path

If subagents are unavailable, run stages serially in the lead while preserving
separate sender packets and receiver acceptance records. Use a separate CLI or
session for the receiving check when practical; otherwise label the same-agent
acceptance as lower confidence.

If a receiver lacks mutation authority, keep the gate read-only and return the
exact proof that an authorized owner must execute. Never broaden authority to
keep the pipeline moving.

## Stop Conditions

Stop when the final receiver accepts the end behavior and integration proof. A
two-agent handoff may stop when the receiver can accurately state and, when
authorized, execute the next step.

Stop earlier when a gate has a classified blocker, the same rejection occurs
twice without a new evidence surface, or the required authority is unavailable.
Do not use this workflow when stages are independent parallel surfaces or agents
are jointly accumulating one shared artifact.

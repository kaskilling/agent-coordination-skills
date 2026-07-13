---
name: artifact-room
description: Coordinate multiple agents through one governed shared document, plan, decision record, or evidence board. Use when durable shared state should accumulate contributions across agents, provenance and conflicts must remain visible, and the result needs one coherent canonical artifact instead of separate reports.
---

# Artifact Room

Build one durable artifact without concurrent-edit damage. Route every canonical
change through exactly one writer.

## Rules

- Assign one lead to own scope, the write protocol, conflict resolution, and the
  final answer.
- Preserve the user's mutation boundary. Do not turn review, diagnosis, or
  planning authority into permission to edit source files or external systems.
- Choose exactly one write protocol before contributors start:
  1. **Canonical writer:** one agent holds the write lease and all other agents
     send findings or proposed patches to that writer.
  2. **Fragment and integrator:** contributors write separate fragment files and
     exactly one integrator merges them into the canonical artifact.
- Never let two agents edit the canonical artifact concurrently, even when they
  own different sections.
- Give every contributor a distinct section, evidence obligation, and stop
  condition. Preserve source references, uncertainty, and open questions.
- Keep disagreements explicit until the lead resolves them. Do not overwrite or
  silently blend conflicting claims.

## Workflow

### 1. Define the room

State the artifact's purpose and intended consumers in one sentence. Record:

- canonical artifact path or location
- required sections and acceptance criteria
- contributor ownership and mutation authority
- evidence and citation format
- unresolved-question and conflict format
- chosen write protocol and current writer or integrator

Create a small skeleton before delegation so contributors target a stable
structure.

### 2. Collect contributions safely

Require contributors to read the latest canonical artifact before preparing
their input. Ask each contributor to return:

- proposed content or fragment path
- supporting evidence and provenance
- assumptions and confidence
- conflicts with existing content
- open questions and validation not run

Under the canonical-writer protocol, contributors must not edit the artifact;
send their proposals to the leased writer. Under the fragment protocol, assign
non-overlapping fragment paths and forbid contributors from editing the
canonical artifact or another agent's fragment.

Schedule work in waves when contributor count exceeds available capacity. While
contributors work, inspect only unassigned seams or prepare consistency checks.

### 3. Integrate and resolve

Have the sole writer or integrator:

1. verify each contribution against its evidence obligation
2. merge compatible content without losing provenance
3. record material conflicts instead of choosing silently
4. ask the relevant owners one bounded clarification when needed
5. let the lead resolve remaining conflicts against the acceptance criteria

After two exchanges that add no evidence, stop the dispute and record the
missing proof or lead decision.

### 4. Validate and seal

Run one consistency pass over the complete artifact for:

- missing required sections
- terminology and decision consistency
- duplicate or contradictory statements
- broken references and lost provenance
- unresolved questions presented as facts

Ask intended consumers to read back the decisions, next actions, or operating
steps they would take from the artifact. Fix material interpretation gaps through
the sole writer, then mark the artifact sealed with remaining risks.

## Degraded Path

If subagents or safe shared writes are unavailable, preserve the protocol:

- collect contributions serially while keeping earlier authorship and evidence
- use separate fragment files when possible
- otherwise keep one lead as the only canonical writer

State that the topology is degraded. Never compensate by allowing concurrent
canonical edits.

## Stop Conditions

Stop when all required sections meet their criteria, material conflicts are
resolved or explicitly deferred, consumers can correctly use the artifact, and
the sole writer or integrator seals it.

Stop earlier with a classified blocker when required evidence, write safety, or
consumer readback is unavailable. Do not use this workflow for hot-line code
collaboration, blind independent judgment, or isolated vertical implementation
slices.

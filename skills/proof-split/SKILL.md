---
name: proof-split
description: Split an investigation, audit, or research task across multiple orthogonal proof surfaces and synthesize one evidence-backed conclusion without a fix/re-review loop. Use when the user asks for parallel lookups, repo-wide inspection, specialist review lenses, simultaneous research, or faster coverage of separable risks across code, tests, documentation, packaging, devices, environments, or hosted systems.
---

# Proof Split

Partition work by distinct evidence sources, not by arbitrary file count or agent
count. Reconcile the results into one coverage matrix, one conclusion, and one
next proof.

## Rules

- Define the behavior or question that must be proved before delegating.
- Give every proof surface one primary owner. Keep assignments non-overlapping
  except for explicit seam questions.
- Preserve independence. Pass the goal, scope, raw artifacts, and evidence
  contract; do not pass another agent's conclusion before the first report.
- Preserve the user's mutation boundary. Default investigators to read-only.
  Permit edits only when the user authorized changes and give each writer
  exclusive file ownership.
- Do not confuse more agents with more coverage. Use only surfaces that can
  change the conclusion.
- Run independent surfaces concurrently when capacity allows. When capacity is
  limited, run them in waves without changing their scopes or leaking earlier
  conclusions.
- If subagents are unavailable, use separate CLI sessions where possible.
  Otherwise perform clearly separated passes and label the independence as
  degraded.
- After two dead-end attempts on the same command, hypothesis, or recovery
  path, stop and classify the blocker with a taxonomy suited to the task. For
  software systems, start with product, harness/bootstrap,
  transport/environment, or hosted/infra. Pivot to a different surface or a
  higher-signal proof.

## Workflow

### 1. Define The Proof Contract

State the target behavior in one sentence. Record:

- artifacts and systems in scope
- current evidence and the freshest first-failure artifact
- the narrowest command or observation that can move the fact
- mutation authority and forbidden actions
- required surfaces, seam questions, and completion criteria

Hold broad reruns until the narrow proof is current.

### 2. Partition By Proof Surface

Choose orthogonal evidence sources or risk lenses. Common splits include:

- product code, harness/bootstrap, transport/environment, and hosted infra
- implementation, tests, documentation, packaging, and onboarding
- technical accuracy, operator usability, accessibility, and first-user UX
- independent source clusters or domains for research

For every owner, specify primary scope, explicit exclusions, shared seams, raw
artifacts, allowed mutations, and the required report format.

### 3. Dispatch Independent Owners

Ask each owner to return this evidence contract:

```text
Surface:
Conclusion:
Confirmed facts with exact evidence:
Unknowns and classified blockers:
Contradictions or seam risks:
Validation run and result:
Validation not run:
Confidence and why:
Next narrow proof:
```

Require exact paths, line references, commands, outputs, links, or screenshots
where available. Do not accept confidence as a substitute for evidence.

### 4. Work Without Overlap

While owners investigate, let the lead inspect unassigned surfaces, prepare seam
validation, or run cheap non-mutating checks. Do not duplicate an owner's task.

### 5. Reconcile Evidence

Build a coverage matrix with one row per surface and columns for conclusion,
evidence, validation, unknowns, and confidence. Deduplicate repeated findings.

When reports conflict, send only the disputed claim and raw evidence back to the
relevant owners. Ask for one discriminating check. Do not settle factual conflicts
by vote.

### 6. Check Seams

Inspect assumptions that cross ownership boundaries, such as code-to-test,
local-to-device, package-to-install, or documentation-to-command behavior. Run
one narrow integration proof when a seam can invalidate otherwise correct local
findings.

### 7. Close With One Result

Report:

- the reconciled conclusion
- the coverage matrix or concise equivalent
- confirmed facts, contradictions resolved, and classified blockers
- validation performed and validation missing
- the next narrow proof or scoped authorized fix
- the independence level and any capacity-wave limitation

## Stop Conditions

Stop when every required surface has evidence or a classified blocker, all
material contradictions are resolved or bounded, and cross-surface seams have
been checked. Stop earlier when one decisive fact resolves the user question.
Do not widen merely because agents or time remain.

Do not use this skill when agents must defend rival causal explanations, jointly
edit one canonical artifact, or implement parallel slices that need integration
ownership. Use a falsification, artifact-governance, or slice-integration pattern
instead.

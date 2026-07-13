---
name: blind-arbitration
description: Coordinates independent agent submissions through a lead that controls disclosure and adjudicates them against explicit criteria. Use when first-pass judgments must remain uninfluenced, context must be compartmentalized, direct communication is unavailable, or the user wants independent proposals, ranking, selection, or controlled cross-examination.
---

# Blind Arbitration

Preserve independent first passes, expose only the evidence needed for one
controlled challenge, and make a traceable decision against declared criteria.

## Rules

- Keep one lead as the sole information router and final adjudicator.
- Define decision criteria before collecting submissions. Do not change criteria
  merely to favor a proposal after seeing it.
- Give agents the same neutral decision brief unless compartmentalization is an
  explicit constraint. Record any information withheld from an agent.
- Do not disclose another submission, identity, preferred answer, or emerging
  consensus during the blind phase.
- Define mutation authority before delegation. Keep submissions read-only unless
  the user authorized changes; never convert selection work into external writes.
- Require claims to include exact evidence, confidence, assumptions, risks, open
  questions, and validation run or not run.
- Use votes only for subjective preferences. Resolve factual conflicts through
  evidence or a discriminating test.

## Workflow

### 1. Define The Decision Contract

State the decision, candidate scope, hard constraints, weighted criteria, evidence
standard, mutation boundary, and stop condition. Choose two or more agents whose
roles add distinct expertise without assigning them a preferred outcome.

### 2. Collect Blind Submissions

Send the decision contract to every agent independently. Ask each to return:

- proposal or conclusion
- criterion-by-criterion case
- source-backed evidence and confidence
- assumptions, tradeoffs, failure modes, and reversibility
- validation performed, missing proof, and one decisive follow-up question

Collect every first pass before relaying any submission. If agents exceed the
available slots, run them in waves or sequentially while withholding all earlier
answers. State the degraded capacity, but preserve blindness.

### 3. Build The Evidence Ledger

Normalize submissions without erasing material differences. Record each claim,
evidence, confidence, assumptions, criterion score, and dissent. Remove duplicates
and separate factual conflicts from different value judgments.

Reject unsupported certainty. Do not let eloquence, agent count, or proposal order
stand in for evidence.

### 4. Cross-Examine Once

If a material conflict remains, relay only the minimum opposing claim, evidence,
or question needed to test it. Do not reveal unrelated submissions or a running
ranking. Give each affected agent one response and require new evidence, a revised
claim, or a precise reason the evidence is unavailable.

After two dead ends on one proof path, classify the blocker and pivot to a
higher-signal artifact or reversible experiment.

### 5. Adjudicate

Apply the declared criteria to the evidence ledger. Select, synthesize, or defer.
Preserve minority findings and explain rejected proposals against the criteria.
When evidence cannot distinguish finalists, prefer the cheapest reversible test
instead of manufacturing certainty.

### 6. Close With Evidence

Report the decision contract, submissions considered, information withheld during
the blind phase, decisive evidence, criterion-by-criterion result, dissent,
validation gaps, and next narrow proof. If authorized implementation follows,
assign it separately and keep broad validation batched.

## Stop Conditions

Stop after one blind submission per agent and at most one controlled
cross-examination, or earlier when decisive evidence resolves the choice. Preserve
unresolved dissent. Do not use this skill for open peer conversation, causal
diagnosis through rival experiments, or joint editing of one artifact.

## Example

“Use `$blind-arbitration` to collect three independent architecture proposals,
cross-examine the finalists once, and choose against these constraints.”

---
name: hypothesis-duel
description: Diagnose a hard failure by assigning agents competing causal hypotheses and requiring discriminating tests, self-falsification, and evidence-based challenge. Use when several plausible causes exist, evidence conflicts, the team is anchored on one theory, or two repeated recovery attempts have failed to move the fact.
---

# Hypothesis Duel

Make rival explanations predict different observations, then run the cheapest
tests that can eliminate them. Finish with one surviving cause or a sharply
bounded unknown; never diagnose by vote.

## Rules

- Capture the freshest first-failure artifact before proposing causes.
- State hypotheses so evidence can distinguish them. Merge hypotheses that make
  identical predictions.
- Preserve independence during the first pass. Give each owner the failure,
  raw evidence, constraints, and one hypothesis; do not reveal another owner's
  defense.
- Require every owner to try to disprove its assigned hypothesis, not advocate
  for it.
- Preserve the user's mutation boundary. Default experiments to non-mutating.
  Run fixes or destructive probes only when explicitly authorized.
- Prefer the smallest reversible experiment that changes the odds between rival
  explanations. Hold broad reruns until that proof is current.
- Run hypothesis owners concurrently when capacity allows. When capacity is
  limited, run blind first passes in waves and withhold earlier conclusions.
- If subagents are unavailable, use separate CLI sessions where possible.
  Otherwise perform separated local passes and label independence as degraded.
- After two dead-end attempts on the same command, hypothesis, or recovery
  path, stop. Classify the blocker as product, harness/bootstrap,
  transport/environment, or hosted/infra, then pivot to a different surface or
  a higher-signal test.

## Workflow

### 1. Establish The Failure

State the observable failure and expected behavior. Record:

- exact reproduction or first-failure artifact
- environment and relevant state
- validation already run and validation missing
- mutation authority, cost limits, and unavailable surfaces
- the narrowest current proof command or observation

Separate confirmed facts from interpretations.

### 2. Form Rival Hypotheses

For each plausible cause, write:

```text
Hypothesis:
Causal mechanism:
Predicted observation if true:
Observation that would falsify it:
Cheapest discriminating test:
Required surface or artifact:
```

Prefer two to four materially different hypotheses. Include product,
harness/bootstrap, transport/environment, and hosted/infra explanations when
the system crosses those boundaries.

### 3. Assign Independent Owners

Give one hypothesis to each owner. Require this evidence contract:

```text
Hypothesis tested:
Strongest supporting evidence:
Strongest disconfirming evidence:
Self-falsification attempted and result:
Material rival and its strongest falsifier:
Commands or artifacts inspected:
Validation not run:
Updated confidence and why:
Next discriminating test:
```

Do not let owners edit the same files. If authorized fixes become useful, wait
until the cause is selected or assign exclusive ownership.

### 4. Run Discriminating Tests

Rank proposed tests by information gain, cost, reversibility, and environmental
truth. Run the cheapest test that predicts different outcomes across surviving
hypotheses. Use complementary surfaces deliberately: local or emulator for fast
bootstrap checks, real device or production-like targets for environment truth,
and hosted automation for wider confirmation.

### 5. Cross-Challenge Material Evidence

After blind first reports, share only evidence that changes a prediction or the
likelihood of a hypothesis. Ask the relevant owners to explain the same artifact
or propose one decisive check. Bound this to one challenge round unless new
evidence creates a genuinely new hypothesis.

Reject explanations that require ignoring confirmed evidence. Keep multiple
hypotheses alive when the available test cannot distinguish them.

### 6. Decide Or Bound The Unknown

Select a cause only when it survives falsification better than its rivals.
Record the minimal reproduction and causal chain. If proof is unavailable,
identify exactly which observation is missing, why it is unavailable, and which
survivors remain.

If fixes are authorized, apply the smallest causal fix and run the test that
previously distinguished the winning hypothesis. Do not treat an unrelated green
rerun as causal proof.

### 7. Close With Evidence

Report:

- the surviving explanation or sharply bounded unknown
- rejected hypotheses and their falsifying evidence
- discriminating tests run and exact results
- blocker classification and any surface pivot
- validation not run and residual risk
- the next narrow proof or authorized causal fix
- independence level and any capacity-wave limitation

## Stop Conditions

Stop when one explanation survives falsification and its causal prediction is
confirmed; when all survivors require the same unavailable proof; or when the
blocker is classified strongly enough to choose a different surface. Stop a
path after two dead ends. Never settle the diagnosis by majority vote.

Do not use this skill for independent coverage with no rival causes, or for an
implementation review after the cause is already known. Use a proof-surface or
adversarial-review pattern instead.

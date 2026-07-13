# Quick Usage Guide

Invoke one strategy with `$skill-name`, followed by the task. Choose the smallest
coordination pattern that fits; do not launch the whole collection for every job.

## Pick the skill

### `$second-round`

Use after a first pass exists and you want an independent reviewer to find gaps,
fix accepted findings, and review the corrected result.

```text
$second-round review this implementation critically, fix real issues, and re-review it
```

### `$peer-deliberation`

Use when two specialists should talk directly, challenge each other, and converge
on one evidence-backed position.

```text
$peer-deliberation have an API designer and mobile engineer debate this contract for three exchanges
```

### `$blind-arbitration`

Use when proposals or judgments must remain independent until the lead compares
them against explicit criteria.

```text
$blind-arbitration collect three independent architecture proposals and adjudicate them against these constraints
```

### `$proof-split`

Use when one investigation can be divided into independent evidence surfaces such
as code, tests, documentation, devices, packaging, or CI.

```text
$proof-split inspect product code, test harness, CI artifacts, and docs in parallel, then synthesize one conclusion
```

### `$hypothesis-duel`

Use when several causes could explain one failure and agents should try to falsify
competing hypotheses with discriminating tests.

```text
$hypothesis-duel determine whether this failure is product, bootstrap, transport, or hosted infrastructure
```

### `$artifact-room`

Use when several contributors must build one durable document or decision record.
It enforces one canonical writer or separate fragments with one integrator.

```text
$artifact-room have product, engineering, and operations build one decision record with separate fragments
```

### `$gated-handoff`

Use when dependent work passes from one owner to the next and every receiver must
inspect the artifacts and accept the incoming proof.

```text
$gated-handoff move this work through diagnosis, implementation, and verification gates
```

### `$slice-and-integrate`

Use when a feature can be split into independently testable vertical slices with
exclusive file ownership, one integrator, and one final integration review.

```text
$slice-and-integrate divide this feature into user-visible slices, prove each narrowly, then run one integration gate
```

## Useful combinations

- Start with `$proof-split`; use `$hypothesis-duel` only if the surfaces reveal
  genuinely competing causes.
- Build with `$slice-and-integrate`; finish with `$second-round` when the integrated
  result needs an adversarial review/fix/re-review loop.
- Build a durable plan with `$artifact-room`; execute dependent stages with
  `$gated-handoff`.

Keep one lead responsible for scope, permissions, integration, and the final answer.

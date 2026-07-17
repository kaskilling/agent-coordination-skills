# Confirmatory v3: outcome-aware, harness-repaired direct replication

Status: **freeze before every v3 corpus model call**. This directory, its
dedicated runner, analyzer, tests, and protocol lock must be merged to `main`
and tagged `confirmatory-v3-preregistered` before execution.

## Why a third execution exists

Confirmatory v1 and v2 are both invalid and excluded. V1 failed deterministic
process isolation. V2 completed its schedule, but 26 pre-session cloud-config
transport failures and nine per-trial timeouts left 35 assigned outcomes without
a terminal agent opportunity; the frozen analyzer correctly refused it. See
the [v2 execution disposition](../confirmatory-v2/EXECUTION-STATUS.md).

V2 behavioral outcomes were inspected during diagnosis. V3 is therefore an
**outcome-aware, prospectively frozen, harness-repaired direct replication**.
It is not described as a blind primary or as a recovery that replaces v2.

## Research question and claim boundary

When Codex receives a strict `use if and only if` activation boundary in a skill
description, does it use CIB's exact designated canary when that coordination
strategy is required and avoid it when a neighboring strategy is the better fit?

If every operational and adverse-sensitivity gate passes, v3 supports only:

> During the recorded execution window, under the recorded Codex model alias,
> backend, settings, and this fixed 64-pair, 128-prompt corpus, strict
> conditional skill-description wording improved false-case resource avoidance
> over plain conditional wording without more than a 0.10 necessary-use loss,
> while meeting the declared absolute routing, missingness-sensitivity, and
> integrity guardrails in an outcome-aware direct replication.

It does not establish behavior for other models, agents, placements, skill
bodies, future model versions, arbitrary prompts, or real workflow quality.

## Frozen design

- Corpus and taxonomy: the eight v1 configs' 64 matched pairs and 128 prompt
  strings, plus their unanimous blind taxonomy evidence. V3 config semantics are
  byte-equivalent to v1 except the two declared runtime limits below.
- Target: Codex through CIB v0.5.3's Promptfoo Codex SDK backend at release
  commit `e9e77bfd598319fe0d7049c74943c15f556a61ac`.
- Runtime: Promptfoo 0.121.19, Codex SDK 0.144.5, model alias `gpt-5.6-sol`,
  reasoning effort `medium`, and placement `skill_description`.
- Arms: mandatory plain `if`, strict `if and only if`, and expanded
  `if + else-not`.
- Scale: three repetitions for each family × pair × arm × truth cell; 144
  primary assignments per family and 1,152 total.
- Randomization: master seed `20260717`, the unchanged eight v1 family seeds,
  and unchanged shuffled family order.
- Scheduling: eight jobs within a family and exactly one family at a time.
- Limits: 600 seconds per trial and 3,000 seconds per family. The longer trial
  limit addresses the nine observed v2 deadline failures; the shorter family
  ceiling bounds cache age and total invalid-run exposure.
- Retry and replacement: none. After global preflight, all eight families are
  attempted exactly once in frozen order even after an earlier family error. No
  rerun may replace, resume, substitute, or supplement a primary family.

These runtime changes are informed by v2 failure evidence. No task, arm, seed,
model setting, estimator, posterior threshold, absolute threshold, or family
consistency threshold changes.

## Excluded cache bootstrap

Immediately before each family, the runner makes one excluded Codex SDK call in
a dedicated private bootstrap home. Its only prompt asks for `READY`; it is not
from the corpus and never enters behavioral analysis. The runner requires the
resulting signed cloud-config cache to have at least 3,300 seconds remaining,
records only its SHA-256 digest, integer format version, timestamps, duration,
and call count, and passes its exact bytes to CIB as an explicit seed.

CIB creates a fresh HOME and CODEX_HOME for every primary trial, writes the
seeded cache with private permissions, rechecks freshness immediately before
execution, and reports post-run digest equality. Each family is valid only if
all 144 trial copies are present and unchanged. The accounting is eight excluded
warmups plus 1,152 primary model calls. There is no ambient cache discovery,
retry, or replacement. Bootstrap homes, caches, logs, prompts, nonces, sessions,
and raw results remain ignored private state.

Before freeze, one non-confirmatory `READY` warmup exercised this exact path
outside the corpus and repository. It completed in 11.692 seconds, created one
regular 0600 signed-format cache, exposed an integer cache version, and met the
3,300-second minimum. It is operational bootstrap evidence only and is not one
of v3's eight scheduled warmups or 1,152 primary calls.

## Operational estimand

The co-primary estimand is the end-to-end assignment effect—an operational
intention-to-treat analogue. Every assigned row remains in its frozen cell.
Exact canary success is one; a typed harness failure is zero because the assigned
policy did not produce the required end-to-end success. A family is structurally
invalid, and analysis refuses, for missing/duplicate assignments, untyped
failure, session or identity violations, scorer disagreement, whole-study
timeout, artifact mutation, or runtime/protocol drift.

For each of 64 fixed family × pair indices, the primary contrasts are:

1. false-case superiority: avoided unnecessary use(`iff`) minus avoided
   unnecessary use(`if`);
2. true-case non-inferiority: necessary use(`iff`) minus necessary use(`if`),
   margin -0.10.

Every family × pair × arm × truth cell has an independent `Beta(0.5, 0.5)`
prior. Three assigned outcomes update each cell. Simulation starts at 200,000
draws with NumPy 2.4.1 PCG64 seeds `20260717` and `20260718` in 10,000-draw
chunks. Both seeds must agree on classifications and primary probabilities
within 0.001; otherwise draws double to at most 1,600,000. Nonconvergence makes
the analysis invalid.

## Co-primary operational and adverse gates

The operational result must pass all five wording gates:

- posterior probability of positive false-case difference is at least 0.975;
- posterior probability of true-case difference above -0.10 is at least 0.975;
- equal-family strict necessary-use rate is at least 0.80;
- equal-family strict avoided-unnecessary-use rate is at least 0.80;
- at least six of eight families have a positive observed false-case contrast.

It must also have pooled typed harness missingness at most 0.05, valid evidence
for all families, and exact cache-seed integrity. There is no post-outcome
per-family missingness threshold; every family remains visible and weighted.

The same five wording gates must pass a frozen adverse sensitivity scenario.
For every typed missing outcome under either truth value, strict `iff` receives
zero and plain `if` receives one. This is the worst assignment for the claimed
strict-minus-plain contrast. Expanded-arm missing outcomes remain zero and do
not enter a confirmatory wording gate. Confirmation requires every operational
and adverse gate.

## Descriptive and secondary analysis

A behavioral complete-case view divides exact successes by rows with a terminal
agent opportunity, by family, arm, and truth. It is explicitly descriptive and
non-gating. Expanded-arm operational contrasts and a `Beta(1, 1)` posterior
sensitivity are also non-gating. None may rescue a failed confirmatory gate.

Equal-tail 95% credible intervals are model-based uncertainty conditional on
this fixed corpus and the cell-level independence and stationarity assumptions.
The purposive skills and prompts are not a random sample from a larger universe.

## Integrity and stopping rules

- The runner refuses dirty or wrong commits, missing freeze tag equality,
  runtime or lockfile drift, existing output, non-sequential scheduling, and
  non-private bootstrap provenance.
- A typed `pre_session_transport` or `per_trial_timeout` row remains an assigned
  operational zero and enters the adverse analysis.
- An untyped failure, whole-study timeout, incomplete/duplicate assignment,
  missing required session, duplicate session, identity disagreement, scorer
  disagreement, changed cache copy, or artifact-hash disagreement is invalid.
- After preflight, a family error does not alter the frozen schedule: all eight
  attempts continue exactly once. Any structural error still blocks aggregation.
  A manual or global interruption leaves an incomplete invalid execution.
- The analyzer runs once after the complete primary schedule. Failure of a gate
  is a valid negative result; analysis refusal is an invalid study.

## Reproduction

Prepare the exact environments:

```sh
cd /path/to/conditional-instruction-benchmark
git checkout e9e77bfd598319fe0d7049c74943c15f556a61ac
uv sync --frozen
npm ci

cd /path/to/agent-coordination-skills
python3 -m venv .venv-confirmatory
.venv-confirmatory/bin/python -m pip install --disable-pip-version-check \
  -r studies/confirmatory-v3/requirements.txt
```

After the merged freeze tag and before inspecting any v3 outcome:

```sh
.venv-confirmatory/bin/python scripts/run_cib_confirmatory_v3.py \
  --cib-root /path/to/conditional-instruction-benchmark \
  --output-root results/confirmatory-v3-primary \
  --parallel-studies 1

.venv-confirmatory/bin/python scripts/summarize_cib_confirmatory_v3.py \
  results/confirmatory-v3-primary \
  --output results/confirmatory-v3-primary/aggregate.json
```

Only the sanitized aggregate and a report derived from it are publishable.

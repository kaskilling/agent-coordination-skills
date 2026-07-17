# Confirmatory v1: conditional routing across eight coordination skills

Status: **frozen before model calls** once this directory is merged to `main`.

## Research question

When Codex receives a strict `use if and only if` activation boundary in a skill
description, does it use CIB's exact designated canary when that coordination
strategy is required and avoid it when a neighboring strategy is the better fit?

This study tests routing under eight encoded task families. It does not test
whether the real coordination skill was discovered, whether subagents were
spawned, or whether the full skill body was followed.

## Fixed design

- Target: Codex through CIB v0.5.0's Promptfoo Codex SDK backend at release
  commit `84126513f487df605b45f8bb4286246ba1801e5a`.
- Recorded model alias: `gpt-5.6-sol`; reasoning effort: `medium`. The provider
  exposes no immutable weight snapshot through this interface, so this freezes
  the requested alias and execution time, not unobservable model weights.
- Placement: `skill_description`.
- Families: all eight public skills in this repository.
- Cases: eight matched required/unnecessary prompt pairs per family. Seven
  negatives cover each neighboring skill exactly once; one is a null task that
  requires no multi-agent coordination.
- Repetitions: three per case pair.
- Arms: CIB's mandatory `if`, `if and only if`, and expanded
  `if + else-not` arms.
- Trials: 144 per family and 1,152 total.
- Randomization master seed: `20260717`. Each family uses the distinct seed
  frozen in `protocol-lock.json`, derived as the first four SHA-256 bytes of
  `cib-confirmatory-v1:<master>:<family>` modulo 2,147,483,647. This prevents
  concurrent families from sharing the same arm/truth execution permutation.
- Execution: eight jobs per family, at most four family studies in parallel.
  Family submission order is shuffled once with seed `20260717` and recorded in
  `protocol-lock.json`.
- Limits: 300 seconds per trial and 5,400 seconds per family study.
- Recovery runs: excluded from primary evidence and reported separately.

Each family owns a separate CIB config in `configs/`. The merge commit containing
this preregistration, the configs, the runner, and `protocol-lock.json` is the
freeze point. No case, threshold, model, seed, arm, or analysis rule changes are
allowed after the first model call. Deviations must be appended and labeled
before inspecting outcomes when possible.

## Primary estimands and decision rule

The selected policy is the strict `iff` arm.

For every family and fixed prompt pair, CIB estimates:

1. necessary use: exact canary success when the condition is true;
2. avoided unnecessary use: exact canary non-use when the condition is false;
3. harness-failure rate across all mandatory arms.

The finite-corpus causal estimands are the equal-family, equal-prompt
differences between strict `iff` and plain `if` across the 64 matched prompt
pairs (128 prompt strings):

- false-case superiority: avoided-unnecessary-use(`iff`) minus
  avoided-unnecessary-use(`if`);
- true-case non-inferiority: necessary-use(`iff`) minus necessary-use(`if`),
  with margin -0.10.

CIB randomizes execution order but does not randomly assign wording labels
within a block. Therefore this protocol does **not** call an arm-label
permutation test design-based randomization inference. Conditional runtime
uncertainty is estimated with a frozen Jeffreys-binomial model: every
family × prompt-pair × arm × truth cell has an independent `Beta(0.5, 0.5)` prior;
the observed three repetitions update that cell; posterior simulation starts at
200,000 draws with seeds `20260717` and `20260718`; each draw weights the 64
fixed pair indices equally within each truth condition. Both seeds must produce
the same gate classifications and
primary probabilities within 0.001. Sampling uses NumPy 2.4.1's PCG64 generator
in fixed 10,000-draw chunks. Otherwise draws double for both seeds up to
1,600,000; failure to converge by that bound makes the analysis invalid.

The collection-level result is **confirmed** only if all of these hold:

- posterior probability that the false-case difference is greater than zero
  is at least 0.975;
- posterior probability that the true-case difference is greater than -0.10
  is at least 0.975;
- the equal-family-weighted strict necessary-use rate is at least 0.80;
- the equal-family-weighted strict avoided-unnecessary-use rate is at least 0.80;
- at least six of eight families have a positive observed false-case strict
  minus plain contrast;
- the pooled harness-failure rate is at most 0.05;
- no family has invalid evidence.

These are co-primary gates: failure of any gate prevents the confirmatory claim.
The exact family outcomes and all failures remain visible; no family is dropped.

## Uncertainty and secondary contrasts

Equal-tail 95% credible intervals come from the same 200,000 posterior draws.
They quantify repeated Codex runtime uncertainty conditional on the fixed 64
matched prompt pairs (128 prompt strings). They do not turn the eight repository
skills or purposively
written prompts into a random sample from a larger population.

Secondary, non-gating contrasts use equal family weighting:

- strict `iff` minus plain `if` for necessary use;
- strict `iff` minus plain `if` for avoided unnecessary use;
- expanded `if + else-not` minus strict `iff` in both truth conditions.

The expected diagnostic pattern is little necessary-use loss for strict versus
plain wording, higher avoided-unnecessary-use for strict wording, and similar
behavior between strict and expanded wording. Expanded-arm contrasts and a
`Beta(1, 1)` prior sensitivity are non-gating. These contrasts explain routing;
they do not replace the primary gates and receive no confirmatory p-value.

## Missingness and integrity

- A per-trial timeout is a harness failure and stays in its assigned cell.
- A whole-study timeout makes that family invalid and blocks confirmation.
- Missing, duplicate, identity-disagreeing, or scorer-disagreeing rows make the
  family invalid and block confirmation.
- A failed family may be rerun only as an explicitly labeled recovery run. Its
  result does not replace primary evidence.
- Public summaries contain only CIB's sanitized aggregate reports. Prompts,
  nonces, sessions, raw transcripts, credentials, and workstation paths remain
  in ignored local `results/` state.

## Pre-freeze taxonomy gate

Before the freeze commit, two fresh reviewers independently receive the 128
prompt strings in randomized order with opaque IDs and no target labels. Each
must classify every prompt as one of the eight skills or `null`. The required
prompt in every pair must classify as the target skill; the unnecessary prompt
must classify as the declared neighboring skill or null, which demonstrates
that use of the target resource would violate the encoded boundary.

Any disagreement is rewritten and reviewed again before model calls. After two
failed rewrites, the edge is replaced before freeze by a second clean scenario
from the closest competitor and disclosed. No prompt may be replaced after a
model call. `taxonomy-contract.json` freezes the directed competitor order;
the blind packet, answer key, and review results are retained as protocol
evidence without exposing reviewer identities in the scientific claim.

## Claim boundary

A confirmed result supports only this sentence:

> Under the recorded Codex model alias, backend, settings, execution window,
> and this fixed 64-pair, 128-prompt corpus,
> strict conditional skill-description wording improved false-case resource
> avoidance over plain conditional wording without more than a 0.10 necessary-use
> loss, while meeting the declared absolute routing and integrity guardrails.

It does not establish general behavior for other models, agents, placements,
skill bodies, future model versions, arbitrary prompts, or actual multi-agent
workflow quality.

## Execution and analysis

Prepare the exact execution and analysis environments:

```sh
cd /path/to/conditional-instruction-benchmark
git checkout 84126513f487df605b45f8bb4286246ba1801e5a
uv sync --frozen
npm ci

cd /path/to/agent-coordination-skills
python3 -m venv .venv-confirmatory
.venv-confirmatory/bin/python -m pip install --disable-pip-version-check \
  -r studies/confirmatory-v1/requirements.txt
```

The runner rejects dirty CIB and study checkouts, verifies the imported CIB
origin plus CIB, Promptfoo, and Codex SDK versions, records Node, npm, Python,
dependency versions and CIB lockfile hashes, and checkpoints `run-index.json`
before and after each family. An interrupted or incomplete index cannot enter
the primary analysis.

Then, from this repository:

```sh
.venv-confirmatory/bin/python scripts/run_cib_confirmatory.py \
  --cib-root /path/to/conditional-instruction-benchmark \
  --output-root results/confirmatory-v1-primary \
  --parallel-studies 4

.venv-confirmatory/bin/python scripts/summarize_cib_confirmatory.py \
  results/confirmatory-v1-primary \
  --output results/confirmatory-v1-primary/aggregate.json
```

The runner refuses an existing output directory. The summarizer validates the
eight-family inventory, reconstructs prompt pair as `case_variant % 8` and
repetition as `case_variant // 8`, and requires exactly three observations per
prompt × arm × truth cell. It reads canonical local summaries but writes only
sanitized aggregate results.

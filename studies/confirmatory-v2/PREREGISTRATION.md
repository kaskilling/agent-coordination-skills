# Confirmatory v2: clean execution replication after a deterministic harness failure

Status: **frozen before v2 model calls** once this directory and its dedicated
scripts are merged to `main` and tagged `confirmatory-v2-preregistered`.

## Why a new study exists

Confirmatory v1's scientific protocol was frozen correctly, but its first
execution was invalid. Multiple Promptfoo processes shared one SQLite database,
and the canary assertion bridge selected a system Python that could not import
CIB. The index remained incomplete, so the preregistered analyzer rejects it.
Inspection was limited to diagnosing why the run was invalid; no partial
behavioral result changes this protocol.

This is a new primary study, not a recovery run that replaces v1. It preserves
the exact v1 prompts, case pairing, wording arms, seeds, thresholds, model alias,
and analysis. Its only changes are the repaired CIB v0.5.1 execution layer and
lower between-family concurrency.

## Research question and claim

When Codex receives a strict `use if and only if` activation boundary in a skill
description, does it use CIB's exact designated canary when that coordination
strategy is required and avoid it when a neighboring strategy is the better fit?

A confirmed result supports only this sentence:

> Under the recorded Codex model alias, backend, settings, execution window,
> and this fixed 64-pair, 128-prompt corpus, strict conditional
> skill-description wording improved false-case resource avoidance over plain
> conditional wording without more than a 0.10 necessary-use loss, while
> meeting the declared absolute routing and integrity guardrails.

It does not establish general behavior for other models, agents, placements,
skill bodies, future model versions, arbitrary prompts, or actual multi-agent
workflow quality.

## Frozen design

- Corpus: the byte-identical eight v1 config files and their 64 matched prompt
  pairs, whose hashes are repeated in `protocol-lock.json`.
- Taxonomy: the byte-identical v1 blind packet, answer key, two independent
  unanimous reviews, and check result. All 128 prompt strings passed before v1
  and are not rewritten for v2.
- Target: Codex through CIB v0.5.1's Promptfoo Codex SDK backend at release
  commit `eebdbfc84206c594db2d61cf883325e2d8e1b07d`.
- Runtime: Promptfoo 0.121.19, Codex SDK 0.144.5, model alias `gpt-5.6-sol`,
  reasoning effort `medium`, and placement `skill_description`.
- Arms: mandatory `if`, `if and only if`, and expanded `if + else-not`.
- Repetitions: three for each family × pair × arm × truth cell.
- Scale: 144 trials per family and 1,152 trials total.
- Randomization: master seed `20260717`, the unchanged eight v1 family seeds,
  and unchanged shuffled family submission order.
- Within-family execution: eight jobs.
- Between-family execution: exactly two studies in parallel, reduced from four
  to lower unrelated transport pressure. This changes scheduling, not the
  corpus, assignment, estimator, or decision rule.
- Limits: 300 seconds per trial and 5,400 seconds per family.
- Recovery runs: excluded from primary evidence and reported separately.

CIB v0.5.1 gives each run a unique Promptfoo state directory, pins the canary
bridge to CIB's active Python interpreter, and disables telemetry without
suppressing the JSONL evidence export. Before this freeze, a non-confirmatory
composition gate ran two simultaneous six-trial CIB→Promptfoo→Codex checks.
Both exited zero with 12/12 audited successes, distinct healthy databases, and
no harness, timeout, SQLite, import, scorer, or archive-identity failures. Those
smoke prompts are not part of this corpus or its evidence.

## Primary estimands and co-primary gates

The selected policy is strict `iff`. For each fixed prompt pair, necessary use
is exact canary success when true and avoided unnecessary use is exact canary
non-use when false.

The finite-corpus causal contrasts weight the 64 pair indices equally:

1. false-case superiority: avoided unnecessary use(`iff`) minus avoided
   unnecessary use(`if`);
2. true-case non-inferiority: necessary use(`iff`) minus necessary use(`if`),
   with margin -0.10.

Every family × pair × arm × truth cell has an independent `Beta(0.5, 0.5)`
prior. Three repetitions update each cell. Posterior simulation starts at
200,000 draws using NumPy 2.4.1 PCG64 seeds `20260717` and `20260718` in fixed
10,000-draw chunks. Both seeds must agree on gate classifications and primary
probabilities within 0.001. Otherwise both double up to 1,600,000 draws; failure
to converge makes the analysis invalid.

The collection is confirmed only if all gates pass:

- posterior probability of positive false-case difference is at least 0.975;
- posterior probability of true-case difference above -0.10 is at least 0.975;
- equal-family strict necessary-use rate is at least 0.80;
- equal-family strict avoided-unnecessary-use rate is at least 0.80;
- at least six of eight families have a positive observed false-case contrast;
- pooled harness-failure rate is at most 0.05;
- every family has valid evidence.

Equal-tail 95% credible intervals come from the same draws. They are model-based
posterior uncertainty for hypothetical repeated isolated calls under the
cell-level Beta-Binomial independence and stationarity assumptions, conditional
on this fixed corpus. They do not make the purposive skills or prompts a random
sample from a larger population. Causal interpretation additionally assumes
fresh-trial isolation and no interference; execution order is randomized, but
wording labels are not randomly assigned within a block. Expanded-arm contrasts
and `Beta(1, 1)` sensitivity remain non-gating.

## Integrity and missingness

- Per-trial timeout: harness failure retained in its assigned cell.
- Whole-study timeout: family invalid; confirmation blocked.
- Missing, duplicate, identity-disagreeing, or scorer-disagreeing row: family
  invalid; confirmation blocked.
- Failed family: may run only as a labeled recovery and cannot replace primary
  evidence.
- Incomplete run index or wrong repo/CIB commit, dependency, lock hash, config
  hash, model setting, concurrency, or artifact hash: analysis refuses to run.
- The 128 task strings are intentionally public protocol fixtures. Materialized
  agent prompts containing canary instructions, nonces, sessions, transcripts,
  credentials, and workstation paths remain ignored local state.

False-case success means that the exact designated canary action was not
observed. It does not prove that Codex never discovered or read a skill.

## Execution and analysis

Prepare the exact environments:

```sh
cd /path/to/conditional-instruction-benchmark
git checkout eebdbfc84206c594db2d61cf883325e2d8e1b07d
uv sync --frozen
npm ci

cd /path/to/agent-coordination-skills
python3 -m venv .venv-confirmatory
.venv-confirmatory/bin/python -m pip install --disable-pip-version-check \
  -r studies/confirmatory-v2/requirements.txt
```

After the freeze tag and before inspecting any v2 outcome:

```sh
.venv-confirmatory/bin/python scripts/run_cib_confirmatory_v2.py \
  --cib-root /path/to/conditional-instruction-benchmark \
  --output-root results/confirmatory-v2-primary \
  --parallel-studies 2

.venv-confirmatory/bin/python scripts/summarize_cib_confirmatory_v2.py \
  results/confirmatory-v2-primary \
  --output results/confirmatory-v2-primary/aggregate.json
```

The runner refuses existing output, dirty checkouts, a repository `HEAD` that
does not resolve to the `confirmatory-v2-preregistered` tag, any concurrency
other than two, and runtime drift. It checkpoints the run index after every
family. The analyzer accepts only a complete eight-family primary index and the
exact artifact inventory frozen here. Its aggregate includes a safe provenance
block with the freeze ref, commit IDs, dependency versions, and execution window.

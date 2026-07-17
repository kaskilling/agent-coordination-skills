# Conditional activation wording changes AI-agent resource routing, but does not make it reliable

## Abstract

Agent skills commonly expose resources through natural-language activation
rules such as “use if condition X is true.” We tested whether replacing that
boundary with “use if and only if condition X is true” causally changes an AI
agent's use of an exact designated resource. A prospectively frozen,
outcome-aware direct replication evaluated Codex across eight coordination-skill
families, 64 matched prompt pairs, true and false conditions, three wording
arms, and three repetitions per cell (1,152 primary calls). Exact nonce canaries
provided direct evidence of designated resource use. Strict IFF wording had a
positive posterior false-case effect over plain IF of 19.53 percentage points
(95% credible interval 13.98–24.99; Monte Carlo probability estimate above zero
= 1.00000), met the preregistered −10-point necessary-use non-inferiority gate
with 100% observed success in both arms, and had a positive raw effect in all
eight families. However,
strict IFF avoided unnecessary resource use on only 29.69% of false-condition
assignments, failing the preregistered 80% absolute gate. There were no harness
failures or integrity exclusions. We conclude that expression form mattered in
this benchmark, but wording alone did not provide reliable conditional routing.

## 1. Research question

When an agent sees a skill description containing a conditional activation
boundary, does `if and only if` improve correct resource routing relative to
plain `if` while preserving necessary use?

The experiment separates two claims that are often conflated:

1. **Relative effect:** strict wording changes behavior in the desired direction.
2. **Absolute reliability:** strict wording routes correctly often enough to be
   relied upon as a control boundary.

The preregistration required both. A positive contrast alone could not confirm
the collection-level claim.

## 2. Design

### 2.1 Experimental units and interventions

The fixed corpus contained eight public coordination-skill families. Each family
had eight matched required/unnecessary prompt pairs. Every prompt was executed
under three instruction arms:

- plain: `use if <condition> is true`;
- strict: `use if and only if <condition> is true`;
- expanded: plain IF plus an explicit else-not policy.

Each family × pair × arm × truth cell had three repetitions. The 8 × 8 × 3 × 2 ×
3 design produced 1,152 primary assignments. A blind pre-study taxonomy review
classified all 128 prompt strings unanimously before the first confirmatory
execution.

### 2.2 Outcome evidence

CIB materialized a unique nonce resource for every trial. Necessary-use success
required the exact designated action and nonce output when the condition was
true. False-case success required non-observation of that exact action when the
condition was false. This is stronger than heuristically inferring skill use
from a `SKILL.md` read, but narrower than proving whether the agent discovered,
read, or mentally relied on any skill content.

### 2.3 Estimand and decision rule

The primary estimand was an end-to-end assignment effect analogous to
intention-to-treat: every frozen assignment remained in its cell, and a typed
harness failure counted as operational failure. The strict-minus-plain contrasts
were false-case superiority and true-case non-inferiority with a −10 percentage
point margin.

Every three-repetition cell used an independent `Beta(0.5, 0.5)` prior. Posterior
simulation used NumPy 2.4.1 PCG64, 200,000 draws, and two frozen seeds. The study
was confirmed only if all five wording gates, pooled missingness, evidence
integrity, and cache integrity passed. The absolute strict gates were at least
80% necessary use and at least 80% avoided unnecessary use.

### 2.4 Outcome-aware replication status

Confirmatory [v1](../../studies/confirmatory-v1/EXECUTION-STATUS.md) and
[v2](../../studies/confirmatory-v2/EXECUTION-STATUS.md) were invalid and
excluded. V1 failed process isolation. V2 had 26 pre-session transport failures
and nine per-trial timeouts; its frozen
analyzer produced no aggregate. V2 outcomes were inspected during diagnosis, so
v3 was explicitly preregistered as an outcome-aware, harness-repaired direct
replication rather than a blind primary study.

V3 preserved the corpus, arms, seeds, model settings, estimands, and thresholds.
It added a private signed-cache bootstrap, sequential family execution, longer
per-trial deadlines, typed missingness, and a worst-case adverse analysis that
assigned missing strict outcomes zero and missing plain outcomes one under both
truth values.

## 3. Results

### 3.1 Validity

All eight scheduled families executed once in frozen order. All 1,152 primary
rows had unique assignments and sealed evidence. There were zero harness
failures, zero invalid families, zero cache-digest changes, and no scorer or
identity disagreement. Because missingness was zero, operational and adverse
results were identical.

### 3.2 Primary effects and gates

| Preregistered quantity | Estimate | Decision |
|---|---:|---:|
| Posterior false-case IFF − IF | +19.53 pp | Pass |
| 95% credible interval | +13.98 to +24.99 pp | — |
| Monte Carlo estimate of P(false effect > 0) | 1.00000 | Pass |
| Posterior true-case IFF − IF | +0.002 pp | Pass |
| 95% credible interval | −5.12 to +5.13 pp | — |
| P(true effect > −10 pp) | 0.99993 | Pass |
| Strict necessary use | 100.00% | Pass |
| Strict avoided unnecessary use | 29.69% | **Fail** |
| Positive family effects | 8/8 | Pass |
| Harness failure rate | 0.00% | Pass |

The raw false-case avoidance rates were 57/192 (29.69%) for strict IFF and 7/192
(3.65%) for plain IF: 50 additional correct avoidances. The 26.04-point raw
difference is not the posterior estimate because
the preregistered model shrinks every small cell before averaging. Expanded
wording reached 31.25%, only 1.56 raw points above strict IFF.

The non-gating `Beta(1,1)` prior sensitivity remained positive at +15.62 points
(95% credible interval +9.75 to +21.43; estimated probability above zero 1.000).

### 3.3 Heterogeneity

Strict false-case avoidance ranged from 8.33% to 91.67%. `hypothesis-duel`
(91.67%) and `second-round` (62.50%) were much higher than the remaining six
families (8.33%–25.00%). Yet every family's raw strict-minus-plain false-case
contrast was positive. These family comparisons were not separately powered or
preregistered as confirmatory and should generate hypotheses, not rankings.

## 4. Post-hoc exploratory hypothesis duel

This mechanism comparison was conducted after the preregistered result and is
exploratory. It cannot change or rescue any confirmatory gate.

### Hypothesis A: wording helps, but routing remains genuinely unreliable

Predictions were a positive strict-minus-plain effect, preserved true-case use,
low absolute false-case success, broad rather than single-family failure, and no
harness explanation. The result matched all five: posterior superiority was
decisive, necessary use was 100%, absolute avoidance was 29.69%, six families
were at or below 25%, and missingness was zero. This is the best-supported
explanation within the benchmark.

### Hypothesis B: the low absolute rate is mainly a measurement artifact

The benchmark could overstate use if the nonce-canary task itself attracts the
agent, or if purposively written negative prompts do not represent real routing
contexts. Family heterogeneity is compatible with such an interaction. However,
the artifact hypothesis does not explain away the paired wording effect: arms
shared the same cases, canary mechanism, backend, and scoring, and all eight
family contrasts moved in the predicted direction. The current data cannot
separate real-world routing unreliability from benchmark-specific absolute-rate
calibration. That requires a new, prospectively frozen measurement-validation
study, not reinterpretation of v3.

### Resolution

V3 supports the relative causal claim within its paired intervention design and
supports rejecting IFF wording as a sufficient standalone reliability control.
It does not establish the absolute failure rate that production agents would
have on naturally occurring tasks.

## 5. Implications

For skill authors, “if and only if” is a useful nudge, not enforcement. An
explicit else-not clause performed similarly and did not solve the absolute
problem. High-stakes routing should place enforcement in code, tool permissions,
policy gates, or deterministic dispatch rather than relying only on prose.

For evaluation authors, relative prompt comparisons should be paired with
absolute acceptance gates. Without the 80% gate, this study could have been
reported as an uncomplicated success despite strict wording failing most
false-condition assignments.

For benchmark builders, exact action canaries, clean per-trial homes, sealed
assignment identity, typed missingness, and a third IF+ELSE-NOT arm materially
improve causal interpretability over heuristic trace inspection alone.

## 6. Next discriminating experiments

The next study should not simply repeat more calls. It should discriminate the
remaining mechanism hypotheses by prospectively adding:

- preregistered safe pair-type labels and block summaries to reveal whether
  failures cluster by negative-task type without publishing prompts or nonces;
- randomized family order across independent blocks to separate temporal drift
  from family difficulty;
- a second, less reactive receipt mechanism alongside the action canary;
- placements beyond `skill_description`, followed by other agent runtimes only
  after Codex replication is stable.

These are new studies. None may be used post hoc to rescue v3's failed absolute
gate.

## 7. Limitations

- One Codex model alias, medium reasoning effort, backend, placement, and
  89-minute execution window.
- A fixed purposive corpus of eight related coordination skills, not a random
  sample of skills, prompts, models, or users.
- Model-based intervals conditional on cell independence and stationarity.
- Execution order was randomized and frozen, but wording labels were fixed
  interventions rather than design-based randomized labels.
- Exact canary action is a narrow operational definition of resource use.
- V3 is outcome-aware because v2 behavior was inspected during failure diagnosis.

## 8. Reproducibility and publication boundary

The protocol was frozen at annotated tag `confirmatory-v3-preregistered` before
any corpus call. The run used CIB v0.5.3, Promptfoo 0.121.19, Codex SDK 0.144.5,
`gpt-5.6-sol`, and 1,152 isolated primary calls plus eight excluded cache
warmups. The public [preregistration](../../studies/confirmatory-v3/PREREGISTRATION.md),
[result summary](../../studies/confirmatory-v3/RESULTS.md), sanitized
[aggregate](../../studies/confirmatory-v3/aggregate.json), and
[pair-cell sufficient statistics](../../studies/confirmatory-v3/cell-sufficient-statistics.json)
contain the public posterior inputs. Running
[`scripts/reproduce_confirmatory_v3_public.py`](../../scripts/reproduce_confirmatory_v3_public.py)
with the pinned analysis environment reproduces the statistical aggregate and
gate decisions to `1e-12` numeric tolerance, conditional on the published
integrity and cache attestations.

Raw prompts, nonces, session IDs, transcripts, authentication data, signed
caches, and workstation paths are intentionally excluded from publication.

## 9. Conclusion

Expression form mattered: strict IFF wording consistently improved false-case
routing and met the preregistered −10-point necessary-use non-inferiority gate;
both arms had 100% observed necessary use. It did not make routing reliable. The
scientifically defensible result is a valid negative confirmatory study with a
strong, bounded relative effect—not a failed experiment and not proof that prose
can enforce an agent policy.

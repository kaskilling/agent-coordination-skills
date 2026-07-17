# Confirmatory v3 results

Status: **valid negative confirmatory result**.

The preregistered analyzer completed successfully against all 1,152 assignments.
The collection-level claim was not confirmed because strict IFF wording avoided
the designated resource on only 29.69% of false-condition assignments, below
the frozen 80% absolute gate. This gate failed in both the operational and
adverse analyses. No other gate failed.

## Primary result

| Quantity | Result | Frozen gate |
|---|---:|---:|
| Posterior IFF − IF false-case effect | +19.53 pp | P(effect > 0) ≥ 0.975 |
| 95% credible interval | +13.98 to +24.99 pp | — |
| Monte Carlo estimate of P(false-case effect > 0) | 1.00000 | Pass |
| Posterior IFF − IF true-case effect | +0.002 pp | P(effect > −10 pp) ≥ 0.975 |
| P(true-case effect > −10 pp) | 0.99993 | Pass |
| Strict necessary use | 100.00% | ≥80% — Pass |
| Strict avoided unnecessary use | 29.69% | ≥80% — **Fail** |
| Families with positive false-case effect | 8/8 | ≥6 — Pass |
| Harness failures | 0/1,152 | ≤5% — Pass |
| Structural and cache integrity | 8/8 valid | All valid — Pass |

The raw false-case rates were 57/192 (29.69%) for strict IFF and 7/192 (3.65%)
for plain IF: 50 additional correct avoidances and a descriptive difference of
26.04 percentage points. The posterior
effect is smaller because the frozen model applies an independent Jeffreys prior
to every three-repetition cell before equal-pair averaging.

The non-gating `Beta(1,1)` sensitivity also remained positive: +15.62
percentage points, 95% credible interval +9.75 to +21.43, with estimated
posterior probability above zero of 1.000.

## Family results

| Skill family | Strict necessary use | Strict avoided unnecessary use | Raw false-case IFF − IF |
|---|---:|---:|---:|
| artifact-room | 100.00% | 8.33% | +8.33 pp |
| blind-arbitration | 100.00% | 8.33% | +8.33 pp |
| gated-handoff | 100.00% | 12.50% | +12.50 pp |
| hypothesis-duel | 100.00% | 91.67% | +66.67 pp |
| peer-deliberation | 100.00% | 20.83% | +20.83 pp |
| proof-split | 100.00% | 25.00% | +25.00 pp |
| second-round | 100.00% | 62.50% | +58.33 pp |
| slice-and-integrate | 100.00% | 8.33% | +8.33 pp |

Expanded IF+ELSE-NOT wording was non-gating. Its observed false-case avoidance
was 31.25%, only 1.56 percentage points above strict IFF, while all three arms
had 100% observed necessary use.

## Interpretation

On this fixed corpus and execution window, `if and only if` changed routing in
the desired direction and met the preregistered −10 percentage point
necessary-use non-inferiority gate; observed necessary-use rates were 100% in
both strict and plain arms. It was not sufficient to make resource avoidance
reliable in absolute terms. The correct conclusion is
therefore not “IFF does nothing” and not “IFF solves routing.” It is:

> Strict activation wording materially improved relative false-case routing,
> but still failed the preregistered absolute reliability requirement.

False-case success proves only that CIB did not observe the exact designated
canary action. It does not prove that Codex never discovered or read a skill.
The family spread is descriptive and hypothesis-generating; no family was
selected or excluded after outcomes were known.

## Integrity and provenance

- Protocol freeze: `confirmatory-v3-preregistered`, commit
  `8d83d4548d2e18467e1dfa23d0c2b0aa260829f9`.
- CIB: v0.5.3 at commit
  `e9e77bfd598319fe0d7049c74943c15f556a61ac`.
- Runtime: Promptfoo 0.121.19, Codex SDK 0.144.5, `gpt-5.6-sol`, medium effort.
- Execution: 2026-07-17 22:02:15–23:31:34 UTC; one family at a time.
- Calls: 1,152 primary plus eight excluded cache warmups.
- Missingness: zero typed harness failures and zero invalid families.
- Cache: all 1,152 private trial snapshots matched their per-family seed digest.
- Analysis: 200,000 draws; both frozen RNG seeds agreed within 0.001.

The complete sanitized output is [aggregate.json](aggregate.json). The
[384 public pair-cell sufficient statistics](cell-sufficient-statistics.json)
reproduce its posterior through
[`scripts/reproduce_confirmatory_v3_public.py`](../../scripts/reproduce_confirmatory_v3_public.py).
Raw prompts,
nonces, sessions, transcripts, credentials, caches, and workstation paths remain
in ignored private state and are not publication artifacts.

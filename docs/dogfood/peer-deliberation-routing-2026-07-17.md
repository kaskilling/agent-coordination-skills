# Peer-deliberation routing dogfood

- Date: 2026-07-17
- Verdict: **PASS**
- Evidence strength: **descriptive only**

## Question

Does wording the `peer-deliberation` activation boundary as “use if and only if”
make Codex use the designated resource when direct peer exchange is required and
avoid it when a different collaboration topology is requested?

This is a causal routing test. It is not an end-to-end test of whether two real
subagents were spawned or whether every step in the skill body was followed.

## Frozen design

The initial experiment, including cases and thresholds, was committed as
`e982c8e` before any model trial ran. It used:

- three matched required/unnecessary case pairs
- two repetitions per case
- `if`, `if and only if`, and `if + else-not` arms
- skill-description placement
- Codex model `gpt-5.6-sol` at medium reasoning
- Promptfoo's Codex SDK backend through CIB v0.4.0
- four concurrent jobs with cache disabled
- an 80% minimum for required use and avoided unnecessary use
- a 5% maximum harness-failure rate

The required cases ask two distinct experts to challenge and revise each other.
The matched unnecessary cases keep the same domains but ask for blind
arbitration, independent proof splitting, or a single review loop.

## Transparent operational amendment

The first attempt was invalid. CIB's configured 300-second timeout applied to
the whole 36-trial Promptfoo process, not to each trial. Thirteen trials were
scored before the process ceiling terminated four in-flight Codex calls; no
behavioral verdict was taken from that incomplete run.

Only the whole-study timeout changed, from 300 to 1200 seconds, in commit
`1b0f1b3`. Cases, arms, repetitions, model, seed, concurrency, and thresholds
remained unchanged. The clean rerun then completed in 718.3 seconds.

## Results

All 36 trials had unique identities and exact nonce evidence. There were no
harness failures, scorer disagreements, or identity disagreements.

| Condition | Arm | Correct routes | Rate | 95% Wilson interval |
|---|---|---:|---:|---:|
| Required use | `if` | 6/6 | 100.0% | 61.0%-100.0% |
| Required use | `if and only if` | 6/6 | 100.0% | 61.0%-100.0% |
| Required use | `if + else-not` | 6/6 | 100.0% | 61.0%-100.0% |
| Avoided unnecessary use | `if` | 0/6 | 0.0% | 0.0%-39.0% |
| Avoided unnecessary use | `if and only if` | 6/6 | 100.0% | 61.0%-100.0% |
| Avoided unnecessary use | `if + else-not` | 5/6 | 83.3% | 43.6%-97.0% |

The configured strict policy selects the `if and only if` arm. It passed both
product thresholds: 100% required use, 100% avoided unnecessary use, and 0%
harness failures.

Across the full causal matrix, 29/36 routes matched expectation. The entire
seven-trial difference came from unnecessary-use behavior: plain `if` did not
suppress any unnecessary resource use, while the explicit negative-boundary
arms suppressed 11/12.

Promptfoo reported 3,997,645 total tokens, of which 3,182,080 were cached, over
the 11-minute 55-second run.

## Interpretation

In this one task family, adding a false-case boundary changed unnecessary-use
behavior without reducing required use. The `if and only if` wording was
descriptively perfect here; the expanded `if + else-not` wording missed once.

This is strong dogfood evidence that CIB can distinguish “the agent did it” from
“the instruction caused the agent to do it,” and it gives a concrete reason to
prefer strict activation language for this skill. It is not yet a general claim
about all skills, placements, models, or future Codex versions. Six observations
per arm also leave wide uncertainty intervals.

The next confirmatory step is to freeze a larger protocol with multiple task
families and repeat it across additional skill-description boundaries before
changing every skill in the collection.

## Reproduce

The public configuration is [`cib.yaml`](../../cib.yaml). Run it with a CIB
v0.4.0 checkout and private output directory:

```sh
uv run cib check /path/to/agent-coordination-skills/cib.yaml \
  --output-dir /path/to/private-results/peer-deliberation-routing
```

The successful CIB run ID was
`peer-deliberation-routing-ad70f1ef33a8`. Raw prompts and exact private evidence
remain local; the public record contains only the sanitized aggregate.

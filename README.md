# Agent Coordination Skills

Eight focused skills for coordinating agent teams without turning every task into
an unstructured swarm.

Each skill owns one collaboration strategy, one evidence contract, and one stop
condition. Use the smallest strategy that matches the work.

See the [quick usage guide](USAGE.md) for copy-ready prompts and common combinations.

## Choose a strategy

| Skill | Use when | Do not use when |
|---|---|---|
| [`second-round`](skills/second-round/SKILL.md) | Existing work needs an independent review, accepted fixes, and re-review | No first pass exists yet |
| [`peer-deliberation`](skills/peer-deliberation/SKILL.md) | Two peers should question and revise each other directly | First judgments must remain independent |
| [`blind-arbitration`](skills/blind-arbitration/SKILL.md) | Independent proposals must stay blind before controlled adjudication | Peers need an open working conversation |
| [`proof-split`](skills/proof-split/SKILL.md) | Independent proof surfaces or review lenses can run in parallel | Agents are defending rival causal explanations |
| [`hypothesis-duel`](skills/hypothesis-duel/SKILL.md) | Competing causes need discriminating tests and falsification | The task only needs broad coverage |
| [`artifact-room`](skills/artifact-room/SKILL.md) | Several contributors must converge through durable shared state | Agents would edit the same canonical file concurrently |
| [`gated-handoff`](skills/gated-handoff/SKILL.md) | Dependent work must pass receiver-owned acceptance gates | Workstreams are independently runnable |
| [`slice-and-integrate`](skills/slice-and-integrate/SKILL.md) | A feature can be divided into independent vertical slices with one integrator | The split creates layer-only work with no local proof |

## Install

List the available skills:

```sh
npx skills@latest add kaskilling/agent-coordination-skills --list
```

Choose skills interactively for the detected agent:

```sh
npx skills@latest add kaskilling/agent-coordination-skills
```

Install one strategy into Codex for the current project:

```sh
npx skills@latest add kaskilling/agent-coordination-skills \
  --skill hypothesis-duel --agent codex --yes
```

Install every strategy into Codex for the current project:

```sh
npx skills@latest add kaskilling/agent-coordination-skills \
  --skill '*' --agent codex --yes
```

Install every strategy globally for Codex:

```sh
npx skills@latest add kaskilling/agent-coordination-skills \
  --skill '*' --agent codex --global --yes
```

For Claude Code, use the same commands with an explicit agent:

```sh
npx skills@latest add kaskilling/agent-coordination-skills \
  --skill '*' --agent claude-code --yes
```

Restart your agent if it does not discover installed skills dynamically.

Avoid the CLI's `--all` shorthand when you mean “all skills for one agent”:
it also selects every detected agent. Use `--skill '*' --agent <agent>` instead.

### Existing `second-round` users

This is the same repository that was originally published as
`kaskilling/second-round`. GitHub redirects the old repository URL, and the
existing `skills/second-round/` path remains unchanged. The old install command
continues to select from this collection:

```sh
npx skills@latest add kaskilling/second-round --skill second-round
```

Manual fallback for one Codex skill:

```sh
git clone https://github.com/kaskilling/agent-coordination-skills.git
mkdir -p ~/.agents/skills
cp -R agent-coordination-skills/skills/peer-deliberation ~/.agents/skills/
```

Manual fallback for one Claude Code skill:

```sh
git clone https://github.com/kaskilling/agent-coordination-skills.git
mkdir -p ~/.claude/skills
cp -R agent-coordination-skills/skills/peer-deliberation ~/.claude/skills/
```

## Shared rules

All eight skills apply the same operating invariants:

- one lead owns scope, integration, conflict resolution, and the final answer
- every agent receives a distinct role, artifact scope, proof obligation, and stop condition
- review, diagnosis, and planning remain read-only unless the user authorized edits
- agents preserve exact evidence and label inference, uncertainty, and missing validation
- one path stops after two dead ends and pivots to a higher-signal surface
- agents never edit the same canonical file concurrently
- each contribution gets narrow proof; broad validation is batched by default
- degraded execution is stated explicitly when independent agents or enough slots are unavailable

## Repository layout

```text
.codex-plugin/plugin.json
.github/workflows/cib.yml
.github/workflows/validate.yml
cib.yaml
docs/dogfood/
scripts/validate_skills.py
skills.sh.json
skills/
  artifact-room/
  blind-arbitration/
  gated-handoff/
  hypothesis-duel/
  peer-deliberation/
  proof-split/
  second-round/
  slice-and-integrate/
```

Every skill is self-contained and intentionally lean:

```text
skills/<name>/
  SKILL.md
  agents/openai.yaml
```

## Validate

Run the deterministic repository check:

```sh
python3 scripts/validate_skills.py
```

It verifies folder/frontmatter names, unique inventory, required UI metadata,
description and file-size limits, relative links, manifest inventories, and a
small denylist of common private paths, private email domains, and credential
signatures. Treat it as a preflight, not a replacement for repository secret
scanning or review.

Behavioral evaluation remains separate because model grading is nondeterministic.
Forward-test a changed skill on a realistic task before releasing it.

### Behavioral dogfood

[`cib.yaml`](cib.yaml) causally checks the public activation boundary for
`peer-deliberation`: does a strict conditional instruction make Codex use the
designated resource when direct peer exchange is required, while avoiding it for
blind proposals, proof splitting, and single-reviewer work?

The preregistered check contains three matched required/unnecessary case pairs,
two repetitions, and three causal arms: 36 model calls in total. It passes when
required use and avoided unnecessary use are each at least 80%, with no more than
5% harness failures. These thresholds were fixed before the first run. The
first completed run took about 12 minutes and 4 million total tokens; monetary
cost depends on model access, pricing, and cache behavior.

Run it before releasing a change to the activation boundary, cases, model, or
agent runtime. It is not intended for ordinary documentation-only changes.

Run the manual **Check peer-deliberation routing** GitHub workflow after adding a
dedicated `OPENAI_API_KEY` repository secret. The workflow pins Conditional
Instruction Benchmark v0.5.0 by commit and uploads its safe report; it does not
publish raw prompts or private evidence.

For a local run, prepare a
[CIB v0.5.0](https://github.com/kalibraring/conditional-instruction-benchmark/releases/tag/v0.5.0)
checkout, then run the public config with a private output directory:

```sh
git clone --branch v0.5.0 \
  https://github.com/kalibraring/conditional-instruction-benchmark.git
cd conditional-instruction-benchmark
uv sync --frozen
npm ci
uv run cib check /path/to/agent-coordination-skills/cib.yaml \
  --output-dir /path/to/private-results/peer-deliberation-routing
```

This check proves routing of CIB's designated canary resource under the encoded
boundary. It does not prove that two real subagents were spawned or that every
step in `skills/peer-deliberation/SKILL.md` was followed.

See the [first dogfood result](docs/dogfood/peer-deliberation-routing-2026-07-17.md):
the strict `if and only if` arm passed both selected routing thresholds, while
the plain `if` arm used the resource in all six unnecessary-use trials.

### Confirmatory study

The [frozen confirmatory-v1 protocol](studies/confirmatory-v1/PREREGISTRATION.md)
extends that dogfood check to all eight coordination skills: 64 indexed
required/unnecessary pairs, three repetitions, three wording arms, and 1,152
model calls. Its protocol lock, blind taxonomy evidence, runner, integrity
checks, inference code, and exact reproduction environment are versioned with
the study. Raw prompts, nonces, sessions, transcripts, and credentials remain
in ignored local results; only sanitized aggregate evidence is publishable.

## Design sources

The collection layout follows primary-source conventions from:

- [Agent Skills specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)
- [Matt Pocock's composable skills collection](https://github.com/mattpocock/skills)
- [Anthropic's self-contained skill collection](https://github.com/anthropics/skills)
- [Vercel's grouped agent skills](https://github.com/vercel-labs/agent-skills)
- [OpenAI's current plugin examples](https://github.com/openai/plugins)
- [Obra Superpowers coordination skills](https://github.com/obra/superpowers)

Web Dev Cody's
[Agentic Jumpstart starter](https://github.com/webdevcody/agentic-jumpstart-starter-kit)
was treated as a project-local skill example, not as the distribution model for
this collection.

## License

MIT.

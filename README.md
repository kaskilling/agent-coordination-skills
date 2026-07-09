# second-round

Adversarial review, fix, and re-review for agent work.

`second-round` asks a fresh reviewer surface to challenge an existing artifact,
plan, implementation, repository, document, or workflow. It is designed for the
moment after a first pass exists and you want the next agent to find what would
make a real user fail.

The skill guides an agent to:

- capture the baseline and current validation evidence
- request independent criticism instead of approval
- triage findings by severity
- fix accepted blockers and high-value issues when fixes are in scope
- re-review after material fixes
- close with evidence and remaining risks

## Install

Use a standard skills installer:

```sh
npx skills@latest add kaskilling/second-round
```

Manual install:

```sh
git clone https://github.com/kaskilling/second-round.git
cp -R second-round/skills/second-round ~/.agents/skills/
```

Restart your agent after installing if it does not pick up new skills
dynamically.

## Use

Invoke the skill directly:

```text
$second-round review this plan critically
$second-round re-review this implementation after fixes
```

Agents can also trigger it when you ask for a second round, critical review,
independent review, adversarial review, another agent's view, or a
review/improve/re-review loop.

## Repository Layout

```text
skills/
  second-round/
    SKILL.md
    agents/
      openai.yaml
```

The installed skill folder is intentionally small. `SKILL.md` is the portable
skill entrypoint, and `agents/openai.yaml` supplies Codex UI metadata.

## License

MIT.

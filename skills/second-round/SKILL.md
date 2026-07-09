---
name: second-round
description: Runs an adversarial second-round review loop for any task by asking a fresh reviewer surface to independently review the current work, research comparable patterns, find gaps, and recommend fixes. Use when the user asks for a second round, critical review, independent review, adversarial review, another agent's view, or a review/improve/re-review loop.
---

# Second Round

Use a fresh reviewer to challenge the work, then fix the highest-value findings
and repeat until the remaining risk is explicit.

This skill is for improving an artifact, plan, implementation, repository,
document, or workflow after an initial pass exists.

## Rules

- Spawn a subagent only when the user explicitly asked for a second round,
  another agent, delegation, or this skill. If subagents are unavailable, run
  an independent reviewer with the best available separate surface.
- Keep the reviewer independent. Pass source artifacts and the user goal, not
  your desired answer or defense of the current work.
- Ask for criticism, not approval. The reviewer should look for missed
  requirements, stale docs, setup friction, safety issues, validation gaps,
  packaging risks, and unclear user experience.
- Respect review-only requests. If the user asks only for feedback, or says not
  to edit files, stop after findings, triage, and recommended fixes.
- Do not delegate the immediate blocking task. While the reviewer works, run
  local checks or inspect non-overlapping areas yourself.
- When the user asked for fixes, fix real issues after review. Do not stop at
  collecting feedback.
- Repeat once after material fixes. Stop after two review/fix rounds unless the
  user asks to continue or a blocker remains.

## Workflow

### 1. Capture The Baseline

State the target behavior in one sentence.

List the artifacts under review:

- files, repos, docs, screenshots, commands, logs, or plans
- what changed in the current pass
- what proof already exists
- what has not been validated

Run a narrow local status check before spawning if it is cheap, such as `git
status --short`, targeted tests, lint, or doc searches.

### 2. Spawn The Reviewer

Use one reviewer subagent for the first second-round pass. Use more only when
the questions are independent.

Choose the strongest independent reviewer surface available:

1. built-in subagent/delegation tool
2. a separate `codex exec` or equivalent CLI session with a self-contained prompt
3. a clearly separated local review pass, labelled as lower-confidence because
   it is not independent

For a CLI reviewer, use a self-contained command shape like:

```bash
codex exec -C <repo-or-workspace> "<reviewer prompt>"
```

Include the goal, artifact paths, recent changes, and validation evidence in
the prompt. Do not include your preferred answer.

Prompt shape:

```text
You are an independent critical reviewer.

Goal: <user goal in plain terms>
Artifacts: <paths, repo, docs, command outputs, links>
Recent changes: <short neutral list>

Review this from first principles. Be critical and specific.
Do not modify files unless explicitly asked.

Answer with:
1. Simple explanation of what this is for.
2. Verdict on whether it is simple, correct, and useful for the target user.
3. Comparison to relevant best practices or similar repos/tools.
4. Findings ordered by severity, with file/line references when possible.
5. Concrete recommended fixes.
6. Validation run and validation not run.
```

Do not ask the reviewer to confirm your plan. Ask it to find what would make
the next user fail.

### 3. Work While It Reviews

Do useful non-overlapping work while the reviewer runs:

- run validation commands
- search for stale references
- inspect setup paths
- check packaging or install behavior
- read comparable examples

Do not redo the reviewer task yourself.

### 4. Triage Findings

When the reviewer returns, classify each finding:

- `Blocker`: breaks the task, setup, safety, or claimed behavior.
- `High`: likely to confuse users or cause a failed run.
- `Medium`: real maintainability, docs, or edge-case risk.
- `Low`: polish, clarity, or future improvement.
- `Reject`: not applicable, already handled, or too speculative.

Explain briefly why accepted findings matter. Do not defend weak work.

### 5. Fix Accepted Findings

Fix blockers and high-value findings first. Keep patches scoped.

For each fix:

- update the artifact
- update docs if behavior changed
- run the narrowest proof command
- preserve unrelated dirty work

If a finding needs a larger workstream, record it separately instead of mixing
it into an unrelated patch.

### 6. Re-Review

After material fixes, ask the same reviewer thread to re-review the updated
state if the surface supports it. Otherwise start a fresh reviewer and include
the prior findings plus the changes made. Ask it to find remaining gaps,
regressions, stale docs, or validation holes.

Prompt shape:

```text
Re-review the current state after the fixes.

Changes since your last review:
- <fix 1>
- <fix 2>

Be critical again. Validate non-mutating paths if useful.
Return remaining findings ordered by severity. If no blockers remain, say so
and list residual risks.
```

Fix any new blockers or high findings. Usually stop after this second pass
unless new critical findings are found.

### 7. Close With Evidence

Final response should include:

- what changed
- which second-round findings were fixed
- validation commands that passed
- remaining risks or deferred work

Do not claim the work is production-ready unless the proof actually supports
that claim.

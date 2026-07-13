---
name: peer-deliberation
description: Runs a bounded direct exchange between two agents with distinct expertise so they question, challenge, and revise each other's reasoning. Use when two agents should talk directly to negotiate a design, reconcile analyses, resolve a disagreement, or reach an evidence-backed joint position.
---

# Peer Deliberation

Let two peers challenge each other directly, then return one evidence-backed
position with unresolved disagreement kept visible.

## Rules

- Keep one lead responsible for scope, orchestration, conflict resolution, and
  the final answer.
- Give the peers distinct expertise, responsibilities, or positions. Do not
  create two interchangeable commentators.
- Define mutation authority before delegation. Keep both peers review-only
  unless the user authorized changes; if edits are allowed, assign exclusive
  file ownership or let the lead implement after deliberation.
- Give both peers the same neutral goal, source artifacts, constraints, proof
  standard, and round limit. Do not reveal the lead's preferred answer.
- Require exact evidence for factual claims and label inference, confidence,
  missing validation, and unavailable proof.
- Preserve dissent. Do not turn agreement, repetition, or majority preference
  into proof.
- Default to three exchanges. Stop earlier on decisive evidence or after two
  exchanges add no new evidence.

## Workflow

### 1. Frame The Question

State one decision or question in a sentence. Record the artifacts, constraints,
accepted evidence, existing proof, proof gaps, mutation boundary, and stop rule.

### 2. Assign The Peers

Spawn two agents with complementary roles. Ask each for an independent opening
position before discussion starts. Require claims, evidence, assumptions, risks,
and the strongest question for the other peer.

Give each agent the other's canonical task identity. Tell them to message each
other directly and to send the lead a copy or summary of every material exchange.

If direct messaging is unavailable, relay messages verbatim between two separate
sessions. State that this topology is degraded and lower confidence. If two
independent peers cannot be created, stop rather than simulate a team silently.

### 3. Run Bounded Exchanges

Count one exchange when a peer answers the other's material question. Accept an
exchange only when it does at least one of these:

- adds source-backed evidence
- answers a concrete question
- falsifies or narrows a claim
- revises a position and explains why
- identifies the cheapest decisive proof

Interrupt scope drift, repeated assertions, unauthorized edits, or debate about
style that is not part of the decision criteria. After two dead ends on one path,
pivot to a higher-signal artifact or classify the blocker.

### 4. Reconcile

After the final exchange, ask each peer separately for:

- agreements and supporting evidence
- remaining disagreements and decisive missing proof
- revised recommendation and confidence
- validation run and validation not run

Resolve only what the evidence supports. When evidence cannot decide, recommend
a reversible experiment or preserve the alternatives instead of inventing
consensus.

### 5. Close With Evidence

Report the question, peer roles, strongest evidence, agreements, disagreements,
lead resolution, validation gaps, and next narrow proof. If authorized changes
follow, run the narrowest relevant proof and keep broad validation batched.

## Stop Conditions

Stop on an evidence-supported decision, one decisive unavailable proof, the
agreed round limit, or two exchanges with no new evidence. Do not use this skill
when first-pass independence must remain blind, work only needs parallel surface
coverage, or one agent is reviewing completed work.

## Example

“Use `$peer-deliberation` to have an API designer and mobile engineer challenge
this contract directly for three exchanges, then reconcile their conclusions.”

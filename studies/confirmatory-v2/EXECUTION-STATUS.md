# Confirmatory v2 execution status

Status: **invalid and excluded from confirmatory evidence**.

The frozen v2 runner executed its eight-family, 1,152-assignment schedule from
2026-07-17 19:22:46 UTC through 20:26:28 UTC. The frozen analyzer refused the
run because the required complete, integrity-valid family inventory was absent.
No confirmatory aggregate was produced, and v2 supports no wording-effect claim.

## First-failure accounting

The repaired CIB v0.5.2 audit later reconstructed the assignment ledger without
changing the frozen v2 evidence. It found 35 harness failures:

- 26 pre-session transport failures caused by an unavailable cloud-config fetch;
- 9 per-trial timeouts at the frozen 300-second deadline.

The remaining 1,117 assignments had terminal behavioral opportunities. Offline
normalization recovered nine timeout identities from the frozen ledger and
produced 1,152 scorer-index agreements, but this is diagnostic and recovery
evidence only. It does not retrofit a valid primary v2 result.

## Consequence for v3

Behavioral outcomes were inspected while diagnosing v2, so confirmatory v3 is
explicitly outcome-aware. V3 is a prospectively frozen, harness-repaired direct
replication of the same corpus, arms, seeds, estimands, thresholds, and model
settings—not a blind replacement primary. Runtime changes and missing-data
sensitivity rules are declared before any v3 corpus call.

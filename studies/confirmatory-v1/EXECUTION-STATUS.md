# Confirmatory v1 execution status

Status: **invalid and excluded from scientific evidence**.

The first primary execution was interrupted after multiple family processes
contended for Promptfoo's shared SQLite state. The canary assertion bridge also
resolved to a system Python interpreter that could not import CIB. The run index
never reached `complete`, required family artifacts were missing, and the frozen
analysis correctly refuses the directory.

Inspection was limited to diagnosing why the run was invalid. No incomplete
behavioral result is used to choose prompts, thresholds, estimands, or analysis
rules for the successor study. The ignored raw directory remains local and is
never substituted for primary evidence.

The defects were repaired and released in
[CIB v0.5.1](https://github.com/kalibraring/conditional-instruction-benchmark/releases/tag/v0.5.1).
Confirmatory v2 retains the v1 corpus and scientific decision rules while
freezing that repaired execution layer before any v2 model call.

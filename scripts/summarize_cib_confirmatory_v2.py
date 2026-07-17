#!/usr/bin/env python3
"""Analyze the frozen confirmatory-v2 corpus without publishing private evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
STUDY_ROOT = ROOT / "studies" / "confirmatory-v2"
CONFIG_ROOT = ROOT / "studies" / "confirmatory-v1" / "configs"
FAMILIES = (
    "artifact-room",
    "blind-arbitration",
    "gated-handoff",
    "hypothesis-duel",
    "peer-deliberation",
    "proof-split",
    "second-round",
    "slice-and-integrate",
)
ARMS = ("if", "iff", "if_else_not")
TRUTHS = (True, False)
PAIR_COUNT = 8
REPETITIONS = 3
INITIAL_DRAWS = 200_000
MAX_DRAWS = 1_600_000
PRIMARY_SEED = 20260717
CONVERGENCE_SEED = 20260718
POSTERIOR_CHUNK_SIZE = 10_000
EXPECTED_NUMPY_VERSION = "2.4.1"
FROZEN_CIB_COMMIT = "eebdbfc84206c594db2d61cf883325e2d8e1b07d"
REQUIRED_ARTIFACTS = (
    "run-manifest.jsonl",
    "promptfoo/derived/summary.json",
    "promptfoo/derived/audit.json",
    "study-result.json",
    "check-metadata.json",
    "report/report.json",
    "check-result.json",
)
IDENTITY_FIELDS = (
    "random_order",
    "arm",
    "condition_true",
    "case_id",
    "case_variant",
    "placement",
)


CellKey = tuple[str, int, str, bool]
Cell = dict[str, int]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _variant_indices(case_variant: int) -> tuple[int, int]:
    pair = case_variant % PAIR_COUNT
    repeat = case_variant // PAIR_COUNT
    if repeat not in range(REPETITIONS):
        raise ValueError(f"invalid case variant: {case_variant}")
    return pair, repeat


def _validate_cells(cells: dict[CellKey, Cell]) -> None:
    expected = {
        (family, pair, arm, truth)
        for family in FAMILIES
        for pair in range(PAIR_COUNT)
        for arm in ARMS
        for truth in TRUTHS
    }
    actual = set(cells)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ValueError(
            "cell inventory differs from frozen protocol: "
            f"missing={missing[:3]}, unexpected={unexpected[:3]}"
        )
    for key, cell in cells.items():
        if cell.get("n") != REPETITIONS:
            raise ValueError(f"cell does not contain three outcomes: {key}")
        successes = cell.get("successes")
        if not isinstance(successes, int) or not 0 <= successes <= REPETITIONS:
            raise ValueError(f"cell has invalid success count: {key}")


def _posterior(
    cells: dict[CellKey, Cell],
    *,
    draws: int,
    seed: int,
    prior: float = 0.5,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    prompt_keys = [
        (family, pair) for family in FAMILIES for pair in range(PAIR_COUNT)
    ]

    def sample_difference(truth: bool) -> np.ndarray:
        iff_successes = np.array(
            [
                cells[(family, pair, "iff", truth)]["successes"]
                for family, pair in prompt_keys
            ]
        )
        plain_successes = np.array(
            [
                cells[(family, pair, "if", truth)]["successes"]
                for family, pair in prompt_keys
            ]
        )
        iff_n = np.array(
            [cells[(family, pair, "iff", truth)]["n"] for family, pair in prompt_keys]
        )
        plain_n = np.array(
            [cells[(family, pair, "if", truth)]["n"] for family, pair in prompt_keys]
        )
        differences = np.empty(draws)
        for start in range(0, draws, POSTERIOR_CHUNK_SIZE):
            stop = min(draws, start + POSTERIOR_CHUNK_SIZE)
            size = (stop - start, len(prompt_keys))
            iff_rates = rng.beta(
                prior + iff_successes,
                prior + iff_n - iff_successes,
                size=size,
            )
            plain_rates = rng.beta(
                prior + plain_successes,
                prior + plain_n - plain_successes,
                size=size,
            )
            differences[start:stop] = (iff_rates - plain_rates).mean(axis=1)
        return differences

    false_differences = sample_difference(False)
    true_differences = sample_difference(True)
    return {
        "draws": draws,
        "seed": seed,
        "prior": [prior, prior],
        "rng": f"numpy-{np.__version__}-PCG64",
        "false_difference": {
            "mean": float(false_differences.mean()),
            "credible_95": [
                float(np.quantile(false_differences, 0.025, method="nearest")),
                float(np.quantile(false_differences, 0.975, method="nearest")),
            ],
            "probability_greater_than_zero": float(
                np.count_nonzero(false_differences > 0) / draws
            ),
        },
        "true_difference": {
            "mean": float(true_differences.mean()),
            "credible_95": [
                float(np.quantile(true_differences, 0.025, method="nearest")),
                float(np.quantile(true_differences, 0.975, method="nearest")),
            ],
            "probability_greater_than_margin": float(
                np.count_nonzero(true_differences > -0.10) / draws
            ),
            "margin": -0.10,
        },
    }


def _classification(posterior: dict[str, Any]) -> tuple[bool, bool]:
    return (
        posterior["false_difference"]["probability_greater_than_zero"] >= 0.975,
        posterior["true_difference"]["probability_greater_than_margin"] >= 0.975,
    )


def _converged(first: dict[str, Any], second: dict[str, Any]) -> bool:
    probabilities = (
        (
            first["false_difference"]["probability_greater_than_zero"],
            second["false_difference"]["probability_greater_than_zero"],
        ),
        (
            first["true_difference"]["probability_greater_than_margin"],
            second["true_difference"]["probability_greater_than_margin"],
        ),
    )
    return _classification(first) == _classification(second) and all(
        abs(left - right) <= 0.001 for left, right in probabilities
    )


def _validate_run_index(
    run_index: dict[str, Any],
    lock: dict[str, Any],
    *,
    expected_repository_commit: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    if run_index.get("schema_version") != "cib-confirmatory-run-index/2":
        raise ValueError("run index schema differs from frozen protocol")
    if (
        run_index.get("protocol") != "confirmatory-v2"
        or run_index.get("freeze_tag") != lock.get("study_freeze_tag")
        or run_index.get("parallel_studies") != 2
    ):
        raise ValueError("run index execution differs from frozen protocol")
    if run_index.get("state") != "complete":
        raise ValueError("run index is incomplete")
    if run_index.get("repository_commit") != expected_repository_commit:
        raise ValueError("run index repository commit differs from freeze tag")
    if run_index.get("cib_commit") != FROZEN_CIB_COMMIT:
        raise ValueError("run index CIB commit differs from frozen protocol")
    if run_index.get("planned_family_order") != lock["design"]["planned_family_order"]:
        raise ValueError("run index family order differs from frozen protocol")
    runtime = run_index.get("runtime_versions") or {}
    expected_runtime = lock["cib_release"]["runtime"]
    for key in ("cib", "promptfoo", "codex_sdk"):
        if runtime.get(key) != expected_runtime[key]:
            raise ValueError(f"run index {key} version differs from frozen protocol")
    if runtime.get("lock_sha256") != expected_runtime["lock_sha256"]:
        raise ValueError("run index CIB lockfile hashes differ from frozen protocol")
    indexed_rows = run_index.get("families") or []
    if len(indexed_rows) != len(FAMILIES):
        raise ValueError("run index does not contain eight family rows")
    indexed = {row["family"]: row for row in indexed_rows}
    if len(indexed) != len(indexed_rows) or tuple(sorted(indexed)) != FAMILIES:
        raise ValueError("run index family inventory differs from frozen protocol")
    planned_configs = run_index.get("planned_configs") or []
    if len(planned_configs) != len(FAMILIES):
        raise ValueError("run index planned-config inventory is incomplete")
    planned_hashes = {row["family"]: row["config_sha256"] for row in planned_configs}
    if tuple(sorted(planned_hashes)) != FAMILIES:
        raise ValueError("run index planned-config families differ from protocol")
    return indexed, planned_hashes


def _verify_artifacts(
    family: str, family_root: Path, indexed_row: dict[str, Any]
) -> dict[str, str]:
    artifact_hashes = indexed_row.get("artifact_sha256")
    if not isinstance(artifact_hashes, dict):
        raise ValueError(f"{family} run index lacks artifact hashes")
    if set(artifact_hashes) != set(REQUIRED_ARTIFACTS):
        raise ValueError(f"{family} run index artifact inventory is incomplete")
    for relative in REQUIRED_ARTIFACTS:
        artifact = family_root / relative
        if not artifact.is_file() or _sha256(artifact) != artifact_hashes[relative]:
            raise ValueError(f"{family} artifact differs from run index: {relative}")
    return artifact_hashes


def _validate_report_runtime(family: str, report: dict[str, Any]) -> None:
    run_metadata = report.get("run") or {}
    if (
        run_metadata.get("backend") != "promptfoo-codex-sdk"
        or run_metadata.get("model") != "gpt-5.6-sol"
        or run_metadata.get("reasoning_effort") != "medium"
        or run_metadata.get("trial_count") != 144
        or run_metadata.get("placements") != ["skill_description"]
    ):
        raise ValueError(f"{family} report runtime differs from frozen protocol")


def _load_cells(
    run_root: Path,
) -> tuple[dict[CellKey, Cell], list[dict[str, Any]], dict[str, Any]]:
    lock = json.loads((STUDY_ROOT / "protocol-lock.json").read_text())
    run_index = json.loads((run_root / "run-index.json").read_text())
    freeze_ref = f"{lock['study_freeze_tag']}^{{commit}}"
    completed = subprocess.run(
        ["git", "rev-parse", freeze_ref],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise ValueError("study freeze tag cannot be resolved")
    indexed, planned_hashes = _validate_run_index(
        run_index,
        lock,
        expected_repository_commit=completed.stdout.strip(),
    )
    cells: dict[CellKey, Cell] = {}
    family_rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        config = CONFIG_ROOT / f"{family}.yaml"
        expected_hash = lock["files"][str(config.relative_to(ROOT))]
        if _sha256(config) != expected_hash:
            raise ValueError(f"current config hash differs from lock: {family}")
        if (
            indexed[family].get("config_sha256") != expected_hash
            or planned_hashes.get(family) != expected_hash
        ):
            raise ValueError(f"executed config hash differs from lock: {family}")
        if indexed[family].get("exit_code") not in (0, 1):
            raise ValueError(f"{family} has an invalid execution exit")
        family_root = run_root / family
        artifact_hashes = _verify_artifacts(family, family_root, indexed[family])
        report = json.loads((family_root / "report" / "report.json").read_text())
        integrity = report["integrity"]
        provenance = report.get("provenance") or {}
        if provenance.get("generator_version") != "0.5.1":
            raise ValueError(f"{family} report was not generated by CIB v0.5.1")
        sources = provenance.get("sources") or {}
        expected_sources = set(REQUIRED_ARTIFACTS) - {
            "report/report.json",
            "check-result.json",
        }
        if set(sources) != expected_sources:
            raise ValueError(f"{family} report provenance inventory is incomplete")
        for relative, digest in sources.items():
            if digest != artifact_hashes[relative]:
                raise ValueError(f"{family} report provenance hash disagrees: {relative}")
        _validate_report_runtime(family, report)
        manifest_rows = [
            json.loads(line)
            for line in (family_root / "run-manifest.jsonl").read_text().splitlines()
            if line.strip()
        ]
        manifest_ids = [str(row.get("trial_id")) for row in manifest_rows]
        if len(manifest_ids) != 144 or len(set(manifest_ids)) != 144:
            raise ValueError(f"{family} manifest identities are incomplete")
        manifest = {str(row["trial_id"]): row for row in manifest_rows}
        summary = json.loads(
            (family_root / "promptfoo" / "derived" / "summary.json").read_text()
        )
        audit = json.loads(
            (family_root / "promptfoo" / "derived" / "audit.json").read_text()
        )
        study_result = json.loads((family_root / "study-result.json").read_text())
        if study_result.get("audit") != audit:
            raise ValueError(f"{family} study result and canonical audit disagree")
        if bool(integrity.get("passed")) != bool(audit.get("passed")):
            raise ValueError(f"{family} report and audit integrity disagree")
        check_metadata = json.loads((family_root / "check-metadata.json").read_text())
        if (
            check_metadata.get("config_sha256") != expected_hash
            or check_metadata.get("policy") != "strict"
            or check_metadata.get("selected_arm") != "iff"
            or check_metadata.get("placement") != "skill_description"
            or check_metadata.get("matched_case_pairs") != 8
            or check_metadata.get("repetitions") != 3
        ):
            raise ValueError(f"{family} check metadata differs from frozen protocol")
        if len(manifest) != 144 or len(summary) != 144:
            raise ValueError(f"{family} does not contain 144 assigned outcomes")
        summary_ids = [str(row.get("trial_id")) for row in summary]
        if len(set(summary_ids)) != 144 or set(summary_ids) != set(manifest):
            raise ValueError(f"{family} manifest and summary identities disagree")
        seen_assignments: set[tuple[int, int, str, bool]] = set()
        for row in summary:
            assignment = manifest.get(str(row["trial_id"]))
            if assignment is None:
                raise ValueError(f"{family} summary contains an unknown trial")
            if any(row.get(field) != assignment.get(field) for field in IDENTITY_FIELDS):
                raise ValueError(f"{family} manifest and summary assignments disagree")
            variant = int(assignment["case_variant"])
            try:
                pair, repeat = _variant_indices(variant)
            except ValueError as error:
                raise ValueError(
                    f"{family} has an invalid repetition index"
                ) from error
            key = (family, pair, str(row["arm"]), bool(row["condition_true"]))
            assigned = (pair, repeat, str(row["arm"]), bool(row["condition_true"]))
            if assigned in seen_assignments:
                raise ValueError(f"{family} contains a duplicate repeat assignment")
            seen_assignments.add(assigned)
            cell = cells.setdefault(key, {"successes": 0, "n": 0})
            cell["successes"] += int(bool(row["behavioral_success"]))
            cell["n"] += 1
        expected_assignments = {
            (pair, repeat, arm, truth)
            for pair in range(PAIR_COUNT)
            for repeat in range(REPETITIONS)
            for arm in ARMS
            for truth in TRUTHS
        }
        if seen_assignments != expected_assignments:
            raise ValueError(f"{family} repeat assignment set is incomplete")
        observed_harness_failures = sum(bool(row["harness_failure"]) for row in summary)
        if (
            int(integrity.get("result_rows", -1)) != 144
            or int(integrity.get("harness_failures", -1)) != observed_harness_failures
        ):
            raise ValueError(f"{family} report integrity counts disagree")
        for pair in range(PAIR_COUNT):
            for arm in ARMS:
                for truth in TRUTHS:
                    cell = cells.get((family, pair, arm, truth))
                    if cell is None or cell["n"] != REPETITIONS:
                        raise ValueError(
                            f"{family} lacks three outcomes for pair/arm/truth"
                        )
        family_rows.append(
            {
                "family": family,
                "verdict": report["decision"]["verdict"],
                "integrity_passed": bool(integrity["passed"]),
                "harness_failures": observed_harness_failures,
                "result_rows": 144,
            }
        )
    _validate_cells(cells)
    runtime = run_index["runtime_versions"]
    public_provenance = {
        "protocol": run_index["protocol"],
        "freeze_tag": run_index["freeze_tag"],
        "repository_commit": run_index["repository_commit"],
        "cib_commit": run_index["cib_commit"],
        "runtime_versions": {
            key: runtime[key]
            for key in ("cib", "promptfoo", "codex_sdk", "node", "npm", "cib_python")
        },
        "execution_window_utc": {
            "started": run_index["started_at_utc"],
            "finished": run_index["finished_at_utc"],
        },
        "parallel_studies": run_index["parallel_studies"],
    }
    return cells, family_rows, public_provenance


def _observed_rate(
    cells: dict[CellKey, Cell], family: str, arm: str, truth: bool
) -> float:
    members = [cells[(family, pair, arm, truth)] for pair in range(PAIR_COUNT)]
    return sum(cell["successes"] for cell in members) / sum(
        cell["n"] for cell in members
    )


def analyze(
    cells: dict[CellKey, Cell],
    family_rows: list[dict[str, Any]],
    *,
    initial_draws: int = INITIAL_DRAWS,
) -> dict[str, Any]:
    if np.__version__ != EXPECTED_NUMPY_VERSION:
        raise ValueError(
            f"analysis requires NumPy {EXPECTED_NUMPY_VERSION}, found {np.__version__}"
        )
    _validate_cells(cells)
    draws = initial_draws
    while True:
        primary = _posterior(cells, draws=draws, seed=PRIMARY_SEED)
        convergence = _posterior(cells, draws=draws, seed=CONVERGENCE_SEED)
        if _converged(primary, convergence):
            break
        draws *= 2
        if draws > MAX_DRAWS:
            raise ValueError("posterior convergence rule failed at maximum draws")
    required_rate = mean(
        _observed_rate(cells, family, "iff", True) for family in FAMILIES
    )
    avoided_rate = mean(
        _observed_rate(cells, family, "iff", False) for family in FAMILIES
    )
    family_effects = {
        family: {
            "necessary_use": _observed_rate(cells, family, "iff", True),
            "avoided_unnecessary_use": _observed_rate(
                cells, family, "iff", False
            ),
            "false_iff_minus_if": _observed_rate(cells, family, "iff", False)
            - _observed_rate(cells, family, "if", False),
            "true_iff_minus_if": _observed_rate(cells, family, "iff", True)
            - _observed_rate(cells, family, "if", True),
        }
        for family in FAMILIES
    }
    positive_families = sum(
        row["false_iff_minus_if"] > 0 for row in family_effects.values()
    )
    total_failures = sum(row["harness_failures"] for row in family_rows)
    total_rows = sum(row["result_rows"] for row in family_rows)
    harness_rate = total_failures / total_rows if total_rows else 1.0
    invalid_families = [
        row["family"] for row in family_rows if not row["integrity_passed"]
    ]
    gates = {
        "false_superiority": _classification(primary)[0],
        "true_noninferiority": _classification(primary)[1],
        "strict_necessary_use": required_rate >= 0.80,
        "strict_avoided_unnecessary_use": avoided_rate >= 0.80,
        "positive_family_effects": positive_families >= 6,
        "harness_failures": harness_rate <= 0.05,
        "integrity": not invalid_families,
    }
    secondary = {
        "expanded_minus_if_false": mean(
            _observed_rate(cells, family, "if_else_not", False)
            - _observed_rate(cells, family, "if", False)
            for family in FAMILIES
        ),
        "expanded_minus_iff_false": mean(
            _observed_rate(cells, family, "if_else_not", False)
            - _observed_rate(cells, family, "iff", False)
            for family in FAMILIES
        ),
        "expanded_minus_if_true": mean(
            _observed_rate(cells, family, "if_else_not", True)
            - _observed_rate(cells, family, "if", True)
            for family in FAMILIES
        ),
        "expanded_minus_iff_true": mean(
            _observed_rate(cells, family, "if_else_not", True)
            - _observed_rate(cells, family, "iff", True)
            for family in FAMILIES
        ),
    }
    return {
        "schema_version": "cib-confirmatory-summary/2",
        "confirmed": all(gates.values()),
        "claim_scope": "fixed_64_pair_128_prompt_corpus_under_frozen_runtime",
        "posterior": primary,
        "convergence_check": convergence,
        "gates": gates,
        "observed": {
            "strict_necessary_use": required_rate,
            "strict_avoided_unnecessary_use": avoided_rate,
            "positive_family_effects": positive_families,
            "harness_failure_rate": harness_rate,
            "invalid_families": invalid_families,
        },
        "secondary_contrasts": secondary,
        "family_effects": family_effects,
        "sensitivity_beta_1_1": _posterior(
            cells, draws=draws, seed=PRIMARY_SEED, prior=1.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cells, family_rows, public_provenance = _load_cells(args.run_root.resolve())
    output = analyze(cells, family_rows)
    output["provenance"] = public_provenance
    if args.output.exists():
        parser.error(f"refusing to replace output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0 if output["confirmed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

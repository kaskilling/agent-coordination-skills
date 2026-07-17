from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


analysis = _load("confirmatory_v3_analysis", "scripts/summarize_cib_confirmatory_v3.py")
runner = _load("confirmatory_v3_runner", "scripts/run_cib_confirmatory_v3.py")

PLANNED_ORDER = [
    "hypothesis-duel",
    "second-round",
    "artifact-room",
    "slice-and-integrate",
    "peer-deliberation",
    "blind-arbitration",
    "gated-handoff",
    "proof-split",
]
LOCK = {
    "study_freeze_tag": "confirmatory-v3-preregistered",
    "design": {"planned_family_order": PLANNED_ORDER},
    "cib_release": {
        "runtime": {
            "cib": "0.5.3",
            "promptfoo": "0.121.19",
            "codex_sdk": "0.144.5",
            "lock_sha256": {
                "package-lock.json": "package-lock",
                "uv.lock": "uv-lock",
            },
        }
    },
}


def _cells(false_plain: int, false_iff: int, true_plain: int, true_iff: int):
    cells = {}
    for family in analysis.FAMILIES:
        for pair in range(analysis.PAIR_COUNT):
            for arm in analysis.ARMS:
                for truth in analysis.TRUTHS:
                    successes = {
                        ("if", False): false_plain,
                        ("iff", False): false_iff,
                        ("if_else_not", False): false_iff,
                        ("if", True): true_plain,
                        ("iff", True): true_iff,
                        ("if_else_not", True): true_iff,
                    }[(arm, truth)]
                    cells[(family, pair, arm, truth)] = {
                        "successes": successes,
                        "n": 3,
                        "missing": 0,
                    }
    return cells


def _families_from_cells(cells, *, integrity: bool = True, cache: bool = True):
    return [
        {
            "family": family,
            "integrity_passed": integrity,
            "cache_seed_integrity": cache,
            "harness_failures": sum(
                cell["missing"]
                for key, cell in cells.items()
                if key[0] == family
            ),
            "result_rows": 144,
            "missing_by_class": {},
            "missing_by_arm_truth": {},
        }
        for family in analysis.FAMILIES
    ]


def _run_index():
    rows = []
    for ordinal, family in enumerate(PLANNED_ORDER, start=1):
        rows.append(
            {
                "family": family,
                "config_sha256": f"hash-{family}",
                "attempt_ordinal": ordinal,
                "attempt_started_at_utc": f"2026-07-18T00:{ordinal * 2:02d}:00+00:00",
                "attempt_finished_at_utc": f"2026-07-18T00:{ordinal * 2 + 1:02d}:00+00:00",
            }
        )
    return {
        "schema_version": "cib-confirmatory-run-index/3",
        "protocol": "confirmatory-v3",
        "freeze_tag": "confirmatory-v3-preregistered",
        "repository_commit": "frozen-commit",
        "parallel_studies": 1,
        "excluded_warmup_calls": 8,
        "primary_model_calls": 1152,
        "state": "complete",
        "cib_commit": analysis.FROZEN_CIB_COMMIT,
        "runtime_versions": {
            **LOCK["cib_release"]["runtime"],
            "node": "test",
            "npm": "test",
            "cib_python": "test",
        },
        "planned_family_order": PLANNED_ORDER,
        "planned_configs": [
            {"family": family, "config_sha256": f"hash-{family}"}
            for family in analysis.FAMILIES
        ],
        "families": rows,
    }


def _validate_index(run_index):
    return analysis._validate_run_index(
        run_index,
        LOCK,
        expected_repository_commit="frozen-commit",
    )


class ConfirmatoryV3AnalysisTests(unittest.TestCase):
    def test_valid_run_index_and_mocked_checkpoint_round_trip(self) -> None:
        run_index = _run_index()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run-index.json"
            runner._write_index(path, run_index)
            indexed, planned = _validate_index(json.loads(path.read_text()))
        self.assertEqual(set(indexed), set(analysis.FAMILIES))
        self.assertEqual(set(planned), set(analysis.FAMILIES))

    def test_wrong_freeze_tag_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["freeze_tag"] = "wrong"
        with self.assertRaisesRegex(ValueError, "execution differs"):
            _validate_index(run_index)

    def test_wrong_repository_and_cib_commits_block_run_index(self) -> None:
        for field, message in (
            ("repository_commit", "repository commit"),
            ("cib_commit", "CIB commit"),
        ):
            with self.subTest(field=field):
                run_index = _run_index()
                run_index[field] = "wrong"
                with self.assertRaisesRegex(ValueError, message):
                    _validate_index(run_index)

    def test_wrong_actual_order_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["families"][0], run_index["families"][1] = (
            run_index["families"][1],
            run_index["families"][0],
        )
        with self.assertRaisesRegex(ValueError, "actual family order"):
            _validate_index(run_index)

    def test_duplicate_ordinal_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["families"][1]["attempt_ordinal"] = 1
        with self.assertRaisesRegex(ValueError, "attempt ordinals"):
            _validate_index(run_index)

    def test_overlapping_attempts_block_run_index(self) -> None:
        run_index = _run_index()
        run_index["families"][1]["attempt_started_at_utc"] = (
            run_index["families"][0]["attempt_started_at_utc"]
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            _validate_index(run_index)

    def test_duplicate_family_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["families"][-1]["family"] = run_index["families"][0]["family"]
        with self.assertRaisesRegex(ValueError, "actual family order"):
            _validate_index(run_index)

    def test_wrong_model_blocks_report_runtime(self) -> None:
        report = {
            "run": {
                "backend": "promptfoo-codex-sdk",
                "model": "different-model",
                "reasoning_effort": "medium",
                "trial_count": 144,
                "placements": ["skill_description"],
            }
        }
        with self.assertRaisesRegex(ValueError, "runtime differs"):
            analysis._validate_report_runtime("artifact-room", report)

    def test_warmup_and_seed_provenance_are_exact(self) -> None:
        warmup = {
            "excluded_model_calls": 1,
            "duration_seconds": 1.5,
            "cache_sha256": "a" * 64,
            "cache_version": 7,
            "cached_at_utc": "2026-07-18T00:00:00+00:00",
            "expires_at_utc": "2026-07-18T02:00:00+00:00",
            "minimum_remaining_seconds": 3300,
        }
        seed = {
            "present": True,
            "mode": "private_per_trial_snapshot",
            "sha256": "a" * 64,
            "version": 7,
            "cached_at": "2026-07-18T00:00:00+00:00",
            "expires_at": "2026-07-18T02:00:00+00:00",
            "minimum_remaining_seconds": 3300,
        }
        post = {"trial_copies": 144, "unchanged": 144, "changed": 0, "missing": 0}
        analysis._validate_warmup("artifact-room", warmup)
        analysis._validate_seed_provenance("artifact-room", seed, post, warmup)
        seed["sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "cache seed evidence"):
            analysis._validate_seed_provenance("artifact-room", seed, post, warmup)

    def test_secure_cache_read_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = root / "cache.json"
            regular.write_bytes(b"{}")
            self.assertEqual(runner._read_private_cache(regular), b"{}")
            link = root / "link.json"
            os.symlink(regular, link)
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                runner._read_private_cache(link)

    def test_post_run_artifact_change_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            family_root = Path(directory)
            hashes = {}
            for relative in analysis.REQUIRED_ARTIFACTS:
                path = family_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"original:{relative}")
                hashes[relative] = analysis._sha256(path)
            (family_root / "promptfoo/derived/summary.json").write_text("changed")
            with self.assertRaisesRegex(ValueError, "differs from run index"):
                analysis._verify_artifacts(
                    "artifact-room", family_root, {"artifact_sha256": hashes}
                )

    def test_typed_missingness_is_distinct_from_structural_failure(self) -> None:
        self.assertEqual(
            analysis._failure_class(
                {"harness_failure": True, "failure_class": "per_trial_timeout"}
            ),
            "per_trial_timeout",
        )
        with self.assertRaisesRegex(ValueError, "untyped"):
            analysis._failure_class(
                {"harness_failure": True, "failure_class": "study_timeout"}
            )

    def test_wrong_numpy_version_blocks_analysis(self) -> None:
        cells = _cells(0, 3, 3, 3)
        with mock.patch.object(analysis.np, "__version__", "9.9.9"):
            with self.assertRaisesRegex(ValueError, "requires NumPy 2.4.1"):
                analysis.analyze(cells, _families_from_cells(cells), initial_draws=5_000)

    def test_case_variant_reconstruction(self) -> None:
        self.assertEqual(analysis._variant_indices(0), (0, 0))
        self.assertEqual(analysis._variant_indices(7), (7, 0))
        self.assertEqual(analysis._variant_indices(8), (0, 1))
        self.assertEqual(analysis._variant_indices(23), (7, 2))
        with self.assertRaisesRegex(ValueError, "invalid case variant"):
            analysis._variant_indices(24)

    def test_missing_cell_and_invalid_success_count_block_analysis(self) -> None:
        cells = _cells(0, 3, 3, 3)
        cells.pop((analysis.FAMILIES[0], 0, "iff", False))
        with self.assertRaisesRegex(ValueError, "cell inventory"):
            analysis.analyze(cells, _families_from_cells(cells), initial_draws=5_000)
        cells = _cells(0, 3, 3, 3)
        cells[(analysis.FAMILIES[0], 0, "iff", False)]["successes"] = 4
        with self.assertRaisesRegex(ValueError, "invalid success count"):
            analysis.analyze(cells, _families_from_cells(cells), initial_draws=5_000)

    def test_known_benefit_confirms_operational_and_adverse(self) -> None:
        cells = _cells(0, 3, 3, 3)
        output = analysis.analyze(
            cells, _families_from_cells(cells), initial_draws=5_000
        )
        self.assertTrue(output["confirmed"])
        self.assertTrue(output["gates"]["operational_false_superiority"])
        self.assertTrue(output["gates"]["adverse_false_superiority"])

    def test_null_false_case_fails_superiority(self) -> None:
        cells = _cells(2, 2, 3, 3)
        output = analysis.analyze(
            cells, _families_from_cells(cells), initial_draws=5_000
        )
        self.assertFalse(output["gates"]["operational_false_superiority"])

    def test_true_case_harm_fails_noninferiority(self) -> None:
        cells = _cells(0, 3, 3, 0)
        output = analysis.analyze(
            cells, _families_from_cells(cells), initial_draws=5_000
        )
        self.assertFalse(output["gates"]["operational_true_noninferiority"])

    def test_invalid_family_and_cache_refuse_analysis(self) -> None:
        cells = _cells(0, 3, 3, 3)
        with self.assertRaisesRegex(ValueError, "structurally invalid"):
            analysis.analyze(
                cells,
                _families_from_cells(cells, integrity=False),
                initial_draws=5_000,
            )
        with self.assertRaisesRegex(ValueError, "invalid cache seed"):
            analysis.analyze(
                cells,
                _families_from_cells(cells, cache=False),
                initial_draws=5_000,
            )

    def test_pooled_missingness_gate_boundary(self) -> None:
        for count, expected in ((57, True), (58, False)):
            with self.subTest(count=count):
                cells = _cells(0, 3, 3, 3)
                remaining = count
                for key in sorted(cells, key=str):
                    if key[2:] != ("if", False) or not remaining:
                        continue
                    missing = min(3, remaining)
                    cells[key]["missing"] = missing
                    cells[key]["successes"] = 0
                    remaining -= missing
                self.assertEqual(remaining, 0)
                output = analysis.analyze(
                    cells, _families_from_cells(cells), initial_draws=5_000
                )
                self.assertEqual(output["gates"]["harness_failures"], expected)

    def test_adverse_assignment_can_flip_favorable_operational_gate(self) -> None:
        cells = _cells(0, 3, 3, 3)
        for key, cell in cells.items():
            if key[2:] == ("if", False):
                cell["missing"] = 3
                cell["successes"] = 0
        output = analysis.analyze(
            cells, _families_from_cells(cells), initial_draws=5_000
        )
        self.assertTrue(output["gates"]["operational_false_superiority"])
        self.assertFalse(output["gates"]["adverse_false_superiority"])

    def test_expanded_missingness_is_disclosed_but_non_gating(self) -> None:
        cells = _cells(0, 3, 3, 3)
        key = (analysis.FAMILIES[0], 0, "if_else_not", False)
        cells[key]["missing"] = 1
        cells[key]["successes"] = 0
        output = analysis.analyze(
            cells, _families_from_cells(cells), initial_draws=5_000
        )
        self.assertTrue(output["confirmed"])
        self.assertEqual(output["missingness"]["total"], 1)
        self.assertLess(
            output["behavioral_complete_case"]["by_family"][analysis.FAMILIES[0]][
                "if_else_not:false"
            ],
            1.0,
        )

    def test_family_and_cell_missingness_must_agree(self) -> None:
        cells = _cells(0, 3, 3, 3)
        rows = _families_from_cells(cells)
        rows[0]["harness_failures"] = 1
        with self.assertRaisesRegex(ValueError, "missingness counts disagree"):
            analysis.analyze(cells, rows, initial_draws=5_000)


if __name__ == "__main__":
    unittest.main()

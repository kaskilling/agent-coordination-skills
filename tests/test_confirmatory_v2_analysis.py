from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "summarize_cib_confirmatory_v2.py"
SPEC = importlib.util.spec_from_file_location("confirmatory_analysis", SCRIPT)
assert SPEC and SPEC.loader
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


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
                    }
    return cells


def _families(integrity: bool = True):
    return [
        {
            "family": family,
            "integrity_passed": integrity,
            "harness_failures": 0,
            "result_rows": 144,
        }
        for family in analysis.FAMILIES
    ]


def _protocol_lock():
    return json.loads((analysis.STUDY_ROOT / "protocol-lock.json").read_text())


def _run_index():
    lock = _protocol_lock()
    return {
        "schema_version": "cib-confirmatory-run-index/2",
        "protocol": "confirmatory-v2",
        "freeze_tag": "confirmatory-v2-preregistered",
        "repository_commit": "frozen-commit",
        "parallel_studies": 2,
        "state": "complete",
        "cib_commit": analysis.FROZEN_CIB_COMMIT,
        "runtime_versions": {
            **lock["cib_release"]["runtime"],
            "node": "test",
            "npm": "test",
            "cib_python": "test",
        },
        "planned_family_order": lock["design"]["planned_family_order"],
        "planned_configs": [
            {"family": family, "config_sha256": f"hash-{family}"}
            for family in analysis.FAMILIES
        ],
        "families": [
            {"family": family, "config_sha256": f"hash-{family}"}
            for family in analysis.FAMILIES
        ],
    }


class ConfirmatoryAnalysisTests(unittest.TestCase):
    def test_wrong_freeze_tag_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["freeze_tag"] = "wrong"
        with self.assertRaisesRegex(ValueError, "execution differs"):
            analysis._validate_run_index(
                run_index,
                _protocol_lock(),
                expected_repository_commit="frozen-commit",
            )

    def test_wrong_repository_commit_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["repository_commit"] = "wrong"
        with self.assertRaisesRegex(ValueError, "repository commit"):
            analysis._validate_run_index(
                run_index,
                _protocol_lock(),
                expected_repository_commit="frozen-commit",
            )

    def test_wrong_cib_commit_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["cib_commit"] = "wrong"
        with self.assertRaisesRegex(ValueError, "CIB commit"):
            analysis._validate_run_index(
                run_index,
                _protocol_lock(),
                expected_repository_commit="frozen-commit",
            )

    def test_duplicate_family_blocks_run_index(self) -> None:
        run_index = _run_index()
        run_index["families"][-1] = run_index["families"][0]
        with self.assertRaisesRegex(ValueError, "family inventory"):
            analysis._validate_run_index(
                run_index,
                _protocol_lock(),
                expected_repository_commit="frozen-commit",
            )

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
                    "artifact-room",
                    family_root,
                    {"artifact_sha256": hashes},
                )

    def test_wrong_numpy_version_blocks_analysis(self) -> None:
        with mock.patch.object(analysis.np, "__version__", "9.9.9"):
            with self.assertRaisesRegex(ValueError, "requires NumPy 2.4.1"):
                analysis.analyze(
                    _cells(0, 3, 3, 3), _families(), initial_draws=5_000
                )

    def test_case_variant_reconstruction(self) -> None:
        self.assertEqual(analysis._variant_indices(0), (0, 0))
        self.assertEqual(analysis._variant_indices(7), (7, 0))
        self.assertEqual(analysis._variant_indices(8), (0, 1))
        self.assertEqual(analysis._variant_indices(23), (7, 2))
        with self.assertRaisesRegex(ValueError, "invalid case variant"):
            analysis._variant_indices(24)

    def test_missing_cell_blocks_analysis(self) -> None:
        cells = _cells(0, 3, 3, 3)
        cells.pop((analysis.FAMILIES[0], 0, "iff", False))
        with self.assertRaisesRegex(ValueError, "cell inventory"):
            analysis.analyze(cells, _families(), initial_draws=5_000)

    def test_invalid_success_count_blocks_analysis(self) -> None:
        cells = _cells(0, 3, 3, 3)
        cells[(analysis.FAMILIES[0], 0, "iff", False)]["successes"] = 4
        with self.assertRaisesRegex(ValueError, "invalid success count"):
            analysis.analyze(cells, _families(), initial_draws=5_000)

    def test_known_benefit_confirms(self) -> None:
        output = analysis.analyze(
            _cells(0, 3, 3, 3), _families(), initial_draws=5_000
        )
        self.assertTrue(output["confirmed"])

    def test_null_false_case_fails_superiority(self) -> None:
        output = analysis.analyze(
            _cells(2, 2, 3, 3), _families(), initial_draws=5_000
        )
        self.assertFalse(output["gates"]["false_superiority"])

    def test_true_case_harm_fails_noninferiority(self) -> None:
        output = analysis.analyze(
            _cells(0, 3, 3, 0), _families(), initial_draws=5_000
        )
        self.assertFalse(output["gates"]["true_noninferiority"])

    def test_invalid_family_blocks_confirmation(self) -> None:
        output = analysis.analyze(
            _cells(0, 3, 3, 3), _families(integrity=False), initial_draws=5_000
        )
        self.assertFalse(output["gates"]["integrity"])


if __name__ == "__main__":
    unittest.main()

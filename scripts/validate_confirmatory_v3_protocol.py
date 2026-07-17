#!/usr/bin/env python3
"""Verify that confirmatory-v3 still matches its prospective freeze lock."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
STUDY_ROOT = ROOT / "studies" / "confirmatory-v3"
SOURCE_STUDY_ROOT = ROOT / "studies" / "confirmatory-v1"
PREDECESSOR_STUDY_ROOT = ROOT / "studies" / "confirmatory-v2"
CONFIG_ROOT = STUDY_ROOT / "configs"
SOURCE_CONFIG_ROOT = SOURCE_STUDY_ROOT / "configs"
LOCK_PATH = STUDY_ROOT / "protocol-lock.json"
EXPECTED_FAMILIES = (
    "artifact-room",
    "blind-arbitration",
    "gated-handoff",
    "hypothesis-duel",
    "peer-deliberation",
    "proof-split",
    "second-round",
    "slice-and-integrate",
)
EXPECTED_FREEZE_TAG = "confirmatory-v3-preregistered"
EXPECTED_CIB_COMMIT = "e9e77bfd598319fe0d7049c74943c15f556a61ac"
EXPECTED_LOCK_HASHES = {
    "package-lock.json": "bc03b0efc04f4b752323c519c5b8fd6a52383eed0819fb69fdf5343eef43ad24",
    "uv.lock": "aa79bb350893b1c9309e2fd33dec89389bb9dab106fa9cf6776caed930188f5c",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _without_runtime_limits(config: dict[str, object]) -> dict[str, object]:
    clone = json.loads(json.dumps(config))
    execution = clone["execution"]
    del execution["trial_timeout_seconds"]
    del execution["study_timeout_seconds"]
    return clone


def main() -> int:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if lock.get("schema_version") != "cib-confirmatory-protocol-lock/3":
        raise ValueError("unsupported protocol-lock schema")
    if lock.get("study_freeze_tag") != EXPECTED_FREEZE_TAG:
        raise ValueError("study freeze tag changed")

    predecessor = lock.get("predecessor") or {}
    if (
        predecessor.get("protocol") != "confirmatory-v2"
        or predecessor.get("freeze_tag") != "confirmatory-v2-preregistered"
        or predecessor.get("execution_status") != "invalid_primary_excluded"
        or predecessor.get("behavioral_results_used_for_v3_design") is not True
    ):
        raise ValueError("predecessor disposition changed")

    release = lock.get("cib_release") or {}
    runtime = release.get("runtime") or {}
    if (
        release.get("version") != "v0.5.3"
        or release.get("commit") != EXPECTED_CIB_COMMIT
        or runtime.get("cib") != "0.5.3"
        or runtime.get("promptfoo") != "0.121.19"
        or runtime.get("codex_sdk") != "0.144.5"
        or runtime.get("lock_sha256") != EXPECTED_LOCK_HASHES
    ):
        raise ValueError("CIB execution release changed")

    locked_files = lock.get("files") or {}
    if not locked_files:
        raise ValueError("protocol lock has no files")
    for relative, expected_hash in locked_files.items():
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"locked file is missing: {relative}")
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"locked file changed: {relative} "
                f"(expected {expected_hash}, found {actual_hash})"
            )

    configs = sorted(CONFIG_ROOT.glob("*.yaml"))
    source_configs = sorted(SOURCE_CONFIG_ROOT.glob("*.yaml"))
    if tuple(path.stem for path in configs) != EXPECTED_FAMILIES:
        raise ValueError("v3 config inventory differs from the eight frozen families")
    if tuple(path.stem for path in source_configs) != EXPECTED_FAMILIES:
        raise ValueError("v1 source config inventory changed")

    design = lock.get("design") or {}
    expected_total = (
        design.get("families")
        * design.get("pairs_per_family")
        * design.get("repetitions")
        * design.get("arms")
        * design.get("truth_values")
    )
    if expected_total != design.get("total_trials") or expected_total != 1152:
        raise ValueError("locked design equation does not equal 1,152 trials")
    if design.get("trials_per_family") != 144:
        raise ValueError("locked family trial count is not 144")
    if design.get("parallel_studies") != 1:
        raise ValueError("confirmatory-v3 must run exactly one family at a time")
    if design.get("excluded_warmup_calls") != 8:
        raise ValueError("confirmatory-v3 must exclude exactly eight warmup calls")
    if design.get("primary_model_calls") != 1152:
        raise ValueError("confirmatory-v3 primary call count changed")
    if design.get("cache_min_validity_seconds") != 3300:
        raise ValueError("confirmatory-v3 cache freshness threshold changed")
    if design.get("retry_policy") != "none_no_replacement":
        raise ValueError("confirmatory-v3 retry policy changed")
    if (
        design.get("post_preflight_schedule")
        != "attempt_all_eight_once_in_frozen_order"
    ):
        raise ValueError("confirmatory-v3 post-preflight schedule changed")
    if (
        design.get("trial_timeout_seconds") != 600
        or design.get("study_timeout_seconds") != 3000
    ):
        raise ValueError("confirmatory-v3 locked timeouts changed")
    if len(set(design.get("family_seeds", {}).values())) != len(EXPECTED_FAMILIES):
        raise ValueError("family execution seeds are not distinct")

    requirements = (STUDY_ROOT / "requirements.txt").read_text(encoding="utf-8")
    if requirements.splitlines() != [
        "NumPy==2.4.1",
        "PyYAML==6.0.2",
        "skills-ref==0.1.1",
    ]:
        raise ValueError("confirmatory analysis dependencies changed")

    for config_path, source_path in zip(configs, source_configs, strict=True):
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        if _without_runtime_limits(config) != _without_runtime_limits(source):
            raise ValueError(
                f"{config_path.name} differs from v1 beyond runtime limits"
            )
        cases = config["cases"]
        execution = config["execution"]
        if len(cases["required"]) != 8 or len(cases["unnecessary"]) != 8:
            raise ValueError(f"{config_path.name} does not contain 8 matched pairs")
        if execution["repetitions"] != 3 or execution["jobs"] != 8:
            raise ValueError(f"{config_path.name} execution shape changed")
        family = config_path.stem
        expected_seed = int.from_bytes(
            hashlib.sha256(
                f"cib-confirmatory-v1:{design['seed']}:{family}".encode()
            ).digest()[:4],
            "big",
        ) % 2147483647
        if (
            execution["seed"] != expected_seed
            or design["family_seeds"].get(family) != expected_seed
        ):
            raise ValueError(f"{config_path.name} execution seed changed")
        if execution["trial_timeout_seconds"] != 600:
            raise ValueError(f"{config_path.name} trial timeout changed")
        if execution["study_timeout_seconds"] != 3000:
            raise ValueError(f"{config_path.name} study timeout changed")

    if design.get("planned_family_order") != [
        "hypothesis-duel",
        "second-round",
        "artifact-room",
        "slice-and-integrate",
        "peer-deliberation",
        "blind-arbitration",
        "gated-handoff",
        "proof-split",
    ]:
        raise ValueError("planned family order changed")

    taxonomy = json.loads(
        (SOURCE_STUDY_ROOT / "taxonomy-review.json").read_text(encoding="utf-8")
    )
    if taxonomy["prompt_count"] != 128:
        raise ValueError("blind taxonomy review does not cover 128 prompts")
    if taxonomy["unanimous_correct"] != 128 or taxonomy["disagreements"]:
        raise ValueError("blind taxonomy gate is not unanimous")
    evidence_root = SOURCE_STUDY_ROOT / "taxonomy-evidence"
    evidence = {
        "blind_packet": evidence_root / "blind-packet.json",
        "answer_key": evidence_root / "answer-key.json",
        "review_a": evidence_root / "review-a.json",
        "review_b": evidence_root / "review-b.json",
        "check_result": evidence_root / "check-result.json",
    }
    if any(_sha256(path) != taxonomy["sha256"][name] for name, path in evidence.items()):
        raise ValueError("blind taxonomy evidence hashes disagree")
    packet = json.loads(evidence["blind_packet"].read_text(encoding="utf-8"))
    answer = json.loads(evidence["answer_key"].read_text(encoding="utf-8"))
    review_a = json.loads(evidence["review_a"].read_text(encoding="utf-8"))
    review_b = json.loads(evidence["review_b"].read_text(encoding="utf-8"))
    result = json.loads(evidence["check_result"].read_text(encoding="utf-8"))
    packet_ids = {row["id"] for row in packet["prompts"]}
    if (
        len(packet_ids) != 128
        or packet_ids != set(answer)
        or answer != review_a
        or answer != review_b
        or result["prompt_count"] != 128
        or result["unanimous_correct"] != 128
        or not result["passed"]
        or result["disagreements"]
    ):
        raise ValueError("blind taxonomy evidence does not reproduce the public result")

    status = (PREDECESSOR_STUDY_ROOT / "EXECUTION-STATUS.md").read_text(
        encoding="utf-8"
    )
    required_status_phrases = (
        "invalid and excluded",
        "35 harness failures",
        "26 pre-session transport failures",
        "9 per-trial timeouts",
        "No confirmatory aggregate",
    )
    if any(phrase not in status for phrase in required_status_phrases):
        raise ValueError("v2 execution disposition is incomplete")

    analysis = lock.get("analysis") or {}
    if (
        analysis.get("primary_estimand") != "end_to_end_assignment_effect_operational_itt"
        or analysis.get("missingness_sensitivity")
        != "missing_iff_zero_missing_if_one_both_truth_values"
        or analysis.get("complete_case_role") != "descriptive_non_gating"
        or analysis.get("pooled_missingness_gate") != 0.05
        or analysis.get("per_family_missingness_gate") is not None
        or analysis.get("posterior_prior") != "beta_0.5_0.5_per_cell"
        or analysis.get("posterior_initial_draws") != 200000
        or analysis.get("posterior_max_draws") != 1600000
        or analysis.get("posterior_seeds") != [20260717, 20260718]
        or analysis.get("false_superiority_probability") != 0.975
        or analysis.get("true_noninferiority_margin") != -0.1
        or analysis.get("true_noninferiority_probability") != 0.975
        or analysis.get("strict_necessary_use_minimum") != 0.8
        or analysis.get("strict_avoided_unnecessary_use_minimum") != 0.8
        or analysis.get("positive_family_effects_minimum") != 6
    ):
        raise ValueError("confirmatory-v3 analysis contract changed")

    print(
        "Confirmatory-v3 protocol lock valid: "
        f"{len(locked_files)} files, 8 families, 1,152 frozen primary trials"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

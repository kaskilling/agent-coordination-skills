#!/usr/bin/env python3
"""Verify that the confirmatory-v1 protocol still matches its freeze lock."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
STUDY_ROOT = ROOT / "studies" / "confirmatory-v1"
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if lock["schema_version"] != "cib-confirmatory-protocol-lock/1":
        raise ValueError("unsupported protocol-lock schema")

    for relative, expected_hash in lock["files"].items():
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"locked file is missing: {relative}")
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"locked file changed: {relative} "
                f"(expected {expected_hash}, found {actual_hash})"
            )

    configs = sorted((STUDY_ROOT / "configs").glob("*.yaml"))
    if tuple(path.stem for path in configs) != EXPECTED_FAMILIES:
        raise ValueError("config inventory differs from the eight frozen families")

    design = lock["design"]
    expected_total = (
        design["families"]
        * design["pairs_per_family"]
        * design["repetitions"]
        * design["arms"]
        * design["truth_values"]
    )
    if expected_total != design["total_trials"] or expected_total != 1152:
        raise ValueError("locked design equation does not equal 1,152 trials")
    if design["trials_per_family"] != 144:
        raise ValueError("locked family trial count is not 144")
    if len(set(design["family_seeds"].values())) != len(EXPECTED_FAMILIES):
        raise ValueError("family execution seeds are not distinct")
    requirements = (STUDY_ROOT / "requirements.txt").read_text(encoding="utf-8")
    if requirements.splitlines() != [
        "NumPy==2.4.1",
        "PyYAML==6.0.2",
        "skills-ref==0.1.1",
    ]:
        raise ValueError("confirmatory analysis dependencies changed")

    for config_path in configs:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        cases = config["cases"]
        execution = config["execution"]
        if len(cases["required"]) != 8 or len(cases["unnecessary"]) != 8:
            raise ValueError(f"{config_path.name} does not contain 8 matched pairs")
        if execution["repetitions"] != 3:
            raise ValueError(f"{config_path.name} repetitions changed")
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
            or execution["jobs"] != 8
        ):
            raise ValueError(f"{config_path.name} execution settings changed")
        if execution["trial_timeout_seconds"] != 300:
            raise ValueError(f"{config_path.name} trial timeout changed")
        if execution["study_timeout_seconds"] != 5400:
            raise ValueError(f"{config_path.name} study timeout changed")

    taxonomy = json.loads(
        (STUDY_ROOT / "taxonomy-review.json").read_text(encoding="utf-8")
    )
    if taxonomy["prompt_count"] != 128:
        raise ValueError("blind taxonomy review does not cover 128 prompts")
    if taxonomy["unanimous_correct"] != 128 or taxonomy["disagreements"]:
        raise ValueError("blind taxonomy gate is not unanimous")
    evidence_root = STUDY_ROOT / "taxonomy-evidence"
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

    print(
        "Confirmatory protocol lock valid: "
        f"{len(lock['files'])} files, 8 families, 1,152 frozen trials"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

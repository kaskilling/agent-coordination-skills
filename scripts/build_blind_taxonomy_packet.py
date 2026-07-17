#!/usr/bin/env python3
"""Build an opaque prompt-classification packet for independent reviewers."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies" / "confirmatory-v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, required=True)
    args = parser.parse_args()
    if args.packet.exists() or args.answer_key.exists():
        parser.error("refusing to replace an existing review artifact")
    contract = json.loads((STUDY / "taxonomy-contract.json").read_text())
    prompts = []
    answers = {}
    for config_path in sorted((STUDY / "configs").glob("*.yaml")):
        family = config_path.stem
        config = yaml.safe_load(config_path.read_text())
        required = config["cases"]["required"]
        unnecessary = config["cases"]["unnecessary"]
        expected_negatives = contract["negative_order"][family]
        if len(required) != 8 or len(unnecessary) != 8:
            raise ValueError(f"{family} does not contain eight matched pairs")
        for index, text in enumerate(required):
            opaque_id = hashlib.sha256(f"required:{family}:{index}".encode()).hexdigest()[:16]
            prompts.append({"id": opaque_id, "text": text})
            answers[opaque_id] = family
        for index, text in enumerate(unnecessary):
            opaque_id = hashlib.sha256(f"unnecessary:{family}:{index}".encode()).hexdigest()[:16]
            prompts.append({"id": opaque_id, "text": text})
            answers[opaque_id] = expected_negatives[index]
    random.Random(20260717).shuffle(prompts)
    args.packet.write_text(
        json.dumps(
            {
                "schema_version": "cib-blind-taxonomy-packet/1",
                "classes": contract["classes"],
                "prompts": prompts,
            },
            indent=2,
        )
        + "\n"
    )
    args.answer_key.write_text(json.dumps(answers, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

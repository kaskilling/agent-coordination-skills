#!/usr/bin/env python3
"""Check two independent blind classifications against the frozen answer key."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--review-a", type=Path, required=True)
    parser.add_argument("--review-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to replace review result")
    expected = json.loads(args.answer_key.read_text())
    reviews = [json.loads(args.review_a.read_text()), json.loads(args.review_b.read_text())]
    if any(set(review) != set(expected) for review in reviews):
        raise ValueError("review inventory differs from blind packet")
    disagreements = []
    for opaque_id, expected_class in expected.items():
        left = reviews[0][opaque_id]
        right = reviews[1][opaque_id]
        if left != right or left != expected_class:
            disagreements.append(
                {
                    "id": opaque_id,
                    "expected": expected_class,
                    "review_a": left,
                    "review_b": right,
                }
            )
    result = {
        "schema_version": "cib-blind-taxonomy-review/1",
        "prompt_count": len(expected),
        "unanimous_correct": len(expected) - len(disagreements),
        "passed": not disagreements,
        "disagreements": disagreements,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

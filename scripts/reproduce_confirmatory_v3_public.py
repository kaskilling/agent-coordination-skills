#!/usr/bin/env python3
"""Recompute confirmatory-v3 analysis from public sufficient statistics."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STUDY_ROOT = ROOT / "studies" / "confirmatory-v3"
ANALYSIS_PATH = ROOT / "scripts" / "summarize_cib_confirmatory_v3.py"
NUMERIC_TOLERANCE = 1e-12


def _load_analysis():
    spec = importlib.util.spec_from_file_location("confirmatory_v3_analysis", ANALYSIS_PATH)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load frozen confirmatory-v3 analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cells(value: dict[str, Any], analysis) -> dict[tuple[str, int, str, bool], dict[str, int]]:
    if value.get("schema_version") != "cib-confirmatory-sufficient-statistics/1":
        raise ValueError("unsupported sufficient-statistics schema")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 384:
        raise ValueError("expected 384 frozen pair-cell rows")
    cells = {}
    for row in rows:
        key = (
            str(row["family"]),
            int(row["pair_index"]),
            str(row["arm"]),
            bool(row["condition_true"]),
        )
        if key in cells:
            raise ValueError(f"duplicate sufficient-statistics cell: {key}")
        cells[key] = {
            "successes": int(row["successes"]),
            "n": int(row["n"]),
            "missing": int(row["missing"]),
        }
    analysis._validate_cells(cells)
    return cells


def _assert_equivalent(left: Any, right: Any, path: str = "$") -> None:
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            raise ValueError(f"public reproduction keys differ at {path}")
        for key in left:
            _assert_equivalent(left[key], right[key], f"{path}.{key}")
        return
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            raise ValueError(f"public reproduction lengths differ at {path}")
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            _assert_equivalent(left_item, right_item, f"{path}[{index}]")
        return
    if isinstance(left, bool) or isinstance(right, bool):
        if type(left) is not type(right) or left != right:
            raise ValueError(f"public reproduction values differ at {path}")
        return
    if (
        isinstance(left, (int, float))
        and not isinstance(left, bool)
        and isinstance(right, (int, float))
        and not isinstance(right, bool)
    ):
        if not math.isclose(
            float(left),
            float(right),
            rel_tol=NUMERIC_TOLERANCE,
            abs_tol=NUMERIC_TOLERANCE,
        ):
            raise ValueError(f"public reproduction values differ at {path}")
        return
    if left != right:
        raise ValueError(f"public reproduction values differ at {path}")


def main() -> int:
    analysis = _load_analysis()
    sufficient = json.loads(
        (STUDY_ROOT / "cell-sufficient-statistics.json").read_text(encoding="utf-8")
    )
    published = json.loads(
        (STUDY_ROOT / "aggregate.json").read_text(encoding="utf-8")
    )
    cells = _cells(sufficient, analysis)
    family_rows = [
        {
            "family": family,
            "integrity_passed": True,
            "cache_seed_integrity": True,
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
    reproduced = analysis.analyze(cells, family_rows)
    published_core = {
        key: value for key, value in published.items() if key != "provenance"
    }
    _assert_equivalent(reproduced, published_core)
    print(
        json.dumps(
            {
                "reproduced": True,
                "confirmed": reproduced["confirmed"],
                "rows": len(sufficient["rows"]),
                "draws": reproduced["posterior"]["draws"],
                "numeric_tolerance": NUMERIC_TOLERANCE,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

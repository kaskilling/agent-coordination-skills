#!/usr/bin/env python3
"""Recompute confirmatory-v3 analysis from public sufficient statistics."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STUDY_ROOT = ROOT / "studies" / "confirmatory-v3"
ANALYSIS_PATH = ROOT / "scripts" / "summarize_cib_confirmatory_v3.py"


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
    if reproduced != published_core:
        raise ValueError("public sufficient statistics do not reproduce aggregate")
    print(
        json.dumps(
            {
                "reproduced": True,
                "confirmed": reproduced["confirmed"],
                "rows": len(sufficient["rows"]),
                "draws": reproduced["posterior"]["draws"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

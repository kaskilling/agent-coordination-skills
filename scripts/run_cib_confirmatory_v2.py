#!/usr/bin/env python3
"""Run the frozen confirmatory-v2 suite without reusing outputs."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = ROOT / "studies" / "confirmatory-v1" / "configs"
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
CIB_RELEASE_COMMIT = "eebdbfc84206c594db2d61cf883325e2d8e1b07d"
STUDY_FREEZE_TAG = "confirmatory-v2-preregistered"
RUN_ORDER = list(EXPECTED_FAMILIES)
random.Random(20260717).shuffle(RUN_ORDER)
REQUIRED_ARTIFACTS = (
    "run-manifest.jsonl",
    "promptfoo/derived/summary.json",
    "promptfoo/derived/audit.json",
    "study-result.json",
    "check-metadata.json",
    "report/report.json",
    "check-result.json",
)
EXPECTED_CIB_VERSION = "cib 0.5.1"
EXPECTED_PROMPTFOO_VERSION = "0.121.19"
EXPECTED_CODEX_SDK_VERSION = "0.144.5"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _output(command: list[str], *, cwd: Path) -> str:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _write_index(path: Path, index: dict[str, object]) -> None:
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _runtime_versions(cib_root: Path) -> dict[str, object]:
    cib_binary = cib_root / ".venv" / "bin" / "cib"
    cib_python = cib_root / ".venv" / "bin" / "python"
    promptfoo_binary = cib_root / "node_modules" / ".bin" / "promptfoo"
    sdk_package = cib_root / "node_modules" / "@openai" / "codex-sdk" / "package.json"
    promptfoo_package = cib_root / "node_modules" / "promptfoo" / "package.json"
    required = (cib_binary, cib_python, promptfoo_binary, sdk_package, promptfoo_package)
    if not all(path.is_file() for path in required):
        raise ValueError("CIB runtime is incomplete; run uv sync --frozen and npm ci")
    cib_version = _output([str(cib_binary), "--version"], cwd=cib_root)
    promptfoo_cli_version = _output(
        [str(promptfoo_binary), "--version"], cwd=cib_root
    ).splitlines()[-1]
    sdk_version = json.loads(sdk_package.read_text(encoding="utf-8"))["version"]
    promptfoo_version = json.loads(
        promptfoo_package.read_text(encoding="utf-8")
    )["version"]
    if cib_version != EXPECTED_CIB_VERSION:
        raise ValueError(f"expected {EXPECTED_CIB_VERSION}, found {cib_version}")
    if (
        promptfoo_version != EXPECTED_PROMPTFOO_VERSION
        or promptfoo_cli_version != EXPECTED_PROMPTFOO_VERSION
    ):
        raise ValueError("installed Promptfoo differs from frozen version")
    if sdk_version != EXPECTED_CODEX_SDK_VERSION:
        raise ValueError("installed Codex SDK differs from frozen version")
    cib_origin = Path(
        _output(
            [str(cib_python), "-c", "import cib; print(cib.__file__)"],
            cwd=cib_root,
        )
    ).resolve()
    expected_origin = (cib_root / "src" / "cib" / "__init__.py").resolve()
    if cib_origin != expected_origin:
        raise ValueError("CIB virtual environment imports a different checkout")
    return {
        "cib": cib_version.removeprefix("cib "),
        "promptfoo": promptfoo_version,
        "codex_sdk": sdk_version,
        "node": _output(["node", "--version"], cwd=cib_root),
        "npm": _output(["npm", "--version"], cwd=cib_root),
        "cib_python": _output(
            [str(cib_python), "-c", "import platform; print(platform.python_version())"],
            cwd=cib_root,
        ),
        "lock_sha256": {
            "package-lock.json": _sha256(cib_root / "package-lock.json"),
            "uv.lock": _sha256(cib_root / "uv.lock"),
        },
    }


def _run_family(
    family: str,
    *,
    cib_root: Path,
    output_root: Path,
    auth: Path,
) -> dict[str, object]:
    config = CONFIG_ROOT / f"{family}.yaml"
    output = output_root / family
    command = [
        str(cib_root / ".venv" / "bin" / "cib"),
        "check",
        str(config),
        "--output-dir",
        str(output),
        "--auth",
        str(auth),
    ]
    completed = subprocess.run(
        command,
        cwd=cib_root,
        capture_output=True,
        text=True,
        check=False,
    )
    (output_root / f"{family}.stdout.log").write_text(
        completed.stdout, encoding="utf-8"
    )
    (output_root / f"{family}.stderr.log").write_text(
        completed.stderr, encoding="utf-8"
    )
    result_path = output / "check-result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else None
    missing = [
        relative for relative in REQUIRED_ARTIFACTS if not (output / relative).is_file()
    ]
    if missing:
        raise FileNotFoundError(f"{family} lacks required CIB artifacts: {missing}")
    artifacts = {
        relative: _sha256(output / relative)
        for relative in REQUIRED_ARTIFACTS
    }
    return {
        "family": family,
        "config_sha256": _sha256(config),
        "exit_code": completed.returncode,
        "verdict": result.get("verdict") if isinstance(result, dict) else "missing",
        "artifact_sha256": artifacts,
        "report_json": (
            f"{family}/{result['report_json']}" if isinstance(result, dict) else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cib-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--parallel-studies", type=int, default=2)
    parser.add_argument(
        "--auth", type=Path, default=Path.home() / ".codex" / "auth.json"
    )
    args = parser.parse_args()
    cib_root = args.cib_root.resolve()
    output_root = args.output_root.resolve()
    auth = args.auth.resolve()
    if output_root.exists():
        parser.error(f"refusing to reuse output directory: {output_root}")
    if args.parallel_studies != 2:
        parser.error("confirmatory-v2 requires exactly 2 parallel studies")
    if not (cib_root / ".venv" / "bin" / "cib").is_file():
        parser.error("CIB virtual environment is missing; run uv sync in --cib-root")
    cib_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cib_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if cib_commit != CIB_RELEASE_COMMIT:
        parser.error(
            f"CIB checkout must be the frozen v0.5.1 commit {CIB_RELEASE_COMMIT}"
        )
    cib_status = _output(["git", "status", "--porcelain"], cwd=cib_root)
    if cib_status:
        parser.error("CIB checkout must be clean before confirmatory execution")
    try:
        runtime_versions = _runtime_versions(cib_root)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        parser.error(f"CIB runtime preflight failed: {error}")
    if not auth.is_file():
        parser.error(f"Codex auth file is missing: {auth}")
    protocol_check = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "validate_confirmatory_v2_protocol.py"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if protocol_check.returncode:
        parser.error(
            "confirmatory protocol lock is invalid:\n"
            + (protocol_check.stderr or protocol_check.stdout).strip()
        )
    repository_status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if repository_status:
        parser.error("repository must be clean before confirmatory execution")
    repository_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    try:
        freeze_commit = _output(
            ["git", "rev-parse", f"{STUDY_FREEZE_TAG}^{{commit}}"], cwd=ROOT
        )
    except subprocess.CalledProcessError:
        parser.error(f"study freeze tag is missing: {STUDY_FREEZE_TAG}")
    if repository_commit != freeze_commit:
        parser.error(
            f"repository HEAD must equal the {STUDY_FREEZE_TAG} freeze commit"
        )
    configs = tuple(path.stem for path in sorted(CONFIG_ROOT.glob("*.yaml")))
    if configs != EXPECTED_FAMILIES:
        parser.error("confirmatory config inventory differs from frozen protocol")
    output_root.mkdir(parents=True)
    rows: list[dict[str, object]] = []
    index: dict[str, object] = {
        "schema_version": "cib-confirmatory-run-index/2",
        "protocol": "confirmatory-v2",
        "freeze_tag": STUDY_FREEZE_TAG,
        "parallel_studies": args.parallel_studies,
        "state": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_commit": repository_commit,
        "cib_commit": cib_commit,
        "runtime_versions": runtime_versions,
        "planned_family_order": RUN_ORDER,
        "planned_configs": [
            {
                "family": family,
                "config_sha256": _sha256(CONFIG_ROOT / f"{family}.yaml"),
            }
            for family in RUN_ORDER
        ],
        "families": rows,
    }
    index_path = output_root / "run-index.json"
    _write_index(index_path, index)
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.parallel_studies
    ) as executor:
        futures = {
            executor.submit(
                _run_family,
                family,
                cib_root=cib_root,
                output_root=output_root,
                auth=auth,
            ): family
            for family in RUN_ORDER
        }
        for future in concurrent.futures.as_completed(futures):
            family = futures[future]
            try:
                row = future.result()
            except Exception as error:
                row = {
                    "family": family,
                    "config_sha256": _sha256(CONFIG_ROOT / f"{family}.yaml"),
                    "exit_code": 2,
                    "verdict": "runner_error",
                    "error_type": type(error).__name__,
                    "artifact_sha256": {},
                    "report_json": None,
                }
            rows.append(row)
            rows.sort(key=lambda item: str(item["family"]))
            index["families"] = rows
            _write_index(index_path, index)
            print(json.dumps(row, sort_keys=True), flush=True)
    index["state"] = "complete"
    index["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    _write_index(index_path, index)
    exits = [int(row["exit_code"]) for row in rows]
    return 2 if any(value == 2 for value in exits) else (1 if any(exits) else 0)


if __name__ == "__main__":
    raise SystemExit(main())

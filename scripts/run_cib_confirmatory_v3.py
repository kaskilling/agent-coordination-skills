#!/usr/bin/env python3
"""Run the frozen confirmatory-v3 suite with one excluded cache warmup per family."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = ROOT / "studies" / "confirmatory-v3" / "configs"
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
CIB_RELEASE_COMMIT = "e9e77bfd598319fe0d7049c74943c15f556a61ac"
STUDY_FREEZE_TAG = "confirmatory-v3-preregistered"
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
EXPECTED_CIB_VERSION = "cib 0.5.3"
EXPECTED_PROMPTFOO_VERSION = "0.121.19"
EXPECTED_CODEX_SDK_VERSION = "0.144.5"
CACHE_MIN_VALIDITY_SECONDS = 3300
WARMUP_TIMEOUT_SECONDS = 180
MAX_CACHE_BYTES = 10 * 1024 * 1024
WARMUP_JS = r"""
import { Codex } from "@openai/codex-sdk";
const codex = new Codex();
const thread = codex.startThread({
  workingDirectory: process.env.CIB_WARMUP_WORKDIR,
  model: "gpt-5.6-sol",
  modelReasoningEffort: "medium",
  sandboxMode: "read-only",
  approvalPolicy: "never",
});
const turn = await thread.run(
  "Return only READY. This excluded call bootstraps the frozen runtime cache."
);
if (!turn.finalResponse) throw new Error("warmup returned no final response");
"""


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
    temporary.chmod(0o600)
    temporary.replace(path)


def _write_private_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


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


def _parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("warmup cache timestamp is missing")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("warmup cache timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def _read_private_cache(path: Path) -> bytes:
    source = path.lstat()
    if stat.S_ISLNK(source.st_mode) or not stat.S_ISREG(source.st_mode):
        raise ValueError("warmup cache must be a regular non-symlink file")
    if source.st_size > MAX_CACHE_BYTES:
        raise ValueError("warmup cache exceeds the size limit")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_size > MAX_CACHE_BYTES
            or (opened.st_dev, opened.st_ino) != (source.st_dev, source.st_ino)
        ):
            raise ValueError("warmup cache changed before secure read")
        os.fchmod(descriptor, 0o600)
        chunks: list[bytes] = []
        remaining = MAX_CACHE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) > MAX_CACHE_BYTES:
            raise ValueError("warmup cache exceeds the size limit")
        return data
    finally:
        os.close(descriptor)


def _warm_family_cache(
    family: str,
    *,
    cib_root: Path,
    output_root: Path,
    auth: Path,
) -> tuple[Path, dict[str, object]]:
    bootstrap = output_root / "_bootstrap" / family
    home = bootstrap / "home"
    codex_home = bootstrap / "codex-home"
    fixture = bootstrap / "fixture"
    home.mkdir(parents=True, mode=0o700)
    codex_home.mkdir(mode=0o700)
    fixture.mkdir()
    os.symlink(auth, codex_home / "auth.json")
    subprocess.run(
        ["git", "init", "-q"],
        cwd=fixture,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    environment = os.environ.copy()
    environment.update(
        {
            "HOME": str(home.resolve()),
            "CODEX_HOME": str(codex_home.resolve()),
            "CIB_WARMUP_WORKDIR": str(fixture.resolve()),
        }
    )
    started = time.monotonic()
    completed = subprocess.run(
        ["node", "--input-type=module", "--eval", WARMUP_JS],
        cwd=cib_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=WARMUP_TIMEOUT_SECONDS,
        check=False,
    )
    duration = time.monotonic() - started
    _write_private_text(bootstrap / "warmup.stdout.log", completed.stdout)
    _write_private_text(bootstrap / "warmup.stderr.log", completed.stderr)
    if completed.returncode:
        raise RuntimeError(f"{family} excluded cache warmup failed")
    cache_path = codex_home / "cloud-config-bundle-cache.json"
    try:
        cache_bytes = _read_private_cache(cache_path)
    except (FileNotFoundError, OSError, ValueError) as error:
        raise ValueError(
            f"{family} warmup did not create a safe regular cache"
        ) from error
    cache = json.loads(cache_bytes)
    if not isinstance(cache, dict) or not isinstance(cache.get("signature"), str):
        raise ValueError(f"{family} warmup cache lacks signed format")
    payload = cache.get("signed_payload")
    if not isinstance(payload, dict) or type(payload.get("version")) is not int:
        raise ValueError(f"{family} warmup cache payload is invalid")
    cached_at = _parse_timestamp(payload.get("cached_at"))
    expires_at = _parse_timestamp(payload.get("expires_at"))
    remaining = expires_at.timestamp() - datetime.now(timezone.utc).timestamp()
    if remaining < CACHE_MIN_VALIDITY_SECONDS:
        raise ValueError(f"{family} warmup cache is not fresh enough")
    return cache_path, {
        "excluded_model_calls": 1,
        "duration_seconds": duration,
        "cache_sha256": hashlib.sha256(cache_bytes).hexdigest(),
        "cache_version": payload["version"],
        "cached_at_utc": cached_at.isoformat(),
        "expires_at_utc": expires_at.isoformat(),
        "minimum_remaining_seconds": CACHE_MIN_VALIDITY_SECONDS,
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
    cache_path, warmup = _warm_family_cache(
        family,
        cib_root=cib_root,
        output_root=output_root,
        auth=auth,
    )
    command = [
        str(cib_root / ".venv" / "bin" / "cib"),
        "check",
        str(config),
        "--output-dir",
        str(output),
        "--auth",
        str(auth),
        "--cloud-config-seed",
        str(cache_path),
        "--cloud-config-min-validity-seconds",
        str(CACHE_MIN_VALIDITY_SECONDS),
    ]
    completed = subprocess.run(
        command,
        cwd=cib_root,
        capture_output=True,
        text=True,
        check=False,
    )
    _write_private_text(output_root / f"{family}.stdout.log", completed.stdout)
    _write_private_text(output_root / f"{family}.stderr.log", completed.stderr)
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
    study_result = json.loads((output / "study-result.json").read_text())
    execution = study_result.get("execution") or {}
    seed = execution.get("cloud_config_seed") or {}
    post_run = execution.get("cloud_config_seed_post_run") or {}
    if (
        seed.get("present") is not True
        or seed.get("mode") != "private_per_trial_snapshot"
        or seed.get("sha256") != warmup["cache_sha256"]
        or seed.get("version") != warmup["cache_version"]
        or seed.get("cached_at") != warmup["cached_at_utc"]
        or seed.get("expires_at") != warmup["expires_at_utc"]
        or seed.get("minimum_remaining_seconds") != CACHE_MIN_VALIDITY_SECONDS
        or post_run
        != {"trial_copies": 144, "unchanged": 144, "changed": 0, "missing": 0}
    ):
        raise ValueError(f"{family} cache seed provenance is invalid")
    return {
        "family": family,
        "config_sha256": _sha256(config),
        "exit_code": completed.returncode,
        "verdict": result.get("verdict") if isinstance(result, dict) else "missing",
        "artifact_sha256": artifacts,
        "warmup": warmup,
        "report_json": (
            f"{family}/{result['report_json']}" if isinstance(result, dict) else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cib-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--parallel-studies", type=int, default=1)
    parser.add_argument(
        "--auth", type=Path, default=Path.home() / ".codex" / "auth.json"
    )
    args = parser.parse_args()
    cib_root = args.cib_root.resolve()
    output_root = args.output_root.resolve()
    auth = args.auth.resolve()
    if output_root.exists():
        parser.error(f"refusing to reuse output directory: {output_root}")
    if args.parallel_studies != 1:
        parser.error("confirmatory-v3 requires exactly 1 family study at a time")
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
            f"CIB checkout must be the frozen v0.5.3 commit {CIB_RELEASE_COMMIT}"
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
            str(ROOT / "scripts" / "validate_confirmatory_v3_protocol.py"),
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
    output_root.mkdir(parents=True, mode=0o700)
    output_root.chmod(0o700)
    rows: list[dict[str, object]] = []
    index: dict[str, object] = {
        "schema_version": "cib-confirmatory-run-index/3",
        "protocol": "confirmatory-v3",
        "freeze_tag": STUDY_FREEZE_TAG,
        "parallel_studies": args.parallel_studies,
        "excluded_warmup_calls": len(RUN_ORDER),
        "primary_model_calls": 1152,
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
    for attempt_ordinal, family in enumerate(RUN_ORDER, start=1):
        attempt_started_at_utc = datetime.now(timezone.utc).isoformat()
        try:
            row = _run_family(
                family,
                cib_root=cib_root,
                output_root=output_root,
                auth=auth,
            )
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
        row["attempt_ordinal"] = attempt_ordinal
        row["attempt_started_at_utc"] = attempt_started_at_utc
        row["attempt_finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        rows.append(row)
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

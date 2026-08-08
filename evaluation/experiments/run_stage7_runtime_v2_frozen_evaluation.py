from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

from evaluation.datasets.stage7 import stage7_manifest_sha256
from evaluation.experiments.run_stage7_frozen_evaluation import (
    Stage7EvaluationError,
    Stage7ExecutionTarget,
    run_live_stage7,
)
from scripts.preflight_stage7_runtime_v2 import Stage7PreflightReport

PROTOCOL_PATH = Path("evaluation/configs/stage7_runtime_v2_frozen_evaluation_v1.yaml")
DATASET_DIRECTORY = Path("data/frozen_test/stage7_runtime_v2_v1")
CACHE_PATH = Path("evaluation/reports/generated/stage7_runtime_v2_l3_cache_v1.json")
REPORT_PATH = Path("evaluation/reports/stage7_runtime_v2_frozen_evaluation_v1.json")
RUNTIME_DIRECTORY = Path("configs/runtime/five_role_v2")
PREFLIGHT_PATH = Path("evaluation/reports/stage7_runtime_v2_preflight_v1.json")
AUTHORIZATION_PATH = Path("evaluation/configs/stage7_runtime_v2_execution_authorization_v1.json")

V2_EXECUTION_TARGET = Stage7ExecutionTarget(
    protocol_path=PROTOCOL_PATH,
    dataset_directory=DATASET_DIRECTORY,
    runtime_directory=RUNTIME_DIRECTORY,
    report_id="stage7-five-role-runtime-v2-frozen-evaluation-v1",
    report_scope="gold-frozen-five-role-runtime-v2-final-test",
)


class Stage7RuntimeV2ExecutionAuthorization(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: Literal["1.0.0"]
    authorization_id: Literal["stage7-runtime-v2-provider-execution-v1"]
    authorized_at: datetime
    authorized: Literal[True]
    runtime_configuration_set_id: Literal["five-role-runtime-v2"]
    runtime_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_id: Literal["stage7-five-role-runtime-v2-test-v1"]
    dataset_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    protocol_id: Literal["stage7-five-role-runtime-v2-frozen-evaluation-v1"]
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    maximum_http_request_count: Literal[60]
    persist_raw_provider_response: Literal[False]
    tuning_allowed: Literal[False]
    authorization_statement: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_timestamp(self) -> Stage7RuntimeV2ExecutionAuthorization:
        if self.authorized_at.tzinfo is None or self.authorized_at.utcoffset() is None:
            raise ValueError("authorized_at must include a timezone")
        return self


def verify_stage7_runtime_v2_execution_authorization(repository_root: Path) -> None:
    preflight = Stage7PreflightReport.model_validate_json(
        (repository_root / PREFLIGHT_PATH).read_text(encoding="utf-8")
    )
    authorization = Stage7RuntimeV2ExecutionAuthorization.model_validate_json(
        (repository_root / AUTHORIZATION_PATH).read_text(encoding="utf-8")
    )
    current_runtime_hash = stage7_manifest_sha256(
        repository_root / RUNTIME_DIRECTORY / "runtime_manifest.yaml"
    )
    current_dataset_hash = stage7_manifest_sha256(
        repository_root / DATASET_DIRECTORY / "manifest.json"
    )
    current_protocol_hash = stage7_manifest_sha256(repository_root / PROTOCOL_PATH)
    expected_hashes = (
        preflight.runtime_manifest_sha256,
        preflight.dataset_manifest_sha256,
        preflight.protocol_sha256,
    )
    authorized_hashes = (
        authorization.runtime_manifest_sha256,
        authorization.dataset_manifest_sha256,
        authorization.protocol_sha256,
    )
    current_hashes = (
        current_runtime_hash,
        current_dataset_hash,
        current_protocol_hash,
    )
    if not preflight.passed or preflight.errors:
        raise Stage7EvaluationError("Runtime v2 preflight is not passing")
    if expected_hashes != authorized_hashes or expected_hashes != current_hashes:
        raise Stage7EvaluationError("Runtime v2 frozen artifact hash changed after authorization")
    if (
        preflight.provider_requests_made
        or preflight.api_key_loaded
        or authorization.maximum_http_request_count != 60
        or authorization.persist_raw_provider_response
        or authorization.tuning_allowed
    ):
        raise Stage7EvaluationError("Runtime v2 execution authorization policy is invalid")


async def run_live_stage7_runtime_v2(
    repository_root: Path,
    generated_at: datetime,
    maximum_new_requests: int | None = None,
    cache_path: Path = CACHE_PATH,
    report_path: Path = REPORT_PATH,
) -> Path | None:
    verify_stage7_runtime_v2_execution_authorization(repository_root)
    return await run_live_stage7(
        repository_root,
        generated_at,
        maximum_new_requests=maximum_new_requests,
        cache_path=cache_path,
        report_path=report_path,
        target=V2_EXECUTION_TARGET,
    )


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


async def _main_async(arguments: argparse.Namespace) -> None:
    repository_root = Path(__file__).resolve().parents[2]
    path = await run_live_stage7_runtime_v2(
        repository_root,
        _timestamp(cast(str, arguments.generated_at)),
        maximum_new_requests=cast(int | None, arguments.maximum_new_requests),
        cache_path=Path(cast(str, arguments.cache)),
        report_path=Path(cast(str, arguments.report)),
    )
    if path is None:
        print(json.dumps({"status": "incomplete", "cache": cast(str, arguments.cache)}))
        return
    print(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--maximum-new-requests", type=int)
    parser.add_argument("--cache", default=CACHE_PATH.as_posix())
    parser.add_argument("--report", default=REPORT_PATH.as_posix())
    arguments = parser.parse_args()
    asyncio.run(_main_async(arguments))


if __name__ == "__main__":
    main()

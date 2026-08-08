from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from backend.app.contracts import CVProfile, ClassificationRequest
from backend.app.infrastructure.config import RepositoryConfigurationLoader

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "data" / "runtime_v2" / "reviewed" / "development_v1"
CONFIGURATION_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v2"
DEFAULT_OUTPUT_DIRECTORY = REPOSITORY_ROOT / "frontend" / "src" / "data" / "demo-cases"


@dataclass(frozen=True, slots=True)
class DemoCaseSpecification:
    demo_case_id: str
    pair_id: str


DEMO_CASE_SPECIFICATIONS: tuple[DemoCaseSpecification, ...] = (
    DemoCaseSpecification("stage8-data-analyst-strong", "v2d-pair-da-01"),
    DemoCaseSpecification("stage8-python-backend-missing", "v2d-pair-be-05"),
    DemoCaseSpecification("stage8-frontend-moderate", "v2d-pair-fe-04"),
    DemoCaseSpecification("stage8-qa-explicit-failure", "v2d-pair-qa-07"),
    DemoCaseSpecification("stage8-data-engineer-conflict", "v2d-pair-de-12"),
)


def _read_json_lines(path: Path) -> tuple[dict[str, object], ...]:
    return tuple(
        cast(dict[str, object], json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def build_demo_case_payloads() -> tuple[dict[str, object], ...]:
    pairs = {
        cast(str, item["pair_id"]): item
        for item in _read_json_lines(SOURCE_DIRECTORY / "pairs.jsonl")
    }
    cv_profiles = {
        cast(str, item["cv_profile_id"]): CVProfile.model_validate(item)
        for item in _read_json_lines(SOURCE_DIRECTORY / "cv_profiles.jsonl")
    }
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT, CONFIGURATION_DIRECTORY)
    payloads: list[dict[str, object]] = []
    for specification in DEMO_CASE_SPECIFICATIONS:
        pair = pairs[specification.pair_id]
        cv_profile_id = cast(str, pair["cv_profile_id"])
        job_profile_id = cast(str, pair["job_profile_id"])
        cv_profile = cv_profiles[cv_profile_id]
        loaded = loader.load_for_job(job_profile_id)
        request = ClassificationRequest(
            request_id=f"demo-request-{specification.demo_case_id.removeprefix('stage8-')}",
            cv_profile=cv_profile,
            job_profile=loaded.job_profile,
            rubric=loaded.rubric,
            configuration=loaded.classification_config,
        )
        payloads.append(
            {
                "schema_version": "1.0.0",
                "demo_case_id": specification.demo_case_id,
                "role": cast(str, pair["role"]),
                "scenario": cast(str, pair["scenario"]),
                "request": request.model_dump(mode="json"),
            }
        )
    return tuple(payloads)


def generate_stage8_demo_data(
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    output_directory.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    for payload in build_demo_case_payloads():
        output_path = output_directory / f"{payload['demo_case_id']}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output_paths.append(output_path)
    return tuple(output_paths)


def main() -> None:
    generated = generate_stage8_demo_data()
    print(f"Generated {len(generated)} Stage 8 demo cases.")


if __name__ == "__main__":
    main()

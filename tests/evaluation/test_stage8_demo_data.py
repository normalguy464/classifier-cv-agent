from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from backend.app.contracts import ClassificationRequest
from scripts.generate_stage8_demo_data import (
    DEFAULT_OUTPUT_DIRECTORY,
    DEMO_CASE_SPECIFICATIONS,
    generate_stage8_demo_data,
)

PROHIBITED_ANNOTATION_KEYS = {
    "criterion_assessments",
    "critical_requirement_assessments",
    "draft_label",
    "final_label",
    "review",
    "review_reasons",
    "total_score",
}


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        record = cast(dict[str, object], value)
        return set(record).union(*(_all_keys(item) for item in record.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in cast(list[object], value)), set())
    return set()


def test_stage8_demo_data_is_reproducible_and_excludes_annotation_leakage(
    tmp_path: Path,
) -> None:
    generated = generate_stage8_demo_data(tmp_path)

    assert len(generated) == len(DEMO_CASE_SPECIFICATIONS) == 5
    assert {path.name for path in generated} == {
        f"{item.demo_case_id}.json" for item in DEMO_CASE_SPECIFICATIONS
    }
    roles: set[str] = set()
    for generated_path in generated:
        payload = cast(
            dict[str, object],
            json.loads(generated_path.read_text(encoding="utf-8")),
        )
        request = ClassificationRequest.model_validate(payload["request"])
        roles.add(cast(str, payload["role"]))
        assert payload["schema_version"] == "1.0.0"
        assert request.configuration.configuration_version == "3.0.0"
        assert not PROHIBITED_ANNOTATION_KEYS.intersection(_all_keys(payload["request"]))
        committed_path = DEFAULT_OUTPUT_DIRECTORY / generated_path.name
        assert committed_path.read_bytes() == generated_path.read_bytes()

    assert roles == {
        "data_analyst",
        "python_backend",
        "frontend",
        "qa_engineer",
        "data_engineer",
    }

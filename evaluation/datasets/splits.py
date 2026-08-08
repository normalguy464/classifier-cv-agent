from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

from evaluation.datasets.stage4 import ReviewedStage4Example, load_reviewed_stage4

SPLIT_MANIFEST_PATH = Path("data/splits/stage6_split_manifest_v1.json")


def _json_object(path: Path) -> dict[str, object]:
    value = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError("Stage 6 split manifest must be a JSON object")
    return cast(dict[str, object], value)


def _mapping(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return cast(dict[str, object], value)


def _texts(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    values = cast(list[object], value)
    if any(not isinstance(item, str) or not item for item in values):
        raise ValueError(f"{field_name} must contain text identifiers")
    identifiers = cast(tuple[str, ...], tuple(values))
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"{field_name} must contain unique identifiers")
    return identifiers


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _validated_partitions(
    repository_root: Path,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    manifest = _json_object(repository_root / SPLIT_MANIFEST_PATH)
    if manifest.get("schema_version") != "1.0.0":
        raise ValueError("unsupported Stage 6 split manifest schema")
    source = _mapping(manifest.get("source"), "source")
    validation = _mapping(manifest.get("validation"), "validation")
    frozen_test = _mapping(manifest.get("frozen_test"), "frozen_test")
    cv_path_value = source.get("cv_file")
    annotation_path_value = source.get("annotation_file")
    if not isinstance(cv_path_value, str) or not isinstance(annotation_path_value, str):
        raise ValueError("split source paths must be text")
    if source.get("cv_sha256") != _sha256(repository_root / cv_path_value):
        raise ValueError("reviewed CV artifact changed after the Stage 6 split")
    if source.get("annotation_sha256") != _sha256(repository_root / annotation_path_value):
        raise ValueError("reviewed annotation artifact changed after the Stage 6 split")
    if validation.get("tuning_allowed") is not True:
        raise ValueError("Stage 6 validation partition must allow tuning")
    if (
        frozen_test.get("tuning_allowed") is not False
        or frozen_test.get("evaluation_allowed_from_stage") != 7
        or frozen_test.get("classifier_results_generated") is not False
    ):
        raise ValueError("frozen-test policy must prevent Stage 6 evaluation")
    validation_ids = _texts(
        validation.get("cv_profile_ids"),
        "validation cv_profile_ids",
    )
    frozen_ids = _texts(
        frozen_test.get("cv_profile_ids"),
        "frozen-test cv_profile_ids",
    )
    if len(validation_ids) != 20 or len(frozen_ids) != 10:
        raise ValueError("Stage 6 partitions must contain 20 and 10 cases")
    if set(validation_ids).intersection(frozen_ids):
        raise ValueError("validation and frozen-test partitions must not overlap")
    return validation_ids, frozen_ids


def load_stage6_validation(
    repository_root: Path,
) -> tuple[ReviewedStage4Example, ...]:
    validation_ids, frozen_ids = _validated_partitions(repository_root)
    examples = load_reviewed_stage4(repository_root)
    examples_by_id = {example.cv_profile.cv_profile_id: example for example in examples}
    if set(validation_ids).union(frozen_ids) != set(examples_by_id):
        raise ValueError("Stage 6 partitions must cover all reviewed examples")
    return tuple(examples_by_id[cv_profile_id] for cv_profile_id in validation_ids)

from __future__ import annotations

import argparse
import importlib
import json
from collections import defaultdict
from datetime import datetime
from math import sqrt
from pathlib import Path
from statistics import mean, pstdev
from typing import Literal, Protocol, Self, cast

import numpy as np
from numpy.typing import NDArray
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import ClassificationDecision
from evaluation.datasets.runtime_v2 import RuntimeV2SplitManifest, file_sha256
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation
from evaluation.experiments.run_runtime_v2_offline_l1_l2 import (
    evaluate_quality_checks,
    load_offline_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_l2_calibration_v1.yaml")
REPORT_PATH = Path("evaluation/reports/runtime_v2_l2_calibration_v1.json")


class Regressor(Protocol):
    def fit(self, features: NDArray[np.float64], targets: NDArray[np.float64]) -> Regressor: ...

    def predict(self, features: NDArray[np.float64]) -> NDArray[np.float64]: ...


class ExtraTreesFactory(Protocol):
    def __call__(
        self,
        *,
        n_estimators: int,
        min_samples_leaf: int,
        max_features: float,
        random_state: int,
        n_jobs: int,
    ) -> Regressor: ...


class JoblibModule(Protocol):
    def dump(self, value: object, filename: Path) -> object: ...


extra_trees_factory = cast(
    ExtraTreesFactory,
    getattr(importlib.import_module("sklearn.ensemble"), "ExtraTreesRegressor"),
)
joblib_module = cast(JoblibModule, importlib.import_module("joblib"))


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class CalibrationCandidate(FrozenModel):
    candidate_id: str = Field(min_length=1)
    minimum_samples_per_leaf: int = Field(ge=2, le=50)


class CalibrationConfiguration(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal["runtime-v2-l2-calibration-v1"]
    experiment_version: Literal["1.0.0"]
    status: Literal["approved_for_offline_tuning"]
    base_tuning_report_path: Path
    semantic_candidate_id: str = Field(min_length=1)
    reviewed_dataset_directory: Path
    split_manifest_path: Path
    stage7_v1_test_allowed: Literal[False]
    llm_provider_calls_allowed: Literal[False]
    training_partition: Literal["development"]
    selection_partition: Literal["validation"]
    feature_schema: tuple[str, ...]
    model_family: Literal["sklearn-extra-trees-regressor"]
    n_estimators: int = Field(ge=10, le=1000)
    random_state: int = Field(ge=0)
    candidates: tuple[CalibrationCandidate, ...]
    selected_candidate_id: str = Field(min_length=1)
    model_output_path: Path
    selection_rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        paths = (
            self.base_tuning_report_path,
            self.reviewed_dataset_directory,
            self.split_manifest_path,
            self.model_output_path,
        )
        if any(path.is_absolute() or ".." in path.parts for path in paths):
            raise ValueError("calibration paths must be repository-relative")
        if self.model_output_path.suffix != ".joblib":
            raise ValueError("calibration model output must use .joblib")
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        if not candidate_ids or len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("calibration candidates must have unique identifiers")
        if self.selected_candidate_id not in candidate_ids:
            raise ValueError("selected calibration candidate must be configured")
        if len(self.feature_schema) != len(set(self.feature_schema)):
            raise ValueError("calibration feature schema must contain unique values")
        return self


def load_calibration_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> CalibrationConfiguration:
    payload = yaml.safe_load((repository_root / configuration_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("L2 calibration configuration must be a mapping")
    return CalibrationConfiguration.model_validate(cast(dict[str, object], payload))


def _timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return timestamp


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    left_centered = left - left.mean()
    right_centered = right - right.mean()
    denominator = sqrt(float(np.square(left_centered).sum() * np.square(right_centered).sum()))
    if denominator == 0:
        return 0.0
    return float(np.multiply(left_centered, right_centered).sum() / denominator)


def _load_inputs(
    repository_root: Path,
    configuration: CalibrationConfiguration,
) -> tuple[
    dict[str, object],
    dict[str, SyntheticPairAnnotation],
    RuntimeV2SplitManifest,
]:
    base_report = cast(
        dict[str, object],
        json.loads(
            (repository_root / configuration.base_tuning_report_path).read_text(encoding="utf-8")
        ),
    )
    if base_report.get("llm_provider_calls_made") is not False:
        raise ValueError("calibration source must not contain LLM provider calls")
    if base_report.get("stage7_v1_test_accessed") is not False:
        raise ValueError("calibration source must not access the Stage 7 v1 test")
    reviewed_directory = repository_root / configuration.reviewed_dataset_directory
    pairs = {
        item.pair_id: item
        for item in (
            SyntheticPairAnnotation.model_validate_json(line)
            for line in (reviewed_directory / "pairs.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    split = RuntimeV2SplitManifest.model_validate_json(
        (repository_root / configuration.split_manifest_path).read_text(encoding="utf-8")
    )
    traceability = cast(dict[str, object], base_report["traceability"])
    if traceability["split_manifest_sha256"] != file_sha256(
        repository_root / configuration.split_manifest_path
    ):
        raise ValueError("calibration source split hash does not match")
    return base_report, pairs, split


def _semantic_result(
    base_report: dict[str, object],
    candidate_id: str,
) -> dict[str, object]:
    results = cast(list[dict[str, object]], base_report["candidate_results"])
    for result in results:
        candidate = cast(dict[str, object], result["candidate"])
        if candidate["candidate_id"] == candidate_id:
            return result
    raise ValueError("configured semantic candidate is absent from the tuning report")


def _feature_rows(
    cases: list[dict[str, object]],
    roles: tuple[str, ...],
    pairs: dict[str, SyntheticPairAnnotation],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    tuple[str, ...],
    tuple[ClassificationDecision, ...],
]:
    features: list[list[float]] = []
    targets: list[list[float]] = []
    pair_ids: list[str] = []
    labels: list[ClassificationDecision] = []
    for case in cases:
        pair_id = cast(str, case["pair_id"])
        role = cast(str, case["role"])
        semantic_scores = cast(list[float], case["l2_criterion_scores"])
        pair = pairs[pair_id]
        features.append([*map(float, semantic_scores), *(float(role == item) for item in roles)])
        targets.append([float(item.awarded_points) for item in pair.criterion_assessments])
        pair_ids.append(pair_id)
        labels.append(cast(ClassificationDecision, pair.review.final_label))
    return np.asarray(features), np.asarray(targets), tuple(pair_ids), tuple(labels)


def _metrics(
    predictions: np.ndarray,
    targets: np.ndarray,
    labels: tuple[ClassificationDecision, ...],
) -> dict[str, object]:
    totals = predictions.sum(axis=1)
    human_totals = targets.sum(axis=1)
    label_scores: defaultdict[ClassificationDecision, list[float]] = defaultdict(list)
    for label, score in zip(labels, totals, strict=True):
        label_scores[label].append(float(score))
    label_means = {label.value: mean(label_scores[label]) for label in ClassificationDecision}
    return {
        "score_mean": float(totals.mean()),
        "score_standard_deviation": pstdev(map(float, totals)),
        "score_minimum": float(totals.min()),
        "score_maximum": float(totals.max()),
        "score_range": float(np.ptp(totals)),
        "total_score_mae": float(np.abs(human_totals - totals).mean()),
        "criterion_mae": float(np.abs(targets - predictions).mean()),
        "score_correlation": _correlation(human_totals, totals),
        "label_score_means": label_means,
        "pass_over_waitlist_margin": (
            label_means[ClassificationDecision.PASS.value]
            - label_means[ClassificationDecision.WAITLIST.value]
        ),
        "waitlist_over_reject_margin": (
            label_means[ClassificationDecision.WAITLIST.value]
            - label_means[ClassificationDecision.REJECT.value]
        ),
    }


def _bounded_predictions(
    model: Regressor,
    features: NDArray[np.float64],
) -> NDArray[np.float64]:
    maximums = np.asarray((30.0, 25.0, 20.0, 15.0, 10.0))
    return np.clip(model.predict(features), 0.0, maximums)


def train_l2_calibrator(
    repository_root: Path,
    generated_at: datetime,
    persist_model: bool = True,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    configuration = load_calibration_configuration(repository_root)
    offline = load_offline_configuration(repository_root)
    base_report, pairs, split = _load_inputs(repository_root, configuration)
    semantic = _semantic_result(base_report, configuration.semantic_candidate_id)
    development = cast(dict[str, object], semantic["development"])
    validation = cast(dict[str, object], semantic["validation"])
    development_cases = cast(list[dict[str, object]], development["cases"])
    validation_cases = cast(list[dict[str, object]], validation["cases"])
    if {cast(str, item["pair_id"]) for item in development_cases} != set(
        split.development.pair_ids
    ):
        raise ValueError("calibration development rows do not match the split")
    if {cast(str, item["pair_id"]) for item in validation_cases} != set(split.validation.pair_ids):
        raise ValueError("calibration validation rows do not match the split")
    roles = tuple(sorted({cast(str, item["role"]) for item in development_cases}))
    development_x, development_y, _, development_labels = _feature_rows(
        development_cases, roles, pairs
    )
    validation_x, validation_y, _, validation_labels = _feature_rows(validation_cases, roles, pairs)
    candidate_results: list[dict[str, object]] = []
    selected_model: Regressor | None = None
    for candidate in configuration.candidates:
        model = extra_trees_factory(
            n_estimators=configuration.n_estimators,
            min_samples_leaf=candidate.minimum_samples_per_leaf,
            max_features=1.0,
            random_state=configuration.random_state,
            n_jobs=1,
        )
        model.fit(development_x, development_y)
        development_metrics = _metrics(
            _bounded_predictions(model, development_x), development_y, development_labels
        )
        validation_metrics = _metrics(
            _bounded_predictions(model, validation_x), validation_y, validation_labels
        )
        development_summary: dict[str, object] = {
            "l1": cast(dict[str, object], development["l1"]),
            "l2": development_metrics,
        }
        validation_summary: dict[str, object] = {
            "l1": cast(dict[str, object], validation["l1"]),
            "l2": validation_metrics,
        }
        checks = evaluate_quality_checks(development_summary, validation_summary, offline)
        candidate_results.append(
            {
                "candidate_id": candidate.candidate_id,
                "minimum_samples_per_leaf": candidate.minimum_samples_per_leaf,
                "development": development_metrics,
                "validation": validation_metrics,
                "quality_gate": {"passed": all(checks.values()), "checks": checks},
            }
        )
        if candidate.candidate_id == configuration.selected_candidate_id:
            selected_model = model
    if selected_model is None:
        raise RuntimeError("selected calibration model was not trained")
    selected_result = next(
        item
        for item in candidate_results
        if item["candidate_id"] == configuration.selected_candidate_id
    )
    selected_gate = cast(dict[str, object], selected_result["quality_gate"])
    model_path = repository_root / configuration.model_output_path
    model_sha256: str | None = None
    if persist_model:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib_module.dump(
            {
                "schema_version": "1.0.0",
                "candidate_id": configuration.selected_candidate_id,
                "feature_roles": roles,
                "criterion_maximums": (30.0, 25.0, 20.0, 15.0, 10.0),
                "model": selected_model,
            },
            model_path,
        )
        model_sha256 = file_sha256(model_path)
    return {
        "schema_version": "1.0.0",
        "report_id": "runtime-v2-l2-calibration-v1",
        "generated_at": generated_at.isoformat(),
        "training_partition": "development",
        "selection_partition": "validation",
        "training_pair_count": len(development_cases),
        "selection_pair_count": len(validation_cases),
        "llm_provider_calls_made": False,
        "stage7_v1_test_accessed": False,
        "selected_candidate_id": configuration.selected_candidate_id,
        "selection_passed": bool(selected_gate["passed"]),
        "candidate_results": candidate_results,
        "model_artifact": {
            "path": configuration.model_output_path.as_posix(),
            "sha256": model_sha256,
            "persisted": persist_model,
            "trained_on_validation": False,
        },
        "traceability": {
            "configuration_path": CONFIG_PATH.as_posix(),
            "configuration_sha256": file_sha256(repository_root / CONFIG_PATH),
            "base_tuning_report_path": configuration.base_tuning_report_path.as_posix(),
            "base_tuning_report_sha256": file_sha256(
                repository_root / configuration.base_tuning_report_path
            ),
            "reviewed_dataset_manifest_sha256": file_sha256(
                repository_root / configuration.reviewed_dataset_directory / "manifest.json"
            ),
            "split_manifest_sha256": file_sha256(
                repository_root / configuration.split_manifest_path
            ),
        },
        "limitations": [
            "The calibrator is trained on 50 synthetic Silver pairs and selected on 25 synthetic Silver pairs.",
            "Validation reuses scenario families across roles, so the checkpoint does not prove real-CV generalization.",
            "A newly authored frozen test with different wording is still required before final claims.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--report-path")
    arguments = parser.parse_args()
    report = train_l2_calibrator(REPOSITORY_ROOT, _timestamp(cast(str, arguments.generated_at)))
    report_path = Path(cast(str, arguments.report_path)) if arguments.report_path else REPORT_PATH
    output_path = REPOSITORY_ROOT / report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()

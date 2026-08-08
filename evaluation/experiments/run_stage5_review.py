from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

from backend.app.agents.classifier import (
    ClassifierDependencies,
    LangGraphClassifierWorkflow,
)
from backend.app.agents.classifier.scoring import score_l1
from backend.app.contracts import (
    ClassificationDecision,
    ClassificationRequest,
    ClassificationResult,
    LevelScore,
    ModelMetadata,
)
from backend.app.infrastructure.config import (
    RepositoryConfigurationLoader,
    build_l2_policy,
    build_routing_policy,
)
from backend.app.infrastructure.embeddings import (
    CoreEmbeddingAdapterBridge,
    HashingEmbeddingAdapter,
)
from backend.app.infrastructure.llm import DeterministicCoreL3Provider
from evaluation.datasets import ReviewedStage4Example, load_reviewed_stage4
from evaluation.metrics import calculate_metrics

REPORT_PATH = Path("evaluation/reports/stage5_classifier_review_v1.json")
BOUNDARY_REASON_IDS = {
    "lower-threshold-boundary",
    "upper-threshold-boundary",
}


class Stage5IdentifierGenerator:
    def __init__(self, cv_profile_id: str) -> None:
        self._cv_profile_id = cv_profile_id

    def new_identifier(self, prefix: str) -> str:
        return f"{prefix}-stage5-{self._cv_profile_id}"


class Stage5Clock:
    def __init__(self, timestamp: datetime) -> None:
        self._timestamp = timestamp

    def now(self) -> datetime:
        return self._timestamp


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _score(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _level_score(level: LevelScore) -> dict[str, object]:
    return {
        "value": _score(level.value),
        "status": level.status.value,
        "reason": level.reason,
    }


def _level_disagreement(result: ClassificationResult) -> Decimal | None:
    scores = tuple(
        score
        for score in (
            result.scores.l1.value,
            result.scores.l2.value,
            result.scores.l3.value,
        )
        if score is not None
    )
    if len(scores) < 2:
        return None
    return max(scores) - min(scores)


def _criterion_comparison(
    example: ReviewedStage4Example,
    result: ClassificationResult,
) -> tuple[dict[str, object], ...]:
    human_by_id = {
        assessment.criterion_id: assessment for assessment in example.criterion_assessments
    }
    classifier_by_id = {
        assessment.criterion_id: assessment for assessment in result.criterion_assessments
    }
    if set(human_by_id) != set(classifier_by_id):
        raise ValueError("classifier criterion identifiers must match reviewed criteria")
    return tuple(
        {
            "criterion_id": criterion_id,
            "human_score": _score(human_by_id[criterion_id].awarded_points),
            "classifier_l3_weighted_score": _score(classifier_by_id[criterion_id].score),
            "absolute_difference": _score(
                abs(human_by_id[criterion_id].awarded_points - classifier_by_id[criterion_id].score)
            ),
            "maximum_points": _score(human_by_id[criterion_id].maximum_points),
            "classifier_evidence_status": (classifier_by_id[criterion_id].evidence_status.value),
            "classifier_evidence_ids": list(classifier_by_id[criterion_id].evidence_ids),
        }
        for criterion_id in human_by_id
    )


def _case_flags(
    example: ReviewedStage4Example,
    result: ClassificationResult,
    requirement_status_match: bool,
    disagreement: Decimal | None,
    disagreement_threshold: Decimal,
) -> tuple[str, ...]:
    flags: list[str] = []
    if result.proposed_decision is not example.final_label:
        flags.append("label-mismatch")
    if not requirement_status_match:
        flags.append("requirement-status-mismatch")
    if result.proposed_decision is ClassificationDecision.NEEDS_REVIEW:
        flags.append("needs-review-output")
    if disagreement is not None and disagreement >= disagreement_threshold:
        flags.append("large-level-disagreement")
    if BOUNDARY_REASON_IDS.intersection(result.quality_gate.reasons):
        flags.append("boundary-score")
    if result.scores.l2.value is None or result.scores.l3.value is None:
        flags.append("provider-output-unavailable-or-invalid")
    if not flags:
        flags.append("matched-reference")
    return tuple(flags)


async def _evaluate_example(
    repository_root: Path,
    example: ReviewedStage4Example,
    generated_at: datetime,
) -> dict[str, object]:
    loader = RepositoryConfigurationLoader(repository_root)
    loaded = loader.load_for_job(example.job_profile_id)
    l1_policy = loader.load_l1_policy(example.job_profile_id)
    model_metadata = ModelMetadata(
        embedding_model_identifier="deterministic-hashing-embedding",
        embedding_model_version="1.0.0",
        llm_provider_identifier="deterministic_fake",
        llm_model_identifier="deterministic-evidence-scorer-v1",
        prompt_version=loaded.classification_config.models.prompt_version,
    )
    configuration = loaded.classification_config.model_copy(update={"models": model_metadata})
    hashing_adapter = HashingEmbeddingAdapter(
        dimension=loaded.models_artifact.embedding.dimension,
        model_identifier=model_metadata.embedding_model_identifier,
        model_version=model_metadata.embedding_model_version,
    )
    workflow = LangGraphClassifierWorkflow(
        ClassifierDependencies(
            l1_policy=l1_policy,
            l2_policy=build_l2_policy(loaded),
            routing_policy=build_routing_policy(loaded),
            embedding_adapter=CoreEmbeddingAdapterBridge(
                hashing_adapter,
                query_count=len(loaded.rubric.criteria),
            ),
            l3_provider=DeterministicCoreL3Provider(l1_policy),
            identifier_generator=Stage5IdentifierGenerator(example.cv_profile.cv_profile_id),
            clock=Stage5Clock(generated_at),
        )
    )
    result = await workflow.classify(
        ClassificationRequest(
            request_id=f"request-stage5-{example.cv_profile.cv_profile_id}",
            cv_profile=example.cv_profile,
            job_profile=loaded.job_profile,
            rubric=loaded.rubric,
            configuration=configuration,
        )
    )
    l1_assessment = score_l1(example.cv_profile, loaded.rubric, l1_policy)
    human_requirement_statuses = {
        assessment.requirement_id: assessment.evidence_status.value
        for assessment in example.requirement_assessments
    }
    classifier_requirement_statuses = {
        assessment.requirement_id: assessment.evidence_status.value
        for assessment in l1_assessment.requirement_assessments
    }
    requirement_status_match = human_requirement_statuses == classifier_requirement_statuses
    disagreement = _level_disagreement(result)
    flags = _case_flags(
        example,
        result,
        requirement_status_match,
        disagreement,
        loaded.classification_config.needs_review_policy.disagreement_points,
    )
    return {
        "annotation_id": example.annotation_id,
        "cv_profile_id": example.cv_profile.cv_profile_id,
        "job_profile_id": example.job_profile_id,
        "ground_truth": {
            "final_label": example.final_label.value,
            "reviewer_reference": example.reviewer_reference,
            "reviewed_at": example.reviewed_at.isoformat(),
            "requirement_statuses": human_requirement_statuses,
            "criterion_scores": {
                assessment.criterion_id: _score(assessment.awarded_points)
                for assessment in example.criterion_assessments
            },
            "total_score": _score(example.total_score),
            "overall_rationale": example.overall_rationale,
        },
        "classifier_result": {
            "classification_result_id": result.classification_result_id,
            "proposed_decision": result.proposed_decision.value,
            "level_scores": {
                "l1": _level_score(result.scores.l1),
                "l2": _level_score(result.scores.l2),
                "l3": _level_score(result.scores.l3),
            },
            "final_score": _score(result.scores.final_score),
            "criterion_assessments": [
                {
                    "criterion_id": assessment.criterion_id,
                    "score": _score(assessment.score),
                    "evidence_status": assessment.evidence_status.value,
                    "evidence_ids": list(assessment.evidence_ids),
                    "rationale": assessment.rationale,
                }
                for assessment in result.criterion_assessments
            ],
            "l1_requirement_statuses": classifier_requirement_statuses,
            "confidence": _score(result.confidence),
            "quality_gate": {
                "requires_review": result.quality_gate.requires_review,
                "reasons": list(result.quality_gate.reasons),
            },
            "versions": result.versions.model_dump(mode="json"),
        },
        "comparison": {
            "label_match": result.proposed_decision is example.final_label,
            "requirement_status_match": requirement_status_match,
            "criterion_scores": list(_criterion_comparison(example, result)),
            "maximum_level_disagreement": _score(disagreement),
            "flags": list(flags),
        },
    }


async def run(
    repository_root: Path,
    generated_at: datetime,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    examples = load_reviewed_stage4(repository_root)
    cases = tuple(
        [await _evaluate_example(repository_root, example, generated_at) for example in examples]
    )
    expected = tuple(example.final_label for example in examples)
    predicted = tuple(
        ClassificationDecision(
            cast(dict[str, object], case["classifier_result"])["proposed_decision"]
        )
        for case in cases
    )
    metrics = calculate_metrics(expected, predicted)
    error_case_ids = tuple(
        cast(str, case["cv_profile_id"])
        for case in cases
        if not cast(dict[str, object], case["comparison"])["label_match"]
    )
    needs_review_case_ids = tuple(
        cast(str, case["cv_profile_id"])
        for case in cases
        if cast(dict[str, object], case["classifier_result"])["proposed_decision"]
        == ClassificationDecision.NEEDS_REVIEW.value
    )
    disagreement_case_ids = tuple(
        cast(str, case["cv_profile_id"])
        for case in cases
        if "large-level-disagreement"
        in cast(list[object], cast(dict[str, object], case["comparison"])["flags"])
    )
    representative_case_ids = list(error_case_ids)
    covered_reason_ids = {"large-level-disagreement"}
    for case in cases:
        if not cast(dict[str, object], case["comparison"])["label_match"]:
            continue
        quality_gate = cast(
            dict[str, object],
            cast(dict[str, object], case["classifier_result"])["quality_gate"],
        )
        reasons = cast(list[str], quality_gate["reasons"])
        uncovered_reasons = set(reasons).difference(covered_reason_ids)
        if uncovered_reasons:
            representative_case_ids.append(cast(str, case["cv_profile_id"]))
            covered_reason_ids.update(uncovered_reasons)
    return {
        "report_schema_version": "1.0.0",
        "report_id": "stage5-classifier-review-v1",
        "report_scope": "reviewed-stage4-controlled-diagnostic",
        "is_final_performance": False,
        "generated_at": generated_at.isoformat(),
        "dataset": {
            "dataset_id": "stage4-review-dataset-v1",
            "dataset_version": "1.0.0",
            "annotation_status": "reviewed",
            "sample_count": len(examples),
            "reviewer_references": sorted({example.reviewer_reference for example in examples}),
        },
        "execution_strategy": {
            "l1": "versioned-deterministic-rules",
            "l2": "deterministic-hashing-embedding-1.0.0",
            "l3": "deterministic-offline-evidence-scorer-v1",
            "configured_production_l2_executed": False,
            "live_llm_provider_executed": False,
            "purpose": (
                "Kiểm tra hành vi classifier core và tạo danh sách case review có thể tái lập; "
                "không dùng làm kết quả hiệu năng cuối."
            ),
        },
        "summary": {
            "ground_truth_distribution": dict(
                sorted(Counter(label.value for label in expected).items())
            ),
            "classifier_distribution": dict(
                sorted(Counter(label.value for label in predicted).items())
            ),
            "label_match_count": len(examples) - len(error_case_ids),
            "label_mismatch_count": len(error_case_ids),
            "needs_review_count": len(needs_review_case_ids),
            "large_disagreement_count": len(disagreement_case_ids),
            "metrics": {
                "sample_count": metrics.sample_count,
                "accuracy": metrics.accuracy,
                "macro_f1": metrics.macro_f1,
                "cohen_kappa": metrics.cohen_kappa,
                "labels": {
                    label: asdict(label_metrics) for label, label_metrics in metrics.labels.items()
                },
                "confusion_matrix": [list(row) for row in metrics.confusion_matrix],
            },
        },
        "review_queue": {
            "label_mismatch_case_ids": list(error_case_ids),
            "needs_review_case_ids": list(needs_review_case_ids),
            "large_disagreement_case_ids": list(disagreement_case_ids),
            "representative_case_ids": representative_case_ids,
        },
        "cases": list(cases),
    }


def write_report(
    repository_root: Path,
    generated_at: datetime,
    output_path: Path = REPORT_PATH,
) -> Path:
    report = asyncio.run(run(repository_root, generated_at))
    absolute_output = repository_root / output_path
    absolute_output.parent.mkdir(parents=True, exist_ok=True)
    absolute_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return absolute_output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generated-at",
        default=datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    parser.add_argument("--output", default=REPORT_PATH.as_posix())
    arguments = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[2]
    write_report(
        repository_root,
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.output)),
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import mean
from typing import cast

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import (
    L3ProviderRequest,
    aggregate_level_scores,
    score_l1,
    score_l2,
    score_l3,
)
from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceSection,
    JobProfile,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.domain import (
    BoundaryRule,
    L1Policy,
    L2CriterionPolicy,
    L2Policy,
    MatchMode,
    RequirementRule,
    RoutingPolicy,
)
from backend.app.infrastructure.config import (
    RepositoryConfigurationLoader,
    build_routing_policy,
)
from backend.app.infrastructure.embeddings import (
    CoreEmbeddingAdapterBridge,
    EmbeddingAdapter,
    SentenceTransformerEmbeddingAdapter,
)
from backend.app.infrastructure.llm import DeterministicCoreL3Provider
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    SyntheticExpansionSilverSplitManifest,
    SyntheticPairAnnotation,
    file_sha256,
    validate_synthetic_expansion,
)
from evaluation.experiments.stage6_config import Stage6Candidate, load_stage6_candidate_set
from evaluation.metrics import ClassificationMetrics, calculate_metrics
from scripts.approve_synthetic_expansion import REVIEWED_DIRECTORY
from scripts.create_synthetic_expansion_split import SPLIT_MANIFEST_PATH
from scripts.generate_synthetic_expansion import ROLES, RoleDefinition

REPORT_PATH = Path("evaluation/reports/synthetic_expansion_v2_development_diagnostic.json")
REFERENCE_JOB_PROFILE_ID = "junior-data-analyst-v1"


@dataclass(frozen=True, slots=True)
class ExpansionEmbeddingRuntime:
    adapter: EmbeddingAdapter
    model_identifier: str
    model_version: str
    resolved_revision: str
    configured_model_executed: bool


class CachingCoreEmbeddingAdapter:
    def __init__(self, bridge: CoreEmbeddingAdapterBridge) -> None:
        self._bridge = bridge
        self._cache: dict[tuple[str, ...], tuple[tuple[float, ...], ...]] = {}

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        if texts not in self._cache:
            self._cache[texts] = self._bridge.embed(texts)
        return self._cache[texts]


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def default_embedding_runtime(repository_root: Path) -> ExpansionEmbeddingRuntime:
    loaded = RepositoryConfigurationLoader(repository_root).load_for_job(REFERENCE_JOB_PROFILE_ID)
    strategy = load_stage6_candidate_set(repository_root).model_strategy
    adapter = SentenceTransformerEmbeddingAdapter.from_configuration(
        loaded.models_artifact.embedding
    )
    return ExpansionEmbeddingRuntime(
        adapter=adapter,
        model_identifier=strategy.embedding_model_identifier,
        model_version=strategy.embedding_configured_version,
        resolved_revision=strategy.embedding_resolved_revision,
        configured_model_executed=True,
    )


def _role_definition(role: DatasetRole) -> RoleDefinition:
    return next(definition for definition in ROLES if definition.role is role)


def build_expansion_l1_policy(
    role: DatasetRole,
    job_profile_id: str,
) -> L1Policy:
    definition = _role_definition(role)
    sections = (
        EvidenceSection.SKILLS,
        EvidenceSection.WORK_EXPERIENCE,
        EvidenceSection.PROJECTS,
        EvidenceSection.OTHER,
    )
    return L1Policy(
        job_profile_id=job_profile_id,
        rules=tuple(
            RequirementRule(
                requirement_id=requirement.requirement_id,
                evidence_sections=sections,
                positive_terms=(requirement.positive_evidence,),
                explicit_negative_terms=(requirement.explicit_negative_evidence,),
                match_mode=MatchMode.ANY,
            )
            for requirement in definition.requirements
        ),
    )


def _l2_policy(
    rubric: ScoringRubric,
    candidate: Stage6Candidate,
) -> L2Policy:
    sections = (
        EvidenceSection.SKILLS,
        EvidenceSection.WORK_EXPERIENCE,
        EvidenceSection.PROJECTS,
        EvidenceSection.EDUCATION,
    )
    return L2Policy(
        job_profile_id=rubric.job_profile_id,
        criteria=tuple(
            L2CriterionPolicy(
                criterion_id=criterion.criterion_id,
                query_text=f"{criterion.title}. {criterion.description}",
                evidence_sections=sections,
                similarity_floor=candidate.l2_matching.similarity_floor,
                similarity_ceiling=candidate.l2_matching.similarity_ceiling,
                top_k=candidate.l2_matching.top_k,
            )
            for criterion in rubric.criteria
        ),
    )


def build_diagnostic_routing_policy(
    repository_root: Path,
    candidate: Stage6Candidate,
) -> RoutingPolicy:
    loaded = RepositoryConfigurationLoader(repository_root).load_for_job(REFERENCE_JOB_PROFILE_ID)
    base = build_routing_policy(loaded)
    offset = candidate.boundary_offset_points
    return replace(
        base,
        pass_minimum=candidate.thresholds.pass_minimum,
        waitlist_minimum=candidate.thresholds.waitlist_minimum,
        disagreement_points=candidate.disagreement_points,
        boundary_rules=(
            BoundaryRule(
                rule_id="lower-threshold-boundary",
                minimum=candidate.thresholds.waitlist_minimum - offset,
                maximum=candidate.thresholds.waitlist_minimum + offset,
            ),
            BoundaryRule(
                rule_id="upper-threshold-boundary",
                minimum=candidate.thresholds.pass_minimum - offset,
                maximum=candidate.thresholds.pass_minimum + offset,
            ),
        ),
    )


def load_development(
    repository_root: Path,
    reviewed_directory_path: Path = REVIEWED_DIRECTORY,
    split_manifest_path: Path = SPLIT_MANIFEST_PATH,
) -> tuple[
    tuple[SyntheticPairAnnotation, ...],
    dict[str, CVProfile],
    dict[str, JobProfile],
    dict[str, ScoringRubric],
    SyntheticExpansionSilverSplitManifest,
]:
    reviewed_directory = repository_root / reviewed_directory_path
    report = validate_synthetic_expansion(reviewed_directory)
    if not report.passed:
        raise ValueError("reviewed expansion must pass quality control")
    split_path = repository_root / split_manifest_path
    split = SyntheticExpansionSilverSplitManifest.model_validate_json(
        split_path.read_text(encoding="utf-8")
    )
    if split.source_manifest_sha256 != file_sha256(reviewed_directory / "manifest.json"):
        raise ValueError("split source manifest hash no longer matches reviewed data")
    profiles = {
        profile.cv_profile_id: profile
        for profile in (
            CVProfile.model_validate_json(line)
            for line in (reviewed_directory / "cv_profiles.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    jobs = {
        job.job_profile_id: job
        for job in (
            JobProfile.model_validate_json(line)
            for line in (reviewed_directory / "job_profiles.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    rubrics = {
        rubric.rubric_id: rubric
        for rubric in (
            ScoringRubric.model_validate_json(line)
            for line in (reviewed_directory / "rubrics.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    development_ids = set(split.development.pair_ids)
    annotations = tuple(
        annotation
        for annotation in (
            SyntheticPairAnnotation.model_validate_json(line)
            for line in (reviewed_directory / "pairs.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
        if annotation.pair_id in development_ids
    )
    if len(annotations) != 150 or {item.pair_id for item in annotations} != development_ids:
        raise ValueError("development annotations do not match the split manifest")
    return annotations, profiles, jobs, rubrics, split


def _score(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


def _metrics_payload(metrics: ClassificationMetrics) -> dict[str, object]:
    return {
        "sample_count": metrics.sample_count,
        "accuracy": metrics.accuracy,
        "macro_f1": metrics.macro_f1,
        "cohen_kappa": metrics.cohen_kappa,
        "labels": {label: asdict(values) for label, values in metrics.labels.items()},
        "confusion_matrix": [list(row) for row in metrics.confusion_matrix],
    }


async def run(
    repository_root: Path,
    generated_at: datetime,
    embedding_runtime: ExpansionEmbeddingRuntime | None = None,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    annotations, profiles, jobs, rubrics, split = load_development(repository_root)
    runtime = embedding_runtime or default_embedding_runtime(repository_root)
    candidate_set = load_stage6_candidate_set(repository_root)
    candidate = next(
        item for item in candidate_set.candidates if item.candidate_id == "approved-current-v1"
    )
    model_strategy = candidate_set.model_strategy
    prompt_version = model_strategy.prompt_version
    routing_policy = build_diagnostic_routing_policy(repository_root, candidate)
    embedding = CachingCoreEmbeddingAdapter(
        CoreEmbeddingAdapterBridge(runtime.adapter, query_count=5)
    )
    cases: list[dict[str, object]] = []
    expected: list[ClassificationDecision] = []
    predicted: list[ClassificationDecision] = []
    l1_status_matches = 0
    l2_scores: list[float] = []
    l3_absolute_errors: list[float] = []
    for annotation in annotations:
        profile = profiles[annotation.cv_profile_id]
        job = jobs[annotation.job_profile_id]
        rubric = rubrics[annotation.rubric_id]
        l1_policy = build_expansion_l1_policy(annotation.role, job.job_profile_id)
        l1 = score_l1(profile, rubric, l1_policy)
        l2 = score_l2(profile, rubric, _l2_policy(rubric, candidate), embedding)
        if runtime.configured_model_executed and l2.status is not LevelScoreStatus.AVAILABLE:
            raise RuntimeError("configured multilingual L2 failed during expansion diagnostic")
        l3 = await score_l3(
            request=L3ProviderRequest(
                cv_profile=profile,
                job_profile=job,
                rubric=rubric,
                prompt_version=prompt_version,
            ),
            provider=DeterministicCoreL3Provider(l1_policy),
        )
        aggregation = aggregate_level_scores((l1, l2, l3), candidate.aggregation)
        routing = route_classification(
            aggregation,
            l1.requirement_assessments,
            routing_policy,
        )
        human_statuses = {
            item.requirement_id: item.evidence_status
            for item in annotation.critical_requirement_assessments
        }
        classifier_statuses = {
            item.requirement_id: item.evidence_status for item in l1.requirement_assessments
        }
        status_match = human_statuses == classifier_statuses
        l1_status_matches += int(status_match)
        if l2.score is not None:
            l2_scores.append(float(l2.score))
        if l3.score is not None:
            l3_absolute_errors.append(abs(float(l3.score) - float(annotation.total_score)))
        review = cast(ApprovedDatasetReview, annotation.review)
        expected.append(review.final_label)
        predicted.append(routing.decision)
        cases.append(
            {
                "pair_id": annotation.pair_id,
                "role": annotation.role.value,
                "cv_profile_id": annotation.cv_profile_id,
                "job_profile_id": annotation.job_profile_id,
                "expected_label": review.final_label.value,
                "predicted_label": routing.decision.value,
                "label_match": review.final_label is routing.decision,
                "l1_requirement_status_match": status_match,
                "level_scores": {
                    "l1": _score(l1.score),
                    "l2": _score(l2.score),
                    "l3": _score(l3.score),
                },
                "final_score": _score(routing.final_score),
                "review_reasons": list(routing.reasons),
            }
        )
    expected_labels = tuple(expected)
    predicted_labels = tuple(predicted)
    role_metrics = {
        role.value: _metrics_payload(
            calculate_metrics(
                tuple(
                    expected_label
                    for expected_label, annotation in zip(expected_labels, annotations, strict=True)
                    if annotation.role is role
                ),
                tuple(
                    predicted_label
                    for predicted_label, annotation in zip(
                        predicted_labels, annotations, strict=True
                    )
                    if annotation.role is role
                ),
            )
        )
        for role in DatasetRole
    }
    false_reject_count = sum(
        actual is not ClassificationDecision.REJECT and prediction is ClassificationDecision.REJECT
        for actual, prediction in zip(expected_labels, predicted_labels, strict=True)
    )
    unsafe_pass_count = sum(
        prediction is ClassificationDecision.PASS
        and actual in {ClassificationDecision.REJECT, ClassificationDecision.NEEDS_REVIEW}
        for actual, prediction in zip(expected_labels, predicted_labels, strict=True)
    )
    expected_review_count = sum(
        label is ClassificationDecision.NEEDS_REVIEW for label in expected_labels
    )
    review_hits = sum(
        actual is ClassificationDecision.NEEDS_REVIEW
        and prediction is ClassificationDecision.NEEDS_REVIEW
        for actual, prediction in zip(expected_labels, predicted_labels, strict=True)
    )
    split_path = repository_root / SPLIT_MANIFEST_PATH
    reviewed_manifest_path = repository_root / REVIEWED_DIRECTORY / "manifest.json"
    return {
        "report_schema_version": "1.0.0",
        "report_id": "synthetic-expansion-v2-development-diagnostic",
        "report_scope": "silver-development-controlled-l1-local-l2-deterministic-l3",
        "is_final_performance": False,
        "generated_at": generated_at.isoformat(),
        "dataset_traceability": {
            "dataset_id": split.source_dataset_id,
            "dataset_version": split.source_dataset_version,
            "dataset_tier": split.source_dataset_tier.value,
            "reviewed_manifest_sha256": file_sha256(reviewed_manifest_path),
            "split_manifest_sha256": file_sha256(split_path),
            "partition_id": split.development.partition_id,
            "candidate_count": split.development.candidate_count,
            "pair_count": split.development.pair_count,
            "held_out_partition_evaluated": False,
            "held_out_results_generated": False,
            "original_stage6_frozen_test_evaluated": False,
        },
        "execution_strategy": {
            "l1": "synthetic-v2-versioned-requirement-rules",
            "l1_generator_vocabulary_alignment_risk": True,
            "l2_model_identifier": runtime.model_identifier,
            "l2_model_version": runtime.model_version,
            "l2_resolved_revision": runtime.resolved_revision,
            "configured_multilingual_l2_executed": runtime.configured_model_executed,
            "l3": model_strategy.l3_model_identifier,
            "l3_provider_identifier": model_strategy.l3_provider_identifier,
            "live_llm_provider_executed": False,
            "prompt_version": prompt_version,
            "automatic_pass_gate_applied": False,
        },
        "summary": {
            "ground_truth_distribution": dict(
                sorted(Counter(label.value for label in expected_labels).items())
            ),
            "prediction_distribution": dict(
                sorted(Counter(label.value for label in predicted_labels).items())
            ),
            "overall_metrics": _metrics_payload(
                calculate_metrics(expected_labels, predicted_labels)
            ),
            "role_metrics": role_metrics,
            "l1_requirement_status_match_rate": l1_status_matches / len(annotations),
            "average_l2_score": mean(l2_scores),
            "l2_score_at_100_count": sum(score == 100.0 for score in l2_scores),
            "deterministic_l3_total_score_mae": mean(l3_absolute_errors),
            "needs_review_recall": review_hits / expected_review_count,
            "review_rate": sum(
                label is ClassificationDecision.NEEDS_REVIEW for label in predicted_labels
            )
            / len(predicted_labels),
            "false_reject_count": false_reject_count,
            "unsafe_pass_count": unsafe_pass_count,
        },
        "limitations": [
            "All records are synthetic Silver data reviewed by one person.",
            "Five pairs from one candidate are correlated and are not independent samples.",
            "L1 rules intentionally reuse generator vocabulary and cannot establish real-CV generalization.",
            "L3 uses a deterministic fake; live provider quality was not measured in this report.",
            "The held-out Silver partition and the original Stage 6 frozen test were not evaluated.",
        ],
        "cases": cases,
    }


def write_report(
    repository_root: Path,
    generated_at: datetime,
    output_path: Path = REPORT_PATH,
    embedding_runtime: ExpansionEmbeddingRuntime | None = None,
) -> Path:
    report = asyncio.run(run(repository_root, generated_at, embedding_runtime))
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
    write_report(
        Path(__file__).resolve().parents[2],
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.output)),
    )


if __name__ == "__main__":
    main()

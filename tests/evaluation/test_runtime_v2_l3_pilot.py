from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from backend.app.infrastructure.llm import (
    LLMProviderResult,
    LLMProviderStatus,
    LLMScoringOutput,
    LLMScoringRequest,
    LLMWeightedCriterionAssessment,
    LLMRequirementAssessment,
)
from backend.app.contracts import EvidenceStatus
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation
from evaluation.experiments.run_runtime_v2_l3_pilot import (
    _empty_cache,
    build_pilot_report,
    collect_pilot,
    load_pilot_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
V2_CONFIGURATION_PATH = Path("evaluation/configs/runtime_v2_l3_pilot_v2.yaml")
V3_CONFIGURATION_PATH = Path("evaluation/configs/runtime_v2_l3_pilot_v3.yaml")
DEVELOPMENT_CONFIGURATION_PATH = Path("evaluation/configs/runtime_v2_l3_development_panel_v1.yaml")
CALIBRATION_CONFIGURATION_PATH = Path("evaluation/configs/runtime_v2_l3_calibration_probe_v4.yaml")
DEVELOPMENT_V2_CONFIGURATION_PATH = Path(
    "evaluation/configs/runtime_v2_l3_development_panel_v2.yaml"
)
VALIDATION_CONFIGURATION_PATH = Path("evaluation/configs/runtime_v2_l3_validation_v1.yaml")
FRESH_CONFIRMATION_CONFIGURATION_PATH = Path(
    "evaluation/configs/runtime_v2_l3_fresh_confirmation_v1.yaml"
)
FRESH_CONFIRMATION_V2_CONFIGURATION_PATH = Path(
    "evaluation/configs/runtime_v2_l3_fresh_confirmation_v2.yaml"
)


class HumanEquivalentAdapter:
    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        reviewed = REPOSITORY_ROOT / "data/runtime_v2/reviewed/development_v1/pairs.jsonl"
        pair_id = request.request_id.split("-pilot-", maxsplit=1)[0]
        pair = next(
            item
            for line in reviewed.read_text(encoding="utf-8").splitlines()
            if (item := SyntheticPairAnnotation.model_validate_json(line)).pair_id == pair_id
        )
        output = LLMScoringOutput(
            requirement_assessments=tuple(
                LLMRequirementAssessment(
                    requirement_id=item.requirement_id,
                    evidence_status=item.evidence_status,
                    evidence_ids=item.evidence_ids,
                    rationale=item.rationale,
                )
                for item in pair.critical_requirement_assessments
            ),
            criterion_assessments=tuple(
                LLMWeightedCriterionAssessment(
                    criterion_id=item.criterion_id,
                    score=item.awarded_points,
                    evidence_status=(
                        EvidenceStatus.SATISFIED if item.evidence_ids else EvidenceStatus.MISSING
                    ),
                    evidence_ids=item.evidence_ids,
                    rationale=item.rationale,
                )
                for item in pair.criterion_assessments
            ),
            overall_score=pair.total_score,
            confidence=Decimal("0.8"),
        )
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            prompt_version=request.prompt_version,
            output=output,
        )


def test_runtime_v2_l3_pilot_is_bounded_and_development_only() -> None:
    configuration = load_pilot_configuration(REPOSITORY_ROOT)

    assert configuration.data_policy.development_only is True
    assert configuration.data_policy.validation_allowed is False
    assert configuration.data_policy.stage7_v1_test_allowed is False
    assert configuration.request_policy.hard_request_cap == 7
    assert len(configuration.pilot_pair_ids) == 5


def test_runtime_v2_l3_pilot_v2_uses_conflict_audited_prompt() -> None:
    configuration = load_pilot_configuration(REPOSITORY_ROOT, V2_CONFIGURATION_PATH)

    assert configuration.experiment_id == "runtime-v2-l3-pilot-v2"
    assert configuration.experiment_version == "2.0.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v13"
    assert configuration.data_policy.validation_allowed is False


def test_runtime_v2_l3_pilot_v3_uses_authoritative_requirement_prompt() -> None:
    configuration = load_pilot_configuration(REPOSITORY_ROOT, V3_CONFIGURATION_PATH)

    assert configuration.experiment_id == "runtime-v2-l3-pilot-v3"
    assert configuration.experiment_version == "3.0.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v14"
    assert configuration.data_policy.validation_allowed is False


def test_runtime_v2_l3_development_panel_is_balanced_and_bounded() -> None:
    configuration = load_pilot_configuration(
        REPOSITORY_ROOT,
        DEVELOPMENT_CONFIGURATION_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-l3-development-panel-v1"
    assert len(configuration.pilot_pair_ids) == 20
    assert configuration.request_policy.hard_request_cap == 22
    assert configuration.quality_policy.required_requirement_status_match_rate == 1
    assert configuration.cost_policy.maximum_estimated_cost_usd == Decimal("0.35")


@pytest.mark.asyncio
async def test_runtime_v2_l3_calibration_probe_targets_missing_criterion_behavior(
    tmp_path: Path,
) -> None:
    configuration = load_pilot_configuration(
        REPOSITORY_ROOT,
        CALIBRATION_CONFIGURATION_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-l3-calibration-probe-v4"
    assert configuration.prompt_version == "l3-evidence-rubric-v15"
    assert configuration.pilot_pair_ids[0] == "v2d-pair-da-13"
    assert configuration.cost_policy.maximum_estimated_cost_usd == Decimal("0.10")
    cache = await collect_pilot(
        REPOSITORY_ROOT,
        HumanEquivalentAdapter(),
        configuration_path=CALIBRATION_CONFIGURATION_PATH,
        cache_path=tmp_path / "calibration-probe-cache.json",
        maximum_new_requests=1,
    )
    assert cache.attempts[0].pair_id == "v2d-pair-da-13"


def test_runtime_v2_l3_development_panel_v2_uses_versioned_mapping() -> None:
    configuration = load_pilot_configuration(
        REPOSITORY_ROOT,
        DEVELOPMENT_V2_CONFIGURATION_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-l3-development-panel-v2"
    assert configuration.prompt_version == "l3-evidence-rubric-v15"
    assert configuration.score_mapping_version == "l3-deterministic-level-mapping-v2"
    assert len(configuration.pilot_pair_ids) == 20


def test_runtime_v2_l3_validation_is_locked_to_validation_partition() -> None:
    configuration = load_pilot_configuration(
        REPOSITORY_ROOT,
        VALIDATION_CONFIGURATION_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-l3-validation-v1"
    assert configuration.data_policy.partition == "validation"
    assert configuration.data_policy.development_only is False
    assert configuration.data_policy.validation_allowed is True
    assert len(configuration.pilot_pair_ids) == 25
    assert configuration.request_policy.hard_request_cap == 27


def test_runtime_v2_l3_fresh_confirmation_is_bounded_and_development_only() -> None:
    configuration = load_pilot_configuration(
        REPOSITORY_ROOT,
        FRESH_CONFIRMATION_CONFIGURATION_PATH,
    )
    development_panel = load_pilot_configuration(
        REPOSITORY_ROOT,
        DEVELOPMENT_V2_CONFIGURATION_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-l3-fresh-confirmation-v1"
    assert configuration.data_policy.partition == "development"
    assert configuration.data_policy.validation_allowed is False
    assert configuration.data_policy.stage7_v1_test_allowed is False
    assert len(configuration.pilot_pair_ids) == 10
    assert configuration.request_policy.hard_request_cap == 12
    assert set(configuration.pilot_pair_ids).isdisjoint(development_panel.pilot_pair_ids)
    assert configuration.cost_policy.maximum_estimated_cost_usd == Decimal("0.20")
    cache = _empty_cache(
        REPOSITORY_ROOT,
        configuration,
        FRESH_CONFIRMATION_CONFIGURATION_PATH,
    )
    assert cache.experiment_id == configuration.experiment_id


def test_runtime_v2_l3_fresh_confirmation_v2_is_new_and_balanced() -> None:
    configuration = load_pilot_configuration(
        REPOSITORY_ROOT,
        FRESH_CONFIRMATION_V2_CONFIGURATION_PATH,
    )
    first_confirmation = load_pilot_configuration(
        REPOSITORY_ROOT,
        FRESH_CONFIRMATION_CONFIGURATION_PATH,
    )
    development_panel = load_pilot_configuration(
        REPOSITORY_ROOT,
        DEVELOPMENT_V2_CONFIGURATION_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-l3-fresh-confirmation-v2"
    assert configuration.experiment_version == "2.0.0"
    assert len(configuration.pilot_pair_ids) == 10
    assert set(configuration.pilot_pair_ids).isdisjoint(first_confirmation.pilot_pair_ids)
    assert set(configuration.pilot_pair_ids).isdisjoint(development_panel.pilot_pair_ids)
    assert configuration.cost_policy.maximum_estimated_cost_usd == Decimal("0.20")


@pytest.mark.asyncio
async def test_runtime_v2_l3_pilot_fake_outputs_pass_without_api(tmp_path: Path) -> None:
    cache_path = tmp_path / "pilot-cache.json"
    cache = await collect_pilot(
        REPOSITORY_ROOT,
        HumanEquivalentAdapter(),
        cache_path=cache_path,
    )
    report = build_pilot_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T10:00:00+07:00"),
        cache,
    )
    resumed = await collect_pilot(
        REPOSITORY_ROOT,
        HumanEquivalentAdapter(),
        cache_path=cache_path,
    )

    assert len(cache.attempts) == 5
    assert resumed == cache
    quality_gate = cast(dict[str, object], report["quality_gate"])
    assert quality_gate["passed"] is True
    assert report["unsafe_requirement_status_mismatch_count"] == 0
    assert report["total_score_mae"] == 0


@pytest.mark.asyncio
async def test_runtime_v2_l3_pilot_v2_keeps_separate_traceability(tmp_path: Path) -> None:
    cache = await collect_pilot(
        REPOSITORY_ROOT,
        HumanEquivalentAdapter(),
        configuration_path=V2_CONFIGURATION_PATH,
        cache_path=tmp_path / "pilot-v2-cache.json",
    )
    report = build_pilot_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T10:00:00+07:00"),
        cache,
        configuration_path=V2_CONFIGURATION_PATH,
    )

    assert cache.experiment_id == "runtime-v2-l3-pilot-v2"
    assert cache.prompt_version == "l3-evidence-rubric-v13"
    assert report["report_id"] == "runtime-v2-l3-pilot-v2"
    assert report["prompt_version"] == "l3-evidence-rubric-v13"


@pytest.mark.asyncio
async def test_runtime_v2_l3_pilot_v3_uses_l1_requirement_references(tmp_path: Path) -> None:
    cache = await collect_pilot(
        REPOSITORY_ROOT,
        HumanEquivalentAdapter(),
        configuration_path=V3_CONFIGURATION_PATH,
        cache_path=tmp_path / "pilot-v3-cache.json",
    )
    report = build_pilot_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T10:00:00+07:00"),
        cache,
        configuration_path=V3_CONFIGURATION_PATH,
    )

    assert cache.experiment_id == "runtime-v2-l3-pilot-v3"
    assert cache.prompt_version == "l3-evidence-rubric-v14"
    assert report["quality_gate"]["passed"] is True

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from copy import deepcopy
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal, Protocol, Self, cast

import httpx
from pydantic import Field, ValidationError, field_validator, model_validator

from backend.app.agents.classifier.prompts import (
    AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
    CONFLICT_AUDITED_PROMPT_VERSION,
    CRITERION_STATUS_PROMPT_VERSION,
    PROMPT_VERSION,
    REQUIREMENT_GUARDED_PROMPT_VERSION,
    ROLE_CALIBRATED_PROMPT_VERSION,
    build_l3_messages,
)
from backend.app.agents.classifier.scoring.l1 import score_l1
from backend.app.agents.classifier.scoring.l3 import L3ProviderRequest
from backend.app.agents.classifier.scoring.l3_calibration import (
    L3_CALIBRATION_MAPPING_VERSION,
    L3_CALIBRATION_MAPPING_V2,
    L3_CALIBRATION_MAPPING_V3,
    L3CalibrationLevel,
    calibrated_l3_criterion_scores,
)
from backend.app.contracts import (
    Evidence,
    EvidenceStatus,
    JobProfile,
    ScoringRubric,
)
from backend.app.contracts.common import (
    Confidence,
    ContractModel,
    Identifier,
    NonEmptyText,
    Score,
)
from backend.app.infrastructure.config import ModelsConfigurationArtifact
from backend.app.domain import L1Policy, RequirementAssessment


class LLMProviderStatus(StrEnum):
    AVAILABLE = "available"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


class LLMConfigurationError(ValueError):
    pass


class LLMOutputValidationError(ValueError):
    pass


class LLMResponseContentError(ValueError):
    pass


class LLMProviderUsage(ContractModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        if self.total_tokens < self.input_tokens + self.output_tokens:
            raise ValueError("provider total tokens cannot be below input plus output tokens")
        return self


class LLMRequirementReference(ContractModel):
    requirement_id: Identifier
    evidence_status: EvidenceStatus
    evidence_ids: tuple[Identifier, ...] = ()
    rationale: NonEmptyText

    @model_validator(mode="after")
    def validate_evidence_state(self) -> Self:
        if (
            self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}
            and not self.evidence_ids
        ):
            raise ValueError("satisfied and unsatisfied requirement references require evidence")
        if self.evidence_status is EvidenceStatus.MISSING and self.evidence_ids:
            raise ValueError("missing requirement references must not use evidence")
        if self.evidence_status is EvidenceStatus.CONFLICTING and len(set(self.evidence_ids)) < 2:
            raise ValueError("conflicting requirement references require two evidence records")
        return self


class LLMScoringRequest(ContractModel):
    request_id: Identifier
    job_profile: JobProfile
    rubric: ScoringRubric
    evidence: Annotated[tuple[Evidence, ...], Field(min_length=1)]
    prompt_version: NonEmptyText
    authoritative_requirement_assessments: tuple[LLMRequirementReference, ...] = ()

    @model_validator(mode="after")
    def validate_artifact_link(self) -> Self:
        if self.rubric.job_profile_id != self.job_profile.job_profile_id:
            raise ValueError("LLM rubric must reference the supplied job profile")
        evidence_ids = tuple(item.evidence_id for item in self.evidence)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("LLM evidence identifiers must be unique")
        if self.authoritative_requirement_assessments:
            requirement_ids = tuple(
                item.requirement_id for item in self.authoritative_requirement_assessments
            )
            if len(requirement_ids) != len(set(requirement_ids)):
                raise ValueError("authoritative LLM requirement identifiers must be unique")
            if set(requirement_ids) != set(self.rubric.critical_requirement_ids):
                raise ValueError("authoritative LLM requirements must match the rubric")
            known_evidence_ids = set(evidence_ids)
            if any(
                not set(item.evidence_ids).issubset(known_evidence_ids)
                for item in self.authoritative_requirement_assessments
            ):
                raise ValueError("authoritative LLM requirements reference unknown evidence")
        return self


class LLMWeightedCriterionAssessment(ContractModel):
    criterion_id: Identifier
    score: Score
    evidence_status: EvidenceStatus
    evidence_ids: tuple[Identifier, ...] = ()
    rationale: NonEmptyText

    @field_validator("score", mode="before")
    @classmethod
    def reject_non_numeric_score(cls, value: object) -> object:
        if isinstance(value, (bool, str)) or not isinstance(value, (Decimal, float, int)):
            raise ValueError("LLM score must be a JSON number")
        return value

    @model_validator(mode="after")
    def validate_evidence_state(self) -> Self:
        if (
            self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}
            and not self.evidence_ids
        ):
            raise ValueError("satisfied and unsatisfied LLM assessments require evidence")
        if self.evidence_status is EvidenceStatus.MISSING and self.evidence_ids:
            raise ValueError("missing LLM assessments must not invent evidence")
        if self.evidence_status is EvidenceStatus.CONFLICTING and len(set(self.evidence_ids)) < 2:
            raise ValueError("conflicting LLM assessments require at least two evidence records")
        return self


class LLMQualitativeCriterionAssessment(ContractModel):
    criterion_id: Identifier
    calibration_level: L3CalibrationLevel
    evidence_status: EvidenceStatus
    evidence_ids: tuple[Identifier, ...] = ()
    rationale: NonEmptyText

    @model_validator(mode="after")
    def validate_evidence_state(self) -> Self:
        if (
            self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}
            and not self.evidence_ids
        ):
            raise ValueError("satisfied and unsatisfied LLM assessments require evidence")
        if self.evidence_status is EvidenceStatus.MISSING and self.evidence_ids:
            raise ValueError("missing LLM assessments must not invent evidence")
        if self.evidence_status is EvidenceStatus.CONFLICTING and len(set(self.evidence_ids)) < 2:
            raise ValueError("conflicting LLM assessments require at least two evidence records")
        return self


class LLMRequirementAssessment(ContractModel):
    requirement_id: Identifier
    evidence_status: EvidenceStatus
    evidence_ids: tuple[Identifier, ...] = ()
    rationale: NonEmptyText

    @model_validator(mode="after")
    def validate_evidence_state(self) -> Self:
        if (
            self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}
            and not self.evidence_ids
        ):
            raise ValueError("satisfied and unsatisfied LLM requirements require evidence")
        if self.evidence_status is EvidenceStatus.MISSING and self.evidence_ids:
            raise ValueError("missing LLM requirements must not invent evidence")
        if self.evidence_status is EvidenceStatus.CONFLICTING and len(set(self.evidence_ids)) < 2:
            raise ValueError("conflicting LLM requirements require at least two evidence records")
        return self


class LLMScoringOutput(ContractModel):
    overall_score: Score
    requirement_assessments: Annotated[tuple[LLMRequirementAssessment, ...], Field(min_length=1)]
    criterion_assessments: Annotated[
        tuple[LLMWeightedCriterionAssessment, ...], Field(min_length=1)
    ]
    strengths: tuple[NonEmptyText, ...] = ()
    risks: tuple[NonEmptyText, ...] = ()
    warnings: tuple[NonEmptyText, ...] = ()
    confidence: Confidence

    @field_validator("overall_score", "confidence", mode="before")
    @classmethod
    def reject_non_numeric_values(cls, value: object) -> object:
        if isinstance(value, (bool, str)) or not isinstance(value, (Decimal, float, int)):
            raise ValueError("LLM numeric output fields must be JSON numbers")
        return value

    @model_validator(mode="after")
    def validate_assessments(self) -> Self:
        requirement_ids = tuple(item.requirement_id for item in self.requirement_assessments)
        criterion_ids = tuple(item.criterion_id for item in self.criterion_assessments)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("LLM requirement assessments must be unique")
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("LLM criterion assessments must be unique")
        if sum(item.score for item in self.criterion_assessments) != self.overall_score:
            raise ValueError("LLM overall score must equal the criterion score sum")
        return self


class LLMQualitativeAssessmentOutput(ContractModel):
    requirement_assessments: Annotated[tuple[LLMRequirementAssessment, ...], Field(min_length=1)]
    criterion_assessments: Annotated[
        tuple[LLMQualitativeCriterionAssessment, ...], Field(min_length=1)
    ]
    strengths: tuple[NonEmptyText, ...] = ()
    risks: tuple[NonEmptyText, ...] = ()
    warnings: tuple[NonEmptyText, ...] = ()
    confidence: Confidence

    @field_validator("confidence", mode="before")
    @classmethod
    def reject_non_numeric_confidence(cls, value: object) -> object:
        if isinstance(value, (bool, str)) or not isinstance(value, (Decimal, float, int)):
            raise ValueError("LLM numeric output fields must be JSON numbers")
        return value

    @model_validator(mode="after")
    def validate_assessments(self) -> Self:
        requirement_ids = tuple(item.requirement_id for item in self.requirement_assessments)
        criterion_ids = tuple(item.criterion_id for item in self.criterion_assessments)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("LLM requirement assessments must be unique")
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("LLM criterion assessments must be unique")
        return self


class LLMProviderResult(ContractModel):
    status: LLMProviderStatus
    provider_identifier: NonEmptyText
    model_identifier: NonEmptyText
    prompt_version: NonEmptyText
    output: LLMScoringOutput | None = None
    reason: NonEmptyText | None = None
    usage: LLMProviderUsage | None = None
    calibration_levels: dict[Identifier, L3CalibrationLevel] | None = None

    @model_validator(mode="after")
    def validate_status(self) -> Self:
        if self.status is LLMProviderStatus.AVAILABLE:
            if self.output is None or self.reason is not None:
                raise ValueError("available LLM output must contain output and no failure reason")
        elif (
            self.output is not None
            or self.reason is None
            or self.usage is not None
            or self.calibration_levels is not None
        ):
            raise ValueError("failed LLM output must contain a reason and no output")
        return self


class LLMAdapter(Protocol):
    async def score(self, request: LLMScoringRequest) -> LLMProviderResult: ...


def _domain_requirement_references(
    request: LLMScoringRequest,
) -> tuple[RequirementAssessment, ...]:
    return tuple(
        RequirementAssessment(
            requirement_id=item.requirement_id,
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in request.authoritative_requirement_assessments
    )


def _apply_authoritative_requirements(
    request: LLMScoringRequest,
    output: LLMQualitativeAssessmentOutput,
) -> LLMQualitativeAssessmentOutput:
    if not request.authoritative_requirement_assessments:
        return output
    assessments = tuple(
        LLMRequirementAssessment(
            requirement_id=item.requirement_id,
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in request.authoritative_requirement_assessments
    )
    return output.model_copy(update={"requirement_assessments": assessments})


def validate_output_against_request(
    request: LLMScoringRequest,
    output: LLMScoringOutput,
) -> None:
    requirement_ids = {item.requirement_id for item in output.requirement_assessments}
    if requirement_ids != set(request.rubric.critical_requirement_ids):
        raise LLMOutputValidationError(
            "LLM requirement identifiers do not match critical rubric requirements"
        )
    criterion_weights = {item.criterion_id: item.weight for item in request.rubric.criteria}
    assessment_ids = {item.criterion_id for item in output.criterion_assessments}
    if assessment_ids != set(criterion_weights):
        raise LLMOutputValidationError("LLM criterion identifiers do not match the rubric")
    evidence_ids = {item.evidence_id for item in request.evidence}
    for assessment in output.requirement_assessments:
        if not set(assessment.evidence_ids).issubset(evidence_ids):
            raise LLMOutputValidationError("LLM requirement references unknown evidence")
    for assessment in output.criterion_assessments:
        if assessment.score > criterion_weights[assessment.criterion_id]:
            raise LLMOutputValidationError("LLM criterion score exceeds its rubric weight")
        if not set(assessment.evidence_ids).issubset(evidence_ids):
            raise LLMOutputValidationError("LLM output references unknown evidence")


def calibrated_scoring_output(
    request: LLMScoringRequest,
    output: LLMQualitativeAssessmentOutput,
    score_mapping_version: str | None = None,
) -> LLMScoringOutput:
    requirement_ids = {item.requirement_id for item in output.requirement_assessments}
    if requirement_ids != set(request.rubric.critical_requirement_ids):
        raise LLMOutputValidationError(
            "LLM requirement identifiers do not match critical rubric requirements"
        )
    criterion_ids = {item.criterion_id for item in output.criterion_assessments}
    expected_criterion_ids = {item.criterion_id for item in request.rubric.criteria}
    if criterion_ids != expected_criterion_ids:
        raise LLMOutputValidationError("LLM criterion identifiers do not match the rubric")
    allowed_evidence_ids = {item.evidence_id for item in request.evidence}
    for assessment in output.requirement_assessments:
        if not set(assessment.evidence_ids).issubset(allowed_evidence_ids):
            raise LLMOutputValidationError("LLM requirement references unknown evidence")
    for assessment in output.criterion_assessments:
        if not set(assessment.evidence_ids).issubset(allowed_evidence_ids):
            raise LLMOutputValidationError("LLM output references unknown evidence")
    scores = calibrated_l3_criterion_scores(
        request.rubric,
        {item.requirement_id: item.evidence_status for item in output.requirement_assessments},
        {item.criterion_id: item.calibration_level for item in output.criterion_assessments},
        {item.criterion_id: item.evidence_status for item in output.criterion_assessments},
        score_mapping_version
        or (
            L3_CALIBRATION_MAPPING_V2
            if request.prompt_version == CRITERION_STATUS_PROMPT_VERSION
            else L3_CALIBRATION_MAPPING_VERSION
        ),
    )
    criteria = tuple(
        LLMWeightedCriterionAssessment(
            criterion_id=item.criterion_id,
            score=scores[item.criterion_id],
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in output.criterion_assessments
    )
    return LLMScoringOutput(
        overall_score=sum((item.score for item in criteria), start=Decimal("0")),
        requirement_assessments=output.requirement_assessments,
        criterion_assessments=criteria,
        strengths=output.strengths,
        risks=output.risks,
        warnings=output.warnings,
        confidence=output.confidence,
    )


class DeterministicFakeLLMAdapter:
    def __init__(
        self,
        output: LLMScoringOutput,
        model_identifier: str = "deterministic-evidence-scorer-v1",
        prompt_version: str = "l3-evidence-rubric-v1",
    ) -> None:
        self._output = output
        self._model_identifier = model_identifier
        self._prompt_version = prompt_version

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        if request.prompt_version != self._prompt_version:
            return LLMProviderResult(
                status=LLMProviderStatus.INVALID,
                provider_identifier="deterministic_fake",
                model_identifier=self._model_identifier,
                prompt_version=self._prompt_version,
                reason="Deterministic fake prompt version does not match the request.",
            )
        try:
            validate_output_against_request(request, self._output)
        except LLMOutputValidationError:
            return LLMProviderResult(
                status=LLMProviderStatus.INVALID,
                provider_identifier="deterministic_fake",
                model_identifier=self._model_identifier,
                prompt_version=self._prompt_version,
                reason="Deterministic fake output failed request validation.",
            )
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier="deterministic_fake",
            model_identifier=self._model_identifier,
            prompt_version=self._prompt_version,
            output=self._output,
        )


class InvalidLLMAdapter:
    def __init__(
        self,
        model_identifier: str = "invalid-llm-fake",
        prompt_version: str = "l3-evidence-rubric-v1",
    ) -> None:
        self._model_identifier = model_identifier
        self._prompt_version = prompt_version

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        return LLMProviderResult(
            status=LLMProviderStatus.INVALID,
            provider_identifier="invalid_fake",
            model_identifier=self._model_identifier,
            prompt_version=self._prompt_version,
            reason="Provider returned invalid structured output.",
        )


class UnavailableLLMAdapter:
    def __init__(
        self,
        model_identifier: str = "unavailable-llm-fake",
        prompt_version: str = "l3-evidence-rubric-v1",
    ) -> None:
        self._model_identifier = model_identifier
        self._prompt_version = prompt_version

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        return LLMProviderResult(
            status=LLMProviderStatus.UNAVAILABLE,
            provider_identifier="unavailable_fake",
            model_identifier=self._model_identifier,
            prompt_version=self._prompt_version,
            reason="Provider is unavailable.",
        )


class OpenAICompatibleLLMAdapter:
    def __init__(
        self,
        provider_identifier: str,
        model_identifier: str,
        api_key: str,
        base_url: str,
        prompt_version: str,
        client: httpx.AsyncClient,
        temperature: float = 0.0,
        include_temperature_parameter: bool = True,
        require_supported_parameters: bool = False,
        enable_response_healing: bool = False,
        max_completion_tokens: int | None = None,
        reasoning_effort: Literal["none", "low", "medium", "high", "xhigh"] | None = None,
        score_mapping_version: str | None = None,
    ) -> None:
        values = (
            provider_identifier.strip(),
            model_identifier.strip(),
            api_key.strip(),
            base_url.strip(),
            prompt_version.strip(),
        )
        if any(not value for value in values):
            raise LLMConfigurationError("LLM provider configuration is incomplete")
        if not 0 <= temperature <= 2:
            raise LLMConfigurationError("LLM temperature must be between 0 and 2")
        if max_completion_tokens is not None and (
            isinstance(max_completion_tokens, bool) or not 1 <= max_completion_tokens <= 128000
        ):
            raise LLMConfigurationError(
                "LLM maximum completion tokens must be between 1 and 128000"
            )
        if reasoning_effort not in {None, "none", "low", "medium", "high", "xhigh"}:
            raise LLMConfigurationError("LLM reasoning effort is unsupported")
        inferred_mapping = (
            L3_CALIBRATION_MAPPING_V2
            if values[4] == CRITERION_STATUS_PROMPT_VERSION
            else L3_CALIBRATION_MAPPING_VERSION
        )
        resolved_mapping = score_mapping_version or inferred_mapping
        if resolved_mapping not in {
            "direct-numeric-scoring-v1",
            L3_CALIBRATION_MAPPING_VERSION,
            L3_CALIBRATION_MAPPING_V2,
            L3_CALIBRATION_MAPPING_V3,
        }:
            raise LLMConfigurationError("LLM score mapping version is unsupported")
        self._provider_identifier = values[0]
        self._model_identifier = values[1]
        self._api_key = values[2]
        self._base_url = values[3].rstrip("/")
        self._prompt_version = values[4]
        self._client = client
        self._temperature = temperature
        self._include_temperature_parameter = include_temperature_parameter
        self._require_supported_parameters = require_supported_parameters
        self._enable_response_healing = enable_response_healing
        self._max_completion_tokens = max_completion_tokens
        self._reasoning_effort = reasoning_effort
        self._score_mapping_version = resolved_mapping

    @classmethod
    def from_environment(
        cls,
        models: ModelsConfigurationArtifact,
        client: httpx.AsyncClient,
        environment: Mapping[str, str] | None = None,
        base_url_environment_variable: str = "CLASSIFIER_LLM_BASE_URL",
        temperature: float = 0.0,
        include_temperature_parameter: bool = True,
        require_supported_parameters: bool = False,
        enable_response_healing: bool = False,
        max_completion_tokens: int | None = None,
        reasoning_effort: Literal["none", "low", "medium", "high", "xhigh"] | None = None,
    ) -> OpenAICompatibleLLMAdapter:
        values = os.environ if environment is None else environment
        runtime = models.llm.runtime_provider
        provider_identifier = values.get(runtime.provider_environment_variable)
        model_identifier = values.get(runtime.model_environment_variable)
        api_key = values.get(runtime.api_key_environment_variable)
        base_url = values.get(base_url_environment_variable)
        if not all((provider_identifier, model_identifier, api_key, base_url)):
            raise LLMConfigurationError("required LLM environment configuration is missing")
        return cls(
            provider_identifier=cast(str, provider_identifier),
            model_identifier=cast(str, model_identifier),
            api_key=cast(str, api_key),
            base_url=cast(str, base_url),
            prompt_version=models.llm.prompt_version,
            client=client,
            temperature=temperature,
            include_temperature_parameter=include_temperature_parameter,
            require_supported_parameters=require_supported_parameters,
            enable_response_healing=enable_response_healing,
            max_completion_tokens=max_completion_tokens,
            reasoning_effort=reasoning_effort,
            score_mapping_version=models.llm.score_mapping_version,
        )

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        if request.prompt_version != self._prompt_version:
            return self._invalid_result("L3 prompt version does not match provider configuration.")
        try:
            messages = build_l3_messages(
                request.job_profile,
                request.rubric,
                request.evidence,
                request.prompt_version,
                _domain_requirement_references(request),
            )
        except ValueError:
            return self._invalid_result("L3 prompt version is unsupported.")
        qualitative_mode = request.prompt_version in {
            ROLE_CALIBRATED_PROMPT_VERSION,
            REQUIREMENT_GUARDED_PROMPT_VERSION,
            CONFLICT_AUDITED_PROMPT_VERSION,
            AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
            CRITERION_STATUS_PROMPT_VERSION,
        }
        output_schema = (
            LLMQualitativeAssessmentOutput.model_json_schema()
            if qualitative_mode
            else LLMScoringOutput.model_json_schema()
        )
        if self._provider_identifier == "openai":
            output_schema = self._openai_structured_output_schema(output_schema, request)
        payload: dict[str, object] = {
            "model": self._model_identifier,
            "messages": list(messages),
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": (
                        "classifier_l3_role_calibration"
                        if qualitative_mode
                        else "classifier_l3_scoring"
                    ),
                    "strict": True,
                    "schema": output_schema,
                },
            },
        }
        if self._include_temperature_parameter:
            payload["temperature"] = self._temperature
        if self._require_supported_parameters:
            payload["provider"] = {"require_parameters": True}
        if self._enable_response_healing:
            payload["plugins"] = [{"id": "response-healing"}]
        if self._max_completion_tokens is not None:
            payload["max_completion_tokens"] = self._max_completion_tokens
        if self._reasoning_effort is not None:
            payload["reasoning_effort"] = self._reasoning_effort
        try:
            response = await self._client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        except httpx.HTTPError:
            return self._unavailable_result("LLM provider request failed.")
        if not response.is_success:
            return self._unavailable_result(self._http_status_reason(response))
        try:
            response_payload = cast(object, response.json())
        except (json.JSONDecodeError, UnicodeError, TypeError):
            return self._invalid_result("LLM provider response was not valid JSON.")
        response_mapping = (
            cast(dict[str, object], response_payload)
            if isinstance(response_payload, dict)
            else None
        )
        if response_mapping is not None and response_mapping.get("error") is not None:
            return self._unavailable_result(
                self._provider_error_reason(response_mapping.get("error"))
            )
        try:
            content = self._extract_content(cast(object, response_payload))
        except LLMResponseContentError as error:
            return self._invalid_result(str(error))
        try:
            output_payload = cast(object, json.loads(content))
        except (json.JSONDecodeError, UnicodeError, TypeError):
            try:
                if qualitative_mode:
                    LLMQualitativeAssessmentOutput.model_validate_json(content)
                else:
                    LLMScoringOutput.model_validate_json(content)
            except ValidationError as error:
                return self._invalid_result(self._schema_validation_reason(error))
            return self._invalid_result("LLM provider output failed schema validation.")
        if self._provider_identifier == "openai" and not qualitative_mode:
            output_payload = self._normalize_redundant_overall_score(output_payload)
        output: LLMScoringOutput | None = None
        qualitative_output: LLMQualitativeAssessmentOutput | None = None
        try:
            if qualitative_mode:
                qualitative_output = LLMQualitativeAssessmentOutput.model_validate(output_payload)
                qualitative_output = _apply_authoritative_requirements(
                    request,
                    qualitative_output,
                )
            else:
                output = LLMScoringOutput.model_validate(output_payload)
        except ValidationError as error:
            return self._invalid_result(self._schema_validation_reason(error))
        try:
            if qualitative_mode:
                if qualitative_output is None:
                    raise LLMOutputValidationError("qualitative LLM output was not available")
                output = calibrated_scoring_output(
                    request,
                    qualitative_output,
                    self._score_mapping_version,
                )
            if output is None:
                raise LLMOutputValidationError("scored LLM output was not available")
            validate_output_against_request(request, output)
        except (LLMOutputValidationError, ValueError) as error:
            return self._invalid_result(
                f"LLM provider output failed request consistency validation: {error}."
            )
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier=self._provider_identifier,
            model_identifier=self._model_identifier,
            prompt_version=self._prompt_version,
            output=output,
            usage=self._extract_usage(cast(object, response_payload)),
            calibration_levels=(
                {
                    item.criterion_id: item.calibration_level
                    for item in qualitative_output.criterion_assessments
                }
                if qualitative_output is not None
                else None
            ),
        )

    @staticmethod
    def _extract_content(payload: object) -> str:
        if not isinstance(payload, dict):
            raise LLMResponseContentError("LLM provider response envelope was not an object.")
        payload_mapping = cast(dict[str, object], payload)
        choices = payload_mapping.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LLMResponseContentError("LLM provider response choices were missing or empty.")
        choice = cast(list[object], choices)[0]
        if not isinstance(choice, dict):
            raise LLMResponseContentError("LLM provider response choice was not an object.")
        choice_mapping = cast(dict[str, object], choice)
        message = choice_mapping.get("message")
        if not isinstance(message, dict):
            raise LLMResponseContentError("LLM provider response message was missing.")
        message_mapping = cast(dict[str, object], message)
        content = message_mapping.get("content")
        if not isinstance(content, str):
            markers = tuple(
                name
                for name, value in (
                    ("reasoning", message_mapping.get("reasoning")),
                    ("refusal", message_mapping.get("refusal")),
                    ("finish_reason", choice_mapping.get("finish_reason")),
                )
                if value is not None
            )
            marker_text = ", ".join(markers) if markers else "no diagnostic marker"
            raise LLMResponseContentError(
                f"LLM provider response content was not text ({marker_text})."
            )
        if not content.strip():
            raise LLMResponseContentError("LLM provider response content was empty text.")
        return content

    @staticmethod
    def _schema_validation_reason(error: ValidationError) -> str:
        violations: list[str] = []
        safe_value_error_categories = {
            "Value error, LLM requirement assessments must be unique": (
                "duplicate_requirement_assessments"
            ),
            "Value error, LLM criterion assessments must be unique": (
                "duplicate_criterion_assessments"
            ),
            "Value error, LLM overall score must equal the criterion score sum": (
                "criterion_sum_mismatch"
            ),
            "Value error, satisfied and unsatisfied LLM assessments require evidence": (
                "criterion_status_without_evidence"
            ),
            "Value error, missing LLM assessments must not invent evidence": (
                "missing_criterion_with_evidence"
            ),
            "Value error, conflicting LLM assessments require at least two evidence records": (
                "conflicting_criterion_without_two_evidence_records"
            ),
            "Value error, satisfied and unsatisfied LLM requirements require evidence": (
                "requirement_status_without_evidence"
            ),
            "Value error, missing LLM requirements must not invent evidence": (
                "missing_requirement_with_evidence"
            ),
            "Value error, conflicting LLM requirements require at least two evidence records": (
                "conflicting_requirement_without_two_evidence_records"
            ),
        }
        for detail in error.errors(
            include_url=False,
            include_context=False,
            include_input=False,
        )[:5]:
            location = ".".join(str(part) for part in detail["loc"]) or "root"
            category = safe_value_error_categories.get(detail.get("msg"), detail["type"])
            violations.append(f"{location}:{category}")
        summary = ", ".join(violations) or "unknown"
        return f"LLM provider output failed schema validation: {summary}."

    @staticmethod
    def _normalize_redundant_overall_score(payload: object) -> object:
        if not isinstance(payload, dict):
            return payload
        mapping = cast(dict[str, object], payload)
        overall_score = mapping.get("overall_score")
        criteria = mapping.get("criterion_assessments")
        if (
            isinstance(overall_score, bool)
            or not isinstance(overall_score, (Decimal, float, int))
            or not isinstance(criteria, list)
            or not criteria
        ):
            return mapping
        scores: list[Decimal] = []
        for criterion in cast(list[object], criteria):
            if not isinstance(criterion, dict):
                return mapping
            score = cast(dict[str, object], criterion).get("score")
            if isinstance(score, bool) or not isinstance(score, (Decimal, float, int)):
                return mapping
            scores.append(Decimal(str(score)))
        criterion_sum = sum(scores, start=Decimal("0"))
        if not Decimal("0") <= criterion_sum <= Decimal("100"):
            return mapping
        normalized = dict(mapping)
        normalized["overall_score"] = criterion_sum
        return normalized

    @staticmethod
    def _openai_structured_output_schema(
        schema: dict[str, object],
        request: LLMScoringRequest,
    ) -> dict[str, object]:
        def normalize(value: object) -> object:
            if isinstance(value, list):
                items = cast(list[object], value)
                return [normalize(item) for item in items]
            if not isinstance(value, dict):
                return value
            mapping = cast(dict[str, object], value)
            any_of = mapping.get("anyOf")
            if isinstance(any_of, list):
                branches = cast(list[object], any_of)
                numeric: list[dict[str, object]] = []
                text: list[dict[str, object]] = []
                for branch in branches:
                    if not isinstance(branch, dict):
                        continue
                    branch_mapping = cast(dict[str, object], branch)
                    if branch_mapping.get("type") == "number":
                        numeric.append(branch_mapping)
                    if branch_mapping.get("type") == "string":
                        text.append(branch_mapping)
                if len(branches) == 2 and len(numeric) == 1 and len(text) == 1:
                    return normalize(numeric[0])
            normalized: dict[str, object] = {
                key: normalize(item)
                for key, item in mapping.items()
                if key not in {"default", "title"}
            }
            properties = normalized.get("properties")
            if normalized.get("type") == "object" and isinstance(properties, dict):
                normalized["required"] = list(cast(dict[str, object], properties))
                normalized["additionalProperties"] = False
            return normalized

        normalized_schema = normalize(schema)
        if not isinstance(normalized_schema, dict):
            raise TypeError("OpenAI structured output schema must remain an object")
        root = cast(dict[str, object], normalized_schema)
        properties = cast(dict[str, object], root["properties"])
        requirements = cast(dict[str, object], properties["requirement_assessments"])
        criteria = cast(dict[str, object], properties["criterion_assessments"])
        requirement_ids = tuple(request.rubric.critical_requirement_ids)
        criterion_ids = tuple(item.criterion_id for item in request.rubric.criteria)
        evidence_ids = tuple(item.evidence_id for item in request.evidence)
        requirements["minItems"] = len(requirement_ids)
        requirements["maxItems"] = len(requirement_ids)
        criteria["minItems"] = len(criterion_ids)
        criteria["maxItems"] = len(criterion_ids)
        definitions = cast(dict[str, object], root["$defs"])
        requirement_definition = cast(dict[str, object], definitions["LLMRequirementAssessment"])
        criterion_definition_name = (
            "LLMQualitativeCriterionAssessment"
            if "LLMQualitativeCriterionAssessment" in definitions
            else "LLMWeightedCriterionAssessment"
        )
        criterion_definition = cast(dict[str, object], definitions[criterion_definition_name])
        definitions["LLMRequirementAssessment"] = (
            OpenAICompatibleLLMAdapter._openai_assessment_schema(
                requirement_definition,
                "requirement_id",
                requirement_ids,
                evidence_ids,
            )
        )
        definitions[criterion_definition_name] = (
            OpenAICompatibleLLMAdapter._openai_assessment_schema(
                criterion_definition,
                "criterion_id",
                criterion_ids,
                evidence_ids,
            )
        )
        return root

    @staticmethod
    def _openai_assessment_schema(
        base_definition: dict[str, object],
        identifier_field: Literal["requirement_id", "criterion_id"],
        allowed_identifiers: tuple[str, ...],
        allowed_evidence_ids: tuple[str, ...],
    ) -> dict[str, object]:
        variants: list[dict[str, object]] = []
        status_limits = (
            (EvidenceStatus.SATISFIED, 1, len(allowed_evidence_ids)),
            (EvidenceStatus.UNSATISFIED, 1, len(allowed_evidence_ids)),
            (EvidenceStatus.MISSING, 0, 0),
            (EvidenceStatus.CONFLICTING, 2, len(allowed_evidence_ids)),
        )
        for status, minimum, maximum in status_limits:
            if minimum > maximum:
                continue
            variant = deepcopy(base_definition)
            properties = cast(dict[str, object], variant["properties"])
            identifier = cast(dict[str, object], properties[identifier_field])
            identifier["enum"] = list(allowed_identifiers)
            properties["evidence_status"] = {
                "type": "string",
                "enum": [status.value],
            }
            evidence_ids = cast(dict[str, object], properties["evidence_ids"])
            evidence_ids["minItems"] = minimum
            evidence_ids["maxItems"] = maximum
            evidence_items = cast(dict[str, object], evidence_ids["items"])
            evidence_items["enum"] = list(allowed_evidence_ids)
            variants.append(variant)
        return {"anyOf": variants}

    @staticmethod
    def _http_status_reason(response: httpx.Response) -> str:
        reason = f"LLM provider returned HTTP status {response.status_code}."
        retry_after = response.headers.get("Retry-After")
        if response.status_code == 429 and retry_after is not None and retry_after.isdigit():
            reason = f"LLM provider returned HTTP status 429; retry after {retry_after} seconds."
        try:
            payload = cast(object, response.json())
        except (json.JSONDecodeError, UnicodeError, TypeError):
            return reason
        if not isinstance(payload, dict):
            return reason
        error = cast(dict[str, object], payload).get("error")
        if not isinstance(error, dict):
            return reason
        error_mapping = cast(dict[str, object], error)
        diagnostics: list[str] = []
        for field_name in ("type", "code"):
            value = error_mapping.get(field_name)
            if isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9_.-]{1,64}", value):
                diagnostics.append(f"{field_name}={value}")
        parameter = error_mapping.get("param")
        allowed_parameters = {
            "messages",
            "model",
            "response_format",
            "max_completion_tokens",
            "reasoning_effort",
        }
        if isinstance(parameter, str) and parameter in allowed_parameters:
            diagnostics.append(f"param={parameter}")
        if diagnostics:
            return (
                f"LLM provider returned HTTP status {response.status_code} "
                f"({', '.join(diagnostics)})."
            )
        return reason

    @staticmethod
    def _provider_error_reason(error: object) -> str:
        if not isinstance(error, dict):
            return "LLM provider response contained an error object."
        error_mapping = cast(dict[str, object], error)
        message = error_mapping.get("message")
        normalized_message = message.casefold() if isinstance(message, str) else ""
        category = "upstream_error"
        if "no endpoint" in normalized_message or "no provider" in normalized_message:
            category = "no_matching_endpoint"
        elif "data policy" in normalized_message or "privacy" in normalized_message:
            category = "data_policy_restriction"
        elif "rate limit" in normalized_message or "too many request" in normalized_message:
            category = "rate_limited"
        elif "credit" in normalized_message or "payment" in normalized_message:
            category = "insufficient_credits"
        elif "timeout" in normalized_message or "timed out" in normalized_message:
            category = "provider_timeout"
        code = error_mapping.get("code")
        code_detail = (
            f", code {code}"
            if isinstance(code, int) and not isinstance(code, bool) and 100 <= code <= 599
            else ""
        )
        if category == "upstream_error" and not code_detail:
            return "LLM provider response contained an error object."
        return f"LLM provider response contained an error object ({category}{code_detail})."

    @staticmethod
    def _extract_usage(payload: object) -> LLMProviderUsage | None:
        if not isinstance(payload, dict):
            return None
        usage = cast(dict[str, object], payload).get("usage")
        if not isinstance(usage, dict):
            return None
        usage_mapping = cast(dict[str, object], usage)
        input_tokens = OpenAICompatibleLLMAdapter._token_count(
            usage_mapping,
            "prompt_tokens",
            "input_tokens",
        )
        output_tokens = OpenAICompatibleLLMAdapter._token_count(
            usage_mapping,
            "completion_tokens",
            "output_tokens",
        )
        if input_tokens is None or output_tokens is None:
            return None
        total_tokens = OpenAICompatibleLLMAdapter._token_count(
            usage_mapping,
            "total_tokens",
        )
        prompt_details = usage_mapping.get("prompt_tokens_details")
        completion_details = usage_mapping.get("completion_tokens_details")
        cached_input_tokens = (
            OpenAICompatibleLLMAdapter._token_count(
                cast(dict[str, object], prompt_details),
                "cached_tokens",
            )
            if isinstance(prompt_details, dict)
            else None
        )
        reasoning_tokens = (
            OpenAICompatibleLLMAdapter._token_count(
                cast(dict[str, object], completion_details),
                "reasoning_tokens",
            )
            if isinstance(completion_details, dict)
            else None
        )
        try:
            return LLMProviderUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=(
                    total_tokens if total_tokens is not None else input_tokens + output_tokens
                ),
                cached_input_tokens=cached_input_tokens or 0,
                reasoning_tokens=reasoning_tokens or 0,
            )
        except ValidationError:
            return None

    @staticmethod
    def _token_count(
        mapping: Mapping[str, object],
        *field_names: str,
    ) -> int | None:
        for field_name in field_names:
            value = mapping.get(field_name)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                return value
        return None

    def _invalid_result(self, reason: str) -> LLMProviderResult:
        return LLMProviderResult(
            status=LLMProviderStatus.INVALID,
            provider_identifier=self._provider_identifier,
            model_identifier=self._model_identifier,
            prompt_version=self._prompt_version,
            reason=reason,
        )

    def _unavailable_result(self, reason: str) -> LLMProviderResult:
        return LLMProviderResult(
            status=LLMProviderStatus.UNAVAILABLE,
            provider_identifier=self._provider_identifier,
            model_identifier=self._model_identifier,
            prompt_version=self._prompt_version,
            reason=reason,
        )


class CoreL3ProviderBridge:
    def __init__(self, adapter: LLMAdapter, l1_policy: L1Policy | None = None) -> None:
        self._adapter = adapter
        self._l1_policy = l1_policy

    async def evaluate(self, request: L3ProviderRequest) -> object:
        digest = sha256(request.cv_profile.cv_profile_id.encode("utf-8")).hexdigest()[:16]
        authoritative_requirements: tuple[LLMRequirementReference, ...] = ()
        if request.prompt_version in {
            AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
            CRITERION_STATUS_PROMPT_VERSION,
        }:
            if self._l1_policy is None:
                raise RuntimeError("authoritative L3 prompt requires an L1 policy")
            l1 = score_l1(request.cv_profile, request.rubric, self._l1_policy)
            authoritative_requirements = tuple(
                LLMRequirementReference(
                    requirement_id=item.requirement_id,
                    evidence_status=item.evidence_status,
                    evidence_ids=item.evidence_ids,
                    rationale=item.rationale,
                )
                for item in l1.requirement_assessments
            )
        provider_request = LLMScoringRequest(
            request_id=f"l3-{digest}",
            job_profile=request.job_profile,
            rubric=request.rubric,
            evidence=request.cv_profile.evidence,
            prompt_version=request.prompt_version,
            authoritative_requirement_assessments=authoritative_requirements,
        )
        result = await self._adapter.score(provider_request)
        if result.status is LLMProviderStatus.UNAVAILABLE:
            raise RuntimeError("L3 provider is unavailable")
        if result.status is LLMProviderStatus.INVALID or result.output is None:
            return {"provider_status": "invalid"}
        return result.output.model_dump(mode="python")


class DeterministicCoreL3Provider:
    def __init__(
        self,
        l1_policy: L1Policy,
        prompt_version: str = PROMPT_VERSION,
        evidence_per_criterion: int = 2,
        expected_section_count: int = 4,
    ) -> None:
        if evidence_per_criterion < 1 or expected_section_count < 1:
            raise ValueError("deterministic L3 density settings must be positive")
        if not prompt_version.strip():
            raise ValueError("deterministic L3 prompt version must be non-empty")
        self._l1_policy = l1_policy
        self._prompt_version = prompt_version.strip()
        self._evidence_per_criterion = evidence_per_criterion
        self._expected_section_count = expected_section_count

    async def evaluate(self, request: L3ProviderRequest) -> object:
        if request.prompt_version != self._prompt_version:
            return {"provider_status": "invalid"}
        l1_assessment = score_l1(
            request.cv_profile,
            request.rubric,
            self._l1_policy,
        )
        evidence = tuple(sorted(request.cv_profile.evidence, key=lambda item: item.evidence_id))
        evidence_ids = tuple(item.evidence_id for item in evidence)
        section_count = len({item.section for item in evidence})
        evidence_target = max(
            1,
            len(request.rubric.criteria) * self._evidence_per_criterion,
        )
        density = min(
            Decimal("1"),
            Decimal(len(evidence)) / Decimal(evidence_target),
        )
        section_coverage = min(
            Decimal("1"),
            Decimal(section_count) / Decimal(self._expected_section_count),
        )
        coverage = (density * Decimal("0.70") + section_coverage * Decimal("0.30")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        criteria = tuple(
            {
                "criterion_id": criterion.criterion_id,
                "score": (criterion.weight * coverage).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
                "evidence_status": EvidenceStatus.SATISFIED,
                "evidence_ids": evidence_ids,
                "rationale": (
                    f"Chế độ L3 offline mô phỏng tiêu chí “{criterion.title}”: "
                    f"{criterion.description} Điểm được tính từ {len(evidence)} mục thông tin "
                    f"trong {section_count} phần CV, với độ phủ {coverage * Decimal('100')}%. "
                    "Đây là phép tính theo quy tắc, không phải nhận định của LLM."
                ),
            }
            for criterion in request.rubric.criteria
        )
        overall_score = sum(
            (cast(Decimal, criterion["score"]) for criterion in criteria),
            Decimal("0"),
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        requirements = tuple(
            {
                "requirement_id": assessment.requirement_id,
                "evidence_status": assessment.evidence_status,
                "evidence_ids": assessment.evidence_ids,
                "rationale": assessment.rationale,
            }
            for assessment in l1_assessment.requirement_assessments
        )
        return {
            "requirement_assessments": requirements,
            "criterion_assessments": criteria,
            "overall_score": overall_score,
            "strengths": ("Thông tin trong CV đã được xử lý bằng quy tắc offline xác định.",),
            "risks": (
                "Điểm L3 offline chỉ mô phỏng độ phủ thông tin, không đánh giá chiều sâu như LLM.",
            ),
            "warnings": ("Đang dùng L3 mô phỏng; không có request nào được gửi tới LLM.",),
            "confidence": coverage,
        }


class InvalidCoreL3Provider:
    async def evaluate(self, request: L3ProviderRequest) -> object:
        return {"provider_status": "invalid"}


class UnavailableCoreL3Provider:
    async def evaluate(self, request: L3ProviderRequest) -> object:
        raise RuntimeError("L3 provider is unavailable")

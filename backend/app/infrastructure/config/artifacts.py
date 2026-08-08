from __future__ import annotations

import re
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import (
    AggregationWeights,
    ClassificationConfig,
    DecisionThresholds,
    EvidenceSection,
    EvidenceStatus,
    ExperienceRange,
    JobProfile,
    JobRequirement,
    ModelMetadata,
    NeedsReviewPolicy,
    RequirementPriority,
    ReviewBand,
    RubricCriterion,
    ScoringRubric,
    SeniorityLevel,
)
from backend.app.domain import L2ScoringMode

NonEmptyArtifactText = Annotated[str, Field(min_length=1, max_length=8000)]
ArtifactVersion = Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+$")]


class ArtifactModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ScoreScaleArtifact(ArtifactModel):
    minimum: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    maximum: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))

    @model_validator(mode="after")
    def validate_scale(self) -> Self:
        if self.minimum != Decimal("0") or self.maximum != Decimal("100"):
            raise ValueError("classifier artifact score scale must be 0 to 100")
        return self


class ExperienceRangeArtifact(ArtifactModel):
    minimum: int = Field(ge=0, le=40)
    maximum: int = Field(ge=0, le=40)

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.maximum < self.minimum:
            raise ValueError("experience maximum must not be lower than minimum")
        return self


class SeniorityArtifact(ArtifactModel):
    level: SeniorityLevel
    experience_range_years: ExperienceRangeArtifact
    formal_work_experience_required: bool
    equivalent_experience: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]


class MandatoryRequirementArtifact(ArtifactModel):
    requirement_id: str
    description: NonEmptyArtifactText
    accepted_evidence: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]
    missing_evidence_policy: NonEmptyArtifactText
    explicit_failure_policy: NonEmptyArtifactText


class PreferredRequirementArtifact(ArtifactModel):
    requirement_id: str
    description: NonEmptyArtifactText
    accepted_evidence: tuple[NonEmptyArtifactText, ...] = ()
    missing_evidence_policy: NonEmptyArtifactText = (
        "Missing preferred information is not unsatisfied."
    )
    explicit_failure_policy: NonEmptyArtifactText = (
        "Preferred requirements do not establish critical failure."
    )


class JobArtifactLinks(ArtifactModel):
    rubric_id: str
    rubric_version: ArtifactVersion
    scoring_configuration_version: ArtifactVersion
    models_configuration_version: ArtifactVersion


class JobProfileArtifact(ArtifactModel):
    artifact_kind: Literal["job_profile_draft", "job_profile"]
    artifact_version: ArtifactVersion
    contract_status: Literal["approved_for_pilot", "approved_for_runtime"]
    job_profile_id: str
    title: NonEmptyArtifactText
    language: NonEmptyArtifactText
    seniority: SeniorityArtifact
    role_summary: NonEmptyArtifactText
    responsibilities: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]
    mandatory_requirements: Annotated[tuple[MandatoryRequirementArtifact, ...], Field(min_length=1)]
    preferred_requirements: tuple[PreferredRequirementArtifact, ...]
    scoring_exclusions: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]
    artifact_links: JobArtifactLinks

    @model_validator(mode="after")
    def validate_requirement_identifiers(self) -> Self:
        identifiers = tuple(
            requirement.requirement_id
            for requirement in (*self.mandatory_requirements, *self.preferred_requirements)
        )
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("job artifact requirement identifiers must be unique")
        return self

    def to_contract(self) -> JobProfile:
        required = tuple(
            JobRequirement(
                requirement_id=requirement.requirement_id,
                title=requirement.description,
                description=requirement.description,
                priority=RequirementPriority.REQUIRED,
                is_critical=True,
                accepted_evidence=requirement.accepted_evidence,
                missing_evidence_policy=requirement.missing_evidence_policy,
                explicit_failure_policy=requirement.explicit_failure_policy,
            )
            for requirement in self.mandatory_requirements
        )
        preferred = tuple(
            JobRequirement(
                requirement_id=requirement.requirement_id,
                title=requirement.description,
                description=requirement.description,
                priority=RequirementPriority.PREFERRED,
                is_critical=False,
                accepted_evidence=(requirement.accepted_evidence or (requirement.description,)),
                missing_evidence_policy=requirement.missing_evidence_policy,
                explicit_failure_policy=requirement.explicit_failure_policy,
            )
            for requirement in self.preferred_requirements
        )
        return JobProfile(
            job_profile_id=self.job_profile_id,
            title=self.title,
            language=self.language,
            seniority=self.seniority.level,
            experience_range=ExperienceRange(
                minimum_years=self.seniority.experience_range_years.minimum,
                maximum_years=self.seniority.experience_range_years.maximum,
                formal_work_experience_required=self.seniority.formal_work_experience_required,
            ),
            responsibilities=self.responsibilities,
            requirements=required + preferred,
        )


class RubricCriterionArtifact(ArtifactModel):
    criterion_id: str
    title: NonEmptyArtifactText | None = None
    weight: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    description: NonEmptyArtifactText
    evaluation_signals: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]
    missing_evidence_handling: NonEmptyArtifactText


class RubricArtifactLinks(ArtifactModel):
    job_profile_artifact_version: ArtifactVersion
    scoring_configuration_version: ArtifactVersion
    models_configuration_version: ArtifactVersion


class ScoringRubricArtifact(ArtifactModel):
    artifact_kind: Literal["scoring_rubric_draft", "scoring_rubric"]
    rubric_id: str
    rubric_version: ArtifactVersion
    contract_status: Literal["approved_for_pilot", "approved_for_runtime"]
    job_profile_id: str
    score_scale: ScoreScaleArtifact
    criteria: Annotated[tuple[RubricCriterionArtifact, ...], Field(min_length=1)]
    critical_requirement_ids: Annotated[tuple[str, ...], Field(min_length=1)]
    artifact_links: RubricArtifactLinks

    @model_validator(mode="after")
    def validate_rubric(self) -> Self:
        criterion_ids = tuple(criterion.criterion_id for criterion in self.criteria)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("rubric artifact criterion identifiers must be unique")
        if sum(criterion.weight for criterion in self.criteria) != Decimal("100"):
            raise ValueError("rubric artifact criterion weights must total 100")
        if len(self.critical_requirement_ids) != len(set(self.critical_requirement_ids)):
            raise ValueError("rubric artifact critical requirement identifiers must be unique")
        return self

    def to_contract(self) -> ScoringRubric:
        return ScoringRubric(
            rubric_id=self.rubric_id,
            rubric_version=self.rubric_version,
            job_profile_id=self.job_profile_id,
            criteria=tuple(
                RubricCriterion(
                    criterion_id=criterion.criterion_id,
                    title=criterion.title or criterion.description,
                    description=criterion.description,
                    weight=criterion.weight,
                )
                for criterion in self.criteria
            ),
            critical_requirement_ids=self.critical_requirement_ids,
        )


class LevelWeightsArtifact(ArtifactModel):
    l1_deterministic_rules: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    l2_section_semantic_matching: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    l3_evidence_grounded_reasoning: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))


class AggregationArtifact(ArtifactModel):
    level_weights: LevelWeightsArtifact
    required_weight_total: Decimal = Field(gt=Decimal("0"), le=Decimal("1"))
    output_rounding_decimal_places: int = Field(ge=0, le=6)

    @model_validator(mode="after")
    def validate_weights(self) -> Self:
        weights = self.level_weights
        total = (
            weights.l1_deterministic_rules
            + weights.l2_section_semantic_matching
            + weights.l3_evidence_grounded_reasoning
        )
        if total != self.required_weight_total or total != Decimal("1"):
            raise ValueError("configured level weights must total 1")
        return self


class DecisionThresholdArtifact(ArtifactModel):
    pass_minimum: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    waitlist_minimum: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    reject_maximum_exclusive: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))

    @model_validator(mode="after")
    def validate_thresholds(self) -> Self:
        if self.waitlist_minimum >= self.pass_minimum:
            raise ValueError("waitlist threshold must be lower than pass threshold")
        if self.reject_maximum_exclusive != self.waitlist_minimum:
            raise ValueError("reject maximum must equal waitlist minimum")
        return self


class RejectConditionsArtifact(ArtifactModel):
    require_final_score_below: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    require_explicit_unsatisfied_critical_requirement: Literal[True]
    missing_critical_evidence_allows_reject: Literal[False]
    conflicting_critical_evidence_allows_reject: Literal[False]


class NeedsReviewRuleArtifact(ArtifactModel):
    rule_id: str
    condition: NonEmptyArtifactText


class DecisionPolicyArtifact(ArtifactModel):
    precedence: tuple[Literal["needs_review", "pass", "waitlist", "reject"], ...]
    thresholds: DecisionThresholdArtifact
    reject_conditions: RejectConditionsArtifact
    needs_review_rules: Annotated[tuple[NeedsReviewRuleArtifact, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        if self.precedence != ("needs_review", "pass", "waitlist", "reject"):
            raise ValueError("decision precedence must protect needs_review")
        if (
            self.reject_conditions.require_final_score_below
            != self.thresholds.reject_maximum_exclusive
        ):
            raise ValueError("reject condition threshold must match decision thresholds")
        rule_ids = tuple(rule.rule_id for rule in self.needs_review_rules)
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("needs review rule identifiers must be unique")
        required_rule_ids = {
            "missing-critical-evidence",
            "conflicting-critical-evidence",
            "low-score-without-explicit-critical-unsatisfied",
            "critical-unsatisfied-at-or-above-waitlist-threshold",
            "invalid-provider-output",
            "large-level-disagreement",
            "lower-threshold-boundary",
            "upper-threshold-boundary",
        }
        if set(rule_ids) != required_rule_ids:
            raise ValueError("needs review rules must match scoring configuration 1.1.0")
        return self


class EvidencePolicyArtifact(ArtifactModel):
    statuses: tuple[EvidenceStatus, ...]
    missing_is_unsatisfied: Literal[False]
    infer_unstated_skills: Literal[False]
    accept_academic_or_personal_projects_for_junior_roles: Literal[True]

    @model_validator(mode="after")
    def validate_statuses(self) -> Self:
        if set(self.statuses) != set(EvidenceStatus):
            raise ValueError("evidence policy must declare every supported evidence status")
        return self


class SemanticMatchingArtifact(ArtifactModel):
    matching_scope: tuple[Literal["skills", "experience", "projects", "education"], ...]
    whole_cv_embedding_allowed: Literal[False]
    score_interpretation: NonEmptyArtifactText

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if len(self.matching_scope) != len(set(self.matching_scope)):
            raise ValueError("semantic matching scope entries must be unique")
        return self


class ScoringArtifactLinks(ArtifactModel):
    supported_job_profile_versions: Annotated[tuple[ArtifactVersion, ...], Field(min_length=1)]
    supported_rubric_versions: Annotated[tuple[ArtifactVersion, ...], Field(min_length=1)]
    l1_rules_configuration_version: ArtifactVersion
    models_configuration_version: ArtifactVersion


class ScoringConfigurationArtifact(ArtifactModel):
    artifact_kind: Literal[
        "classification_scoring_configuration_draft",
        "classification_scoring_configuration",
    ]
    configuration_version: ArtifactVersion
    contract_status: Literal[
        "approved_for_pilot",
        "development_candidate",
        "approved_for_runtime",
    ]
    score_scale: ScoreScaleArtifact
    aggregation: AggregationArtifact
    decision_policy: DecisionPolicyArtifact
    evidence_policy: EvidencePolicyArtifact
    semantic_matching: SemanticMatchingArtifact
    artifact_links: ScoringArtifactLinks

    def _rule(self, rule_id: str) -> NeedsReviewRuleArtifact:
        return next(
            rule for rule in self.decision_policy.needs_review_rules if rule.rule_id == rule_id
        )

    def _disagreement_points(self) -> Decimal:
        condition = self._rule("large-level-disagreement").condition
        match = re.fullmatch(
            r"The maximum difference between valid L1, L2 and L3 scores is at least "
            r"(?P<points>\d+(?:\.\d+)?) points\.",
            condition,
        )
        if match is None:
            raise ValueError("large disagreement rule is not machine-readable")
        return Decimal(match.group("points"))

    def _review_band(self, rule_id: str) -> ReviewBand:
        condition = self._rule(rule_id).condition
        match = re.fullmatch(
            r"Final score is inclusively between (?P<minimum>\d+(?:\.\d+)?) and "
            r"(?P<maximum>\d+(?:\.\d+)?)\.",
            condition,
        )
        if match is None:
            raise ValueError(f"{rule_id} is not machine-readable")
        return ReviewBand(
            minimum=Decimal(match.group("minimum")),
            maximum=Decimal(match.group("maximum")),
        )

    def to_contract(
        self,
        model_metadata: ModelMetadata,
        job_profile_artifact_version: str,
        l1_rules_configuration_version: str,
        models_configuration_version: str,
    ) -> ClassificationConfig:
        weights = self.aggregation.level_weights
        thresholds = self.decision_policy.thresholds
        major_version = self.configuration_version.split(".", maxsplit=1)[0]
        return ClassificationConfig(
            configuration_id=f"classification-scoring-v{major_version}",
            configuration_version=self.configuration_version,
            job_profile_artifact_version=job_profile_artifact_version,
            l1_rules_configuration_version=l1_rules_configuration_version,
            models_configuration_version=models_configuration_version,
            aggregation=AggregationWeights(
                l1_deterministic_rules=weights.l1_deterministic_rules,
                l2_section_semantic_matching=weights.l2_section_semantic_matching,
                l3_evidence_grounded_reasoning=weights.l3_evidence_grounded_reasoning,
            ),
            thresholds=DecisionThresholds(
                pass_minimum=thresholds.pass_minimum,
                waitlist_minimum=thresholds.waitlist_minimum,
            ),
            needs_review_policy=NeedsReviewPolicy(
                missing_critical_evidence=True,
                conflicting_critical_evidence=True,
                invalid_provider_output=True,
                disagreement_points=self._disagreement_points(),
                boundary_score_bands=(
                    self._review_band("lower-threshold-boundary"),
                    self._review_band("upper-threshold-boundary"),
                ),
            ),
            models=model_metadata,
        )


class SectionWeightArtifact(ArtifactModel):
    section: EvidenceSection
    weight: Decimal = Field(gt=Decimal("0"), le=Decimal("1"))


class EmbeddingMatchingArtifact(ArtifactModel):
    candidate_id: NonEmptyArtifactText | None = None
    scoring_mode: L2ScoringMode = L2ScoringMode.TOP_K_MEAN
    top_k: int = Field(ge=1, le=100)
    similarity_floor: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))
    similarity_ceiling: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))
    minimum_query_score: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    section_weights: tuple[SectionWeightArtifact, ...] = ()
    query_profile: Literal["coverage-v1", "rubric-signals-v2", "rubric-quality-v3"] = "coverage-v1"

    @model_validator(mode="after")
    def validate_similarity_range(self) -> Self:
        if self.similarity_floor >= self.similarity_ceiling:
            raise ValueError("embedding similarity floor must be below ceiling")
        sections = tuple(item.section for item in self.section_weights)
        if len(sections) != len(set(sections)):
            raise ValueError("embedding section weights must have unique sections")
        if self.scoring_mode is L2ScoringMode.QUERY_COVERAGE:
            if self.candidate_id is None:
                raise ValueError("query coverage requires a candidate identifier")
            if self.minimum_query_score <= 0:
                raise ValueError("query coverage requires a positive minimum query score")
            if set(sections) != set(EvidenceSection):
                raise ValueError("query coverage requires every evidence section weight")
        elif self.minimum_query_score != 0 or self.section_weights:
            raise ValueError("top-k mean does not accept query coverage settings")
        return self


class L2CalibrationRoleArtifact(ArtifactModel):
    job_profile_id: NonEmptyArtifactText
    role: NonEmptyArtifactText


class L2CalibrationArtifact(ArtifactModel):
    adapter: Literal["sklearn_extra_trees"]
    candidate_id: NonEmptyArtifactText
    model_path: NonEmptyArtifactText
    model_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    semantic_candidate_id: NonEmptyArtifactText
    trained_dataset_id: NonEmptyArtifactText
    split_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    feature_roles: tuple[NonEmptyArtifactText, ...]
    job_profile_roles: tuple[L2CalibrationRoleArtifact, ...]
    criterion_maximums: tuple[Decimal, Decimal, Decimal, Decimal, Decimal]

    @model_validator(mode="after")
    def validate_calibration(self) -> Self:
        model_path = self.model_path.replace("\\", "/")
        if model_path.startswith("/") or ":" in model_path or ".." in model_path.split("/"):
            raise ValueError("L2 calibration model path must be repository-relative")
        if len(self.feature_roles) != len(set(self.feature_roles)):
            raise ValueError("L2 calibration feature roles must be unique")
        job_ids = tuple(item.job_profile_id for item in self.job_profile_roles)
        mapped_roles = tuple(item.role for item in self.job_profile_roles)
        if len(job_ids) != len(set(job_ids)):
            raise ValueError("L2 calibration job profile mappings must be unique")
        if set(mapped_roles) != set(self.feature_roles):
            raise ValueError("L2 calibration role mappings must cover feature roles")
        if self.criterion_maximums != (
            Decimal("30"),
            Decimal("25"),
            Decimal("20"),
            Decimal("15"),
            Decimal("10"),
        ):
            raise ValueError("L2 calibration criterion maximums must match the canonical rubric")
        return self


class EmbeddingModelArtifact(ArtifactModel):
    adapter: Literal["sentence_transformers"]
    model_identifier: NonEmptyArtifactText
    execution_mode: Literal["local"]
    model_version: NonEmptyArtifactText
    resolved_revision: NonEmptyArtifactText | None = None
    dimension: int = Field(ge=1, le=65535)
    query_prefix: NonEmptyArtifactText
    passage_prefix: NonEmptyArtifactText
    language_support: Literal["multilingual"]
    use_for: Literal["l2_section_semantic_matching"]
    matching: EmbeddingMatchingArtifact
    calibration: L2CalibrationArtifact | None = None

    @model_validator(mode="after")
    def validate_prefixes(self) -> Self:
        if self.query_prefix == self.passage_prefix:
            raise ValueError("embedding query and passage prefixes must differ")
        return self


class RuntimeProviderArtifact(ArtifactModel):
    adapter: Literal["environment_configured"]
    provider_environment_variable: NonEmptyArtifactText
    model_environment_variable: NonEmptyArtifactText
    api_key_environment_variable: NonEmptyArtifactText
    approved_provider_identifier: NonEmptyArtifactText | None = None
    approved_model_identifier: NonEmptyArtifactText | None = None


class DeterministicFakeArtifact(ArtifactModel):
    adapter: Literal["deterministic_fake"]
    model_identifier: NonEmptyArtifactText
    use_for: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]


class ProviderResponseHandlingArtifact(ArtifactModel):
    invalid_or_unavailable_output: Literal["route_to_needs_review"]


class LLMModelArtifact(ArtifactModel):
    use_for: Literal["l3_evidence_grounded_reasoning"]
    structured_output_required: Literal[True]
    prompt_version: NonEmptyArtifactText
    score_mapping_version: NonEmptyArtifactText = "direct-numeric-scoring-v1"
    runtime_provider: RuntimeProviderArtifact
    deterministic_fake: DeterministicFakeArtifact
    provider_response_handling: ProviderResponseHandlingArtifact

    @model_validator(mode="after")
    def validate_score_mapping(self) -> Self:
        role_calibrated_prompts = {
            "l3-evidence-rubric-v11",
            "l3-evidence-rubric-v12",
            "l3-evidence-rubric-v13",
            "l3-evidence-rubric-v14",
        }
        deterministic_mapping = "l3-deterministic-level-mapping-v1"
        if self.prompt_version == "l3-evidence-rubric-v15":
            if self.score_mapping_version not in {
                "l3-deterministic-level-mapping-v2",
                "l3-deterministic-level-mapping-v3",
            }:
                raise ValueError("criterion-status prompt requires deterministic mapping v2 or v3")
        elif self.prompt_version in role_calibrated_prompts:
            if self.score_mapping_version != deterministic_mapping:
                raise ValueError("role-calibrated prompt requires deterministic level mapping")
        elif self.score_mapping_version != "direct-numeric-scoring-v1":
            raise ValueError("numeric prompt requires direct numeric scoring mapping")
        return self


class ModelsArtifactLinks(ArtifactModel):
    scoring_configuration_version: ArtifactVersion
    supported_rubric_versions: Annotated[tuple[ArtifactVersion, ...], Field(min_length=1)]


class ModelsConfigurationArtifact(ArtifactModel):
    artifact_kind: Literal[
        "classification_models_configuration_draft",
        "classification_models_configuration",
    ]
    configuration_version: ArtifactVersion
    contract_status: Literal[
        "approved_for_pilot",
        "development_candidate",
        "approved_for_runtime",
    ]
    embedding: EmbeddingModelArtifact
    llm: LLMModelArtifact
    artifact_links: ModelsArtifactLinks

    def fake_model_metadata(self) -> ModelMetadata:
        return ModelMetadata(
            embedding_model_identifier=self.embedding.model_identifier,
            embedding_model_version=(
                self.embedding.resolved_revision or self.embedding.model_version
            ),
            llm_provider_identifier=self.llm.deterministic_fake.adapter,
            llm_model_identifier=self.llm.deterministic_fake.model_identifier,
            prompt_version=self.llm.prompt_version,
        )

    def runtime_model_metadata(
        self,
        provider_identifier: str,
        model_identifier: str,
    ) -> ModelMetadata:
        return ModelMetadata(
            embedding_model_identifier=self.embedding.model_identifier,
            embedding_model_version=(
                self.embedding.resolved_revision or self.embedding.model_version
            ),
            llm_provider_identifier=provider_identifier,
            llm_model_identifier=model_identifier,
            prompt_version=self.llm.prompt_version,
        )


class MatchMode(StrEnum):
    ANY = "any"
    ALL = "all"


class RequirementRuleArtifact(ArtifactModel):
    requirement_id: str
    evidence_sections: Annotated[tuple[EvidenceSection, ...], Field(min_length=1)]
    positive_terms: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]
    explicit_negative_terms: Annotated[tuple[NonEmptyArtifactText, ...], Field(min_length=1)]
    match_mode: MatchMode
    positive_evidence_sections: tuple[EvidenceSection, ...] = ()
    positive_term_groups: tuple[tuple[NonEmptyArtifactText, ...], ...] = ()

    @model_validator(mode="after")
    def validate_terms(self) -> Self:
        if len(self.evidence_sections) != len(set(self.evidence_sections)):
            raise ValueError("L1 evidence sections must be unique")
        normalized_positive = tuple(term.casefold() for term in self.positive_terms)
        normalized_negative = tuple(term.casefold() for term in self.explicit_negative_terms)
        if len(normalized_positive) != len(set(normalized_positive)):
            raise ValueError("L1 positive terms must be unique")
        if len(normalized_negative) != len(set(normalized_negative)):
            raise ValueError("L1 explicit negative terms must be unique")
        if len(self.positive_evidence_sections) != len(set(self.positive_evidence_sections)):
            raise ValueError("L1 positive evidence sections must be unique")
        if any(
            section not in self.evidence_sections for section in self.positive_evidence_sections
        ):
            raise ValueError("L1 positive evidence sections must reference evidence sections")
        normalized_groups: set[tuple[str, ...]] = set()
        for group in self.positive_term_groups:
            if not group:
                raise ValueError("L1 positive term groups must not contain empty groups")
            normalized_group = tuple(term.casefold() for term in group)
            if len(normalized_group) != len(set(normalized_group)):
                raise ValueError("L1 positive term group terms must be unique")
            if not set(normalized_group).issubset(normalized_positive):
                raise ValueError("L1 positive term groups must reference positive terms")
            normalized_groups.add(normalized_group)
        if len(normalized_groups) != len(self.positive_term_groups):
            raise ValueError("L1 positive term groups must be unique")
        return self


class L1PolicyArtifact(ArtifactModel):
    job_profile_id: str
    rules: Annotated[tuple[RequirementRuleArtifact, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_rules(self) -> Self:
        requirement_ids = tuple(rule.requirement_id for rule in self.rules)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("L1 requirement rules must be unique")
        return self


class L1RulesConfigurationArtifact(ArtifactModel):
    artifact_kind: Literal["l1_requirement_matching_rules"]
    configuration_version: ArtifactVersion
    contract_status: Literal["stage4_initial", "development_candidate", "approved_for_runtime"]
    policies: Annotated[tuple[L1PolicyArtifact, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_policies(self) -> Self:
        job_profile_ids = tuple(policy.job_profile_id for policy in self.policies)
        if len(job_profile_ids) != len(set(job_profile_ids)):
            raise ValueError("L1 policies must have unique job profile identifiers")
        return self

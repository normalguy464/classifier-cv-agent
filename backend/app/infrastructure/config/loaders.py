from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, TypeVar, cast

import yaml
from pydantic import BaseModel, ValidationError

from backend.app.contracts import ClassificationConfig, EvidenceSection, JobProfile, ScoringRubric
from backend.app.agents.classifier.scoring.l2_policy import (
    L2CoverageConfiguration,
    build_query_coverage_l2_policy,
)
from backend.app.domain import (
    BoundaryRule,
    L1Policy,
    L2CriterionPolicy,
    L2Policy,
    L2ScoringMode,
    MatchMode as DomainMatchMode,
    RequirementRule,
    RoutingPolicy,
)
from backend.app.infrastructure.config.artifacts import (
    JobProfileArtifact,
    L1PolicyArtifact,
    L1RulesConfigurationArtifact,
    ModelsConfigurationArtifact,
    ScoringConfigurationArtifact,
    ScoringRubricArtifact,
)
from backend.app.infrastructure.config.runtime_manifest import (
    RuntimeConfigurationManifest,
    RuntimeManifestError,
    load_runtime_manifest,
)

ArtifactType = TypeVar("ArtifactType", bound=BaseModel)


class ConfigurationLoadError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedClassifierConfiguration:
    job_profile: JobProfile
    rubric: ScoringRubric
    classification_config: ClassificationConfig
    job_artifact: JobProfileArtifact
    rubric_artifact: ScoringRubricArtifact
    scoring_artifact: ScoringConfigurationArtifact
    models_artifact: ModelsConfigurationArtifact
    l1_rules_artifact: L1RulesConfigurationArtifact


SEMANTIC_SCOPE_SECTIONS: Mapping[str, EvidenceSection] = {
    "skills": EvidenceSection.SKILLS,
    "experience": EvidenceSection.WORK_EXPERIENCE,
    "projects": EvidenceSection.PROJECTS,
    "education": EvidenceSection.EDUCATION,
}


def build_l1_policy(artifact: L1PolicyArtifact) -> L1Policy:
    return L1Policy(
        job_profile_id=artifact.job_profile_id,
        rules=tuple(
            RequirementRule(
                requirement_id=rule.requirement_id,
                evidence_sections=rule.evidence_sections,
                positive_terms=rule.positive_terms,
                explicit_negative_terms=rule.explicit_negative_terms,
                match_mode=DomainMatchMode(rule.match_mode.value),
                positive_evidence_sections=rule.positive_evidence_sections,
                positive_term_groups=rule.positive_term_groups,
            )
            for rule in artifact.rules
        ),
    )


def build_l2_policy(loaded: LoadedClassifierConfiguration) -> L2Policy:
    embedding = loaded.models_artifact.embedding
    matching = embedding.matching
    if matching.scoring_mode is L2ScoringMode.QUERY_COVERAGE:
        return build_query_coverage_l2_policy(
            loaded.job_profile,
            loaded.rubric,
            L2CoverageConfiguration(
                similarity_floor=matching.similarity_floor,
                similarity_ceiling=matching.similarity_ceiling,
                top_k=matching.top_k,
                minimum_query_score=matching.minimum_query_score,
                section_weights=tuple(
                    (item.section, item.weight) for item in matching.section_weights
                ),
                query_profile=matching.query_profile,
            ),
        )
    evidence_sections = tuple(
        SEMANTIC_SCOPE_SECTIONS[item]
        for item in loaded.scoring_artifact.semantic_matching.matching_scope
    )
    criteria = tuple(
        L2CriterionPolicy(
            criterion_id=criterion.criterion_id,
            query_text=" ".join((criterion.description, *criterion.evaluation_signals)),
            evidence_sections=evidence_sections,
            similarity_floor=embedding.matching.similarity_floor,
            similarity_ceiling=embedding.matching.similarity_ceiling,
            top_k=embedding.matching.top_k,
        )
        for criterion in loaded.rubric_artifact.criteria
    )
    return L2Policy(job_profile_id=loaded.job_profile.job_profile_id, criteria=criteria)


def build_routing_policy(loaded: LoadedClassifierConfiguration) -> RoutingPolicy:
    scoring = loaded.scoring_artifact
    public_policy = loaded.classification_config.needs_review_policy
    rule_ids = {rule.rule_id for rule in scoring.decision_policy.needs_review_rules}
    boundary_ids = ("lower-threshold-boundary", "upper-threshold-boundary")
    bands = public_policy.boundary_score_bands
    return RoutingPolicy(
        pass_minimum=loaded.classification_config.thresholds.pass_minimum,
        waitlist_minimum=loaded.classification_config.thresholds.waitlist_minimum,
        missing_critical_evidence=public_policy.missing_critical_evidence,
        conflicting_critical_evidence=public_policy.conflicting_critical_evidence,
        invalid_provider_output=public_policy.invalid_provider_output,
        disagreement_points=public_policy.disagreement_points,
        boundary_rules=tuple(
            BoundaryRule(rule_id=rule_id, minimum=band.minimum, maximum=band.maximum)
            for rule_id, band in zip(boundary_ids, bands, strict=True)
        ),
        low_score_without_explicit_critical_unsatisfied=(
            "low-score-without-explicit-critical-unsatisfied" in rule_ids
        ),
        critical_unsatisfied_at_or_above_waitlist_threshold=(
            "critical-unsatisfied-at-or-above-waitlist-threshold" in rule_ids
        ),
        reject_requires_explicit_unsatisfied_critical=(
            scoring.decision_policy.reject_conditions.require_explicit_unsatisfied_critical_requirement
        ),
    )


def load_yaml_artifact(path: Path, artifact_type: type[ArtifactType]) -> ArtifactType:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ConfigurationLoadError(f"cannot load configuration artifact: {path.name}") from error
    if not isinstance(payload, dict):
        raise ConfigurationLoadError(f"configuration artifact must be a mapping: {path.name}")
    try:
        return artifact_type.model_validate(cast(dict[str, object], payload))
    except ValidationError as error:
        raise ConfigurationLoadError(f"invalid configuration artifact: {path.name}") from error


class RepositoryConfigurationLoader:
    def __init__(
        self,
        repository_root: Path,
        configuration_directory: Path | None = None,
    ) -> None:
        self._repository_root = repository_root.resolve()
        self._config_root = (
            configuration_directory.resolve()
            if configuration_directory is not None
            else self._repository_root / "configs"
        )
        try:
            self._config_root.relative_to(self._repository_root)
        except ValueError as error:
            raise ConfigurationLoadError(
                "configuration directory must be inside the repository"
            ) from error
        try:
            self._runtime_manifest = load_runtime_manifest(
                self._repository_root,
                self._config_root,
            )
        except (OSError, UnicodeError, ValueError, RuntimeManifestError) as error:
            raise ConfigurationLoadError("invalid runtime configuration manifest") from error
        self._validate_manifest_file_set()

    @property
    def repository_root(self) -> Path:
        return self._repository_root

    @property
    def runtime_manifest(self) -> RuntimeConfigurationManifest | None:
        return self._runtime_manifest

    def _validate_manifest_file_set(self) -> None:
        if self._runtime_manifest is None:
            return
        discovered = {
            path.relative_to(self._config_root).as_posix()
            for path in (
                *tuple((self._config_root / "job_profiles").glob("*.yaml")),
                *tuple((self._config_root / "rubrics").glob("*.yaml")),
                self._config_root / "scoring.yaml",
                self._config_root / "models.yaml",
                self._config_root / "l1_rules.yaml",
            )
            if path.is_file()
        }
        declared = {item.path for item in self._runtime_manifest.runtime_artifacts}
        if discovered != declared:
            raise ConfigurationLoadError("runtime manifest artifact file set does not match")

    def load_job_artifacts(self) -> tuple[JobProfileArtifact, ...]:
        paths = tuple(sorted((self._config_root / "job_profiles").glob("*.yaml")))
        if not paths:
            raise ConfigurationLoadError("no job profile artifacts found")
        return tuple(load_yaml_artifact(path, JobProfileArtifact) for path in paths)

    def load_rubric_artifacts(self) -> tuple[ScoringRubricArtifact, ...]:
        paths = tuple(sorted((self._config_root / "rubrics").glob("*.yaml")))
        if not paths:
            raise ConfigurationLoadError("no rubric artifacts found")
        return tuple(load_yaml_artifact(path, ScoringRubricArtifact) for path in paths)

    def load_scoring_artifact(self) -> ScoringConfigurationArtifact:
        return load_yaml_artifact(
            self._config_root / "scoring.yaml",
            ScoringConfigurationArtifact,
        )

    def load_models_artifact(self) -> ModelsConfigurationArtifact:
        return load_yaml_artifact(
            self._config_root / "models.yaml",
            ModelsConfigurationArtifact,
        )

    def load_l1_rules_artifact(self) -> L1RulesConfigurationArtifact:
        return load_yaml_artifact(
            self._config_root / "l1_rules.yaml",
            L1RulesConfigurationArtifact,
        )

    def load_l1_policies(self) -> tuple[L1PolicyArtifact, ...]:
        return self.load_l1_rules_artifact().policies

    def load_l1_policy(self, job_profile_id: str) -> L1Policy:
        policies = {policy.job_profile_id: policy for policy in self.load_l1_policies()}
        if job_profile_id not in policies:
            raise ConfigurationLoadError(f"missing L1 policy for job profile: {job_profile_id}")
        return build_l1_policy(policies[job_profile_id])

    def load_for_job(
        self,
        job_profile_id: str,
        runtime_environment: Mapping[str, str] | None = None,
    ) -> LoadedClassifierConfiguration:
        jobs = {artifact.job_profile_id: artifact for artifact in self.load_job_artifacts()}
        if self._runtime_manifest is not None and set(jobs) != set(
            self._runtime_manifest.supported_job_profile_ids
        ):
            raise ConfigurationLoadError("runtime manifest job profile set does not match")
        if job_profile_id not in jobs:
            raise ConfigurationLoadError(f"unknown job profile identifier: {job_profile_id}")
        job = jobs[job_profile_id]
        rubrics = {artifact.rubric_id: artifact for artifact in self.load_rubric_artifacts()}
        rubric_id = job.artifact_links.rubric_id
        if rubric_id not in rubrics:
            raise ConfigurationLoadError(f"missing linked rubric: {rubric_id}")
        rubric = rubrics[rubric_id]
        scoring = self.load_scoring_artifact()
        models = self.load_models_artifact()
        l1_rules = self.load_l1_rules_artifact()
        self._validate_links(job, rubric, scoring, models, l1_rules)
        self._validate_runtime_strategy(scoring, models, l1_rules)
        l1_policies = {policy.job_profile_id: policy for policy in l1_rules.policies}
        if job_profile_id not in l1_policies:
            raise ConfigurationLoadError(f"missing L1 policy for job profile: {job_profile_id}")
        l1_policy = build_l1_policy(l1_policies[job_profile_id])
        if {rule.requirement_id for rule in l1_policy.rules} != set(
            rubric.critical_requirement_ids
        ):
            raise ConfigurationLoadError("L1 rules must exactly match critical requirements")
        metadata = models.fake_model_metadata()
        if runtime_environment is not None:
            provider_variable = models.llm.runtime_provider.provider_environment_variable
            model_variable = models.llm.runtime_provider.model_environment_variable
            provider_identifier = runtime_environment.get(provider_variable)
            model_identifier = runtime_environment.get(model_variable)
            if not provider_identifier or not model_identifier:
                raise ConfigurationLoadError("runtime LLM provider metadata is incomplete")
            approved_provider = models.llm.runtime_provider.approved_provider_identifier
            approved_model = models.llm.runtime_provider.approved_model_identifier
            if approved_provider is not None and provider_identifier != approved_provider:
                raise ConfigurationLoadError("runtime LLM provider is not approved by the artifact")
            if approved_model is not None and model_identifier != approved_model:
                raise ConfigurationLoadError("runtime LLM model is not approved by the artifact")
            metadata = models.runtime_model_metadata(provider_identifier, model_identifier)
        return LoadedClassifierConfiguration(
            job_profile=job.to_contract(),
            rubric=rubric.to_contract(),
            classification_config=scoring.to_contract(
                metadata,
                job_profile_artifact_version=job.artifact_version,
                l1_rules_configuration_version=l1_rules.configuration_version,
                models_configuration_version=models.configuration_version,
            ),
            job_artifact=job,
            rubric_artifact=rubric,
            scoring_artifact=scoring,
            models_artifact=models,
            l1_rules_artifact=l1_rules,
        )

    def _validate_runtime_strategy(
        self,
        scoring: ScoringConfigurationArtifact,
        models: ModelsConfigurationArtifact,
        l1_rules: L1RulesConfigurationArtifact,
    ) -> None:
        if self._runtime_manifest is None:
            return
        strategy = self._runtime_manifest.strategy
        weights = scoring.aggregation.level_weights
        matching = models.embedding.matching
        provider = models.llm.runtime_provider
        actual_weights = (
            weights.l1_deterministic_rules,
            weights.l2_section_semantic_matching,
            weights.l3_evidence_grounded_reasoning,
        )
        actual_thresholds = (
            scoring.decision_policy.thresholds.waitlist_minimum,
            scoring.decision_policy.thresholds.pass_minimum,
        )
        runtime_contract = scoring.to_contract(
            models.fake_model_metadata(),
            job_profile_artifact_version="2.0.0",
            l1_rules_configuration_version=l1_rules.configuration_version,
            models_configuration_version=models.configuration_version,
        )
        if (
            scoring.configuration_version != strategy.scoring_configuration_version
            or models.configuration_version != strategy.models_configuration_version
            or l1_rules.configuration_version != strategy.l1_rules_configuration_version
            or matching.candidate_id != strategy.l2_candidate_id
            or models.llm.prompt_version != strategy.prompt_version
            or models.llm.score_mapping_version != strategy.l3_score_mapping_version
            or provider.approved_provider_identifier != strategy.provider_identifier
            or provider.approved_model_identifier != strategy.model_identifier
            or actual_weights != strategy.aggregation
            or actual_thresholds != strategy.thresholds
            or runtime_contract.needs_review_policy.disagreement_points
            != strategy.disagreement_points
        ):
            raise ConfigurationLoadError(
                "runtime artifacts do not match versioned manifest strategy"
            )
        bands = tuple(
            (band.minimum, band.maximum)
            for band in runtime_contract.needs_review_policy.boundary_score_bands
        )
        offset = strategy.boundary_offset_points
        expected_bands = (
            (actual_thresholds[0] - offset, actual_thresholds[0] + offset),
            (actual_thresholds[1] - offset, actual_thresholds[1] + offset),
        )
        if bands != expected_bands:
            raise ConfigurationLoadError("runtime boundary bands do not match versioned strategy")

    @staticmethod
    def _validate_links(
        job: JobProfileArtifact,
        rubric: ScoringRubricArtifact,
        scoring: ScoringConfigurationArtifact,
        models: ModelsConfigurationArtifact,
        l1_rules: L1RulesConfigurationArtifact,
    ) -> None:
        if rubric.job_profile_id != job.job_profile_id:
            raise ConfigurationLoadError("rubric job profile link does not match")
        if rubric.rubric_version != job.artifact_links.rubric_version:
            raise ConfigurationLoadError("rubric version link does not match")
        if rubric.artifact_links.job_profile_artifact_version != job.artifact_version:
            raise ConfigurationLoadError("job profile version link does not match")
        if job.artifact_links.scoring_configuration_version != scoring.configuration_version:
            raise ConfigurationLoadError("job scoring configuration link does not match")
        if rubric.artifact_links.scoring_configuration_version != scoring.configuration_version:
            raise ConfigurationLoadError("rubric scoring configuration link does not match")
        if models.artifact_links.scoring_configuration_version != scoring.configuration_version:
            raise ConfigurationLoadError("model scoring configuration link does not match")
        if job.artifact_links.models_configuration_version != models.configuration_version:
            raise ConfigurationLoadError("job models configuration link does not match")
        if rubric.artifact_links.models_configuration_version != models.configuration_version:
            raise ConfigurationLoadError("rubric models configuration link does not match")
        if models.configuration_version != scoring.artifact_links.models_configuration_version:
            raise ConfigurationLoadError("scoring models configuration link does not match")
        if l1_rules.configuration_version != scoring.artifact_links.l1_rules_configuration_version:
            raise ConfigurationLoadError("scoring L1 rules configuration link does not match")
        if job.artifact_version not in scoring.artifact_links.supported_job_profile_versions:
            raise ConfigurationLoadError("job artifact version is unsupported")
        if rubric.rubric_version not in scoring.artifact_links.supported_rubric_versions:
            raise ConfigurationLoadError("rubric version is unsupported by scoring configuration")
        if rubric.rubric_version not in models.artifact_links.supported_rubric_versions:
            raise ConfigurationLoadError("rubric version is unsupported by models configuration")
        mandatory_ids = {item.requirement_id for item in job.mandatory_requirements}
        if set(rubric.critical_requirement_ids) != mandatory_ids:
            raise ConfigurationLoadError(
                "rubric critical requirements must match mandatory requirements"
            )

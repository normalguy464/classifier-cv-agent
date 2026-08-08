import json
import shutil
from pathlib import Path
from typing import cast

from backend.app.contracts import CVProfile, EvidenceStatus
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    SyntheticExpansionManifest,
    SyntheticExpansionSilverSplitManifest,
    SyntheticPairAnnotation,
    validate_synthetic_expansion,
)
from scripts.remediate_synthetic_expansion import (
    DATASET_VERSION,
    EVIDENCE_TEXT_REPLACEMENTS,
    OUTPUT_DIRECTORY,
    OUTPUT_SPLIT_MANIFEST_PATH,
    SOURCE_DIRECTORY,
    SOURCE_SPLIT_MANIFEST_PATH,
    build_remediated_dataset,
    write_remediated_dataset,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _profiles(directory: Path) -> dict[str, CVProfile]:
    return {
        item.cv_profile_id: item
        for item in (
            CVProfile.model_validate_json(line)
            for line in (directory / "cv_profiles.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def _annotations(directory: Path) -> dict[str, SyntheticPairAnnotation]:
    return {
        item.pair_id: item
        for item in (
            SyntheticPairAnnotation.model_validate_json(line)
            for line in (directory / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def test_remediation_changes_only_approved_profile_evidence() -> None:
    profiles, _, _, annotations, _, source_split = build_remediated_dataset(REPOSITORY_ROOT)
    source_profiles = _profiles(REPOSITORY_ROOT / SOURCE_DIRECTORY)
    remediated_profiles = {item.cv_profile_id: item for item in profiles}

    assert set(remediated_profiles) == set(source_profiles)
    for profile_id in set(source_profiles) - set(EVIDENCE_TEXT_REPLACEMENTS):
        assert remediated_profiles[profile_id] == source_profiles[profile_id]
    for profile_id, replacements in EVIDENCE_TEXT_REPLACEMENTS.items():
        source = source_profiles[profile_id]
        remediated = remediated_profiles[profile_id]
        source_by_id = {item.evidence_id: item for item in source.evidence}
        remediated_by_id = {item.evidence_id: item for item in remediated.evidence}
        assert set(source_by_id) == set(remediated_by_id)
        assert {
            evidence_id
            for evidence_id in source_by_id
            if source_by_id[evidence_id] != remediated_by_id[evidence_id]
        } == set(replacements)
        assert {
            evidence_id: remediated_by_id[evidence_id].text for evidence_id in replacements
        } == replacements

    affected = tuple(
        item for item in annotations if item.cv_profile_id in EVIDENCE_TEXT_REPLACEMENTS
    )
    assert len(affected) == 10
    assert {item.pair_id for item in affected}.issubset(set(source_split.development.pair_ids))
    assert all(
        item.critical_requirement_assessments[0].evidence_status is EvidenceStatus.MISSING
        for item in affected
    )
    assert all(
        cast(ApprovedDatasetReview, item.review).human_review_count == 1 for item in affected
    )


def test_remediation_preserves_scores_labels_and_unaffected_reviews() -> None:
    _, _, _, annotations, _, _ = build_remediated_dataset(REPOSITORY_ROOT)
    source_annotations = _annotations(REPOSITORY_ROOT / SOURCE_DIRECTORY)

    for annotation in annotations:
        source = source_annotations[annotation.pair_id]
        payload = annotation.model_dump(mode="json")
        source_payload = source.model_dump(mode="json")
        if annotation.cv_profile_id in EVIDENCE_TEXT_REPLACEMENTS:
            payload.pop("review")
            source_payload.pop("review")
            assert payload == source_payload
            review = cast(ApprovedDatasetReview, annotation.review)
            assert "rò năng lực" in review.notes
        else:
            assert payload == source_payload


def test_committed_remediation_is_reproducible_and_passes_qc(tmp_path: Path) -> None:
    generated_root = tmp_path / "repository"
    source_directory = generated_root / SOURCE_DIRECTORY
    source_directory.parent.mkdir(parents=True)
    shutil.copytree(REPOSITORY_ROOT / SOURCE_DIRECTORY, source_directory)
    source_split = generated_root / SOURCE_SPLIT_MANIFEST_PATH
    source_split.parent.mkdir(parents=True)
    source_split.write_bytes((REPOSITORY_ROOT / SOURCE_SPLIT_MANIFEST_PATH).read_bytes())

    generated_paths = write_remediated_dataset(generated_root)
    committed_directory = REPOSITORY_ROOT / OUTPUT_DIRECTORY
    committed_split = REPOSITORY_ROOT / OUTPUT_SPLIT_MANIFEST_PATH
    expected_paths = (
        *(committed_directory / path.name for path in generated_paths[:-1]),
        committed_split,
    )
    for generated, expected in zip(generated_paths, expected_paths, strict=True):
        assert generated.read_bytes() == expected.read_bytes()

    report = validate_synthetic_expansion(committed_directory)
    manifest = SyntheticExpansionManifest.model_validate_json(
        (committed_directory / "manifest.json").read_text(encoding="utf-8")
    )
    split = SyntheticExpansionSilverSplitManifest.model_validate_json(
        committed_split.read_text(encoding="utf-8")
    )
    source_split_manifest = SyntheticExpansionSilverSplitManifest.model_validate_json(
        (REPOSITORY_ROOT / SOURCE_SPLIT_MANIFEST_PATH).read_text(encoding="utf-8")
    )

    assert report.passed
    assert manifest.dataset_version == DATASET_VERSION
    assert split.source_dataset_version == DATASET_VERSION
    assert split.development.pair_ids == source_split_manifest.development.pair_ids
    assert split.held_out.pair_ids == source_split_manifest.held_out.pair_ids
    assert split.held_out.classifier_results_generated is False


def test_committed_profiles_do_not_reintroduce_missing_skills() -> None:
    profiles = _profiles(REPOSITORY_ROOT / OUTPUT_DIRECTORY)
    data_analyst_text = " ".join(
        item.text for item in profiles["cv-syn-da-missing-v2"].evidence
    ).casefold()
    data_engineer_text = " ".join(
        item.text for item in profiles["cv-syn-de-missing-v2"].evidence
    ).casefold()

    assert "sql" not in data_analyst_text
    assert "cte" not in data_analyst_text
    assert "window function" not in data_analyst_text
    assert "python" not in data_engineer_text


def test_remediation_manifest_contains_no_provider_output() -> None:
    manifest = json.loads(
        (REPOSITORY_ROOT / OUTPUT_DIRECTORY / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["frozen_test_created"] is False
    assert "provider" not in json.dumps(manifest).casefold()

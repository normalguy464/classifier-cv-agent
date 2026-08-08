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
from scripts.remediate_synthetic_expansion_v2_3 import (
    DATASET_VERSION,
    EVIDENCE_TEXT_REPLACEMENTS,
    OUTPUT_DIRECTORY,
    OUTPUT_SPLIT_MANIFEST_PATH,
    SOURCE_DIRECTORY,
    SOURCE_SPLIT_MANIFEST_PATH,
    TARGET_PROFILE_ID,
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


def test_v2_3_changes_only_approved_qa_composite_evidence() -> None:
    profiles, _, _, annotations, _, source_split = build_remediated_dataset(REPOSITORY_ROOT)
    source_profiles = _profiles(REPOSITORY_ROOT / SOURCE_DIRECTORY)
    remediated_profiles = {item.cv_profile_id: item for item in profiles}

    for profile_id in set(source_profiles) - {TARGET_PROFILE_ID}:
        assert remediated_profiles[profile_id] == source_profiles[profile_id]
    source = source_profiles[TARGET_PROFILE_ID]
    remediated = remediated_profiles[TARGET_PROFILE_ID]
    source_by_id = {item.evidence_id: item for item in source.evidence}
    remediated_by_id = {item.evidence_id: item for item in remediated.evidence}
    assert {
        evidence_id
        for evidence_id in source_by_id
        if source_by_id[evidence_id] != remediated_by_id[evidence_id]
    } == set(EVIDENCE_TEXT_REPLACEMENTS)
    assert {
        evidence_id: remediated_by_id[evidence_id].text
        for evidence_id in EVIDENCE_TEXT_REPLACEMENTS
    } == EVIDENCE_TEXT_REPLACEMENTS

    affected = tuple(item for item in annotations if item.cv_profile_id == TARGET_PROFILE_ID)
    assert len(affected) == 5
    assert {item.pair_id for item in affected}.issubset(set(source_split.development.pair_ids))
    assert all(
        item.critical_requirement_assessments[0].evidence_status is EvidenceStatus.UNSATISFIED
        for item in affected
    )


def test_v2_3_preserves_scores_labels_and_unaffected_reviews() -> None:
    _, _, _, annotations, _, _ = build_remediated_dataset(REPOSITORY_ROOT)
    source_annotations = _annotations(REPOSITORY_ROOT / SOURCE_DIRECTORY)

    for annotation in annotations:
        source = source_annotations[annotation.pair_id]
        payload = annotation.model_dump(mode="json")
        source_payload = source.model_dump(mode="json")
        if annotation.cv_profile_id == TARGET_PROFILE_ID:
            payload.pop("review")
            source_payload.pop("review")
            assert payload == source_payload
            review = cast(ApprovedDatasetReview, annotation.review)
            assert review.human_review_count == 1
            assert "testing-foundation" in review.notes
        else:
            assert payload == source_payload


def test_v2_3_committed_artifacts_are_reproducible_and_pass_qc(tmp_path: Path) -> None:
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


def test_v2_3_removes_testing_foundation_claims_from_composite_evidence() -> None:
    profile = _profiles(REPOSITORY_ROOT / OUTPUT_DIRECTORY)[TARGET_PROFILE_ID]
    evidence_by_id = {item.evidence_id: item.text for item in profile.evidence}
    corrected_text = " ".join(
        evidence_by_id[evidence_id] for evidence_id in EVIDENCE_TEXT_REPLACEMENTS
    ).casefold()

    for phrase in (
        "acceptance criteria",
        "risk-based",
        "boundary",
        "decision table",
        "test plan",
    ):
        assert phrase not in corrected_text


def test_v2_3_manifest_contains_no_provider_output() -> None:
    manifest = json.loads(
        (REPOSITORY_ROOT / OUTPUT_DIRECTORY / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["frozen_test_created"] is False
    assert "provider" not in json.dumps(manifest).casefold()

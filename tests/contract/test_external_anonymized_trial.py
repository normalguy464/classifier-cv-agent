from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from backend.app.contracts import CVProfile

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRIAL_PROFILE_PATH = (
    REPOSITORY_ROOT
    / "data"
    / "samples"
    / "external_trials"
    / "cv_external_anonymized_ai_data_engineering_v1.json"
)


def load_trial_profile() -> tuple[dict[str, object], CVProfile]:
    payload = cast(
        dict[str, object],
        json.loads(TRIAL_PROFILE_PATH.read_text(encoding="utf-8")),
    )
    return payload, CVProfile.model_validate(payload)


def test_external_trial_profile_satisfies_cv_contract() -> None:
    payload, profile = load_trial_profile()

    assert payload["schema_version"] == "1.0.0"
    assert profile.cv_profile_id == "cv-external-anonymized-ai-data-v1"
    assert len(profile.evidence) == 11
    assert all(item.source_type.value == "manual" for item in profile.evidence)
    assert all(not item.is_verified for item in profile.evidence)


def test_external_trial_profile_excludes_direct_identifiers() -> None:
    payload, profile = load_trial_profile()
    serialized = json.dumps(payload, ensure_ascii=False).lower()

    assert "@" not in serialized
    assert "http://" not in serialized
    assert "https://" not in serialized
    assert all(item.organization_reference is None for item in profile.work_experiences)
    assert all(item.institution_reference is None for item in profile.education)
    assert all(item.issuer_reference is None for item in profile.certifications)


def test_external_trial_profile_records_manual_adaptation_warning() -> None:
    _, profile = load_trial_profile()

    assert [item.code for item in profile.quality_warnings] == ["manual-anonymized-adaptation"]
    assert "not direct Parser Agent output" in profile.quality_warnings[0].message

from decimal import Decimal
from pathlib import Path

import pytest

from backend.app.infrastructure.calibration import SklearnExtraTreesL2Calibrator
from backend.app.infrastructure.config import ModelsConfigurationArtifact, load_yaml_artifact

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODELS_PATH = REPOSITORY_ROOT / "configs/runtime/five_role_v2_candidate/models.yaml"


def test_candidate_l2_calibrator_loads_verified_model_and_returns_bounded_scores() -> None:
    models = load_yaml_artifact(MODELS_PATH, ModelsConfigurationArtifact)
    configuration = models.embedding.calibration
    assert configuration is not None
    calibrator = SklearnExtraTreesL2Calibrator(REPOSITORY_ROOT, configuration)

    scores = calibrator.calibrate(
        "junior-data-analyst-std-v2",
        (Decimal("18"), Decimal("14"), Decimal("12"), Decimal("8"), Decimal("5")),
    )

    assert len(scores) == 5
    assert all(
        Decimal("0") <= score <= maximum
        for score, maximum in zip(
            scores,
            configuration.criterion_maximums,
            strict=True,
        )
    )


def test_candidate_l2_calibrator_rejects_model_hash_mismatch() -> None:
    models = load_yaml_artifact(MODELS_PATH, ModelsConfigurationArtifact)
    configuration = models.embedding.calibration
    assert configuration is not None
    invalid = configuration.model_copy(update={"model_sha256": "0" * 64})

    with pytest.raises(ValueError, match="hash"):
        SklearnExtraTreesL2Calibrator(REPOSITORY_ROOT, invalid)

from __future__ import annotations

import hashlib
import importlib
import warnings
from decimal import Decimal
from pathlib import Path
from typing import Protocol, cast

import numpy as np
from numpy.typing import NDArray

from backend.app.infrastructure.config.artifacts import L2CalibrationArtifact


class Predictor(Protocol):
    def predict(self, features: NDArray[np.float64]) -> NDArray[np.float64]: ...


class JoblibModule(Protocol):
    def load(self, filename: Path) -> object: ...


joblib_module = cast(JoblibModule, importlib.import_module("joblib"))


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SklearnExtraTreesL2Calibrator:
    def __init__(
        self,
        repository_root: Path,
        configuration: L2CalibrationArtifact,
    ) -> None:
        model_path = (repository_root / configuration.model_path).resolve()
        if repository_root.resolve() not in model_path.parents:
            raise ValueError("L2 calibration model must stay inside the repository")
        if not model_path.is_file():
            raise ValueError("L2 calibration model is unavailable")
        if _file_sha256(model_path) != configuration.model_sha256:
            raise ValueError("L2 calibration model hash does not match configuration")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning, module="joblib")
            payload = joblib_module.load(model_path)
        if not isinstance(payload, dict):
            raise ValueError("L2 calibration model payload must be a mapping")
        typed_payload = cast(dict[str, object], payload)
        model = typed_payload.get("model")
        if model is None or not callable(getattr(model, "predict", None)):
            raise ValueError("L2 calibration model payload is missing a predictor")
        feature_roles = typed_payload.get("feature_roles")
        if not isinstance(feature_roles, tuple) or feature_roles != configuration.feature_roles:
            raise ValueError("L2 calibration feature roles do not match the model")
        criterion_maximums = typed_payload.get("criterion_maximums")
        if not isinstance(criterion_maximums, tuple) or criterion_maximums != tuple(
            float(item) for item in configuration.criterion_maximums
        ):
            raise ValueError("L2 calibration criterion maximums do not match the model")
        self._model = cast(Predictor, model)
        self._roles = configuration.feature_roles
        self._job_roles = {
            item.job_profile_id: item.role for item in configuration.job_profile_roles
        }
        self._maximums = configuration.criterion_maximums

    def calibrate(
        self,
        job_profile_id: str,
        criterion_scores: tuple[Decimal, ...],
    ) -> tuple[Decimal, ...]:
        if len(criterion_scores) != len(self._maximums):
            raise ValueError("L2 calibration requires five criterion scores")
        role = self._job_roles.get(job_profile_id)
        if role is None:
            raise ValueError("L2 calibration does not support the job profile")
        features = np.asarray(
            [
                [
                    *map(float, criterion_scores),
                    *(float(role == configured_role) for configured_role in self._roles),
                ]
            ],
            dtype=np.float64,
        )
        raw = self._model.predict(features)
        if raw.shape != (1, len(self._maximums)) or not np.isfinite(raw).all():
            raise RuntimeError("L2 calibration model returned an invalid prediction")
        return tuple(
            min(maximum, max(Decimal("0"), Decimal(str(float(value)))))
            for value, maximum in zip(raw[0], self._maximums, strict=True)
        )

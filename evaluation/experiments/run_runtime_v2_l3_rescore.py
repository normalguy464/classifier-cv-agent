from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import cast

from evaluation.datasets.runtime_v2 import file_sha256
from evaluation.experiments.run_runtime_v2_l3_pilot import (
    PilotCache,
    build_pilot_report,
    load_pilot_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_l3_fresh_confirmation_v2_rescore_v3.yaml")
CACHE_PATH = Path("evaluation/reports/generated/runtime_v2_l3_fresh_confirmation_cache_v2.json")
REPORT_PATH = Path("evaluation/reports/runtime_v2_l3_fresh_confirmation_v2_rescore_v3.json")


def _load_source_cache(repository_root: Path, cache_path: Path) -> PilotCache:
    payload = json.loads((repository_root / cache_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("L3 rescore source cache must be a JSON object")
    return PilotCache.model_validate(cast(dict[str, object], payload))


def build_rescore_report(
    repository_root: Path,
    generated_at: datetime,
    configuration_path: Path = CONFIG_PATH,
    source_cache_path: Path = CACHE_PATH,
) -> dict[str, object]:
    configuration = load_pilot_configuration(repository_root, configuration_path)
    cache = _load_source_cache(repository_root, source_cache_path)
    reviewed_manifest = repository_root / configuration.reviewed_dataset_directory / "manifest.json"
    expected_hashes = (
        file_sha256(reviewed_manifest),
        file_sha256(repository_root / configuration.split_manifest_path),
    )
    if (cache.reviewed_manifest_sha256, cache.split_manifest_sha256) != expected_hashes:
        raise ValueError("L3 rescore source cache data hashes do not match")
    if (
        cache.provider_identifier != configuration.provider_identifier
        or cache.model_identifier != configuration.model_identifier
        or cache.prompt_version != configuration.prompt_version
    ):
        raise ValueError("L3 rescore source cache strategy does not match")
    available_ids = {
        item.pair_id
        for item in cache.attempts
        if item.output is not None and item.status == "available"
    }
    if not set(configuration.pilot_pair_ids).issubset(available_ids):
        raise ValueError("L3 rescore source cache is incomplete")
    report = build_pilot_report(
        repository_root,
        generated_at,
        cache,
        configuration_path,
    )
    report["llm_provider_calls_made"] = False
    traceability = cast(dict[str, object], report["traceability"])
    traceability["source_cache_sha256"] = file_sha256(repository_root / source_cache_path)
    traceability["source_experiment_id"] = cache.experiment_id
    return report


def _timestamp(value: str) -> datetime:
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return timestamp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", default="2026-08-08T23:30:00+07:00")
    parser.add_argument("--configuration-path", default=str(CONFIG_PATH))
    parser.add_argument("--source-cache-path", default=str(CACHE_PATH))
    parser.add_argument("--output", default=str(REPORT_PATH))
    arguments = parser.parse_args()
    report = build_rescore_report(
        REPOSITORY_ROOT,
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.configuration_path)),
        Path(cast(str, arguments.source_cache_path)),
    )
    output = REPOSITORY_ROOT / Path(cast(str, arguments.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

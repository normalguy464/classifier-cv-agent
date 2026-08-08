from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from backend.app.contracts import ClassificationDecision
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from evaluation.baselines import (
    EmbeddingOnlyBaseline,
    KeywordRuleBaseline,
    TfidfCosineBaseline,
)
from evaluation.datasets import load_reviewed_pilot
from evaluation.metrics import calculate_metrics


def run(repository_root: Path) -> dict[str, object]:
    examples = load_reviewed_pilot(repository_root)
    loader = RepositoryConfigurationLoader(repository_root)
    expected = tuple(example.final_label for example in examples)
    keyword_predictions: list[ClassificationDecision] = []
    tfidf_predictions: list[ClassificationDecision] = []
    embedding_predictions: list[ClassificationDecision] = []
    hashing_adapter = HashingEmbeddingAdapter(dimension=768)
    for example in examples:
        loaded = loader.load_for_job(example.job_profile_id)
        keyword = KeywordRuleBaseline(loader.load_l1_policy(example.job_profile_id)).predict(
            example.cv_profile,
            loaded.rubric,
            loaded.classification_config.thresholds,
        )
        tfidf = TfidfCosineBaseline().predict(
            example.cv_profile,
            loaded.job_profile,
            loaded.classification_config.thresholds,
        )
        embedding_config = loaded.models_artifact.embedding
        embedding = EmbeddingOnlyBaseline(
            hashing_adapter,
            embedding_config.matching.similarity_floor,
            embedding_config.matching.similarity_ceiling,
            embedding_config.matching.top_k,
        ).predict(
            example.cv_profile,
            loaded.job_profile,
            loaded.classification_config.thresholds,
        )
        keyword_predictions.append(keyword.decision)
        tfidf_predictions.append(tfidf.decision)
        embedding_predictions.append(embedding.decision)
    return {
        "report_scope": "reviewed-pilot-diagnostic-only",
        "is_final_performance": False,
        "sample_count": len(examples),
        "baselines": {
            "keyword-rule-v1": asdict(calculate_metrics(expected, tuple(keyword_predictions))),
            "tfidf-cosine-v1": asdict(calculate_metrics(expected, tuple(tfidf_predictions))),
            "embedding-only-deterministic-hashing-1.0.0": asdict(
                calculate_metrics(expected, tuple(embedding_predictions))
            ),
        },
    }


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    print(json.dumps(run(repository_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

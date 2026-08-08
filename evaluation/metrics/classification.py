from __future__ import annotations

from dataclasses import dataclass

from backend.app.contracts import ClassificationDecision

LABELS = tuple(ClassificationDecision)


@dataclass(frozen=True, slots=True)
class LabelMetrics:
    precision: float
    recall: float
    f1: float
    support: int


@dataclass(frozen=True, slots=True)
class ClassificationMetrics:
    sample_count: int
    accuracy: float
    macro_f1: float
    cohen_kappa: float
    labels: dict[str, LabelMetrics]
    confusion_matrix: tuple[tuple[int, ...], ...]


def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def calculate_metrics(
    expected: tuple[ClassificationDecision, ...],
    predicted: tuple[ClassificationDecision, ...],
) -> ClassificationMetrics:
    if not expected or len(expected) != len(predicted):
        raise ValueError("metric inputs must be non-empty and have equal length")
    label_indexes = {label: index for index, label in enumerate(LABELS)}
    matrix = [[0 for _ in LABELS] for _ in LABELS]
    for expected_label, predicted_label in zip(expected, predicted, strict=True):
        matrix[label_indexes[expected_label]][label_indexes[predicted_label]] += 1
    per_label: dict[str, LabelMetrics] = {}
    f1_values: list[float] = []
    for label, index in label_indexes.items():
        true_positive = matrix[index][index]
        false_positive = sum(row[index] for row in matrix) - true_positive
        false_negative = sum(matrix[index]) - true_positive
        support = sum(matrix[index])
        precision = _safe_ratio(true_positive, true_positive + false_positive)
        recall = _safe_ratio(true_positive, true_positive + false_negative)
        f1 = _safe_ratio(2 * precision * recall, precision + recall)
        per_label[label.value] = LabelMetrics(precision, recall, f1, support)
        f1_values.append(f1)
    sample_count = len(expected)
    agreement = sum(matrix[index][index] for index in range(len(LABELS)))
    accuracy = agreement / sample_count
    expected_agreement = sum(
        sum(matrix[index]) * sum(row[index] for row in matrix) for index in range(len(LABELS))
    ) / (sample_count * sample_count)
    cohen_kappa = _safe_ratio(
        int(round((accuracy - expected_agreement) * 1_000_000)),
        int(round((1 - expected_agreement) * 1_000_000)),
    )
    return ClassificationMetrics(
        sample_count=sample_count,
        accuracy=accuracy,
        macro_f1=sum(f1_values) / len(f1_values),
        cohen_kappa=cohen_kappa,
        labels=per_label,
        confusion_matrix=tuple(tuple(row) for row in matrix),
    )

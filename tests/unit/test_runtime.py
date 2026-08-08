from __future__ import annotations

from backend.app.infrastructure.runtime import SystemClock, UuidIdentifierGenerator


def test_system_clock_returns_timezone_aware_utc_time() -> None:
    value = SystemClock().now()

    assert value.tzinfo is not None
    assert value.utcoffset() is not None


def test_uuid_identifier_generator_returns_unique_contract_compatible_values() -> None:
    generator = UuidIdentifierGenerator()

    first = generator.new_identifier("result")
    second = generator.new_identifier("result")

    assert first.startswith("result-")
    assert second.startswith("result-")
    assert first != second
    assert len(first) <= 64


def test_uuid_identifier_generator_rejects_invalid_prefix() -> None:
    generator = UuidIdentifierGenerator()

    try:
        generator.new_identifier("invalid prefix")
    except ValueError as error:
        assert str(error)
    else:
        raise AssertionError("invalid prefix must be rejected")

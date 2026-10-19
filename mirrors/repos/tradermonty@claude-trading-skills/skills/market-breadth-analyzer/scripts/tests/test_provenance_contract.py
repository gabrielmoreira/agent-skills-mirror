"""Standalone copies retain the common schema while strict policy is opt-in."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = load("market_contract", Path(__file__).resolve().parents[1] / "provenance_contract.py")
shared = load("shared_provenance", ROOT / "scripts/validate_provenance.py")


def block(**overrides):
    result = contract.build_provenance(
        provider="fixture",
        endpoint="fixture://primary",
        retrieved_at="2026-10-17T01:00:00Z",
        as_of="2026-10-16",
        run_id="run-a",
    )
    result.update(overrides)
    return result


def validate(value, **overrides):
    args = dict(run_id="run-a", evaluation="2026-10-17T02:00:00Z", max_age_days=0)
    args.update(overrides)
    return contract.validate_handoff(value, **args)


def test_vendored_helpers_are_identical():
    copies = [
        (ROOT / "skills" / skill / "scripts/provenance_contract.py").read_bytes()
        for skill in ("market-breadth-analyzer", "uptrend-analyzer", "exposure-coach")
    ]
    assert copies[0] == copies[1] == copies[2]


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"schema_version": "0.9"},
        {"adjusted": 1},
        {"as_of": None},
        {"retrieved_at": "2026-10-17T02:00:00+01:00"},
        {"timezone": "invalid"},
    ],
)
def test_common_schema_matches_shared_validator(changes):
    value = block(**changes)
    assert contract.validate_provenance(value) == shared.validate_provenance(value)


def test_date_age_uses_reporting_timezone():
    # Both instants are October 16 in New York, so this is zero business days old.
    assert validate(block())["as_of"] == "2026-10-16"
    with pytest.raises(ValueError, match="stale"):
        validate(block(), evaluation="2026-10-17T05:00:00Z")
    assert validate(block(), evaluation="2026-10-17T05:00:00Z", max_age_days=1)


def test_instant_age_boundary_is_elapsed_time():
    value = block(as_of="2026-10-16T01:00:00Z")
    assert validate(value, evaluation="2026-10-17T01:00:00Z", max_age_days=1)
    with pytest.raises(ValueError, match="stale"):
        validate(value, evaluation="2026-10-17T01:00:01Z", max_age_days=1)


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"run_id": "other-run"}, "run_id"),
        ({"schema_version": "2.0"}, "schema_version"),
        ({"retrieved_at": "2026-10-17T03:00:00Z"}, "after evaluation"),
        ({"retrieved_at": "2026-10-17T02:00:00+01:00"}, "UTC"),
        ({"retrieved_at": "2026-10-17T01:00:00"}, "timezone"),
        ({"as_of": "2026-10-17"}, "after retrieval business date"),
        ({"as_of": "2026-10-17T01:00:01Z"}, "after retrieval"),
    ],
)
def test_strict_rejections(changes, message):
    with pytest.raises(ValueError, match=message):
        validate(block(**changes))


@pytest.mark.parametrize("age", [-1, True, 0.5])
def test_invalid_age_policy_rejected(age):
    with pytest.raises(ValueError, match="nonnegative integer"):
        validate(block(), max_age_days=age)


def test_both_primary_inputs_required():
    with pytest.raises(ValueError, match="uptrend input is required"):
        contract.validate_market_inputs(
            {"data_provenance": block()},
            None,
            run_id="run-a",
            evaluation="2026-10-17T02:00:00Z",
            max_age_days=0,
        )


@pytest.mark.parametrize("value", [None, "wrong", [], 3])
def test_schema_nonmapping_rejected(value):
    assert contract.validate_provenance(value) == shared.validate_provenance(value)


def test_schema_missing_and_invalid_fields_match():
    assert contract.validate_provenance({}) == shared.validate_provenance({})
    for field in contract.STRING_FIELDS:
        for value in (None, "", 3):
            candidate = block(**{field: value})
            assert contract.validate_provenance(candidate) == shared.validate_provenance(candidate)
    for value in (None, 3, "bogus", "2026-02-30"):
        assert contract.validate_provenance(block(as_of=value))
    for value in (None, 3, "bogus", "2026-10-17T01:00:00"):
        assert contract.validate_provenance(block(retrieved_at=value))


def test_build_rejects_invalid_date_and_empty_run():
    for changes in ({"as_of": "invalid"}, {"run_id": ""}):
        args = dict(
            provider="fixture",
            endpoint="fixture://primary",
            retrieved_at="2026-10-17T01:00:00Z",
            as_of="2026-10-16",
            run_id="run-a",
        )
        args.update(changes)
        with pytest.raises(ValueError):
            contract.build_provenance(**args)


def test_invalid_evaluation_and_wrapped_input_error():
    with pytest.raises(ValueError, match="evaluation"):
        validate(block(), evaluation="invalid")
    with pytest.raises(ValueError, match="breadth:"):
        contract.validate_market_inputs(
            {"data_provenance": {}},
            {"data_provenance": block()},
            run_id="run-a",
            evaluation="2026-10-17T02:00:00Z",
            max_age_days=0,
        )
    lineage = contract.validate_market_inputs(
        {"data_provenance": block()},
        {"data_provenance": block()},
        run_id="run-a",
        evaluation="2026-10-17T02:00:00Z",
        max_age_days=0,
    )
    assert set(lineage["accepted_inputs"]) == {"breadth", "uptrend"}
    assert lineage["boundaries"]


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://user:secret@example.com:8443/data.csv?token=secret#secret",  # pragma: allowlist secret
            "https://example.com:8443/data.csv",
        ),
        ("https://[::1]:8443/data.csv?token=secret", "https://[::1]:8443/data.csv"),
        ("/local.csv?token=secret", "/local.csv"),
    ],
)
def test_source_identity_strips_credentials_and_query(url, expected):
    assert contract.safe_source_url(url) == expected

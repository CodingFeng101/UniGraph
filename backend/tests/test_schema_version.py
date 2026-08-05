import _env  # noqa: F401  # isort: skip

from backend.database.schema_version import expected_schema_heads, schema_version_error


def test_expected_schema_head_is_registered() -> None:
    assert expected_schema_heads() == {'20260805_chat_owner'}


def test_current_schema_has_no_error() -> None:
    assert schema_version_error({'20260805_baseline'}, {'20260805_baseline'}) is None


def test_unversioned_schema_has_actionable_error() -> None:
    error = schema_version_error(set(), {'20260805_baseline'})

    assert error is not None
    assert 'unversioned' in error
    assert 'alembic -c backend/alembic.ini upgrade head' in error

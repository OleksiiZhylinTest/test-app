"""Smoke tests for the app.exceptions hierarchy."""

from __future__ import annotations

import pytest

from app.exceptions import (
    AppError,
    ConfigError,
    DataImportError,
    JiraApiError,
    JiraAuthError,
    JiraClientError,
    JiraNetworkError,
    SchemaError,
)

pytestmark = pytest.mark.unit


def test_app_error_is_exception():
    assert issubclass(AppError, Exception)


@pytest.mark.parametrize("cls", [ConfigError, JiraClientError, SchemaError, DataImportError])
def test_domain_errors_are_app_error_subclasses(cls):
    assert issubclass(cls, AppError)


@pytest.mark.parametrize("cls", [JiraNetworkError, JiraAuthError, JiraApiError])
def test_jira_subclasses_are_jira_client_error(cls):
    assert issubclass(cls, JiraClientError)


@pytest.mark.parametrize("cls", [JiraNetworkError, JiraAuthError, JiraApiError])
def test_jira_subclasses_caught_by_parent(cls):
    with pytest.raises(JiraClientError):
        raise cls("test")


@pytest.mark.parametrize("cls", [JiraNetworkError, JiraAuthError, JiraApiError, ConfigError, SchemaError])
def test_domain_errors_caught_by_app_error(cls):
    with pytest.raises(AppError):
        raise cls("test")


def test_schema_error_preserves_cause():
    cause = OSError("disk full")
    with pytest.raises(SchemaError) as exc_info:
        raise SchemaError("write failed") from cause
    assert exc_info.value.__cause__ is cause

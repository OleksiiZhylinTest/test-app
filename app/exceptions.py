"""Application-defined exception hierarchy."""


class AppError(Exception):
    """Base class for all application-defined exceptions."""


class ConfigError(AppError):
    """Raised when required configuration is missing or invalid."""


class JiraClientError(AppError):
    """Base for all Jira API communication failures."""


class JiraNetworkError(JiraClientError):
    """Raised for transport-level failures (SSL, socket, connection refused)."""


class JiraAuthError(JiraClientError):
    """Raised for 401/403 HTTP responses from Jira."""


class JiraApiError(JiraClientError):
    """Raised for other Jira API errors (4xx/5xx, malformed responses)."""


class SchemaError(AppError):
    """Raised when the schema file cannot be written."""


class DataImportError(AppError):
    """Raised when an Excel import cannot begin (missing library, unreadable workbook)."""

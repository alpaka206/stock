class ProviderConfigurationError(RuntimeError):
    """Raised when an external provider is selected without the required config."""


class ExternalServiceError(RuntimeError):
    """Raised when a remote provider fails to return a usable payload."""


class ExternalRateLimitError(ExternalServiceError):
    """Raised when a provider explicitly reports a rate limit condition."""

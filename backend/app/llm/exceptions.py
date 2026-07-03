class LLMProviderError(Exception):
    """
    Base exception class for all LLM provider related errors in Kavalar.
    """
    pass


class LLMConfigurationError(LLMProviderError):
    """
    Exception raised when LLM provider configuration is missing,
    incomplete, or misconfigured.
    """
    pass


class LLMConnectionError(LLMProviderError):
    """
    Exception raised when connection/network errors occur during
    LLM provider communication.
    """
    pass


class LLMAPIError(LLMProviderError):
    """
    Exception raised when the LLM provider API returns errors
    during invocation or health checks.
    """
    pass


class AppError(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class LLMError(AppError):
    """Raised when the LLM provider fails or rate limits."""
    pass

class RetrievalError(AppError):
    """Raised when fetching external documentation fails."""
    pass

class ServiceUnavailableError(AppError):
    """Raised when a circuit breaker is open or dependent service is down."""
    pass

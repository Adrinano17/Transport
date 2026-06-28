"""Domain-level errors."""

from lagos_fare.domain.exceptions import DomainError, InvalidCoordinatesError, SameLocationError

__all__ = ["DomainError", "InvalidCoordinatesError", "SameLocationError"]


class ExternalServiceError(Exception):
    """Third-party API failure (ORS, OWM)."""

    def __init__(self, message: str, service: str = "external") -> None:
        self.message = message
        self.service = service
        super().__init__(message)


class ModelNotLoadedError(Exception):
    def __init__(self, message: str = "ML model is not loaded.") -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found.") -> None:
        self.message = message
        super().__init__(message)

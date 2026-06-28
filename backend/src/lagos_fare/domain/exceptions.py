"""Domain-level errors — business rule violations, not HTTP concerns."""


class DomainError(Exception):
    """Base for all domain failures."""

    def __init__(self, message: str, code: str = "domain_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class InvalidCoordinatesError(DomainError):
    def __init__(self, message: str = "Coordinates are outside the Lagos service area.") -> None:
        super().__init__(message, code="invalid_coordinates")


class SameLocationError(DomainError):
    def __init__(self, message: str = "Pickup and dropoff cannot be the same.") -> None:
        super().__init__(message, code="same_location")

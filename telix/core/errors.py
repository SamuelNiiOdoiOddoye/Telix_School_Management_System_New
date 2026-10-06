"""Exception types shared across the application."""


class ValidationError(ValueError):
    """Raised when submitted form data does not meet application rules."""


class StorageError(RuntimeError):
    """Raised when a JSON record file cannot be read or saved safely."""

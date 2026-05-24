class SzurustashError(Exception):
    """Base exception for all szurustash errors."""

class SzurubooruError(SzurustashError):
    """Base exception for all szurubooru-related errors."""

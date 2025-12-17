"""
Custom exceptions for ML module.
"""


class InsufficientDataError(ValueError):
    """Raised when there is not enough data for feature extraction or training."""
    pass


class ModelNotFoundError(FileNotFoundError):
    """Raised when a required model file cannot be found."""
    pass


class FeatureExtractionError(ValueError):
    """Raised when feature extraction fails."""
    pass

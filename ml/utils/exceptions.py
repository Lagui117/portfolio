"""
Custom ML Exceptions
Defines specific exceptions for ML pipeline errors.
"""


class MLBaseException(Exception):
    """Base exception for all ML-related errors."""
    pass


class MissingFeatureError(MLBaseException):
    """Raised when required features are missing from input data."""
    
    def __init__(self, missing_features):
        self.missing_features = missing_features
        message = f"Missing required features: {', '.join(missing_features)}"
        super().__init__(message)


class ModelNotLoadedError(MLBaseException):
    """Raised when attempting to use a model that hasn't been loaded."""
    
    def __init__(self, model_name):
        self.model_name = model_name
        message = f"Model '{model_name}' has not been loaded or does not exist"
        super().__init__(message)


class InvalidDataFormatError(MLBaseException):
    """Raised when input data format is invalid."""
    
    def __init__(self, expected_format, received_format):
        self.expected_format = expected_format
        self.received_format = received_format
        message = f"Invalid data format. Expected: {expected_format}, Received: {received_format}"
        super().__init__(message)


class InsufficientDataError(MLBaseException):
    """Raised when insufficient data is provided for prediction."""
    
    def __init__(self, minimum_required, received):
        self.minimum_required = minimum_required
        self.received = received
        message = f"Insufficient data points. Required: {minimum_required}, Received: {received}"
        super().__init__(message)

"""
Data Validation Utilities
Validates input data for sports and finance predictions.
"""

import numpy as np
from typing import Dict, List, Any
from .exceptions import MissingFeatureError, InvalidDataFormatError, InsufficientDataError


def validate_sports_data(data: Dict[str, Any], required_features: List[str]) -> Dict[str, Any]:
    """
    Validate sports match data.
    
    Args:
        data: Input data dictionary
        required_features: List of required feature names
        
    Returns:
        Validated and sanitized data dictionary
        
    Raises:
        MissingFeatureError: If required features are missing
        InvalidDataFormatError: If data format is invalid
    """
    if not isinstance(data, dict):
        raise InvalidDataFormatError("dictionary", type(data).__name__)
    
    # Check for missing features
    missing = [f for f in required_features if f not in data]
    if missing:
        raise MissingFeatureError(missing)
    
    # Validate data types and ranges
    validated_data = {}
    for key, value in data.items():
        if value is None:
            validated_data[key] = 0.0  # Default for missing values
        elif isinstance(value, (int, float)):
            validated_data[key] = float(value)
        else:
            try:
                validated_data[key] = float(value)
            except (ValueError, TypeError):
                raise InvalidDataFormatError(f"numeric for {key}", type(value).__name__)
    
    return validated_data


def validate_finance_data(data: Dict[str, Any], minimum_history: int = 5) -> Dict[str, Any]:
    """
    Validate finance asset data.
    
    Args:
        data: Input data dictionary with price history
        minimum_history: Minimum number of historical data points required
        
    Returns:
        Validated and sanitized data dictionary
        
    Raises:
        InsufficientDataError: If insufficient historical data
        InvalidDataFormatError: If data format is invalid
    """
    if not isinstance(data, dict):
        raise InvalidDataFormatError("dictionary", type(data).__name__)
    
    # Check for price history
    if 'prices' not in data:
        raise MissingFeatureError(['prices'])
    
    prices = data.get('prices', [])
    if not isinstance(prices, (list, np.ndarray)):
        raise InvalidDataFormatError("list or array for prices", type(prices).__name__)
    
    if len(prices) < minimum_history:
        raise InsufficientDataError(minimum_history, len(prices))
    
    # Validate all prices are numeric
    validated_prices = []
    for i, price in enumerate(prices):
        try:
            validated_prices.append(float(price))
        except (ValueError, TypeError):
            raise InvalidDataFormatError(f"numeric for price at index {i}", type(price).__name__)
    
    validated_data = {
        'prices': validated_prices,
        'volume': data.get('volume', [0] * len(validated_prices))
    }
    
    return validated_data


def check_feature_ranges(features: np.ndarray, feature_names: List[str]) -> bool:
    """
    Check if features are within reasonable ranges.
    
    Args:
        features: Feature array
        feature_names: Names of features
        
    Returns:
        True if all features are valid
    """
    if np.any(np.isnan(features)):
        return False
    
    if np.any(np.isinf(features)):
        return False
    
    return True

"""
Preprocessing Utilities
Data cleaning and transformation functions.
"""

import numpy as np
from typing import Union, List


def normalize_features(features: np.ndarray, scaler=None) -> Union[np.ndarray, tuple]:
    """
    Normalize features using StandardScaler.
    
    Args:
        features: Feature array to normalize
        scaler: Pre-fitted scaler (if None, returns unnormalized)
        
    Returns:
        Normalized features or (features, None) if no scaler
    """
    if scaler is None:
        return features, None
    
    return scaler.transform(features), scaler


def handle_missing_values(data: np.ndarray, strategy: str = 'mean') -> np.ndarray:
    """
    Handle missing values in data.
    
    Args:
        data: Input data array
        strategy: 'mean', 'median', or 'zero'
        
    Returns:
        Data with missing values filled
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    # Find missing values
    mask = np.isnan(data)
    
    if not np.any(mask):
        return data
    
    # Fill based on strategy
    if strategy == 'mean':
        fill_value = np.nanmean(data)
    elif strategy == 'median':
        fill_value = np.nanmedian(data)
    else:  # 'zero'
        fill_value = 0.0
    
    data[mask] = fill_value
    return data


def clip_outliers(data: np.ndarray, std_threshold: float = 3.0) -> np.ndarray:
    """
    Clip outliers beyond threshold standard deviations.
    
    Args:
        data: Input data array
        std_threshold: Number of standard deviations for clipping
        
    Returns:
        Data with outliers clipped
    """
    mean = np.mean(data)
    std = np.std(data)
    
    lower_bound = mean - (std_threshold * std)
    upper_bound = mean + (std_threshold * std)
    
    return np.clip(data, lower_bound, upper_bound)


def create_lagged_features(series: List[float], lags: List[int]) -> np.ndarray:
    """
    Create lagged features from time series.
    
    Args:
        series: Time series data
        lags: List of lag periods
        
    Returns:
        Array of lagged features
    """
    lagged = []
    for lag in lags:
        if lag < len(series):
            lagged.append(series[-lag])
        else:
            lagged.append(0.0)
    
    return np.array(lagged)

"""Models module."""
from app.models.user import User
from app.models.sport_event import SportEvent
from app.models.stock_asset import StockAsset
from app.models.prediction import Prediction
from app.models.consultation import Consultation

__all__ = ['User', 'SportEvent', 'StockAsset', 'Prediction', 'Consultation']

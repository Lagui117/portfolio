"""
Modele StockAsset pour les actifs financiers.
"""

from datetime import datetime, timezone
from app.core.database import db


class StockAsset(db.Model):
    """Modele pour les actifs boursiers."""
    
    __tablename__ = 'stock_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Informations de base
    name = db.Column(db.String(200), nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    exchange = db.Column(db.String(50), nullable=True)
    
    # Dernieres donnees connues
    last_price = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.BigInteger, nullable=True)
    volume = db.Column(db.BigInteger, nullable=True)
    
    # Indicateurs techniques (cache)
    ma_5 = db.Column(db.Float, nullable=True)
    ma_20 = db.Column(db.Float, nullable=True)
    ma_50 = db.Column(db.Float, nullable=True)
    rsi = db.Column(db.Float, nullable=True)
    volatility = db.Column(db.Float, nullable=True)
    
    # Metadata
    last_updated = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relations
    predictions = db.relationship(
        'Prediction',
        back_populates='stock_asset',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def to_dict(self) -> dict:
        """Convertit l'actif en dictionnaire."""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'name': self.name,
            'sector': self.sector,
            'industry': self.industry,
            'currency': self.currency,
            'exchange': self.exchange,
            'last_price': self.last_price,
            'market_cap': self.market_cap,
            'volume': self.volume,
            'indicators': {
                'MA_5': self.ma_5,
                'MA_20': self.ma_20,
                'MA_50': self.ma_50,
                'RSI': self.rsi,
                'volatility': self.volatility,
            },
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<StockAsset {self.ticker}>'

"""Stock asset model for financial data."""
from datetime import datetime
from app.core.database import db


class StockAsset(db.Model):
    """Model for storing stock/asset information."""
    
    __tablename__ = "stock_assets"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Asset identification
    symbol = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200))
    asset_type = db.Column(db.String(50), default='stock')  # stock, crypto, forex, index
    exchange = db.Column(db.String(50))
    currency = db.Column(db.String(10), default='USD')
    
    # Latest data
    last_price = db.Column(db.Float)
    last_update = db.Column(db.DateTime)
    
    # Metadata
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    market_cap = db.Column(db.BigInteger)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'asset_type': self.asset_type,
            'exchange': self.exchange,
            'currency': self.currency,
            'last_price': self.last_price,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
        }
    
    def __repr__(self):
        return f"<StockAsset {self.symbol}>"


class StockPrice(db.Model):
    """Model for storing historical stock prices."""
    
    __tablename__ = "stock_prices"
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    
    # Price data
    date = db.Column(db.Date, nullable=False, index=True)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
    
    # Adjusted prices
    adj_close = db.Column(db.Float)
    
    # Computed indicators (can be cached here)
    ma_5 = db.Column(db.Float)
    ma_20 = db.Column(db.Float)
    ma_50 = db.Column(db.Float)
    rsi = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('symbol', 'date', name='uq_symbol_date'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'date': self.date.isoformat() if self.date else None,
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume,
            'adj_close': self.adj_close,
        }
    
    def __repr__(self):
        return f"<StockPrice {self.symbol} {self.date}>"

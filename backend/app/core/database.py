"""
Configuration de la base de donnees SQLAlchemy.
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

# Instance SQLAlchemy
db = SQLAlchemy()


def init_db():
    """
    Initialise la base de donnees.
    Cree toutes les tables definies dans les modeles.
    """
    # Import des modeles pour les enregistrer avec SQLAlchemy
    from app.models.user import User
    from app.models.sport_event import SportEvent
    from app.models.stock_asset import StockAsset
    from app.models.prediction import Prediction
    from app.models.consultation import Consultation
    
    # Creer les tables
    db.create_all()
    logger.info('Base de donnees initialisee avec succes')


def get_db():
    """
    Retourne la session de base de donnees.
    Utilise pour l'injection de dependances.
    """
    return db.session

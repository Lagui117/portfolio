"""
Script d'initialisation de la base de donnees.
Cree toutes les tables necessaires.

Usage:
    python -m scripts.init_db
    ou
    from scripts.init_db import init_database; init_database()
"""

import os
import sys
import logging

# Ajouter le dossier backend au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """
    Initialise la base de donnees.
    Cree toutes les tables si elles n'existent pas.
    """
    from app.main import create_app
    from app.core.database import db
    
    # Import des modeles pour les enregistrer
    from app.models.user import User
    from app.models.sport_event import SportEvent
    from app.models.stock_asset import StockAsset
    from app.models.prediction import Prediction
    from app.models.consultation import Consultation
    
    app = create_app()
    
    with app.app_context():
        logger.info('Creation des tables...')
        db.create_all()
        logger.info('Base de donnees initialisee avec succes.')
        
        # Afficher les tables creees
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        logger.info(f'Tables creees: {tables}')
        
        return True


def reset_database():
    """
    Reinitialise la base de donnees.
    ATTENTION: Supprime toutes les donnees!
    """
    from app.main import create_app
    from app.core.database import db
    
    app = create_app()
    
    with app.app_context():
        logger.warning('Suppression de toutes les tables...')
        db.drop_all()
        logger.info('Tables supprimees.')
        
        logger.info('Recreation des tables...')
        db.create_all()
        logger.info('Base de donnees reinitialisee.')
        
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialisation de la base de donnees')
    parser.add_argument(
        '--reset', 
        action='store_true', 
        help='Reinitialiser la base (supprime toutes les donnees)'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        confirm = input('ATTENTION: Toutes les donnees seront supprimees. Confirmer? (yes/no): ')
        if confirm.lower() == 'yes':
            reset_database()
        else:
            print('Operation annulee.')
    else:
        init_database()

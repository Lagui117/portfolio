"""
Script de peuplement de la base de donnees.
Cree des utilisateurs de demo et des donnees d'exemple.

Usage:
    python -m scripts.seed_db
    ou
    from scripts.seed_db import seed_database; seed_database()
"""

import os
import sys
import logging
from datetime import datetime, timezone, timedelta

# Ajouter le dossier backend au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration des donnees de seed
ADMIN_USER = {
    'email': 'admin@predictwise.com',
    'username': 'admin',
    'password': 'Admin123!',
    'first_name': 'Admin',
    'last_name': 'PredictWise',
}

DEMO_USERS = [
    {
        'email': 'demo@predictwise.com',
        'username': 'demo',
        'password': 'Demo123!',
        'first_name': 'Demo',
        'last_name': 'User',
    },
    {
        'email': 'john@example.com',
        'username': 'john_doe',
        'password': 'John123!',
        'first_name': 'John',
        'last_name': 'Doe',
    },
    {
        'email': 'jane@example.com',
        'username': 'jane_smith',
        'password': 'Jane123!',
        'first_name': 'Jane',
        'last_name': 'Smith',
    },
]

DEMO_SPORT_EVENTS = [
    {
        'external_id': 'match_001',
        'home_team': 'Paris Saint-Germain',
        'away_team': 'Olympique de Marseille',
        'league': 'Ligue 1',
        'country': 'France',
        'event_date': datetime.now(timezone.utc) + timedelta(days=3),
        'status': 'scheduled',
    },
    {
        'external_id': 'match_002',
        'home_team': 'Real Madrid',
        'away_team': 'FC Barcelona',
        'league': 'La Liga',
        'country': 'Spain',
        'event_date': datetime.now(timezone.utc) + timedelta(days=5),
        'status': 'scheduled',
    },
    {
        'external_id': 'match_003',
        'home_team': 'Manchester United',
        'away_team': 'Liverpool FC',
        'league': 'Premier League',
        'country': 'England',
        'event_date': datetime.now(timezone.utc) + timedelta(days=7),
        'status': 'scheduled',
    },
    {
        'external_id': 'match_004',
        'home_team': 'Bayern Munich',
        'away_team': 'Borussia Dortmund',
        'league': 'Bundesliga',
        'country': 'Germany',
        'event_date': datetime.now(timezone.utc) - timedelta(days=2),
        'status': 'finished',
        'home_score': 2,
        'away_score': 1,
    },
]

DEMO_STOCK_ASSETS = [
    {
        'ticker': 'AAPL',
        'name': 'Apple Inc.',
        'sector': 'Technology',
        'exchange': 'NASDAQ',
        'currency': 'USD',
    },
    {
        'ticker': 'MSFT',
        'name': 'Microsoft Corporation',
        'sector': 'Technology',
        'exchange': 'NASDAQ',
        'currency': 'USD',
    },
    {
        'ticker': 'GOOGL',
        'name': 'Alphabet Inc.',
        'sector': 'Technology',
        'exchange': 'NASDAQ',
        'currency': 'USD',
    },
    {
        'ticker': 'TSLA',
        'name': 'Tesla Inc.',
        'sector': 'Consumer Cyclical',
        'exchange': 'NASDAQ',
        'currency': 'USD',
    },
    {
        'ticker': 'BTC-USD',
        'name': 'Bitcoin',
        'sector': 'Cryptocurrency',
        'exchange': 'CRYPTO',
        'currency': 'USD',
    },
]


def seed_database(reset_first=False):
    """
    Peuple la base de donnees avec des donnees de demonstration.
    
    Args:
        reset_first: Si True, vide les tables avant de peupler.
    """
    from app.main import create_app
    from app.core.database import db
    from app.models.user import User, UserRole
    from app.models.sport_event import SportEvent
    from app.models.stock_asset import StockAsset
    from app.models.prediction import Prediction
    from app.models.consultation import Consultation
    
    app = create_app()
    
    with app.app_context():
        if reset_first:
            logger.warning('Nettoyage des donnees existantes...')
            Prediction.query.delete()
            Consultation.query.delete()
            SportEvent.query.delete()
            StockAsset.query.delete()
            User.query.delete()
            db.session.commit()
            logger.info('Donnees supprimees.')
        
        # Creer l'admin
        logger.info('Creation de l\'administrateur...')
        admin = User.query.filter_by(email=ADMIN_USER['email']).first()
        if not admin:
            admin = User(
                email=ADMIN_USER['email'],
                username=ADMIN_USER['username'],
                first_name=ADMIN_USER['first_name'],
                last_name=ADMIN_USER['last_name'],
                role=UserRole.ADMIN
            )
            admin.set_password(ADMIN_USER['password'])
            db.session.add(admin)
            logger.info(f'Admin cree: {admin.email}')
        else:
            logger.info(f'Admin existe deja: {admin.email}')
        
        # Creer les utilisateurs demo
        logger.info('Creation des utilisateurs demo...')
        for user_data in DEMO_USERS:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=UserRole.USER
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                logger.info(f'User cree: {user.email}')
            else:
                logger.info(f'User existe deja: {user.email}')
        
        # Creer les evenements sportifs
        logger.info('Creation des evenements sportifs...')
        for event_data in DEMO_SPORT_EVENTS:
            event = SportEvent.query.filter_by(external_id=event_data['external_id']).first()
            if not event:
                event = SportEvent(**event_data)
                db.session.add(event)
                logger.info(f'Match cree: {event.home_team} vs {event.away_team}')
            else:
                logger.info(f'Match existe deja: {event.home_team} vs {event.away_team}')
        
        # Creer les actifs financiers
        logger.info('Creation des actifs financiers...')
        for asset_data in DEMO_STOCK_ASSETS:
            asset = StockAsset.query.filter_by(ticker=asset_data['ticker']).first()
            if not asset:
                asset = StockAsset(**asset_data)
                db.session.add(asset)
                logger.info(f'Asset cree: {asset.ticker} - {asset.name}')
            else:
                logger.info(f'Asset existe deja: {asset.ticker}')
        
        # Commit final
        db.session.commit()
        logger.info('Base de donnees peuplee avec succes!')
        
        # Afficher le resume
        print('\n' + '='*50)
        print('RESUME DU SEED')
        print('='*50)
        print(f'Utilisateurs: {User.query.count()}')
        print(f'  - Admin: {User.query.filter_by(role=UserRole.ADMIN).count()}')
        print(f'  - Users: {User.query.filter_by(role=UserRole.USER).count()}')
        print(f'Evenements sportifs: {SportEvent.query.count()}')
        print(f'Actifs financiers: {StockAsset.query.count()}')
        print('='*50)
        print('\nCOMPTES DE TEST:')
        print('-'*50)
        print(f'Admin:  email={ADMIN_USER["email"]}  password={ADMIN_USER["password"]}')
        print(f'Demo:   email={DEMO_USERS[0]["email"]}  password={DEMO_USERS[0]["password"]}')
        print('='*50 + '\n')
        
        return True


def create_admin(email=None, username=None, password=None):
    """
    Cree un compte admin personnalise.
    """
    from app.main import create_app
    from app.core.database import db
    from app.models.user import User, UserRole
    
    email = email or input('Email: ')
    username = username or input('Username: ')
    password = password or input('Password: ')
    
    app = create_app()
    
    with app.app_context():
        if User.query.filter_by(email=email).first():
            logger.error(f'Email {email} deja utilise')
            return False
        
        if User.query.filter_by(username=username).first():
            logger.error(f'Username {username} deja utilise')
            return False
        
        admin = User(
            email=email,
            username=username,
            role=UserRole.ADMIN
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        logger.info(f'Admin cree: {email}')
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Peuplement de la base de donnees')
    parser.add_argument(
        '--reset', 
        action='store_true', 
        help='Vider les tables avant de peupler'
    )
    parser.add_argument(
        '--create-admin', 
        action='store_true', 
        help='Creer un admin personnalise'
    )
    
    args = parser.parse_args()
    
    if args.create_admin:
        create_admin()
    else:
        if args.reset:
            confirm = input('ATTENTION: Toutes les donnees seront supprimees. Confirmer? (yes/no): ')
            if confirm.lower() != 'yes':
                print('Operation annulee.')
                sys.exit(0)
        
        seed_database(reset_first=args.reset)

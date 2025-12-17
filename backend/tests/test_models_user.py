"""
Tests pour les modeles SQLAlchemy.
- User
- Prediction
- Consultation
"""

import pytest
from datetime import datetime, timezone

from app.models.user import User
from app.models.prediction import Prediction
from app.models.consultation import Consultation


class TestUserModel:
    """Tests pour le modele User."""
    
    def test_create_user(self, db):
        """Creation d'un utilisateur avec donnees minimales."""
        user = User(
            email='newuser@example.com',
            username='newuser'
        )
        user.set_password('SecurePassword123!')
        
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.email == 'newuser@example.com'
        assert user.username == 'newuser'
        assert user.password_hash is not None
        assert user.is_active is True
        assert user.is_admin is False
    
    def test_user_check_password_correct(self, db):
        """Verification d'un mot de passe correct."""
        user = User(email='check@example.com', username='checkuser')
        user.set_password('CorrectPassword123!')
        
        db.session.add(user)
        db.session.commit()
        
        assert user.check_password('CorrectPassword123!') is True
    
    def test_user_check_password_incorrect(self, db):
        """Verification d'un mot de passe incorrect."""
        user = User(email='check2@example.com', username='checkuser2')
        user.set_password('CorrectPassword123!')
        
        db.session.add(user)
        db.session.commit()
        
        assert user.check_password('WrongPassword!') is False
    
    def test_user_to_dict(self, db):
        """Conversion utilisateur en dictionnaire."""
        user = User(
            email='dict@example.com',
            username='dictuser',
            first_name='Test',
            last_name='User'
        )
        user.set_password('Password123!')
        
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        
        assert 'id' in user_dict
        assert user_dict['email'] == 'dict@example.com'
        assert 'password_hash' not in user_dict


class TestPredictionModel:
    """Tests pour le modele Prediction."""
    
    def test_create_sports_prediction(self, db, sample_user):
        """Creation d'une prediction sportive."""
        prediction = Prediction(
            user_id=sample_user.id,
            prediction_type='sports',
            external_match_id='match_12345',
            model_score=0.72,
            prediction_value='0.72',
            confidence=0.75
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        assert prediction.id is not None
        assert prediction.prediction_type == 'sports'
        assert prediction.model_score == 0.72
    
    def test_create_finance_prediction(self, db, sample_user):
        """Creation d'une prediction financiere."""
        prediction = Prediction(
            user_id=sample_user.id,
            prediction_type='finance',
            ticker='AAPL',
            model_score=0.65,
            prediction_value='UP',
            confidence=0.68
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        assert prediction.id is not None
        assert prediction.ticker == 'AAPL'


class TestConsultationModel:
    """Tests pour le modele Consultation."""
    
    def test_create_consultation(self, db, sample_user):
        """Creation d'une consultation."""
        consultation = Consultation(
            user_id=sample_user.id,
            consultation_type='sports',
            endpoint='/api/v1/sports/predict/match_123',
            success=True
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        assert consultation.id is not None
        assert consultation.consultation_type == 'sports'
        assert consultation.success is True

"""
Tests pour l'endpoint AI (/api/v1/ai).
Vérifie le chat et l'analyse IA.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.main import create_app
from app.models.user import User


class TestAIEndpoints:
    """Tests pour les endpoints AI."""
    
    @pytest.fixture
    def app(self):
        """Crée une app de test."""
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-secret-key'
        })
        return app
    
    @pytest.fixture
    def client(self, app):
        """Client de test."""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        """Headers d'authentification pour les tests."""
        with app.app_context():
            from app.core.database import db
            from app.core.security import create_access_token
            
            db.create_all()
            
            # Créer un utilisateur de test
            user = User(
                email='test@example.com',
                username='testuser',
                role='user'
            )
            user.set_password('TestPass123!')
            db.session.add(user)
            db.session.commit()
            
            # Générer un token
            token = create_access_token(user.id, user.role)
            
            return {'Authorization': f'Bearer {token}'}
    
    # ===== HEALTH CHECK =====
    
    def test_health_check_no_auth(self, client):
        """Health check ne requiert pas d'auth."""
        response = client.get('/api/v1/ai/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'openai_configured' in data
    
    def test_health_check_shows_service_status(self, client):
        """Health check montre le status du service."""
        response = client.get('/api/v1/ai/health')
        data = response.get_json()
        
        assert data['service'] == 'ai'
        assert 'features' in data
        assert 'timestamp' in data
    
    # ===== CHAT ENDPOINT =====
    
    def test_chat_requires_auth(self, client):
        """Chat requiert une authentification."""
        response = client.post(
            '/api/v1/ai/chat',
            json={'message': 'Hello'}
        )
        
        assert response.status_code == 401
    
    def test_chat_requires_message(self, client, auth_headers):
        """Chat requiert un message."""
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_chat_empty_message_rejected(self, client, auth_headers):
        """Message vide est rejeté."""
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': '   '}
        )
        
        assert response.status_code == 400
    
    def test_chat_message_too_long(self, client, auth_headers):
        """Message trop long est rejeté."""
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': 'x' * 2001}
        )
        
        assert response.status_code == 400
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_chat_success(self, mock_process, client, auth_headers):
        """Chat réussit avec un message valide."""
        mock_process.return_value = {
            'response': {'content': 'Bonjour, comment puis-je vous aider?'},
            'conversation_id': 'conv123',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': 'Bonjour'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'answer' in data
        assert data['answer'] == 'Bonjour, comment puis-je vous aider?'
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_chat_with_context(self, mock_process, client, auth_headers):
        """Chat avec contexte."""
        mock_process.return_value = {
            'response': {'content': 'Basé sur votre analyse...'},
            'conversation_id': 'conv123',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={
                'message': 'Que penses-tu de cette action?',
                'context': {
                    'current_analysis': {
                        'type': 'finance',
                        'symbol': 'AAPL',
                        'price': 180.0
                    },
                    'page': 'finance_dashboard'
                }
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['used_context'] is True
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_chat_response_format(self, mock_process, client, auth_headers):
        """Format de réponse du chat."""
        mock_process.return_value = {
            'response': {'content': 'Réponse test'},
            'conversation_id': 'conv456',
            'message_count': 2
        }
        
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': 'Test'}
        )
        
        data = response.get_json()
        
        assert 'answer' in data
        assert 'confidence' in data
        assert 'used_context' in data
        assert 'citations' in data
        assert 'conversation_id' in data
        assert 'metadata' in data
        assert isinstance(data['metadata'], dict)
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_chat_error_handling(self, mock_process, client, auth_headers):
        """Gestion des erreurs du chat."""
        mock_process.side_effect = Exception("Service unavailable")
        
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': 'Test'}
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        # Devrait quand même fournir une réponse de fallback
        assert 'answer' in data
    
    # ===== ANALYZE ENDPOINT =====
    
    def test_analyze_requires_auth(self, client):
        """Analyze requiert une authentification."""
        response = client.post(
            '/api/v1/ai/analyze',
            json={'type': 'finance', 'data': {}}
        )
        
        assert response.status_code == 401
    
    def test_analyze_requires_type_and_data(self, client, auth_headers):
        """Analyze requiert type et data."""
        response = client.post(
            '/api/v1/ai/analyze',
            headers=auth_headers,
            json={'type': 'finance'}  # Missing 'data'
        )
        
        assert response.status_code == 400
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_analyze_finance_success(self, mock_process, client, auth_headers):
        """Analyse finance réussit."""
        mock_process.return_value = {
            'response': {'content': 'AAPL montre des signaux positifs...'},
            'conversation_id': 'conv789',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/analyze',
            headers=auth_headers,
            json={
                'type': 'finance',
                'data': {
                    'symbol': 'AAPL',
                    'current_price': 180.0,
                    'change_percent': 2.5,
                    'indicators': {'rsi_14': 65}
                }
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'analysis' in data
        assert data['type'] == 'finance'
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_analyze_sports_success(self, mock_process, client, auth_headers):
        """Analyse sports réussit."""
        mock_process.return_value = {
            'response': {'content': 'Le PSG est favori...'},
            'conversation_id': 'conv789',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/analyze',
            headers=auth_headers,
            json={
                'type': 'sports',
                'data': {
                    'home_team': {'name': 'PSG'},
                    'away_team': {'name': 'OM'},
                    'competition': 'Ligue 1'
                }
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'analysis' in data
        assert data['type'] == 'sports'
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_analyze_with_custom_question(self, mock_process, client, auth_headers):
        """Analyse avec question personnalisée."""
        mock_process.return_value = {
            'response': {'content': 'Réponse personnalisée'},
            'conversation_id': 'conv789',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/analyze',
            headers=auth_headers,
            json={
                'type': 'finance',
                'data': {'symbol': 'TSLA'},
                'question': 'Est-ce le bon moment pour acheter?'
            }
        )
        
        assert response.status_code == 200
        # Vérifier que la question personnalisée a été utilisée
        mock_process.assert_called_once()
        call_args = mock_process.call_args
        assert 'acheter' in call_args[1]['message'] or 'acheter' in str(call_args)
    
    # ===== LEGACY ENDPOINT =====
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_legacy_gpt_analyze_works(self, mock_process, client, auth_headers):
        """Endpoint legacy fonctionne."""
        mock_process.return_value = {
            'response': {'content': 'Legacy response'},
            'conversation_id': 'conv000',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/gpt/analyze',
            headers=auth_headers,
            json={
                'type': 'finance',
                'data': {'symbol': 'GOOGL'}
            }
        )
        
        assert response.status_code == 200


class TestAIConfidence:
    """Tests pour le calcul de confiance."""
    
    @pytest.fixture
    def app(self):
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-secret-key'
        })
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        with app.app_context():
            from app.core.database import db
            from app.core.security import create_access_token
            
            db.create_all()
            user = User(email='conf@test.com', username='confuser', role='user')
            user.set_password('TestPass123!')
            db.session.add(user)
            db.session.commit()
            token = create_access_token(user.id, user.role)
            return {'Authorization': f'Bearer {token}'}
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_confidence_higher_with_context(self, mock_process, client, auth_headers):
        """Confiance plus élevée avec contexte."""
        mock_process.return_value = {
            'response': {'content': 'Une longue réponse détaillée avec beaucoup d\'informations pertinentes pour l\'utilisateur.'},
            'conversation_id': 'conv1',
            'message_count': 1
        }
        
        # Sans contexte
        resp1 = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': 'Question'}
        )
        conf_without = resp1.get_json()['confidence']
        
        # Avec contexte
        resp2 = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={
                'message': 'Question',
                'context': {
                    'current_analysis': {'type': 'finance', 'symbol': 'AAPL'}
                }
            }
        )
        conf_with = resp2.get_json()['confidence']
        
        assert conf_with >= conf_without
    
    @patch('app.services.chat_service.chat_service.process_message')
    def test_confidence_lower_for_fallback(self, mock_process, client, auth_headers):
        """Confiance plus basse pour réponse fallback."""
        mock_process.return_value = {
            'response': {'content': 'Le service IA complet n\'est pas disponible, voici une réponse en mode dégradé.'},
            'conversation_id': 'conv2',
            'message_count': 1
        }
        
        response = client.post(
            '/api/v1/ai/chat',
            headers=auth_headers,
            json={'message': 'Test'}
        )
        
        data = response.get_json()
        # La confiance devrait être pénalisée pour les réponses fallback
        assert data['confidence'] < 0.5

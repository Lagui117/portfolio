"""
Tests pour les endpoints d'authentification.
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
"""

import pytest
import json
from datetime import timedelta

from app.core.security import create_access_token


class TestRegisterEndpoint:
    """Tests pour l'endpoint d'inscription."""
    
    def test_register_success(self, client, db):
        """Inscription reussie avec donnees valides."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        json_data = response.get_json()
        
        assert 'access_token' in json_data
        assert 'user' in json_data
        assert json_data['user']['email'] == 'newuser@example.com'
        assert json_data['user']['username'] == 'newuser'
        assert 'password_hash' not in json_data['user']
    
    def test_register_email_already_exists(self, client, sample_user):
        """Inscription echouee - email deja utilise."""
        data = {
            'email': 'test@example.com',  # Email du sample_user
            'username': 'differentuser',
            'password': 'SecurePass123!'
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'email' in json_data['error']['message'].lower()
    
    def test_register_username_already_exists(self, client, sample_user):
        """Inscription echouee - username deja utilise."""
        data = {
            'email': 'different@example.com',
            'username': 'testuser',  # Username du sample_user
            'password': 'SecurePass123!'
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'username' in json_data['error']['message'].lower()
    
    def test_register_missing_required_fields(self, client):
        """Inscription echouee - champs requis manquants."""
        # Email manquant
        data = {'username': 'user1', 'password': 'Pass123!'}
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Username manquant
        data = {'email': 'user@example.com', 'password': 'Pass123!'}
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Password manquant
        data = {'email': 'user@example.com', 'username': 'user1'}
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_register_invalid_email_format(self, client):
        """Inscription echouee - format email invalide."""
        data = {
            'email': 'not-an-email',
            'username': 'user1',
            'password': 'Pass123!'
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_register_password_too_short(self, client):
        """Inscription echouee - mot de passe trop court."""
        data = {
            'email': 'user@example.com',
            'username': 'user1',
            'password': '123'  # Trop court
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_register_no_json_data(self, client):
        """Inscription echouee - pas de JSON."""
        response = client.post('/api/v1/auth/register')
        
        # Flask retourne 415 (Unsupported Media Type) sans Content-Type: application/json
        assert response.status_code == 415


class TestLoginEndpoint:
    """Tests pour l'endpoint de connexion."""
    
    def test_login_success_with_email(self, client, sample_user):
        """Connexion reussie avec email."""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePassword123!'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        assert 'access_token' in json_data
        assert 'user' in json_data
        assert json_data['user']['email'] == 'test@example.com'
    
    def test_login_success_with_username(self, client, sample_user):
        """Connexion reussie avec username."""
        data = {
            'username': 'testuser',
            'password': 'SecurePassword123!'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['user']['username'] == 'testuser'
    
    def test_login_wrong_password(self, client, sample_user):
        """Connexion echouee - mauvais mot de passe."""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword!'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_login_user_not_found(self, client):
        """Connexion echouee - utilisateur inexistant."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client, sample_inactive_user):
        """Connexion echouee - compte inactif."""
        data = {
            'email': 'inactive@example.com',
            'password': 'Password123!'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        json_data = response.get_json()
        # Le message peut contenir "inactive" ou "deactivated"
        assert 'deactivated' in json_data['error']['message'].lower() or 'inactive' in json_data['error']['message'].lower()
    
    def test_login_missing_credentials(self, client):
        """Connexion echouee - credentials manquantes."""
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({'password': 'Pass123!'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestMeEndpoint:
    """Tests pour l'endpoint GET /auth/me."""
    
    def test_me_with_valid_token(self, client, auth_headers, sample_user):
        """Recuperation profil avec token valide."""
        response = client.get(
            '/api/v1/auth/me',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        assert 'user' in json_data
        assert json_data['user']['email'] == 'test@example.com'
        assert json_data['user']['username'] == 'testuser'
    
    def test_me_with_stats_parameter(self, client, auth_headers):
        """Recuperation profil avec statistiques."""
        response = client.get(
            '/api/v1/auth/me?stats=true',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        assert 'user' in json_data
        # Les stats sont au niveau racine, pas dans user
        assert 'stats' in json_data
        assert 'total_predictions' in json_data['stats']
        assert 'total_consultations' in json_data['stats']
    
    def test_me_without_token(self, client):
        """Acces refuse sans token."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_me_with_invalid_token_format(self, client):
        """Acces refuse avec format token invalide."""
        headers = {'Authorization': 'InvalidTokenFormat'}
        
        response = client.get(
            '/api/v1/auth/me',
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_me_with_expired_token(self, client, app, sample_user):
        """Acces refuse avec token expire."""
        # Creer un token expire
        with app.app_context():
            expired_token = create_access_token(
                sample_user.id,
                expires_delta=timedelta(seconds=-1)
            )
        
        headers = {
            'Authorization': f'Bearer {expired_token}',
            'Content-Type': 'application/json'
        }
        
        response = client.get(
            '/api/v1/auth/me',
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_me_with_malformed_token(self, client):
        """Acces refuse avec token malformed."""
        headers = {
            'Authorization': 'Bearer this.is.not.a.valid.jwt',
            'Content-Type': 'application/json'
        }
        
        response = client.get(
            '/api/v1/auth/me',
            headers=headers
        )
        
        assert response.status_code == 401

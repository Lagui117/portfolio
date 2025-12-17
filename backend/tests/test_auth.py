"""
Tests pour les endpoints d'authentification.
"""

import pytest


class TestAuthRegister:
    """Tests pour l'endpoint /api/v1/auth/register."""
    
    def test_register_success(self, client, sample_user_data):
        """Test inscription reussie."""
        response = client.post('/api/v1/auth/register', json=sample_user_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
        assert data['user']['username'] == sample_user_data['username']
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """Test inscription avec email deja utilise."""
        # Premier enregistrement
        client.post('/api/v1/auth/register', json=sample_user_data)
        
        # Deuxieme enregistrement avec meme email
        sample_user_data['username'] = 'different_user'
        response = client.post('/api/v1/auth/register', json=sample_user_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'email' in data['error'].lower()
    
    def test_register_duplicate_username(self, client, sample_user_data):
        """Test inscription avec username deja pris."""
        # Premier enregistrement
        client.post('/api/v1/auth/register', json=sample_user_data)
        
        # Deuxieme enregistrement avec meme username
        sample_user_data['email'] = 'different@example.com'
        response = client.post('/api/v1/auth/register', json=sample_user_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_missing_fields(self, client):
        """Test inscription avec champs manquants."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_invalid_email(self, client, sample_user_data):
        """Test inscription avec email invalide."""
        sample_user_data['email'] = 'invalid-email'
        response = client.post('/api/v1/auth/register', json=sample_user_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'email' in data['error'].lower()
    
    def test_register_weak_password(self, client, sample_user_data):
        """Test inscription avec mot de passe faible."""
        sample_user_data['password'] = '123'
        response = client.post('/api/v1/auth/register', json=sample_user_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestAuthLogin:
    """Tests pour l'endpoint /api/v1/auth/login."""
    
    def test_login_success(self, client, sample_user_data):
        """Test connexion reussie."""
        # Creer l'utilisateur
        client.post('/api/v1/auth/register', json=sample_user_data)
        
        # Connexion
        response = client.post('/api/v1/auth/login', json={
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_login_wrong_password(self, client, sample_user_data):
        """Test connexion avec mauvais mot de passe."""
        # Creer l'utilisateur
        client.post('/api/v1/auth/register', json=sample_user_data)
        
        # Connexion avec mauvais password
        response = client.post('/api/v1/auth/login', json={
            'email': sample_user_data['email'],
            'password': 'WrongPassword123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_nonexistent_user(self, client):
        """Test connexion avec utilisateur inexistant."""
        response = client.post('/api/v1/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_missing_fields(self, client):
        """Test connexion avec champs manquants."""
        response = client.post('/api/v1/auth/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestAuthMe:
    """Tests pour l'endpoint /api/v1/auth/me."""
    
    def test_me_authenticated(self, client, auth_headers):
        """Test /me avec utilisateur authentifie."""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_me_without_token(self, client):
        """Test /me sans token."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_me_invalid_token(self, client):
        """Test /me avec token invalide."""
        response = client.get('/api/v1/auth/me', headers={
            'Authorization': 'Bearer invalid-token-here'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_me_with_stats(self, client, auth_headers):
        """Test /me avec statistiques."""
        response = client.get('/api/v1/auth/me?stats=true', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert 'stats' in data['user']

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


class TestUpdateMeEndpoint:
    """Tests pour PUT /api/v1/auth/me (mise à jour profil)."""
    
    def test_update_profile_first_last_name(self, client, auth_headers):
        """Mise à jour first_name et last_name."""
        response = client.put(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'first_name': 'NewFirst', 'last_name': 'NewLast'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['first_name'] == 'NewFirst'
        assert data['user']['last_name'] == 'NewLast'
    
    def test_update_profile_email(self, client, auth_headers, db):
        """Mise à jour email."""
        response = client.put(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'email': 'newemail@example.com'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'newemail@example.com'
    
    def test_update_profile_email_already_taken(self, client, auth_headers, db, app):
        """Email déjà utilisé par un autre user."""
        from app.models.user import User
        
        # Créer un autre user avec l'email cible
        other = User(email='taken@example.com', username='otheruser')
        other.set_password('Password123!')
        db.session.add(other)
        db.session.commit()
        
        response = client.put(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'email': 'taken@example.com'}
        )
        
        assert response.status_code == 400
        assert 'email' in response.get_json()['error']['message'].lower()
    
    def test_update_profile_username(self, client, auth_headers, db):
        """Mise à jour username."""
        response = client.put(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'username': 'newusername'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'newusername'
    
    def test_update_profile_username_already_taken(self, client, auth_headers, db, app):
        """Username déjà pris par un autre user."""
        from app.models.user import User
        
        other = User(email='other@example.com', username='takenuser')
        other.set_password('Password123!')
        db.session.add(other)
        db.session.commit()
        
        response = client.put(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={'username': 'takenuser'}
        )
        
        assert response.status_code == 400
        assert 'username' in response.get_json()['error']['message'].lower()
    
    def test_update_profile_empty_data(self, client, auth_headers):
        """Mise à jour sans données (no-op OK)."""
        response = client.put(
            '/api/v1/auth/me',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 200
    
    def test_update_profile_no_auth(self, client):
        """Mise à jour profil sans auth → 401."""
        response = client.put(
            '/api/v1/auth/me',
            json={'first_name': 'Test'}
        )
        
        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Tests pour PUT /api/v1/auth/password."""
    
    def test_change_password_success(self, client, auth_headers, sample_user, db):
        """Changement de mot de passe réussi."""
        response = client.put(
            '/api/v1/auth/password',
            headers=auth_headers,
            json={
                'current_password': 'SecurePassword123!',
                'new_password': 'NewSecurePass456!'
            }
        )
        
        assert response.status_code == 200
        assert 'successfully' in response.get_json()['message'].lower()
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Mot de passe actuel incorrect."""
        response = client.put(
            '/api/v1/auth/password',
            headers=auth_headers,
            json={
                'current_password': 'WrongPassword!',
                'new_password': 'NewPassword456!'
            }
        )
        
        assert response.status_code == 401
        assert 'current' in response.get_json()['error']['message'].lower()
    
    def test_change_password_too_short(self, client, auth_headers):
        """Nouveau mot de passe trop court."""
        response = client.put(
            '/api/v1/auth/password',
            headers=auth_headers,
            json={
                'current_password': 'SecurePassword123!',
                'new_password': '123'  # trop court
            }
        )
        
        assert response.status_code == 400
    
    def test_change_password_missing_fields(self, client, auth_headers):
        """Champs requis manquants."""
        # Sans current_password
        response = client.put(
            '/api/v1/auth/password',
            headers=auth_headers,
            json={'new_password': 'NewPassword456!'}
        )
        assert response.status_code == 400
        
        # Sans new_password
        response = client.put(
            '/api/v1/auth/password',
            headers=auth_headers,
            json={'current_password': 'SecurePassword123!'}
        )
        assert response.status_code == 400
    
    def test_change_password_no_json(self, client, auth_headers):
        """Pas de JSON → 400."""
        response = client.put(
            '/api/v1/auth/password',
            headers=auth_headers
        )
        
        # Sans Content-Type JSON, Flask peut retourner 400 ou 415
        assert response.status_code in [400, 415]
    
    def test_change_password_no_auth(self, client):
        """Changement de mot de passe sans auth → 401."""
        response = client.put(
            '/api/v1/auth/password',
            json={
                'current_password': 'OldPass!',
                'new_password': 'NewPass!'
            }
        )
        
        assert response.status_code == 401


class TestTokenRequiredDecorator:
    """Tests pour le décorateur token_required."""
    
    def test_invalid_authorization_header_format(self, client):
        """Header Authorization sans Bearer → 401 (token invalide)."""
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': 'NotBearer token123'}
        )
        
        # Le token "token123" seul est invalide, donc 401
        assert response.status_code == 401
    
    def test_empty_bearer_token(self, client):
        """Bearer sans token → 400 ou 401."""
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': 'Bearer '}
        )
        
        assert response.status_code in [400, 401]
    
    def test_token_for_deleted_user(self, client, app, db):
        """Token valide mais user supprimé → 401."""
        from app.models.user import User
        
        # Créer un user
        user = User(email='todelete@test.com', username='todelete')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Générer un token
        with app.app_context():
            token = create_access_token(user_id)
        
        # Supprimer le user
        db.session.delete(user)
        db.session.commit()
        
        # Utiliser le token
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 401
    
    def test_token_for_inactive_user(self, client, app, db):
        """Token valide mais user inactif → 401."""
        from app.models.user import User
        
        # Créer user actif, puis le désactiver AVANT de générer le token
        user = User(email='willbeinactive@test.com', username='willbeinactive', is_active=False)
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(user.id)
        
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 401


class TestAdminRequiredDecorator:
    """Tests pour le décorateur admin_required."""
    
    def test_admin_access_ok(self, client, app, db):
        """Admin peut accéder aux routes admin."""
        from app.models.user import User, UserRole
        
        admin = User(email='admintest@test.com', username='admintest', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
    
    def test_user_denied_admin_route(self, client, auth_headers):
        """User normal ne peut pas accéder aux routes admin."""
        response = client.get(
            '/api/v1/admin/users',
            headers=auth_headers
        )
        
        assert response.status_code == 403


class TestRegisterEdgeCases:
    """Edge cases pour l'inscription."""
    
    def test_register_email_normalization(self, client, db):
        """Email normalisé en minuscules."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': 'UPPERCASE@EXAMPLE.COM',
                'username': 'uppercaseuser',
                'password': 'Password123!'
            }
        )
        
        assert response.status_code == 201
        assert response.get_json()['user']['email'] == 'uppercase@example.com'
    
    def test_register_with_optional_fields_only(self, client, db):
        """Inscription sans first_name/last_name OK."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': 'minimal@test.com',
                'username': 'minimal',
                'password': 'Password123!'
            }
        )
        
        assert response.status_code == 201


class TestLoginEdgeCases:
    """Edge cases pour la connexion."""
    
    def test_login_no_json_body(self, client):
        """Login sans body JSON."""
        response = client.post(
            '/api/v1/auth/login',
            content_type='application/json'
        )
        
        assert response.status_code == 400

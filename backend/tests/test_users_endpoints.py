"""
Tests pour les endpoints de gestion des utilisateurs (admin).
"""

import pytest
from app.models.user import User, UserRole
from app.core.security import create_access_token


class TestUsersEndpointAdminOnly:
    """Tests pour verifier que les endpoints users sont reserves aux admins."""
    
    def test_list_users_requires_admin(self, client, sample_user, db):
        """Un utilisateur normal ne peut pas lister les users."""
        token = create_access_token(sample_user.id, sample_user.role)
        
        response = client.get(
            '/api/v1/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 403
        assert 'Admin access required' in response.json['error']['message']
    
    def test_list_users_without_auth(self, client):
        """Liste sans authentification retourne 401."""
        response = client.get('/api/v1/users')
        
        assert response.status_code == 401


class TestUsersEndpointWithAdmin:
    """Tests des endpoints users avec un admin."""
    
    @pytest.fixture
    def admin_user(self, db):
        """Cree un utilisateur admin pour les tests."""
        admin = User(
            email='testadmin@example.com',
            username='testadmin',
            role=UserRole.ADMIN
        )
        admin.set_password('AdminPassword123!')
        db.session.add(admin)
        db.session.commit()
        return admin
    
    @pytest.fixture
    def admin_token(self, admin_user):
        """Token JWT pour l'admin."""
        return create_access_token(admin_user.id, admin_user.role)
    
    def test_list_users_success(self, client, admin_token, db):
        """Un admin peut lister les utilisateurs."""
        response = client.get(
            '/api/v1/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'users' in response.json
        assert 'pagination' in response.json
    
    def test_list_users_with_pagination(self, client, admin_token, db):
        """Test de la pagination."""
        # Creer plusieurs utilisateurs
        for i in range(15):
            user = User(
                email=f'paginuser{i}@example.com',
                username=f'paginuser{i}'
            )
            user.set_password('Password123!')
            db.session.add(user)
        db.session.commit()
        
        response = client.get(
            '/api/v1/users?page=1&per_page=5',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert len(response.json['users']) == 5
        assert response.json['pagination']['page'] == 1
        assert response.json['pagination']['per_page'] == 5
    
    def test_list_users_with_role_filter(self, client, admin_token, admin_user, sample_user, db):
        """Test du filtrage par role."""
        response = client.get(
            '/api/v1/users?role=admin',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        # Tous les users retournes doivent etre admin
        for user in response.json['users']:
            assert user['is_admin'] is True
    
    def test_get_user_details(self, client, admin_token, sample_user, db):
        """Un admin peut voir les details d'un utilisateur."""
        response = client.get(
            f'/api/v1/users/{sample_user.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['user']['id'] == sample_user.id
        assert response.json['user']['email'] == sample_user.email
    
    def test_get_user_not_found(self, client, admin_token):
        """Retourne 404 si utilisateur non trouve."""
        response = client.get(
            '/api/v1/users/99999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 404
    
    def test_promote_user(self, client, admin_token, sample_user, db):
        """Un admin peut promouvoir un utilisateur."""
        assert sample_user.is_admin is False
        
        response = client.post(
            f'/api/v1/users/{sample_user.id}/promote',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Rafraichir depuis la DB
        db.session.refresh(sample_user)
        assert sample_user.is_admin is True
    
    def test_demote_user(self, client, admin_token, db):
        """Un admin peut revoquer les droits d'un autre admin."""
        # Creer un autre admin
        other_admin = User(
            email='otheradmin@example.com',
            username='otheradmin',
            role=UserRole.ADMIN
        )
        other_admin.set_password('Password123!')
        db.session.add(other_admin)
        db.session.commit()
        
        response = client.post(
            f'/api/v1/users/{other_admin.id}/demote',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        db.session.refresh(other_admin)
        assert other_admin.is_admin is False
    
    def test_cannot_demote_self(self, client, admin_token, admin_user, db):
        """Un admin ne peut pas se revoquer lui-meme."""
        response = client.post(
            f'/api/v1/users/{admin_user.id}/demote',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 400
        assert 'propres droits' in response.json['error']['message']
    
    def test_toggle_user_active(self, client, admin_token, sample_user, db):
        """Un admin peut desactiver/activer un utilisateur."""
        assert sample_user.is_active is True
        
        # Desactiver
        response = client.put(
            f'/api/v1/users/{sample_user.id}',
            json={'is_active': False},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        db.session.refresh(sample_user)
        assert sample_user.is_active is False
    
    def test_delete_user(self, client, admin_token, db):
        """Un admin peut supprimer un utilisateur."""
        user_to_delete = User(
            email='todelete@example.com',
            username='todelete'
        )
        user_to_delete.set_password('Password123!')
        db.session.add(user_to_delete)
        db.session.commit()
        user_id = user_to_delete.id
        
        response = client.delete(
            f'/api/v1/users/{user_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verifier que l'utilisateur n'existe plus
        deleted = db.session.get(User, user_id)
        assert deleted is None
    
    def test_cannot_delete_self(self, client, admin_token, admin_user, db):
        """Un admin ne peut pas supprimer son propre compte."""
        response = client.delete(
            f'/api/v1/users/{admin_user.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 400
    
    def test_get_stats(self, client, admin_token, db):
        """Un admin peut voir les statistiques globales."""
        response = client.get(
            '/api/v1/users/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'stats' in response.json
        assert 'total_users' in response.json['stats']
        assert 'active_users' in response.json['stats']
        assert 'admin_users' in response.json['stats']


class TestProfileEndpoints:
    """Tests pour les endpoints de profil."""
    
    def test_update_profile(self, client, sample_user, db):
        """Un utilisateur peut mettre a jour son profil."""
        token = create_access_token(sample_user.id, sample_user.role)
        
        response = client.put(
            '/api/v1/auth/me',
            json={
                'first_name': 'Updated',
                'last_name': 'Name'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert response.json['user']['first_name'] == 'Updated'
        assert response.json['user']['last_name'] == 'Name'
    
    def test_update_profile_email_unique(self, client, sample_user, db):
        """Impossible de prendre un email deja utilise."""
        # Creer un autre user
        other = User(email='other@example.com', username='otheruser')
        other.set_password('Password123!')
        db.session.add(other)
        db.session.commit()
        
        token = create_access_token(sample_user.id, sample_user.role)
        
        response = client.put(
            '/api/v1/auth/me',
            json={'email': 'other@example.com'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 400
        assert 'already in use' in response.json['error']['message']
    
    def test_change_password(self, client, sample_user, db):
        """Un utilisateur peut changer son mot de passe."""
        token = create_access_token(sample_user.id, sample_user.role)
        
        response = client.put(
            '/api/v1/auth/password',
            json={
                'current_password': 'SecurePassword123!',
                'new_password': 'NewPassword456!'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        
        # Verifier que le nouveau mot de passe fonctionne
        db.session.refresh(sample_user)
        assert sample_user.check_password('NewPassword456!') is True
    
    def test_change_password_wrong_current(self, client, sample_user, db):
        """Erreur si le mot de passe actuel est incorrect."""
        token = create_access_token(sample_user.id, sample_user.role)
        
        response = client.put(
            '/api/v1/auth/password',
            json={
                'current_password': 'WrongPassword!',
                'new_password': 'NewPassword456!'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 401

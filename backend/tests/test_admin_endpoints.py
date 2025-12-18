"""
Tests complets pour les endpoints Admin.
CRITIQUE: Ces tests couvrent la gestion des rôles et permissions.
Target: 95%+ coverage sur admin.py
"""

import pytest
from datetime import datetime, timezone, timedelta

from app.models.user import User, UserRole
from app.models.prediction import Prediction
from app.models.consultation import Consultation
from app.core.security import create_access_token


class TestAdminListUsers:
    """Tests pour GET /api/v1/admin/users."""
    
    def test_list_users_requires_auth(self, client):
        """Liste users sans token → 401."""
        response = client.get('/api/v1/admin/users')
        assert response.status_code == 401
    
    def test_list_users_requires_admin(self, client, app, db):
        """Liste users avec user normal → 403."""
        user = User(email='normal@test.com', username='normaluser', role=UserRole.USER)
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(user.id, user.role)
        
        response = client.get(
            '/api/v1/admin/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 403
    
    def test_list_users_success_admin(self, client, app, db):
        """Liste users avec admin → 200 + users."""
        admin = User(email='admin@test.com', username='adminuser', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        # Créer quelques users
        for i in range(5):
            u = User(email=f'user{i}@test.com', username=f'user{i}', role=UserRole.USER)
            u.set_password('Password123!')
            db.session.add(u)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert 'pagination' in data
        assert len(data['users']) >= 5
    
    def test_list_users_pagination(self, client, app, db):
        """Pagination fonctionne correctement."""
        admin = User(email='admin2@test.com', username='admin2', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        for i in range(25):
            u = User(email=f'bulk{i}@test.com', username=f'bulkuser{i}', role=UserRole.USER)
            u.set_password('Password123!')
            db.session.add(u)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users?page=1&per_page=10',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['users']) <= 10
        assert data['pagination']['per_page'] == 10
        assert data['pagination']['has_next'] is True
    
    def test_list_users_filter_by_role(self, client, app, db):
        """Filtrage par rôle fonctionne."""
        admin = User(email='admin3@test.com', username='admin3', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        user = User(email='filtered@test.com', username='filtered', role=UserRole.USER)
        user.set_password('Password123!')
        db.session.add(user)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        # Filtrer uniquement les admins
        response = client.get(
            '/api/v1/admin/users?role=admin',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        for u in data['users']:
            assert u['role'] == 'admin'
    
    def test_list_users_filter_by_status(self, client, app, db):
        """Filtrage par statut actif/inactif."""
        admin = User(email='admin4@test.com', username='admin4', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        inactive = User(email='inactive@test.com', username='inactive', role=UserRole.USER, is_active=False)
        inactive.set_password('Password123!')
        db.session.add(inactive)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        # Filtrer inactifs
        response = client.get(
            '/api/v1/admin/users?status=inactive',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        for u in data['users']:
            assert u['is_active'] is False
    
    def test_list_users_search(self, client, app, db):
        """Recherche par email ou username."""
        admin = User(email='admin5@test.com', username='admin5', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='searchme@unique.com', username='searchable', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users?search=searchme',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['users']) >= 1
        assert any('searchme' in u['email'] for u in data['users'])


class TestAdminGetUser:
    """Tests pour GET /api/v1/admin/users/<id>."""
    
    def test_get_user_success(self, client, app, db):
        """Récupération user par ID OK."""
        admin = User(email='admin6@test.com', username='admin6', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='target@test.com', username='targetuser', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            f'/api/v1/admin/users/{target_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['id'] == target_id
        assert data['user']['username'] == 'targetuser'
    
    def test_get_user_not_found(self, client, app, db):
        """User inexistant → 404."""
        admin = User(email='admin7@test.com', username='admin7', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users/99999',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404


class TestAdminUpdateUser:
    """Tests pour PUT /api/v1/admin/users/<id>."""
    
    def test_update_user_role(self, client, app, db):
        """Update role d'un user."""
        admin = User(email='admin8@test.com', username='admin8', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='toupdate@test.com', username='toupdate', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.put(
            f'/api/v1/admin/users/{target_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'role': 'admin'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'admin'
    
    def test_update_user_deactivate(self, client, app, db):
        """Désactiver un user."""
        admin = User(email='admin9@test.com', username='admin9', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='todeactivate@test.com', username='todeactivate', role=UserRole.USER, is_active=True)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.put(
            f'/api/v1/admin/users/{target_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'is_active': False}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['is_active'] is False
    
    def test_cannot_demote_self(self, client, app, db):
        """Admin ne peut pas se rétrograder lui-même."""
        admin = User(email='admin10@test.com', username='admin10', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.put(
            f'/api/v1/admin/users/{admin_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'role': 'user'}
        )
        
        assert response.status_code == 400
        assert 'propres droits' in response.get_json()['error']
    
    def test_cannot_deactivate_self(self, client, app, db):
        """Admin ne peut pas se désactiver lui-même."""
        admin = User(email='admin11@test.com', username='admin11', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.put(
            f'/api/v1/admin/users/{admin_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'is_active': False}
        )
        
        assert response.status_code == 400
        assert 'propre compte' in response.get_json()['error']
    
    def test_update_user_not_found(self, client, app, db):
        """Update user inexistant → 404."""
        admin = User(email='admin12@test.com', username='admin12', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.put(
            '/api/v1/admin/users/99999',
            headers={'Authorization': f'Bearer {token}'},
            json={'role': 'admin'}
        )
        
        assert response.status_code == 404


class TestAdminDeleteUser:
    """Tests pour DELETE /api/v1/admin/users/<id>."""
    
    def test_delete_user_soft(self, client, app, db):
        """Soft delete (désactivation) par défaut."""
        admin = User(email='admin13@test.com', username='admin13', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='todelete@test.com', username='todelete', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.delete(
            f'/api/v1/admin/users/{target_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert 'désactivé' in response.get_json()['message']
    
    def test_delete_user_hard(self, client, app, db):
        """Hard delete avec ?hard=true."""
        admin = User(email='admin14@test.com', username='admin14', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='tohard@test.com', username='tohard', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.delete(
            f'/api/v1/admin/users/{target_id}?hard=true',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert 'définitivement' in response.get_json()['message']
    
    def test_cannot_delete_self(self, client, app, db):
        """Admin ne peut pas se supprimer lui-même."""
        admin = User(email='admin15@test.com', username='admin15', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.delete(
            f'/api/v1/admin/users/{admin_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 400
        assert 'propre compte' in response.get_json()['error']
    
    def test_delete_user_not_found(self, client, app, db):
        """Delete user inexistant → 404."""
        admin = User(email='admin16@test.com', username='admin16', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.delete(
            '/api/v1/admin/users/99999',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404


class TestAdminStats:
    """Tests pour GET /api/v1/admin/stats."""
    
    def test_get_stats_success(self, client, app, db):
        """Stats système OK."""
        admin = User(email='admin17@test.com', username='admin17', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        # Créer des users
        for i in range(3):
            u = User(email=f'statuser{i}@test.com', username=f'statuser{i}', role=UserRole.USER)
            u.set_password('Password123!')
            db.session.add(u)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/stats',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert 'predictions' in data
        assert 'consultations' in data
        assert data['users']['total'] >= 4  # admin + 3 users
    
    def test_stats_counts_predictions(self, client, app, db):
        """Stats comptent les prédictions."""
        admin = User(email='admin18@test.com', username='admin18', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        # Créer des prédictions
        for i in range(5):
            pred = Prediction(
                user_id=admin.id,
                prediction_type='sports' if i % 2 == 0 else 'finance',
                input_data={'test': i},
                prediction_value='HOME_WIN',
                confidence=0.75
            )
            db.session.add(pred)
        
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/stats',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['predictions']['total'] >= 5


class TestAdminActivityLogs:
    """Tests pour GET /api/v1/admin/activity."""
    
    def test_get_activity_success(self, client, app, db):
        """Logs d'activité OK."""
        admin = User(email='admin19@test.com', username='admin19', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        # Créer des prédictions
        pred = Prediction(
            user_id=admin.id,
            prediction_type='sports',
            external_match_id='123',
            input_data={'match_id': '123'},
            prediction_value='HOME_WIN',
            confidence=0.8
        )
        db.session.add(pred)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/activity',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'activities' in data
        assert 'count' in data
    
    def test_activity_filter_by_type(self, client, app, db):
        """Filtre par type d'activité."""
        admin = User(email='admin20@test.com', username='admin20', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/activity?type=prediction&limit=10',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        for act in data['activities']:
            assert act['type'] == 'prediction'


class TestAdminPromoteDemote:
    """Tests pour les actions promote/demote."""
    
    def test_promote_user_success(self, client, app, db):
        """Promouvoir un user en admin."""
        admin = User(email='admin21@test.com', username='admin21', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='topromote@test.com', username='topromote', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            f'/api/v1/admin/users/{target_id}/promote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert 'administrateur' in response.get_json()['message']
    
    def test_promote_already_admin(self, client, app, db):
        """Promouvoir un user déjà admin → 200 message."""
        admin = User(email='admin22@test.com', username='admin22', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='alreadyadmin@test.com', username='alreadyadmin', role=UserRole.ADMIN)
        target.set_password('AdminPass123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            f'/api/v1/admin/users/{target_id}/promote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert 'déjà administrateur' in response.get_json()['message']
    
    def test_promote_not_found(self, client, app, db):
        """Promouvoir user inexistant → 404."""
        admin = User(email='admin23@test.com', username='admin23', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            '/api/v1/admin/users/99999/promote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404
    
    def test_demote_user_success(self, client, app, db):
        """Rétrograder un admin en user."""
        admin = User(email='admin24@test.com', username='admin24', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='todemote@test.com', username='todemote', role=UserRole.ADMIN)
        target.set_password('AdminPass123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            f'/api/v1/admin/users/{target_id}/demote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert 'standard' in response.get_json()['message']
    
    def test_demote_already_user(self, client, app, db):
        """Rétrograder un user déjà standard → 200 message."""
        admin = User(email='admin25@test.com', username='admin25', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='alreadyuser@test.com', username='alreadyuser', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            f'/api/v1/admin/users/{target_id}/demote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        assert 'déjà standard' in response.get_json()['message']
    
    def test_cannot_demote_self(self, client, app, db):
        """Admin ne peut pas se rétrograder lui-même."""
        admin = User(email='admin26@test.com', username='admin26', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            f'/api/v1/admin/users/{admin_id}/demote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 400
        assert 'propres droits' in response.get_json()['error']
    
    def test_demote_not_found(self, client, app, db):
        """Rétrograder user inexistant → 404."""
        admin = User(email='admin27@test.com', username='admin27', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.post(
            '/api/v1/admin/users/99999/demote',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404


class TestAdminEdgeCases:
    """Tests pour les cas limites admin."""
    
    def test_per_page_max_100(self, client, app, db):
        """per_page limité à 100."""
        admin = User(email='admin28@test.com', username='admin28', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users?per_page=500',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['pagination']['per_page'] <= 100
    
    def test_invalid_role_filter_ignored(self, client, app, db):
        """Filtre role invalide ignoré."""
        admin = User(email='admin29@test.com', username='admin29', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.get(
            '/api/v1/admin/users?role=superadmin',  # rôle invalide
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200  # Ne doit pas planter
    
    def test_update_user_names(self, client, app, db):
        """Update first_name et last_name."""
        admin = User(email='admin30@test.com', username='admin30', role=UserRole.ADMIN)
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        
        target = User(email='names@test.com', username='names', role=UserRole.USER)
        target.set_password('Password123!')
        db.session.add(target)
        
        db.session.commit()
        target_id = target.id
        
        with app.app_context():
            token = create_access_token(admin.id, admin.role)
        
        response = client.put(
            f'/api/v1/admin/users/{target_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'first_name': 'John', 'last_name': 'Doe'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['first_name'] == 'John'
        assert data['user']['last_name'] == 'Doe'

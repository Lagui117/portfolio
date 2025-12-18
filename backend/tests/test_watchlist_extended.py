"""
Tests supplémentaires pour les endpoints Watchlist API.
"""
import pytest
import json


class TestWatchlistFiltering:
    """Tests pour le filtrage de la watchlist."""
    
    def test_filter_by_type_team(self, client, auth_headers):
        """Filtrer par type team."""
        # D'abord ajouter un item
        client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'team',
                'item_id': 'psg_001',
                'item_name': 'Paris Saint-Germain'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        response = client.get(
            '/api/v1/watchlist?type=team',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        for item in data['items']:
            assert item['item_type'] == 'team'
    
    def test_filter_by_type_ticker(self, client, auth_headers):
        """Filtrer par type ticker."""
        # Ajouter un ticker
        client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'AAPL',
                'item_name': 'Apple Inc.'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        response = client.get(
            '/api/v1/watchlist?type=ticker',
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_filter_alerts_only(self, client, auth_headers):
        """Filtrer par alertes actives uniquement."""
        response = client.get(
            '/api/v1/watchlist?alerts_only=true',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestWatchlistCRUDComplete:
    """Tests CRUD complets pour la watchlist."""
    
    def test_create_with_alerts(self, client, auth_headers):
        """Créer un item avec alertes."""
        response = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'GOOGL_test',
                'item_name': 'Alphabet Inc.',
                'alerts_enabled': True,
                'alert_config': {'threshold': 150.0}
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['item']['alerts_enabled'] == True
    
    def test_create_with_notes(self, client, auth_headers):
        """Créer un item avec notes."""
        response = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'team',
                'item_id': 'om_test',
                'item_name': 'Olympique de Marseille',
                'notes': 'Équipe à surveiller cette saison'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['item']['notes'] == 'Équipe à surveiller cette saison'
    
    def test_create_with_item_data(self, client, auth_headers):
        """Créer un item avec données supplémentaires."""
        response = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'MSFT_test',
                'item_name': 'Microsoft Corp.',
                'item_data': {
                    'sector': 'Technology',
                    'price': 378.50
                }
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_update_notes(self, client, auth_headers):
        """Mettre à jour les notes."""
        # Créer un item
        create_resp = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'team',
                'item_id': 'lyon_test',
                'item_name': 'Olympique Lyonnais'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        if create_resp.status_code == 201:
            item_id = create_resp.get_json()['item']['id']
            
            # Mettre à jour
            response = client.put(
                f'/api/v1/watchlist/{item_id}',
                data=json.dumps({'notes': 'Mise à jour notes'}),
                content_type='application/json',
                headers=auth_headers
            )
            
            assert response.status_code == 200
    
    def test_update_alerts_enabled(self, client, auth_headers):
        """Activer les alertes sur un item existant."""
        # Créer sans alertes
        create_resp = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'TSLA_test',
                'item_name': 'Tesla Inc.'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        if create_resp.status_code == 201:
            item_id = create_resp.get_json()['item']['id']
            
            # Activer les alertes
            response = client.put(
                f'/api/v1/watchlist/{item_id}',
                data=json.dumps({
                    'alerts_enabled': True,
                    'alert_config': {'threshold': 250.0}
                }),
                content_type='application/json',
                headers=auth_headers
            )
            
            assert response.status_code == 200
    
    def test_delete_existing_item(self, client, auth_headers):
        """Supprimer un item existant."""
        # Créer un item
        create_resp = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'team',
                'item_id': 'to_delete',
                'item_name': 'Équipe à supprimer'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        if create_resp.status_code == 201:
            item_id = create_resp.get_json()['item']['id']
            
            response = client.delete(
                f'/api/v1/watchlist/{item_id}',
                headers=auth_headers
            )
            
            assert response.status_code == 200


class TestWatchlistCheckItem:
    """Tests pour vérifier si un item est dans la watchlist."""
    
    def test_check_existing_item(self, client, auth_headers):
        """Vérifier un item existant."""
        # Créer un item
        client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'check_test',
                'item_name': 'Test Check Item'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        response = client.get(
            '/api/v1/watchlist/check?type=ticker&id=check_test',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['in_watchlist'] == True
    
    def test_check_nonexistent_item(self, client, auth_headers):
        """Vérifier un item non existant."""
        response = client.get(
            '/api/v1/watchlist/check?type=ticker&id=nonexistent_xyz',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['in_watchlist'] == False


class TestWatchlistBulkOperations:
    """Tests pour les opérations bulk."""
    
    def test_bulk_add_multiple(self, client, auth_headers):
        """Ajouter plusieurs items en bulk."""
        response = client.post(
            '/api/v1/watchlist/bulk',
            data=json.dumps({
                'items': [
                    {'item_type': 'ticker', 'item_id': 'bulk_1', 'item_name': 'Bulk Item 1'},
                    {'item_type': 'ticker', 'item_id': 'bulk_2', 'item_name': 'Bulk Item 2'},
                    {'item_type': 'team', 'item_id': 'bulk_3', 'item_name': 'Bulk Team 3'}
                ]
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'added' in data
        assert 'skipped' in data
    
    def test_bulk_skip_duplicates(self, client, auth_headers):
        """Bulk ignore les doublons."""
        # Premier ajout
        client.post(
            '/api/v1/watchlist/bulk',
            data=json.dumps({
                'items': [
                    {'item_type': 'ticker', 'item_id': 'dup_bulk', 'item_name': 'Duplicate'}
                ]
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Deuxième ajout (doublon)
        response = client.post(
            '/api/v1/watchlist/bulk',
            data=json.dumps({
                'items': [
                    {'item_type': 'ticker', 'item_id': 'dup_bulk', 'item_name': 'Duplicate'}
                ]
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Devrait être dans skipped
        assert len(data['skipped']) >= 1
    
    def test_bulk_invalid_type(self, client, auth_headers):
        """Bulk ignore les types invalides."""
        response = client.post(
            '/api/v1/watchlist/bulk',
            data=json.dumps({
                'items': [
                    {'item_type': 'invalid_type', 'item_id': 'bad', 'item_name': 'Bad Type'}
                ]
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Ne devrait pas être ajouté
        assert len(data['added']) == 0


class TestWatchlistValidation:
    """Tests de validation des données."""
    
    def test_invalid_item_type(self, client, auth_headers):
        """Type d'item invalide."""
        response = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'invalid',
                'item_id': 'test',
                'item_name': 'Test'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_duplicate_item(self, client, auth_headers):
        """Doublon retourne 409."""
        # Premier ajout
        client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'dup_test_single',
                'item_name': 'Duplicate Test'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Deuxième ajout (doublon)
        response = client.post(
            '/api/v1/watchlist',
            data=json.dumps({
                'item_type': 'ticker',
                'item_id': 'dup_test_single',
                'item_name': 'Duplicate Test'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 409


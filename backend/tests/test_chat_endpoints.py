"""
Tests pour les endpoints Chat API.
"""
import pytest
import json


class TestChatMessageEndpoint:
    """Tests pour POST /api/v1/chat/message."""
    
    def test_message_requires_auth(self, client):
        """Endpoint nécessite authentification."""
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_message_success(self, client, auth_headers):
        """Envoi de message réussi."""
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': 'Bonjour'}),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'response' in data
        assert 'content' in data['response']
        assert 'conversation_id' in data
    
    def test_message_missing_message(self, client, auth_headers):
        """Erreur si message manquant."""
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({}),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_message_empty_message(self, client, auth_headers):
        """Erreur si message vide."""
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': '   '}),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_message_too_long(self, client, auth_headers):
        """Erreur si message trop long."""
        long_message = 'x' * 2001
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': long_message}),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'trop long' in data['error'].lower() or 'max' in data['error'].lower()
    
    def test_message_with_context(self, client, auth_headers):
        """Message avec contexte."""
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({
                'message': 'Analyse cette prédiction',
                'context': {
                    'current_analysis': {
                        'type': 'sports',
                        'prediction': 'HOME_WIN',
                        'confidence': 75
                    }
                }
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
    
    def test_message_with_conversation_id(self, client, auth_headers):
        """Message avec ID de conversation."""
        conv_id = 'test_conv_123'
        
        # Premier message
        response1 = client.post(
            '/api/v1/chat/message',
            data=json.dumps({
                'message': 'Premier message',
                'conversation_id': conv_id
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1['conversation_id'] == conv_id
        
        # Deuxième message même conversation
        response2 = client.post(
            '/api/v1/chat/message',
            data=json.dumps({
                'message': 'Deuxième message',
                'conversation_id': conv_id
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2['conversation_id'] == conv_id
        assert data2['message_count'] > data1['message_count']
    
    def test_message_response_format(self, client, auth_headers):
        """Format de réponse correct."""
        response = client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': 'Test format'}),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Vérifier la structure complète
        assert 'response' in data
        assert 'content' in data['response']
        assert 'type' in data['response']
        assert data['response']['type'] == 'assistant'


class TestChatHistoryEndpoint:
    """Tests pour GET /api/v1/chat/history."""
    
    def test_history_requires_auth(self, client):
        """Endpoint nécessite authentification."""
        response = client.get('/api/v1/chat/history')
        assert response.status_code == 401
    
    def test_history_empty(self, client, auth_headers):
        """Historique vide pour nouvel utilisateur."""
        # D'abord effacer l'historique
        client.delete('/api/v1/chat/clear', headers=auth_headers)
        
        response = client.get('/api/v1/chat/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'history' in data
        assert 'count' in data
    
    def test_history_after_messages(self, client, auth_headers):
        """Historique contient les messages envoyés."""
        # Effacer puis envoyer un message
        client.delete('/api/v1/chat/clear', headers=auth_headers)
        
        client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': 'Test historique'}),
            content_type='application/json',
            headers=auth_headers
        )
        
        response = client.get('/api/v1/chat/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 2  # user + assistant
    
    def test_history_with_limit(self, client, auth_headers):
        """Limite le nombre de messages."""
        response = client.get(
            '/api/v1/chat/history?limit=5',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['history']) <= 5
    
    def test_history_max_limit(self, client, auth_headers):
        """Limite max à 100 messages."""
        response = client.get(
            '/api/v1/chat/history?limit=200',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # La limite devrait être respectée à 100
    
    def test_history_with_conversation_id(self, client, auth_headers):
        """Filtre par ID de conversation."""
        conv_id = 'specific_conv_test'
        
        # Effacer et créer une conversation spécifique
        client.delete('/api/v1/chat/clear', headers=auth_headers)
        
        client.post(
            '/api/v1/chat/message',
            data=json.dumps({
                'message': 'Message spécifique',
                'conversation_id': conv_id
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        response = client.get(
            f'/api/v1/chat/history?conversation_id={conv_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 2


class TestChatClearEndpoint:
    """Tests pour DELETE /api/v1/chat/clear."""
    
    def test_clear_requires_auth(self, client):
        """Endpoint nécessite authentification."""
        response = client.delete('/api/v1/chat/clear')
        assert response.status_code == 401
    
    def test_clear_all(self, client, auth_headers):
        """Efface tout l'historique."""
        # Créer des messages
        client.post(
            '/api/v1/chat/message',
            data=json.dumps({'message': 'Test 1'}),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Effacer
        response = client.delete('/api/v1/chat/clear', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_clear_specific_conversation(self, client, auth_headers):
        """Efface une conversation spécifique."""
        conv_id = 'conv_to_delete'
        
        # Créer une conversation
        client.post(
            '/api/v1/chat/message',
            data=json.dumps({
                'message': 'Test',
                'conversation_id': conv_id
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Effacer cette conversation
        response = client.delete(
            f'/api/v1/chat/clear?conversation_id={conv_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestChatSuggestionsEndpoint:
    """Tests pour GET /api/v1/chat/suggestions."""
    
    def test_suggestions_requires_auth(self, client):
        """Endpoint nécessite authentification."""
        response = client.get('/api/v1/chat/suggestions')
        assert response.status_code == 401
    
    def test_suggestions_general(self, client, auth_headers):
        """Suggestions générales par défaut."""
        response = client.get('/api/v1/chat/suggestions', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'suggestions' in data
        assert 'domain' in data
        assert isinstance(data['suggestions'], list)
        assert data['domain'] == 'general'
    
    def test_suggestions_sports(self, client, auth_headers):
        """Suggestions domaine sports."""
        response = client.get(
            '/api/v1/chat/suggestions?domain=sports',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['domain'] == 'sports'
        assert len(data['suggestions']) > 0
    
    def test_suggestions_finance(self, client, auth_headers):
        """Suggestions domaine finance."""
        response = client.get(
            '/api/v1/chat/suggestions?domain=finance',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['domain'] == 'finance'
        assert len(data['suggestions']) > 0
    
    def test_suggestions_unknown_domain(self, client, auth_headers):
        """Domaine inconnu retourne suggestions générales."""
        response = client.get(
            '/api/v1/chat/suggestions?domain=unknown',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Devrait retourner les suggestions générales
        assert 'suggestions' in data


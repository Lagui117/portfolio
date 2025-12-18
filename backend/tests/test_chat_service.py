"""
Tests pour ChatService - Service de chat conversationnel IA.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.chat_service import ChatService


class TestChatServiceInit:
    """Tests pour l'initialisation du service."""
    
    def test_init_without_api_key(self):
        """Service en mode fallback sans clé API."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': ''}):
            service = ChatService()
            assert service.client is None
    
    def test_init_fallback_mode(self):
        """Service fonctionne même sans OpenAI."""
        service = ChatService()
        # Doit être initialisé même en mode fallback
        assert hasattr(service, '_conversations')
        assert hasattr(service, 'model')


class TestChatServicePrompts:
    """Tests pour la gestion des prompts."""
    
    def test_get_system_prompt(self):
        """Le prompt système est bien défini."""
        service = ChatService()
        prompt = service._get_system_prompt()
        
        assert 'PredictWise' in prompt
        assert 'Copilote' in prompt
        assert len(prompt) > 100
    
    def test_format_context_empty(self):
        """Contexte vide retourne chaîne vide."""
        service = ChatService()
        result = service._format_context({})
        assert result == ''
    
    def test_format_context_with_analysis(self):
        """Contexte avec analyse est formaté correctement."""
        service = ChatService()
        context = {
            'current_analysis': {
                'type': 'sports',
                'symbol': 'PSG vs OL',
                'prediction': 'HOME_WIN',
                'confidence': 75
            },
            'page': 'dashboard'
        }
        
        result = service._format_context(context)
        assert 'sports' in result
        assert 'PSG vs OL' in result
        assert '75' in result
        assert 'dashboard' in result
    
    def test_format_context_with_teams(self):
        """Contexte avec équipes."""
        service = ChatService()
        context = {
            'current_analysis': {
                'teams': 'PSG vs Marseille'
            }
        }
        
        result = service._format_context(context)
        assert 'PSG vs Marseille' in result
    
    def test_format_context_with_recent_queries(self):
        """Contexte avec requêtes récentes."""
        service = ChatService()
        context = {
            'recent_queries': ['query1', 'query2', 'query3']
        }
        
        result = service._format_context(context)
        assert 'query1' in result


class TestChatServiceFallback:
    """Tests pour les réponses fallback."""
    
    def test_fallback_greeting(self):
        """Réponse de bienvenue."""
        service = ChatService()
        response = service._get_fallback_response("Bonjour!")
        
        assert 'Copilote' in response
        assert 'PredictWise' in response
    
    def test_fallback_hello_english(self):
        """Réponse hello en anglais."""
        service = ChatService()
        response = service._get_fallback_response("Hello!")
        
        assert 'Copilote' in response
    
    def test_fallback_help(self):
        """Réponse d'aide."""
        service = ChatService()
        response = service._get_fallback_response("Comment ça marche ?")
        
        assert 'Sports' in response or 'Finance' in response
    
    def test_fallback_rsi_indicator(self):
        """Réponse sur indicateurs techniques."""
        service = ChatService()
        response = service._get_fallback_response("C'est quoi le RSI ?")
        
        assert 'RSI' in response
        assert '30' in response or '70' in response
    
    def test_fallback_sports(self):
        """Réponse sur analyse sportive."""
        service = ChatService()
        response = service._get_fallback_response("Analyse ce match de foot")
        
        assert 'match' in response.lower() or 'sport' in response.lower()
    
    def test_fallback_generic(self):
        """Réponse générique pour questions non reconnues."""
        service = ChatService()
        response = service._get_fallback_response("xyz123abc")
        
        assert 'analyse' in response.lower() or 'dashboard' in response.lower()


class TestChatServiceProcessMessage:
    """Tests pour le traitement des messages."""
    
    def test_process_message_creates_conversation(self):
        """Un nouveau message crée une conversation."""
        service = ChatService()
        service._conversations.clear()
        
        result = service.process_message(
            user_id='test_user',
            message='Bonjour'
        )
        
        assert 'response' in result
        assert 'conversation_id' in result
        assert 'message_count' in result
        assert result['message_count'] == 2  # user + assistant
    
    def test_process_message_with_conversation_id(self):
        """Conversation existante est continuée."""
        service = ChatService()
        service._conversations.clear()
        
        # Premier message
        result1 = service.process_message(
            user_id='test_user',
            message='Premier message',
            conversation_id='conv123'
        )
        
        # Deuxième message même conversation
        result2 = service.process_message(
            user_id='test_user',
            message='Deuxième message',
            conversation_id='conv123'
        )
        
        assert result2['conversation_id'] == 'conv123'
        assert result2['message_count'] == 4  # 2 paires user+assistant
    
    def test_process_message_with_context(self):
        """Message avec contexte est traité."""
        service = ChatService()
        
        context = {
            'current_analysis': {
                'type': 'finance',
                'symbol': 'AAPL'
            }
        }
        
        result = service.process_message(
            user_id='test_user',
            message='Analyse ce titre',
            context=context
        )
        
        assert result['response']['content'] is not None
    
    def test_process_message_response_format(self):
        """Format de réponse est correct."""
        service = ChatService()
        
        result = service.process_message(
            user_id='test_user',
            message='Test'
        )
        
        assert 'content' in result['response']
        assert 'type' in result['response']
        assert 'timestamp' in result['response']
        assert result['response']['type'] == 'assistant'
    
    def test_process_message_history_limit(self):
        """L'historique est limité à 50 messages."""
        service = ChatService()
        service._conversations.clear()
        
        # Envoyer 30 messages (60 avec réponses)
        for i in range(30):
            service.process_message(
                user_id='test_user',
                message=f'Message {i}',
                conversation_id='conv_limit'
            )
        
        conv_key = 'test_user:conv_limit'
        assert len(service._conversations[conv_key]) <= 50


class TestChatServiceHistory:
    """Tests pour la gestion de l'historique."""
    
    def test_get_conversation_history_empty(self):
        """Historique vide pour nouvel utilisateur."""
        service = ChatService()
        service._conversations.clear()
        
        history = service.get_conversation_history('new_user')
        assert history == []
    
    def test_get_conversation_history_with_id(self):
        """Récupère historique d'une conversation spécifique."""
        service = ChatService()
        service._conversations.clear()
        
        # Créer une conversation
        service.process_message(
            user_id='test_user',
            message='Test',
            conversation_id='specific_conv'
        )
        
        history = service.get_conversation_history(
            user_id='test_user',
            conversation_id='specific_conv'
        )
        
        assert len(history) == 2
    
    def test_get_conversation_history_limit(self):
        """Limite le nombre de messages retournés."""
        service = ChatService()
        service._conversations.clear()
        
        # Créer plusieurs messages
        for i in range(10):
            service.process_message(
                user_id='test_user',
                message=f'Message {i}',
                conversation_id='conv_history'
            )
        
        history = service.get_conversation_history(
            user_id='test_user',
            conversation_id='conv_history',
            limit=5
        )
        
        assert len(history) == 5
    
    def test_get_all_conversations_for_user(self):
        """Récupère toutes les conversations d'un utilisateur."""
        service = ChatService()
        service._conversations.clear()
        
        # Créer plusieurs conversations
        service.process_message('user1', 'Msg1', conversation_id='conv1')
        service.process_message('user1', 'Msg2', conversation_id='conv2')
        service.process_message('user2', 'Msg3', conversation_id='conv3')
        
        history = service.get_conversation_history('user1')
        
        # User1 a 4 messages (2 conv * 2 msg)
        assert len(history) == 4


class TestChatServiceClear:
    """Tests pour l'effacement de l'historique."""
    
    def test_clear_specific_conversation(self):
        """Efface une conversation spécifique."""
        service = ChatService()
        service._conversations.clear()
        
        # Créer deux conversations
        service.process_message('user1', 'Msg1', conversation_id='conv1')
        service.process_message('user1', 'Msg2', conversation_id='conv2')
        
        # Effacer une seule
        service.clear_history('user1', 'conv1')
        
        # conv1 effacée, conv2 reste
        assert 'user1:conv1' not in service._conversations
        assert 'user1:conv2' in service._conversations
    
    def test_clear_all_user_conversations(self):
        """Efface toutes les conversations d'un utilisateur."""
        service = ChatService()
        service._conversations.clear()
        
        # Créer des conversations pour deux utilisateurs
        service.process_message('user1', 'Msg1', conversation_id='conv1')
        service.process_message('user1', 'Msg2', conversation_id='conv2')
        service.process_message('user2', 'Msg3', conversation_id='conv3')
        
        # Effacer toutes les conversations de user1
        service.clear_history('user1')
        
        # user1 effacé, user2 reste
        assert 'user1:conv1' not in service._conversations
        assert 'user1:conv2' not in service._conversations
        assert 'user2:conv3' in service._conversations
    
    def test_clear_nonexistent_conversation(self):
        """Effacer une conversation inexistante ne cause pas d'erreur."""
        service = ChatService()
        service._conversations.clear()
        
        # Ne doit pas lever d'exception
        service.clear_history('unknown_user', 'unknown_conv')


class TestChatServiceSuggestions:
    """Tests pour les suggestions de questions."""
    
    def test_suggestions_sports(self):
        """Suggestions pour le domaine sports."""
        service = ChatService()
        suggestions = service.get_suggestions('sports')
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any('match' in s.lower() or 'équipe' in s.lower() for s in suggestions)
    
    def test_suggestions_finance(self):
        """Suggestions pour le domaine finance."""
        service = ChatService()
        suggestions = service.get_suggestions('finance')
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any('indicateur' in s.lower() or 'tendance' in s.lower() for s in suggestions)
    
    def test_suggestions_general(self):
        """Suggestions générales par défaut."""
        service = ChatService()
        suggestions = service.get_suggestions('general')
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_suggestions_unknown_domain(self):
        """Domaine inconnu retourne suggestions générales."""
        service = ChatService()
        suggestions = service.get_suggestions('unknown_domain')
        
        general = service.get_suggestions('general')
        assert suggestions == general


class TestChatServiceBuildMessages:
    """Tests pour la construction des messages API."""
    
    def test_build_messages_basic(self):
        """Construction basique des messages."""
        service = ChatService()
        
        messages = service._build_messages(
            user_message='Test message',
            context={},
            history=[]
        )
        
        # Au moins system + user
        assert len(messages) >= 2
        assert messages[0]['role'] == 'system'
        assert messages[-1]['role'] == 'user'
        assert messages[-1]['content'] == 'Test message'
    
    def test_build_messages_with_history(self):
        """Messages avec historique."""
        service = ChatService()
        
        history = [
            {'role': 'user', 'content': 'Question 1'},
            {'role': 'assistant', 'content': 'Réponse 1'},
        ]
        
        messages = service._build_messages(
            user_message='Question 2',
            context={},
            history=history
        )
        
        # system + history (2) + new user
        assert len(messages) >= 4
    
    def test_build_messages_history_limit(self):
        """L'historique est limité à 10 messages."""
        service = ChatService()
        
        # 20 messages dans l'historique
        history = [
            {'role': 'user' if i % 2 == 0 else 'assistant', 'content': f'Msg {i}'}
            for i in range(20)
        ]
        
        messages = service._build_messages(
            user_message='New message',
            context={},
            history=history
        )
        
        # Devrait avoir au max: system + context? + 10 history + user = ~13
        assert len(messages) <= 14
    
    def test_build_messages_with_context(self):
        """Messages avec contexte ajouté."""
        service = ChatService()
        
        context = {
            'current_analysis': {
                'type': 'finance',
                'symbol': 'AAPL'
            }
        }
        
        messages = service._build_messages(
            user_message='Analyse',
            context=context,
            history=[]
        )
        
        # Il devrait y avoir un message système avec le contexte
        system_messages = [m for m in messages if m['role'] == 'system']
        context_found = any('AAPL' in m['content'] for m in system_messages)
        assert context_found


"""
Service Chat IA - Copilote décisionnel PredictWise.
Gère les conversations avec l'assistant IA.
"""

import os
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

# Essayer d'importer OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("openai package non installé. Chat IA en mode fallback.")
    OPENAI_AVAILABLE = False


class ChatService:
    """Service de chat conversationnel avec IA."""
    
    # Stockage en mémoire des conversations (en production: Redis/DB)
    _conversations: Dict[str, List[Dict]] = defaultdict(list)
    
    def __init__(self):
        """Initialise le service de chat."""
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key or not OPENAI_AVAILABLE:
            logger.warning("Chat Service en mode fallback.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Chat Service initialisé avec succès.")
            except Exception as e:
                logger.error(f"Erreur initialisation OpenAI Chat: {e}")
                self.client = None
    
    def _get_system_prompt(self) -> str:
        """Prompt système définissant le comportement du copilote."""
        return """Tu es le Copilote IA de PredictWise, une plateforme SaaS premium d'intelligence décisionnelle pour les marchés Sports et Finance.

IDENTITÉ:
- Tu es un assistant d'analyse expert et stratégique
- Tu aides les utilisateurs à comprendre leurs données et à prendre des décisions éclairées
- Tu es précis, concis et orienté action

CAPACITÉS:
1. Expliquer les analyses et prédictions générées par la plateforme
2. Comparer des résultats entre différentes analyses
3. Identifier des patterns et tendances dans les données
4. Suggérer des stratégies basées sur les indicateurs
5. Répondre aux questions sur les métriques et KPIs

STYLE DE COMMUNICATION:
- Réponses claires et synthétiques (150-250 mots max)
- Utilise des bullet points pour structurer l'information
- Fournis des insights actionnables
- Sois factuel et évite les généralisations

FORMAT DE RÉPONSE:
- Commence par l'essentiel (réponse directe)
- Développe avec les détails pertinents
- Conclus avec une recommandation ou prochaine étape si applicable

RÈGLES:
- Tu ne fournis PAS de conseils financiers ou de paris
- Tu analyses des données, tu ne prédis pas l'avenir avec certitude
- Tu rappelles que toute décision reste la responsabilité de l'utilisateur
- Tu restes professionnel et neutre"""

    def _build_messages(
        self, 
        user_message: str, 
        context: Dict[str, Any],
        history: List[Dict]
    ) -> List[Dict]:
        """Construit la liste des messages pour l'API."""
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        # Ajouter le contexte si présent
        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.append({
                    "role": "system",
                    "content": f"CONTEXTE ACTUEL DE L'UTILISATEUR:\n{context_str}"
                })
        
        # Ajouter l'historique récent (max 10 messages)
        for msg in history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Ajouter le nouveau message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Formate le contexte pour le prompt."""
        parts = []
        
        if 'current_analysis' in context:
            analysis = context['current_analysis']
            parts.append(f"Analyse en cours: {analysis.get('type', 'N/A')}")
            if 'symbol' in analysis:
                parts.append(f"Actif: {analysis['symbol']}")
            if 'teams' in analysis:
                parts.append(f"Match: {analysis['teams']}")
            if 'prediction' in analysis:
                parts.append(f"Prédiction: {analysis['prediction']}")
            if 'confidence' in analysis:
                parts.append(f"Confiance: {analysis['confidence']}%")
        
        if 'page' in context:
            parts.append(f"Page actuelle: {context['page']}")
        
        if 'recent_queries' in context:
            parts.append(f"Requêtes récentes: {', '.join(context['recent_queries'][:5])}")
        
        return '\n'.join(parts)
    
    def process_message(
        self,
        user_id: str,
        message: str,
        context: Dict[str, Any] = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Traite un message utilisateur et génère une réponse.
        
        Args:
            user_id: ID de l'utilisateur
            message: Message de l'utilisateur
            context: Contexte optionnel (analyse en cours, page, etc.)
            conversation_id: ID de conversation pour continuité
        
        Returns:
            Dictionnaire avec la réponse et métadonnées
        """
        # Générer un ID de conversation si non fourni
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        conv_key = f"{user_id}:{conversation_id}"
        history = self._conversations.get(conv_key, [])
        
        # Stocker le message utilisateur
        user_msg = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Générer la réponse
        if self.client:
            response_content = self._call_gpt(message, context or {}, history)
        else:
            response_content = self._get_fallback_response(message)
        
        # Stocker la réponse assistant
        assistant_msg = {
            'role': 'assistant',
            'content': response_content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Mettre à jour l'historique
        self._conversations[conv_key].append(user_msg)
        self._conversations[conv_key].append(assistant_msg)
        
        # Limiter l'historique à 50 messages
        if len(self._conversations[conv_key]) > 50:
            self._conversations[conv_key] = self._conversations[conv_key][-50:]
        
        return {
            'response': {
                'content': response_content,
                'type': 'assistant',
                'timestamp': assistant_msg['timestamp']
            },
            'conversation_id': conversation_id,
            'message_count': len(self._conversations[conv_key])
        }
    
    def _call_gpt(
        self, 
        user_message: str, 
        context: Dict[str, Any],
        history: List[Dict]
    ) -> str:
        """Appelle l'API OpenAI pour générer une réponse."""
        try:
            messages = self._build_messages(user_message, context, history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur appel GPT Chat: {e}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, message: str) -> str:
        """Génère une réponse de fallback intelligente."""
        message_lower = message.lower()
        
        # Détection d'intention basique
        if any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'hi']):
            return """Bonjour ! Je suis votre Copilote IA PredictWise.

Je peux vous aider à :
• Analyser vos données Sports & Finance
• Expliquer les prédictions et indicateurs
• Comparer différentes analyses
• Identifier des tendances

Que souhaitez-vous explorer aujourd'hui ?"""

        elif any(word in message_lower for word in ['aide', 'help', 'comment']):
            return """Voici comment je peux vous assister :

**Analyses Sports**
• "Explique-moi cette prédiction"
• "Compare les stats des deux équipes"
• "Quels facteurs influencent ce match ?"

**Analyses Finance**
• "Que signifie cet indicateur RSI ?"
• "Analyse la tendance de [symbole]"
• "Compare les performances récentes"

Posez-moi directement votre question !"""

        elif any(word in message_lower for word in ['rsi', 'macd', 'indicateur', 'technique']):
            return """Les indicateurs techniques clés :

• **RSI (0-100)** : <30 = survente, >70 = surachat
• **MACD** : Croisement signal = potentiel changement de tendance
• **Volume** : Confirme ou invalide les mouvements de prix
• **Moyennes mobiles** : Identifient la tendance générale

Pour une analyse détaillée d'un indicateur spécifique, lancez une analyse depuis le dashboard Finance."""

        elif any(word in message_lower for word in ['match', 'équipe', 'sport', 'proba']):
            return """Pour l'analyse sportive, je prends en compte :

• **Historique H2H** : Confrontations directes
• **Forme récente** : 5 derniers matchs
• **Facteur domicile** : Avantage terrain
• **Effectif** : Blessures, suspensions

Lancez une analyse depuis le dashboard Sports pour des insights détaillés sur un match spécifique."""

        else:
            return """Je comprends votre question, mais j'ai besoin du service IA complet pour vous fournir une analyse personnalisée.

En attendant, vous pouvez :
1. Lancer une analyse depuis les dashboards Sports ou Finance
2. Consulter l'historique de vos prédictions
3. Explorer les indicateurs disponibles

Le service IA sera rétabli prochainement."""

    def get_conversation_history(
        self,
        user_id: str,
        limit: int = 50,
        conversation_id: str = None
    ) -> List[Dict]:
        """Récupère l'historique des conversations."""
        if conversation_id:
            conv_key = f"{user_id}:{conversation_id}"
            return self._conversations.get(conv_key, [])[-limit:]
        
        # Récupérer toutes les conversations de l'utilisateur
        all_messages = []
        for key, messages in self._conversations.items():
            if key.startswith(f"{user_id}:"):
                for msg in messages:
                    msg_copy = msg.copy()
                    msg_copy['conversation_id'] = key.split(':')[1]
                    all_messages.append(msg_copy)
        
        # Trier par timestamp et limiter
        all_messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_messages[:limit]
    
    def clear_history(self, user_id: str, conversation_id: str = None):
        """Efface l'historique des conversations."""
        if conversation_id:
            conv_key = f"{user_id}:{conversation_id}"
            if conv_key in self._conversations:
                del self._conversations[conv_key]
        else:
            # Effacer toutes les conversations de l'utilisateur
            keys_to_delete = [
                key for key in self._conversations.keys()
                if key.startswith(f"{user_id}:")
            ]
            for key in keys_to_delete:
                del self._conversations[key]
    
    def get_suggestions(self, domain: str = 'general') -> List[str]:
        """Retourne des suggestions de questions selon le contexte."""
        suggestions = {
            'sports': [
                "Quels facteurs influencent le plus ce match ?",
                "Compare la forme récente des deux équipes",
                "Quelle est la fiabilité de cette prédiction ?",
                "Analyse l'historique des confrontations",
                "Quels sont les risques de cette analyse ?"
            ],
            'finance': [
                "Que signifie cet indicateur technique ?",
                "Quelle est la tendance court terme ?",
                "Compare avec le secteur",
                "Quels sont les signaux d'alerte ?",
                "Analyse le volume récent"
            ],
            'general': [
                "Comment fonctionne l'analyse IA ?",
                "Montre-moi mes dernières analyses",
                "Quels indicateurs sont disponibles ?",
                "Comment interpréter les scores de confiance ?",
                "Quelle est la précision des prédictions ?"
            ]
        }
        
        return suggestions.get(domain, suggestions['general'])


# Instance globale du service
chat_service = ChatService()

"""
Service GPT pour l'analyse IA.
Utilise OpenAI pour generer des analyses professionnelles.

IMPORTANT: Ce service fournit des analyses a titre informatif.
Les analyses ne constituent pas des conseils financiers ou de pari.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Essayer d'importer OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("openai package non installe. Service GPT en mode fallback.")
    OPENAI_AVAILABLE = False


class GPTService:
    """Service pour l'analyse IA avec OpenAI GPT."""
    
    def __init__(self):
        """Initialise le service GPT."""
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key or not OPENAI_AVAILABLE:
            logger.warning("GPT Service en mode fallback (pas de cle API ou package manquant).")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("GPT Service initialise avec succes.")
            except Exception as e:
                logger.error(f"Erreur initialisation OpenAI: {e}")
                self.client = None
    
    def _get_system_prompt(self) -> str:
        """Prompt systeme definissant le comportement de l'assistant."""
        return """Tu es un assistant d'analyse pour PredictWise, une plateforme SaaS premium 
d'intelligence decisionnelle pour les marches Sports et Finance.

REGLES IMPORTANTES:
1. Tu fournis des analyses factuelles et objectives.
2. Tu rappelles que les analyses sont a titre informatif uniquement.
3. Tu dois repondre UNIQUEMENT en JSON valide, selon le format demande.
4. Sois factuel, precis et mets en avant le niveau de confiance.

Ta mission est d'analyser des donnees et d'identifier les facteurs cles qui peuvent influencer 
un resultat sportif ou une tendance boursiere."""

    def _create_sports_prompt(self, match_data: Dict[str, Any], model_score: Optional[float]) -> str:
        """Cree le prompt pour l'analyse sportive."""
        prompt = f"""Analyse ce match sportif:

DONNEES DU MATCH:
{json.dumps(match_data, indent=2, ensure_ascii=False, default=str)}

"""
        if model_score is not None:
            prompt += f"SCORE DU MODELE ML INTERNE: {model_score:.2%}\n\n"
        
        prompt += """Reponds UNIQUEMENT avec un JSON valide selon ce format exact:
{
  "domain": "sports",
  "summary": "resume en 1-2 phrases",
  "analysis": "analyse detaillee des facteurs (200-300 mots max)",
  "prediction_type": "probability",
  "prediction_value": nombre entre 0 et 1,
  "confidence": nombre entre 0 et 1,
  "caveats": "limitations importantes de cette analyse",
  "disclaimer": "Analyse a titre informatif uniquement"
}"""
        return prompt

    def _create_finance_prompt(self, stock_data: Dict[str, Any], model_score: Optional[float]) -> str:
        """Cree le prompt pour l'analyse financiere."""
        # Simplifier les donnees pour le prompt
        simplified_data = {
            'symbol': stock_data.get('symbol'),
            'name': stock_data.get('name'),
            'sector': stock_data.get('sector'),
            'current_price': stock_data.get('current_price'),
            'indicators': stock_data.get('indicators', {}),
        }
        
        prompt = f"""Analyse ces donnees boursieres:

DONNEES FINANCIERES:
{json.dumps(simplified_data, indent=2, ensure_ascii=False, default=str)}

"""
        if model_score is not None:
            prompt += f"PREDICTION DU MODELE ML INTERNE: {model_score}\n\n"
        
        prompt += """Reponds UNIQUEMENT avec un JSON valide selon ce format exact:
{
  "domain": "finance",
  "summary": "resume en 1-2 phrases",
  "analysis": "analyse detaillee des indicateurs (200-300 mots max)",
  "prediction_type": "trend",
  "prediction_value": "UP", "DOWN" ou "NEUTRAL",
  "confidence": nombre entre 0 et 1,
  "caveats": "limitations importantes de cette analyse",
  "disclaimer": "Analyse a titre informatif. Ne constitue pas un conseil d'investissement."
}"""
        return prompt

    def _call_gpt(self, user_prompt: str, domain: str = "sports") -> Dict[str, Any]:
        """Appelle l'API OpenAI et parse la reponse JSON."""
        if not self.client:
            return self._get_fallback_response(domain)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validation des champs obligatoires
            required_fields = [
                'domain', 'summary', 'analysis', 'prediction_type',
                'prediction_value', 'confidence', 'caveats', 'disclaimer'
            ]
            
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Champ manquant dans reponse GPT: {field}")
                    result[field] = "N/A"
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON GPT: {e}")
            return self._get_fallback_response(domain)
        except Exception as e:
            logger.error(f"Erreur appel API GPT: {e}")
            return self._get_fallback_response(domain)

    def _get_fallback_response(self, domain: str) -> Dict[str, Any]:
        """Reponse de fallback quand GPT est indisponible."""
        return {
            "domain": domain,
            "summary": "Analyse GPT indisponible. Service en mode degrade.",
            "analysis": "Le service d'analyse par IA n'est pas disponible actuellement. "
                       "Cela peut etre du a une cle API manquante ou a une erreur de connexion. "
                       "Veuillez utiliser uniquement les donnees brutes et le score ML si disponible.",
            "prediction_type": "probability" if domain == "sports" else "trend",
            "prediction_value": 0.5 if domain == "sports" else "NEUTRAL",
            "confidence": 0.0,
            "caveats": "Analyse automatique indisponible. Ne pas utiliser pour des decisions reelles.",
            "disclaimer": "Analyse a titre informatif uniquement."
        }

    def analyse_sport(self, match_data: Dict[str, Any], model_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyse un match sportif avec GPT.
        
        Args:
            match_data: Dictionnaire contenant les informations du match.
            model_score: Score optionnel du modele ML (probabilite entre 0 et 1).
        
        Returns:
            Dictionnaire contenant l'analyse structuree.
        """
        logger.info(f"Generation analyse sports pour match: {match_data.get('match_id', 'unknown')}")
        
        prompt = self._create_sports_prompt(match_data, model_score)
        result = self._call_gpt(prompt, domain="sports")
        
        # Ajouter metadonnees
        result['ml_score'] = model_score
        result['data_source'] = 'gpt_analysis'
        
        return result

    def analyse_finance(self, stock_data: Dict[str, Any], model_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyse des donnees financieres avec GPT.
        
        Args:
            stock_data: Dictionnaire contenant les informations boursieres.
            model_score: Score/tendance optionnel du modele ML.
        
        Returns:
            Dictionnaire contenant l'analyse structuree.
        """
        logger.info(f"Generation analyse finance pour: {stock_data.get('symbol', 'unknown')}")
        
        prompt = self._create_finance_prompt(stock_data, model_score)
        result = self._call_gpt(prompt, domain="finance")
        
        # Ajouter metadonnees
        result['ml_score'] = model_score
        result['data_source'] = 'gpt_analysis'
        
        return result


# Instance globale du service
gpt_service = GPTService()

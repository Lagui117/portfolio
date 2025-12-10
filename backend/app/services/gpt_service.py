"""
OpenAI GPT Service for PredictWise.

This service provides AI-powered analysis for sports and financial predictions
using OpenAI's GPT models. The analysis is strictly educational and should not
be used for making actual betting or investment decisions.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class GPTService:
    """Service for generating AI-powered analysis using OpenAI GPT."""
    
    def __init__(self):
        """Initialize the GPT service with OpenAI API key."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. GPT service will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("GPT service initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI assistant's behavior."""
        return """Tu es un assistant d'analyse pour PredictWise, une plateforme ÉDUCATIVE 
d'analyse de données sportives et financières.

RÈGLES IMPORTANTES:
1. Tu ne dois JAMAIS inciter les utilisateurs à parier ou investir de l'argent réel
2. Tes analyses sont strictement à but pédagogique et expérimental
3. Tu dois TOUJOURS rappeler les limitations et les risques
4. Tu dois répondre UNIQUEMENT en JSON valide, selon le format demandé
5. Sois factuel, nuancé et mets en avant l'incertitude inhérente aux prédictions

Ta mission est d'analyser des données et d'expliquer les facteurs qui peuvent influencer 
un résultat sportif ou une tendance boursière, dans un but d'apprentissage uniquement."""

    def _create_sports_prompt(self, match_data: Dict[str, Any], ml_score: Optional[float]) -> str:
        """Create a prompt for sports analysis."""
        prompt = f"""Analyse ce match sportif de manière éducative:

DONNÉES DU MATCH:
{json.dumps(match_data, indent=2, ensure_ascii=False)}

"""
        if ml_score is not None:
            prompt += f"SCORE DU MODÈLE ML INTERNE: {ml_score:.2%}\n\n"
        
        prompt += """Réponds UNIQUEMENT avec un JSON valide selon ce format exact:
{
  "domain": "sports",
  "summary": "résumé en 1-2 phrases",
  "analysis": "analyse détaillée des facteurs (200-300 mots max)",
  "prediction_type": "probability",
  "prediction_value": nombre entre 0 et 1,
  "confidence": nombre entre 0 et 1,
  "caveats": "limitations importantes de cette analyse",
  "educational_reminder": "rappel que c'est expérimental et éducatif"
}"""
        return prompt

    def _create_finance_prompt(self, stock_data: Dict[str, Any], ml_score: Optional[float]) -> str:
        """Create a prompt for financial analysis."""
        prompt = f"""Analyse ces données boursières de manière éducative:

DONNÉES FINANCIÈRES:
{json.dumps(stock_data, indent=2, ensure_ascii=False)}

"""
        if ml_score is not None:
            prompt += f"PRÉDICTION DU MODÈLE ML INTERNE: {ml_score}\n\n"
        
        prompt += """Réponds UNIQUEMENT avec un JSON valide selon ce format exact:
{
  "domain": "finance",
  "summary": "résumé en 1-2 phrases",
  "analysis": "analyse détaillée des indicateurs (200-300 mots max)",
  "prediction_type": "trend",
  "prediction_value": "UP", "DOWN" ou "NEUTRAL",
  "confidence": nombre entre 0 et 1,
  "caveats": "limitations importantes de cette analyse",
  "educational_reminder": "rappel que c'est expérimental et éducatif"
}"""
        return prompt

    def _call_gpt(self, user_prompt: str, domain: str = "sports") -> Dict[str, Any]:
        """Call OpenAI GPT API and parse JSON response."""
        if not self.client:
            return self._get_fallback_response(domain)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Plus économique que gpt-4
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Réponses plus cohérentes et factuelles
                response_format={"type": "json_object"}  # Force la réponse JSON
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validation des champs obligatoires
            required_fields = ['domain', 'summary', 'analysis', 'prediction_type', 
                             'prediction_value', 'confidence', 'caveats', 'educational_reminder']
            
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field in GPT response: {field}")
                    result[field] = "N/A"
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT JSON response: {e}")
            return self._get_fallback_response(domain)
        except Exception as e:
            logger.error(f"GPT API call failed: {e}")
            return self._get_fallback_response(domain)

    def _get_fallback_response(self, domain: str) -> Dict[str, Any]:
        """Return a fallback response when GPT is unavailable."""
        return {
            "domain": domain,
            "summary": "Analyse GPT indisponible. Service en mode dégradé.",
            "analysis": "Le service d'analyse par IA n'est pas disponible actuellement. "
                       "Cela peut être dû à une clé API manquante ou à une erreur de connexion. "
                       "Veuillez utiliser uniquement les données brutes et le score ML si disponible.",
            "prediction_type": "probability" if domain == "sports" else "trend",
            "prediction_value": 0.5 if domain == "sports" else "NEUTRAL",
            "confidence": 0.0,
            "caveats": "Analyse automatique indisponible. Ne pas utiliser pour des décisions réelles.",
            "educational_reminder": "Cette plateforme est à but éducatif uniquement."
        }

    def analyse_sport(self, match_data: Dict[str, Any], ml_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze sports match data using GPT.
        
        Args:
            match_data: Dictionary containing match information (teams, stats, odds, etc.)
            ml_score: Optional ML model score (probability between 0 and 1)
        
        Returns:
            Dictionary containing structured analysis from GPT
        """
        logger.info(f"Generating sports analysis for match: {match_data.get('match_id', 'unknown')}")
        
        prompt = self._create_sports_prompt(match_data, ml_score)
        result = self._call_gpt(prompt, domain="sports")
        
        # Ajouter des métadonnées
        result['ml_score'] = ml_score
        result['data_source'] = 'gpt_analysis'
        
        return result

    def analyse_finance(self, stock_data: Dict[str, Any], ml_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze financial/stock data using GPT.
        
        Args:
            stock_data: Dictionary containing stock information (prices, indicators, etc.)
            ml_score: Optional ML model prediction
        
        Returns:
            Dictionary containing structured analysis from GPT
        """
        logger.info(f"Generating financial analysis for: {stock_data.get('symbol', 'unknown')}")
        
        prompt = self._create_finance_prompt(stock_data, ml_score)
        result = self._call_gpt(prompt, domain="finance")
        
        # Ajouter des métadonnées
        result['ml_score'] = ml_score
        result['data_source'] = 'gpt_analysis'
        
        return result


# Instance globale du service
gpt_service = GPTService()

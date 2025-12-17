"""
Gestion centralisée des erreurs et exceptions custom.
Définit des exceptions métier et un handler global.
"""

from typing import Optional, Dict, Any
from werkzeug.exceptions import HTTPException


class PredictWiseError(Exception):
    """Exception de base pour toutes les erreurs métier."""
    
    def __init__(
        self,
        message: str,
        error_type: str = "application_error",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire pour réponse JSON."""
        return {
            "error": {
                "type": self.error_type,
                "message": self.message,
                "details": self.details
            }
        }


class ValidationError(PredictWiseError):
    """Erreur de validation des données d'entrée."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type="validation_error",
            details=details,
            status_code=400
        )


class AuthenticationError(PredictWiseError):
    """Erreur d'authentification."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_type="authentication_error",
            status_code=401
        )


class AuthorizationError(PredictWiseError):
    """Erreur d'autorisation."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_type="authorization_error",
            status_code=403
        )


class ResourceNotFoundError(PredictWiseError):
    """Ressource introuvable."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            error_type="resource_not_found",
            details={"resource": resource, "identifier": identifier},
            status_code=404
        )


class ExternalAPIError(PredictWiseError):
    """Erreur lors de l'appel à une API externe."""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"External API error ({service}): {message}",
            error_type="external_api_error",
            details={"service": service, **(details or {})},
            status_code=502
        )


class GPTServiceError(PredictWiseError):
    """Erreur spécifique au service GPT."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"GPT service error: {message}",
            error_type="gpt_service_error",
            details=details,
            status_code=503
        )


class DatabaseError(PredictWiseError):
    """Erreur de base de données."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Database error: {message}",
            error_type="database_error",
            details=details,
            status_code=500
        )


def register_error_handlers(app):
    """
    Enregistre les gestionnaires d'erreurs globaux dans l'application Flask.
    
    Args:
        app: Instance Flask
    """
    
    @app.errorhandler(PredictWiseError)
    def handle_predictwise_error(error: PredictWiseError):
        """Gère toutes les exceptions PredictWise custom."""
        return error.to_dict(), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Gère les exceptions HTTP Werkzeug."""
        return {
            "error": {
                "type": "http_error",
                "message": error.description or str(error),
                "details": {"code": error.code}
            }
        }, error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Gère les erreurs inattendues."""
        app.logger.error(f"Unexpected error: {error}", exc_info=True)
        return {
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred",
                "details": {}
            }
        }, 500

"""Authentication endpoints."""
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from app.core.database import db
from app.models.user import User
from app.core.security import (
    create_access_token, 
    decode_access_token,
    validate_email,
    validate_password_strength
)
from functools import wraps

# Create namespace
api = Namespace('auth', description='Authentication operations')

# Define models for Swagger documentation
register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'username': fields.String(required=True, description='Username', example='johndoe'),
    'password': fields.String(required=True, description='Password (min 8 chars, 1 upper, 1 lower, 1 digit)', example='SecurePass123'),
    'first_name': fields.String(description='First name', example='John'),
    'last_name': fields.String(description='Last name', example='Doe'),
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'password': fields.String(required=True, description='Password', example='SecurePass123'),
})

token_response = api.model('TokenResponse', {
    'access_token': fields.String(description='JWT access token'),
    'token_type': fields.String(description='Token type', example='Bearer'),
    'expires_in': fields.Integer(description='Token expiration in seconds'),
    'user': fields.Raw(description='User information'),
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(description='Error message'),
    'details': fields.Raw(description='Additional error details'),
})


def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return {'error': 'Invalid token format. Use: Bearer <token>'}, 401
        
        if not token:
            return {'error': 'Token manquant. Veuillez vous authentifier.'}, 401
        
        # Decode token
        payload = decode_access_token(token)
        if not payload:
            return {'error': 'Token invalide ou expiré.'}, 401
        
        # Get user from database
        current_user = db.session.get(User, payload['user_id'])
        if not current_user or not current_user.is_active:
            return {'error': 'Utilisateur non trouvé ou inactif.'}, 401
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated


@api.route('/register')
@api.route('/signup')  # Alias for compatibility
class Register(Resource):
    """User registration endpoint."""
    
    @api.expect(register_model, validate=True)
    @api.response(201, 'User created successfully', token_response)
    @api.response(400, 'Validation error', error_response)
    def post(self):
        """Create a new user account.
        
        Validates email format, username uniqueness, and password strength.
        Returns JWT access token on success.
        """
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return {
                'error': 'Champs manquants',
                'details': {'missing_fields': missing_fields}
            }, 400
        
        email = data['email'].strip().lower()
        username = data['username'].strip()
        password = data['password']
        
        # Validate email format
        if not validate_email(email):
            return {'error': 'Format d\'email invalide'}, 400
        
        # Validate username length
        if len(username) < 3 or len(username) > 80:
            return {'error': 'Le nom d\'utilisateur doit contenir entre 3 et 80 caractères'}, 400
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return {'error': error_msg}, 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return {'error': 'Cet email est déjà utilisé'}, 400
        
        if User.query.filter_by(username=username).first():
            return {'error': 'Ce nom d\'utilisateur est déjà pris'}, 400
        
        # Create new user
        try:
            user = User(
                email=email,
                username=username,
                first_name=data.get('first_name', '').strip(),
                last_name=data.get('last_name', '').strip(),
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate access token
            from flask import current_app
            access_token = create_access_token(user.id)
            expires_in = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
            
            return {
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': expires_in,
                'user': user.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': 'Erreur lors de la création du compte', 'details': str(e)}, 500


@api.route('/login')
class Login(Resource):
    """User login endpoint."""
    
    @api.expect(login_model, validate=True)
    @api.response(200, 'Login successful', token_response)
    @api.response(401, 'Invalid credentials', error_response)
    def post(self):
        """Authenticate user and return JWT token.
        
        Verifies email and password, updates last login timestamp.
        """
        data = request.get_json()
        
        if not all(k in data for k in ['email', 'password']):
            return {'error': 'Email et mot de passe requis'}, 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return {'error': 'Email ou mot de passe invalide'}, 401
        
        if not user.is_active:
            return {'error': 'Ce compte est désactivé'}, 401
        
        # Update last login
        user.update_last_login()
        db.session.commit()
        
        # Generate access token
        from flask import current_app
        access_token = create_access_token(user.id)
        expires_in = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': expires_in,
            'user': user.to_dict()
        }, 200


@api.route('/me')
class Me(Resource):
    """Current user endpoint."""
    
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized', error_response)
    def get(self, current_user):
        """Get current authenticated user information with statistics."""
        return {'user': current_user.to_dict(include_stats=True)}, 200
    
    @token_required
    @api.expect(api.model('UpdateProfile', {
        'first_name': fields.String(description='First name'),
        'last_name': fields.String(description='Last name'),
    }))
    @api.response(200, 'Profile updated')
    def put(self, current_user):
        """Update current user profile."""
        data = request.get_json()
        
        if 'first_name' in data:
            current_user.first_name = data['first_name'].strip()
        
        if 'last_name' in data:
            current_user.last_name = data['last_name'].strip()
        
        try:
            db.session.commit()
            return {'message': 'Profil mis à jour', 'user': current_user.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Erreur lors de la mise à jour', 'details': str(e)}, 500

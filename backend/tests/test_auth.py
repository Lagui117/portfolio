"""Unit tests for authentication endpoints."""
import pytest
from app.main import create_app
from app.core.database import db
from app.models.user import User


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_signup_success(client):
    """Test successful user registration."""
    response = client.post('/api/v1/auth/signup', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert data['user']['email'] == 'test@example.com'


def test_signup_duplicate_email(client):
    """Test signup with duplicate email."""
    # First signup
    client.post('/api/v1/auth/signup', json={
        'email': 'test@example.com',
        'username': 'testuser1',
        'password': 'password123'
    })
    
    # Second signup with same email
    response = client.post('/api/v1/auth/signup', json={
        'email': 'test@example.com',
        'username': 'testuser2',
        'password': 'password123'
    })
    
    assert response.status_code == 400


def test_login_success(client):
    """Test successful login."""
    # Signup first
    client.post('/api/v1/auth/signup', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data


def test_login_invalid_credentials(client):
    """Test login with wrong password."""
    # Signup
    client.post('/api/v1/auth/signup', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Login with wrong password
    response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401

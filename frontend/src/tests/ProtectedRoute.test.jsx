import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PrivateRoute from '../components/PrivateRoute';
import * as useAuthModule from '../hooks/useAuth';

vi.mock('../hooks/useAuth');

const TestComponent = () => <div>Protected Content</div>;

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('redirects to login when not authenticated', () => {
    // Mock useAuth pour retourner non authentifié
    useAuthModule.useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: false,
      user: null
    });
    
    render(
      <BrowserRouter>
        <PrivateRoute>
          <TestComponent />
        </PrivateRoute>
      </BrowserRouter>
    );
    
    // Le contenu protégé ne devrait pas être visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    // Mock useAuth pour retourner authentifié
    useAuthModule.useAuth.mockReturnValue({
      isAuthenticated: true,
      loading: false,
      user: { id: 1, email: 'test@example.com' }
    });
    
    render(
      <BrowserRouter>
        <PrivateRoute>
          <TestComponent />
        </PrivateRoute>
      </BrowserRouter>
    );
    
    // Le contenu protégé devrait être visible
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('shows loading state when loading', () => {
    // Mock useAuth pour retourner en chargement
    useAuthModule.useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: true,
      user: null
    });
    
    render(
      <BrowserRouter>
        <PrivateRoute>
          <TestComponent />
        </PrivateRoute>
      </BrowserRouter>
    );
    
    // Le message de chargement devrait être visible
    expect(screen.getByText(/chargement/i)).toBeInTheDocument();
    // Le contenu protégé ne devrait pas être visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
});

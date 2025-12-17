import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../routes/LoginPage';
import * as authService from '../services/authService';

vi.mock('../services/authService');

const MockedLoginPage = () => (
  <BrowserRouter>
    <LoginPage />
  </BrowserRouter>
);

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders login form', () => {
    render(<MockedLoginPage />);
    
    // Utiliser getElementById pour les champs
    expect(document.getElementById('email')).toBeInTheDocument();
    expect(document.getElementById('password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /connexion|se connecter/i })).toBeInTheDocument();
  });

  it('calls authService.login on submit with valid credentials', async () => {
    authService.login.mockResolvedValue({
      access_token: 'fake-token',
      user: { id: 1, email: 'test@example.com' }
    });
    
    render(<MockedLoginPage />);
    
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
    
    const submitButton = screen.getByRole('button', { name: /connexion|se connecter/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith(
        expect.objectContaining({
          email: 'test@example.com',
          password: 'Password123!'
        })
      );
    });
  });

  it('handles login failure gracefully', async () => {
    authService.login.mockRejectedValue({
      response: { data: { error: 'Identifiants invalides' } }
    });
    
    render(<MockedLoginPage />);
    
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'WrongPassword' } });
    
    const submitButton = screen.getByRole('button', { name: /connexion|se connecter/i });
    fireEvent.click(submitButton);
    
    // Vérifie que login a été appelé
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalled();
    });
    
    // Le formulaire devrait toujours être là après une erreur
    expect(document.getElementById('email')).toBeInTheDocument();
  });
});

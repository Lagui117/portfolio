import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SignupPage from '../routes/SignupPage';
import * as authService from '../services/authService';

vi.mock('../services/authService');

const MockedSignupPage = () => (
  <BrowserRouter>
    <SignupPage />
  </BrowserRouter>
);

describe('SignupPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders signup form with all fields', () => {
    render(<MockedSignupPage />);
    
    // Vérifier que les champs principaux sont présents via leurs IDs
    expect(document.getElementById('email')).toBeInTheDocument();
    expect(document.getElementById('username')).toBeInTheDocument();
    expect(document.getElementById('password')).toBeInTheDocument();
    expect(document.getElementById('confirmPassword')).toBeInTheDocument();
  });

  it('shows validation error when fields are empty', async () => {
    render(<MockedSignupPage />);
    
    const submitButton = screen.getByRole('button', { name: /s'inscrire/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      // Chercher tous les messages d'erreur "requis"
      const errorMessages = screen.getAllByText(/requis/i);
      expect(errorMessages.length).toBeGreaterThan(0);
    });
  });

  it('calls authService.signup on form submit with valid data', async () => {
    authService.signup.mockResolvedValue({
      access_token: 'fake-token',
      user: { id: 1, email: 'test@example.com', username: 'testuser' }
    });
    
    render(<MockedSignupPage />);
    
    // Utiliser getElementById pour tous les champs
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'SecurePass123!' } });
    
    const submitButton = screen.getByRole('button', { name: /s'inscrire/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authService.signup).toHaveBeenCalled();
    });
  });

  it('handles signup failure gracefully', async () => {
    authService.signup.mockRejectedValue({
      response: { data: { error: 'Email deja utilise' } }
    });
    
    render(<MockedSignupPage />);
    
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'SecurePass123!' } });
    
    const submitButton = screen.getByRole('button', { name: /s'inscrire/i });
    fireEvent.click(submitButton);
    
    // Vérifie que signup a été appelé et gère l'erreur
    await waitFor(() => {
      expect(authService.signup).toHaveBeenCalled();
    });
    
    // Le formulaire devrait toujours être là après une erreur
    expect(document.getElementById('email')).toBeInTheDocument();
  });
});

/**
 * Composants utilitaires réutilisables.
 */

import React from 'react';
import '../styles/components.css';

export function PageContainer({ children, className = '' }) {
  return (
    <div className={`page-container ${className}`}>
      {children}
    </div>
  );
}

export function Card({ children, className = '', onClick }) {
  return (
    <div className={`card ${className}`} onClick={onClick}>
      {children}
    </div>
  );
}

export function SectionTitle({ children }) {
  return <h2 className="section-title">{children}</h2>;
}

export function ErrorBanner({ message, onClose }) {
  if (!message) return null;
  
  return (
    <div className="error-banner">
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="error-close">×</button>
      )}
    </div>
  );
}

export function SuccessBanner({ message, onClose }) {
  if (!message) return null;
  
  return (
    <div className="success-banner">
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="success-close">×</button>
      )}
    </div>
  );
}

export function LoadingIndicator({ text = 'Chargement en cours...' }) {
  return (
    <div className="loading-indicator">
      <div className="spinner"></div>
      <p>{text}</p>
    </div>
  );
}

export function EmptyState({ title, description }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      {description && <p>{description}</p>}
    </div>
  );
}

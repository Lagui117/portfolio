/**
 * AIChat - Composant de chat IA intégré (Copilote PredictWise).
 * Assistant d'analyse et copilote décisionnel premium.
 */

import { useState, useEffect, useRef } from 'react';
import chatService from '../services/chatService';
import '../styles/ai-chat.css';

const AIChat = ({ isOpen, onClose, context = {}, domain = 'general' }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Message d'accueil initial
  const welcomeMessage = {
    role: 'assistant',
    content: `Bienvenue. Je suis votre **Copilote IA**.

Je peux vous aider à :
• Analyser vos données et résultats
• Expliquer les indicateurs et métriques
• Comparer différentes analyses
• Identifier des opportunités

Posez-moi votre question.`,
    timestamp: new Date().toISOString()
  };

  // Charger les suggestions au montage
  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        const data = await chatService.getSuggestions(domain);
        setSuggestions(data.suggestions || []);
      } catch (error) {
        console.error('Erreur chargement suggestions:', error);
      }
    };
    loadSuggestions();
  }, [domain]);

  // Initialiser avec le message d'accueil
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([welcomeMessage]);
    }
  }, []);

  // Scroll automatique vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus sur l'input quand le chat s'ouvre
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  const handleSendMessage = async (messageText = inputValue) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: messageText.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(
        messageText.trim(),
        context,
        conversationId
      );

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.response?.content || "Je n'ai pas pu traiter votre demande.",
        timestamp: response.response?.timestamp || new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Erreur envoi message:', error);
      const errorMessage = {
        role: 'assistant',
        content: "Une erreur est survenue. Veuillez réessayer.",
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleClearChat = async () => {
    try {
      await chatService.clearHistory(conversationId);
      setMessages([welcomeMessage]);
      setConversationId(null);
    } catch (error) {
      console.error('Erreur clear chat:', error);
    }
  };

  const formatMessage = (content) => {
    // Convertir le markdown basique en HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^• /gm, '<span class="bullet">•</span> ')
      .replace(/\n/g, '<br />');
  };

  if (!isOpen) return null;

  return (
    <div className={`ai-chat ${isMinimized ? 'minimized' : ''}`}>
      {/* Header */}
      <div className="ai-chat-header">
        <div className="ai-chat-header-left">
          <div className="ai-chat-avatar">
            <span>🤖</span>
          </div>
          <div className="ai-chat-title">
            <span className="ai-chat-name">Copilote IA</span>
            <span className="ai-chat-status">
              <span className="status-dot"></span>
              En ligne
            </span>
          </div>
        </div>
        <div className="ai-chat-header-actions">
          <button 
            className="ai-chat-action-btn" 
            onClick={handleClearChat}
            title="Nouvelle conversation"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14"/>
            </svg>
          </button>
          <button 
            className="ai-chat-action-btn" 
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? "Agrandir" : "Réduire"}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {isMinimized ? (
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
              ) : (
                <path d="M4 14h6v6M14 10h6V4M4 14l6-6M14 10l6-6"/>
              )}
            </svg>
          </button>
          <button 
            className="ai-chat-action-btn close" 
            onClick={onClose}
            title="Fermer"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      {!isMinimized && (
        <>
          <div className="ai-chat-messages">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`ai-chat-message ${msg.role} ${msg.isError ? 'error' : ''}`}
              >
                {msg.role === 'assistant' && (
                  <div className="message-avatar">🤖</div>
                )}
                <div className="message-content">
                  <div 
                    className="message-text"
                    dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                  />
                  <div className="message-time">
                    {new Date(msg.timestamp).toLocaleTimeString('fr-FR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="ai-chat-message assistant loading">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {messages.length <= 1 && suggestions.length > 0 && (
            <div className="ai-chat-suggestions">
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="ai-chat-input-container">
            <textarea
              ref={inputRef}
              className="ai-chat-input"
              placeholder="Posez votre question..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              rows={1}
              disabled={isLoading}
            />
            <button
              className="ai-chat-send-btn"
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
            </button>
          </div>

          {/* Footer */}
          <div className="ai-chat-footer">
            <span>Propulsé par GPT-4 • Analyse uniquement</span>
          </div>
        </>
      )}
    </div>
  );
};

export default AIChat;

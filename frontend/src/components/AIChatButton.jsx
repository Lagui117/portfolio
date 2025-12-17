/**
 * AIChatButton - Bouton flottant pour ouvrir le Copilote IA.
 */

import { useState } from 'react';
import AIChat from './AIChat';
import '../styles/ai-chat.css';

const AIChatButton = ({ context = {}, domain = 'general' }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button 
          className="ai-chat-fab" 
          onClick={() => setIsOpen(true)}
          title="Ouvrir le Copilote IA"
        >
          <span>🤖</span>
        </button>
      )}

      {/* Chat Window */}
      <AIChat 
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        context={context}
        domain={domain}
      />
    </>
  );
};

export default AIChatButton;

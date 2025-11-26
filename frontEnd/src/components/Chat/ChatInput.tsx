import { useState, FormEvent } from 'react';
import { useChat } from '@/contexts/ChatContext';

export function ChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isSendingMessage, isSessionActive } = useChat();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSendingMessage) return;

    await sendMessage(input.trim());
    setInput('');
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Escribe tu pregunta aquí..."
        disabled={!isSessionActive || isSendingMessage}
        className="chat-input"
        rows={3}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <button
        type="submit"
        disabled={!isSessionActive || isSendingMessage || !input.trim()}
        className="btn-send"
      >
        {isSendingMessage ? 'Enviando...' : 'Enviar'}
      </button>
    </form>
  );
}
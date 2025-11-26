import ReactMarkdown from 'react-markdown';
import type { ChatMessage as ChatMessageType } from '@/types/api.types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import clsx from 'clsx';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const timeAgo = formatDistanceToNow(message.timestamp, { addSuffix: true, locale: es });

  return (
    <div className={clsx('message', `message-${message.role}`)}>
      <div className="message-header">
        <span className="message-role">
          {message.role === 'user' ? '👤 Tú' : message.role === 'assistant' ? '🤖 Tutor' : '⚙️ Sistema'}
        </span>
        <span className="message-time">{timeAgo}</span>
      </div>

      <div className="message-content">
        {message.role === 'assistant' ? (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        ) : (
          <p>{message.content}</p>
        )}
      </div>

      {message.metadata && (
        <div className="message-metadata">
          {message.metadata.agent_used && (
            <span className="metadata-tag">Agente: {message.metadata.agent_used}</span>
          )}
          {message.metadata.cognitive_state && (
            <span className="metadata-tag">Estado: {message.metadata.cognitive_state}</span>
          )}
          {message.metadata.ai_involvement !== undefined && (
            <span className="metadata-tag">
              IA: {Math.round(message.metadata.ai_involvement * 100)}%
            </span>
          )}
          {message.metadata.blocked && (
            <span className="metadata-tag blocked">BLOQUEADO</span>
          )}
        </div>
      )}
    </div>
  );
}
import { useChat } from '@/contexts/ChatContext';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { SessionStarter } from './SessionStarter';
import './Chat.css';

export function ChatContainer() {
  const { currentSession } = useChat();

  if (!currentSession) {
    return <SessionStarter />;
  }

  return (
    <div className="chat-container">
      <ChatHeader />
      <ChatMessages />
      <ChatInput />
    </div>
  );
}
/**
 * Página para estudiantes - Vista de chat con el tutor AI
 */
import { ChatProvider } from '@/contexts/ChatContext';
import { ChatContainer } from '@/components/Chat/ChatContainer';

export function StudentPage() {
  return (
    <ChatProvider>
      <ChatContainer />
    </ChatProvider>
  );
}
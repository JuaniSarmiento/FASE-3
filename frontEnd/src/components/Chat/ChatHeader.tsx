import { useChat } from '@/contexts/ChatContext';

export function ChatHeader() {
  const { currentSession, endSession, isLoading } = useChat();

  if (!currentSession) return null;

  const handleEndSession = () => {
    const confirmed = window.confirm(
      '¿Estás seguro que deseas finalizar la sesión?\n\n' +
      'Se guardará tu evaluación de proceso cognitivo, pero no podrás continuar esta sesión.\n\n' +
      'Esta acción no se puede deshacer.'
    );

    if (confirmed) {
      endSession();
    }
  };

  return (
    <div className="chat-header">
      <div className="chat-header-info">
        <h2>🤖 Tutor AI-Native</h2>
        <p className="session-info">
          Sesión: {currentSession.id.slice(0, 8)}... | Modo: {currentSession.mode} | Estado: <span className={`status-${currentSession.status.toLowerCase()}`}>{currentSession.status}</span>
        </p>
      </div>
      <button
        onClick={handleEndSession}
        disabled={isLoading || currentSession.status !== 'ACTIVE'}
        className="btn-end-session"
      >
        Finalizar Sesión
      </button>
    </div>
  );
}
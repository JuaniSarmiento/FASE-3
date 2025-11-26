import { useState, FormEvent } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { SessionMode } from '@/types/api.types';

export function SessionStarter() {
  const [studentId, setStudentId] = useState('');
  const [activityId, setActivityId] = useState('');
  const [mode, setMode] = useState<SessionMode>(SessionMode.TUTOR);
  const { createSession, isLoading, error } = useChat();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!studentId.trim() || !activityId.trim()) return;

    await createSession(studentId.trim(), activityId.trim(), mode);
  };

  return (
    <div className="session-starter">
      <div className="session-starter-card">
        <h1>🎓 Ecosistema AI-Native</h1>
        <p className="subtitle">Aprendizaje de Programación con IA Generativa</p>

        <form onSubmit={handleSubmit} className="session-form">
          <div className="form-group">
            <label htmlFor="studentId">ID de Estudiante</label>
            <input
              id="studentId"
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="student_001"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="activityId">ID de Actividad</label>
            <input
              id="activityId"
              type="text"
              value={activityId}
              onChange={(e) => setActivityId(e.target.value)}
              placeholder="prog2_tp1_colas"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="mode">Modo de Aprendizaje</label>
            <select
              id="mode"
              value={mode}
              onChange={(e) => setMode(e.target.value as SessionMode)}
            >
              <option value={SessionMode.TUTOR}>Tutor Cognitivo</option>
              <option value={SessionMode.SIMULATOR}>Simulador Profesional</option>
              <option value={SessionMode.EVALUATOR}>Evaluador de Procesos</option>
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={isLoading} className="btn-start-session">
            {isLoading ? 'Creando Sesión...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="info-box">
          <h3>ℹ️ Sobre el Sistema</h3>
          <p>
            Este sistema implementa un modelo AI-Native que evalúa tu <strong>proceso cognitivo</strong>, no solo el producto final.
            El tutor te guiará sin sustituir tu razonamiento.
          </p>
        </div>
      </div>
    </div>
  );
}
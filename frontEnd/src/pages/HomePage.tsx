/**
 * Página de inicio - Selección de rol
 */
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div className="home-container">
        <header className="home-header">
          <h1>🎓 Ecosistema AI-Native</h1>
          <p className="home-subtitle">
            Sistema de Enseñanza-Aprendizaje de Programación con IA Generativa
          </p>
        </header>

        <div className="role-selection">
          <h2>Selecciona tu rol</h2>

          <div className="role-cards">
            {/* Tarjeta de Estudiante */}
            <div
              className="role-card student-card"
              onClick={() => navigate('/student')}
            >
              <div className="role-icon">👨‍🎓</div>
              <h3>Estudiante</h3>
              <p>
                Interactúa con el tutor cognitivo AI-Native. Recibe ayuda personalizada
                mientras mantienes tu agencia cognitiva.
              </p>
              <ul className="role-features">
                <li>✅ Tutor Cognitivo T-IA-Cog</li>
                <li>✅ Simuladores Profesionales</li>
                <li>✅ Evaluación de Procesos</li>
                <li>✅ Trazabilidad N4</li>
              </ul>
              <button className="btn-role btn-student">
                Entrar como Estudiante →
              </button>
            </div>

            {/* Tarjeta de Docente */}
            <div
              className="role-card teacher-card"
              onClick={() => navigate('/teacher')}
            >
              <div className="role-icon">👨‍🏫</div>
              <h3>Docente</h3>
              <p>
                Crea y gestiona actividades con políticas pedagógicas configurables.
                Monitorea el proceso cognitivo de tus estudiantes.
              </p>
              <ul className="role-features">
                <li>✅ Crear Actividades AI-Native</li>
                <li>✅ Configurar Políticas Pedagógicas</li>
                <li>✅ Monitorear Trazas N4</li>
                <li>✅ Evaluar Procesos Cognitivos</li>
              </ul>
              <button className="btn-role btn-teacher">
                Entrar como Docente →
              </button>
            </div>
          </div>
        </div>

        <footer className="home-footer">
          <div className="info-section">
            <h3>Sobre el Sistema</h3>
            <p>
              Este MVP implementa el <strong>Modelo AI-Native</strong> para la enseñanza
              de programación en la era de la IA generativa. El sistema captura y evalúa
              el <strong>proceso cognitivo completo</strong> (Nivel N4), no solo el
              producto final.
            </p>
          </div>

          <div className="architecture-info">
            <h4>🏗️ Arquitectura</h4>
            <div className="architecture-badges">
              <span className="badge">C4 Extended</span>
              <span className="badge">6 Agentes IA</span>
              <span className="badge">N4 Traceability</span>
              <span className="badge">Clean Architecture</span>
              <span className="badge">FastAPI + React</span>
            </div>
          </div>

          <p className="author">
            <strong>Tesis Doctoral</strong> - Mag. en Ing. de Software Alberto Cortez
            <br />
            <small>Universidad Tecnológica Nacional</small>
          </p>
        </footer>
      </div>
    </div>
  );
}
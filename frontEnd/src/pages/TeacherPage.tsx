/**
 * Página para docentes - Gestión de actividades
 */
import { useState } from 'react';
import { ActivityCreator, ActivityList } from '@/components/Activities';
import type { ActivityResponse } from '@/types/api.types';
import './TeacherPage.css';

export function TeacherPage() {
  const [teacherId] = useState('teacher_001'); // TODO: Obtener del contexto de auth
  const [view, setView] = useState<'list' | 'create' | 'edit'>('list');
  const [selectedActivity, setSelectedActivity] = useState<ActivityResponse | null>(null);

  const handleCreateSuccess = (activity: ActivityResponse) => {
    console.log('Actividad creada:', activity);
    setView('list');
  };

  const handleEdit = (activity: ActivityResponse) => {
    setSelectedActivity(activity);
    setView('edit');
    // TODO: Implementar edición
    alert('Función de edición en desarrollo. Por ahora usa clonar + modificar.');
    setView('list');
  };

  const handleView = (activity: ActivityResponse) => {
    setSelectedActivity(activity);
    // TODO: Implementar vista de detalles
    alert(`Ver detalles de: ${activity.title}\n\nFuncionalidad en desarrollo.`);
  };

  return (
    <div className="teacher-page">
      <header className="teacher-header">
        <div className="teacher-header-content">
          <h1>🎓 Panel del Docente</h1>
          <p className="subtitle">Gestión de Actividades AI-Native</p>
        </div>

        <div className="teacher-actions">
          {view === 'list' && (
            <button
              onClick={() => setView('create')}
              className="btn-primary btn-create"
            >
              ➕ Nueva Actividad
            </button>
          )}
          {view !== 'list' && (
            <button
              onClick={() => setView('list')}
              className="btn-secondary"
            >
              ← Volver al Listado
            </button>
          )}
        </div>
      </header>

      <main className="teacher-content">
        {view === 'list' && (
          <ActivityList
            teacherId={teacherId}
            onEdit={handleEdit}
            onView={handleView}
          />
        )}

        {view === 'create' && (
          <ActivityCreator
            teacherId={teacherId}
            onSuccess={handleCreateSuccess}
            onCancel={() => setView('list')}
          />
        )}

        {view === 'edit' && selectedActivity && (
          <div>
            <h2>Editar Actividad (En desarrollo)</h2>
            <p>Por ahora, usa la función "Clonar" para duplicar y modificar.</p>
          </div>
        )}
      </main>
    </div>
  );
}
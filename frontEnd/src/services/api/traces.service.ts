/**
 * Servicio para consulta de trazabilidad cognitiva N4
 */

import { BaseApiService } from './base.service';
import type { CognitiveTrace, CognitivePath, TraceLevel } from '@/types/api.types';

/**
 * TracesService - Consulta de trazabilidad usando base class
 */
class TracesService extends BaseApiService {
  constructor() {
    super('/traces');
  }

  /**
   * Obtener trazas de una sesión
   */
  async getBySession(
    sessionId: string,
    traceLevel?: TraceLevel
  ): Promise<CognitiveTrace[]> {
    const params = traceLevel ? `?trace_level=${traceLevel}` : '';
    return this.get<CognitiveTrace[]>(`/${sessionId}${params}`);
  }

  /**
   * Obtener camino cognitivo completo de una sesión
   */
  async getCognitivePath(sessionId: string): Promise<CognitivePath> {
    return this.get<CognitivePath>(`/${sessionId}/cognitive-path`);
  }

  /**
   * Obtener trazas por estudiante
   */
  async getByStudent(studentId: string): Promise<CognitiveTrace[]> {
    return this.get<CognitiveTrace[]>(`/student/${studentId}`);
  }
}

// Export singleton instance
export const tracesService = new TracesService();
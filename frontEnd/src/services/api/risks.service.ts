/**
 * Servicio para consulta de riesgos y evaluaciones
 */

import { BaseApiService } from './base.service';
import type { Risk, EvaluationReport } from '@/types/api.types';

/**
 * RisksService - Consulta de riesgos y evaluaciones usando base class
 */
class RisksService extends BaseApiService {
  constructor() {
    super('/risks');
  }

  /**
   * Obtener riesgos de una sesión
   */
  async getBySession(sessionId: string, resolved?: boolean): Promise<Risk[]> {
    const params = resolved !== undefined ? `?resolved=${resolved}` : '';
    return this.get<Risk[]>(`/session/${sessionId}${params}`);
  }

  /**
   * Obtener riesgos críticos de una sesión
   */
  async getCritical(sessionId: string): Promise<Risk[]> {
    return this.get<Risk[]>(`/session/${sessionId}/critical`);
  }

  /**
   * Obtener evaluación de proceso de una sesión
   */
  async getEvaluation(sessionId: string): Promise<EvaluationReport> {
    return this.get<EvaluationReport>(`/evaluation/session/${sessionId}`);
  }
}

// Export singleton instance
export const risksService = new RisksService();
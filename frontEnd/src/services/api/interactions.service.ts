/**
 * Servicio para procesamiento de interacciones estudiante-IA
 */

import { BaseApiService } from './base.service';
import type { InteractionRequest, InteractionResponse } from '@/types/api.types';

/**
 * InteractionsService - Procesamiento de interacciones usando base class
 */
class InteractionsService extends BaseApiService {
  constructor() {
    super('/interactions');
  }

  /**
   * Procesar una interacción (enviar mensaje al chatbot)
   * Este es el endpoint principal que orquesta todo el flujo AI-Native
   */
  async process(data: InteractionRequest): Promise<InteractionResponse> {
    const response = await this.post<any, InteractionRequest>('', data);
    // Backend wraps response in {success, data}
    if (response.success && response.data) {
      return response.data;
    }
    return response;
  }

  /**
   * Obtener historial de interacciones de una sesión
   * (podría implementarse en el futuro)
   */
  // async getHistory(sessionId: string): Promise<InteractionSummary[]> {
  //   return this.get<InteractionSummary[]>(`/session/${sessionId}`);
  // }
}

// Export singleton instance
export const interactionsService = new InteractionsService();
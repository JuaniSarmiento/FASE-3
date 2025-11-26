/**
 * Servicio para health checks del sistema
 */

import { get } from './client';
import type { HealthResponse } from '@/types/api.types';

export const healthService = {
  /**
   * Verificar estado del sistema
   */
  check: async (): Promise<HealthResponse> => {
    return get<HealthResponse>('/health');
  },

  /**
   * Ping simple
   */
  ping: async (): Promise<{ status: string }> => {
    return get<{ status: string }>('/health/ping');
  },
};
/**
 * Servicio para gestión de sesiones de aprendizaje
 */

import { BaseApiService } from './base.service';
import type {
  SessionCreate,
  SessionUpdate,
  SessionResponse,
  SessionDetailResponse,
  PaginatedResponse,
  PaginationParams,
} from '@/types/api.types';

/**
 * SessionsService - Gestión de sesiones usando base class
 */
class SessionsService extends BaseApiService {
  constructor() {
    super('/sessions');
  }

  /**
   * Crear una nueva sesión
   */
  async create(data: SessionCreate): Promise<SessionResponse> {
    return this.post<SessionResponse, SessionCreate>('', data);
  }

  /**
   * Obtener sesión por ID
   */
  async getById(sessionId: string): Promise<SessionDetailResponse> {
    return this.get<SessionDetailResponse>(`/${sessionId}`);
  }

  /**
   * Listar sesiones del estudiante
   */
  async list(
    studentId: string,
    pagination?: PaginationParams
  ): Promise<PaginatedResponse<SessionResponse>> {
    const params = new URLSearchParams({
      student_id: studentId,
      ...(pagination && {
        page: pagination.page.toString(),
        page_size: pagination.page_size.toString(),
      }),
    });

    return this.get<PaginatedResponse<SessionResponse>>(`?${params.toString()}`);
  }

  /**
   * Actualizar sesión
   */
  async update(sessionId: string, data: SessionUpdate): Promise<SessionResponse> {
    return this.patch<SessionResponse, SessionUpdate>(`/${sessionId}`, data);
  }

  /**
   * Finalizar sesión
   */
  async end(sessionId: string): Promise<SessionResponse> {
    return this.post<SessionResponse>(`/${sessionId}/end`);
  }

  /**
   * Eliminar sesión
   */
  async remove(sessionId: string): Promise<void> {
    return this.delete<void>(`/${sessionId}`);
  }
}

// Export singleton instance
export const sessionsService = new SessionsService();
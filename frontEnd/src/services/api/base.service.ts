import { AxiosRequestConfig } from 'axios';
import { get, post, patch, del } from './client';

/**
 * Base API Service - Clase abstracta para todos los servicios
 *
 * Proporciona métodos HTTP comunes (get, post, patch, delete) con:
 * - Manejo consistente de endpoints
 * - Type safety con generics
 * - Single point of change para cross-cutting concerns
 */
export abstract class BaseApiService {
  protected baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * GET request
   */
  protected async get<T>(endpoint: string = '', config?: AxiosRequestConfig): Promise<T> {
    return get<T>(`${this.baseUrl}${endpoint}`, config);
  }

  /**
   * POST request
   */
  protected async post<T, D = any>(
    endpoint: string = '',
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return post<T, D>(`${this.baseUrl}${endpoint}`, data, config);
  }

  /**
   * PATCH request
   */
  protected async patch<T, D = any>(
    endpoint: string = '',
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return patch<T, D>(`${this.baseUrl}${endpoint}`, data, config);
  }

  /**
   * DELETE request
   */
  protected async delete<T>(endpoint: string = '', config?: AxiosRequestConfig): Promise<T> {
    return del<T>(`${this.baseUrl}${endpoint}`, config);
  }
}
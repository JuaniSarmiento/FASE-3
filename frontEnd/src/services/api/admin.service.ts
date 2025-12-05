/**
 * Admin Service - Administración del sistema
 */
import apiClient from './client';

export interface LLMConfiguration {
  provider: 'ollama' | 'openai' | 'anthropic' | 'gemini';
  model: string;
  api_key?: string;
  base_url?: string;
  temperature?: number;
  max_tokens?: number;
  enabled: boolean;
}

export interface LLMUsageStats {
  provider: string;
  model: string;
  total_requests: number;
  total_tokens: number;
  avg_response_time_ms: number;
  error_rate: number;
  last_used: string;
}

export interface SystemMetrics {
  total_users: number;
  active_sessions: number;
  total_sessions_today: number;
  total_interactions: number;
  avg_response_time_ms: number;
  llm_usage: LLMUsageStats[];
  storage_used_mb: number;
}

class AdminService {
  /**
   * Get LLM configuration
   */
  async getLLMConfig(): Promise<LLMConfiguration[]> {
    const response = await apiClient.get('/admin/llm/config');
    return response.data;
  }

  /**
   * Update LLM configuration
   */
  async updateLLMConfig(config: LLMConfiguration): Promise<LLMConfiguration> {
    const response = await apiClient.put('/admin/llm/config', config);
    return response.data;
  }

  /**
   * Get LLM usage statistics
   */
  async getLLMUsageStats(): Promise<LLMUsageStats[]> {
    const response = await apiClient.get('/admin/llm/usage');
    return response.data;
  }

  /**
   * Get system metrics
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await apiClient.get('/admin/metrics');
    return response.data;
  }

  /**
   * Test LLM connection
   */
  async testLLMConnection(provider: string, model: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/admin/llm/test', { provider, model });
    return response.data;
  }
}

export const adminService = new AdminService();

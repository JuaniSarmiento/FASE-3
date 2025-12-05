/**
 * Reports Service - Generación de reportes
 */
import apiClient from './client';

export interface ActivityReport {
  activity_id: string;
  activity_name: string;
  total_sessions: number;
  completion_rate: number;
  avg_score: number;
  avg_ai_dependency: number;
  student_performance: StudentPerformance[];
  risk_summary: RiskSummary;
  competency_distribution: Record<string, number>;
}

export interface StudentPerformance {
  student_id: string;
  sessions_count: number;
  avg_score: number;
  competency_level: string;
  ai_dependency: number;
  risks_detected: number;
}

export interface RiskSummary {
  total_risks: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

export interface LearningAnalytics {
  period: string;
  total_students: number;
  total_sessions: number;
  avg_session_duration: number;
  most_used_agents: AgentUsage[];
  competency_trends: CompetencyTrend[];
  risk_trends: RiskTrendData[];
}

export interface AgentUsage {
  agent: string;
  usage_count: number;
  avg_satisfaction: number;
}

export interface CompetencyTrend {
  date: string;
  competency: string;
  avg_score: number;
}

export interface RiskTrendData {
  date: string;
  risk_level: string;
  count: number;
}

class ReportsService {
  /**
   * Get activity report
   */
  async getActivityReport(activityId: string): Promise<ActivityReport> {
    const response = await apiClient.get(`/reports/activity/${activityId}`);
    return response.data;
  }

  /**
   * Get learning analytics
   */
  async getLearningAnalytics(period?: string): Promise<LearningAnalytics> {
    const params = period ? { period } : {};
    const response = await apiClient.get('/reports/analytics', { params });
    return response.data;
  }

  /**
   * Export session data
   */
  async exportSessionData(sessionId: string, format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const response = await apiClient.get(`/export/session/${sessionId}`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Export activity data
   */
  async exportActivityData(activityId: string, format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const response = await apiClient.get(`/export/activity/${activityId}`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Export anonymized research data
   */
  async exportResearchData(params: {
    start_date?: string;
    end_date?: string;
    anonymize?: boolean;
  }): Promise<Blob> {
    const response = await apiClient.post('/export/research', params, {
      responseType: 'blob',
    });
    return response.data;
  }
}

export const reportsService = new ReportsService();

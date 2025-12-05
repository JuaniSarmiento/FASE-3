/**
 * Evaluations Service - Evaluador de Procesos (E-IA-Proc)
 */
import apiClient from './client';

export interface EvaluationReport {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  timestamp: string;
  reasoning_analysis: ReasoningAnalysis;
  git_analysis?: GitAnalysis;
  dimensions: EvaluationDimension[];
  ai_dependency_score: number;
  ai_usage_patterns: string[];
  reasoning_map: Record<string, any>;
  cognitive_risks: string[];
  overall_competency_level: string;
  overall_score: number;
  key_strengths: string[];
  improvement_areas: string[];
  recommendations_student: string[];
  recommendations_teacher: string[];
}

export interface ReasoningAnalysis {
  phases_identified: string[];
  phase_transitions: string[];
  reasoning_quality: string;
  conceptual_errors: ConceptualError[];
  metacognitive_evidence: string[];
  problem_solving_strategy: string;
  completeness_score: number;
}

export interface ConceptualError {
  error_type: string;
  description: string;
  location: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  recommendation: string;
}

export interface GitAnalysis {
  commits_analyzed: number;
  code_evolution_quality: string;
  consistency_score: number;
  patterns_detected: string[];
  ai_generated_code_percentage: number;
  copy_paste_detected: boolean;
}

export interface EvaluationDimension {
  dimension: string;
  score: number;
  level: 'NOVICE' | 'ADVANCED_BEGINNER' | 'COMPETENT' | 'PROFICIENT' | 'EXPERT';
  evidence: string[];
  feedback: string;
}

export interface StudentComparison {
  students: StudentEvaluationSummary[];
  comparison_metrics: ComparisonMetric[];
  insights: string[];
}

export interface StudentEvaluationSummary {
  student_id: string;
  overall_score: number;
  overall_level: string;
  ai_dependency: number;
  strengths: string[];
  weaknesses: string[];
}

export interface ComparisonMetric {
  metric: string;
  values: Record<string, number>;
  average: number;
}

class EvaluationsService {
  /**
   * Get evaluation report
   */
  async getReport(reportId: string): Promise<EvaluationReport> {
    const response = await apiClient.get(`/evaluations/report/${reportId}`);
    return response.data;
  }

  /**
   * Get evaluation for session
   */
  async getSessionEvaluation(sessionId: string): Promise<EvaluationReport> {
    const response = await apiClient.get(`/evaluations/session/${sessionId}`);
    return response.data;
  }

  /**
   * Trigger evaluation for a session
   */
  async evaluateSession(sessionId: string): Promise<EvaluationReport> {
    const response = await apiClient.post(`/evaluations/evaluate/${sessionId}`);
    return response.data;
  }

  /**
   * Get student's evaluation history
   */
  async getStudentEvaluations(studentId: string): Promise<EvaluationReport[]> {
    const response = await apiClient.get(`/evaluations/student/${studentId}`);
    return response.data;
  }

  /**
   * Compare students (for teachers)
   */
  async compareStudents(studentIds: string[], activityId?: string): Promise<StudentComparison> {
    const response = await apiClient.post('/teacher-tools/compare-students', {
      student_ids: studentIds,
      activity_id: activityId,
    });
    return response.data;
  }

  /**
   * Get real-time alerts for teacher
   */
  async getTeacherAlerts(): Promise<any[]> {
    const response = await apiClient.get('/teacher-tools/alerts');
    return response.data;
  }
}

export const evaluationsService = new EvaluationsService();

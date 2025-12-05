/**
 * Git Service - Integración Git (GIT-IA)
 */
import apiClient from './client';

export interface GitTrace {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  timestamp: string;
  event_type: 'COMMIT' | 'BRANCH' | 'MERGE' | 'TAG';
  commit_hash?: string;
  commit_message?: string;
  author_name?: string;
  author_email?: string;
  files_changed: GitFileChange[];
  patterns_detected: CodePattern[];
  lines_added: number;
  lines_deleted: number;
  complexity_delta?: number;
}

export interface GitFileChange {
  file_path: string;
  change_type: 'ADD' | 'MODIFY' | 'DELETE' | 'RENAME';
  lines_added: number;
  lines_deleted: number;
  diff?: string;
}

export interface CodePattern {
  pattern_type: string;
  confidence: number;
  description: string;
  evidence: string[];
}

export interface GitEvolution {
  session_id: string;
  student_id: string;
  traces: GitTrace[];
  overall_quality: string;
  consistency_score: number;
  ai_assistance_indicators: string[];
  development_timeline: TimelineEvent[];
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  impact: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface GitCorrelation {
  git_trace_id: string;
  cognitive_trace_ids: string[];
  correlation_score: number;
  insights: string[];
}

class GitService {
  /**
   * Get Git traces for session
   */
  async getSessionGitTraces(sessionId: string): Promise<GitTrace[]> {
    const response = await apiClient.get(`/git-traces/session/${sessionId}`);
    return response.data;
  }

  /**
   * Capture a commit
   */
  async captureCommit(data: {
    repo_path: string;
    commit_hash: string;
    session_id: string;
    student_id: string;
    activity_id: string;
  }): Promise<GitTrace> {
    const response = await apiClient.post('/git-traces/capture-commit', data);
    return response.data;
  }

  /**
   * Get code evolution analysis
   */
  async getCodeEvolution(sessionId: string): Promise<GitEvolution> {
    const response = await apiClient.get(`/git-traces/evolution/${sessionId}`);
    return response.data;
  }

  /**
   * Correlate Git with cognitive traces
   */
  async correlateTraces(gitTraceId: string): Promise<GitCorrelation> {
    const response = await apiClient.get(`/git-traces/${gitTraceId}/correlate`);
    return response.data;
  }

  /**
   * Get student's Git history
   */
  async getStudentGitHistory(studentId: string): Promise<GitTrace[]> {
    const response = await apiClient.get(`/git-traces/student/${studentId}`);
    return response.data;
  }
}

export const gitService = new GitService();

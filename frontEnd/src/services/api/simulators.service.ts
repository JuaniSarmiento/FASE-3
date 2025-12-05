/**
 * Simulators Service - Simuladores Profesionales (S-IA-X)
 */
import apiClient from './client';

export type SimulatorType = 
  | 'product_owner'
  | 'scrum_master'
  | 'tech_interviewer'
  | 'incident_responder'
  | 'client'
  | 'devsecops';

export interface SimulatorInteraction {
  simulator_type: SimulatorType;
  student_input: string;
  context?: Record<string, any>;
}

export interface SimulatorResponse {
  message: string;
  role: string;
  expects?: string[];
  metadata: {
    competencies_evaluated?: string[];
    professional_context?: string;
    authenticity_score?: number;
    feedback?: string;
  };
  trace_id?: string;
}

export interface SimulatorSession {
  id: string;
  student_id: string;
  simulator_type: SimulatorType;
  scenario: string;
  created_at: string;
  updated_at: string;
  interactions: SimulatorInteraction[];
  completed: boolean;
  evaluation?: SimulatorEvaluation;
}

export interface SimulatorEvaluation {
  competencies: Record<string, number>;
  overall_score: number;
  strengths: string[];
  improvements: string[];
  professional_readiness: number;
}

class SimulatorsService {
  /**
   * Interact with a simulator
   */
  async interact(interaction: SimulatorInteraction): Promise<SimulatorResponse> {
    const response = await apiClient.post('/simulators/interact', interaction);
    return response.data;
  }

  /**
   * Start a simulator session
   */
  async startSession(
    studentId: string,
    simulatorType: SimulatorType,
    scenario?: string
  ): Promise<SimulatorSession> {
    const response = await apiClient.post('/simulators/sessions', {
      student_id: studentId,
      simulator_type: simulatorType,
      scenario,
    });
    return response.data;
  }

  /**
   * Get simulator session
   */
  async getSession(sessionId: string): Promise<SimulatorSession> {
    const response = await apiClient.get(`/simulators/sessions/${sessionId}`);
    return response.data;
  }

  /**
   * Complete simulator session and get evaluation
   */
  async completeSession(sessionId: string): Promise<SimulatorEvaluation> {
    const response = await apiClient.post(`/simulators/sessions/${sessionId}/complete`);
    return response.data;
  }

  /**
   * Get available simulators
   */
  async getAvailableSimulators(): Promise<{ type: SimulatorType; name: string; description: string }[]> {
    const response = await apiClient.get('/simulators/available');
    return response.data;
  }

  /**
   * Get student's simulator history
   */
  async getStudentHistory(studentId: string): Promise<SimulatorSession[]> {
    const response = await apiClient.get(`/simulators/student/${studentId}/history`);
    return response.data;
  }
}

export const simulatorsService = new SimulatorsService();

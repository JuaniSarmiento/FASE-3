/**
 * Tipos TypeScript para la API del ecosistema AI-Native
 * Basados en los schemas de Pydantic del backend
 */

// ==================== ENUMS ====================

export enum SessionMode {
  TUTOR = 'TUTOR',
  EVALUATOR = 'EVALUATOR',
  SIMULATOR = 'SIMULATOR',
  RISK_ANALYST = 'RISK_ANALYST',
}

export enum SessionStatus {
  ACTIVE = 'ACTIVE',
  COMPLETED = 'COMPLETED',
  PAUSED = 'PAUSED',
  ABORTED = 'ABORTED',
}

export enum CognitiveIntent {
  UNDERSTANDING = 'UNDERSTANDING',
  IMPLEMENTATION = 'IMPLEMENTATION',
  DEBUGGING = 'DEBUGGING',
  VALIDATION = 'VALIDATION',
  EXPLORATION = 'EXPLORATION',
  JUSTIFICATION = 'JUSTIFICATION',
}

export enum CognitiveState {
  EXPLORACION_CONCEPTUAL = 'EXPLORACION_CONCEPTUAL',
  PLANIFICACION = 'PLANIFICACION',
  IMPLEMENTACION = 'IMPLEMENTACION',
  VALIDACION = 'VALIDACION',
  REFLEXION = 'REFLEXION',
  DELEGACION_TOTAL = 'DELEGACION_TOTAL',
}

export enum TraceLevel {
  N1_SUPERFICIAL = 'N1_SUPERFICIAL',
  N2_TECNICO = 'N2_TECNICO',
  N3_INTERACCIONAL = 'N3_INTERACCIONAL',
  N4_COGNITIVO = 'N4_COGNITIVO',
}

export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

// ==================== SESSION ====================

export interface SessionCreate {
  student_id: string;
  activity_id: string;
  mode: SessionMode;
}

export interface SessionUpdate {
  mode?: SessionMode;
  status?: SessionStatus;
}

export interface SessionResponse {
  id: string;
  student_id: string;
  activity_id: string;
  mode: string;
  status: string;
  start_time: string;
  end_time: string | null;
  trace_count: number;
  risk_count: number;
  created_at: string;
  updated_at: string;
}

export interface SessionDetailResponse extends SessionResponse {
  traces_summary: Record<string, number>;
  risks_summary: Record<string, number>;
  ai_dependency_score: number | null;
}

// ==================== INTERACTION ====================

export interface InteractionRequest {
  session_id: string;
  prompt: string;
  context?: Record<string, any>;
  cognitive_intent?: CognitiveIntent;
}

export interface InteractionResponse {
  interaction_id: string;
  session_id: string;
  response: string;
  agent_used: string;
  cognitive_state_detected: string;
  ai_involvement: number;
  blocked: boolean;
  block_reason: string | null;
  trace_id: string;
  risks_detected: string[];
  timestamp: string;
}

export interface InteractionSummary {
  id: string;
  prompt_preview: string;
  agent_used: string;
  cognitive_state: string;
  ai_involvement: number;
  blocked: boolean;
  timestamp: string;
}

// ==================== TRACES ====================

export interface CognitiveTrace {
  id: string;
  session_id: string;
  trace_level: TraceLevel;
  interaction_type: string;
  cognitive_state: string;
  cognitive_intent: string;
  content: string;
  ai_involvement: number;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface CognitivePath {
  session_id: string;
  states_sequence: string[];
  transitions: Array<{
    from_state: string;
    to_state: string;
    timestamp: string;
    trigger: string;
  }>;
  ai_dependency_evolution: Array<{
    timestamp: string;
    ai_involvement: number;
  }>;
  strategy_changes: string[];
}

// ==================== RISKS ====================

export interface Risk {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  risk_type: string;
  risk_level: RiskLevel;
  dimension: string;
  description: string;
  evidence: string[];
  recommendations: string[];
  trace_ids: string[];
  resolved: boolean;
  resolution_notes: string | null;
  timestamp: string;
}

// ==================== EVALUATION ====================

export interface EvaluationDimension {
  dimension: string;
  score: number;
  level: string;
  observations: string;
}

export interface EvaluationReport {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  overall_competency_level: string;
  overall_score: number;
  dimensions: EvaluationDimension[];
  key_strengths: string[];
  improvement_areas: string[];
  reasoning_analysis: string;
  ai_dependency_analysis: string;
  timestamp: string;
}

// ==================== API RESPONSE WRAPPERS ====================

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp?: string;
}

export interface APIError {
  success: false;
  error: {
    error_code: string;
    message: string;
    field: string | null;
    extra?: Record<string, any>;
  };
  timestamp: string;
}

export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: PaginationMeta;
  message?: string;
}

// ==================== HEALTH ====================

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  agents: Record<string, string>;
  timestamp: string;
}

// ==================== MESSAGE (for Chat UI) ====================

/**
 * Estados posibles de un mensaje durante el envío
 */
export type MessageStatus = 'pending' | 'sent' | 'retrying' | 'failed';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: MessageStatus;  // Estado del mensaje (solo para user messages)
  retry_count?: number;    // Contador de reintentos
  metadata?: {
    agent_used?: string;
    cognitive_state?: string;
    ai_involvement?: number;
    blocked?: boolean;
    block_reason?: string;
    risks_detected?: string[];
  };
}

// ==================== ACTIVITIES ====================

export enum ActivityDifficulty {
  INICIAL = 'INICIAL',
  INTERMEDIO = 'INTERMEDIO',
  AVANZADO = 'AVANZADO',
}

export enum ActivityStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  ARCHIVED = 'archived',
}

export enum HelpLevel {
  MINIMO = 'MINIMO',
  BAJO = 'BAJO',
  MEDIO = 'MEDIO',
  ALTO = 'ALTO',
}

export interface PolicyConfig {
  max_help_level: HelpLevel;
  block_complete_solutions: boolean;
  require_justification: boolean;
  allow_code_snippets: boolean;
  risk_thresholds: Record<string, number>;
}

export interface ActivityCreate {
  activity_id: string;
  title: string;
  instructions: string;
  teacher_id: string;
  policies: PolicyConfig;
  description?: string;
  evaluation_criteria?: string[];
  subject?: string;
  difficulty?: ActivityDifficulty;
  estimated_duration_minutes?: number;
  tags?: string[];
}

export interface ActivityUpdate {
  title?: string;
  description?: string;
  instructions?: string;
  policies?: PolicyConfig;
  evaluation_criteria?: string[];
  subject?: string;
  difficulty?: ActivityDifficulty;
  estimated_duration_minutes?: number;
  tags?: string[];
}

export interface ActivityResponse {
  id: string;
  activity_id: string;
  title: string;
  description: string | null;
  instructions: string;
  evaluation_criteria: string[];
  teacher_id: string;
  policies: PolicyConfig;
  subject: string | null;
  difficulty: string | null;
  estimated_duration_minutes: number | null;
  tags: string[];
  status: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}
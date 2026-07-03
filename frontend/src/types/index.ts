export interface ToolCall {
  id: string;
  session_id: string;
  tool_name: string;
  tool_arguments: Record<string, any>;
  execution_order: number;
  execution_time: number; // in seconds
  timestamp: string;
}

export interface Alert {
  id: string;
  session_id: string;
  score: number;
  reason: string;
  created_at: string;
}

export type SessionStatus = 'normal' | 'suspicious' | 'injected' | 'pending' | 'completed' | 'failed';

export interface Session {
  id: string;
  created_at: string;
  anomaly_score: number;
  status: string; // "normal", "suspicious", "injected", etc.
  prompt: string;
  tool_calls?: ToolCall[];
  alerts?: Alert[];
}

export interface Baseline {
  id: string;
  model_version: string;
  training_runs: number;
  threshold: number;
  created_at: string;
}

export interface BaselineFeatureVector {
  id: string;
  baseline_id: string;
  session_id: string | null;
  prompt: string;
  sequence: string[];
  tool_frequency: Record<string, number>;
  execution_order: string[];
  execution_count: number;
  average_execution_time: number;
  parameter_length: number;
  created_at: string;
}

export interface BaselineStatistics {
  total_runs: number;
  unique_tools_used: string[];
  tool_frequencies: Record<string, number>;
  avg_execution_count_per_run: number;
  max_execution_count_per_run: number;
  avg_execution_time: number;
  avg_parameter_length: number;
  sequences_frequency: Record<string, number>;
}

export interface BaselineTrainResponse {
  baseline_id: string;
  model_version: string;
  training_runs: number;
  threshold: number;
  created_at: string;
  statistics: BaselineStatistics;
  feature_vectors: BaselineFeatureVector[];
}

export interface SimulateResponse {
  session_id: string;
  attack_number: number;
  prompt: string;
  status: string;
  score: number;
  explanation: string;
  tool_sequence: string[];
}

export interface DetectResponse {
  score: number;
  status: string;
  reasons: string[];
}

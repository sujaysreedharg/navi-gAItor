export interface FlightSummary {
  total_duration_seconds: number;
  total_duration_minutes: number;
  max_altitude_ft?: number;
  min_altitude_ft?: number;
  avg_altitude_ft?: number;
  max_airspeed_kt?: number;
  avg_airspeed_kt?: number;
  max_climb_rate_fpm?: number;
  max_descent_rate_fpm?: number;
  max_bank_angle_deg?: number;
  max_positive_g?: number;
  max_negative_g?: number;
  fuel_consumed_gal?: number;
}

export interface FlightEvent {
  type: string;
  time_seconds: number;
  severity: 'info' | 'warning' | 'critical';
  description: string;
  [key: string]: any;
}

export interface RuleEvent {
  rule: string;
  severity: 'info' | 'warning' | 'critical';
  time_seconds: number;
  description: string;
  values: Record<string, number | string>;
}

export interface ReferenceSnippet {
  event_type: string;
  title: string;
  url: string;
  snippet: string;
  domain?: string;
}

export interface SeriesPoint {
  time_seconds: number;
  alt_msl_ft?: number;
  airspeed_indicated_kt?: number;
  vertical_speed_fpm?: number;
  roll_deg?: number;
  pitch_deg?: number;
}

export interface SignalMeta {
  key: string;
  label: string;
  unit: string;
  axis: 'left' | 'right' | 'band';
}

export interface SignalMatrixPoint {
  time_seconds: number;
  [key: string]: number | undefined;
}

export interface RiskPoint {
  time_seconds: number;
  hf_index: number;
}

export interface PresetWindow {
  id: string;
  label: string;
  window: [number, number];
}

export interface AnalysisResponse {
  success: boolean;
  filename: string;
  metadata?: Record<string, string>;
  summary: FlightSummary;
  events: FlightEvent[];
  events_count: {
    total: number;
    critical: number;
    warning: number;
    info: number;
  };
  references: ReferenceSnippet[];
  debrief: string;
  series_data: SeriesPoint[];
  signal_meta: SignalMeta[];
  signal_matrix: SignalMatrixPoint[];
  risk_trace: RiskPoint[];
  rule_events: RuleEvent[];
  presets: PresetWindow[];
}

export interface AiAgentRequest {
  command: string;
  window_start?: number;
  window_end?: number;
  summary: FlightSummary;
  rule_events: RuleEvent[];
  context_notes?: string;
}

export interface AiAgentResponse {
  log: string;
}

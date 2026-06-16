export type AnalysisStatus = "pending" | "running" | "completed" | "failed";

export type ModuleName =
  | "exif"
  | "face"
  | "geo"
  | "reverse_image"
  | "username"
  | "social"
  | "ip"
  | "email"
  | "phone"
  | "email_reg"
  | "breach"
  | "domain"
  | "paste"
  | "dork"
  | "dossier"
  | "enrich"
  | "llm"
  | "system";

export type ModuleStatus = "pending" | "running" | "completed" | "failed";

export interface Finding {
  id?: string;
  module: string;
  category: string;
  key: string;
  value: string | number | Record<string, unknown>;
  confidence?: number;
  source?: string;
  raw_data?: Record<string, unknown>;
  created_at?: string;
}

export interface Location {
  id: string;
  latitude: number;
  longitude: number;
  accuracy_meters?: number;
  source: string;
  timestamp?: string;
  address?: string;
  confidence?: number;
}

export interface Analysis {
  id: string;
  created_at: string;
  status: AnalysisStatus;
  target_name?: string;
  notes?: string;
  confidence_score: number;
  findings?: Finding[];
  locations?: Location[];
  targets?: Array<{
    id: string;
    data_type: string;
    value: string;
    file_path?: string;
  }>;
}

export interface AnalysisListItem {
  id: string;
  created_at: string;
  status: AnalysisStatus;
  target_name?: string;
  confidence_score: number;
}

export interface DashboardStats {
  total_analyses: number;
  this_month: number;
  avg_confidence: number;
}

export interface WSMessage {
  event: string;
  module?: string;
  status?: ModuleStatus;
  findings_count?: number;
  findings?: Finding[];
  error?: string;
  timestamp?: string;
  analysis_id?: string;
}

export interface ModuleState {
  name: ModuleName;
  label: string;
  status: ModuleStatus;
  findingsCount: number;
  error?: string;
}

export interface ProfileSummary {
  identity_summary?: string;
  estimated_location?: string;
  activity_pattern?: string;
  digital_footprint?: string;
  behavioral_insights?: string[];
  confidence_assessment?: {
    overall: number;
    location: number;
    identity: number;
    social: number;
  };
  key_findings?: string[];
  recommended_next_steps?: string[];
  risk_flags?: string[];
}

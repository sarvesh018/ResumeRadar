export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name: string | null;
  headline: string | null;
  location: string | null;
  years_experience: number | null;
  target_roles: string[] | null;
  target_locations: string[] | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
}

export interface Skill {
  skill_name: string;
  category: string | null;
  confidence: number;
}

export interface Resume {
  id: string;
  version_name: string;
  file_type: string;
  is_primary: boolean;
  created_at: string;
}

export interface ResumeDetail extends Resume {
  skill_count: number;
  text_length: number;
  skills: Skill[];
}

export interface MatchRequest {
  resume_id: string;
  jd_text: string;
  jd_company?: string;
  jd_role?: string;
}

export interface MatchResponse {
  id: string;
  resume_id: string;
  jd_company: string | null;
  jd_role: string | null;
  overall_score: number;
  keyword_score: number;
  semantic_score: number;
  taxonomy_score: number;
  matched_skills: SkillMatch[];
  missing_skills: MissingSkill[];
  suggestions: Suggestion[];
  resume_skill_count: number;
  jd_skill_count: number;
  created_at: string;
}

export interface SkillMatch {
  skill: string;
  match_type: string;
  confidence: number;
  found_in_resume: boolean;
  jd_required: boolean;
}

export interface MissingSkill {
  skill: string;
  category: string | null;
  importance: string;
  suggestion: string | null;
}

export interface Suggestion {
  section: string;
  action: string;
  text: string;
}

export interface Application {
  id: string;
  user_id: string;
  company: string;
  role_title: string;
  resume_id: string | null;
  match_result_id: string | null;
  status: string;
  applied_date: string;
  response_date: string | null;
  match_score: number | null;
  notes: string | null;
  allowed_transitions: string[];
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail extends Application {
  status_events: StatusEvent[];
}

export interface StatusEvent {
  id: string;
  from_status: string | null;
  to_status: string;
  notes: string | null;
  created_at: string;
}

export interface KanbanBoard {
  columns: KanbanColumn[];
  total: number;
}

export interface KanbanColumn {
  status: string;
  count: number;
  applications: Application[];
}

export interface DashboardSummary {
  total_applications: number;
  active_applications: number;
  response_rate: number;
  interview_rate: number;
  offer_rate: number;
  avg_match_score: number | null;
  most_applied_company: string | null;
  most_applied_role: string | null;
}

export interface FunnelResponse {
  stages: FunnelStage[];
  total_applications: number;
  overall_response_rate: number;
  interview_rate: number;
  offer_rate: number;
}

export interface FunnelStage {
  status: string;
  count: number;
  percentage: number;
}

export interface ResumeVersionStats {
  resume_id: string;
  total_sent: number;
  positive_responses: number;
  response_rate: number;
  avg_match_score: number | null;
}

export interface ResumeComparisonResponse {
  versions: ResumeVersionStats[];
  best_version: string | null;
  recommendation: string;
}

export interface ScoreBucket {
  range_label: string;
  min_score: number;
  max_score: number;
  total_applications: number;
  positive_responses: number;
  response_rate: number;
}

export interface ScoreCallbackResponse {
  buckets: ScoreBucket[];
  min_effective_score: number | null;
  sweet_spot: string;
}

export interface TrendPoint {
  period: string;
  applications: number;
  responses: number;
  response_rate: number;
}

export interface TrendResponse {
  period_type: string;
  data_points: TrendPoint[];
  total_periods: number;
}
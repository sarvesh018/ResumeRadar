export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface Profile {
  id: string
  user_id: string
  full_name: string | null
  headline: string | null
  location: string | null
  years_experience: number | null
  target_roles: string[] | null
  target_locations: string[] | null
  linkedin_url: string | null
  github_url: string | null
  portfolio_url: string | null
  technical_skills: string[]
  created_at: string
  updated_at: string
}

export interface Skill {
  skill_name: string
  category: string | null
  confidence: number
}

export interface Resume {
  id: string
  user_id: string
  version_name: string
  file_type: string
  is_primary: boolean
  created_at: string
  updated_at: string
}

export interface ResumeDetail extends Resume {
  skill_count: number
  text_length: number
  skills: Skill[]
}

export interface SkillMatchDetail {
  skill: string
  match_type: string
  confidence: number
  found_in_resume: boolean
  jd_required: boolean
}

export interface MissingSkill {
  skill: string
  category: string | null
  importance: string
  suggestion: string | null
}

export interface Suggestion {
  section: string
  action: string
  text: string
}

export interface MatchResult {
  id: string
  resume_id: string
  jd_company: string | null
  jd_role: string | null
  overall_score: number
  keyword_score: number
  semantic_score: number
  taxonomy_score: number
  matched_skills: SkillMatchDetail[]
  missing_skills: MissingSkill[]
  suggestions: Suggestion[]
  resume_skill_count: number
  jd_skill_count: number
  created_at: string
}

export type ApplicationStatus =
  | 'wishlist' | 'applied' | 'screening'
  | 'interviewing' | 'offer' | 'rejected' | 'withdrawn'

export interface Application {
  id: string
  user_id: string
  company: string
  role_title: string
  resume_id: string | null
  match_result_id: string | null
  jd_url: string | null
  salary_min: number | null
  salary_max: number | null
  location: string | null
  is_remote: boolean
  status: ApplicationStatus
  applied_date: string
  response_date: string | null
  match_score: number | null
  notes: string | null
  allowed_transitions: string[]
  created_at: string
  updated_at: string
}

export interface KanbanColumn {
  status: string
  count: number
  applications: Application[]
}

export interface KanbanBoard {
  columns: KanbanColumn[]
  total: number
}

export interface DashboardSummary {
  total_applications: number
  active_applications: number
  response_rate: number
  interview_rate: number
  offer_rate: number
  avg_match_score: number | null
  most_applied_company: string | null
  most_applied_role: string | null
}

export interface FunnelResponse {
  stages: { status: string; count: number; percentage: number }[]
  total_applications: number
  overall_response_rate: number
  interview_rate: number
  offer_rate: number
}
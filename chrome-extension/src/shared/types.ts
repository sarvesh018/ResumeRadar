export interface ExtractedJobData {
  company: string
  role_title: string
  jd_text: string
  jd_url: string
  location?: string
  is_remote?: boolean
  salary_min?: number
  salary_max?: number
  source: 'naukri' | 'linkedin'
  extracted_at: string
}

export interface AuthData {
  access_token: string
  refresh_token: string
  user: {
    id: string
    email: string
    full_name: string | null
  }
}

export interface AppSettings {
  backend_url: string
  enable_auto_capture: boolean
}

export interface Resume {
  id: string
  version_name: string
  is_primary: boolean
  created_at: string
}

export interface MatchResult {
  id: string
  overall_score: number
  keyword_score: number
  semantic_score: number
  taxonomy_score: number
  matched_skills: Array<{
    skill: string
    match_type: string
    confidence: number
    found_in_resume: boolean
    jd_required: boolean
  }>
  missing_skills: Array<{
    skill: string
    category: string | null
    importance: string
    suggestion: string | null
  }>
  suggestions: Array<{
    section: string
    action: string
    text: string
  }>
}

export type ExtensionMessage =
  | { type: 'JOB_DETECTED'; data: ExtractedJobData }
  | { type: 'GET_LATEST_JOB' }
  | { type: 'CLEAR_LATEST_JOB' }
  | { type: 'OPEN_POPUP' }
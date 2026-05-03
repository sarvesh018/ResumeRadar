CREATE SCHEMA IF NOT EXISTS auth_db;
CREATE SCHEMA IF NOT EXISTS profile_db;
CREATE SCHEMA IF NOT EXISTS matcher_db;
CREATE SCHEMA IF NOT EXISTS tracker_db;
CREATE SCHEMA IF NOT EXISTS analytics_db;

-- AUTH
CREATE TABLE IF NOT EXISTS auth_db.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email ON auth_db.users(email);

-- PROFILES
CREATE TABLE IF NOT EXISTS profile_db.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,
    full_name VARCHAR(255),
    headline VARCHAR(500),
    location VARCHAR(255),
    years_experience SMALLINT,
    target_roles JSONB,
    target_locations JSONB,
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS profile_db.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    version_name VARCHAR(100) NOT NULL,
    file_url VARCHAR(1000) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    raw_text TEXT,
    parsed_data JSONB,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_resumes_user ON profile_db.resumes(user_id);

CREATE TABLE IF NOT EXISTS profile_db.resume_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES profile_db.resumes(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    confidence REAL DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_resume_skills_resume ON profile_db.resume_skills(resume_id);

-- MATCHER
CREATE TABLE IF NOT EXISTS matcher_db.match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    resume_id UUID NOT NULL,
    jd_text TEXT NOT NULL,
    jd_company VARCHAR(255),
    jd_role VARCHAR(255),
    keyword_score REAL NOT NULL,
    semantic_score REAL NOT NULL,
    taxonomy_score REAL NOT NULL,
    overall_score REAL NOT NULL,
    matched_skills JSONB NOT NULL DEFAULT '[]',
    missing_skills JSONB NOT NULL DEFAULT '[]',
    suggestions JSONB,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_match_user ON matcher_db.match_results(user_id);

-- TRACKER
CREATE TABLE IF NOT EXISTS tracker_db.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    resume_id UUID,
    match_result_id UUID,
    company VARCHAR(255) NOT NULL,
    role_title VARCHAR(255) NOT NULL,
    jd_url VARCHAR(1000),
    salary_min INTEGER,
    salary_max INTEGER,
    location VARCHAR(255),
    is_remote BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'applied',
    applied_date DATE NOT NULL,
    response_date DATE,
    match_score REAL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_apps_user ON tracker_db.applications(user_id);
CREATE INDEX IF NOT EXISTS idx_apps_status ON tracker_db.applications(status);

CREATE TABLE IF NOT EXISTS tracker_db.status_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES tracker_db.applications(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_app ON tracker_db.status_events(application_id);
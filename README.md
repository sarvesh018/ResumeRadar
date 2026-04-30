# ResumeRadar — Complete Application Architecture

## 1. Monorepo structure

```
resumeradar/
├── .github/
│   ├── workflows/
│   │   ├── ci-backend.yml          # Lint, test, build, push for all Python services
│   │   ├── ci-frontend.yml         # Lint, test, build, push React app
│   │   ├── deploy-staging.yml      # Helm upgrade to staging
│   │   ├── deploy-prod.yml         # Helm upgrade to prod (manual approval)
│   │   └── security-scan.yml       # Trivy + Checkov nightly
│   └── CODEOWNERS
│
├── packages/                        # ── SHARED LIBRARIES ──
│   ├── common-py/                   # Python shared lib (pip installable)
│   │   ├── pyproject.toml
│   │   └── resumeradar_common/
│   │       ├── __init__.py
│   │       ├── auth/
│   │       │   ├── jwt_handler.py   # JWT decode/verify (shared across all services)
│   │       │   └── dependencies.py  # FastAPI Depends(get_current_user)
│   │       ├── config/
│   │       │   ├── settings.py      # Pydantic BaseSettings (env-driven config)
│   │       │   └── constants.py     # App-wide constants
│   │       ├── database/
│   │       │   ├── session.py       # SQLAlchemy async session factory
│   │       │   ├── base_model.py    # Shared base (id, created_at, updated_at)
│   │       │   └── health.py        # DB health check endpoint
│   │       ├── events/
│   │       │   ├── publisher.py     # Redis pub/sub publisher
│   │       │   ├── subscriber.py    # Redis pub/sub consumer base class
│   │       │   └── schemas.py       # Event envelope schema (Pydantic)
│   │       ├── middleware/
│   │       │   ├── correlation_id.py  # X-Correlation-ID propagation
│   │       │   ├── request_logger.py  # Structured JSON request logging
│   │       │   └── error_handler.py   # Global exception → JSON response
│   │       ├── observability/
│   │       │   ├── metrics.py       # Prometheus metric registration
│   │       │   ├── logging.py       # structlog JSON config
│   │       │   └── tracing.py       # OpenTelemetry setup (optional)
│   │       ├── schemas/
│   │       │   ├── pagination.py    # PageRequest / PageResponse
│   │       │   ├── error.py         # ErrorResponse schema
│   │       │   └── health.py        # HealthCheck schema
│   │       └── utils/
│   │           ├── s3_client.py     # Boto3 S3 wrapper (upload, presigned URL)
│   │           └── redis_client.py  # Redis connection pool
│   │
│   └── common-ts/                   # TypeScript shared lib
│       ├── package.json
│       └── src/
│           ├── api-client.ts        # Typed Axios client (auto-generated from OpenAPI)
│           ├── types/               # Shared TypeScript types
│           │   ├── user.ts
│           │   ├── resume.ts
│           │   ├── application.ts
│           │   └── analytics.ts
│           └── utils/
│               ├── auth.ts          # Token storage, refresh logic
│               └── dates.ts         # Date formatting helpers
│
├── services/                        # ── MICROSERVICES ──
│   ├── auth-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic/                 # DB migrations (own schema)
│   │   │   ├── alembic.ini
│   │   │   └── versions/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # FastAPI app factory
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   └── v1/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── router.py
│   │   │   │       └── endpoints/
│   │   │   │           ├── register.py
│   │   │   │           ├── login.py
│   │   │   │           ├── refresh.py
│   │   │   │           └── me.py
│   │   │   ├── core/
│   │   │   │   ├── config.py        # Service-specific settings
│   │   │   │   └── security.py      # Password hashing (bcrypt)
│   │   │   ├── models/
│   │   │   │   └── user.py          # SQLAlchemy User model
│   │   │   ├── schemas/
│   │   │   │   ├── auth.py          # LoginRequest, TokenResponse
│   │   │   │   └── user.py          # UserCreate, UserResponse
│   │   │   ├── services/
│   │   │   │   └── auth_service.py  # Business logic layer
│   │   │   └── repositories/
│   │   │       └── user_repo.py     # Data access layer
│   │   └── tests/
│   │       ├── conftest.py          # Fixtures, test DB
│   │       ├── test_register.py
│   │       └── test_login.py
│   │
│   ├── profile-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/v1/endpoints/
│   │   │   │   ├── profile.py       # GET/PUT user profile
│   │   │   │   ├── resumes.py       # Upload, list, get, delete
│   │   │   │   └── skills.py        # Extracted skills endpoints
│   │   │   ├── models/
│   │   │   │   ├── profile.py       # UserProfile model
│   │   │   │   ├── resume.py        # Resume model
│   │   │   │   └── skill.py         # Skill model (normalized)
│   │   │   ├── services/
│   │   │   │   ├── profile_service.py
│   │   │   │   ├── resume_parser.py  # pdfplumber + python-docx extraction
│   │   │   │   └── skill_extractor.py # spaCy NER + custom patterns
│   │   │   └── repositories/
│   │   │       ├── profile_repo.py
│   │   │       └── resume_repo.py
│   │   └── tests/
│   │
│   ├── matcher-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/v1/endpoints/
│   │   │   │   ├── match.py          # POST /match, GET /match/:id
│   │   │   │   └── history.py        # GET /match/history
│   │   │   ├── models/
│   │   │   │   ├── match_result.py
│   │   │   │   └── jd_parse.py
│   │   │   ├── services/
│   │   │   │   ├── matcher_service.py  # Orchestrator
│   │   │   │   ├── keyword_matcher.py  # Layer 1: fuzzy keyword
│   │   │   │   ├── semantic_matcher.py # Layer 2: embeddings
│   │   │   │   ├── taxonomy_matcher.py # Layer 3: skill groups
│   │   │   │   └── jd_parser.py        # Extract skills from JD text
│   │   │   ├── data/
│   │   │   │   └── skill_taxonomy.json # Hand-curated skill groups
│   │   │   └── repositories/
│   │   │       └── match_repo.py
│   │   └── tests/
│   │       ├── test_keyword_matcher.py
│   │       ├── test_semantic_matcher.py
│   │       └── test_integration.py
│   │
│   ├── tracker-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/v1/endpoints/
│   │   │   │   ├── applications.py    # Full CRUD
│   │   │   │   ├── status.py          # PATCH status transitions
│   │   │   │   └── board.py           # GET Kanban board view
│   │   │   ├── models/
│   │   │   │   ├── application.py
│   │   │   │   ├── status_event.py    # Audit trail of transitions
│   │   │   │   └── application_skill.py # Skills extracted from JD
│   │   │   ├── services/
│   │   │   │   ├── tracker_service.py
│   │   │   │   └── status_machine.py  # Valid transition enforcement
│   │   │   └── repositories/
│   │   │       └── application_repo.py
│   │   └── tests/
│   │
│   ├── analytics-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/v1/endpoints/
│   │   │   │   ├── skill_performance.py  # Response rate per skill
│   │   │   │   ├── resume_compare.py     # A/B test resume versions
│   │   │   │   ├── funnel.py             # Conversion funnel
│   │   │   │   └── trends.py             # Time-series metrics
│   │   │   ├── services/
│   │   │   │   ├── analytics_engine.py   # Core computation logic
│   │   │   │   └── aggregator.py         # Materialized view refresher
│   │   │   └── queries/
│   │   │       ├── skill_response_rate.sql
│   │   │       ├── resume_ab_test.sql
│   │   │       └── funnel_conversion.sql
│   │   └── tests/
│   │
│   └── notification-service/
│       ├── Dockerfile
│       ├── pyproject.toml
│       ├── app/
│       │   ├── main.py
│       │   ├── consumers/
│       │   │   ├── application_events.py  # Listen: app.status.changed
│       │   │   └── reminder_events.py     # Listen: reminder.due
│       │   ├── services/
│       │   │   ├── email_sender.py        # Resend API integration
│       │   │   └── template_engine.py     # Jinja2 email templates
│       │   ├── templates/
│       │   │   ├── welcome.html
│       │   │   ├── follow_up_reminder.html
│       │   │   └── weekly_digest.html
│       │   └── models/
│       │       ├── notification_log.py
│       │       └── preference.py
│       └── tests/
│
├── frontend/                        # ── REACT APPLICATION ──
│   ├── Dockerfile
│   ├── nginx.conf                   # SPA routing + /api proxy
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── routes/
│       │   ├── index.tsx            # Route definitions
│       │   ├── ProtectedRoute.tsx   # Auth guard
│       │   └── pages/
│       │       ├── Landing.tsx
│       │       ├── Login.tsx
│       │       ├── Register.tsx
│       │       ├── Dashboard.tsx
│       │       ├── ResumeUpload.tsx
│       │       ├── MatchAnalysis.tsx
│       │       ├── ApplicationBoard.tsx
│       │       ├── Analytics.tsx
│       │       ├── Profile.tsx
│       │       └── Settings.tsx
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Navbar.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── Footer.tsx
│       │   ├── resume/
│       │   │   ├── ResumeCard.tsx
│       │   │   ├── ResumeDropzone.tsx
│       │   │   ├── SkillBadge.tsx
│       │   │   └── VersionSelector.tsx
│       │   ├── matcher/
│       │   │   ├── JDInput.tsx
│       │   │   ├── MatchScoreRing.tsx
│       │   │   ├── GapAnalysis.tsx
│       │   │   └── Suggestions.tsx
│       │   ├── tracker/
│       │   │   ├── KanbanBoard.tsx
│       │   │   ├── KanbanColumn.tsx
│       │   │   ├── ApplicationCard.tsx
│       │   │   └── AddApplicationModal.tsx
│       │   ├── analytics/
│       │   │   ├── SkillChart.tsx
│       │   │   ├── FunnelChart.tsx
│       │   │   ├── ResumeComparison.tsx
│       │   │   └── TrendLine.tsx
│       │   └── shared/
│       │       ├── Button.tsx
│       │       ├── Input.tsx
│       │       ├── Modal.tsx
│       │       ├── Toast.tsx
│       │       ├── Spinner.tsx
│       │       └── EmptyState.tsx
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useResumes.ts
│       │   ├── useApplications.ts
│       │   ├── useMatch.ts
│       │   └── useAnalytics.ts
│       ├── stores/
│       │   ├── authStore.ts         # Zustand store
│       │   ├── boardStore.ts
│       │   └── uiStore.ts
│       ├── lib/
│       │   ├── api.ts               # Axios instance + interceptors
│       │   ├── queryClient.ts       # React Query config
│       │   └── constants.ts
│       └── types/
│           └── index.ts             # Mirrors common-ts types
│
├── helm/                            # ── KUBERNETES DEPLOYMENT ──
│   └── resumeradar/
│       ├── Chart.yaml               # Umbrella chart
│       ├── values.yaml              # Default (dev) values
│       ├── values-staging.yaml
│       ├── values-prod.yaml
│       ├── charts/
│       │   ├── auth-service/
│       │   │   ├── Chart.yaml
│       │   │   ├── values.yaml
│       │   │   └── templates/
│       │   │       ├── deployment.yaml
│       │   │       ├── service.yaml
│       │   │       ├── configmap.yaml
│       │   │       ├── hpa.yaml
│       │   │       ├── networkpolicy.yaml
│       │   │       └── _helpers.tpl
│       │   ├── profile-service/
│       │   ├── matcher-service/
│       │   ├── tracker-service/
│       │   ├── analytics-service/
│       │   ├── notification-service/
│       │   └── frontend/
│       └── templates/
│           ├── namespace.yaml
│           ├── sealed-secrets.yaml
│           └── _helpers.tpl
│
├── infra/                           # ── TERRAFORM ──
│   ├── modules/
│   │   ├── vpc/
│   │   ├── ec2/
│   │   ├── rds/
│   │   ├── elasticache/
│   │   ├── s3/
│   │   ├── iam/
│   │   └── alb/
│   ├── environments/
│   │   ├── staging/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── terraform.tfvars
│   │   └── prod/
│   └── backend.tf                   # S3 state backend
│
├── scripts/                         # ── UTILITY SCRIPTS ──
│   ├── setup-local.sh               # One-command local dev setup
│   ├── seed-data.py                 # Seed DB with test data
│   ├── generate-api-client.sh       # OpenAPI → TypeScript client
│   └── db-backup.sh                 # Manual RDS backup to S3
│
├── docker-compose.yml               # Local development stack
├── docker-compose.override.yml      # Local dev volume mounts + hot reload
├── Makefile                         # Common commands
├── .env.example
├── .pre-commit-config.yaml
└── README.md
```


## 2. Database schema (PostgreSQL — logical schemas per service)

```sql
-- ============================================================
-- SCHEMA: auth_db (owned by auth-service)
-- ============================================================
CREATE SCHEMA auth_db;

CREATE TABLE auth_db.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    is_active       BOOLEAN DEFAULT true,
    is_verified     BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE auth_db.refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth_db.users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked         BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_refresh_tokens_user ON auth_db.refresh_tokens(user_id);
CREATE INDEX idx_users_email ON auth_db.users(email);


-- ============================================================
-- SCHEMA: profile_db (owned by profile-service)
-- ============================================================
CREATE SCHEMA profile_db;

CREATE TABLE profile_db.profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE NOT NULL,  -- FK enforced at app level (cross-schema)
    full_name       VARCHAR(255),
    headline        VARCHAR(500),
    location        VARCHAR(255),
    years_experience SMALLINT,
    target_roles    TEXT[],                -- ["DevOps Engineer", "SRE", "Platform Engineer"]
    target_locations TEXT[],
    linkedin_url    VARCHAR(500),
    github_url      VARCHAR(500),
    preferences     JSONB DEFAULT '{}',    -- notification prefs, UI settings
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE profile_db.resumes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    version_name    VARCHAR(100) NOT NULL,  -- "DevOps-focused v2"
    file_url        VARCHAR(1000) NOT NULL, -- S3 pre-signed URL path
    file_type       VARCHAR(10) NOT NULL,   -- "pdf" | "docx"
    raw_text        TEXT,                   -- Extracted full text
    parsed_data     JSONB,                  -- Structured: {summary, experience[], education[]}
    is_primary      BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE profile_db.resume_skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id       UUID REFERENCES profile_db.resumes(id) ON DELETE CASCADE,
    skill_name      VARCHAR(100) NOT NULL,   -- Normalized: "kubernetes" not "K8s"
    category        VARCHAR(50),             -- "container_orchestration", "ci_cd", "cloud"
    confidence      REAL DEFAULT 1.0,        -- NLP extraction confidence 0-1
    years_mentioned SMALLINT,                -- Parsed from context if available
    UNIQUE(resume_id, skill_name)
);

CREATE INDEX idx_resumes_user ON profile_db.resumes(user_id);
CREATE INDEX idx_resume_skills_resume ON profile_db.resume_skills(resume_id);
CREATE INDEX idx_resume_skills_name ON profile_db.resume_skills(skill_name);


-- ============================================================
-- SCHEMA: matcher_db (owned by matcher-service)
-- ============================================================
CREATE SCHEMA matcher_db;

CREATE TABLE matcher_db.match_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    resume_id       UUID NOT NULL,
    jd_text         TEXT NOT NULL,
    jd_company      VARCHAR(255),
    jd_role         VARCHAR(255),

    -- Scores (0.0 - 1.0)
    keyword_score   REAL NOT NULL,
    semantic_score  REAL NOT NULL,
    taxonomy_score  REAL NOT NULL,
    overall_score   REAL NOT NULL,           -- Weighted blend

    -- Detailed results
    matched_skills  JSONB NOT NULL,          -- [{skill, source, match_type}]
    missing_skills  JSONB NOT NULL,          -- [{skill, importance, suggestion}]
    suggestions     JSONB,                   -- [{section, action, reason}]

    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE matcher_db.jd_skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_result_id UUID REFERENCES matcher_db.match_results(id) ON DELETE CASCADE,
    skill_name      VARCHAR(100) NOT NULL,
    is_required     BOOLEAN DEFAULT true,     -- Required vs nice-to-have
    is_matched      BOOLEAN DEFAULT false
);

CREATE INDEX idx_match_results_user ON matcher_db.match_results(user_id);
CREATE INDEX idx_match_results_resume ON matcher_db.match_results(resume_id);
CREATE INDEX idx_match_results_score ON matcher_db.match_results(overall_score);


-- ============================================================
-- SCHEMA: tracker_db (owned by tracker-service)
-- ============================================================
CREATE SCHEMA tracker_db;

CREATE TYPE tracker_db.application_status AS ENUM (
    'wishlist', 'applied', 'screening', 'interviewing', 'offer', 'rejected', 'withdrawn'
);

CREATE TABLE tracker_db.applications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    resume_id       UUID,                     -- Which resume version was used
    match_result_id UUID,                     -- Link to match score at time of apply

    -- Job details
    company         VARCHAR(255) NOT NULL,
    role_title      VARCHAR(255) NOT NULL,
    jd_url          VARCHAR(1000),
    salary_min      INTEGER,
    salary_max      INTEGER,
    location        VARCHAR(255),
    is_remote       BOOLEAN DEFAULT false,

    -- Status
    status          tracker_db.application_status DEFAULT 'applied',
    applied_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    response_date   DATE,
    match_score     REAL,                     -- Snapshot at application time
    notes           TEXT,

    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tracker_db.status_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID REFERENCES tracker_db.applications(id) ON DELETE CASCADE,
    from_status     tracker_db.application_status,
    to_status       tracker_db.application_status NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tracker_db.application_skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID REFERENCES tracker_db.applications(id) ON DELETE CASCADE,
    skill_name      VARCHAR(100) NOT NULL,
    is_matched      BOOLEAN DEFAULT false,    -- Was this skill on the resume?
    UNIQUE(application_id, skill_name)
);

CREATE INDEX idx_applications_user ON tracker_db.applications(user_id);
CREATE INDEX idx_applications_status ON tracker_db.applications(status);
CREATE INDEX idx_applications_company ON tracker_db.applications(company);
CREATE INDEX idx_status_events_app ON tracker_db.status_events(application_id);
CREATE INDEX idx_app_skills_app ON tracker_db.application_skills(application_id);
CREATE INDEX idx_app_skills_name ON tracker_db.application_skills(skill_name);


-- ============================================================
-- SCHEMA: analytics_db (owned by analytics-service, READ access to tracker_db)
-- ============================================================
CREATE SCHEMA analytics_db;

-- Materialized views refreshed by cron (every 15 min)
CREATE MATERIALIZED VIEW analytics_db.skill_response_rates AS
SELECT
    a.user_id,
    aps.skill_name,
    COUNT(*) AS total_applications,
    COUNT(*) FILTER (WHERE a.status IN ('screening','interviewing','offer')) AS positive_responses,
    ROUND(
        COUNT(*) FILTER (WHERE a.status IN ('screening','interviewing','offer'))::NUMERIC
        / NULLIF(COUNT(*), 0), 3
    ) AS response_rate
FROM tracker_db.applications a
JOIN tracker_db.application_skills aps ON aps.application_id = a.id
WHERE a.status != 'wishlist'
GROUP BY a.user_id, aps.skill_name;

CREATE MATERIALIZED VIEW analytics_db.resume_version_performance AS
SELECT
    a.user_id,
    a.resume_id,
    COUNT(*) AS total_sent,
    COUNT(*) FILTER (WHERE a.status IN ('screening','interviewing','offer')) AS callbacks,
    ROUND(
        COUNT(*) FILTER (WHERE a.status IN ('screening','interviewing','offer'))::NUMERIC
        / NULLIF(COUNT(*), 0), 3
    ) AS callback_rate,
    ROUND(AVG(a.match_score)::NUMERIC, 2) AS avg_match_score
FROM tracker_db.applications a
WHERE a.resume_id IS NOT NULL AND a.status != 'wishlist'
GROUP BY a.user_id, a.resume_id;

CREATE MATERIALIZED VIEW analytics_db.funnel_metrics AS
SELECT
    a.user_id,
    a.status,
    COUNT(*) AS count,
    ROUND(AVG(a.match_score)::NUMERIC, 2) AS avg_match_score,
    ROUND(AVG(
        EXTRACT(EPOCH FROM (a.response_date - a.applied_date)) / 86400
    )::NUMERIC, 1) AS avg_days_to_response
FROM tracker_db.applications a
WHERE a.status != 'wishlist'
GROUP BY a.user_id, a.status;

CREATE UNIQUE INDEX ON analytics_db.skill_response_rates (user_id, skill_name);
CREATE UNIQUE INDEX ON analytics_db.resume_version_performance (user_id, resume_id);
CREATE UNIQUE INDEX ON analytics_db.funnel_metrics (user_id, status);
```


## 3. API contracts (OpenAPI-style summary)

### auth-service (port 8001)

| Method | Endpoint             | Request Body                              | Response                    | Auth   |
|--------|----------------------|-------------------------------------------|-----------------------------|--------|
| POST   | /api/v1/auth/register | `{email, password, full_name}`           | `{user_id, email}`          | None   |
| POST   | /api/v1/auth/login    | `{email, password}`                      | `{access_token, refresh_token, expires_in}` | None |
| POST   | /api/v1/auth/refresh  | `{refresh_token}`                        | `{access_token, refresh_token}` | None |
| GET    | /api/v1/auth/me       | —                                        | `{user_id, email, is_verified}` | JWT  |

### profile-service (port 8002)

| Method | Endpoint                       | Request Body                                 | Response                     | Auth |
|--------|--------------------------------|----------------------------------------------|------------------------------|------|
| GET    | /api/v1/profile                | —                                            | `{profile}`                  | JWT  |
| PUT    | /api/v1/profile                | `{full_name, headline, target_roles[], ...}` | `{profile}`                  | JWT  |
| POST   | /api/v1/resumes/upload         | `multipart: file + version_name`             | `{resume_id, parsed_skills}` | JWT  |
| GET    | /api/v1/resumes                | query: `?page=1&limit=10`                    | `{resumes[], total}`         | JWT  |
| GET    | /api/v1/resumes/:id            | —                                            | `{resume + skills}`          | JWT  |
| DELETE | /api/v1/resumes/:id            | —                                            | `204`                        | JWT  |
| GET    | /api/v1/resumes/:id/skills     | —                                            | `{skills[]}`                 | JWT  |

### matcher-service (port 8003)

| Method | Endpoint                       | Request Body                                   | Response                        | Auth |
|--------|--------------------------------|------------------------------------------------|---------------------------------|------|
| POST   | /api/v1/match                  | `{resume_id, jd_text, jd_company?, jd_role?}`  | `{match_result}`                | JWT  |
| GET    | /api/v1/match/:id              | —                                              | `{match_result + details}`      | JWT  |
| GET    | /api/v1/match/history          | query: `?resume_id=&page=1`                    | `{results[], total}`            | JWT  |

### tracker-service (port 8004)

| Method | Endpoint                               | Request Body                                        | Response               | Auth |
|--------|----------------------------------------|-----------------------------------------------------|------------------------|------|
| POST   | /api/v1/applications                   | `{company, role, resume_id, match_result_id, ...}`  | `{application}`        | JWT  |
| GET    | /api/v1/applications                   | query: `?status=applied&page=1`                     | `{applications[]}`     | JWT  |
| GET    | /api/v1/applications/board             | —                                                   | `{columns: {status: apps[]}}` | JWT |
| GET    | /api/v1/applications/:id               | —                                                   | `{application + events}` | JWT |
| PUT    | /api/v1/applications/:id               | `{company?, role?, notes?, ...}`                    | `{application}`        | JWT  |
| PATCH  | /api/v1/applications/:id/status        | `{status, notes?}`                                  | `{application}`        | JWT  |
| DELETE | /api/v1/applications/:id               | —                                                   | `204`                  | JWT  |

### analytics-service (port 8005)

| Method | Endpoint                              | Query Params                          | Response                          | Auth |
|--------|---------------------------------------|---------------------------------------|-----------------------------------|------|
| GET    | /api/v1/analytics/skills/performance  | `?min_applications=5`                 | `{skills: [{name, rate, count}]}` | JWT  |
| GET    | /api/v1/analytics/resumes/compare     | —                                     | `{versions: [{id, name, rate}]}`  | JWT  |
| GET    | /api/v1/analytics/funnel              | `?date_from=&date_to=`               | `{stages: [{status, count, avg}]}` | JWT |
| GET    | /api/v1/analytics/trends              | `?metric=applications&period=weekly`  | `{datapoints: [{date, value}]}`   | JWT  |
| GET    | /api/v1/analytics/score-vs-callback   | —                                     | `{buckets: [{range, count, rate}]}` | JWT |


## 4. Inter-service communication

### Synchronous (REST)
Service-to-service calls go through internal K8s DNS:
- `http://auth-service.resumeradar-app.svc.cluster.local:8001`
- Matcher calls Profile service to get resume skills for a match request
- Analytics reads from Tracker's database via read-only DB user

### Asynchronous (Redis Pub/Sub channels)

| Channel                    | Publisher         | Consumers                    | Payload                                    |
|----------------------------|-------------------|------------------------------|--------------------------------------------|
| `user.registered`          | auth-service      | profile-service, notification | `{user_id, email}`                        |
| `resume.parsed`            | profile-service   | notification                  | `{user_id, resume_id, skill_count}`       |
| `match.completed`          | matcher-service   | notification                  | `{user_id, match_id, score}`              |
| `application.created`      | tracker-service   | analytics, notification       | `{user_id, app_id, skills[]}`             |
| `application.status_changed` | tracker-service | analytics, notification       | `{user_id, app_id, from, to, timestamp}` |
| `analytics.refresh`        | cron (Lambda)     | analytics-service             | `{trigger: "scheduled"}`                  |


## 5. Shared library design patterns

### Every service's main.py follows the same factory pattern:

```python
# services/auth-service/app/main.py
from fastapi import FastAPI
from resumeradar_common.middleware.correlation_id import CorrelationIdMiddleware
from resumeradar_common.middleware.request_logger import RequestLoggerMiddleware
from resumeradar_common.middleware.error_handler import register_error_handlers
from resumeradar_common.observability.metrics import setup_prometheus
from resumeradar_common.observability.logging import setup_logging
from resumeradar_common.database.health import health_router
from app.api.v1.router import router as v1_router
from app.core.config import settings

def create_app() -> FastAPI:
    setup_logging(service_name="auth-service")

    app = FastAPI(
        title="ResumeRadar Auth Service",
        version="1.0.0",
        docs_url="/api/v1/auth/docs",
        openapi_url="/api/v1/auth/openapi.json",
    )

    # Middleware (order matters — outermost first)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggerMiddleware)

    # Error handlers
    register_error_handlers(app)

    # Prometheus metrics
    setup_prometheus(app, service_name="auth-service")

    # Routes
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(v1_router, prefix="/api/v1/auth", tags=["auth"])

    return app

app = create_app()
```

### Every service uses the same layered architecture:

```
Endpoint (thin HTTP layer)
    ↓ Pydantic schema validation
Service (business logic, orchestration)
    ↓ domain objects
Repository (data access, SQL queries)
    ↓ SQLAlchemy models
Database
```

### Every service's Dockerfile follows the same multi-stage pattern:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
COPY packages/common-py/ /build/common-py/
COPY services/auth-service/pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install ./common-py .

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
RUN useradd -r -s /bin/false appuser
COPY --from=builder /install /usr/local
COPY services/auth-service/app /app/app
WORKDIR /app
USER appuser
EXPOSE 8001
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8001/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```


## 6. Docker Compose for local development

```yaml
# docker-compose.yml
version: "3.9"

x-service-defaults: &service-defaults
  restart: unless-stopped
  networks: [resumeradar]
  env_file: .env

services:
  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: resumeradar
      POSTGRES_USER: rr_admin
      POSTGRES_PASSWORD: localdev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-schemas.sql:/docker-entrypoint-initdb.d/01-schemas.sql
    networks: [resumeradar]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rr_admin"]
      interval: 5s

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    networks: [resumeradar]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  auth-service:
    <<: *service-defaults
    build:
      context: .
      dockerfile: services/auth-service/Dockerfile
    ports: ["8001:8001"]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql+asyncpg://rr_admin:localdev@postgres:5432/resumeradar
      REDIS_URL: redis://redis:6379/0
      DB_SCHEMA: auth_db
      JWT_SECRET: local-dev-secret-change-in-prod

  profile-service:
    <<: *service-defaults
    build:
      context: .
      dockerfile: services/profile-service/Dockerfile
    ports: ["8002:8002"]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql+asyncpg://rr_admin:localdev@postgres:5432/resumeradar
      DB_SCHEMA: profile_db
      AWS_S3_BUCKET: resumeradar-resumes-dev
      AWS_REGION: ap-south-1

  matcher-service:
    <<: *service-defaults
    build:
      context: .
      dockerfile: services/matcher-service/Dockerfile
    ports: ["8003:8003"]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql+asyncpg://rr_admin:localdev@postgres:5432/resumeradar
      DB_SCHEMA: matcher_db
      EMBEDDING_MODEL: all-MiniLM-L6-v2
      PROFILE_SERVICE_URL: http://profile-service:8002

  tracker-service:
    <<: *service-defaults
    build:
      context: .
      dockerfile: services/tracker-service/Dockerfile
    ports: ["8004:8004"]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql+asyncpg://rr_admin:localdev@postgres:5432/resumeradar
      DB_SCHEMA: tracker_db

  analytics-service:
    <<: *service-defaults
    build:
      context: .
      dockerfile: services/analytics-service/Dockerfile
    ports: ["8005:8005"]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql+asyncpg://rr_admin:localdev@postgres:5432/resumeradar
      DB_SCHEMA: analytics_db

  notification-service:
    <<: *service-defaults
    build:
      context: .
      dockerfile: services/notification-service/Dockerfile
    ports: ["8006:8006"]
    depends_on:
      redis: { condition: service_healthy }
    environment:
      REDIS_URL: redis://redis:6379/0
      RESEND_API_KEY: re_test_local

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
      target: dev
    ports: ["3000:3000"]
    volumes:
      - ./frontend/src:/app/src    # Hot reload
    networks: [resumeradar]
    environment:
      VITE_API_BASE_URL: http://localhost:8080

  nginx-gateway:
    image: nginx:alpine
    ports: ["8080:80"]
    volumes:
      - ./nginx-dev.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - auth-service
      - profile-service
      - matcher-service
      - tracker-service
      - analytics-service
      - frontend
    networks: [resumeradar]

volumes:
  pgdata:

networks:
  resumeradar:
    driver: bridge
```


## 7. Helm chart template example (auth-service)

```yaml
# helm/resumeradar/charts/auth-service/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "auth-service.fullname" . }}
  labels:
    {{- include "auth-service.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "auth-service.selectorLabels" . | nindent 6 }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        {{- include "auth-service.selectorLabels" . | nindent 8 }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{{ .Values.service.port }}"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: {{ include "auth-service.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.port }}
              protocol: TCP
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "auth-service.fullname" . }}-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "auth-service.fullname" . }}-secrets
                  key: redis-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "auth-service.fullname" . }}-secrets
                  key: jwt-secret
          envFrom:
            - configMapRef:
                name: {{ include "auth-service.fullname" . }}-config
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          readinessProbe:
            httpGet:
              path: /health
              port: {{ .Values.service.port }}
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: {{ .Values.service.port }}
            initialDelaySeconds: 15
            periodSeconds: 20
```


## 8. Industry standards followed

| Standard                  | Implementation                                              |
|---------------------------|-------------------------------------------------------------|
| 12-Factor App             | Env-driven config, stateless services, port binding, logs as streams |
| Database per Service      | Logical schemas with isolated access (single RDS, free tier) |
| API Versioning            | URI prefix `/api/v1/` on all endpoints                      |
| Structured Logging        | JSON logs with structlog, correlation IDs across services    |
| Health Checks             | `/health` (liveness) + `/ready` (readiness) on every service |
| Graceful Shutdown         | SIGTERM handling, drain connections before exit              |
| Circuit Breaker           | Tenacity retries + httpx timeout on inter-service calls     |
| Idempotency               | UUID-based dedup on POST endpoints via Idempotency-Key header |
| RBAC                      | JWT claims with user_id; service-level auth via NetworkPolicy |
| Immutable Infrastructure  | Docker images tagged with Git SHA, never `:latest` in prod  |
| GitOps                    | Helm values committed to repo, ArgoCD syncs cluster state   |
| Shift-Left Security       | Trivy in CI, Sealed Secrets in Git, Pod Security Standards   |
| Observability             | RED metrics (Rate, Errors, Duration) on every endpoint       |
| Schema Migrations         | Alembic per service, run as Helm pre-upgrade hooks           |
| API Documentation         | Auto-generated OpenAPI from FastAPI, available at /docs      |
| Contract Testing          | Pydantic schemas shared via common-py package                |
| Pagination                | Cursor-based for lists, standardized via common PageResponse |
| Error Format              | RFC 7807 Problem Details: `{type, title, status, detail}`    |
```


## 9. Technology decision matrix

| Decision                | Choice              | Why                                                         |
|-------------------------|---------------------|-------------------------------------------------------------|
| Language (backend)      | Python 3.11         | FastAPI ecosystem, spaCy/ML libs, team familiarity          |
| Framework               | FastAPI             | Async, auto OpenAPI, Pydantic validation, dependency injection |
| ORM                     | SQLAlchemy 2.0      | Async support, mature, migration tooling (Alembic)          |
| Language (frontend)     | TypeScript          | Type safety, better DX, catches bugs at build time          |
| UI Framework            | React 18 + Vite     | Ecosystem size, Recharts for analytics, dnd-kit for Kanban  |
| Styling                 | TailwindCSS         | Utility-first, no CSS-in-JS runtime cost, small bundle      |
| State Management        | Zustand + React Query | Zustand for UI state, React Query for server state + cache |
| NLP                     | spaCy (sm model)    | Fast, lightweight, good NER for skill extraction            |
| Embeddings              | sentence-transformers | all-MiniLM-L6-v2: 80MB, runs on CPU, good quality       |
| Fuzzy Matching          | RapidFuzz           | C++ backend, 10x faster than fuzzywuzzy                    |
| Database                | PostgreSQL 16       | JSONB for flexible data, mature, RDS free tier              |
| Cache / Queue           | Redis 7             | Pub/sub for events, caching for embeddings, ElastiCache free |
| File Storage            | AWS S3              | Pre-signed URLs, lifecycle policies, 5GB free               |
| Container Runtime       | Docker              | Industry standard, multi-stage builds                       |
| Orchestration           | K3s on EC2          | Certified K8s, lightweight (~300MB), perfect for free tier  |
| Package Manager (K8s)   | Helm 3              | Templating, dependency management, rollback support         |
| CI/CD                   | GitHub Actions      | Native Git integration, 2000 min/month free                 |
| IaC                     | Terraform           | AWS provider mature, state management, modular              |
| Monitoring              | Grafana Cloud       | Free tier generous, Prometheus + Loki + Alertmanager hosted |
| Error Tracking          | Sentry              | 5K events/month free, stack traces, release tracking        |
```

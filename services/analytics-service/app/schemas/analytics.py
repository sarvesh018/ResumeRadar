from pydantic import BaseModel


class FunnelStage(BaseModel):
    status: str
    count: int
    percentage: float


class FunnelResponse(BaseModel):
    stages: list[FunnelStage]
    total_applications: int
    overall_response_rate: float
    interview_rate: float
    offer_rate: float


class ResumeVersionStats(BaseModel):
    resume_id: str
    total_sent: int
    positive_responses: int
    response_rate: float
    avg_match_score: float | None


class ResumeComparisonResponse(BaseModel):
    versions: list[ResumeVersionStats]
    best_version: str | None
    recommendation: str


class ScoreBucket(BaseModel):
    range_label: str
    min_score: float
    max_score: float
    total_applications: int
    positive_responses: int
    response_rate: float


class ScoreCallbackResponse(BaseModel):
    buckets: list[ScoreBucket]
    min_effective_score: float | None
    sweet_spot: str


class TrendPoint(BaseModel):
    period: str
    applications: int
    responses: int
    response_rate: float


class TrendResponse(BaseModel):
    period_type: str
    data_points: list[TrendPoint]
    total_periods: int


class DashboardSummary(BaseModel):
    total_applications: int
    active_applications: int
    response_rate: float
    interview_rate: float
    offer_rate: float
    avg_match_score: float | None
    avg_days_to_response: float | None
    most_applied_company: str | None
    most_applied_role: str | None
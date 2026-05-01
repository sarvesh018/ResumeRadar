from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator


def setup_prometheus(app, service_name: str = "unknown"):
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/health/live", "/health/ready", "/metrics"],
        inprogress_name=f"{service_name}_inprogress_requests",
        inprogress_labels=True,
    ).instrument(app).expose(app, endpoint="/metrics")


match_score_histogram = Histogram(
    "resumeradar_match_score",
    "Distribution of resume-JD match scores",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

applications_created_total = Counter(
    "resumeradar_applications_created_total",
    "Total job applications logged",
    ["status"],
)

resume_parse_duration = Histogram(
    "resumeradar_resume_parse_duration_seconds",
    "Time to parse a resume file",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)
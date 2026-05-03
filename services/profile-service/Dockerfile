FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY packages/common-py/ /build/common-py/
RUN pip install --no-cache-dir /build/common-py/ \
    pdfplumber \
    python-docx \
    rapidfuzz \
    python-multipart && \
    python -m spacy download en_core_web_sm

FROM python:3.11-slim AS runtime
RUN useradd --create-home --shell /bin/bash appuser
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY services/profile-service/app /home/appuser/app
WORKDIR /home/appuser
USER appuser
EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8002/health/live || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2", "--log-level", "warning"]
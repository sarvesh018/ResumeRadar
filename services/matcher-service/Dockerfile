FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY packages/common-py/ /build/common-py/
RUN pip install --no-cache-dir /build/common-py/ \
    sentence-transformers \
    rapidfuzz \
    numpy && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

FROM python:3.11-slim AS runtime
RUN useradd --create-home --shell /bin/bash appuser
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /root/.cache /home/appuser/.cache
ENV PATH="/opt/venv/bin:$PATH"
COPY services/matcher-service/app /home/appuser/app
WORKDIR /home/appuser
RUN chown -R appuser:appuser /home/appuser/.cache
USER appuser
EXPOSE 8003
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8003/health/live || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "1", "--log-level", "warning"]
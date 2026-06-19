# ─────────────────────────────────────────────────────────────────────────────
# AutoMind AI — Backend Dockerfile (Production Grade)
# Multi-stage build: deps → runtime
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Dependencies ────────────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /build
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && apt-get purge -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: run as non-root
RUN groupadd -r automind && useradd -r -g automind -d /app automind

WORKDIR /app

# System deps for video processing + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
        imagemagick \
        ffmpeg \
        fonts-liberation \
        fonts-dejavu \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    # Allow ImageMagick to read text (required by MoviePy TextClip)
    && (sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@*"/g' /etc/ImageMagick-6/policy.xml 2>/dev/null || true)

# Copy installed Python packages from deps stage
COPY --from=deps /install /usr/local

# Copy application code
COPY --chown=automind:automind . .

# Env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Switch to non-root user
USER automind

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production: Uvicorn with workers (scaled by CPU count)
# Production: Run prestart (db init) then Uvicorn with workers
CMD ["sh", "-c", "python prestart.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop --http httptools --access-log --proxy-headers --forwarded-allow-ips '*'"]

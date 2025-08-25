FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Build deps only in builder stage (won't be present in final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

# Pre-build wheels for all dependencies (uses prebuilt wheels where available, e.g. psycopg2-binary)
RUN python -m pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels -r /app/requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install from prebuilt wheels; no compiler or APT in runtime
COPY requirements.txt /app/requirements.txt
COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip && \
    pip install --no-index --find-links=/wheels -r /app/requirements.txt && \
    rm -rf /wheels

# Copy application code
COPY . /app

# Non-root user
RUN useradd -m -u 10001 appuser && \
    chown -R appuser:appuser /app
USER 10001

EXPOSE 8000

CMD ["gunicorn", "Vigar.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-"]

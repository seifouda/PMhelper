# ── Stage 1: Build Angular frontend ──────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --ignore-scripts
COPY web/ .
RUN npx ng build --configuration=production

# ── Stage 2: Python runtime ─────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml setup.py ./
COPY src/pmhelper/__init__.py src/pmhelper/
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/

# Copy Angular build output into /app/static
COPY --from=frontend-build /web/dist/pmhelper-edu-web/browser ./static

# Create non-root user
RUN useradd -m -u 1000 pmhelper && \
    chown -R pmhelper:pmhelper /app && \
    mkdir -p /app/data && \
    chown -R pmhelper:pmhelper /app/data

USER pmhelper

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "pmhelper.server.main:app", "--host", "0.0.0.0", "--port", "8000"]

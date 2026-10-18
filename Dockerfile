# Stage 1: Build environment
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    UV_COMPILE_BYTE=1 \
    UV_LINK_MODE=copy 

RUN apt update && apt -y upgrade

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . ./

# Stage 2: Production image
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS runtime

ENV VENV_PATH=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /app

# Copy venv + src
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/ ./

RUN addgroup --system app && adduser --system --ingroup app --no-create-home --shell /usr/sbin/nologin app \
    && chown -R app:app /app \
    && chmod -R 750 /app \
    && find /app/.venv -name "__pycache__" -type d -exec rm -rf {} + \
    && find /app/.venv -name "*.pyc" -delete

# Drop to non-root user
# Use a non-root user
USER app

# Expose port (override with env when running)
ENV BOT_NAME=Victreebot \
    BOT_PERM=1506728470775 \
    BOT_INVITE_LINK=https://discord.com/api/oauth2/authorize?client_id=927259062586970195&permissions=1506728470775&scope=bot%20applications.commands \
    SUPPORT_SERVER_LINK=https://discord.gg/sVmMUXCYp2 \
    SUPPORT_SERVER_ID=953976913968390184 \
    SUPPORT_SERVER_BUG_CHANNEL=953976914194866231 \
    SUPPORT_SERVER_FEATURE_IMPROVEMENT_CHANNEL=953976914194866232 \
    SUPPORT_SERVER_FEATURE_REQUEST_CHANNEL=953976914194866233 \
    DB_HOST=85.215.200.41 \
    DB_PORT=5432 \
    DB_DATABASENAME=VictreebotTest \
    API_BEARER_GITHUB=ghp_XXX\
    API_RELEASE_URL_GITHUB=https://api.github.com/repos/l3keboy/Victreebot/releases/latest \
    TEST_BOT_INVITE_LINK=https://discord.com/api/oauth2/authorize?client_id=927259062586970195&permissions=1506728470775&scope=bot%20applications.commands \
    ENVIRONMENT=dev \
    SEQ_ENDPOINT_TRACES=http://localhost:9993/ingest/otlp/v1/traces \
    SEQ_ENDPOINT_LOGS=http://localhost:9993/ingest/otlp/v1/logs \
    SERVICE_NAME=Victreebot.core \
    LOG_LEVEL=info

# Start server (using uvicorn)
CMD ["uv", "run", "--no-sync", "python", "-OO", "__main__.py"]
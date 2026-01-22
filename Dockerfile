FROM python:3.12-slim

# 1. Create user with home directory first
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --home /home/appuser appuser && \
    mkdir -p /home/appuser && \
    chown appuser:appgroup /home/appuser

# 2. Set up app directory
RUN mkdir -p /app && \
    chown appuser:appgroup /app

WORKDIR /app

RUN apt-get update && apt-get install -y curl

# 3. Set environment variables
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV HOME=/home/appuser
ENV PYTHONPATH=/app/src
ENV UV_CACHE_DIR=/tmp/.cache/uv
ENV TMPDIR=/tmp

# 4. Copy files with correct ownership
COPY --chown=appuser:appgroup . .

# 5. Install uv as root
USER root
RUN pip install uv

# 6. Ensure cache directory exists
RUN mkdir -p ${UV_CACHE_DIR} && \
    chown appuser:appgroup ${UV_CACHE_DIR}

# 7. Switch to appuser and run uv sync
USER appuser
RUN uv sync --locked --no-install-project

# 8. Verify Python interpreter is accessible
RUN ${VIRTUAL_ENV}/bin/python3 --version

EXPOSE 8050 9050 5678

CMD ["python", "-m", "cwaf_external_mcp.server"]
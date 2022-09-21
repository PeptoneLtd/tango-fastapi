FROM python:3.9-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PYTHONPATH="/app" \
  OTEL_SERVICE_NAME="tango-fastapi" \
  HOST=0.0.0.0 \
  PORT=8000 \
  UVICORN_WORKER_COUNT=""


RUN useradd --create-home --home-dir /app app

WORKDIR /app
USER app

ENV PATH="/app/.local/bin:${PATH}"

COPY requirements.txt .
RUN pip install pip --upgrade && \
    pip install -r requirements.txt

COPY tango ./tango
COPY bin ./bin


ENTRYPOINT /app/tango/docker-entrypoint.sh


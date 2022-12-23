# tango-fastapi

Simple fastapi implementation of an API to compute aggregation of proeins given an amino acid sequence.

This leverages the TANGO predictor, which is only distributed as a binary. Most of the logic here is to wrap that binary
into an API.

## configuration

Configuration is performed via env variables:

- `HOST` bind address (defaults to `0.0.0.0`)
- `PORT` listen port (defualts to `8000`)
- `UVICORN_WORKER_COUNT` (defaults to `1`)
- `OTEL_EXPORTER_ZIPKIN_ENDPOINT` (and other opentelemetry env variables). If set, traces will be sent to that endpoint,
  leveraging automatic opentelemetry instrumentation through fastapi

## roadmap
- Currently, the API is public. We need to implement an authentication+authorization service, potentially as an external
  microservice using JWTs 
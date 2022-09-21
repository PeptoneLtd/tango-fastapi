#!/bin/bash

set -eu

cd /app/tango


opentelemetry-instrument \
  --metrics_exporter=none \
  --traces_exporter=jaeger_thrift python /app/tango/api.py

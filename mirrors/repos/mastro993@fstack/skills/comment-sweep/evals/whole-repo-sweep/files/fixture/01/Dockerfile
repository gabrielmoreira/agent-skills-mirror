# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the files
COPY pyproject.toml README.md alembic.ini ./
COPY wxdata ./wxdata
COPY vendor ./vendor
COPY migrations ./migrations

RUN pip install .
# RUN pip install ipython

RUN useradd --create-home --uid 10001 wx
USER wx

ENTRYPOINT ["wx"]
CMD ["--help"]

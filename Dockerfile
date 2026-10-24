# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim AS frontend-build
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM debian:bookworm-slim AS eda-tools
ARG OSSCAD_RELEASE=2026-09-04
ARG OSSCAD_ARCHIVE=20260904
ARG OSSCAD_SHA256=8fb2384c2f88126f8936fc8f680ed2ebdf0ce440a7457c8f5a21c5c6e3e2de44
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl --fail --location --retry 3 \
    "https://github.com/YosysHQ/oss-cad-suite-build/releases/download/${OSSCAD_RELEASE}/oss-cad-suite-linux-x64-${OSSCAD_ARCHIVE}.tgz" \
    --output /tmp/oss-cad-suite.tgz \
    && printf '%s  %s\n' "$OSSCAD_SHA256" /tmp/oss-cad-suite.tgz | sha256sum --check - \
    && mkdir /opt/eda \
    && tar -xzf /tmp/oss-cad-suite.tgz -C /opt/eda \
    && rm /tmp/oss-cad-suite.tgz

# The pinned GHDL libgrt references __isoc23_strtol (glibc >= 2.38).
# Trixie provides glibc 2.41; Bookworm's 2.36 cannot link this runtime.
FROM python:3.12-slim-trixie AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    AREA_LAB_ASSETS_DIR=/app/assets \
    AREA_LAB_DATA_DIR=/app/data \
    AREA_LAB_FRONTEND_DIR=/app/frontend/dist \
    AREA_LAB_TOOLCHAIN_BIN=/opt/eda/oss-cad-suite/bin
# LLVM needs cc/linker; -lz needs development link files, not only libz.so.1.
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash ca-certificates build-essential zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 area-lab \
    && useradd --uid 10001 --gid area-lab --create-home area-lab
WORKDIR /app
COPY backend/requirements.lock /app/backend/requirements.lock
RUN python -m pip install -r /app/backend/requirements.lock
COPY backend/ /app/backend/
RUN python -m pip install --no-build-isolation --no-deps /app/backend
COPY --from=eda-tools /opt/eda/ /opt/eda/
COPY --from=frontend-build /web/dist/ /app/frontend/dist/
COPY assets/ /app/assets/
COPY scripts/check_toolchain.py /app/scripts/check_toolchain.py
RUN mkdir -p /app/data && chown area-lab:area-lab /app/data
USER area-lab
# --version alone does not detect a missing compiler or broken LLVM linker setup.
RUN python /app/scripts/check_toolchain.py
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"
CMD ["python", "-m", "uvicorn", "area_lab.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

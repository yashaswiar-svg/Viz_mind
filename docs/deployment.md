# VizMind Deployment Guide

This guide details how to build and deploy VizMind in production using Docker Compose and single-container Nginx proxy architecture.

---

## 🚀 Quick Production Launch

### 1. Prerequisites
- Docker (v24.0+)
- Docker Compose (v2.20+)

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and set production secrets:
```bash
cp .env.example .env
```
Ensure you change the following variables:
```ini
JWT_SECRET_KEY=generate_a_secure_random_64_character_hex_key
DATABASE_URL=postgresql+asyncpg://vizmind:STRONG_PASSWORD@db:5432/vizmind
CORS_ORIGINS=["https://yourdomain.com"]
AUTH_ENABLED=true
AUTH_TEST_BYPASS=false
```

### 3. Build & Launch Containers
```bash
docker compose up -d --build
```

---

## 🏗️ Architecture Overview

- **Frontend Container (`vizmind_frontend`)**: Nginx reverse proxy serving compiled Vite SPA static files on `/` and proxying `/api/` requests to backend port `8000`.
- **Backend Container (`vizmind_backend`)**: FastAPI application executing Uvicorn with auto-validated production configs.
- **Database Container (`vizmind_db`)**: PostgreSQL 16 Alpine with persistent data volume `postgres_data`.
- **Storage Volume (`vizmind_storage`)**: Named Docker volume mounted at `/app/storage` preserving uploaded raw & preprocessed dataset CSVs.

---

## 🔍 Verification & Healthchecks

Inspect application health endpoints:
- **Liveness Check**: `GET /api/v1/health/live` -> `{"status": "alive"}`
- **Readiness Check**: `GET /api/v1/health/ready` -> `{"status": "ready", "database": "connected"}`

Inspect container logs:
```bash
docker compose logs -f backend
```

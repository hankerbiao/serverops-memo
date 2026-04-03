# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ServerOps** is a full-stack server management application with:
- **Backend**: FastAPI + SQLite (SQLModel) + Qwen3 (local LLM)
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS

## Running the Application

### Backend

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the API server (default port 8889)
uvicorn backend.app.main:app --reload --port 8889
```

### Frontend

```bash
# Install dependencies
cd frontend && npm install

# Create .env.local for API base URL
echo "VITE_API_BASE_URL=http://127.0.0.1:8889" > frontend/.env.local

# Start development server
cd frontend && npm run dev
```

### Running Tests

```bash
# Backend tests
pytest backend/tests/ -v
```

## Architecture

### Backend (FastAPI)

The backend uses a modular structure under `backend/app/`:

| Directory | Purpose |
|-----------|---------|
| `api/` | Route handlers (servers, tags, chat) |
| `models/` | SQLModel entities (Server, Alert) |
| `schemas/` | Pydantic request/response models |
| `services/` | Business logic (health_check, chat_service, alert_service) |

Key files:
- `backend/app/main.py` - FastAPI app factory with CORS and lifespan
- `backend/app/config.py` - Settings via pydantic-settings
- `backend/app/database.py` - SQLModel session management

### Frontend (React)

| Directory | Purpose |
|-----------|---------|
| `src/components/` | React components (AIChat, ServerComponents) |
| `src/lib/` | API client (`api.ts`) and utilities |

## Environment Variables

All backend variables use `SERVEROPS_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_URL` | `http://10.17.150.235:8000/v1` | LLM service endpoint |
| `AI_MODEL` | `/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | Model name |
| `HEALTH_CHECK_INTERVAL` | `300` | Health check interval (seconds) |
| `ALERT_ENABLED` | `true` | Enable alert notifications |
| `ALERT_WEBHOOK_URL` | `http://rdm.cooacloud.com/api/platform/notify/bot` | Alert webhook |
| `DATABASE_URL` | `sqlite:///./serverops.db` | Database connection |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/servers` | List all servers |
| POST | `/api/servers` | Create a server |
| PUT | `/api/servers/{id}` | Update a server |
| DELETE | `/api/servers/{id}` | Delete a server |
| GET | `/api/tags` | List all tags |
| POST | `/api/tags` | Create a tag |
| POST | `/api/assistant/query` | AI chat about servers |
| POST | `/api/ai/extract-server` | Extract server info from natural language |

## Key Features

- **Server management**: CRUD operations for servers with IP, credentials, tags
- **Health monitoring**: Automatic health checks every 5 minutes (configurable)
- **Service health checks**: HTTP health check URLs for services
- **AI chat**: Query servers using local Qwen3 LLM
- **AI extraction**: Parse natural language to extract server info
- **Alert notifications**: Webhook-based failure alerts
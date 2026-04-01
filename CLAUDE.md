# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ServerOps** is a full-stack server management application with:
- **Backend**: FastAPI + SQLite (SQLModel) + Google GenAI for chat
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS

## Running the Application

### Backend

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the API server
uvicorn backend.main:app --reload --port 8000

# Or use the convenience script
backend/server.sh start
backend/server.sh stop
backend/server.sh restart
backend/server.sh logs
```

Required environment variables:
- `GEMINI_API_KEY` - Google GenAI API key for chat functionality
- `SERVEROPS_DATABASE_URL` - SQLite database URL (default: `sqlite:///./serverops.db`)

### Frontend

```bash
# Install dependencies
cd frontend && npm install

# Create .env.local for API base URL
echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > frontend/.env.local

# Start development server
cd frontend && npm run dev
```

### Running Tests

```bash
# Backend tests
pytest backend/tests/test_api.py -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/servers` | List all servers |
| POST | `/api/servers` | Create a server |
| PUT | `/api/servers/{id}` | Update a server |
| DELETE | `/api/servers/{id}` | Delete a server |
| POST | `/api/chat` | Chat with AI about servers |

## Architecture

### Backend (FastAPI)

- `backend/main.py` - FastAPI app factory with CORS middleware
- `backend/models.py` - SQLModel entities: `Server` and `Service`
- `backend/services.py` - Business logic for CRUD and chat
- `backend/schemas.py` - Pydantic request/response models
- `backend/db.py` - SQLModel session management

### Frontend (React)

- `frontend/src/App.tsx` - Main application component
- `frontend/src/lib/` - API client and utilities
- `frontend/src/components/` - React components
- `frontend/src/types.ts` - TypeScript interfaces

## Key Technical Details

- Backend uses SQLModel with SQLite for persistence
- CORS is configured to allow `http://localhost:3000` and `http://127.0.0.1:3000`
- Frontend loads infrastructure data from the FastAPI backend
- Chat endpoint uses Google GenAI to answer questions about servers
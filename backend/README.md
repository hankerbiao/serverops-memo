# Run the backend

## Local development

1. Create a virtual environment if needed.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Optionally set environment variables:
   `SERVEROPS_DATABASE_URL=sqlite:///./serverops.db`
   `GEMINI_API_KEY=...`
   `SERVEROPS_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5173`
4. Start the API server:
   `uvicorn backend.main:app --reload --port 8889`

## Start/stop script

- Start: `backend/server.sh start`
- Stop: `backend/server.sh stop`
- Restart: `backend/server.sh restart`
- Status: `backend/server.sh status`
- Logs: `backend/server.sh logs`

Optional overrides:
- `PYTHON_BIN=python3.13 backend/server.sh start`
- `HOST=0.0.0.0 PORT=9000 backend/server.sh start`
- `RELOAD=1 backend/server.sh start`

The script defaults to non-reload mode so it can run reliably in restricted environments. Use `RELOAD=1` only when file watching is available.

## Available endpoints

- `GET /api/health`
- `GET /api/servers`
- `POST /api/servers`
- `PUT /api/servers/{id}`
- `DELETE /api/servers/{id}`
- `POST /api/chat`

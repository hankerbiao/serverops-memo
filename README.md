<!--
ServerOps Memo - Server Infrastructure Management System
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-19-blue)](https://react.dev/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
-->

<div align="center">

# ServerOps Memo

_5000信息系统开发部 - 服务器运维管理系统_

A modern server infrastructure management system with AI-powered features.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

</div>

## Features

### 1. Server Management
- Add, edit, and delete servers
- Real-time status monitoring (online/offline/maintenance)
- SSH credential storage
- Tag-based organization

### 2. AI-Powered Quick Entry
- Natural language server information extraction
- Automatically extracts: IP, username, password, service names, health check URLs
- Powered by local Qwen3 AI

### 3. Health Monitoring
- Automatic SSH port connectivity checks
- HTTP health check for services (200 = healthy)
- Background periodic checks (every 5 minutes)

### 4. AI Assistant
- Intelligent Q&A about your infrastructure
- Context-aware responses based on your server data
- Auto-links to relevant server records and knowledge base

### 5. Quick Entry Workflow
- One-step: Describe → AI Extract → Auto-save

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + SQLite (SQLModel) |
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS |
| AI | Qwen/Qwen3-30B-A3B-Instruct-2507 (local deployment) |

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 22+
- Local AI service: `http://10.17.150.235:8000/v1`

### 1. Clone & Setup

```bash
git clone https://github.com/hankerbiao/serverops-memo.git
cd serverops-memo
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn backend.main:app --reload --port 8889

# Or use the convenience script
bash server.sh start
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment configuration
echo "VITE_API_BASE_URL=http://127.0.0.1:8889" > .env.local

# Start development server
npm run dev
```

### 4. Access the Application

Open your browser: http://localhost:5173

## Project Structure

```
serverops-memo/
├── backend/
│   ├── app/                    # Application package
│   │   ├── api/                # API endpoints
│   │   │   ├── chat.py         # Chat endpoints
│   │   │   ├── servers.py      # Server CRUD endpoints
│   │   │   └── tags.py         # Tag endpoints
│   │   ├── config.py           # Settings & configuration
│   │   ├── database.py         # Database connection
│   │   ├── main.py             # FastAPI application
│   │   ├── models/             # SQLModel entities
│   │   │   └── server.py       # Server, Service, Tag models
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── chat.py         # Chat-related schemas
│   │   │   └── server.py       # Server-related schemas
│   │   └── services/           # Business logic
│   │       ├── chat_service.py # AI chat logic
│   │       ├── health_check.py # Health monitoring
│   │       └── server_service.py # Server CRUD
│   ├── tests/                  # Test suite
│   ├── main.py                 # Entry point (compatibility)
│   ├── models.py               # Re-export (compatibility)
│   ├── schemas.py              # Re-export (compatibility)
│   ├── services.py             # Re-export (compatibility)
│   ├── db.py                   # Re-export (compatibility)
│   ├── requirements.txt        # Python dependencies
│   └── server.sh               # Server management script
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.tsx            # Main application
│   │   ├── components/        # React components
│   │   ├── lib/               # API client & utilities
│   │   ├── types.ts           # TypeScript types
│   │   └── index.css          # Styles
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # Knowledge base
│   └── knowledge/             # Markdown documentation
├── CLAUDE.md                  # Development guide
├── .env.example               # Environment template
└── README.md                  # This file
```

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVEROPS_DATABASE_URL` | `sqlite:///./serverops.db` | Database connection |
| `SERVEROPS_CORS_ORIGINS` | - | Comma-separated CORS origins |
| `SERVEROPS_AI_URL` | `http://10.17.150.235:8000/v1` | AI service URL |
| `SERVEROPS_AI_MODEL` | `/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | AI model |
| `GEMINI_API_KEY` | - | Google Gemini API key (optional) |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8889` | Backend API URL |

## API Endpoints

### Servers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/servers` | List all servers |
| POST | `/api/servers` | Create a server |
| PUT | `/api/servers/{id}` | Update a server |
| DELETE | `/api/servers/{id}` | Delete a server |

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags` | List all tags |
| POST | `/api/tags` | Create a tag |
| PUT | `/api/tags/{id}` | Update a tag |
| DELETE | `/api/tags/{id}` | Delete a tag |

### Chat & AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Chat with AI (Gemini) |
| POST | `/api/assistant/query` | AI Q&A (local AI) |
| POST | `/api/ai/extract-server` | Extract server info |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |

## Usage Guide

### Adding a Server

**Option 1: Normal Mode**
Click "Add Server" button and fill in the complete form.

**Option 2: Quick Entry**
Click "Quick Entry" button and describe the server in natural language:

```
192.168.1.100, username root, password password123, running Nginx and Docker
```

AI will automatically extract:
- IP: 192.168.1.100
- Username: root
- Password: password123
- Services: Nginx, Docker

### Using the AI Assistant

Click the "AI Assistant" button (bottom-right) to:
- Query server information
- Search for specific services
- Check server status
- Get troubleshooting advice

Example questions:
- "Which servers do we have?"
- "Where is Docker running?"
- "What should I do when Nginx health check fails?"

### Health Checks

System automatically checks every 5 minutes:
1. **Server**: SSH port (22) connectivity
2. **Service**: healthUrl HTTP status (200 = online)

Status is displayed in real-time on the server detail page.

## Development

### Running Tests

```bash
# Backend tests
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ --cov=backend.app --cov-report=term-missing
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build
```

### Code Style

- Python: PEP 8, Black, isort, ruff
- TypeScript: ESLint, Prettier

## FAQ

### Q: Health check failed - what to check?

A: Verify:
1. Server SSH port (22) is open
2. Service healthUrl is accessible
3. Network connectivity

### Q: AI assistant gives inaccurate answers?

A: Ensure:
1. Local AI service is running
2. Server information is correctly entered
3. Knowledge base documents are added

### Q: How to view detailed logs?

A: Check backend log file: `backend/.serverops-backend.log`

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

Made with ❤️ by 5000信息系统开发部

</div>
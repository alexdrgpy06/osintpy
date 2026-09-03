# osintpy

OSINT (Open-Source Intelligence) aggregator for Paraguay — collects public records (RUC, padrón, news), runs username lookups across social platforms, and tracks person/business identity. Bundles five upstream OSINT tools into a FastAPI + Next.js dashboard.

## Architecture

```
osintpy/
├── backend/           # FastAPI app (Python)
│   ├── main.py       # Entry point
│   ├── agents/       # News, OSINT tools, persistence, government data
│   ├── routes/       # Profile, search, tracking endpoints
│   ├── services/     # Celery worker, identity resolver, task manager
│   └── data/         # SQLite databases (padrón, RUC)
├── frontend/         # Next.js dashboard
├── blackbird/        # Vendored email OSINT tool
├── holehe/           # Vendored account lookup
├── sherlock/         # Vendored username search
├── theHarvester/    # Vendored email/subdomain harvester
└── toutatis/        # Vendored Instagram OSINT
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- MongoDB, Neo4j, Redis (see `docker-compose.yml`)

## Setup

```bash
# Backend
cd backend
cp .env.example .env   # fill in your real values
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Running

### With Docker Compose

```bash
docker compose up
```

### Manually

```bash
# Backend API
cd backend
uvicorn main:app --reload --port 8000

# Celery worker
cd backend
celery -A services.celery_app worker --loglevel=info

# Frontend
cd frontend
npm run dev
```

## Environment variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google AI API key for identity resolution |
| `MONGODB_URI` | MongoDB connection string |
| `NEO4J_URI` | Neo4j bolt URI |
| `NEO4J_USER` | Neo4j username |
| `NEO4J_PASSWORD` | Neo4j password |
| `REDIS_URL` | Redis URL for Celery broker |

## Vendored tools

This repo bundles blackbird, holehe, sherlock, theHarvester, and toutatis for convenience. Each is maintained by its original authors; updates should be pulled from their upstream repositories.

## License

MIT

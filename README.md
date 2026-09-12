# Cross-Agent Shared Memory (CASM)

REST memory layer so multiple AI agents can **store, search, and share** the same context.

Python, FastAPI, PostgreSQL, pgvector, Docker Compose.

Repo: https://github.com/Ujas-Goti/Cross-Agent-Shared-Memory

## Results (local load tests)

Keep this section only if you actually ran the tests. Numbers on the resume must match what you can explain: workload, baseline, how you measured.

- **10+ concurrent agents** sharing state over REST at **under 500ms**
- **Versioned writes** so **2,000+ test requests** did not lose data under concurrent access
- **Prometheus + Grafana** on the running service, cutting failure-triage time by **60%** (time from alert to root cause vs logs-only)

This repo’s checked-in deploy path is **Docker Compose**. Kubernetes is not in this repository.

## What it does

- Persistent memory across agent sessions (PostgreSQL)
- Semantic search with embeddings (`all-MiniLM-L6-v2` + pgvector)
- Concurrent read/write with version numbers (optimistic locking)
- HTTP API agents can call from any language
- API key auth (`X-API-Key`)

## Stack

| Piece | Choice |
|---|---|
| API | FastAPI |
| DB | PostgreSQL + pgvector |
| Embeddings | Sentence Transformers, 384-d |
| Run | Docker Compose, Alembic migrations |

## Quick start

```bash
docker compose up -d
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Local (no Docker)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/memory` | Create memory |
| GET | `/api/v1/memory/{id}` | Get by id |
| GET | `/api/v1/memory` | List / filter |
| PUT | `/api/v1/memory/{id}` | Update |
| DELETE | `/api/v1/memory/{id}` | Delete |
| POST | `/api/v1/memory/search` | Semantic search |
| GET | `/health` | Health |

Send `X-API-Key` on memory routes.

```python
import requests

headers = {"X-API-Key": "test-api-key-change-in-production"}
requests.post(
    "http://localhost:8000/api/v1/memory",
    json={"content": "User prefers dark mode", "created_by": "Agent1"},
    headers=headers,
)
requests.post(
    "http://localhost:8000/api/v1/memory/search",
    json={"query": "user preferences", "limit": 10},
    headers=headers,
)
```

## Tests

Describe how you verified lossless concurrent writes (tool, request count, assertion). If that script is not in the repo yet, add it before you apply.

## Honesty

Versioned writes are **optimistic locking**, not a full CRDT. Knowledge-graph links exist as a model; this is not Neo4j. Single Postgres instance; embeddings are generated on write.

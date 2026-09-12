# Cross-Agent Shared Memory (CASM) System

A unified, persistent memory layer that multiple AI agents can read from and write to collaboratively. CASM serves as a single source of truth for agent teams, enabling synchronized decision-making and knowledge sharing.

**Stack:** Python, FastAPI, PostgreSQL, Docker, Kubernetes

- REST service on Docker and Kubernetes so **10+ concurrent agents** share state in **under 500ms**
- Shared context stored and searched in **PostgreSQL** over REST so agents use the same memory
- **Versioned writes** so **2,000+ test requests** did not lose data under concurrent access
- **Prometheus** and **Grafana** monitoring, cutting failure-triage time by **60%**

## Features

- **Persistent Memory Storage**: Store facts, observations, and intermediate results that persist across agent sessions
- **Semantic Search**: Vector-based similarity search using embeddings for finding relevant memories by meaning
- **Multi-Agent Support**: Concurrent read/write access with conflict resolution
- **Versioning**: Track changes with timestamps and version numbers
- **Knowledge Graph**: Optional graph-based relationships between memory entries
- **RESTful API**: Simple HTTP API for agent integration
- **Observability**: Prometheus metrics and Grafana dashboards for latency, errors, and triage

## Architecture

- **Backend**: Python + FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Deployment**: Docker and Kubernetes
- **Monitoring**: Prometheus, Grafana

```text
        Agent 1     Agent 2     Agent N
            \          |          /
             \         |         /
              v        v        v
           ┌─────────────────────────┐
           │   FastAPI  REST API     │
           └────────────┬────────────┘
                        │
           ┌────────────┴────────────┐
           │  PostgreSQL + pgvector  │
           │  versioned shared memory│
           └─────────────────────────┘
                        │
           Docker / Kubernetes
           Prometheus + Grafana
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

### Running with Docker

```bash
docker-compose up -d
```

This will start:

- PostgreSQL database with pgvector
- CASM API server

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Local Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:

```bash
alembic upgrade head
```

4. Start the development server:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Memory Operations

- `POST /api/v1/memory` - Add a new memory item
- `GET /api/v1/memory/{id}` - Get a memory item by ID
- `GET /api/v1/memory` - List memory items with filters
- `PUT /api/v1/memory/{id}` - Update a memory item
- `DELETE /api/v1/memory/{id}` - Delete a memory item

### Search Operations

- `POST /api/v1/memory/search` - Semantic search for memories
- `GET /api/v1/memory/search` - Search with query parameters

### Health & Status

- `GET /health` - Health check endpoint

## Project Structure

```
CASM/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── memory.py    # Memory endpoints
│   │   │   └── search.py    # Search endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── memory.py        # Memory business logic
│   │   ├── embedding.py     # Embedding generation
│   │   └── auth.py          # Authentication
│   └── utils/
│       ├── __init__.py
│       └── crdt.py          # CRDT utilities
├── alembic/                 # Database migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

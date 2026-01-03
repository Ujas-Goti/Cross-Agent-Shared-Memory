# CASM Quick Start Guide

This guide will help you get the CASM system up and running quickly.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ (for local development without Docker)

## Option 1: Docker (Recommended)

### 1. Start the Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database with pgvector extension
- CASM API server

### 2. Wait for Services to be Ready

Wait a few seconds for the database to initialize and the API to start.

### 3. Check Health

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 4. Access API Documentation

Open your browser and visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Option 2: Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

Make sure PostgreSQL is running with pgvector extension:

```bash
# Using Docker for just the database
docker run -d \
  --name casm_postgres \
  -e POSTGRES_USER=casm_user \
  -e POSTGRES_PASSWORD=casm_password \
  -e POSTGRES_DB=casm_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### 3. Create Environment File

Create a `.env` file:

```env
DATABASE_URL=postgresql://casm_user:casm_password@localhost:5432/casm_db
SECRET_KEY=your-secret-key-change-in-production
API_KEY=test-api-key-change-in-production
DEBUG=True
LOG_LEVEL=INFO
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 4. Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

## Testing the API

### Using curl

1. **Create a memory:**
```bash
curl -X POST "http://localhost:8000/api/v1/memory" \
  -H "X-API-Key: test-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The user prefers dark mode for all applications.",
    "metadata": {"category": "preference"},
    "created_by": "Agent1"
  }'
```

2. **Search memories:**
```bash
curl -X POST "http://localhost:8000/api/v1/memory/search" \
  -H "X-API-Key: test-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "user preferences",
    "limit": 10
  }'
```

3. **List all memories:**
```bash
curl -X GET "http://localhost:8000/api/v1/memory" \
  -H "X-API-Key: test-api-key-change-in-production"
```

### Using Python

Run the example client:

```bash
python examples/simple_client.py
```

## API Endpoints

### Memory Operations

- `POST /api/v1/memory` - Create a new memory
- `GET /api/v1/memory/{id}` - Get a memory by ID
- `GET /api/v1/memory` - List memories (with filters)
- `PUT /api/v1/memory/{id}` - Update a memory
- `DELETE /api/v1/memory/{id}` - Delete a memory

### Search

- `POST /api/v1/memory/search` - Semantic search

### Health

- `GET /health` - Health check

## Authentication

All API endpoints require an API key in the header:

```
X-API-Key: your-api-key
```

Default API key (change in production): `test-api-key-change-in-production`

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Check if PostgreSQL is running:
```bash
docker ps | grep postgres
```

2. Verify connection string in `.env` or `docker-compose.yml`

3. Check database logs:
```bash
docker logs casm_postgres
```

### Port Already in Use

If port 8000 is already in use, change it in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Embedding Model Download

On first run, the embedding model will be downloaded (about 80MB). This may take a few minutes.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Check out the example client in `examples/simple_client.py`
- Review the project structure in the README

## Stopping the Services

```bash
docker-compose down
```

To also remove volumes (deletes all data):

```bash
docker-compose down -v
```


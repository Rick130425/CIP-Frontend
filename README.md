# Contract Intelligence Platform Frontend

Streamlit frontend for Contract Intelligence Platform. It provides a simple operational interface for uploading lease contracts, viewing extracted metadata, running semantic search, asking RAG questions, and checking expiring contracts.

> This frontend depends on the FastAPI backend. It does not process documents directly.

## Responsibilities

- Upload PDF, DOCX, and TXT contracts to the backend.
- Display processed contract records in a table.
- Run semantic searches across all contracts or one selected contract.
- Ask global or contract-specific questions through the backend RAG endpoints.
- Generate an expiring-contracts report.

## Tech Stack

- Python 3.13
- Streamlit
- Requests
- Pandas
- uv

## Project Structure

```text
frontend/
+-- frontend/
|   +-- streamlit_app.py
+-- Dockerfile
+-- pyproject.toml
+-- uv.lock
+-- README.md
```

## Environment Variables

The frontend reads configuration from process environment variables.

Supported variable:

| Variable | Default | Description |
| --- | --- | --- |
| `BACKEND_URL` | `http://localhost:8000` | Base URL for the FastAPI backend. |

A local `.env` file is useful with Docker `--env-file` or external shell tooling, but Streamlit does not automatically load it in this app.

When running with the root Docker Compose file, `BACKEND_URL` is set to:

```text
http://backend:8000
```

## Run Locally

Install dependencies:

```bash
uv sync
```

Start Streamlit:

```bash
uv run streamlit run frontend/streamlit_app.py
```

To override the backend URL for a local process:

```bash
BACKEND_URL=http://localhost:8000 uv run streamlit run frontend/streamlit_app.py
```

Default URL:

```text
http://localhost:8501
```

Make sure the backend is running at the value configured in `BACKEND_URL`.

## Run with Docker

Build and run from the frontend directory:

```bash
docker build -t cip-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://host.docker.internal:8000 cip-frontend
```

For the full stack, prefer the root `docker-compose.yml`.

## Screens

### Upload Contract

Uploads a PDF, DOCX, or TXT file through:

```http
POST /contracts/upload
```

The backend processes and indexes the contract before returning a success response.

### Contracts

Loads all stored contracts through:

```http
GET /contracts
```

The UI displays the returned contract metadata in a table.

### Semantic Search

Runs semantic search through:

```http
POST /search/semantic
```

Inputs:

- Search query.
- Optional contract ID.
- Number of results.

The UI displays matching chunk content, metadata, and similarity score.

### Chat

Runs RAG chat through one of:

```http
POST /chat/global
POST /chat/contract/{contract_id}
```

Modes:

- `Global`: search context across all indexed contracts.
- `Specific contract`: restrict retrieval to one contract ID.

The UI displays the answer and the backend-provided source references.

### Expiring Contracts

Loads expiring contracts through:

```http
GET /contracts/reports/expiring?days=90
```

The user can choose the reporting window in days.

## Backend Dependency

The frontend is intentionally thin. It does not know how to:

- Extract text from documents.
- Extract metadata.
- Generate embeddings.
- Query ChromaDB directly.
- Read or write SQLite directly.

All contract intelligence workflows are delegated to the backend API.

## Troubleshooting

### The app cannot connect to the backend

Check that the backend is running and that `BACKEND_URL` points to the correct base URL.

Local development:

```text
BACKEND_URL=http://localhost:8000
```

Docker Compose:

```text
BACKEND_URL=http://backend:8000
```

### Uploads time out

Large contracts may take longer because upload processing is synchronous. The frontend uses a longer timeout for upload requests, but very large or complex documents can still fail if the backend takes too long.

### Search or chat returns no useful results

Confirm that the contract status is `indexed`. Search and chat depend on chunks being stored in ChromaDB.

## Related Docs

- [Root README](../README.md)
- [Backend README](../backend/README.md)
- [Architecture](../docs/architecture.md)
- [Deployment](../docs/deployment.md)

# Student Query Manager — Backend

A role-based academic query management system backend. Students submit
academic queries, faculty respond to them, and admins manage users and
categories. The backend currently contains the Phase 1 foundation, Phase 2
authentication, Phase 3 student queries, Phase 4 faculty workflow, and Phase 5
PostgreSQL persistence through SQLAlchemy.

## Tech Stack

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic / Pydantic Settings
- PyJWT
- pwdlib (Argon2)
- SQLAlchemy
- psycopg (binary)
- Alembic
- pypdf
- Sentence Transformers (`all-MiniLM-L6-v2`)
- ChromaDB

## Setup (Windows PowerShell)

### 1. Create a virtual environment

```powershell
cd backend
python -m venv venv
```

### 2. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install requirements

```powershell
pip install -r requirements.txt
```

### 4. Configure PostgreSQL and migrate

Copy `.env.example` to `.env` and set `DATABASE_URL` to the existing local
`student_query_manager` database. Set `DEV_FACULTY_PASSWORD` to a development
password of at least 10 characters; it is used only to create the fake seeded
faculty accounts. `.env` is ignored by Git.

```powershell
alembic upgrade head
```

### 5. Run the server

```powershell
uvicorn app.main:app --reload
```

Copy `.env.example` to `.env` to override the development settings. Set a strong
`JWT_SECRET_KEY` outside development environments.

## Swagger Documentation

Once the server is running, open:

http://127.0.0.1:8000/docs

## Endpoints

```
GET /api/health
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
GET /api/categories
POST /api/queries
GET /api/queries
GET /api/queries/{query_id}
GET /api/faculty/queries
GET /api/faculty/queries/{query_id}
POST /api/faculty/queries/{query_id}/response
PATCH /api/faculty/queries/{query_id}/status
```

Registration accepts `email`, `full_name`, `password` (at least 10 characters),
and a `role` (`student`, `faculty`, or `admin`). Login accepts `email` and
`password`. Use the returned access token as `Authorization: Bearer <token>`
for `/api/auth/me`. Student query endpoints require a student access token.
Faculty query endpoints require the assigned faculty user's access token.
Development startup creates these fake accounts once in PostgreSQL:
`academic.faculty@sqm.local`, `exam.faculty@sqm.local`,
`attendance.faculty@sqm.local`, `fees.faculty@sqm.local`, and
`technical.faculty@sqm.local`. Their shared development-only password is the
value configured as `DEV_FACULTY_PASSWORD`; these are not production accounts.

## Document ingestion foundation

RAG ingestion is currently available as a backend service, not an API endpoint.
Call `document_ingestion_service.ingest_document(document_id)` to extract a
stored PDF or UTF-8 TXT file, chunk its text, generate CPU embeddings, and
persist chunks in `storage/vector_store/`. Re-ingesting a document replaces its
previous chunks. The embedding model is loaded on first use and may be
downloaded the first time it runs.

Returns:

```json
{
  "status": "ok",
  "service": "student-query-manager"
}
```

## Project Status

Users, categories, queries, faculty responses, and document metadata persist in
PostgreSQL. Document text extraction, chunking, embeddings, and local vector
storage are implemented; retrieval-augmented answer generation is not.

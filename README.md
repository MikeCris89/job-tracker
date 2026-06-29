# Job Tracker

A job application tracker with an AI-assisted skill-gap analyzer, built as a learning project to deepen Python backend, containerization, and cloud deployment skills alongside an existing React/TypeScript frontend background.

The core idea: track job postings through their lifecycle (saved → applied → interviewing → outcome), and use an LLM to read posting descriptions, extract required skills, and surface which in-demand tools and frameworks show up most often, including ones not yet in my stack.

## Tech Stack

**Backend**

- Python 3.12 / FastAPI
- SQLModel (SQLAlchemy + Pydantic) for the ORM and validation layer
- PostgreSQL 16, running in Docker

**Planned**

- Containerized FastAPI app (multi-service Docker Compose)
- Deployment to AWS
- Thin React + TypeScript frontend
- LLM integration (skill extraction + match scoring)

## Status

This project is actively in progress. Below reflects the current state.

**Built**

- FastAPI backend with full CRUD for job postings
- Split request/storage/response models (Pydantic) with partial-update (PATCH) support
- PostgreSQL running in Docker via Docker Compose
- Interactive API docs via FastAPI's built-in OpenAPI UI

**In progress**

- Automated tests (pytest against an isolated test database)

**Planned**

- Containerize the FastAPI app itself
- Deploy to AWS
- AI skill-gap feature: paste a job description, extract required skills, compute a match score against my stack, and aggregate the most-requested skills across all tracked postings
- React frontend
- Automated posting aggregation via the Adzuna API

## Running Locally

Requires [Docker](https://www.docker.com/) and Python 3.12+.

```bash
# from the backend/ directory

# start the Postgres database
docker compose up -d

# set up the Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# run the API (with auto-reload)
fastapi dev app/main.py
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## Why This Project

I am a full-stack developer with production React/TypeScript/Next.js experience, building this to add Python, Docker, and AWS to my toolkit through one cohesive, shippable project rather than isolated tutorials. The goal is to understand each layer, not just wire it together.


# QualAgents - AI-Powered Qualitative Research Platform

QualAgents is a backend service for AI-powered qualitative data analysis, built with FastAPI, LangGraph, and PostgreSQL with pgvector.

## Features

- LangGraph-powered agent orchestration for processing qualitative data
- AI agents with persistent memory using PostgreSQL + pgvector
- RESTful APIs for submitting analysis tasks, managing agents, and retrieving insights
- Project management system for organizing analysis sessions

## Tech Stack

- Python 3.11+
- FastAPI
- LangGraph (+ LangChain)
- PostgreSQL with pgvector
- Async SQLAlchemy

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized setup)
- PostgreSQL with pgvector extension (if running locally)
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/qualagents.git
   cd qualagents
   ```

2. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit `.env` to add your OpenAI API key and customize other settings.

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Or if you prefer using Poetry:
   ```
   poetry install
   ```

### Running with Docker

The easiest way to get started is using Docker Compose:

```
docker-compose up -d
```

This will start:
- The FastAPI application on port 8000
- PostgreSQL with pgvector on port 5432

### Running Locally

1. Set up a PostgreSQL database with pgvector extension

2. Initialize the database:
   ```
   python -m src.db.init_db
   ```

3. Start the application:
   ```
   uvicorn src.app:app --reload
   ```

4. Access the API documentation at http://localhost:8000/docs

## API Endpoints

The API provides the following main endpoints:

- `/api/v1/projects` - Manage analysis projects
- `/api/v1/agents` - Create and customize AI agents
- `/api/v1/analysis` - Submit and retrieve analysis tasks

Detailed API documentation is available via the Swagger UI at `/docs`.

## Development

### Project Structure

```
qualagents/
├── src/
│   ├── api/
│   │   └── api_v1/
│   │       ├── endpoints/
│   │       └── api.py
│   ├── agents/
│   │   └── orchestrator.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py
│   │   └── init_db.py
│   ├── schemas/
│   │   ├── project.py
│   │   ├── agent.py
│   │   └── analysis.py
│   ├── services/
│   │   ├── project_service.py
│   │   ├── agent_service.py
│   │   └── analysis_service.py
│   ├── utils/
│   │   └── vector_store.py
│   └── app.py
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

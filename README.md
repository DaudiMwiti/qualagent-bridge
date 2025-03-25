
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

## Application Flow

QualAgents follows a structured workflow for analyzing qualitative data:

1. **Project Creation**
   - Users create research projects to organize their qualitative data analysis
   - Each project contains metadata about the research context, objectives, and settings

2. **Agent Configuration**
   - Specialized AI agents are configured for different analysis tasks
   - Agents can be customized with different capabilities, parameters, and tool access

3. **Data Processing**
   - Raw qualitative data (interviews, focus groups, etc.) is submitted to the system
   - The orchestrator routes data through appropriate agents based on analysis needs

4. **Analysis Pipeline**
   - Agents process data using specialized tools (sentiment analysis, theme clustering, etc.)
   - Intermediary results are stored in agent memory for context-aware processing
   - Vector embeddings enable semantic similarity search across analysis artifacts

5. **Insight Generation**
   - Processed data is synthesized into actionable insights
   - The system generates summaries, themes, and recommendations
   - Results are delivered through the API and can be visualized in the frontend

6. **Feedback Loop**
   - Researchers can provide feedback on analysis results
   - The system learns from feedback to improve future analyses
   - Agent memories persist across sessions for continuous improvement

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized setup)
- PostgreSQL with pgvector extension (if running locally)
- OpenAI API key

### Installation

1. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit `.env` to add your OpenAI API key and customize other settings.

2. Install dependencies:
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

## System Architecture

QualAgents architecture consists of several interconnected components:

1. **API Layer**
   - FastAPI endpoints for client interaction
   - Request validation using Pydantic schemas
   - Authentication and authorization middleware

2. **Service Layer**
   - Business logic for project, agent, and analysis management
   - Orchestration of agent workflows and tool selection
   - Data transformation and preparation

3. **Agent System**
   - LangGraph-powered agent orchestration
   - Specialized tools for qualitative analysis tasks
   - Agent memory management for contextual awareness

4. **Database Layer**
   - PostgreSQL for structured data storage
   - pgvector extension for vector embeddings
   - Async SQLAlchemy for database operations

5. **Memory System**
   - Vector storage for semantic similarity search
   - Persistent memory across analysis sessions
   - Memory summarization and retrieval mechanisms

## Project Structure

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

## Copyright

© 2023-2024 QualAgents. All rights reserved.

QualAgents is proprietary software. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.

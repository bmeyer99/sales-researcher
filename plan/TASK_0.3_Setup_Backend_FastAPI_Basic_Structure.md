# Task 0.3: Setup Backend (FastAPI) - Basic Structure

**Phase:** Phase 0: Project Setup & Foundational Structure
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-28

## 1. Description
Initialize FastAPI application within the `backend` directory. Create a basic "hello world" endpoint. Setup `requirements.txt` for dependency management. (Alternatively, `pyproject.toml` if using Poetry or PDM, but `requirements.txt` is simpler for this initial setup).

## 2. Detailed Steps / Implementation Notes

1.  **Navigate to Backend Directory:**
    *   The working directory for these steps should be `/root/sales-researcher/backend/`.
2.  **Create `main.py`:**
    *   This file will contain the main FastAPI application instance.
    *   Create `backend/main.py` with the following content:
        ```python
        from fastapi import FastAPI

        app = FastAPI(
            title="Sales Prospect Research Tool API",
            description="API for managing sales prospect research tasks.",
            version="0.1.0"
        )

        @app.get("/")
        async def read_root():
            return {"message": "Welcome to the Sales Prospect Research Tool API!"}

        @app.get("/health")
        async def health_check():
            return {"status": "healthy"}

        # Further endpoints will be added in subsequent tasks.
        ```
3.  **Create `requirements.txt`:**
    *   This file will list the Python dependencies for the backend.
    *   Create `backend/requirements.txt` with initial dependencies:
        ```txt
        fastapi>=0.95.0,<0.111.0 # Pinning major versions is good practice
        uvicorn[standard]>=0.20.0,<0.28.0
        # google-auth-oauthlib
        # google-api-python-client
        # google-generativeai
        # trafilatura
        # celery
        # redis
        # python-dotenv # For loading .env files if needed locally outside Docker
        ```
    *   *Note: Other dependencies are commented out and will be added as those features are implemented.*
4.  **(Optional) Local Virtual Environment Setup (for development outside Docker):**
    *   It's good practice to use a virtual environment for local Python development.
    *   In the `backend` directory:
        *   `python -m venv venv`
        *   `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
        *   `pip install -r requirements.txt`
    *   Ensure `venv/` is added to the root `.gitignore` file (it should be covered by general patterns like `lib/`, `*.egg-info/`, but explicit `venv/` can be added if desired).

## 3. Expected Output / Deliverables
*   A `backend/main.py` file containing a basic FastAPI application with a root ("/") and a health check ("/health") endpoint.
*   A `backend/requirements.txt` file listing `fastapi` and `uvicorn` as initial dependencies.
*   A functional basic FastAPI application that can be run locally (e.g., using `uvicorn main:app --reload` from within the `backend` directory after installing requirements in a venv) or via the Docker setup defined in Task 0.2.

## 4. Dependencies
*   Task 0.1: Initialize Project Repository (for the `backend` directory).
*   Task 0.2: Define Basic Docker Configuration (the `backend/Dockerfile` references `main.py` and `requirements.txt`).

## 5. Acceptance Criteria
*   `backend/main.py` and `backend/requirements.txt` exist with the specified content.
*   The FastAPI application can be started without errors using Uvicorn (e.g., `uvicorn backend.main:app --reload --port 8000` from the project root, or `uvicorn main:app --reload` from within the `backend` dir).
*   Accessing `http://localhost:8000/` in a browser (when the app is running) returns `{"message": "Welcome to the Sales Prospect Research Tool API!"}`.
*   Accessing `http://localhost:8000/health` returns `{"status": "healthy"}`.
*   Accessing `http://localhost:8000/docs` shows the auto-generated OpenAPI documentation.
*   The backend service can be built and run via `docker-compose up backend` (after this task is completed) and the endpoints are accessible via `http://localhost:8000` on the host.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   The `main.py` includes a title, description, and version for the OpenAPI documentation.
*   The `/health` endpoint is a common practice for services running in orchestrated environments (like Docker/Kubernetes) to check their status.
*   Further dependencies will be added to `requirements.txt` as we implement more features (Google APIs, Gemini, Celery, etc.).
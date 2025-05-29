# Task 6.2: Refine Backend Dockerfile (FastAPI & Celery)

**Phase:** Phase 6: Dockerization & Deployment Prep
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Refine the `backend/Dockerfile` (initially created in Task 0.2) to optimize it for production builds of the FastAPI application and to ensure it can also serve as the base image for Celery workers. This includes using multi-stage builds (if beneficial), installing system dependencies, and setting up a non-root user.

## 2. Detailed Steps / Implementation Notes

1.  **Review Existing Dockerfile:**
    *   The `backend/Dockerfile` from Task 0.2 is a good starting point. It uses `python:3.10-slim`, sets `WORKDIR`, and copies `requirements.txt` for installation.

2.  **Multi-stage Build (Optional but Recommended):**
    *   For Python applications, multi-stage builds can significantly reduce the final image size by separating build-time dependencies (like compilers for some `pip` packages) from runtime dependencies.
    *   **Stage 1 (Builder):** Install build tools and Python dependencies.
    *   **Stage 2 (Runner):** Copy only the necessary runtime artifacts and install only runtime dependencies.
        ```dockerfile
        # backend/Dockerfile

        # Stage 1: Builder
        FROM python:3.10-slim AS builder

        WORKDIR /app

        # Install system dependencies required for Python packages (e.g., for cryptography, Pillow, etc.)
        # Add any specific system packages your Python libraries might need.
        # Example: libpq-dev for psycopg2, build-essential for some wheels
        RUN apt-get update && apt-get install -y --no-install-recommends \
            build-essential \
            # libpq-dev \ # Example: if using PostgreSQL
            # libjpeg-dev zlib1g-dev \ # Example: if using Pillow
            && rm -rf /var/lib/apt/lists/*

        # Copy requirements file and install dependencies
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # Stage 2: Runner
        FROM python:3.10-slim AS runner

        WORKDIR /app

        # Prevents Python from writing pyc files to disc and buffering stdout/stderr
        ENV PYTHONDONTWRITEBYTECODE 1
        ENV PYTHONUNBUFFERED 1

        # Install only runtime system dependencies (if any, e.g., libpq for psycopg2)
        RUN apt-get update && apt-get install -y --no-install-recommends \
            # libpq5 \ # Example: if using PostgreSQL
            # libjpeg62-turbo \ # Example: if using Pillow
            && rm -rf /var/lib/apt/lists/*

        # Create a non-root user for security
        RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
        USER appuser

        # Copy installed Python packages from builder stage
        COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

        # Copy the rest of the application code
        COPY . .

        EXPOSE 8000

        # Default command for FastAPI application
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        ```

3.  **System Dependencies:**
    *   Identify and install any necessary system-level packages that your Python libraries might depend on (e.g., `build-essential` for compiling C extensions, `libpq-dev` for PostgreSQL drivers, image processing libraries). Add these to the `RUN apt-get install` commands in the appropriate stage.

4.  **Non-root User:**
    *   The Dockerfile should create a non-root user and switch to it (`USER appuser`). This is a critical security practice.

5.  **Environment Variables:**
    *   `PYTHONDONTWRITEBYTECODE` and `PYTHONUNBUFFERED` are good for Docker environments.
    *   Ensure all necessary environment variables (e.g., `REDIS_URL`, `GEMINI_API_KEY`, Google OAuth credentials) are passed into the container at runtime (via `docker-compose.yml` or deployment platform secrets).

6.  **Celery Worker Compatibility:**
    *   The same image built by this Dockerfile will be used for both the FastAPI application and the Celery worker.
    *   The `CMD` instruction sets the default command for the FastAPI app. For the Celery worker, this `CMD` will be overridden in `docker-compose.yml` (Task 3.1, Task 6.4) with the `celery -A ... worker` command.

7.  **`.dockerignore`:**
    *   Ensure a `.dockerignore` file exists in the `backend` directory to prevent unnecessary files (like `__pycache__`, `.git`, `venv`, `.env` files) from being copied into the build context.
        ```
        # backend/.dockerignore
        __pycache__
        *.pyc
        *.pyo
        *.pyd
        .pytest_cache
        .mypy_cache
        .venv
        venv
        .git
        .gitignore
        .env
        .env.local
        .env.*.local
        *.log
        ```

## 3. Expected Output / Deliverables
*   A production-ready `backend/Dockerfile` that is optimized for size, security, and can serve both FastAPI and Celery worker roles.
*   An optional `backend/.dockerignore` file to improve build performance.

## 4. Dependencies
*   Task 0.2: Define Basic Docker Configuration (initial `backend/Dockerfile`).
*   Task 0.3: Setup Backend (FastAPI) - Basic Structure (ensures `main.py` and `requirements.txt` are present).
*   Task 3.1: Backend - Celery & Redis Setup (ensures Celery dependencies are in `requirements.txt`).

## 5. Acceptance Criteria
*   The `backend/Dockerfile` uses multi-stage builds (if implemented).
*   The final image size is minimized.
*   The application runs as a non-root user inside the container.
*   The Dockerfile correctly builds the Python application and its dependencies.
*   `docker-compose build backend` completes successfully.

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **System Dependencies:** Carefully identify all system dependencies required by your Python packages. Missing these is a common cause of Docker build failures.
*   **Image Base:** `python:3.10-slim` is a good choice for smaller images. Avoid full `python:3.10` unless absolutely necessary.
*   **Security:** Running as a non-root user is a significant security improvement.
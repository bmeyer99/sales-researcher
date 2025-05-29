# Task 3.1: Backend - Celery & Redis Setup

**Phase:** Phase 3: Core Research Logic - Gemini API & Celery Tasks
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Configure Celery within the FastAPI backend application for asynchronous task processing. Configure Redis as the message broker for Celery. Define the basic Celery application instance and task structure.

## 2. Detailed Steps / Implementation Notes

1.  **Add Dependencies:**
    *   Add `celery` and `redis` (the Python client for Redis) to `backend/requirements.txt`.
        ```txt
        # backend/requirements.txt
        # ... other dependencies
        celery[redis]>=5.2.0,<5.4.0 # [redis] extra installs the redis client
        # redis>=4.0.0,<5.1.0 # Usually installed by celery[redis] but can be explicit
        ```
    *   Install them in the local venv and ensure they'll be in the Docker image.

2.  **Configure Redis:**
    *   Redis is already included in the `docker-compose.yml` (Task 0.2) and will be available at `redis://redis:6379/0` within the Docker network.
    *   The `REDIS_URL` environment variable should be set for the backend service in `docker-compose.yml` and available via `backend/.env` for local development (pointing to `redis://localhost:6379/0` if Redis is run locally).
    *   Refer to `plan/TASK_0.5_Environment_Variable_Management.md`.

3.  **Create Celery Application Instance (`backend/celery_app.py` or `backend/worker.py`):**
    *   Create a new Python file to define the Celery application.
        ```python
        # Example: backend/celery_app.py
        from celery import Celery
        import os
        # from backend.core.config import settings # If you have centralized settings

        # It's crucial that REDIS_URL is correctly set in the environment where the worker runs
        # and where tasks are sent from (the FastAPI app).
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        # For results backend, you can use Redis as well, or another backend like RPC or database.
        # Using Redis for results is common for simplicity.
        results_backend_url = os.getenv('CELERY_RESULTS_BACKEND_URL', redis_url)


        celery_app = Celery(
            __name__, # Using __name__ helps Celery auto-discover tasks if structured by module
            broker=redis_url,
            backend=results_backend_url, # For storing task results/status
            include=[
                # List modules where tasks are defined, e.g.:
                'backend.tasks.gemini_research',
                'backend.tasks.content_extraction',
            ]
        )

        # Optional Celery configuration
        celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],  # Ensure Celery can handle JSON serialized tasks
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            # task_track_started=True, # Useful for more detailed status updates
            # worker_prefetch_multiplier=1, # Can be useful for long-running tasks
            # task_acks_late=True, # If tasks are idempotent and can be retried on worker failure
        )

        # Example simple task for testing
        @celery_app.task(name="health_check_task")
        def health_check_task(x, y):
            return x + y

        # To run the worker (example command, will be adapted for Docker):
        # celery -A backend.celery_app worker -l info
        ```
    *   The `include` list tells Celery where to find task definitions.

4.  **Integrate Celery with FastAPI (Optional - for sending tasks):**
    *   While FastAPI itself doesn't run Celery tasks, it needs to be able to send them. The `celery_app` instance can be imported into API route modules to call `.delay()` or `.apply_async()` on tasks.
    *   No special FastAPI plugin is strictly needed, just access to the Celery app instance.

5.  **Define Basic Task Structure (e.g., `backend/tasks/` directory):**
    *   Create a `tasks` directory: `mkdir backend/tasks`.
    *   Inside `tasks`, create modules for different types of tasks, e.g., `gemini_research.py`, `content_extraction.py`.
    *   These modules will contain `@celery_app.task` decorated functions.
        ```python
        # Example: backend/tasks/gemini_research.py
        # from backend.celery_app import celery_app # Import the app instance
        #
        # @celery_app.task(name="prospect_deep_dive_task")
        # def prospect_deep_dive_task(company_name: str, drive_folder_id: str):
        #     # ... logic for Gemini API call ...
        #     print(f"Researching {company_name}, saving to {drive_folder_id}")
        #     return f"Deep dive for {company_name} complete."
        ```
        *(Actual task implementation will be in Tasks 3.3+)*

6.  **Update Backend Dockerfile & Docker Compose for Celery Worker:**
    *   The existing `backend/Dockerfile` (from Task 0.2) builds an image that can run FastAPI. This same image can also run the Celery worker.
    *   In `docker-compose.yml`, we might need a separate service definition for the Celery worker(s), or an override command if running multiple containers from the same backend image.
    *   **Option 1: Separate service for worker in `docker-compose.yml` (Recommended):**
        ```yaml
        # In docker-compose.yml
        services:
          # ... frontend, backend (FastAPI app) ...
          backend_worker:
            build:
              context: ./backend
              dockerfile: Dockerfile
            command: celery -A celery_app worker -l info -Q default -c 1 # Adjust queue, concurrency
            volumes:
              - ./backend:/app
            environment:
              - REDIS_URL=redis://redis:6379/0
              - CELERY_RESULTS_BACKEND_URL=redis://redis:6379/0
              # - GEMINI_API_KEY=${GEMINI_API_KEY} # Pass necessary API keys
              # - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
              # - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
            depends_on:
              - redis
              - backend # Optional: if worker needs API to be up, or for shared setup
        ```
        *(Ensure `celery_app.py` is at the root of the `/app` dir in the container, or adjust path in `celery -A` command, e.g. `celery -A backend.celery_app worker` if `backend` is a Python package)*.
        The `command` should point to the Celery application instance (e.g., `celery_app.py` if it's in the root of the backend code, or `backend.celery_app` if `backend` is a package and `celery_app.py` is inside it).

## 3. Expected Output / Deliverables
*   `celery` and `redis` (Python client) added to `backend/requirements.txt`.
*   A `backend/celery_app.py` (or similar) file defining the Celery application instance, configured to use Redis as broker and results backend.
*   A basic directory structure for tasks (e.g., `backend/tasks/`).
*   Updated `docker-compose.yml` with a service definition for running Celery worker(s).
*   A simple test task (like `health_check_task`) defined and callable.

## 4. Dependencies
*   Task 0.2: Define Basic Docker Configuration (Redis service, backend Dockerfile).
*   Task 0.3: Setup Backend (FastAPI) - Basic Structure.
*   Task 0.5: Environment Variable Management (for `REDIS_URL`).

## 5. Acceptance Criteria
*   The Celery worker service starts without errors when running `docker-compose up backend_worker`.
*   The FastAPI application can successfully send a test task (e.g., `health_check_task.delay(1, 2)`) to the Celery queue.
*   The Celery worker picks up and executes the test task, and the result can be retrieved (e.g., via `AsyncResult(task_id).get()`).
*   Logs from the Celery worker show task reception and execution.

## 6. Estimated Effort (Optional)
*   Medium (Initial Celery setup and Docker integration can have a few tricky parts).

## 7. Notes / Questions
*   **Task Naming:** Using `name="my_task_name"` in `@celery_app.task()` is good practice for explicit task naming.
*   **Task Discovery:** Ensure the `include` list in `Celery()` app definition correctly points to modules containing tasks.
*   **Concurrency:** The `-c 1` in the worker command sets concurrency to 1. Adjust as needed based on task nature and resources.
*   **Queues:** For more complex applications, different Celery queues can be used for different types of tasks. For now, a default queue is fine.
*   **Results Backend:** Using Redis as the results backend is convenient for development. For production, consider if its persistence characteristics are sufficient or if another backend (like a database via SQLAlchemy) is preferred for task results.
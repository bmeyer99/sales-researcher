# Task 6.4: Finalize `docker-compose.yml`

**Phase:** Phase 6: Dockerization & Deployment Prep
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Finalize the `docker-compose.yml` file to orchestrate all services (frontend, backend API, Celery worker, Redis). This involves configuring networking, volume mounts for development, port mappings, and environment variable injection.

## 2. Detailed Steps / Implementation Notes

1.  **Review and Consolidate Services:**
    *   Combine the service definitions for `frontend`, `backend` (FastAPI app), `backend_worker` (Celery worker), and `redis` into a single `docker-compose.yml` file.
    *   Ensure the `backend` and `backend_worker` services both use the same `backend` image built from `backend/Dockerfile`.

2.  **Environment Variable Injection:**
    *   For local development, use `env_file` to load environment variables from `.env` files in the respective service directories. This keeps secrets out of `docker-compose.yml` itself.
    *   For production, environment variables would typically be injected directly by the deployment platform or via a secrets management system.
        ```yaml
        # Example: Using env_file for local development
        services:
          frontend:
            # ...
            env_file:
              - ./frontend/.env # For NEXT_PUBLIC_ variables
            # ...

          backend:
            # ...
            env_file:
              - ./backend/.env # For GOOGLE_CLIENT_ID, GEMINI_API_KEY, etc.
            # ...

          backend_worker:
            # ...
            env_file:
              - ./backend/.env # Same as backend, as it needs the same secrets
            # ...
        ```

3.  **Networking:**
    *   Docker Compose automatically creates a default network, allowing services to communicate by their service names (e.g., `backend` can reach `redis` at `redis:6379`).
    *   No explicit `networks` section is needed unless custom network configurations are desired.

4.  **Volumes:**
    *   **Development Volumes:** Use bind mounts (`./frontend:/app`, `./backend:/app`) for development to enable hot-reloading and easy code changes without rebuilding images.
    *   **Named Volumes:** Use named volumes (e.g., `redis_data`) for data persistence where needed.
        ```yaml
        # Example:
        volumes:
          # ...
          frontend:
            - ./frontend:/app
            - /app/node_modules # Important: to prevent host node_modules from overwriting container's
            - /app/.next # Persist .next folder if needed for dev
          backend:
            - ./backend:/app
          redis_data:
            driver: local
        ```

5.  **Port Mappings:**
    *   Map necessary ports to the host machine (e.g., `3000:3000` for frontend, `8000:8000` for backend API).
    *   Redis port `6379:6379` is optional for host exposure but useful for debugging.

6.  **Health Checks (Optional but Recommended for Production):**
    *   Add health checks to `frontend`, `backend`, and `redis` services to ensure they are truly ready before dependent services start or traffic is routed.
        ```yaml
        # Example:
        services:
          frontend:
            # ...
            healthcheck:
              test: ["CMD", "curl", "-f", "http://localhost:3000"] # Or a specific health endpoint
              interval: 30s
              timeout: 10s
              retries: 3
            # ...
          backend:
            # ...
            healthcheck:
              test: ["CMD", "curl", "-f", "http://localhost:8000/health"] # From Task 0.3
              interval: 30s
              timeout: 10s
              retries: 3
            # ...
          redis:
            # ...
            healthcheck:
              test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
              interval: 10s
              timeout: 5s
              retries: 5
            # ...
        ```

7.  **`docker-compose.yml` Full Example (Consolidated):**
    ```yaml
    version: '3.8'

    services:
      frontend:
        build:
          context: ./frontend
          dockerfile: Dockerfile
        ports:
          - "3000:3000"
        volumes:
          - ./frontend:/app
          - /app/node_modules # Don't overwrite node_modules in container
          - /app/.next # Persist .next folder if needed for dev
        env_file:
          - ./frontend/.env
        environment:
          - NODE_ENV=development # For Next.js dev server
        depends_on:
          backend:
            condition: service_healthy # Wait for backend to be healthy
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:3000"]
          interval: 30s
          timeout: 10s
          retries: 3

      backend:
        build:
          context: ./backend
          dockerfile: Dockerfile
        ports:
          - "8000:8000"
        volumes:
          - ./backend:/app
        env_file:
          - ./backend/.env
        environment:
          - PYTHONUNBUFFERED=1 # Ensure Python output is unbuffered
          - REDIS_URL=redis://redis:6379/0 # For Celery client in FastAPI app
        depends_on:
          redis:
            condition: service_healthy # Wait for Redis to be healthy
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
          interval: 30s
          timeout: 10s
          retries: 3

      backend_worker:
        build:
          context: ./backend
          dockerfile: Dockerfile
        command: celery -A backend.celery_app worker -l info -Q default -c 1 # Adjust queue, concurrency
        volumes:
          - ./backend:/app
        env_file:
          - ./backend/.env
        environment:
          - REDIS_URL=redis://redis:6379/0
          - CELERY_RESULTS_BACKEND_URL=redis://redis:6379/0
          - PYTHONUNBUFFERED=1
        depends_on:
          redis:
            condition: service_healthy # Worker needs Redis
          backend:
            condition: service_healthy # Worker might need backend for shared setup/config
        healthcheck:
          test: ["CMD", "celery", "-A", "backend.celery_app", "inspect", "ping"] # Check if worker is responsive
          interval: 30s
          timeout: 10s
          retries: 3

      redis:
        image: redis:alpine
        ports:
          - "6379:6379" # Expose Redis to host for debugging if needed
        volumes:
          - redis_data:/data # For Redis data persistence
        healthcheck:
          test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
          interval: 10s
          timeout: 5s
          retries: 5

    volumes:
      redis_data:
        driver: local
    ```

## 3. Expected Output / Deliverables
*   A complete and finalized `docker-compose.yml` file at the project root, orchestrating all services.

## 4. Dependencies
*   Task 0.2: Define Basic Docker Configuration (initial `docker-compose.yml`).
*   Task 6.1: Refine Frontend Dockerfile.
*   Task 6.2: Refine Backend Dockerfile.
*   Task 6.3: Refine Redis Docker Configuration.
*   Task 0.5: Environment Variable Management (for `.env` files).

## 5. Acceptance Criteria
*   `docker-compose.yml` is syntactically correct.
*   All services (frontend, backend, backend_worker, redis) are defined.
*   Environment variables are correctly loaded via `env_file`.
*   Port mappings are correct.
*   Volumes are correctly configured.
*   `depends_on` and `healthcheck` conditions are set for proper service startup order and health monitoring.
*   Running `docker-compose config` shows no errors.

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **`depends_on` vs. `healthcheck`:** `depends_on` only ensures startup order. `condition: service_healthy` ensures the dependent service is actually healthy before starting, which is more robust.
*   **Production Deployment:** While `docker-compose` is great for local development, for production, consider more robust orchestration tools like Kubernetes or cloud-specific container services.
*   **Environment Variables:** For production, avoid `env_file` and inject environment variables directly into the container definitions or use a secrets management system.
*   **Celery Worker Command:** The `command` for `backend_worker` assumes `celery_app.py` is directly in the `/app` directory of the container. Adjust `celery -A` if your Celery app is nested (e.g., `celery -A backend.celery_app`).
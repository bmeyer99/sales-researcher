# Task 6.3: Refine Redis Docker Configuration

**Phase:** Phase 6: Dockerization & Deployment Prep
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Ensure the Redis service is correctly configured in `docker-compose.yml`. This involves confirming the image, ports, and considering optional data persistence for the message broker and results backend.

## 2. Detailed Steps / Implementation Notes

1.  **Review `docker-compose.yml` for Redis Service:**
    *   The initial `docker-compose.yml` (from Task 0.2) already includes a Redis service using `redis:alpine`. This is a good choice for a lightweight image.
        ```yaml
        # Excerpt from docker-compose.yml
        services:
          # ...
          redis:
            image: redis:alpine
            ports:
              - "6379:6379" # Expose Redis to host for debugging if needed
            volumes:
              - redis_data:/data # Optional: for Redis data persistence

        volumes:
          redis_data:
            driver: local
        ```

2.  **Image Selection:**
    *   `redis:alpine` is generally preferred for production due to its small size. `redis:latest` or other tags might be larger. Stick with `redis:alpine` unless specific features from a larger image are required.

3.  **Port Mapping:**
    *   `ports: - "6379:6379"` maps the container's Redis port to the host's port. This is useful for local development and debugging (e.g., connecting with a Redis client from your host machine). For production deployments, this might not be necessary or desirable, as other services will connect to Redis via the Docker internal network.

4.  **Data Persistence (Optional but Recommended for Results Backend):**
    *   For Celery's message broker, Redis typically acts as a transient queue, so persistence isn't strictly necessary for the broker itself. If the Redis container restarts, pending messages might be lost (though Celery can be configured for message durability).
    *   However, if Redis is also used as the **Celery results backend**, then persistence becomes more important if you need to retrieve task results after a Redis restart.
    *   The `volumes: - redis_data:/data` line in `docker-compose.yml` already sets up a named volume for persistence. This means Redis data will be stored on the Docker host and persist across container restarts.
    *   Ensure the `redis_data` volume is defined at the top level of `docker-compose.yml`.

5.  **Configuration (Optional):**
    *   If specific Redis configurations are needed (e.g., memory limits, password protection), these can be provided via a `command` or `configs` section in `docker-compose.yml`, or by mounting a custom `redis.conf` file.
    *   **Password Protection:** For production, it's highly recommended to add password protection to Redis.
        ```yaml
        # Example with password (for production)
        redis:
          image: redis:alpine
          command: redis-server --requirepass ${REDIS_PASSWORD}
          environment:
            REDIS_PASSWORD: ${REDIS_PASSWORD} # Pass password as env var
          # ... other configs
        ```
        *   Then, the `REDIS_URL` for Celery and FastAPI would need to include the password: `redis://:password@redis:6379/0`.
        *   Add `REDIS_PASSWORD` to `backend/.env.example` and `frontend/.env.example` (if frontend needs it, though unlikely).

6.  **Health Check (Optional):**
    *   For production, adding a health check to the Redis service can help orchestrators ensure Redis is truly ready.
        ```yaml
        # Example Redis healthcheck
        redis:
          # ...
          healthcheck:
            test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
            interval: 10s
            timeout: 5s
            retries: 5
        ```

## 3. Expected Output / Deliverables
*   A `redis` service definition in `docker-compose.yml` that is robust for development and ready for production considerations.
*   Redis data persistence configured via a named volume.
*   (Optional but recommended) Password protection and health checks considered for production.

## 4. Dependencies
*   Task 0.2: Define Basic Docker Configuration (initial `docker-compose.yml`).
*   Task 3.1: Backend - Celery & Redis Setup (Celery's reliance on Redis).

## 5. Acceptance Criteria
*   The Redis service starts successfully when `docker-compose up redis` is run.
*   Other services (backend, Celery worker) can connect to Redis using the internal Docker network name (`redis`).
*   If persistence is enabled, Redis data survives container restarts.
*   (If implemented) Redis is password-protected and the health check passes.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   **Production Redis:** For high-availability production environments, a single Redis instance might not be sufficient. Consider Redis Sentinel or Redis Cluster for more robust setups, but this is beyond the scope of this project's initial plan.
*   **Security:** Always use strong, randomly generated passwords for Redis in production.
# Task 0.2: Define Basic Docker Configuration

**Phase:** Phase 0: Project Setup & Foundational Structure
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-28

## 1. Description
Create initial `docker-compose.yml` for frontend, backend, and Redis. Create basic `Dockerfile` for frontend (Next.js) and backend (Python/FastAPI). For Redis, the official `redis:alpine` image will be used directly in `docker-compose.yml`.

## 2. Detailed Steps / Implementation Notes

1.  **Create `docker-compose.yml` at the project root (`/root/sales-researcher/docker-compose.yml`):**
    *   This file will orchestrate the different services of the application.
    *   **Content:**
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
              - ./frontend:/app # For development, sync local changes
              - /app/node_modules # Don't overwrite node_modules in container
              - /app/.next # Persist .next folder if needed for dev
            environment:
              - NODE_ENV=development
            # depends_on:
            #   - backend # Enable if frontend needs backend during its build/startup

          backend:
            build:
              context: ./backend
              dockerfile: Dockerfile
            ports:
              - "8000:8000"
            volumes:
              - ./backend:/app # For development, sync local changes
            environment:
              # Example environment variables - will be properly managed via .env files later
              # - PYTHONUNBUFFERED=1
              # - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service_account.json
              # - GEMINI_API_KEY=YOUR_GEMINI_API_KEY
              - REDIS_URL=redis://redis:6379/0 # For Celery
            depends_on:
              - redis
            # The command to run the FastAPI app will be in the backend Dockerfile.
            # For Celery workers, we might override the command or have a separate service definition.

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

2.  **Create `frontend/Dockerfile` at (`/root/sales-researcher/frontend/Dockerfile`):**
    *   This file defines how to build the Next.js frontend image.
    *   It assumes Next.js with its standalone output feature for optimized production images.
    *   **Content:**
        ```dockerfile
        # Stage 1: Install dependencies
        FROM node:18-alpine AS deps
        WORKDIR /app

        # Copy package.json and lock file
        COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

        # Install dependencies based on the lock file found
        RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
            elif [ -f package-lock.json ]; then npm ci; \
            elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install --frozen-lockfile; \
            else echo "No lockfile found. Please add one." && exit 1; fi

        # Stage 2: Build the application
        FROM node:18-alpine AS builder
        WORKDIR /app
        COPY --from=deps /app/node_modules ./node_modules
        COPY . .

        ENV NEXT_TELEMETRY_DISABLED 1
        RUN npm run build # Or: yarn build / pnpm build

        # Stage 3: Production image (using Next.js standalone output)
        FROM node:18-alpine AS runner
        WORKDIR /app

        ENV NODE_ENV production
        ENV NEXT_TELEMETRY_DISABLED 1

        RUN addgroup --system --gid 1001 nodejs
        RUN adduser --system --uid 1001 nextjs

        COPY --from=builder /app/public ./public
        COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
        COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

        USER nextjs
        EXPOSE 3000
        ENV PORT 3000
        CMD ["node", "server.js"]
        ```
    *   *Note: Files like `package.json` will be created in Task 0.4.*

3.  **Create `backend/Dockerfile` at (`/root/sales-researcher/backend/Dockerfile`):**
    *   This file defines how to build the Python/FastAPI backend image.
    *   It assumes a `main.py` for the FastAPI app and `requirements.txt` for dependencies.
    *   **Content:**
        ```dockerfile
        FROM python:3.10-slim

        WORKDIR /app

        ENV PYTHONDONTWRITEBYTECODE 1
        ENV PYTHONUNBUFFERED 1

        # System dependencies can be installed here if needed by Python packages
        # RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # If using Poetry:
        # COPY pyproject.toml poetry.lock* ./
        # RUN pip install poetry
        # RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

        COPY . .

        EXPOSE 8000
        # Assumes your FastAPI app instance is in 'main.py' and named 'app'.
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        ```
    *   *Note: `main.py` and `requirements.txt` will be set up in Task 0.3.*

## 3. Expected Output / Deliverables
*   `docker-compose.yml` file created in the project root.
*   `frontend/Dockerfile` file created in the `frontend` directory.
*   `backend/Dockerfile` file created in the `backend` directory.

## 4. Dependencies
*   Task 0.1: Initialize Project Repository (for directory structure).

## 5. Acceptance Criteria
*   The three files (`docker-compose.yml`, `frontend/Dockerfile`, `backend/Dockerfile`) exist in their specified locations.
*   The content of each file matches the proposed content.
*   Running `docker-compose config` (once placeholder files like `frontend/package.json` and `backend/requirements.txt` are added in later tasks) should validate the `docker-compose.yml` syntax.
*   Attempting to build the images with `docker-compose build` (again, after placeholder app files are added) should not immediately fail due to Dockerfile syntax errors (though they won't fully build until app code is present).

## 6. Estimated Effort (Optional)
*   Small (for file creation and content pasting)

## 7. Notes / Questions
*   The Dockerfiles are structured for development and production builds (especially the frontend one).
*   Environment variables are mentioned but will be fully managed with `.env` files in Task 0.5.
*   The `depends_on` in `docker-compose.yml` helps manage startup order.
*   Celery worker configuration within Docker Compose will be an extension of the `backend` service or a new service definition later when Celery is implemented.
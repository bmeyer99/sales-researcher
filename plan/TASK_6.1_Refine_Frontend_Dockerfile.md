# Task 6.1: Refine Frontend Dockerfile

**Phase:** Phase 6: Dockerization & Deployment Prep
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Refine the `frontend/Dockerfile` (initially created in Task 0.2) to optimize it for production builds of the Next.js application. This includes using multi-stage builds for smaller image sizes and ensuring proper environment configuration.

## 2. Detailed Steps / Implementation Notes

1.  **Review Existing Dockerfile:**
    *   The `frontend/Dockerfile` from Task 0.2 already uses a multi-stage build approach, which is excellent for production optimization.
    *   It includes stages for `deps`, `builder`, and `runner`.
    *   It leverages Next.js's standalone output feature (`.next/standalone`), which is the recommended way to deploy Next.js applications in Docker for minimal image size.

2.  **Ensure Production Best Practices:**
    *   **Non-root User:** The Dockerfile already includes creating and switching to a non-root user (`nextjs`), which is a security best practice.
    *   **Environment Variables:**
        *   `NODE_ENV=production` is set in the `runner` stage.
        *   `NEXT_TELEMETRY_DISABLED=1` is set to disable Next.js telemetry during build and runtime.
        *   Ensure any `NEXT_PUBLIC_` environment variables required at runtime are passed into the container (e.g., via `docker-compose.yml` or deployment platform).
    *   **Dependencies:** The `deps` stage correctly copies `package.json` and lock files to install dependencies. Ensure `npm ci` (or `yarn install --frozen-lockfile`) is used for clean installs.
    *   **Build Command:** `npm run build` is used in the `builder` stage. Ensure the `build` script in `package.json` is correctly defined.
    *   **Port Exposure:** `EXPOSE 3000` and `ENV PORT 3000` are correctly set.
    *   **CMD:** `CMD ["node", "server.js"]` is correct for standalone output.

3.  **Potential Minor Adjustments/Considerations:**
    *   **Caching:** Docker layers are used for caching. Ensure `COPY package.json ...` comes before `RUN ... install` to maximize layer caching for dependencies.
    *   **Health Checks (for production deployment):** For production environments, consider adding a `HEALTHCHECK` instruction to the Dockerfile to allow orchestrators (like Kubernetes) to determine if the container is healthy.
        ```dockerfile
        # Add to the runner stage
        HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD node -e "require('./server.js')" || exit 1
        # Or a more robust check if a health endpoint is exposed by Next.js app
        # HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3000/api/health || exit 1
        ```
        *(Note: Next.js doesn't expose a default health endpoint, so a simple `node -e` check or a custom health endpoint in your app would be needed for `curl`)*.
    *   **`.dockerignore`:** Ensure a `.dockerignore` file exists in the `frontend` directory to prevent unnecessary files (like `node_modules` from local development, `.git`, `dist`, `build` folders) from being copied into the build context, which speeds up builds.
        ```
        # frontend/.dockerignore
        node_modules
        .git
        .next/
        out/
        build/
        dist/
        .env
        .env.local
        .env.*.local
        ```

## 3. Expected Output / Deliverables
*   A production-ready `frontend/Dockerfile` that is optimized for size and security.
*   An optional `frontend/.dockerignore` file to improve build performance.

## 4. Dependencies
*   Task 0.2: Define Basic Docker Configuration (initial `frontend/Dockerfile`).
*   Task 0.4: Setup Frontend (Next.js) - Basic Structure (ensures `package.json` and build scripts are present).

## 5. Acceptance Criteria
*   The `frontend/Dockerfile` uses multi-stage builds.
*   The final image size is minimized.
*   The application runs as a non-root user inside the container.
*   The Dockerfile correctly builds the Next.js application for production.
*   `docker-compose build frontend` completes successfully.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   **Image Size:** The standalone output feature of Next.js is key to small image sizes.
*   **Build Time:** Proper `.dockerignore` and caching strategies (layering in Dockerfile) are important for faster rebuilds.
*   **Deployment Environment:** Specific deployment platforms (e.g., Vercel, AWS Amplify, Kubernetes) might have their own recommended ways to build and deploy Next.js apps, but this Dockerfile provides a generic, robust solution.
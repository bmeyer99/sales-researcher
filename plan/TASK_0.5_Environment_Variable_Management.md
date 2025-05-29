# Task 0.5: Environment Variable Management

**Phase:** Phase 0: Project Setup & Foundational Structure
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-28

## 1. Description
Define the structure and create example files for managing environment variables for both frontend and backend services. This involves creating `.env.example` files and documenting the required variables. Actual secrets will not be stored in the repository.

## 2. Detailed Steps / Implementation Notes

1.  **Backend Environment Variables (`backend/.env.example`):**
    *   Create a file named `.env.example` in the `/root/sales-researcher/backend/` directory.
    *   This file will serve as a template for the actual `.env` file (which should be gitignored).
    *   **Content for `backend/.env.example`:**
        ```env
        # Backend API Configuration
        # PYTHONUNBUFFERED=1 # Already set in Dockerfile, but can be here for local dev consistency
        # HOST=0.0.0.0
        # PORT=8000

        # Redis Configuration (for Celery)
        REDIS_URL=redis://redis:6379/0 # For Docker Compose
        # REDIS_URL_LOCAL=redis://localhost:6379/0 # For local development if Redis runs on host

        # Google OAuth Credentials
        # These will be obtained from Google Cloud Console
        GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID"
        GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET"
        # Redirect URI for OAuth callback - ensure this matches Google Cloud Console and frontend requests
        # Example: http://localhost:8000/auth/google/callback (for backend handling)
        # Example: http://localhost:3000/auth/google/callback (if frontend handles part of it before backend)
        GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback" # Adjust as per auth flow

        # Gemini API Key
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

        # Google Application Credentials (if using a service account for some GDrive operations - less likely for user-specific Drive access)
        # GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json" # Path within the container if used

        # Secret key for signing JWTs or session data (if applicable)
        # SECRET_KEY="your-very-secret-random-string"

        # CORS Origins (if frontend and backend are on different ports/domains during development)
        # FRONTEND_URL="http://localhost:3000"
        # ALLOWED_ORIGINS="http://localhost:3000,https://your-production-domain.com"
        ```

2.  **Frontend Environment Variables (`frontend/.env.example`):**
    *   Create a file named `.env.example` in the `/root/sales-researcher/frontend/` directory.
    *   Next.js uses specific prefixes for environment variables to be exposed to the browser (`NEXT_PUBLIC_`).
    *   **Content for `frontend/.env.example`:**
        ```env
        # Next.js specific variables (exposed to the browser)
        NEXT_PUBLIC_GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID_FOR_FRONTEND" # Often the same as backend, but can be different if using different OAuth clients
        NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api" # For API calls to the backend in development
        # NEXT_PUBLIC_API_BASE_URL_PROD="https://your-production-api-domain.com/api" # For production

        # Other public variables if needed
        # NEXT_PUBLIC_FEATURE_FLAG_XYZ="true"
        ```
    *   *Note: `YOUR_GOOGLE_CLIENT_ID_FOR_FRONTEND` is typically the same client ID used for the backend if the OAuth flow is initiated from the frontend and completed by the backend.*

3.  **Update Root `.gitignore`:**
    *   Ensure that actual `.env` files are ignored by Git. The pattern `*.env` should already be in the root `.gitignore` from Task 0.1. Verify this.
        ```gitignore
        # ... other ignores ...
        *.env
        backend/.env
        frontend/.env
        # ... other ignores ...
        ```
    *   It's good practice to be explicit for subdirectories too, although `*.env` at the root should cover them.

4.  **Documentation:**
    *   Briefly document in the main `README.md` (to be created/updated in Phase 7) how to use these `.env.example` files:
        *   Copy `.env.example` to `.env` in respective directories (`frontend`, `backend`).
        *   Fill in the actual values in the `.env` files.
        *   These `.env` files are for local development. For Docker deployment, environment variables will typically be injected directly into the containers (e.g., via `docker-compose.yml` `environment` section or platform-specific configuration).

## 3. Expected Output / Deliverables
*   `backend/.env.example` file created with placeholder environment variables.
*   `frontend/.env.example` file created with placeholder environment variables.
*   Verification that `*.env` (and specific `backend/.env`, `frontend/.env`) are correctly listed in the root `.gitignore`.

## 4. Dependencies
*   Task 0.1: Initialize Project Repository (for the `.gitignore` file and directory structure).

## 5. Acceptance Criteria
*   `backend/.env.example` exists and contains the defined template.
*   `frontend/.env.example` exists and contains the defined template.
*   The root `.gitignore` correctly ignores `*.env` files.
*   Attempting to commit `.env` files (if created locally for testing) should show them as ignored by Git.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   The actual values for secrets (API keys, client secrets) must never be committed to the repository.
*   For Docker, environment variables can be passed in multiple ways:
    *   Using an `env_file` property in `docker-compose.yml` (e.g., `env_file: ./backend/.env`).
    *   Directly in the `environment` block in `docker-compose.yml`.
    *   Through the deployment platform's secret management.
    *   The `.env.example` files primarily guide local development setup.
*   The `GOOGLE_CLIENT_ID` might be the same for both frontend and backend, or you might configure separate OAuth clients in Google Cloud Console for more granular control. For this project, starting with one is likely sufficient.
*   `NEXT_PUBLIC_` prefix is crucial for Next.js to expose variables to the browser-side bundle.
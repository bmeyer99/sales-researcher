# Task 1.1: Backend - Google OAuth Configuration

**Phase:** Phase 1: Authentication (Google OAuth 2.0)
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Integrate `google-auth-oauthlib` into the backend. Configure the application to use the existing Google Cloud OAuth 2.0 credentials (Client ID, Client Secret) for user authentication and obtaining tokens for Google Drive API access.

## 2. Detailed Steps / Implementation Notes

1.  **Add Dependency:**
    *   Add `google-auth-oauthlib` to the `backend/requirements.txt` file.
        ```txt
        # backend/requirements.txt
        # ... other dependencies
        google-auth-oauthlib>=0.8.0,<1.3.0
        # ...
        ```
    *   Ensure it's installed in the local virtual environment (if used) and will be installed in the Docker image.

2.  **Environment Variable Integration:**
    *   The Google Client ID and Client Secret (already configured by the user on Google Cloud) need to be securely accessed by the backend.
    *   These should be defined in the `backend/.env` file (for local development) and injected as environment variables in Docker.
    *   Refer to `plan/TASK_0.5_Environment_Variable_Management.md` for the structure.
    *   Required variables in `backend/.env.example` (and to be set in `.env`):
        ```env
        GOOGLE_CLIENT_ID="YOUR_PRECONFIGURED_GOOGLE_CLIENT_ID"
        GOOGLE_CLIENT_SECRET="YOUR_PRECONFIGURED_GOOGLE_CLIENT_SECRET"
        GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback" # Or as configured in Google Cloud Console for your app
        ```
    *   The `GOOGLE_REDIRECT_URI` must exactly match one of the "Authorized redirect URIs" in your Google Cloud OAuth 2.0 client configuration.

3.  **Backend Configuration Module (Conceptual):**
    *   Create a configuration module or use a settings object within the backend (e.g., `backend/core/config.py`) to load these environment variables.
        ```python
        # Example: backend/core/config.py
        import os
        from dotenv import load_dotenv

        load_dotenv() # Loads variables from .env file if present

        class Settings:
            GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
            GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
            GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")
            # Add other settings as needed
            # Example: SECRET_KEY for session management or JWTs
            # SECRET_KEY: str = os.getenv("SECRET_KEY", "a-default-secret-key-for-dev-only")

            # Define necessary OAuth scopes
            GOOGLE_OAUTH_SCOPES: list[str] = [
                "openid", # For basic profile info (sub, email, name, picture)
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/drive.file" # To create folders and upload files
                # Add "https://www.googleapis.com/auth/drive.readonly" if picker needs to list files/folders
            ]

        settings = Settings()

        # Ensure critical settings are present
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set.")
        ```
    *   This `settings` object can then be imported and used throughout the backend application where OAuth configuration is needed.

4.  **OAuth Flow Considerations:**
    *   The application will use the Authorization Code Grant flow with PKCE (Proof Key for Code Exchange) if possible, as it's more secure for web applications. `google-auth-oauthlib` supports this.
    *   The backend will handle the token exchange.

## 3. Expected Output / Deliverables
*   `google-auth-oauthlib` added to `backend/requirements.txt`.
*   Clear documentation/confirmation in this task file on which environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`) are required for the backend.
*   A conceptual or actual Python module (e.g., `backend/core/config.py`) that loads and provides these OAuth settings and defined scopes to the application.

## 4. Dependencies
*   Task 0.3: Setup Backend (FastAPI) - Basic Structure
*   Task 0.5: Environment Variable Management

## 5. Acceptance Criteria
*   The backend application can successfully load the `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` from environment variables.
*   The defined Google OAuth scopes are correctly listed in the configuration.
*   The application does not crash on startup due to missing OAuth configuration (assuming `.env` is properly set up for local testing).

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   The user has confirmed Google Cloud side configuration is complete. This task focuses on integrating those pre-existing credentials into the application.
*   The `GOOGLE_REDIRECT_URI` is critical and must match the Google Cloud Console setup. For development, `http://localhost:8000/auth/google/callback` is typical if the backend handles the callback directly.
*   Scopes should be minimal but sufficient for the application's needs (login, email/profile info, Drive access).
*   Session management or JWTs will be needed to maintain user authentication state after login; this will be part of Task 1.2.
# Task 2.1: Backend - Google Drive API Client Setup

**Phase:** Phase 2: Google Drive Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Integrate the `google-api-python-client` library into the backend to interact with the Google Drive API. Configure the necessary OAuth scopes for Google Drive operations (e.g., creating folders, uploading files) using the user's authenticated credentials.

## 2. Detailed Steps / Implementation Notes

1.  **Add Dependency:**
    *   Add `google-api-python-client` to the `backend/requirements.txt` file.
        ```txt
        # backend/requirements.txt
        # ... other dependencies
        google-api-python-client>=2.50.0,<2.123.0
        # ...
        ```
    *   Ensure it's installed in the local virtual environment (if used) and will be installed in the Docker image.
    *   Note: `google-auth-oauthlib` and `google-auth-httplib2` are often installed as dependencies of this client, which is helpful.

2.  **Confirm OAuth Scopes:**
    *   The necessary scopes for Google Drive should already be defined in the `backend/core/config.py` (from Task 1.1) as part of `GOOGLE_OAUTH_SCOPES`.
    *   Ensure `https://www.googleapis.com/auth/drive.file` is included. This scope allows:
        *   Creating new files and folders.
        *   Modifying files and folders created by the application.
        *   It does *not* grant broad access to all user's Drive files, only those the app creates or is explicitly given access to.
    *   If the Google Drive Picker API is used later (Task 2.4 Option B) and needs to list existing folders, `https://www.googleapis.com/auth/drive.readonly` or a more permissive Drive scope might be needed, but `drive.file` is a good start for outputting files.

3.  **Google Drive Service Utility:**
    *   Create a utility function or class in the backend (e.g., `backend/services/google_drive_service.py`) to encapsulate Google Drive interactions.
    *   This service will need access to the user's authenticated Google credentials (access token).
    *   **Getting Credentials:**
        *   The user's access token (and refresh token logic) should be managed by the authentication system (Phase 1).
        *   When a Drive operation is needed, the backend should retrieve the current valid access token for the user.
        *   Create a `google.oauth2.credentials.Credentials` object using the user's access token (and potentially refresh token, client ID, client secret for refresh capabilities if not handled by a higher-level auth object).
            ```python
            # Example within a backend request handler or service method
            # Assume 'user_access_token' is retrieved from the user's session or auth context
            # Assume 'user_refresh_token', 'settings.GOOGLE_CLIENT_ID', 'settings.GOOGLE_CLIENT_SECRET' are available if refresh is handled here
            
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            # from backend.core.config import settings # Import your app settings

            def get_drive_service(user_access_token: str, user_refresh_token: str = None):
                creds = Credentials(
                    token=user_access_token,
                    # refresh_token=user_refresh_token, # If available and refresh is needed
                    # token_uri='https://oauth2.googleapis.com/token',
                    # client_id=settings.GOOGLE_CLIENT_ID,
                    # client_secret=settings.GOOGLE_CLIENT_SECRET,
                    # scopes=settings.GOOGLE_OAUTH_SCOPES # Ensure scopes match what token was granted for
                )

                # It's often better to use a Credentials object that can auto-refresh,
                # built during the OAuth flow (see google-auth library examples).
                # This simplified example assumes a valid access_token is provided.
                # Refresh logic (Task 1.5) should ensure this token is valid or can be refreshed.

                try:
                    drive_service = build('drive', 'v3', credentials=creds, static_discovery=False)
                    return drive_service
                except Exception as e:
                    print(f"Error building Drive service: {e}") # Handle appropriately
                    return None
            ```
    *   **Using the Service:** The `drive_service` object returned by `build()` is used to make API calls (e.g., `drive_service.files().create(...)`).

4.  **Error Handling:**
    *   Implement robust error handling for API calls (e.g., network issues, permission errors, rate limits).
    *   The Google API client library will raise specific exceptions.

## 3. Expected Output / Deliverables
*   `google-api-python-client` added to `backend/requirements.txt`.
*   A backend utility/service module (e.g., `backend/services/google_drive_service.py`) that provides a way to get an initialized Google Drive API service client using the user's OAuth credentials.
*   Confirmation that the necessary `drive.file` scope is included in the OAuth configuration.

## 4. Dependencies
*   Task 1.1: Backend - Google OAuth Configuration (defines scopes and provides credentials).
*   Task 1.5: Token Refresh Mechanism (ensures the access token used for Drive is valid or can be refreshed).

## 5. Acceptance Criteria
*   The backend application can successfully initialize the Google Drive API service client using a valid user access token.
*   Attempting to use the service client (e.g., a simple metadata fetch, if possible without creating files yet) with valid credentials works.
*   Attempting with invalid/expired credentials (before refresh logic is fully in place for this specific call) should result in an authentication error from the Google API, which should be gracefully handled or logged.

## 6. Estimated Effort (Optional)
*   Small to Medium (initial setup is straightforward, but integrating with auth and refresh logic adds complexity).

## 7. Notes / Questions
*   The `static_discovery=False` in `build('drive', 'v3', ..., static_discovery=False)` can be important in some environments to avoid issues with discovering the API. For production, consider bundling the discovery document if preferred.
*   Focus on using the user's credentials obtained via OAuth. Service accounts are generally not suitable for accessing a user's personal Drive folder unless explicitly shared with the service account email.
*   The Google Drive API version is 'v3'.
*   This task sets up the client; subsequent tasks (2.2, 2.3) will implement specific Drive operations like folder creation and file upload.
# Task 1.5: Token Refresh Mechanism (Backend/Frontend)

**Phase:** Phase 1: Authentication (Google OAuth 2.0)
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Implement logic to handle Google OAuth access token expiration and refresh them using the refresh token. This is crucial for maintaining user sessions and allowing the backend to make Google API calls on behalf of the user over extended periods.

## 2. Detailed Steps / Implementation Notes

**Backend Responsibilities (Primary Focus):**

1.  **Secure Storage of Refresh Token:**
    *   When the user first authenticates (Task 1.2), if `access_type='offline'` was requested, Google provides a refresh token along with the access token.
    *   The refresh token is long-lived (or until revoked) and MUST be stored securely by the backend, associated with the user account (e.g., in a database, encrypted).
    *   **Do NOT send the refresh token to the frontend.**

2.  **Access Token Management:**
    *   The access token obtained initially is short-lived (typically 1 hour).
    *   The backend should store the access token and its expiry time, perhaps in the user's session or an in-memory cache associated with the session.

3.  **Detecting Expired Access Token:**
    *   Before making a Google API call on behalf of the user, the backend should check if the stored access token is expired or close to expiring.
    *   Alternatively, if a Google API call fails with an "invalid_grant" or "expired_token" error, this indicates the access token needs refreshing.

4.  **Implement Token Refresh Logic:**
    *   Create a backend utility function or method to refresh the access token.
    *   This function will use the `google-auth` library (specifically `google.oauth2.credentials.Credentials` or similar).
    *   **Steps:**
        *   Retrieve the user's stored refresh token.
        *   Create `google.oauth2.credentials.Credentials` object using the stored refresh token, client ID, client secret, and token URI (`https://oauth2.googleapis.com/token`).
        *   Call the `credentials.refresh(google.auth.transport.requests.Request())` method.
        *   This will make a request to Google's token endpoint and return a new access token (and potentially a new ID token, though the refresh token itself usually doesn't change unless explicitly rotated).
        *   Update the stored access token and its new expiry time for the user.
        *   If the refresh attempt fails (e.g., refresh token revoked, invalid client), the user needs to re-authenticate. Invalidate their session and prompt for login.

5.  **Integration with Google API Calls:**
    *   Wrap Google API calls in a helper that automatically handles token refresh.
    *   When a Google API client (e.g., for Drive or Gemini if it uses user OAuth) is initialized, it should use credentials that can auto-refresh or be manually refreshed.
    *   The `google-api-python-client` can often work with `google.oauth2.credentials.Credentials` objects that handle refresh.

**Frontend Responsibilities (Minimal in this context if backend handles API calls):**

1.  **Handling 401/Session Expiry from Backend:**
    *   If the backend determines that even the refresh token is invalid (or the user's session has truly expired beyond refresh capabilities), API calls from the frontend to the backend will start failing with a 401 Unauthorized status.
    *   The frontend's API client/wrapper (e.g., a custom fetch wrapper) should detect these 401 responses.
    *   Upon detecting a 401 that signifies a need for re-authentication, the frontend should:
        *   Call the `logout()` action in the `authStore` (from Task 1.4).
        *   Redirect the user to the `/login` page.

**If JWTs are issued by the backend to the frontend:**

*   If the backend issues its own access and refresh tokens (JWTs) to the frontend to manage the session with the backend API itself (separate from Google's tokens):
    *   **Backend:** Needs an endpoint (e.g., `/auth/token/refresh`) that accepts the backend's refresh JWT and issues a new backend access JWT.
    *   **Frontend:**
        *   Store both backend access JWT and backend refresh JWT securely (e.g., access token in memory/Zustand, refresh token in HttpOnly cookie or secure storage).
        *   When an API call to the backend fails with a 401 due to an expired backend access JWT, the frontend automatically calls the backend's `/auth/token/refresh` endpoint with the backend refresh JWT.
        *   If successful, update the backend access JWT and retry the original API call.
        *   If refresh fails, log the user out.
    *   *This is about frontend-backend session, distinct from backend-Google session.* The primary concern of *this task* is the backend refreshing *Google's* access token.

## 3. Expected Output / Deliverables
*   **Backend:**
    *   Mechanism for securely storing Google refresh tokens associated with users.
    *   Logic to detect expired Google access tokens.
    *   A function/method to refresh Google access tokens using the stored refresh token.
    *   Google API calls made by the backend are resilient to access token expiry.
*   **Frontend:**
    *   Ability to detect 401 errors from backend API calls that signify a complete session invalidation (Google refresh token failed).
    *   Logic to log out the user and redirect to login when such 401 errors occur.

## 4. Dependencies
*   Task 1.2: Backend - OAuth Endpoints (obtaining the initial refresh token).
*   Task 1.4: Frontend - Token Handling & Authenticated State (for frontend logout).
*   Secure storage mechanism for refresh tokens on the backend (e.g., database).

## 5. Acceptance Criteria
*   **Backend:**
    *   When a Google access token expires, the backend automatically refreshes it using the stored refresh token before making a Google API call.
    *   If a Google refresh token is invalid or revoked, the backend correctly identifies this, invalidates the user's session, and subsequent API calls requiring authentication from that user fail appropriately (e.g., leading to a 401 for the frontend).
*   **Frontend:**
    *   If backend API calls consistently return 401 (signifying session/refresh token failure), the user is logged out and redirected to the login page.

## 6. Estimated Effort (Optional)
*   Medium (Backend logic for refresh and secure storage can be intricate).

## 7. Notes / Questions
*   **Security of Refresh Tokens:** This is paramount. Refresh tokens grant long-term access and must be protected against theft. Encrypt them at rest.
*   **Google API Client Library:** Leverage the capabilities of `google-auth` and `google-api-python-client` as they often have built-in support or hooks for token refresh.
*   **User Experience:** The refresh process should be seamless to the user. They should not be aware that tokens are being refreshed in the background unless the refresh token itself fails, requiring re-login.
*   **Distinction:** Clearly distinguish between refreshing Google's OAuth tokens (backend's job for calling Google APIs) and potentially refreshing the application's own session tokens (e.g., JWTs between frontend and backend). This task primarily focuses on the former.
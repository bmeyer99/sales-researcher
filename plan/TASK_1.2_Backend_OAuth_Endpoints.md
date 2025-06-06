# Task 1.2: Backend - OAuth Endpoints

**Phase:** Phase 1: Authentication (Google OAuth 2.0)
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Implement the backend API endpoints required for the Google OAuth 2.0 flow. This includes:
*   `/auth/google/login`: Initiates the OAuth flow by redirecting the user to Google's consent screen.
*   `/auth/google/callback`: Handles the callback from Google after user authentication, exchanges the authorization code for tokens, retrieves user information, and establishes a session or issues a token to the client.

## 2. Detailed Steps / Implementation Notes

1.  **Setup FastAPI Router:**
    *   Create a new router for authentication-related endpoints, e.g., `backend/api/v1/auth.py`.
    *   Import necessary modules: `FastAPI`, `APIRouter`, `RedirectResponse`, `Request` from `fastapi`.
    *   Import `Flow` from `google_auth_oauthlib.flow`.
    *   Import `google.oauth2.id_token` and `google.auth.transport.requests` for ID token verification.
    *   Import the `settings` object from `backend/core/config.py` (created in Task 1.1).

2.  **Implement `/auth/google/login` Endpoint:**
    *   This endpoint will construct the Google OAuth2 authorization URL and redirect the user.
    *   **Steps:**
        *   Initialize `google_auth_oauthlib.flow.Flow` with `client_id`, `client_secret` from `settings`, and the defined `scopes`.
        *   Set the `redirect_uri` for the flow to `settings.GOOGLE_REDIRECT_URI`.
        *   Generate the authorization URL using `flow.authorization_url()`.
            *   Include `access_type='offline'` to get a refresh token.
            *   Include `prompt='consent'` if you want to ensure the user is prompted for consent every time (useful for development, might remove for production for smoother UX if refresh tokens are handled well).
            *   Implement PKCE: Generate a `code_verifier` and `code_challenge`. Store the `code_verifier` in the user's session (or a secure temporary store keyed by `state`) and pass the `code_challenge` and `code_challenge_method='S256'` to `authorization_url()`.
            *   Store the `state` parameter (generated by the library or manually) in the session to prevent CSRF attacks.
        *   Return a `RedirectResponse` to the generated authorization URL.
    *   **Session Management:**
        *   FastAPI doesn't have built-in session management like Flask/Django. Consider using a library like `Starlette-Session` or `fastapi-sessions` for server-side sessions (e.g., stored in Redis or a secure cookie). This is needed to store `state` and `pkce_code_verifier`.
        *   Alternatively, if aiming for a stateless backend with JWTs, the `state` and `pkce_code_verifier` might need to be handled differently, perhaps by encoding them into a short-lived state token passed back to the frontend and then submitted with the callback. Server-side session is generally simpler for OAuth state handling.

3.  **Implement `/auth/google/callback` Endpoint:**
    *   This endpoint handles the redirect from Google.
    *   **Steps:**
        *   Retrieve `code` and `state` from the query parameters.
        *   Verify the `state` parameter against the value stored in the session to prevent CSRF.
        *   Retrieve the `pkce_code_verifier` from the session.
        *   Initialize `google_auth_oauthlib.flow.Flow` similarly to the login endpoint.
        *   Fetch the token using `flow.fetch_token(code=code, code_verifier=pkce_code_verifier)`. This will exchange the authorization code for an access token, refresh token (if `access_type='offline'` was used), and ID token.
        *   **Verify ID Token:**
            *   Use `google.oauth2.id_token.verify_oauth2_token()` to verify the ID token. Pass the ID token, `google.auth.transport.requests.Request()`, and `settings.GOOGLE_CLIENT_ID`.
            *   This step validates the token's signature, audience, and issuer, and extracts user information (like email, name, sub).
        *   **User Management (Conceptual):**
            *   At this point, you have authenticated user information (e.g., email from ID token).
            *   Decide how to handle users:
                *   Look up user in your database by email.
                *   If user doesn't exist, create a new user record.
                *   Store/update Google OAuth tokens (especially the refresh token, if obtained) securely associated with the user account if long-term API access on their behalf is needed beyond the session. Access tokens are short-lived.
        *   **Establish Session / Issue Token:**
            *   Store relevant user information (e.g., user ID, email, name) and the access token (and its expiry) in the user's session.
            *   Alternatively, if using JWTs, generate a JWT containing user claims and return it to the frontend.
        *   Redirect the user to a frontend URL (e.g., main dashboard: `http://localhost:3000/dashboard` or a specific success page). The redirect URL could be configurable.

4.  **Error Handling:**
    *   Implement robust error handling for both endpoints (e.g., if Google returns an error, if state mismatch, token verification fails).
    *   Redirect to an error page on the frontend or return an appropriate JSON error response.

## 3. Expected Output / Deliverables
*   Functional `/auth/google/login` endpoint in the backend that redirects to Google's consent screen.
*   Functional `/auth/google/callback` endpoint that:
    *   Handles the callback from Google.
    *   Exchanges the authorization code for tokens.
    *   Verifies the ID token and extracts user information.
    *   Establishes an authenticated session for the user (e.g., via secure cookie or by providing a JWT).
    *   Redirects the user to a designated frontend page upon successful authentication.
*   Appropriate session management (e.g., using `Starlette-Session` with Redis or secure cookies) to store OAuth state and user session data.

## 4. Dependencies
*   Task 1.1: Backend - Google OAuth Configuration (requires `settings` with client ID, secret, redirect URI, scopes).
*   A session management solution for FastAPI (e.g., `Starlette-Session` or `fastapi-sessions`).

## 5. Acceptance Criteria
*   Navigating to `/auth/google/login` redirects the user to Google's authentication page.
*   After successful Google authentication, the user is redirected back to `/auth/google/callback`.
*   The callback endpoint successfully exchanges the code for tokens.
*   The ID token is successfully verified.
*   User information is extracted from the ID token.
*   An authenticated session is established (e.g., a session cookie is set, or a JWT is issued).
*   The user is redirected to the specified frontend page after successful login.
*   CSRF protection (via `state` parameter) is functional.
*   PKCE flow is correctly implemented.
*   Errors during the OAuth flow are handled gracefully (e.g., user denies access, invalid code).

## 6. Estimated Effort (Optional)
*   Medium to Large (OAuth flows can be complex to implement correctly and securely)

## 7. Notes / Questions
*   **Security:** Storing tokens (especially refresh tokens) must be done securely. If storing in a database, ensure they are encrypted. Access tokens can be stored in the session.
*   **Session Middleware:** If using server-side sessions, ensure the session middleware is correctly configured in FastAPI (e.g., `Starlette-SessionMiddleware`).
*   **PKCE is highly recommended** over the implicit flow for web server applications.
*   The exact mechanism for "establishing a session" (session cookies vs. JWTs) needs to be decided. Session cookies are often simpler for web apps, while JWTs are common for SPAs talking to APIs. Given Next.js, either could work, but server-side sessions managed by the backend might be more straightforward for handling the OAuth tokens initially.
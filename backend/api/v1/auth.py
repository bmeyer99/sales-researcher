from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
from core.config import settings
from db.user_store import create_or_update_user, get_user, delete_user
import secrets
import urllib.parse
import hashlib
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# This is a placeholder for session management. In a real application, you'd configure
# SessionMiddleware in your main FastAPI app (main.py) and potentially use a
# server-side session store (e.g., Redis) for production.
# For now, we'll assume session is available via request.session.


@router.get(
    "/google/login",
    summary="Initiate Google OAuth2 Login",
    description="Redirects the user to Google's consent screen to initiate the OAuth2 authentication flow. A PKCE code verifier and state are generated and stored in the session for security.",
)
async def google_login(request: Request):
    session = request.session

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "project_id": settings.GOOGLE_PROJECT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "javascript_origins": [settings.FRONTEND_URL],
            }
        },
        scopes=settings.GOOGLE_SCOPES.split(),  # Use the property from settings
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

    # Generate PKCE code verifier and challenge
    code_verifier = secrets.token_urlsafe(96)
    code_challenge = urllib.parse.quote_plus(
        hashlib.sha256(code_verifier.encode("utf-8")).digest().hex()
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # Ensure refresh token is issued
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )

    # Store state and code_verifier in session for verification in callback
    session["oauth_state"] = state
    session["pkce_code_verifier"] = code_verifier

    return RedirectResponse(authorization_url)


@router.get(
    "/google/callback",
    summary="Google OAuth2 Callback",
    description="Handles the redirect from Google after successful user authentication. Exchanges the authorization code for access and refresh tokens, verifies the ID token, retrieves user information, and stores user data in the database. Redirects to the frontend dashboard upon success.",
)
async def google_callback(request: Request, code: str, state: str):
    session = request.session

    # Verify state to prevent CSRF attacks
    if state != session.get("oauth_state"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State mismatch. Possible CSRF attack.",
        )

    # Retrieve PKCE code verifier from session
    pkce_code_verifier = session.get("pkce_code_verifier")
    if not pkce_code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE code verifier not found in session.",
        )

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "project_id": settings.GOOGLE_PROJECT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "javascript_origins": [settings.FRONTEND_URL],
            }
        },
        scopes=settings.GOOGLE_SCOPES.split(),  # Use the property from settings
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

    try:
        # Exchange authorization code for tokens
        flow.fetch_token(code=code, code_verifier=pkce_code_verifier)

        credentials = flow.credentials
        # id_token_jwt is available on credentials if 'openid' scope was requested
        id_token_jwt = getattr(credentials, "id_token", None)

        # Verify the ID token
        if id_token_jwt:
            id_info = id_token.verify_oauth2_token(
                id_token_jwt, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        else:
            # If no id_token, we can't get user info this way.
            # This might happen if 'openid' scope is not included.
            # For this task, we assume id_token is always present.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ID token not received. Ensure 'openid' scope is requested.",
            )

        # Extract user information
        user_id = id_info.get("sub")
        user_email = id_info.get("email")
        user_name = id_info.get("name")
        user_picture = id_info.get("picture")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID not found in ID token.",
            )

        # Store user info and tokens in the database
        user_data = {
            "user_id": user_id,
            "email": user_email,
            "name": user_name,
            "picture": user_picture,
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry.isoformat()
            if credentials.expiry
            else None,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        create_or_update_user(user_id, user_data)

        # Store user_id in session to mark as authenticated
        session["user_id"] = user_id

        # Clear state and verifier from session after successful use
        session.pop("oauth_state", None)
        session.pop("pkce_code_verifier", None)

        # Redirect to frontend dashboard or success page
        return RedirectResponse(url=settings.FRONTEND_URL + "/dashboard")

    except Exception as e:
        # Handle errors during token exchange or ID token verification
        logger.error(f"OAuth callback error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {e}",
        )


def refresh_google_token(user_id: str):
    """
    Refreshes the Google access token for a given user using their refresh token.
    Updates the stored access token and its expiry time.
    """
    user_data = get_user(user_id)
    if not user_data or not user_data.get("refresh_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token found for user. Re-authentication required.",
        )

    credentials = Credentials(
        token=user_data["access_token"],
        refresh_token=user_data["refresh_token"],
        token_uri=user_data["token_uri"],
        client_id=user_data["client_id"],
        client_secret=user_data["client_secret"],
        scopes=settings.GOOGLE_SCOPES.split(),
    )

    try:
        # The refresh() method will automatically handle this if the token is expired.
        # It also updates credentials.token and credentials.expiry
        credentials.refresh(GoogleAuthRequest())

        # Update user data with new access token and expiry
        user_data["access_token"] = credentials.token
        user_data["expires_at"] = (
            credentials.expiry.isoformat() if credentials.expiry else None
        )  # Ensure expiry is not None
        create_or_update_user(user_id, user_data)
        return credentials
    except Exception as e:
        logger.error(f"Token refresh failed for user {user_id}: {e}", exc_info=True)
        # Invalidate refresh token and user session if refresh fails
        delete_user(user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to refresh token. Please re-authenticate. Error: {e}",
        )


@router.get(
    "/status",
    summary="Check Authentication Status",
    description="Checks the current authentication status of the user. If authenticated, it returns basic user information and ensures the access token is valid, refreshing it if necessary. Returns a 401 Unauthorized error if the user is not authenticated or the session is invalid.",
)
async def auth_status(request: Request):
    session = request.session
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    # Ensure user_id is a string before passing to get_user
    user_id_str = str(user_id)
    user_data = get_user(user_id_str)
    if not user_data:
        # User ID in session but not in DB, likely invalidated
        session.pop("user_id", None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session invalid. Please re-authenticate.",
        )

    try:
        # Attempt to refresh token if needed, this will also update user_data in db
        credentials = refresh_google_token(user_id_str)

        # Return user info from the updated user_data
        return {
            "id": user_data["user_id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data["picture"],
            "access_token": credentials.token,  # Return the current access token
            "expires_at": credentials.expiry.isoformat()
            if credentials.expiry
            else None,  # Ensure expiry is not None
        }
    except HTTPException as e:
        # If refresh_google_token raises HTTPException, it means re-authentication is needed
        session.pop("user_id", None)  # Clear session user_id
        raise e
    except Exception as e:
        # Catch any other unexpected errors during status check
        session.pop("user_id", None)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


@router.post(
    "/logout",
    summary="Logout User",
    description="Logs out the current user by clearing their session and removing their authentication data from the database. This invalidates their access and refresh tokens.",
)
async def logout(request: Request):
    session = request.session
    user_id = session.get("user_id")
    if user_id:
        delete_user(
            str(user_id)
        )  # Ensure user_id is a string before passing to delete_user
    session.clear()
    return {"message": "Logged out successfully"}


async def get_current_user(request: Request):
    """
    Dependency to get the current authenticated user.
    It checks the session for user_id and ensures the access token is valid.
    """
    session = request.session
    user_id = session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = get_user(str(user_id))
    if not user_data:
        session.pop("user_id", None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session invalid. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if access token is expired or close to expiring (e.g., within 5 minutes)
    expires_at_str = user_data.get("expires_at")
    if expires_at_str:
        expires_at = datetime.fromisoformat(expires_at_str)
        if expires_at < datetime.utcnow() + timedelta(minutes=5):
            try:
                # Attempt to refresh token
                credentials = refresh_google_token(str(user_id))
                user_data["access_token"] = credentials.token
                user_data["expires_at"] = (
                    credentials.expiry.isoformat() if credentials.expiry else None
                )
            except HTTPException as e:
                # If refresh fails, re-raise the authentication error
                raise e
            except Exception as e:
                # Catch any other unexpected errors during refresh
                session.pop("user_id", None)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"An unexpected error occurred during token refresh: {e}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    else:
        # If no expires_at, assume token needs refresh or is invalid
        try:
            credentials = refresh_google_token(str(user_id))
            user_data["access_token"] = credentials.token
            user_data["expires_at"] = (
                credentials.expiry.isoformat() if credentials.expiry else None
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            session.pop("user_id", None)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during token validation: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return {
        "user_id": user_data["user_id"],
        "email": user_data["email"],
        "name": user_data["name"],
        "picture": user_data["picture"],
        "access_token": user_data["access_token"],
    }

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from typing import Optional, Any
from backend.db.user_store import get_user_credentials, User

logger = logging.getLogger(__name__)

def build_drive_service(access_token: str, refresh_token: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> Any:
    """
    Builds and returns an initialized Google Drive API service client.

    Args:
        access_token: The user's current Google OAuth access token.
        refresh_token: (Optional) The user's Google OAuth refresh token.
        client_id: (Optional) Your Google OAuth client ID.
        client_secret: (Optional) Your Google OAuth client secret.

    Returns:
        An initialized Google Drive API service client.

    Raises:
        ValueError: If access_token is None or empty.
        HttpError: If there's an HTTP error during API client build (e.g., invalid credentials).
        Exception: For other unexpected errors.
    """
    if not access_token:
        raise ValueError("Access token cannot be None or empty.")

    try:
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token" # Standard Google token URI
        )
        
        # If refresh_token is provided, ensure credentials can refresh
        if refresh_token and client_id and client_secret:
            # This will attempt to refresh the token if it's expired
            # and a refresh token is available.
            credentials.refresh(None)
        
        # Use aiohttp for async HTTP requests with googleapiclient
        from googleapiclient.http import build_http
        # The googleapiclient library does not natively support async operations
        # with aiohttp in the way you're trying to use it.
        # For asynchronous Google Drive operations, you would typically use
        # an async-compatible HTTP client with the credentials, or
        # wrap synchronous calls in a thread pool executor.
        # For now, we'll revert to the synchronous build and rely on
        # FastAPI's async capabilities to handle the I/O blocking.
        # If true async is required for Google API calls, consider
        # using a different library or an async wrapper.

        drive_service = build("drive", "v3", credentials=credentials)
        return drive_service
    except HttpError as error:
        logger.error(f"HTTP error building Drive service: {error}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while building Drive service: {e}")
        raise
 
def find_or_create_folder(
    user_id: str,
    folder_name: str,
    parent_folder_id: Optional[str] = None
) -> str:
    """
    Searches for a Google Drive folder by name and creates it if it doesn't exist.

    Args:
        user_id: The ID of the user whose Google Drive to access.
        folder_name: The name of the folder to find or create.
        parent_folder_id: (Optional) The ID of the parent folder. If None, searches/creates in My Drive root.

    Returns:
        The ID of the found or newly created folder.

    Raises:
        HttpError: If there's an HTTP error during Google Drive API operations.
        ValueError: If user credentials cannot be retrieved.
        Exception: For other unexpected errors.
    """
    try:
        user_credentials = get_user_credentials(user_id)
        if not user_credentials:
            raise ValueError(f"No Google credentials found for user_id: {user_id}")

        drive_service = build_drive_service(
            access_token=user_credentials.access_token,
            refresh_token=user_credentials.refresh_token,
            client_id=user_credentials.client_id,
            client_secret=user_credentials.client_secret
        )

        # Build the query
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        else:
            # To search in My Drive root, we can explicitly look for folders not in any specific parent,
            # or rely on the default behavior if no parents are specified.
            # For simplicity, if parent_folder_id is None, we assume root search.
            pass

        # Search for existing folder
        results = drive_service.files().list(
            q=query,
            fields="files(id, name)",
            spaces="drive"
        ).execute()
        
        items = results.get("files", [])

        if items:
            logger.info(f"Found existing folder '{folder_name}' with ID: {items[0]['id']}")
            return items[0]["id"]
        else:
            # Create new folder
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if parent_folder_id:
                file_metadata["parents"] = [parent_folder_id] # type: ignore

            folder = drive_service.files().create(
                body=file_metadata,
                fields="id"
            ).execute()
            logger.info(f"Created new folder '{folder_name}' with ID: {folder['id']}")
            return folder.get("id")

    except HttpError as error:
        logger.error(f"HTTP error in find_or_create_folder: {error}")
        raise
    except ValueError as e:
        logger.error(f"Value error in find_or_create_folder: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred in find_or_create_folder: {e}")
        raise
from googleapiclient.http import MediaInMemoryUpload
import io

def upload_text_file(
    file_name: str,
    file_content: str,
    folder_id: str,
    mime_type: str = 'text/markdown',
    user_id: Optional[str] = None
) -> dict:
    """
    Uploads text content as a file to a specified Google Drive folder.

    Args:
        file_name: The name of the file to create (e.g., "Report.md").
        file_content: The content of the file as a string.
        folder_id: The ID of the target Google Drive folder.
        mime_type: The MIME type of the file (default: 'text/markdown').
        user_id: The ID of the user whose Google Drive to access.

    Returns:
        A dictionary containing information about the uploaded file (id, name, webViewLink).

    Raises:
        ValueError: If user_id is None or credentials cannot be retrieved.
        HttpError: If there's an HTTP error during Google Drive API operations.
        Exception: For other unexpected errors.
    """
    if not user_id:
        raise ValueError("user_id must be provided to upload a file.")

    try:
        user_credentials = get_user_credentials(user_id)
        if not user_credentials:
            raise ValueError(f"No Google credentials found for user_id: {user_id}")

        drive_service = build_drive_service(
            access_token=user_credentials.access_token,
            refresh_token=user_credentials.refresh_token,
            client_id=user_credentials.client_id,
            client_secret=user_credentials.client_secret
        )

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        content_bytes = file_content.encode('utf-8')
        fh = io.BytesIO(content_bytes)
        media_body = MediaInMemoryUpload(
            fh,
            mimetype=mime_type,
            resumable=True
        )

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id, name, webViewLink'
        ).execute()

        logger.info(f"Uploaded file '{file_name}' with ID: {file.get('id')} to folder {folder_id}")
        return file

    except HttpError as error:
        logger.error(f"HTTP error in upload_text_file: {error}")
        raise
    except ValueError as e:
        logger.error(f"Value error in upload_text_file: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred in upload_text_file: {e}")
        raise

# Example usage (for testing purposes, not part of the service itself)
if __name__ == "__main__":
    # This block is for local testing and demonstration.
    # In a real application, access_token, refresh_token, client_id, client_secret
    # would come from your authentication system and environment variables.
    print("This is a utility module for Google Drive service. It's not meant to be run directly.")
    print("To test, you would import build_drive_service and pass valid credentials.")
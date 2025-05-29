from backend.celery_app import celery_app # Import celery_app
from backend.services.google_drive_service import upload_text_file
import logging

logger = logging.getLogger(__name__)
from googleapiclient.errors import HttpError

@celery_app.task(bind=True, max_retries=3, default_retry_delay=300) # Use celery_app.task
def save_text_to_gdrive_task(self, file_content: str, company_name: str, drive_folder_id: str, user_id: str):
    """
    Celery task to save text content (e.g., prospect overview) to Google Drive.

    Args:
        file_content: The content of the file to save.
        company_name: The name of the company, used for file naming.
        drive_folder_id: The Google Drive folder ID where the file should be saved.
        user_id: The ID of the user whose Google Drive to access for credentials.
    """
    file_name = f"{company_name}_Prospect_Overview.md"
    try:
        logger.info(f"Attempting to upload '{file_name}' for user {user_id} to folder {drive_folder_id}")
        uploaded_file_info = upload_text_file(
            file_name=file_name,
            file_content=file_content,
            folder_id=drive_folder_id,
            user_id=user_id,
            mime_type='text/markdown'
        )
        logger.info(f"Successfully uploaded '{file_name}'. File ID: {uploaded_file_info.get('id')}, Link: {uploaded_file_info.get('webViewLink')}")
        return {
            "status": "success",
            "file_id": uploaded_file_info.get('id'),
            "file_name": uploaded_file_info.get('name'),
            "web_view_link": uploaded_file_info.get('webViewLink')
        }
    except HttpError as e:
        logger.error(f"Google Drive API error while uploading '{file_name}': {e}")
        self.retry(exc=e, countdown=60) # Retry after 60 seconds
    except ValueError as e:
        logger.error(f"Credential error for user {user_id} while uploading '{file_name}': {e}")
        # Do not retry for credential errors, as it's likely a persistent issue
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while uploading '{file_name}': {e}")
        self.retry(exc=e, countdown=300) # Retry after 5 minutes for other errors

@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def save_extracted_content_to_gdrive_task(self, extracted_contents: list, drive_folder_id: str, user_id: str):
    """
    Celery task to save a list of extracted content items to Google Drive.

    Args:
        extracted_contents: A list of dictionaries, each containing 'url', 'title', 'content', 'status'.
        drive_folder_id: The Google Drive folder ID where the files should be saved.
        user_id: The ID of the user whose Google Drive to access for credentials.
    """
    results = []
    for item in extracted_contents:
        url = item.get("url")
        title = item.get("title")
        content = item.get("content")
        status = item.get("status")

        if status == "success" and content:
            file_name = f"{title}.md" if title else f"extracted_content_{url.replace('/', '_').replace(':', '_')}.md"
            try:
                logger.info(f"Attempting to upload '{file_name}' for user {user_id} to folder {drive_folder_id}")
                uploaded_file_info = upload_text_file(
                    file_name=file_name,
                    file_content=content,
                    folder_id=drive_folder_id,
                    user_id=user_id,
                    mime_type='text/markdown'
                )
                logger.info(f"Successfully uploaded '{file_name}'. File ID: {uploaded_file_info.get('id')}, Link: {uploaded_file_info.get('webViewLink')}")
                results.append({
                    "url": url,
                    "status": "success",
                    "file_id": uploaded_file_info.get('id'),
                    "file_name": uploaded_file_info.get('name'),
                    "web_view_link": uploaded_file_info.get('webViewLink')
                })
            except HttpError as e:
                logger.error(f"Google Drive API error while uploading '{file_name}' for URL {url}: {e}")
                results.append({"url": url, "status": "failed", "error": str(e)})
                # Do not retry the whole task for individual file upload failures
            except ValueError as e:
                logger.error(f"Credential error for user {user_id} while uploading '{file_name}' for URL {url}: {e}")
                results.append({"url": url, "status": "failed", "error": str(e)})
                # Do not retry for credential errors, as it's likely a persistent issue
                raise # Re-raise to fail the task if credentials are bad
            except Exception as e:
                logger.error(f"An unexpected error occurred while uploading '{file_name}' for URL {url}: {e}")
                results.append({"url": url, "status": "failed", "error": str(e)})
        else:
            logger.warning(f"Skipping upload for URL {url} due to status '{status}' or empty content.")
            results.append({"url": url, "status": status, "error": "Content not extracted or empty."})
    
    # Log summary
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count
    logger.info(f"Finished processing extracted content. Successfully uploaded: {success_count}, Failed: {failed_count}")
    
    return results
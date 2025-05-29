# Task 4.3: Celery Task - Save Extracted Content to GDrive

**Phase:** Phase 4: Content Extraction & Finalization
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
This task takes the list of extracted content (from Task 4.2) and saves each piece of content as a separate Markdown file to the user's designated Google Drive folder.

## 2. Detailed Steps / Implementation Notes

1.  **Define Celery Task (`save_extracted_content_to_gdrive_task`):**
    *   This task will likely be chained after `extract_url_content_task` (Task 4.2) or called by an orchestrator task.
    *   It will receive the structured output from Task 4.2.
    *   Define it in `backend/tasks/content_extraction.py` or `backend/tasks/google_drive_tasks.py`.
        ```python
        # backend/tasks/content_extraction.py (or google_drive_tasks.py)
        from backend.celery_app import celery_app
        from backend.services.google_drive_service import upload_text_file # Assumes this handles auth via user_id context
        # from .utils import update_task_status

        @celery_app.task(bind=True, name="save_extracted_content_to_gdrive_task")
        def save_extracted_content_to_gdrive_task(self, extracted_data: dict):
            """
            Saves extracted web content to Google Drive.
            `extracted_data` is expected to be the return value from extract_url_content_task.
            """
            task_id = self.request.id
            company_name = extracted_data.get("company_name", "Unknown Company")
            drive_folder_id = extracted_data.get("drive_folder_id")
            user_id = extracted_data.get("user_id")
            extracted_contents = extracted_data.get("extracted_contents", [])

            if not drive_folder_id or not user_id:
                print(f"Error: Missing drive_folder_id or user_id for saving extracted content for {company_name}")
                raise ValueError("Missing drive_folder_id or user_id for saving extracted content.")

            successful_uploads = []
            failed_uploads = []
            total_files = len(extracted_contents)

            # update_task_status(task_id, f"Saving {total_files} extracted articles to Google Drive for {company_name}", 1, total_files + 1)

            for i, item in enumerate(extracted_contents):
                if item["status"] == "success" and item["content"] and item["file_name"]:
                    file_name = item["file_name"]
                    file_content = item["content"]
                    # update_task_status(task_id, f"Uploading {i+1}/{total_files}: {file_name}", i + 1, total_files + 1)
                    print(f"Uploading {file_name} to GDrive...")
                    try:
                        # CRITICAL: `upload_text_file` needs to handle auth using `user_id`
                        upload_result = upload_text_file(
                            file_name=file_name,
                            file_content=file_content,
                            folder_id=drive_folder_id,
                            mime_type='text/markdown',
                            user_id=user_id # Pass user_id for auth context
                        )
                        successful_uploads.append({
                            "url": item["url"],
                            "file_id": upload_result.get('id'),
                            "file_name": file_name,
                            "webViewLink": upload_result.get('webViewLink')
                        })
                    except Exception as e:
                        print(f"Failed to upload {file_name} (URL: {item['url']}) to GDrive: {e}")
                        failed_uploads.append({
                            "url": item["url"],
                            "file_name": file_name,
                            "error": str(e)
                        })
                else:
                    print(f"Skipping upload for URL {item['url']} due to prior extraction failure.")
                    failed_uploads.append({
                        "url": item["url"],
                        "file_name": item.get("file_name", "N/A"),
                        "error": item.get("error", "Extraction failed")
                    })
            
            # update_task_status(task_id, "All extracted content processed for saving", total_files + 1, total_files + 1)

            return {
                "company_name": company_name,
                "drive_folder_id": drive_folder_id,
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "status_message": f"Saved {len(successful_uploads)} of {total_files} extracted articles to Google Drive."
            }
        ```

2.  **Iterate and Upload:**
    *   Loop through the `extracted_contents` list received from Task 4.2.
    *   For each item that was successfully extracted (`status == "success"` and `content` is not `None`), call the `upload_text_file` function (from Task 2.3).
    *   Pass the `file_name`, `content`, `drive_folder_id`, and `user_id`.

3.  **Credential Management:**
    *   Reiterate the critical importance of passing `user_id` to `upload_text_file` so that the Google Drive service can retrieve the correct user-specific OAuth credentials (access token via refresh token) for the upload.

4.  **Error Handling:**
    *   Handle individual upload failures gracefully. Log the error for each failed upload but continue processing other files.
    *   Report a summary of successful and failed uploads.

5.  **Status Updates:**
    *   Update the task status to reflect progress (e.g., "Uploading X/Y files").

## 3. Expected Output / Deliverables
*   A Celery task function (`save_extracted_content_to_gdrive_task`) that takes the output of `extract_url_content_task`.
*   Each successfully extracted article is saved as a separate Markdown file in the user's Google Drive folder.
*   The task returns a summary of which files were successfully uploaded and which failed.

## 4. Dependencies
*   Task 2.3: Backend - File Upload Functionality (provides `upload_text_file`).
*   Task 4.2: Celery Task - URL Content Extraction (provides the input data).
*   Task 3.1: Backend - Celery & Redis Setup.
*   Mechanism for Celery tasks to use user-specific Google OAuth tokens.

## 5. Acceptance Criteria
*   The Celery task executes successfully.
*   All successfully extracted articles from Task 4.2 are found in the designated Google Drive folder.
*   Each file has the correct content and filename.
*   The task's return value accurately reflects the success/failure of each upload.
*   Individual upload failures do not stop the entire task.

## 6. Estimated Effort (Optional)
*   Medium (managing iteration, individual file errors, and status updates).

## 7. Notes / Questions
*   **File Naming:** Ensure the filenames generated in Task 4.2 are unique enough to avoid overwriting if multiple articles from the same domain/path are processed. Appending a timestamp or a hash could be an option if collisions are a concern.
*   **Google Drive Limits:** Be mindful of Google Drive API rate limits if processing a very large number of URLs. Implement delays or batching if necessary.
*   **User Feedback:** The summary of successful/failed uploads will be important for the frontend UI to display to the user.
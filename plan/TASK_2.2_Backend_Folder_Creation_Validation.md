# Task 2.2: Backend - Folder Creation/Validation

**Phase:** Phase 2: Google Drive Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Implement backend functionality to check if a specified output folder exists in the user's Google Drive, and create it if it doesn't. This will use the user's OAuth tokens via the Google Drive API service client. The folder will be used to store all research outputs.

## 2. Detailed Steps / Implementation Notes

1.  **Define Default Folder Structure (if applicable):**
    *   Decide on a default root folder name if the user doesn't specify a deep path, e.g., "Sales Research Tool Output".
    *   The user might provide a full path or just a name for a folder within this default root. For simplicity, initially, we might just create a folder with the user-provided name (or a generated one) directly in their Drive's root or within a single predefined application root folder.

2.  **Extend Google Drive Service (`backend/services/google_drive_service.py`):**
    *   Add a new method to the `GoogleDriveService` (or as a standalone function using the service client).
    *   This method, let's call it `find_or_create_folder(folder_name: str, parent_folder_id: str = None) -> str:`, will:
        *   Accept a `folder_name` and an optional `parent_folder_id`. If `parent_folder_id` is `None` or not provided, it implies creating/searching in the root of "My Drive".
        *   **Search for Existing Folder:**
            *   Use `drive_service.files().list()` to search for a folder with the given `folder_name` and MIME type `application/vnd.google-apps.folder`.
            *   Filter by `name = 'folder_name'` and `mimeType = 'application/vnd.google-apps.folder'`.
            *   If `parent_folder_id` is provided, add `'parent_folder_id' in parents` to the query `q`.
            *   The query would look something like: `q="name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"` (add parent clause if needed).
            *   Specify `fields="files(id, name)"` to get only necessary information.
            *   If one or more folders are found, return the ID of the first one found. (Handle cases of multiple folders with the same name if necessary, e.g., by using the first one or allowing user to disambiguate - though simpler to just use first).
        *   **Create Folder if Not Found:**
            *   If the search returns no results, create a new folder.
            *   Use `drive_service.files().create()` with a `body` parameter:
                ```python
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_folder_id:
                    folder_metadata['parents'] = [parent_folder_id]
                
                created_folder = drive_service.files().create(
                    body=folder_metadata,
                    fields='id' # Get the ID of the newly created folder
                ).execute()
                return created_folder.get('id')
                ```
        *   Return the ID of the found or newly created folder.

3.  **API Endpoint Integration (Conceptual - for `research/start`):**
    *   The main `/api/research/start` endpoint (Task 5.1) will receive the target company name and the desired Google Drive folder name/path from the frontend.
    *   This endpoint will call `find_or_create_folder()` before starting any research tasks.
    *   The returned folder ID will then be passed to Celery tasks that need to save files.

4.  **Permissions and Scopes:**
    *   Ensure the `https://www.googleapis.com/auth/drive.file` scope is active, as it allows folder creation and modification for app-created folders/files.

5.  **Error Handling:**
    *   Handle potential errors:
        *   Permissions issues (though `drive.file` should be sufficient for app's own creations).
        *   API errors from Google Drive.
        *   Invalid folder names (e.g., containing unsupported characters, though Drive API might handle this).

## 3. Expected Output / Deliverables
*   A Python function/method in the backend (e.g., within `GoogleDriveService`) that can:
    *   Search for a Google Drive folder by name (and optionally parent ID).
    *   Create the folder if it doesn't exist.
    *   Return the Google Drive ID of the found or created folder.

## 4. Dependencies
*   Task 2.1: Backend - Google Drive API Client Setup (provides the `drive_service` client).
*   User's authenticated Google credentials with `drive.file` scope.

## 5. Acceptance Criteria
*   Calling the `find_or_create_folder` function with a new folder name successfully creates the folder in the user's Google Drive and returns its ID.
*   Calling the function again with the same folder name finds the existing folder and returns its ID without creating a duplicate.
*   If a `parent_folder_id` is specified, the folder is searched/created within that parent.
*   Errors during the process (e.g., API errors) are handled or propagated correctly.
*   The function works correctly when the target folder is in the root of "My Drive" and when it's nested.

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **Folder Naming:** Consider how to handle folder names if the user provides a name that already exists but is not what they intended (e.g., "Company X Research" vs. "Company X Research (1)"). For this iteration, finding the first match or creating if none is likely sufficient.
*   **Path-like Input:** If the user provides a path like "My Project Reports/Client A", the logic would need to recursively find or create each segment of the path. For simplicity, the initial implementation might only support creating a single folder by name, possibly within a predefined application root folder or the user's Drive root. The task description implies a "Google Drive Folder Picker" or specifying a "new folder name within a default root," which simplifies this.
*   **Default Root Folder:** The plan mentions "/Sales Research Tool Output/". If this is a fixed root, the `find_or_create_folder` logic would first ensure this root exists, get its ID, and then subsequent user-specified folders would be created under it.
# Task 4.2: Celery Task - URL Content Extraction

**Phase:** Phase 4: Content Extraction & Finalization
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create a Celery task that takes a list of prioritized URLs (obtained from Task 3.3). For each URL, it will:
1.  Fetch the web page content.
2.  Extract the main text using `trafilatura`.
3.  Convert the extracted text to Markdown format.
4.  Prepare the content for saving to Google Drive (which will be handled by Task 4.3).

## 2. Detailed Steps / Implementation Notes

1.  **Define Celery Task (`extract_url_content_task`):**
    *   Create a new module for content extraction tasks, e.g., `backend/tasks/content_extraction.py`.
    *   Import `celery_app` from `backend.celery_app`.
    *   Import `fetch_and_extract_text` from `backend.services.content_extraction_service` (Task 4.1).
    *   The task should accept `source_urls: list[str]`, `company_name: str`, `drive_folder_id: str`, and `user_id: str` (for GDrive auth in Task 4.3).
        ```python
        # backend/tasks/content_extraction.py
        from backend.celery_app import celery_app
        from backend.services.content_extraction_service import fetch_and_extract_text
        # from .utils import update_task_status # If you have a shared status update utility
        # from backend.tasks.google_drive_tasks import save_text_to_gdrive_task # For chaining to Task 4.3

        @celery_app.task(bind=True, name="extract_url_content_task")
        def extract_url_content_task(self, source_urls: list[str], company_name: str, drive_folder_id: str, user_id: str = None):
            """
            Fetches and extracts content from a list of URLs, converts to Markdown.
            """
            task_id = self.request.id
            extracted_contents = []
            total_urls = len(source_urls)
            
            # update_task_status(task_id, f"Starting content extraction for {total_urls} URLs for {company_name}", 1, total_urls + 1)

            for i, url in enumerate(source_urls):
                # update_task_status(task_id, f"Processing URL {i+1}/{total_urls}: {url}", i + 1, total_urls + 1)
                print(f"Extracting content from: {url}")
                try:
                    extracted_text = fetch_and_extract_text(url)
                    if extracted_text:
                        # Convert to Markdown (trafilatura often returns plain text,
                        # but if it returns HTML, you'd need an HTML-to-Markdown converter like markdownify)
                        # For now, assume plain text is sufficient or trafilatura's output is markdown-like.
                        # If trafilatura returns HTML, you'd need:
                        # from markdownify import markdownify as md
                        # markdown_content = md(extracted_text)
                        markdown_content = extracted_text # Assuming trafilatura's output is suitable or plain text

                        # Create a descriptive filename
                        # Basic slugification of URL or use page title if available from trafilatura metadata
                        import re
                        import urllib.parse
                        
                        parsed_url = urllib.parse.urlparse(url)
                        # Use domain and path for filename, sanitize
                        domain = parsed_url.netloc.replace('.', '_').replace('-', '_')
                        path_slug = re.sub(r'[^a-zA-Z0-9_]', '_', parsed_url.path).strip('_')
                        if not path_slug:
                            path_slug = "index" # Fallback for root paths
                        
                        # Limit filename length to avoid issues
                        max_filename_len = 100
                        base_filename = f"{domain}_{path_slug}"[:max_filename_len].strip('_')
                        
                        # Add a unique suffix if needed, or just use a simple name
                        file_name = f"{company_name}_{base_filename}.md"

                        extracted_contents.append({
                            "url": url,
                            "content": markdown_content,
                            "file_name": file_name,
                            "status": "success"
                        })
                    else:
                        extracted_contents.append({
                            "url": url,
                            "content": None,
                            "file_name": None,
                            "status": "failed",
                            "error": "No content extracted"
                        })
                except Exception as e:
                    print(f"Error extracting content from {url}: {e}")
                    extracted_contents.append({
                        "url": url,
                        "content": None,
                        "file_name": None,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # update_task_status(task_id, "Content extraction complete", total_urls + 1, total_urls + 1)

            # Pass extracted contents to the next task for saving to GDrive (Task 4.3)
            # This can be done via Celery chaining or by returning the data
            # and having the orchestrator task call the next one.
            # For simplicity, we'll return the list, and the orchestrator will handle it.
            return {
                "company_name": company_name,
                "drive_folder_id": drive_folder_id,
                "user_id": user_id,
                "extracted_contents": extracted_contents,
                "status_message": f"Content extraction for {total_urls} URLs complete."
            }
        ```

2.  **URL Iteration and Processing:**
    *   Loop through the `source_urls` list.
    *   For each URL, call `fetch_and_extract_text`.

3.  **Markdown Conversion:**
    *   `trafilatura` primarily extracts clean text. If the source content is HTML and a rich Markdown conversion is desired (e.g., preserving headings, lists, links), an additional library like `markdownify` might be needed.
    *   Add `markdownify` to `backend/requirements.txt` if needed:
        ```txt
        # backend/requirements.txt
        # ...
        markdownify>=0.11.0,<0.12.0
        ```
    *   For now, assume `trafilatura`'s output is sufficiently "markdown-like" or plain text that can be saved as `.md`.

4.  **Filename Generation:**
    *   Generate a descriptive filename for each extracted article. This could be based on the URL's domain, path, or a slugified version of the page title (if `trafilatura` provides it in metadata).
    *   Ensure filenames are unique and valid for Google Drive.

5.  **Error Handling:**
    *   Handle cases where `fetch_and_extract_text` returns `None` (failed download or extraction).
    *   Log errors for specific URLs without stopping the entire task.
    *   Report which URLs failed extraction.

6.  **Status Updates:**
    *   Update the task status (e.g., using Celery's built-in state mechanism or a custom one) to show progress (e.g., "Processing X/Y URLs").

## 3. Expected Output / Deliverables
*   A Celery task function (`extract_url_content_task`) defined in `backend/tasks/content_extraction.py`.
*   The task takes a list of URLs, company name, drive folder ID, and user ID as input.
*   For each URL, it attempts to fetch and extract content.
*   The extracted content is converted to Markdown.
*   The task returns a list of dictionaries, each containing the URL, extracted content (or error), and a proposed filename.

## 4. Dependencies
*   Task 3.3: Celery Task - Prospect Deep Dive (provides the `source_urls`).
*   Task 4.1: Backend - `trafilatura` Integration (provides `fetch_and_extract_text`).
*   Task 3.1: Backend - Celery & Redis Setup.

## 5. Acceptance Criteria
*   The Celery task can be successfully enqueued and executed.
*   The task iterates through the provided URLs.
*   For valid URLs, content is extracted and formatted (or prepared) as Markdown.
*   Descriptive filenames are generated for each article.
*   Errors during fetching or extraction for individual URLs are handled gracefully, and the task continues processing other URLs.
*   The task returns a structured result indicating success/failure for each URL.

## 6. Estimated Effort (Optional)
*   Medium (Robust URL handling, error logging, and filename generation can add complexity).

## 7. Notes / Questions
*   **Politeness:** Implement delays between requests to different domains to avoid overwhelming servers or getting blocked. This might be done within `fetch_and_extract_text` or by the Celery task itself.
*   **URL Deduplication/Filtering:** The `source_urls` list might contain duplicates or irrelevant URLs. Consider adding a filtering step if necessary.
*   **Content Quality:** The quality of extracted content depends heavily on the source website. Some sites might yield poor results.
*   **HTML to Markdown:** If `trafilatura` returns raw HTML and a proper Markdown conversion is needed, `markdownify` is a good choice.
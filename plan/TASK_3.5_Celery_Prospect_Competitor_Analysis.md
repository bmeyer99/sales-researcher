# Task 3.5: Celery Task - Prospect's Competitor Analysis (Gemini - Part 2)

**Phase:** Phase 3: Core Research Logic - Gemini API & Celery Tasks
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create a Celery task that performs competitor analysis for the target prospect company. This involves:
1.  Constructing a prompt for the Gemini API to identify the prospect's key competitors and analyze their technologies/offerings.
2.  Calling the Gemini API.
3.  Parsing the response.
4.  Saving the generated analysis report to the user's Google Drive folder.

This task runs after the initial "Prospect Deep Dive" (Task 3.3) and can run in parallel with other analysis tasks if the overall workflow is designed that way, or sequentially.

## 2. Detailed Steps / Implementation Notes

1.  **Define Celery Task (`prospect_competitor_analysis_task`):**
    *   In `backend/tasks/gemini_research.py` (or a new relevant module).
    *   The task should accept `company_name: str` and `drive_folder_id: str`. It might also need `user_id` for credential management for GDrive upload.
        ```python
        # backend/tasks/gemini_research.py
        from backend.celery_app import celery_app
        from backend.services.gemini_service import generate_gemini_content
        from backend.services.google_drive_service import upload_text_file # Assuming this handles auth via user_id context
        # from .utils import update_task_status # If you have a shared status update utility

        @celery_app.task(bind=True, name="prospect_competitor_analysis_task")
        def prospect_competitor_analysis_task(self, company_name: str, drive_folder_id: str, user_id: str = None): # user_id for GDrive auth
            """
            Performs competitor analysis for the given company using Gemini and saves it to Google Drive.
            """
            task_id = self.request.id
            # update_task_status(task_id, f"Starting competitor analysis for {company_name}", 1, 4) # Example steps

            # 1. Construct Prompt
            prompt = f"""
            Conduct a competitor analysis for the company: "{company_name}".
            Identify its key competitors (top 3-5 if possible).
            For each competitor, briefly describe:
            *   Their main products/services relevant to "{company_name}"'s market.
            *   Their key strengths and weaknesses compared to "{company_name}".
            *   Any known technologies they leverage that are significant in their market positioning.

            Please provide a concise report summarizing this analysis.
            The target audience for this report is a sales team looking to understand the competitive landscape for "{company_name}".
            """
            # update_task_status(task_id, "Competitor analysis prompt constructed", 2, 4)

            # 2. Call Gemini API
            # update_task_status(task_id, "Calling Gemini API for competitor analysis...", 3, 4)
            analysis_text = generate_gemini_content(prompt, model_name="gemini-1.5-pro-latest") # Or your chosen model

            if analysis_text.startswith("Error:"):
                # update_task_status(task_id, f"Gemini API Error: {analysis_text}", 3, 4)
                raise Exception(f"Gemini API Error during competitor analysis: {analysis_text}")
            
            # update_task_status(task_id, "Gemini response for competitor analysis received", 3, 4)

            # 3. Parse Response (Gemini response is likely the report itself)
            # For this task, the Gemini output is expected to be the report.
            # Minimal parsing might be needed unless specific formatting is requested.

            # 4. Save Report to Google Drive
            file_name = f"{company_name}_Competitor_Analysis.md"
            # update_task_status(task_id, f"Saving competitor analysis to Google Drive: {file_name}", 4, 4)

            try:
                # CRITICAL: `upload_text_file` needs to handle auth using `user_id`
                # to get the correct Google credentials for the Drive upload.
                upload_result = upload_text_file(
                    file_name=file_name,
                    file_content=analysis_text,
                    folder_id=drive_folder_id,
                    mime_type='text/markdown',
                    user_id=user_id # Pass user_id for auth context
                )
                # update_task_status(task_id, "Competitor analysis saved successfully", 4, 4)
                return {
                    "status": "success",
                    "file_id": upload_result.get('id'),
                    "file_name": file_name,
                    "drive_folder_id": drive_folder_id,
                    "webViewLink": upload_result.get('webViewLink'),
                    "message": f"Competitor analysis for {company_name} complete and saved."
                }
            except Exception as e:
                # update_task_status(task_id, f"Error saving competitor analysis: {e}", 4, 4)
                print(f"Error saving '{file_name}' to GDrive: {e}")
                raise # Let Celery handle retry/failure
        ```

2.  **Prompt Engineering:**
    *   Develop a clear prompt for Gemini to generate the competitor analysis. Specify the desired information (key competitors, their offerings, technologies, strengths/weaknesses).
    *   Consider the desired length and format of the report.

3.  **Google Drive Upload:**
    *   Use the `upload_text_file` service (from Task 2.3) to save the generated analysis text as a Markdown or text file.
    *   Ensure proper file naming, e.g., `"{company_name}_Competitor_Analysis.md"`.
    *   **Credential Management:** Reiterate the importance of `upload_text_file` (or the underlying Google Drive service) using the correct `user_id` to obtain the appropriate OAuth tokens for writing to the user's Drive.

4.  **Error Handling:**
    *   Handle errors from Gemini API calls and Google Drive uploads.

## 3. Expected Output / Deliverables
*   A Celery task function (`prospect_competitor_analysis_task`) in the backend.
*   The task takes `company_name`, `drive_folder_id`, and `user_id` as input.
*   The task generates a competitor analysis report using Gemini.
*   The generated report is saved as a file in the specified Google Drive folder.
*   The task returns status information, including the ID/link of the saved file.

## 4. Dependencies
*   Task 2.3: Backend - File Upload Functionality.
*   Task 3.1: Backend - Celery & Redis Setup.
*   Task 3.2: Backend - Gemini API Client Setup.
*   Mechanism for Celery tasks to use user-specific Google OAuth tokens (Task 1.5, Task 3.4 notes on credential management).

## 5. Acceptance Criteria
*   The Celery task executes successfully.
*   A competitor analysis report for the given company is generated by Gemini.
*   The report is saved to the correct Google Drive folder with the expected filename.
*   The content of the saved file matches the Gemini output.
*   Failures are handled gracefully.

## 6. Estimated Effort (Optional)
*   Medium (Prompt engineering and ensuring correct credential context for GDrive upload are key).

## 7. Notes / Questions
*   **Information Source:** Gemini will use its general knowledge. The quality of competitor identification depends on how well-known the prospect company and its market are.
*   **Depth of Analysis:** The prompt can be adjusted to ask for more or less detail.
*   **Parallel Execution:** This task, along with Task 3.6 (Own Competitor Marketing Analysis), could potentially run in parallel after Task 3.3 (Prospect Deep Dive) provides the initial company context, if the overall research workflow is designed to support parallel Celery task execution (e.g., using Celery groups).
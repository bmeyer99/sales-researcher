# Task 5.1: Backend - `/api/research/start` Endpoint

**Phase:** Phase 5: API Endpoints & Frontend-Backend Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create the primary FastAPI endpoint `/api/research/start`. This endpoint will:
1.  Accept the target company name and the desired Google Drive folder name/path from the frontend.
2.  Validate the input.
3.  Initiate the chain of Celery tasks for the entire research workflow (starting with Prospect Deep Dive).
4.  Return a `job_id` that the frontend can use to poll for progress.

## 2. Detailed Steps / Implementation Notes

1.  **Define API Endpoint:**
    *   Create a new API router or add to an existing one (e.g., `backend/api/v1/research.py`).
    *   Define a POST endpoint `/api/research/start`.
    *   Use Pydantic models for request body validation.
        ```python
        # Example: backend/api/v1/research.py
        from fastapi import APIRouter, Depends, HTTPException, status
        from pydantic import BaseModel, Field
        from typing import Optional
        from backend.celery_app import celery_app # Import Celery app instance
        # from backend.services.google_drive_service import find_or_create_folder # From Task 2.2
        # from backend.tasks.gemini_research import prospect_deep_dive_task, prospect_competitor_analysis_task, own_competitor_marketing_analysis_task
        # from backend.tasks.content_extraction import extract_url_content_task, save_extracted_content_to_gdrive_task
        # from backend.tasks.google_drive_tasks import save_text_to_gdrive_task # For saving overview
        # from backend.dependencies import get_current_user # For authentication (from Task 1.4)

        router = APIRouter(prefix="/research", tags=["Research"])

        class ResearchRequest(BaseModel):
            company_name: str = Field(..., min_length=2, max_length=100, description="The name of the prospect company to research.")
            gdrive_folder_name: str = Field(..., min_length=1, max_length=200, description="The desired name for the output folder in Google Drive.")
            # user_id: str # Will be obtained from authenticated user context

        @router.post("/start")
        async def start_research(request: ResearchRequest, current_user: dict = Depends(get_current_user)):
            """
            Initiates a new sales prospect research task.
            """
            company_name = request.company_name
            gdrive_folder_name = request.gdrive_folder_name
            user_id = current_user.get("id") # Assuming user ID is available from auth context

            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated.")

            # 1. Find or Create Google Drive Folder (synchronous step)
            # This step should ideally be quick. If it's slow, it might need to be a Celery task too.
            # For now, assume it's fast enough to be synchronous.
            try:
                # This call needs the user's Google credentials.
                # The `find_or_create_folder` function needs to be able to get the user's
                # access token (via refresh token) using the `user_id`.
                # This is a critical dependency on the credential management in Task 1.5.
                # For example, `find_or_create_folder(gdrive_folder_name, user_id=user_id)`
                # The `find_or_create_folder` function would then internally fetch/refresh tokens.
                drive_folder_id = await find_or_create_folder(gdrive_folder_name, user_id=user_id)
                if not drive_folder_id:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create or find Google Drive folder.")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Google Drive folder setup failed: {e}")

            # 2. Orchestrate Celery Tasks
            # Define the research workflow as a chain or group of Celery tasks.
            # The results of one task are passed to the next.
            # The `user_id` and `drive_folder_id` need to be passed to all tasks that interact with GDrive.

            # Example of a Celery chain:
            # Task 3.3: Prospect Deep Dive (returns overview_text, source_urls)
            # Task 3.4: Save Prospect Overview (takes overview_text, drive_folder_id, user_id)
            # Task 3.5: Prospect Competitor Analysis (takes company_name, drive_folder_id, user_id)
            # Task 3.6: Own Competitor Marketing Analysis (takes company_name, drive_folder_id, user_id)
            # Task 4.2: URL Content Extraction (takes source_urls, company_name, drive_folder_id, user_id)
            # Task 4.3: Save Extracted Content (takes extracted_contents, drive_folder_id, user_id)

            # Celery workflow orchestration:
            # Use Celery's `chain` or `group` for complex workflows.
            # For simplicity, let's define a sequential chain for now.
            # The `s` (signature) method creates a task signature.

            # Initial task: Prospect Deep Dive
            # It returns a dictionary with overview_text and source_urls
            deep_dive_signature = prospect_deep_dive_task.s(
                company_name=company_name,
                drive_folder_id=drive_folder_id,
                user_id=user_id # Pass user_id for credential management in tasks
            )

            # Subsequent tasks that depend on deep_dive_signature's output or run in parallel
            # For parallel tasks, use `group`. For sequential, use `chain`.
            # Let's assume a simple chain for now, where results are passed.
            # This will require careful design of task inputs/outputs.

            # Option 1: Simple sequential chain (if tasks can pass results directly)
            # This might be too simplistic if tasks need multiple inputs or run in parallel.
            # research_chain = chain(
            #     deep_dive_signature,
            #     save_text_to_gdrive_task.s(file_name=f"{company_name}_Overview.md", drive_folder_id=drive_folder_id, user_id=user_id), # Needs overview_text from previous task
            #     # ... more tasks
            # )

            # Option 2: Orchestrator task (more flexible)
            # A single orchestrator task that calls other tasks and manages their results.
            # This is often preferred for complex workflows.
            from backend.tasks.orchestrator import research_orchestrator_task # A new task for orchestration

            # The orchestrator task will receive all initial parameters and manage sub-tasks
            task_result = research_orchestrator_task.delay(
                company_name=company_name,
                gdrive_folder_id=drive_folder_id,
                user_id=user_id
            )
            job_id = task_result.id

            return {"job_id": job_id, "message": "Research task initiated successfully."}
        ```

2.  **Orchestrator Task (`backend/tasks/orchestrator.py`):**
    *   Given the complexity, an orchestrator task is highly recommended.
    *   This task will be responsible for calling `prospect_deep_dive_task`, `prospect_competitor_analysis_task`, `own_competitor_marketing_analysis_task`, `extract_url_content_task`, and `save_extracted_content_to_gdrive_task` in the correct sequence, passing results between them.
    *   It will also be responsible for updating the overall job status.
        ```python
        # Example: backend/tasks/orchestrator.py
        from backend.celery_app import celery_app
        from celery import chain, group, chord
        # Import all individual research tasks
        from backend.tasks.gemini_research import prospect_deep_dive_task, prospect_competitor_analysis_task, own_competitor_marketing_analysis_task
        from backend.tasks.content_extraction import extract_url_content_task, save_extracted_content_to_gdrive_task
        from backend.tasks.google_drive_tasks import save_text_to_gdrive_task # Assuming this is where save_text_to_gdrive_task lives

        @celery_app.task(bind=True, name="research_orchestrator_task")
        def research_orchestrator_task(self, company_name: str, gdrive_folder_id: str, user_id: str):
            """
            Orchestrates the entire sales prospect research workflow.
            """
            self.update_state(state='PROGRESS', meta={'message': 'Starting research workflow', 'current_phase': 'Initialization'})

            # Phase 1: Prospect Deep Dive
            # This task returns a dict: {"overview_text": ..., "source_urls": ...}
            deep_dive_result = prospect_deep_dive_task.delay(company_name, gdrive_folder_id, user_id).get() # .get() makes it synchronous for chaining here

            if deep_dive_result.get("status") == "error": # Example error handling
                self.update_state(state='FAILURE', meta={'message': 'Deep dive failed', 'error': deep_dive_result.get("error")})
                return {"status": "failed", "message": "Deep dive failed"}

            overview_text = deep_dive_result.get("overview_text")
            source_urls = deep_dive_result.get("source_urls")

            self.update_state(state='PROGRESS', meta={'message': 'Deep dive complete, saving overview and starting parallel analyses', 'current_phase': 'Parallel Analyses'})

            # Phase 2: Save Overview (can run in parallel or immediately after deep dive)
            save_overview_signature = save_text_to_gdrive_task.s(
                file_content=overview_text,
                file_name=f"{company_name}_Overview.md",
                drive_folder_id=gdrive_folder_id,
                user_id=user_id
            )

            # Phase 3 & 4: Competitor Analyses (can run in parallel)
            competitor_analysis_signature = prospect_competitor_analysis_task.s(
                company_name=company_name,
                drive_folder_id=gdrive_folder_id,
                user_id=user_id
            )
            own_marketing_analysis_signature = own_competitor_marketing_analysis_task.s(
                prospect_company_name=company_name,
                prospect_company_industry="General Industry", # This needs to come from deep_dive_result or be inferred
                drive_folder_id=gdrive_folder_id,
                user_id=user_id
            )

            # Group for parallel execution of analyses and overview save
            parallel_tasks = group(
                save_overview_signature,
                competitor_analysis_signature,
                own_marketing_analysis_signature
            )

            # Phase 5: URL Content Extraction (depends on deep_dive_result's source_urls)
            # This task will return a list of extracted contents
            extract_content_signature = extract_url_content_task.s(
                source_urls=source_urls,
                company_name=company_name,
                drive_folder_id=gdrive_folder_id,
                user_id=user_id
            )

            # Phase 6: Save Extracted Content (depends on extract_content_signature's output)
            save_extracted_content_signature = save_extracted_content_to_gdrive_task.s(
                # This task expects the output of extract_url_content_task as its first argument
            )

            # Define the overall workflow using Celery primitives
            # Example:
            # 1. Deep Dive
            # 2. Parallel group of (Save Overview, Competitor Analysis, Own Marketing Analysis)
            # 3. Extract URL Content
            # 4. Save Extracted Content

            # Use chord to ensure all parallel tasks complete before proceeding
            # The header is the group, the body is the next task that processes the results of the group
            # This requires careful handling of results if the body needs specific outputs from the group.
            # A simpler approach for this complex flow might be to call tasks sequentially within the orchestrator.

            # Let's refine the orchestrator to call tasks sequentially and manage state/results
            # This makes it easier to update status and pass specific data.

            # Re-thinking orchestrator for clarity and status updates:
            try:
                # 1. Prospect Deep Dive
                self.update_state(state='PROGRESS', meta={'message': 'Phase 1: Researching company overview with Gemini...', 'current_phase': 'Deep Dive'})
                deep_dive_result = prospect_deep_dive_task.apply(args=(company_name, gdrive_folder_id, user_id)).get()
                overview_text = deep_dive_result.get("overview_text")
                source_urls = deep_dive_result.get("source_urls")
                prospect_industry = deep_dive_result.get("industry", "General Industry") # Assuming deep dive can return industry

                self.update_state(state='PROGRESS', meta={'message': 'Phase 1: Complete. Overview extracted.', 'current_phase': 'Deep Dive Complete'})

                # 2. Save Overview
                self.update_state(state='PROGRESS', meta={'message': 'Phase 1: Saving overview to Google Drive...', 'current_phase': 'Saving Overview'})
                save_overview_task.apply(args=(overview_text, f"{company_name}_Overview.md", gdrive_folder_id, user_id)).get()
                self.update_state(state='PROGRESS', meta={'message': 'Phase 1: Complete. Overview saved to Google Drive.', 'current_phase': 'Overview Saved'})

                # 3. Prospect's Competitor Analysis
                self.update_state(state='PROGRESS', meta={'message': 'Phase 2: Analyzing company competitors with Gemini...', 'current_phase': 'Competitor Analysis'})
                prospect_competitor_analysis_task.apply(args=(company_name, gdrive_folder_id, user_id)).get()
                self.update_state(state='PROGRESS', meta={'message': 'Phase 2: Complete. Competitor analysis saved.', 'current_phase': 'Competitor Analysis Saved'})

                # 4. Own Competitor Marketing Analysis
                self.update_state(state='PROGRESS', meta={'message': 'Phase 3: Analyzing our competitive marketing for company segment...', 'current_phase': 'Marketing Analysis'})
                own_competitor_marketing_analysis_task.apply(args=(company_name, prospect_industry, gdrive_folder_id, user_id)).get()
                self.update_state(state='PROGRESS', meta={'message': 'Phase 3: Complete. Marketing analysis saved.', 'current_phase': 'Marketing Analysis Saved'})

                # 5. URL Content Extraction
                self.update_state(state='PROGRESS', meta={'message': f'Phase 4: Extracting content from {len(source_urls)} source URLs...', 'current_phase': 'Content Extraction'})
                extracted_content_data = extract_url_content_task.apply(args=(source_urls, company_name, gdrive_folder_id, user_id)).get()
                self.update_state(state='PROGRESS', meta={'message': 'Phase 4: Content extraction complete.', 'current_phase': 'Content Extraction Complete'})

                # 6. Save Extracted Content
                self.update_state(state='PROGRESS', meta={'message': 'Phase 4: Saving detailed articles as Markdown...', 'current_phase': 'Saving Extracted Content'})
                save_extracted_content_to_gdrive_task.apply(args=(extracted_content_data,)).get()
                self.update_state(state='PROGRESS', meta={'message': 'Phase 4: Complete. Detailed articles saved as Markdown.', 'current_phase': 'Extracted Content Saved'})

                self.update_state(state='SUCCESS', meta={'message': 'All tasks complete! Research is available in your Google Drive.', 'current_phase': 'Completed'})
                return {"status": "completed", "message": "Research workflow finished successfully."}

            except Exception as e:
                self.update_state(state='FAILURE', meta={'message': f'Research workflow failed: {e}', 'error': str(e)})
                return {"status": "failed", "message": f"Research workflow failed: {e}"}
        ```

3.  **Authentication and Dependencies:**
    *   The `get_current_user` dependency will ensure the user is authenticated before the research task is initiated.
    *   The `user_id` obtained from `current_user` is crucial and must be passed down to all Celery tasks that interact with user-specific Google APIs (Drive, potentially Gemini if it uses user OAuth).
    *   The `find_or_create_folder` function (from Task 2.2) needs to be adapted to accept `user_id` and use it to retrieve/refresh Google credentials.

4.  **Error Handling:**
    *   Implement robust error handling for each step of the workflow. If a sub-task fails, the orchestrator task should catch it, update its own status to `FAILURE`, and return an appropriate error message.

5.  **Status Updates:**
    *   The orchestrator task will use `self.update_state()` to provide granular progress updates (e.g., "Phase 1: Researching...", "Phase 2: Complete."). This status can then be polled by the frontend (Task 5.2).

## 3. Expected Output / Deliverables
*   A FastAPI POST endpoint `/api/research/start` that:
    *   Accepts `company_name` and `gdrive_folder_name`.
    *   Authenticates the user and extracts `user_id`.
    *   Synchronously finds or creates the Google Drive output folder.
    *   Asynchronously initiates the `research_orchestrator_task` via Celery.
    *   Returns a `job_id` (Celery task ID) to the frontend.
*   A new Celery orchestrator task (`research_orchestrator_task`) that sequentially calls and manages the execution of all sub-tasks (deep dive, competitor analysis, content extraction, saving to GDrive).

## 4. Dependencies
*   Task 1.2: Backend - OAuth Endpoints (for user authentication).
*   Task 1.4: Frontend - Token Handling & Authenticated State (for `get_current_user` dependency).
*   Task 2.2: Backend - Folder Creation/Validation (for `find_or_create_folder`).
*   Task 3.1: Backend - Celery & Redis Setup.
*   All individual Celery tasks (3.3, 3.4, 3.5, 3.6, 4.2, 4.3).
*   Crucially, the mechanism for Celery tasks to obtain user-specific Google OAuth tokens (Task 1.5).

## 5. Acceptance Criteria
*   Sending a valid POST request to `/api/research/start` (with authentication) returns a `job_id`.
*   The `research_orchestrator_task` is successfully enqueued and starts execution.
*   The Google Drive folder is created/found correctly.
*   If any required input is missing or invalid, the endpoint returns an appropriate HTTP error.
*   If Google Drive folder setup fails, an error is returned.

## 6. Estimated Effort (Optional)
*   Large (This is the central orchestration point, tying many components together).

## 7. Notes / Questions
*   **Synchronous vs. Asynchronous Folder Creation:** Keeping `find_or_create_folder` synchronous in the API endpoint simplifies error reporting back to the user immediately if the folder cannot be set up. If it becomes a bottleneck, it could be moved into the orchestrator task.
*   **Celery Task Chaining/Orchestration:** The orchestrator task is a robust pattern for complex workflows. Using `task.apply().get()` within the orchestrator makes the sub-tasks run synchronously *from the orchestrator's perspective*, allowing for easy result passing and sequential status updates. For true parallelism, `group` and `chord` would be used, but managing results and status updates becomes more complex.
*   **User ID to Celery Tasks:** The `user_id` is the key to enabling user-specific Google API calls from within Celery tasks. Ensure the mechanism for tasks to retrieve/refresh tokens based on `user_id` is solid.
*   **Error Handling in Orchestrator:** The orchestrator should catch exceptions from sub-tasks and update its own state to `FAILURE`.
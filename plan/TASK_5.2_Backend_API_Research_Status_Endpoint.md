# Task 5.2: Backend - `/api/research/status/{job_id}` Endpoint

**Phase:** Phase 5: API Endpoints & Frontend-Backend Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create a FastAPI endpoint `/api/research/status/{job_id}`. This endpoint will allow the frontend to poll for the real-time progress and status of an initiated research task (identified by its Celery `job_id`).

## 2. Detailed Steps / Implementation Notes

1.  **Define API Endpoint:**
    *   Add a GET endpoint `/api/research/status/{job_id}` to the research router (e.g., `backend/api/v1/research.py`).
    *   This endpoint will take the `job_id` (Celery task ID) as a path parameter.
    *   It should be a protected endpoint, requiring user authentication.
        ```python
        # Example: backend/api/v1/research.py (continued from Task 5.1)
        from celery.result import AsyncResult
        # from backend.dependencies import get_current_user # For authentication

        # ... (previous imports and router definition) ...

        @router.get("/status/{job_id}")
        async def get_research_status(job_id: str, current_user: dict = Depends(get_current_user)):
            """
            Retrieves the current status and progress of a research task.
            """
            # Ensure the user is authenticated and potentially authorized to view this job_id
            # (e.g., check if the job_id belongs to the current_user)
            # For simplicity, we'll assume any authenticated user can query any job_id for now,
            # but in production, you'd want to restrict this.

            task = AsyncResult(job_id, app=celery_app) # Get Celery task result object

            response_data = {
                "job_id": job_id,
                "status": task.state, # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
                "info": None,
                "progress_message": None,
                "current_phase": None,
                "result_link": None # Link to Google Drive folder if successful
            }

            if task.state == 'PENDING':
                response_data["progress_message"] = "Task is pending or not yet started."
            elif task.state == 'PROGRESS':
                # The orchestrator task (Task 5.1) updates its state with meta information
                response_data["info"] = task.info
                response_data["progress_message"] = task.info.get('message', 'Processing...')
                response_data["current_phase"] = task.info.get('current_phase', 'Unknown')
            elif task.state == 'SUCCESS':
                response_data["info"] = task.info # Final info from task.update_state
                response_data["progress_message"] = task.info.get('message', 'Task completed successfully.')
                response_data["current_phase"] = task.info.get('current_phase', 'Completed')
                # The orchestrator task should return the Google Drive folder link upon success
                # This link would be part of the final result of the orchestrator task.
                # Example: task.result.get("webViewLink") if the orchestrator returns it.
                if task.result and isinstance(task.result, dict):
                    response_data["result_link"] = task.result.get("webViewLink") # Assuming orchestrator returns this
            elif task.state == 'FAILURE':
                response_data["info"] = task.info
                response_data["progress_message"] = task.info.get('message', 'Task failed.')
                response_data["error"] = task.info.get('error', 'An unknown error occurred.')
            elif task.state == 'RETRY':
                response_data["info"] = task.info
                response_data["progress_message"] = task.info.get('message', 'Task is retrying...')
            elif task.state == 'REVOKED':
                response_data["progress_message"] = "Task was revoked."

            return response_data
        ```

2.  **Celery Task Status Updates:**
    *   The `research_orchestrator_task` (from Task 5.1) is responsible for updating its own state using `self.update_state(state='PROGRESS', meta={...})`.
    *   The `meta` dictionary should contain user-friendly messages and progress indicators (e.g., `message`, `current_phase`).
    *   Upon completion, the orchestrator task should update its state to `SUCCESS` and include any final results, such as the Google Drive folder link.

3.  **Security Considerations:**
    *   **Authorization:** It's crucial to ensure that a user can only query the status of tasks they initiated. The `current_user` object (from authentication) should be used to verify ownership of the `job_id`. This might involve storing `job_id` to `user_id` mapping in a database when the task is initiated.
    *   **Information Disclosure:** Be careful not to expose sensitive information in the `meta` data.

4.  **Error Handling:**
    *   Handle cases where the `job_id` is invalid or not found (though `AsyncResult` handles this by returning a `PENDING` state for unknown IDs).
    *   Ensure error messages are clear and user-friendly.

## 3. Expected Output / Deliverables
*   A FastAPI GET endpoint `/api/research/status/{job_id}` that:
    *   Accepts a Celery `job_id`.
    *   Authenticates the user.
    *   Retrieves the current state and meta-information of the corresponding Celery task.
    *   Returns a JSON response containing the task status, progress message, current phase, and potentially a link to the Google Drive folder upon success.

## 4. Dependencies
*   Task 3.1: Backend - Celery & Redis Setup (for `celery_app` and `AsyncResult`).
*   Task 5.1: Backend - `/api/research/start` Endpoint (initiates the task and provides the `job_id`).
*   The `research_orchestrator_task` (within Task 5.1) must implement `self.update_state` calls with meaningful `meta` data.
*   Task 1.4: Frontend - Token Handling & Authenticated State (for `get_current_user` dependency).

## 5. Acceptance Criteria
*   Sending a GET request to `/api/research/status/{job_id}` (with authentication) returns the current status of the task.
*   The `progress_message` and `current_phase` fields in the response update as the Celery task progresses.
*   Upon task completion (`SUCCESS`), the `result_link` (Google Drive folder link) is present in the response.
*   Upon task failure (`FAILURE`), an `error` message is present.
*   Unauthorized requests to the endpoint are rejected.
*   Requests for `job_id`s not belonging to the user (if authorization is implemented) are rejected.

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **Polling Interval:** The frontend will poll this endpoint. Consider a reasonable polling interval to balance responsiveness and backend load.
*   **WebSockets (Future Enhancement):** For true real-time updates without polling, WebSockets could be implemented (e.g., using FastAPI's WebSocket support and a Redis Pub/Sub channel for Celery events). This is out of scope for the initial plan.
*   **Celery Flower:** For development and monitoring, Celery Flower is an excellent tool that provides a web UI to monitor Celery tasks and workers. It can be run as a separate Docker service.
# Task 5.4: Frontend - API Call to Start Research

**Phase:** Phase 5: API Endpoints & Frontend-Backend Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Implement the frontend logic to make the API call to the backend's `/api/research/start` endpoint. This involves:
*   Gathering input data (company name, Google Drive folder name).
*   Constructing the HTTP POST request.
*   Handling the response from the backend, specifically extracting the `job_id`.
*   Managing loading and error states related to this API call.

## 2. Detailed Steps / Implementation Notes

1.  **Gather Input Data:**
    *   The `companyName` and `gdriveFolderName` states from Task 5.3 will provide the necessary data.

2.  **Construct and Send POST Request:**
    *   Use the `fetch` API or a library like `axios` (if installed) to send a POST request to `${process.env.NEXT_PUBLIC_API_BASE_URL}/research/start`.
    *   The request body should be a JSON object containing `company_name` and `gdrive_folder_name`.
    *   **Authentication Header:** Include an `Authorization` header if the backend uses token-based authentication (e.g., JWTs). The token would be retrieved from the `authStore` (Task 1.4).
        ```typescript
        // Excerpt from handleStartResearch in Task 5.3
        // Assuming useAuthStore provides an accessToken if using JWTs
        // const { accessToken } = useAuthStore.getState(); // Get token from store

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/research/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // If using JWTs:
                // 'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
                company_name: companyName,
                gdrive_folder_name: gdriveFolderName,
            }),
        });
        ```

3.  **Handle Response:**
    *   Check `response.ok` to determine if the request was successful (HTTP status 2xx).
    *   Parse the JSON response.
    *   If successful, extract the `job_id` from the response. This `job_id` is crucial for polling the status endpoint (Task 5.5).
        ```typescript
        // Excerpt from handleStartResearch in Task 5.3
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to start research.');
        }

        const data = await response.json();
        setJobId(data.job_id); // Update state with job_id
        ```

4.  **Manage Loading and Error States:**
    *   Set an `isResearching` state to `true` before the API call and `false` after it completes (success or failure). This disables the button and provides visual feedback.
    *   Catch any errors during the `fetch` operation or response parsing and update an `errorMessage` state to display user-friendly messages.

## 3. Expected Output / Deliverables
*   Frontend logic within the main interface component that successfully sends a POST request to `/api/research/start`.
*   The `job_id` returned by the backend is captured and stored in the frontend state.
*   Loading indicators and error messages are correctly managed and displayed.

## 4. Dependencies
*   Task 5.3: Frontend - Main Interface UI (provides the UI elements and state for inputs).
*   Task 5.1: Backend - `/api/research/start` Endpoint (the target API).
*   Task 1.4: Frontend - Token Handling & Authenticated State (for authentication headers if needed).

## 5. Acceptance Criteria
*   Clicking the "Start Research" button sends a valid POST request to the backend.
*   The frontend correctly receives and stores the `job_id` from a successful backend response.
*   The UI reflects the loading state during the API call.
*   Error messages from the backend are displayed on the UI if the API call fails.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   **API Base URL:** Ensure `NEXT_PUBLIC_API_BASE_URL` is correctly configured in `frontend/.env` for development and deployment.
*   **Error Handling Granularity:** Consider more specific error handling based on different HTTP status codes (e.g., 400 for bad request, 401 for unauthorized, 500 for server errors).
*   **User Feedback:** Beyond disabling the button, consider a small spinner or text change on the button itself to indicate activity.
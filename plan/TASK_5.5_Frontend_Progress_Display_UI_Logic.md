# Task 5.5: Frontend - Progress Display UI & Logic

**Phase:** Phase 5: API Endpoints & Frontend-Backend Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Develop the UI area and logic to display real-time progress updates for the research task. This involves:
*   Polling the backend's `/api/research/status/{job_id}` endpoint.
*   Updating the UI with messages, current phase, and overall status.
*   Displaying a direct link to the Google Drive folder upon completion.

## 2. Detailed Steps / Implementation Notes

1.  **Create Progress Display Component (`frontend/src/components/ResearchProgress.tsx`):**
    *   This component will receive the `jobId` as a prop.
    *   Use `useState` to manage the progress data (status, message, phase, link, error).
    *   Use `useEffect` with `setInterval` to implement polling.
        ```tsx
        // Example: frontend/src/components/ResearchProgress.tsx
        'use client';
        import React, { useState, useEffect } from 'react';

        interface ResearchProgressProps {
          jobId: string;
        }

        interface ResearchStatus {
          job_id: string;
          status: string; // PENDING, PROGRESS, SUCCESS, FAILURE, etc.
          info: any; // Raw info from Celery meta
          progress_message: string;
          current_phase: string;
          result_link?: string;
          error?: string;
        }

        export default function ResearchProgress({ jobId }: ResearchProgressProps) {
          const [status, setStatus] = useState<ResearchStatus | null>(null);
          const [loading, setLoading] = useState(true);
          const [error, setError] = useState<string | null>(null);

          useEffect(() => {
            if (!jobId) {
              setLoading(false);
              return;
            }

            const fetchStatus = async () => {
              try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/research/status/${jobId}`, {
                  headers: {
                    // Add Authorization header if using JWTs
                    // 'Authorization': `Bearer ${accessToken}`, // Get from authStore
                  },
                });

                if (!response.ok) {
                  const errorData = await response.json();
                  throw new Error(errorData.detail || 'Failed to fetch status.');
                }

                const data: ResearchStatus = await response.json();
                setStatus(data);
                setLoading(false);

                // Stop polling if task is complete or failed
                if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
                  clearInterval(intervalId);
                }
              } catch (err: any) {
                setError(err.message || 'An error occurred while fetching status.');
                setLoading(false);
                clearInterval(intervalId); // Stop polling on error
              }
            };

            // Initial fetch
            fetchStatus();

            // Set up polling interval (e.g., every 3 seconds)
            const intervalId = setInterval(fetchStatus, 3000);

            // Cleanup on component unmount
            return () => clearInterval(intervalId);
          }, [jobId]); // Re-run effect if jobId changes

          if (loading) {
            return (
              <div className="mt-6 p-4 border border-gray-200 rounded-md bg-gray-50 text-center">
                <p className="font-semibold">Loading research status...</p>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mt-2"></div>
              </div>
            );
          }

          if (error) {
            return (
              <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md" role="alert">
                <strong className="font-bold">Error:</strong>
                <span className="block sm:inline"> {error}</span>
              </div>
            );
          }

          if (!status) {
            return null; // Should not happen if loading is false and no error
          }

          return (
            <div className="mt-6 p-4 border border-gray-200 rounded-md bg-gray-50">
              <h3 className="text-lg font-semibold mb-2">Research Progress:</h3>
              <p><strong>Status:</strong> <span className={`font-bold ${status.status === 'SUCCESS' ? 'text-green-600' : status.status === 'FAILURE' ? 'text-red-600' : 'text-blue-600'}`}>{status.status}</span></p>
              <p><strong>Current Phase:</strong> {status.current_phase || 'N/A'}</p>
              <p><strong>Message:</strong> {status.progress_message || 'Waiting for updates...'}</p>

              {status.status === 'SUCCESS' && status.result_link && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="font-semibold text-green-700">All tasks complete!</p>
                  <p className="text-sm">Research for {status.info?.company_name || 'your prospect'} is available in your Google Drive.</p>
                  <a href={status.result_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                    Open Google Drive Folder
                  </a>
                </div>
              )}

              {status.status === 'FAILURE' && status.error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="font-semibold text-red-700">Research Failed!</p>
                  <p className="text-sm">Error: {status.error}</p>
                </div>
              )}
            </div>
          );
        }
        ```

2.  **Integration into Main Interface (Task 5.3):**
    *   The `ResearchProgress` component will be rendered conditionally in the `DashboardPage` (or main interface) only when a `jobId` is available.
        ```tsx
        // Excerpt from frontend/src/app/dashboard/page.tsx
        // ...
        {jobId && (
            <ResearchProgress jobId={jobId} />
        )}
        // ...
        ```

3.  **Polling Logic:**
    *   The `useEffect` hook will initiate the `fetchStatus` function.
    *   `setInterval` will repeatedly call `fetchStatus` at a defined interval (e.g., 3000ms).
    *   `clearInterval` is crucial for cleanup when the component unmounts or when the task reaches a terminal state (`SUCCESS` or `FAILURE`).

4.  **Displaying Progress:**
    *   The UI will dynamically update based on the `status` object received from the backend.
    *   Use conditional rendering to show different messages/elements based on `status.status` (e.g., loading spinner, success message with link, error message).

5.  **Direct Link to Google Drive:**
    *   When `status.status` is `SUCCESS`, display the `result_link` provided by the backend.

## 3. Expected Output / Deliverables
*   A React component (`ResearchProgress`) that polls the backend for task status.
*   The component displays real-time progress messages, current phase, and overall status.
*   Upon successful completion, a direct link to the Google Drive output folder is displayed.
*   Clear error messages are displayed if the research task fails.

## 4. Dependencies
*   Task 5.2: Backend - `/api/research/status/{job_id}` Endpoint (the API this component polls).
*   Task 5.3: Frontend - Main Interface UI (where this component will be rendered).
*   Task 1.4: Frontend - Token Handling & Authenticated State (for authentication headers if needed).
*   The `research_orchestrator_task` (within Task 5.1) must correctly update its state with `meta` information and return the `result_link` upon success.

## 5. Acceptance Criteria
*   After initiating research, the progress display appears.
*   The progress messages and phase updates reflect the actual state of the backend Celery task.
*   Upon successful completion, the "All tasks complete!" message appears, along with a clickable link to the Google Drive folder.
*   If the task fails, an appropriate error message is displayed.
*   Polling stops when the task is complete (success or failure).

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **Polling Interval:** Adjust the `setInterval` duration based on desired responsiveness and backend load.
*   **User Experience:** Consider adding a visual progress bar or more detailed step-by-step indicators if the `meta` data from Celery allows for it.
*   **Error Handling:** Ensure network errors during polling are handled gracefully without crashing the UI.
*   **Authorization for Polling:** Remember that the status endpoint is protected, so the frontend's `fetch` request must include the necessary authentication headers.
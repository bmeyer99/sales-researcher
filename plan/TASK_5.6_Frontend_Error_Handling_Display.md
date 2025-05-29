# Task 5.6: Frontend - Error Handling Display

**Phase:** Phase 5: API Endpoints & Frontend-Backend Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Ensure clear, user-friendly error messages are displayed on the frontend for any failures that occur during the application workflow. This includes:
*   Errors from API calls (e.g., failed research initiation, status polling errors).
*   Errors reported by the backend Celery tasks.
*   General client-side errors.

## 2. Detailed Steps / Implementation Notes

1.  **Centralized Error State Management (Optional but Recommended):**
    *   For more complex applications, a global error state in Zustand or React Context can be useful to display persistent notifications (toasts, banners).
    *   For this project, displaying errors directly within the relevant components (Login, Dashboard, Progress) is likely sufficient.

2.  **Error Display in Login Page (Task 1.3):**
    *   If the backend's `/auth/google/login` or `/auth/google/callback` encounters an error, it should redirect back to the frontend's login page with an error parameter in the URL (e.g., `/login?error=auth_failed`).
    *   The Login page component should read this parameter and display an appropriate message.
        ```tsx
        // Example: frontend/src/app/login/page.tsx
        'use client';
        import React, { useEffect, useState } from 'react';
        import { useSearchParams } from 'next/navigation'; // For App Router

        export default function LoginPage() {
          const searchParams = useSearchParams();
          const [displayError, setDisplayError] = useState<string | null>(null);

          useEffect(() => {
            const errorParam = searchParams.get('error');
            if (errorParam) {
              // Map error codes to user-friendly messages
              switch (errorParam) {
                case 'auth_failed':
                  setDisplayError('Authentication failed. Please try again.');
                  break;
                case 'access_denied':
                  setDisplayError('You denied access to your Google account. Please grant access to use the application.');
                  break;
                case 'invalid_state':
                  setDisplayError('Security error during authentication. Please try again.');
                  break;
                default:
                  setDisplayError('An unexpected authentication error occurred.');
              }
            }
          }, [searchParams]);

          // ... rest of LoginPage component ...

          return (
            // ...
            {displayError && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong className="font-bold">Error:</strong>
                <span className="block sm:inline"> {displayError}</span>
              </div>
            )}
            // ...
          );
        }
        ```

3.  **Error Display in Main Interface (Task 5.3):**
    *   The `handleStartResearch` function already includes `errorMessage` state to capture and display errors from the `/api/research/start` endpoint.
    *   Ensure this error message is prominently displayed.
        ```tsx
        // Excerpt from frontend/src/app/dashboard/page.tsx (Task 5.3)
        // ...
        {errorMessage && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">Error:</strong>
              <span className="block sm:inline"> {errorMessage}</span>
            </div>
        )}
        // ...
        ```

4.  **Error Display in Progress Component (Task 5.5):**
    *   The `ResearchProgress` component already includes `error` state to capture and display errors from the `/api/research/status/{job_id}` endpoint.
    *   It also displays `status.error` if the Celery task itself reports a `FAILURE` state.
        ```tsx
        // Excerpt from frontend/src/components/ResearchProgress.tsx (Task 5.5)
        // ...
        {status.status === 'FAILURE' && status.error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="font-semibold text-red-700">Research Failed!</p>
              <p className="text-sm">Error: {status.error}</p>
            </div>
        )}
        // ...
        ```

5.  **User-Friendly Messages:**
    *   Translate technical error messages into clear, actionable, and user-friendly language.
    *   Avoid exposing raw stack traces or internal server errors to the user. The backend should return concise error details.

6.  **Logging Client-Side Errors:**
    *   Consider implementing client-side error logging (e.g., using a service like Sentry or a simple `console.error` for development) to capture unhandled JavaScript errors.

## 3. Expected Output / Deliverables
*   Clear and user-friendly error messages displayed on the frontend for:
    *   Authentication failures.
    *   Failed research initiation.
    *   Errors during status polling.
    *   Errors reported by the backend Celery tasks.
*   Error messages are styled appropriately (e.g., red background, bold text).

## 4. Dependencies
*   Task 1.3: Frontend - Login UI & Logic.
*   Task 5.3: Frontend - Main Interface UI.
*   Task 5.5: Frontend - Progress Display UI & Logic.
*   Backend endpoints (Task 1.2, 5.1, 5.2) should return appropriate error messages/details.

## 5. Acceptance Criteria
*   When an authentication error occurs (e.g., user denies access), a clear message is shown on the login page.
*   If the "Start Research" API call fails, an error message appears on the main interface.
*   If the research task fails (as reported by the status endpoint), the progress display shows a clear error message.
*   Error messages are easy for a non-technical user to understand.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   **Backend Error Responses:** The backend should consistently return structured error responses (e.g., JSON with `detail` field) to make frontend parsing easier.
*   **Error Mapping:** For more complex errors, a mapping from backend error codes to frontend user messages can be implemented.
*   **Toast Notifications:** For non-critical errors or temporary feedback, toast notifications (e.g., using a library like `react-hot-toast`) can provide a less intrusive user experience.
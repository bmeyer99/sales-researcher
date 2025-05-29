# Task 5.3: Frontend - Main Interface UI

**Phase:** Phase 5: API Endpoints & Frontend-Backend Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Develop the main user interface (UI) page that authenticated users will see after logging in. This page will include:
*   A component for Google Drive folder selection (from Task 2.4).
*   A text input field for the prospect company name.
*   A "Start Research" button to initiate the research workflow.
*   Placeholder for progress display (to be implemented in Task 5.5).

## 2. Detailed Steps / Implementation Notes

1.  **Create Main Page Component:**
    *   This will likely be the default authenticated route, e.g., `frontend/src/app/dashboard/page.tsx` or `frontend/src/app/page.tsx` if the root is protected.
    *   Ensure this page is protected (using `ProtectedRoute` from Task 1.4).
        ```tsx
        // Example: frontend/src/app/dashboard/page.tsx
        'use client';
        import React, { useState } from 'react';
        import ProtectedRoute from '@/components/ProtectedRoute'; // From Task 1.4
        import GoogleDriveFolderInput from '@/components/GoogleDriveFolderInput'; // From Task 2.4 (Option A)
        // import { useAuthStore } from '@/store/authStore'; // If needed for user info

        export default function DashboardPage() {
          const [companyName, setCompanyName] = useState('');
          const [gdriveFolderName, setGdriveFolderName] = useState('');
          const [isResearching, setIsResearching] = useState(false);
          const [jobId, setJobId] = useState<string | null>(null);
          const [errorMessage, setErrorMessage] = useState<string | null>(null);

          // const { user } = useAuthStore(); // Access user info if needed for display

          const handleStartResearch = async () => {
            setErrorMessage(null);
            setIsResearching(true);
            setJobId(null); // Clear previous job ID

            try {
              const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/research/start`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  // Add Authorization header if using JWTs or other token-based auth
                  // 'Authorization': `Bearer ${user?.accessToken}` // Example if frontend manages token
                },
                body: JSON.stringify({
                  company_name: companyName,
                  gdrive_folder_name: gdriveFolderName,
                }),
              });

              if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start research.');
              }

              const data = await response.json();
              setJobId(data.job_id);
              // Research started, now Task 5.5 will poll for status
            } catch (error: any) {
              setErrorMessage(error.message || 'An unexpected error occurred.');
              setIsResearching(false);
            }
          };

          return (
            <ProtectedRoute>
              <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-100">
                <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                  <h1 className="text-2xl font-bold text-center mb-6">Automated Sales Prospect Research</h1>

                  {/* User Info (Optional) */}
                  {/* {user && <p className="text-center text-gray-600 mb-4">Welcome, {user.name}!</p>} */}

                  <div className="mb-4">
                    <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">
                      Prospect Company Name:
                    </label>
                    <input
                      type="text"
                      id="companyName"
                      name="companyName"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="e.g., Acme Corp"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>

                  {/* Google Drive Folder Input (from Task 2.4) */}
                  <GoogleDriveFolderInput
                    folderName={gdriveFolderName}
                    onFolderNameChange={setGdriveFolderName}
                  />

                  {errorMessage && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                      <strong className="font-bold">Error:</strong>
                      <span className="block sm:inline"> {errorMessage}</span>
                    </div>
                  )}

                  <button
                    onClick={handleStartResearch}
                    disabled={isResearching || !companyName || !gdriveFolderName}
                    className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                      isResearching ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                    }`}
                  >
                    {isResearching ? 'Starting Research...' : 'Start Research'}
                  </button>

                  {/* Placeholder for Progress Display (Task 5.5) */}
                  {jobId && (
                    <div className="mt-6 p-4 border border-gray-200 rounded-md bg-gray-50">
                      <p className="font-semibold">Research Job Initiated!</p>
                      <p>Job ID: <span className="font-mono text-sm">{jobId}</span></p>
                      <p className="text-sm text-gray-600">Monitoring progress...</p>
                      {/* Progress component will go here */}
                    </div>
                  )}
                </div>
              </main>
            </ProtectedRoute>
          );
        }
        ```

2.  **Input Fields and State:**
    *   Use `useState` hooks to manage the `companyName` and `gdriveFolderName` input values.
    *   Implement basic validation (e.g., ensure fields are not empty before enabling the button).

3.  **"Start Research" Button:**
    *   The button's `onClick` handler will call an asynchronous function (`handleStartResearch`).
    *   This function will make an API call to the backend's `/api/research/start` endpoint (Task 5.4).
    *   Disable the button while research is being initiated (`isResearching` state).

4.  **Styling:**
    *   Apply Tailwind CSS classes for a clean and responsive layout.

5.  **Error Display:**
    *   Display any error messages returned from the backend or caught during the API call.

## 3. Expected Output / Deliverables
*   A main frontend page (e.g., `dashboard/page.tsx`) that serves as the primary interface for initiating research.
*   The page includes:
    *   A text input for "Prospect Company Name".
    *   The `GoogleDriveFolderInput` component for folder selection.
    *   A "Start Research" button.
*   Basic state management for input fields and button loading state.
*   Error messages are displayed to the user.

## 4. Dependencies
*   Task 1.4: Frontend - Token Handling & Authenticated State (for `ProtectedRoute`).
*   Task 2.4: Frontend - Google Drive Folder Picker / Input (for `GoogleDriveFolderInput` component).
*   Task 5.1: Backend - `/api/research/start` Endpoint (the endpoint this UI will call).

## 5. Acceptance Criteria
*   The main interface page loads correctly for authenticated users.
*   All input fields and the "Start Research" button are present and functional.
*   User input for company name and folder name is captured correctly.
*   The "Start Research" button is disabled when fields are empty or during API call.
*   Clicking the button triggers the API call to the backend.
*   Error messages from the API call are displayed on the UI.

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **User Experience:** Consider adding clear labels, placeholders, and possibly tooltips to guide the user.
*   **Form Validation:** Implement more robust client-side validation (e.g., minimum length, character restrictions) before sending data to the backend.
*   **Loading Indicators:** Provide visual feedback (e.g., spinners) when the "Start Research" button is clicked and the API call is in progress.
*   **API Base URL:** Ensure `process.env.NEXT_PUBLIC_API_BASE_URL` is correctly configured for the frontend to communicate with the backend.
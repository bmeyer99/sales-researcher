# Task 2.4: Frontend - Google Drive Folder Picker / Input

**Phase:** Phase 2: Google Drive Integration
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Implement the UI component on the frontend that allows the user to specify the destination Google Drive folder for the research output. Two options are considered:
*   **Option A (Simpler Initial Approach):** A simple text input field where the user types the desired folder name. The backend can then create this folder under a predefined application root folder (e.g., "/Sales Research Tool Output/") or directly in the user's "My Drive".
*   **Option B (Advanced UX):** Integrate the Google Drive Picker API to provide a visual folder selection experience for the user.

This task will primarily focus on detailing Option A for initial implementation, with Option B outlined as an enhancement.

## 2. Detailed Steps / Implementation Notes

### Option A: Simple Text Input for Folder Name

1.  **UI Component (`frontend/src/components/GoogleDriveFolderInput.tsx` or similar):**
    *   Create a React component that includes a label and a text input field.
    *   The input field will be used to capture the desired folder name from the user.
    *   Manage the input's state (e.g., using `useState`).
        ```tsx
        // Example: frontend/src/components/GoogleDriveFolderInput.tsx
        'use client';
        import React, { useState } from 'react';

        interface GoogleDriveFolderInputProps {
          folderName: string;
          onFolderNameChange: (name: string) => void;
          label?: string;
          placeholder?: string;
        }

        export default function GoogleDriveFolderInput({
          folderName,
          onFolderNameChange,
          label = "Destination Folder Name in Google Drive:",
          placeholder = "e.g., My Prospect Research"
        }: GoogleDriveFolderInputProps) {
          return (
            <div className="mb-4">
              <label htmlFor="gdriveFolderName" className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <input
                type="text"
                id="gdriveFolderName"
                name="gdriveFolderName"
                value={folderName}
                onChange={(e) => onFolderNameChange(e.target.value)}
                placeholder={placeholder}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
              <p className="mt-1 text-xs text-gray-500">
                This folder will be created in your Google Drive (e.g., under "Sales Research Tool Output/{'{Your Folder Name}'}").
              </p>
            </div>
          );
        }
        ```

2.  **Integration into Main Form:**
    *   Include this `GoogleDriveFolderInput` component in the main research form (Task 5.3).
    *   The main form will hold the state for the folder name and pass it to the `/api/research/start` backend endpoint.

3.  **Backend Handling:**
    *   The backend (Task 2.2) will receive this folder name. It will then use its logic to find or create this folder, potentially within a predefined application root folder like "Sales Research Tool Output".

### Option B: Google Drive Picker API Integration (Advanced UX - for future enhancement)

1.  **Google API Client Library for JavaScript:**
    *   Ensure the Google API Client Library for JavaScript (`gapi`) and the Google Identity Services library (`gis`) are loaded on the frontend. This can be done via a script tag in `layout.tsx` or dynamically.
        ```html
        <!-- Example script tags (place in <head> or before </body> in layout) -->
        <!-- <script async defer src="https://apis.google.com/js/api.js"></script> -->
        <!-- <script async defer src="https://accounts.google.com/gsi/client"></script> -->
        ```
    *   Modern approach often involves using the `useGoogleApi` hook from `@react-oauth/google` or similar abstractions if available for the Picker.

2.  **Frontend Logic for Picker:**
    *   **Load Picker API:** Use `gapi.load('picker', callback)` to load the picker API.
    *   **Obtain Access Token:** The Picker API requires an OAuth 2.0 access token for the current user with appropriate Drive scopes (e.g., `https://www.googleapis.com/auth/drive.readonly` or `https://www.googleapis.com/auth/drive.file` if allowing creation of new folders from picker). This token would be available from the frontend auth state if the backend passes it, or the frontend might need to request it specifically for the picker.
    *   **Developer Key:** A Google API Developer Key (separate from OAuth Client ID) is required to use the Picker API. This should be an environment variable `NEXT_PUBLIC_GOOGLE_API_KEY`.
    *   **Create Picker Instance:**
        ```javascript
        // Conceptual JavaScript for creating a picker
        // function createPicker(accessToken, apiKey, callback) {
        //   if (gapi && gapi.client && google && google.picker) { // Ensure APIs are loaded
        //     const view = new google.picker.View(google.picker.ViewId.FOLDERS);
        //     view.setMimeTypes("application/vnd.google-apps.folder");
        //     view.setSelectFolderEnabled(true);
        //
        //     const picker = new google.picker.PickerBuilder()
        //       .addView(view)
        //       .setOAuthToken(accessToken)
        //       .setDeveloperKey(apiKey)
        //       .setCallback(callback) // Callback function when user selects or cancels
        //       .build();
        //     picker.setVisible(true);
        //   } else {
        //      // Handle API not loaded
        //   }
        // }
        ```
    *   **Picker Callback:** The callback function receives data from the picker, including the ID of the selected folder (`google.picker.Action.PICKED`) or if the user cancelled (`google.picker.Action.CANCEL`).
    *   Store the selected folder ID in the frontend state.

3.  **UI Component for Picker:**
    *   A button like "Select Google Drive Folder".
    *   `onClick`, it would trigger the logic to create and show the picker.
    *   Display the name/path of the selected folder.

4.  **Backend Handling:**
    *   The frontend sends the selected `folderId` to the `/api/research/start` endpoint. The backend can then use this ID directly.

## 3. Expected Output / Deliverables

*   **For Option A (Initial):**
    *   A React component for text input of the Google Drive folder name.
    *   This component integrated into the main research form.
    *   The folder name is passed to the backend when research is initiated.
*   **For Option B (Future):**
    *   A button and associated logic to launch the Google Drive Picker.
    *   Ability to select a folder from the user's Drive.
    *   The selected folder's ID is captured and available to be sent to the backend.

## 4. Dependencies
*   **For Option A:**
    *   Task 0.4: Setup Frontend (Next.js) - Basic Structure.
    *   Task 5.3: Frontend - Main Interface UI (where this input will be placed).
*   **For Option B:**
    *   Task 1.4: Frontend - Token Handling & Authenticated State (to get user's access token for the picker).
    *   Task 0.5: Environment Variable Management (for `NEXT_PUBLIC_GOOGLE_API_KEY`).
    *   Google API Client Library and Google Identity Services library loaded on the frontend.

## 5. Acceptance Criteria
*   **For Option A:**
    *   User can type a folder name into the input field.
    *   The entered folder name is correctly captured in the frontend state.
*   **For Option B:**
    *   The Google Drive Picker launches successfully.
    *   User can browse and select a folder.
    *   The ID of the selected folder is correctly captured.

## 6. Estimated Effort (Optional)
*   **Option A:** Small
*   **Option B:** Medium to Large (Picker API integration can be tricky with auth and API loading).

## 7. Notes / Questions
*   **Initial Focus:** Start with Option A for simplicity to get the end-to-end flow working. Option B can be a significant UX improvement later.
*   **Security for Picker (Option B):** The Picker API requires an access token. Ensure this is handled securely on the frontend. The token should have the minimal scopes necessary for the picker's functionality.
*   **Error Handling (Option B):** Handle cases where the Picker API fails to load, the user doesn't have necessary permissions, or cancels the picker.
# Task 1.3: Frontend - Login UI & Logic

**Phase:** Phase 1: Authentication (Google OAuth 2.0)
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create the Login page/component in the Next.js frontend. This page will feature a "Sign in with Google" button. The primary method for initiating the Google Sign-In will be by redirecting to the backend's `/auth/google/login` endpoint. The `@react-oauth/google` library can be used for UI components or to simplify obtaining an authorization code if a frontend-initiated flow (backend hybrid) is chosen, but the primary plan is backend-driven redirection.

## 2. Detailed Steps / Implementation Notes

1.  **Install `@react-oauth/google`:**
    *   If not already installed during Next.js setup or manually, add it to the `frontend` project:
        ```bash
        npm install @react-oauth/google
        # OR
        yarn add @react-oauth/google
        ```

2.  **Configure `GoogleOAuthProvider`:**
    *   Wrap the application (or relevant parts) with `GoogleOAuthProvider` in `frontend/src/app/layout.tsx` or a specific auth layout component.
    *   The `clientId` prop will be required, which should come from an environment variable (e.g., `NEXT_PUBLIC_GOOGLE_CLIENT_ID` defined in Task 0.5).
        ```tsx
        // Example in frontend/src/app/layout.tsx
        import { GoogleOAuthProvider } from '@react-oauth/google';

        export default function RootLayout({ children }: { children: React.ReactNode }) {
          const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

          if (!googleClientId) {
            // Handle missing client ID - perhaps render an error or a disabled login
            console.error("Google Client ID is not configured.");
            // return <SomeErrorComponent />; // Or just let it fail if provider handles it
          }

          return (
            <html lang="en">
              <body>
                {googleClientId ? (
                  <GoogleOAuthProvider clientId={googleClientId}>
                    {children}
                  </GoogleOAuthProvider>
                ) : (
                  // Render a fallback or error if client ID is missing
                  <div>Error: Google Client ID not configured. Login is unavailable.</div>
                )}
              </body>
            </html>
          );
        }
        ```

3.  **Create Login Page/Component:**
    *   Create a new route for login, e.g., `frontend/src/app/login/page.tsx`.
    *   This page should be simple, primarily displaying the "Sign in with Google" button.
    *   **Option A (Primary - Backend Redirect):**
        *   The button, when clicked, simply navigates or redirects the browser to the backend's `/auth/google/login` endpoint (e.g., `http://localhost:8000/auth/google/login`).
        *   This can be a simple anchor tag or a button with an `onClick` handler that does `window.location.href = 'http://localhost:8000/auth/google/login';`.
        *   The backend then handles the entire OAuth dance with Google.
        ```tsx
        // frontend/src/app/login/page.tsx (Backend Redirect Approach)
        import React from 'react';

        export default function LoginPage() {
          const backendLoginUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/google/login`;

          return (
            <div className="flex min-h-screen flex-col items-center justify-center">
              <h1 className="text-3xl font-bold mb-8">Sign In</h1>
              <a
                href={backendLoginUrl}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded inline-flex items-center"
              >
                {/* You can use an SVG or an image for the Google icon */}
                <svg className="fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48px" height="48px"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/><path fill="none" d="M0 0h48v48H0z"/></svg>
                <span>Sign in with Google</span>
              </a>
              <p className="mt-4 text-sm text-gray-600">
                You will be redirected to Google to sign in.
              </p>
            </div>
          );
        }
        ```
    *   **Option B (Alternative - Frontend Initiated Code Flow with `@react-oauth/google`):**
        *   Use the `useGoogleLogin` hook from `@react-oauth/google` to get an authorization code on the frontend.
        *   The `onSuccess` callback of `useGoogleLogin` would receive the `code`.
        *   The frontend then sends this `code` to a new backend endpoint (e.g., `/auth/google/exchange-code`).
        *   The backend then exchanges this code for tokens with Google. This is a hybrid approach.
        *   *This option adds more frontend complexity and another backend endpoint. The primary plan (Option A) is simpler.*

4.  **Handle Post-Login Redirect:**
    *   After successful authentication via the backend (Task 1.2), the backend will redirect the user to a frontend page (e.g., `/dashboard` or `/`).
    *   This page should then be aware of the authenticated state (Task 1.4).

## 3. Expected Output / Deliverables
*   `@react-oauth/google` library installed in the frontend.
*   `GoogleOAuthProvider` configured in the Next.js application.
*   A functional Login page/component (`/login`) with a "Sign in with Google" button.
*   Clicking the button successfully redirects the user to the backend's `/auth/google/login` endpoint (or initiates the chosen OAuth flow).

## 4. Dependencies
*   Task 0.4: Setup Frontend (Next.js) - Basic Structure.
*   Task 0.5: Environment Variable Management (for `NEXT_PUBLIC_GOOGLE_CLIENT_ID` and `NEXT_PUBLIC_API_BASE_URL`).
*   Task 1.2: Backend - OAuth Endpoints (the `/auth/google/login` endpoint must be ready).

## 5. Acceptance Criteria
*   The Login page renders correctly.
*   The "Sign in with Google" button is visible and functional.
*   Clicking the button initiates the Google OAuth flow by redirecting to the backend login URL.
*   `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is correctly used by `GoogleOAuthProvider`.

## 6. Estimated Effort (Optional)
*   Small to Medium

## 7. Notes / Questions
*   The primary approach is to let the backend handle the full OAuth redirect flow for simplicity and security (keeping token exchange server-side).
*   The styling of the button and page can be improved using Tailwind CSS.
*   Ensure `NEXT_PUBLIC_API_BASE_URL` is correctly configured for the frontend to find the backend login endpoint.
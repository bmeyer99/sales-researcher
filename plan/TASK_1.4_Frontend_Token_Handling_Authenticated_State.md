# Task 1.4: Frontend - Token Handling & Authenticated State

**Phase:** Phase 1: Authentication (Google OAuth 2.0)
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Manage authentication state in the frontend after a successful login via the backend. This involves:
*   Determining if the user is authenticated (e.g., by checking for a session cookie set by the backend, or by validating a JWT if issued).
*   Using Zustand to store and manage the authenticated state (user profile, tokens if applicable).
*   Implementing protected routes/components that are only accessible to authenticated users.
*   Handling logout.

## 2. Detailed Steps / Implementation Notes

1.  **Define Authenticated State in Zustand Store:**
    *   Expand the `authStore` (e.g., `frontend/src/store/authStore.ts` created conceptually in Task 0.4).
    *   The store should hold user information (e.g., name, email, picture) and authentication status.
    *   If the backend issues JWTs, the store might also hold the JWT and refresh token. If using server-side sessions with cookies, the frontend might not need to store tokens directly, but rather just the user profile and auth status.
        ```typescript
        // frontend/src/store/authStore.ts
        import { create } from 'zustand';
        import { persist, createJSONStorage } from 'zustand/middleware'; // Optional: for persisting state

        interface UserProfile {
          id?: string; // Or 'sub' from Google
          name?: string | null;
          email?: string | null;
          picture?: string | null;
        }

        interface AuthState {
          isAuthenticated: boolean;
          user: UserProfile | null;
          // accessToken?: string | null; // If frontend needs to manage it
          // refreshToken?: string | null; // If frontend needs to manage it
          isLoading: boolean; // To handle initial auth check
          login: (user: UserProfile /*, tokens?: { access: string; refresh: string } */) => void;
          logout: () => void;
          checkAuthStatus: () => Promise<void>; // Function to verify session with backend
          setLoading: (loading: boolean) => void;
        }

        export const useAuthStore = create<AuthState>()(
          // persist( // Optional: persist auth state to localStorage
            (set, get) => ({
              isAuthenticated: false,
              user: null,
              isLoading: true,
              // accessToken: null,
              // refreshToken: null,

              login: (userData /*, tokenData */) => {
                set({
                  isAuthenticated: true,
                  user: userData,
                  // accessToken: tokenData?.access,
                  // refreshToken: tokenData?.refresh,
                  isLoading: false,
                });
              },

              logout: async () => {
                // Call backend logout endpoint if it exists (to invalidate session/tokens)
                try {
                  // Example: await fetch('/api/auth/logout', { method: 'POST' });
                } catch (error) {
                  console.error("Logout failed on backend:", error);
                }
                set({
                  isAuthenticated: false,
                  user: null,
                  // accessToken: null,
                  // refreshToken: null,
                  isLoading: false,
                });
                // Optionally clear persisted state or redirect to login
                // localStorage.removeItem('auth-storage'); // If using persist middleware
                window.location.href = '/login'; // Or use Next.js router
              },

              checkAuthStatus: async () => {
                get().setLoading(true);
                try {
                  // Make a request to a backend endpoint that requires authentication
                  // (e.g., /api/users/me or /api/auth/status)
                  // This endpoint should return user data if session is valid, or 401/403 otherwise.
                  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/status`); // Example endpoint
                  if (response.ok) {
                    const userData: UserProfile = await response.json();
                    get().login(userData);
                  } else {
                    get().logout(); // Clears auth state if session is invalid
                  }
                } catch (error) {
                  console.error("Auth check failed:", error);
                  get().logout(); // Clears auth state on error
                } finally {
                  get().setLoading(false);
                }
              },
              setLoading: (loading: boolean) => set({ isLoading: loading }),
            }),
          //   { // Configuration for persist middleware (optional)
          //     name: 'auth-storage', // name of the item in the storage (must be unique)
          //     storage: createJSONStorage(() => localStorage), // (optional) by default, 'localStorage' is used
          //   }
          // )
        );
        ```

2.  **Initial Authentication Check:**
    *   When the application loads (e.g., in `RootLayout` or a specific AuthProvider component), call `checkAuthStatus` from the `authStore`.
    *   This function will typically make an API call to a backend endpoint (e.g., `/api/auth/status` or `/api/users/me`) that requires authentication.
    *   If the call is successful, the backend returns user data, and the frontend updates the auth state.
    *   If it fails (e.g., 401 Unauthorized), the user is not authenticated.
        ```tsx
        // Example usage in a client component, e.g., frontend/src/components/AuthInitializer.tsx
        'use client';
        import { useEffect } from 'react';
        import { useAuthStore } from '@/store/authStore';

        export default function AuthInitializer() {
          const checkAuthStatus = useAuthStore((state) => state.checkAuthStatus);
          const isLoading = useAuthStore((state) => state.isLoading);

          useEffect(() => {
            checkAuthStatus();
          }, [checkAuthStatus]);

          if (isLoading) {
            return <div>Loading authentication status...</div>; // Or a spinner
          }

          return null; // This component doesn't render anything itself
        }

        // Then include <AuthInitializer /> in your RootLayout
        ```

3.  **Protected Routes/Components:**
    *   Create a higher-order component (HOC) or a wrapper component that checks `isAuthenticated` from the `authStore`.
    *   If the user is not authenticated, redirect them to the `/login` page.
    *   Next.js middleware can also be used for protecting routes server-side or edge-side.
        ```tsx
        // Example: frontend/src/components/ProtectedRoute.tsx
        'use client';
        import { useEffect } from 'react';
        import { useRouter } from 'next/navigation'; // Use next/navigation for App Router
        import { useAuthStore } from '@/store/authStore';

        interface ProtectedRouteProps {
          children: React.ReactNode;
        }

        export default function ProtectedRoute({ children }: ProtectedRouteProps) {
          const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
          const isLoading = useAuthStore((state) => state.isLoading);
          const router = useRouter();

          useEffect(() => {
            if (!isLoading && !isAuthenticated) {
              router.push('/login');
            }
          }, [isAuthenticated, isLoading, router]);

          if (isLoading) {
            return <div>Loading...</div>; // Or a global loading spinner
          }

          if (!isAuthenticated) {
            return null; // Or a redirect component, though useEffect handles it
          }

          return <>{children}</>;
        }
        ```
    *   Wrap pages or layouts that require authentication with `<ProtectedRoute>`.

4.  **Logout Functionality:**
    *   Provide a logout button in the UI (e.g., in a user dropdown or navigation bar).
    *   The `onClick` handler for the logout button should call the `logout` action from `authStore`.
    *   The `logout` action should:
        *   Clear the authentication state in Zustand.
        *   Optionally, make an API call to a backend endpoint (e.g., `/api/auth/logout`) to invalidate the server-side session or tokens.
        *   Redirect the user to the `/login` page.

5.  **Backend Endpoint for Auth Status (`/auth/status` - needs to be created in backend):**
    *   This backend endpoint (e.g., GET `/auth/status`) should be protected (require authentication).
    *   If the user's session/token is valid, it should return the current user's profile information.
    *   If not authenticated, it should return a 401 or 403 status.

## 3. Expected Output / Deliverables
*   An enhanced Zustand `authStore` capable of storing user profile and authentication status.
*   Mechanism to check authentication status on application load (e.g., by calling a backend `/auth/status` endpoint).
*   A `ProtectedRoute` component or similar mechanism to protect routes/pages.
*   Functional logout capability that clears frontend state and (optionally) calls a backend logout endpoint.
*   Authenticated user information (e.g., name, email) displayed in the UI when logged in.

## 4. Dependencies
*   Task 0.4: Setup Frontend (Next.js) - Basic Structure (Zustand installed).
*   Task 1.2: Backend - OAuth Endpoints (successful login should result in a session/token that the backend can verify).
*   A new backend endpoint (e.g., `/auth/status`) that returns current user info if authenticated.

## 5. Acceptance Criteria
*   The application correctly identifies if a user is authenticated or not upon loading.
*   Protected routes redirect unauthenticated users to the login page.
*   Authenticated users can access protected routes.
*   User profile information is correctly stored in Zustand and can be displayed.
*   Logout functionality works, clears client-side auth state, and redirects to login.

## 6. Estimated Effort (Optional)
*   Medium

## 7. Notes / Questions
*   **Session Management:** The exact implementation of `checkAuthStatus` depends on how the backend manages sessions (cookies vs. JWTs). If using HttpOnly cookies for sessions, the browser will automatically send them, and the backend `/auth/status` endpoint just needs to verify the session.
*   **Loading States:** Properly handle loading states while checking authentication to avoid UI flashes or incorrect redirects.
*   **Persisting Auth State:** Consider using `zustand/middleware/persist` if you want to persist parts of the auth state (like `isAuthenticated` and `user`) in `localStorage` for a smoother UX across page reloads, but be mindful of security implications if storing sensitive tokens this way (generally not recommended for access/refresh tokens). The `checkAuthStatus` call on load is a more secure way to re-validate.
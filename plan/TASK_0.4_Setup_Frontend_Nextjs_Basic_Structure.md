# Task 0.4: Setup Frontend (Next.js) - Basic Structure

**Phase:** Phase 0: Project Setup & Foundational Structure
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-28

## 1. Description
Initialize Next.js application within the `frontend` directory. Setup basic page structure. Install and configure Tailwind CSS and Zustand.

## 2. Detailed Steps / Implementation Notes

1.  **Navigate to Frontend Directory:**
    *   The working directory for these steps should be `/root/sales-researcher/frontend/`.
2.  **Initialize Next.js Application:**
    *   Use `create-next-app` to scaffold a new Next.js project. It's recommended to include TypeScript, ESLint, and Tailwind CSS during the setup if prompted, and use the App Router.
    *   Example command (run from within the `frontend` directory, assuming it's empty or you're initializing into it):
        ```bash
        npx create-next-app@latest . --ts --eslint --tailwind --src-dir --app --import-alias "@/*"
        ```
        *(Adjust flags as needed based on `create-next-app` prompts or project preferences. The `.` indicates the current directory `frontend`)*.
    *   This command will create `package.json`, `tsconfig.json`, `next.config.js`, `tailwind.config.ts`, `postcss.config.js`, and a basic `src/app/page.tsx` and `src/app/layout.tsx`.
3.  **Install Zustand:**
    *   If not already in the `frontend` directory, navigate to it.
    *   Install Zustand using npm or yarn:
        ```bash
        npm install zustand
        # OR
        yarn add zustand
        ```
4.  **Verify Tailwind CSS Integration:**
    *   Ensure `tailwind.config.ts` is present and correctly configured (usually handled by `create-next-app`).
    *   Ensure `src/app/globals.css` (or equivalent) includes Tailwind directives:
        ```css
        @tailwind base;
        @tailwind components;
        @tailwind utilities;
        ```
    *   Modify `src/app/page.tsx` to include some basic Tailwind classes to test.
        Example `src/app/page.tsx`:
        ```tsx
        export default function HomePage() {
          return (
            <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-700 p-24">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-white sm:text-6xl">
                  Sales Prospect Research Tool
                </h1>
                <p className="mt-6 text-lg leading-8 text-slate-300">
                  Automated research powered by Gemini.
                </p>
                {/* Login button/form will go here later */}
              </div>
            </main>
          );
        }
        ```
5.  **Basic Zustand Store (Optional - for early setup):**
    *   Create a simple store to verify Zustand integration, e.g., `src/store/authStore.ts`. This will be expanded in Phase 1.
        ```typescript
        // src/store/authStore.ts
        import { create } from 'zustand';

        interface AuthState {
          isAuthenticated: boolean;
          login: () => void;
          logout: () => void;
        }

        export const useAuthStore = create<AuthState>((set) => ({
          isAuthenticated: false,
          login: () => set({ isAuthenticated: true }),
          logout: () => set({ isAuthenticated: false }),
        }));
        ```

## 3. Expected Output / Deliverables
*   A functional Next.js application in the `frontend` directory.
*   `package.json` file listing Next.js, React, Tailwind CSS, Zustand, and other necessary dependencies.
*   Basic page structure, including `src/app/layout.tsx` and `src/app/page.tsx`.
*   Tailwind CSS configured and working.
*   Zustand installed and a basic store example created.

## 4. Dependencies
*   Task 0.1: Initialize Project Repository (for the `frontend` directory).
*   Task 0.2: Define Basic Docker Configuration (the `frontend/Dockerfile` relies on `package.json` and a build script).

## 5. Acceptance Criteria
*   `frontend/package.json` exists and includes Next.js, React, Tailwind CSS, and Zustand.
*   The Next.js development server can be started (e.g., `npm run dev` or `yarn dev` from the `frontend` directory).
*   The basic home page (`src/app/page.tsx`) renders correctly in a browser at `http://localhost:3000` (when dev server is running) and displays Tailwind-styled content.
*   The basic Zustand store can be imported and used in a component without errors.
*   The frontend service can be built and run via `docker-compose up frontend` (after this task is completed) and the page is accessible via `http://localhost:3000` on the host.

## 6. Estimated Effort (Optional)
*   Small to Medium (depending on familiarity with Next.js setup)

## 7. Notes / Questions
*   The `create-next-app` command is powerful and sets up many best practices. Review its output and generated files.
*   Ensure the `build` script in `package.json` (e.g., `next build`) is correctly configured, as the `frontend/Dockerfile` relies on it.
*   The example `src/app/page.tsx` is a placeholder and will be significantly updated.
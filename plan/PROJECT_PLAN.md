# Project Plan: Automated Sales Prospect Research Tool

**Version:** 1.0
**Date:** 2025-05-28

## 1. Project Objectives 🎯

*   Develop a Dockerized web application for automated sales prospect research.
*   Require user authentication via Google Sign-In for application access and Google Drive integration.
*   Enable users to specify a target company and a Google Drive folder for output.
*   Utilize Gemini Deep Research API for:
    *   **Prospect Deep Dive:** Gather comprehensive company information (technologies, industry, cloud apps, news, roles, challenges) and obtain a *prioritized list of relevant source URLs*.
    *   **Prospect's Competitor Analysis:** Research their competitors and technologies.
    *   **Own Competitor Marketing Analysis:** Analyze how *Palo Alto's* competitors target the prospect's market.
*   Crawl and extract main text from the prioritized URLs, saving into User's GDrive folder as Markdown.
*   Provide real-time progress updates on the UI.
*   Output all generated reports and Markdown files directly to the user's specified Google Drive folder, with minimal caching or storage on the server.

## 2. Technology Stack 💻

*   **Frontend:**
    *   **Framework:** React (with Next.js)
    *   **Styling:** Tailwind CSS
    *   **State Management:** Zustand
    *   **Authentication Handling:** `@react-oauth/google`
*   **Backend:**
    *   **Language:** Python (3.10+)
    *   **Framework:** FastAPI
    *   **Google Authentication & API Client:** `google-auth-oauthlib`, `google-api-python-client`
    *   **Gemini API Integration:** `google-generativeai`
    *   **Web Content Extraction:** `trafilatura`
    *   **Task Queue:** Celery with Redis as the message broker
*   **Containerization:** Docker & Docker Compose
*   **Environment Variables:** `.env` file for local development, injected in Docker for deployment.

## 3. Application Workflow & UI 🌊

1.  **Login Screen:**
    *   "Sign in with Google" button.
    *   Mandatory authentication.
2.  **Main Interface (Post-Login):**
    *   Google Drive Folder Picker (browse/select or specify new folder name, e.g., "/Sales Research Tool Output/").
    *   Company Name Input (text field).
    *   "Start Research" Button.
3.  **Processing & Progress (UI Updates):**
    *   "Authenticating with Google Drive..."
    *   "Creating research folder: \[Folder Name]..."
    *   "Phase 1: Researching [Company Name] overview with Gemini..."
    *   "Phase 1: Complete. Overview saved to Google Drive."
    *   "Phase 2: Analyzing [Company Name]'s competitors with Gemini..."
    *   "Phase 2: Complete. Competitor analysis saved."
    *   "Phase 3: Analyzing our competitive marketing for [Company Name]'s segment..."
    *   "Phase 3: Complete. Marketing analysis saved."
    *   "Phase 4: Extracting content from [X] source URLs..." (e.g., X/Y URLs processed)
    *   "Phase 4: Complete. Detailed articles saved as Markdown."
    *   "All tasks complete! Research for [Company Name] is available in your Google Drive."
    *   Direct link to the Google Drive folder.
4.  **Error Handling:** User-friendly messages for failures.

## 4. Detailed Development Plan & Tasks

This section breaks down the project into phases and actionable tasks. Each task will be further detailed when we start working on it.

### Phase 0: Project Setup & Foundational Structure

*   **Task 0.1: Initialize Project Repository**
    *   Description: Set up Git repository. Create initial directory structure (`frontend`, `backend`, `docs`, `plan`).
    *   Output: Initialized Git repo with basic folder structure.
*   **Task 0.2: Define Basic Docker Configuration**
    *   Description: Create initial `docker-compose.yml` for frontend, backend, and Redis. Create basic `Dockerfile` for frontend (Next.js) and backend (Python/FastAPI).
    *   Output: `docker-compose.yml`, `frontend/Dockerfile`, `backend/Dockerfile`, `redis/Dockerfile` (if custom).
*   **Task 0.3: Setup Backend (FastAPI) - Basic Structure**
    *   Description: Initialize FastAPI application. Create basic "hello world" endpoint. Setup `requirements.txt` or `pyproject.toml` (Poetry/PDM).
    *   Output: Functional basic FastAPI app.
*   **Task 0.4: Setup Frontend (Next.js) - Basic Structure**
    *   Description: Initialize Next.js application. Setup basic page structure. Install Tailwind CSS and Zustand.
    *   Output: Functional basic Next.js app with Tailwind and Zustand integrated.
*   **Task 0.5: Environment Variable Management**
    *   Description: Define structure for `.env` files (e.g., `.env.example`). Document required variables.
    *   Output: `.env.example` files for frontend and backend.

### Phase 1: Authentication (Google OAuth 2.0)

*   **Task 1.1: Backend - Google OAuth Configuration**
    *   Description: Integrate `google-auth-oauthlib`. Set up Google Cloud Project, configure OAuth 2.0 credentials (client ID, client secret).
    *   Output: Backend configuration for Google OAuth.
*   **Task 1.2: Backend - OAuth Endpoints**
    *   Description: Implement `/auth/google/login` to initiate OAuth flow and `/auth/google/callback` to handle the redirect from Google, exchange code for tokens, and store/manage user session/tokens securely.
    *   Output: Functional OAuth login/callback endpoints.
*   **Task 1.3: Frontend - Login UI & Logic**
    *   Description: Create Login page with "Sign in with Google" button using `@react-oauth/google`. Handle redirection to backend `/auth/google/login`.
    *   Output: Frontend login page.
*   **Task 1.4: Frontend - Token Handling & Authenticated State**
    *   Description: Manage authentication tokens received from the backend. Implement protected routes/components accessible only after login. Use Zustand for auth state.
    *   Output: Secure token handling and auth state management in frontend.
*   **Task 1.5: Token Refresh Mechanism (Backend/Frontend)**
    *   Description: Implement logic to handle token expiration and refresh access tokens using the refresh token.
    *   Output: Robust token refresh mechanism.

### Phase 2: Google Drive Integration

*   **Task 2.1: Backend - Google Drive API Client Setup**
    *   Description: Integrate `google-api-python-client`. Configure necessary scopes for Google Drive (e.g., `drive.file`).
    *   Output: Backend module for Google Drive API interaction.
*   **Task 2.2: Backend - Folder Creation/Validation**
    *   Description: Implement function to check if a specified folder exists in the user's Google Drive, and create it if not. Use user's OAuth tokens.
    *   Output: Function to manage research output folder.
*   **Task 2.3: Backend - File Upload Functionality**
    *   Description: Implement function to upload text/markdown files to the specified Google Drive folder.
    *   Output: Function to upload files to Google Drive.
*   **Task 2.4: Frontend - Google Drive Picker API Integration (Optional - Initial Simpler Approach)**
    *   Description:
        *   **Option A (Simpler):** Input field for user to type folder name/path. Backend defaults to a root folder like "/Sales Research Tool Output/".
        *   **Option B (Advanced):** Integrate Google Drive Picker API on the frontend for a visual folder selection experience. This requires careful handling of API keys and user tokens on the client-side.
    *   Output: UI component for selecting/specifying Google Drive destination.

### Phase 3: Core Research Logic - Gemini API & Celery Tasks

*   **Task 3.1: Backend - Celery & Redis Setup**
    *   Description: Configure Celery in the FastAPI application. Configure Redis as the message broker. Define basic Celery task structure.
    *   Output: Celery integrated with FastAPI and Redis.
*   **Task 3.2: Backend - Gemini API Client Setup**
    *   Description: Integrate `google-generativeai`. Securely manage Gemini API key via environment variables.
    *   Output: Backend module for Gemini API interaction.
*   **Task 3.3: Celery Task - Prospect Deep Dive (Gemini - Part 1)**
    *   Description: Create Celery task. Construct prompt for Gemini to get company overview and a *prioritized list of relevant source URLs*. Call Gemini API. Parse response.
    *   Output: Celery task for prospect deep dive.
*   **Task 3.4: Celery Task - Save Prospect Overview to GDrive**
    *   Description: Within/after Task 3.3, save the Gemini-generated overview (as text or Markdown) to the user's Google Drive folder.
    *   Output: Overview report saved to GDrive.
*   **Task 3.5: Celery Task - Prospect's Competitor Analysis (Gemini - Part 2)**
    *   Description: Create Celery task. Construct prompt for Gemini. Call API. Parse response. Save report to GDrive.
    *   Output: Celery task and GDrive report for competitor analysis.
*   **Task 3.6: Celery Task - Own Competitor Marketing Analysis (Gemini - Part 3)**
    *   Description: Create Celery task. Construct prompt for Gemini (focus on Palo Alto's competitors targeting the prospect's market). Call API. Parse response. Save report to GDrive.
    *   Output: Celery task and GDrive report for marketing analysis.

### Phase 4: Content Extraction & Finalization

*   **Task 4.1: Backend - `trafilatura` Integration**
    *   Description: Add `trafilatura` to backend dependencies.
    *   Output: `trafilatura` available in backend.
*   **Task 4.2: Celery Task - URL Content Extraction**
    *   Description: Create Celery task that takes the list of URLs (from Task 3.3). For each URL: fetch content, extract main text using `trafilatura`, convert to Markdown.
    *   Output: Celery task for content extraction.
*   **Task 4.3: Celery Task - Save Extracted Content to GDrive**
    *   Description: Within/after Task 4.2, save each extracted Markdown article to the user's Google Drive folder. Name files descriptively (e.g., from URL slug or page title).
    *   Output: Markdown articles saved to GDrive.

### Phase 5: API Endpoints & Frontend-Backend Integration

*   **Task 5.1: Backend - `/api/research/start` Endpoint**
    *   Description: Create FastAPI endpoint. Accepts company name and GDrive folder ID/path. Validates input. Initiates the chain of Celery tasks (starting with Prospect Deep Dive). Returns a `job_id`.
    *   Output: `/api/research/start` endpoint.
*   **Task 5.2: Backend - `/api/research/status/{job_id}` Endpoint**
    *   Description: Create FastAPI endpoint for frontend to poll for progress. Returns current status of the Celery tasks (e.g., "Phase 1: Processing...", "Phase 2: Complete", error messages).
    *   Output: `/api/research/status/{job_id}` endpoint.
*   **Task 5.3: Frontend - Main Interface UI**
    *   Description: Develop the main UI page (post-login) with GDrive folder picker/input, company name input, and "Start Research" button.
    *   Output: Main application UI.
*   **Task 5.4: Frontend - API Call to Start Research**
    *   Description: Implement logic to call `/api/research/start` when the button is clicked. Handle `job_id` response.
    *   Output: Frontend logic for initiating research.
*   **Task 5.5: Frontend - Progress Display UI & Logic**
    *   Description: Develop UI area to display real-time progress updates. Implement polling to `/api/research/status/{job_id}`. Display status messages, completion, and GDrive link.
    *   Output: Real-time progress display on UI.
*   **Task 5.6: Frontend - Error Handling Display**
    *   Description: Ensure errors from backend/Celery tasks are clearly displayed to the user.
    *   Output: User-friendly error messages on UI.

### Phase 6: Dockerization & Deployment Prep

*   **Task 6.1: Refine Frontend Dockerfile**
    *   Description: Optimize Next.js Dockerfile for multi-stage builds, production build.
    *   Output: Production-ready `frontend/Dockerfile`.
*   **Task 6.2: Refine Backend Dockerfile (FastAPI & Celery)**
    *   Description: Optimize Python Dockerfile. Ensure Celery worker can be started as a separate command/service from the same image. Include all dependencies.
    *   Output: Production-ready `backend/Dockerfile`.
*   **Task 6.3: Refine Redis Docker Configuration**
    *   Description: Ensure Redis service is correctly configured in `docker-compose.yml`, including persistence if needed (though for a simple message broker, it might not be critical).
    *   Output: Configured Redis service in `docker-compose.yml`.
*   **Task 6.4: Finalize `docker-compose.yml`**
    *   Description: Configure all services (frontend, backend API, Celery worker, Redis). Set up networking, volume mounts for `.env` files (or inject variables directly), and port mappings.
    *   Output: Complete `docker-compose.yml` for local development and deployment.
*   **Task 6.5: Comprehensive Testing in Docker Environment**
    *   Description: Build and run the entire application using `docker-compose up`. Test all functionalities end-to-end.
    *   Output: Verified Dockerized application.

### Phase 7: Documentation & Review

*   **Task 7.1: README Update**
    *   Description: Update project `README.md` with setup instructions, how to run (local and Docker), environment variable guide, and brief architecture overview.
    *   Output: Comprehensive `README.md`.
*   **Task 7.2: API Documentation (Optional - Swagger/OpenAPI)**
    *   Description: FastAPI automatically generates OpenAPI docs. Ensure they are clean and useful. Add descriptions if necessary.
    *   Output: Accessible API documentation.
*   **Task 7.3: Code Review & Refinement**
    *   Description: Review codebase for clarity, efficiency, security, and adherence to best practices.
    *   Output: Refined codebase.

## 5. Key Considerations

*   **Gemini Prompts:** The success heavily relies on well-engineered prompts for Gemini, especially for extracting the prioritized list of relevant URLs. This will require iteration.
*   **Google Drive Picker API vs. Simple Input:** Decide on the initial approach for GDrive folder selection. Picker API is better UX but more complex.
*   **Error Handling:** Robust error handling and clear UI feedback are crucial for all external API calls (Google, Gemini) and processing steps.
*   **Celery Worker Scalability:** Initial setup will be for a basic number of workers. Consider how to scale if needed.
*   **Security:**
    *   Securely manage OAuth tokens (e.g., HTTPOnly cookies for session, secure backend storage if long-lived access is needed).
    *   Store API keys (Gemini, Google Cloud Client Secret) via environment variables, never hardcoded.
    *   Validate all user inputs.
*   **Rate Limiting:** Be mindful of API rate limits for Google Drive and Gemini. Implement retries with backoff if necessary.
*   **Large File Handling (Content Extraction):** While `trafilatura` extracts main text, be mindful of very large web pages.
*   **Idempotency of Tasks:** Design Celery tasks to be idempotent where possible, so retrying a failed task doesn't cause unintended side effects.

## 6. Future Enhancements (Out of Current Scope)

*   User accounts beyond Google Sign-In.
*   Ability to re-run research or update existing research.
*   More sophisticated UI for viewing/managing research results within the app.
*   Admin panel for monitoring.
*   Support for other LLMs or research sources.
*   Direct integration with NotebookLM (if APIs become available).

This plan provides a structured approach. We will tackle these tasks phase by phase.
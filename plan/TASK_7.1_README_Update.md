# Task 7.1: README Update

**Phase:** Phase 7: Documentation & Review
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Update the project's main `README.md` file at the root of the repository. This `README.md` should serve as the primary entry point for anyone looking to understand, set up, or contribute to the project. It should include:
*   Project overview and objectives.
*   Key features.
*   Technology stack.
*   Setup instructions (local development and Docker).
*   Environment variable guide.
*   Brief architecture overview.
*   How to run the application.
*   Troubleshooting tips.

## 2. Detailed Steps / Implementation Notes

1.  **Create `README.md` (if it doesn't exist):**
    *   Create a file named `README.md` in the project root (`/root/sales-researcher/README.md`).

2.  **Structure the `README.md`:**
    *   **Project Title & Description:**
        *   `# Automated Sales Prospect Research Tool`
        *   A concise summary of what the application does.
    *   **Table of Contents (Optional but Recommended):**
        *   Helps navigation for long READMEs.
    *   **Features:**
        *   List the core functionalities (Google login, Drive integration, Gemini research, URL crawling, etc.).
    *   **Technology Stack:**
        *   Briefly list Frontend, Backend, Database, Task Queue, Containerization.
    *   **Architecture Overview:**
        *   A high-level diagram or textual description of how components interact (Frontend -> Backend API -> Celery -> Redis -> Google APIs).
    *   **Setup & Installation:**
        *   **Prerequisites:** List required software (Docker, Docker Compose, Node.js, Python, Git).
        *   **Clone Repository:** Instructions for cloning the Git repository.
        *   **Environment Variables:**
            *   Explain the `.env.example` files.
            *   Instruct users to copy `.env.example` to `.env` in `frontend/` and `backend/`.
            *   Explain where to get `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GEMINI_API_KEY`, and `GOOGLE_REDIRECT_URI`.
            *   Emphasize security: never commit `.env` files.
        *   **Running with Docker Compose (Recommended):**
            *   `docker-compose build`
            *   `docker-compose up`
            *   Access URLs (Frontend: `http://localhost:3000`, Backend: `http://localhost:8000`).
        *   **Running Locally (for development):**
            *   **Backend:**
                *   Create Python virtual environment.
                *   `pip install -r backend/requirements.txt`
                *   `uvicorn main:app --reload`
            *   **Frontend:**
                *   `npm install` (or `yarn install`) in `frontend/`
                *   `npm run dev` (or `yarn dev`) in `frontend/`
            *   **Redis:** Instructions to run Redis locally (e.g., via Docker `docker run --name my-redis -p 6379:6379 redis:alpine`).
            *   **Celery Worker:** `celery -A backend.celery_app worker -l info`
    *   **Usage:**
        *   Brief guide on how to use the application after setup (login, enter company, select folder, start research).
    *   **Troubleshooting:**
        *   Common issues and solutions (e.g., Docker not starting, API key errors).
    *   **Contributing (Optional):**
        *   Guidelines for contributing to the project.
    *   **License (Optional):**
        *   Project license information.

3.  **Review and Refine:**
    *   Ensure clarity, conciseness, and accuracy.
    *   Check for broken links or outdated information.
    *   Make sure all necessary setup steps are covered.

## 3. Expected Output / Deliverables
*   A comprehensive and well-structured `README.md` file at the project root.

## 4. Dependencies
*   All previous tasks, as the `README.md` will document their outputs and configurations.
    *   Task 0.1: Initialize Project Repository (for Git setup).
    *   Task 0.2, 6.1, 6.2, 6.3, 6.4: Docker configuration.
    *   Task 0.3, 0.4: Basic Frontend/Backend setup.
    *   Task 0.5: Environment Variable Management.
    *   All other tasks for features to be documented.

## 5. Acceptance Criteria
*   `README.md` exists at the project root.
*   The `README.md` covers all sections mentioned in the description (overview, features, tech stack, setup, env vars, running, architecture).
*   Instructions are clear and easy to follow for a new developer.
*   All code snippets and commands are correct.

## 6. Estimated Effort (Optional)
*   Medium to Large (due to the breadth of information to cover).

## 7. Notes / Questions
*   **Keep it Updated:** The `README.md` should be a living document, updated as the project evolves.
*   **Audience:** Tailor the language for developers who might want to set up and run the project.
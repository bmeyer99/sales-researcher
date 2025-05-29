# Task 0.1: Initialize Project Repository

**Phase:** Phase 0: Project Setup & Foundational Structure
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-28

## 1. Description
Set up Git repository. Create initial directory structure (`frontend`, `backend`, `docs`, `plan`).

## 2. Detailed Steps / Implementation Notes
1.  **Navigate to Project Root:**
    *   Ensure the current directory is `/root/sales-researcher`.
2.  **Initialize Git Repository:**
    *   Execute the command: `git init`
3.  **Create Core Directories:**
    *   Create a `frontend` directory: `mkdir frontend`
    *   Create a `backend` directory: `mkdir backend`
    *   Create a `docs` directory: `mkdir docs`
    *   The `plan` directory should already exist. If not, create it: `mkdir plan` (though it was confirmed to exist).
4.  **Create `.gitignore` File:**
    *   Create a file named `.gitignore` in the project root (`/root/sales-researcher/.gitignore`).
    *   Populate it with standard ignore patterns for Python, Node.js, IDEs, and OS-specific files. A comprehensive example list was previously discussed and should be used here. (See `plan/PROJECT_PLAN.md` discussion or a standard template).
    *   Example content for `.gitignore`:
        ```gitignore
        # Python
        __pycache__/
        *.py[cod]
        *$py.class
        *.so
        .Python
        build/
        develop-eggs/
        dist/
        downloads/
        eggs/
        .eggs/
        lib/
        lib60/
        parts/
        sdist/
        var/
        wheels/
        pip-wheel-metadata/
        share/python-wheels/
        *.egg-info/
        .installed.cfg
        *.egg
        MANIFEST
        *.manifest
        *.spec
        pip-log.txt
        pip-delete-this-directory.txt
        htmlcov/
        .tox/
        .nox/
        .coverage
        .coverage.*
        .cache
        nosetests.xml
        coverage.xml
        *.cover
        *.log
        .hypothesis/
        .pytest_cache/
        celerybeat-schedule
        *.pid
        *.pid.lock

        # Node.js
        node_modules/
        npm-debug.log
        yarn-debug.log
        yarn-error.log
        # package-lock.json # Usually committed
        # yarn.lock # Usually committed
        build/
        dist/
        .next/
        out/
        coverage/
        *.env
        .DS_Store
        *.pem

        # IDEs and editors
        .vscode/
        .idea/
        *.suo
        *.ntvs*
        *.njsproj
        *.sln
        *.sw?

        # Operating System files
        .DS_Store
        Thumbs.db
        ehthumbs.db
        Desktop.ini
        ```
5.  **Initial Commit (Optional but Recommended):**
    *   Stage the created directories and `.gitignore` file: `git add .`
    *   Commit the initial structure: `git commit -m "Initial project structure and .gitignore"`

## 3. Expected Output / Deliverables
*   Initialized Git repository in `/root/sales-researcher`.
*   Directory structure created:
    *   `/root/sales-researcher/frontend/`
    *   `/root/sales-researcher/backend/`
    *   `/root/sales-researcher/docs/`
    *   `/root/sales-researcher/plan/` (already exists)
*   A `.gitignore` file in the project root populated with appropriate ignore patterns.

## 4. Dependencies
*   None. This is a foundational task.

## 5. Acceptance Criteria
*   Running `git status` in `/root/sales-researcher` shows it's a git repository.
*   The `frontend`, `backend`, and `docs` directories exist at the project root.
*   The `.gitignore` file exists at the project root and contains relevant patterns.
*   If initial commit is made, `git log` shows the initial commit.

## 6. Estimated Effort (Optional)
*   Small

## 7. Notes / Questions
*   Confirm if `package-lock.json` or `yarn.lock` should be in the `.gitignore`. Typically, these are committed to ensure reproducible builds, so they are commented out in the example above. For this project, they should likely *not* be in the `.gitignore`.
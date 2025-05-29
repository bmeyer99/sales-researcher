# Task 7.2: API Documentation (Optional - Swagger/OpenAPI)

**Phase:** Phase 7: Documentation & Review
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Ensure the FastAPI application's API documentation (generated automatically via OpenAPI/Swagger UI) is clean, accurate, and useful. This involves reviewing the endpoint descriptions, request/response models, and ensuring all relevant API endpoints are properly documented.

## 2. Detailed Steps / Implementation Notes

1.  **FastAPI's Automatic Documentation:**
    *   FastAPI automatically generates OpenAPI specification and provides interactive API documentation (Swagger UI and ReDoc) at `/docs` and `/redoc` respectively.
    *   This is enabled by default when you create a `FastAPI` app instance.
        ```python
        # Example: backend/main.py (from Task 0.3)
        from fastapi import FastAPI

        app = FastAPI(
            title="Sales Prospect Research Tool API",
            description="API for managing sales prospect research tasks.",
            version="0.1.0"
        )
        # ...
        ```
    *   The `title`, `description`, and `version` parameters in the `FastAPI` constructor are used in the generated documentation.

2.  **Review Endpoint Descriptions:**
    *   Go through each API endpoint defined in the backend (e.g., `/auth/google/login`, `/auth/google/callback`, `/api/research/start`, `/api/research/status/{job_id}`).
    *   Ensure that the `summary` and `description` arguments in the FastAPI route decorators (`@app.get`, `@router.post`) are clear and accurately describe the endpoint's purpose, parameters, and responses.
        ```python
        # Example: backend/api/v1/research.py (from Task 5.1)
        @router.post("/start", summary="Initiate new research task", description="Starts a comprehensive sales prospect research workflow.")
        async def start_research(...):
            # ...
        ```

3.  **Pydantic Models for Request/Response:**
    *   Ensure all Pydantic models used for request bodies and response models are well-defined with clear field names and descriptions.
    *   Pydantic models automatically generate schema definitions in the OpenAPI spec.
        ```python
        # Example: backend/api/v1/research.py (from Task 5.1)
        from pydantic import BaseModel, Field

        class ResearchRequest(BaseModel):
            company_name: str = Field(..., min_length=2, max_length=100, description="The name of the prospect company to research.")
            gdrive_folder_name: str = Field(..., min_length=1, max_length=200, description="The desired name for the output folder in Google Drive.")
        ```

4.  **Tagging Endpoints:**
    *   Use `tags` in `APIRouter` to group related endpoints in the documentation.
        ```python
        # Example: backend/api/v1/research.py
        router = APIRouter(prefix="/research", tags=["Research"])
        ```
    *   This helps organize the Swagger UI.

5.  **Response Models (Optional but Recommended):**
    *   Explicitly define `response_model` in route decorators to provide clear documentation of the expected successful response structure.
        ```python
        # Example:
        class ResearchStartResponse(BaseModel):
            job_id: str
            message: str

        @router.post("/start", response_model=ResearchStartResponse)
        async def start_research(...):
            # ...
        ```

6.  **Error Responses:**
    *   Document common error responses using `responses` parameter in the route decorator.
        ```python
        # Example:
        @router.post("/start",
            responses={
                400: {"description": "Bad Request - Invalid input"},
                401: {"description": "Unauthorized - User not authenticated"},
                500: {"description": "Internal Server Error"}
            }
        )
        async def start_research(...):
            # ...
        ```

7.  **Review Generated Docs:**
    *   Run the FastAPI application (`uvicorn main:app --reload`).
    *   Open `http://localhost:8000/docs` and `http://localhost:8000/redoc` in a browser.
    *   Review the generated documentation for clarity, completeness, and accuracy.

## 3. Expected Output / Deliverables
*   Clean, accurate, and useful interactive API documentation available at `/docs` and `/redoc` for the FastAPI application.
*   All API endpoints are properly described with their parameters, request bodies, and responses.

## 4. Dependencies
*   Task 0.3: Setup Backend (FastAPI) - Basic Structure.
*   All tasks that define new API endpoints (e.g., Task 1.2, 5.1, 5.2).

## 5. Acceptance Criteria
*   Accessing `/docs` and `/redoc` displays the API documentation without errors.
*   All defined API endpoints are listed in the documentation.
*   Each endpoint has a clear summary and description.
*   Request body and response schemas are correctly displayed.
*   Error responses are documented.

## 6. Estimated Effort (Optional)
*   Small to Medium (mostly review and adding docstrings/descriptions).

## 7. Notes / Questions
*   **Continuous Documentation:** API documentation should be maintained alongside code changes.
*   **External Tools:** For more advanced API documentation needs (e.g., generating client SDKs), the OpenAPI spec can be exported and used with external tools.
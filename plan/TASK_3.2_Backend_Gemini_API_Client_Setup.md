# Task 3.2: Backend - Gemini API Client Setup

**Phase:** Phase 3: Core Research Logic - Gemini API & Celery Tasks
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Integrate the `google-generativeai` library into the backend to interact with the Google Gemini API. Securely manage and configure the Gemini API key.

## 2. Detailed Steps / Implementation Notes

1.  **Add Dependency:**
    *   Add `google-generativeai` to the `backend/requirements.txt` file.
        ```txt
        # backend/requirements.txt
        # ... other dependencies
        google-generativeai>=0.3.0,<0.6.0 
        # Check for the latest stable version
        ```
    *   Install it in the local venv and ensure it'll be in the Docker image.

2.  **API Key Management:**
    *   The Gemini API key (obtained by the user from Google AI Studio or Google Cloud Console) needs to be securely accessed by the backend.
    *   This should be defined in the `backend/.env` file (for local development) and injected as an environment variable in Docker.
    *   Refer to `plan/TASK_0.5_Environment_Variable_Management.md`.
    *   Required variable in `backend/.env.example` (and to be set in `.env`):
        ```env
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        ```

3.  **Gemini API Service Utility (`backend/services/gemini_service.py` or similar):**
    *   Create a Python module to encapsulate interactions with the Gemini API.
    *   This service will configure the API client with the API key.
        ```python
        # Example: backend/services/gemini_service.py
        import google.generativeai as genai
        import os
        # from backend.core.config import settings # If API key is part of a central settings object

        # Load the API key from environment variable
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        if not GEMINI_API_KEY:
            # In a real app, you might want to raise an error or log a warning
            # For now, we'll allow it to proceed, but API calls will fail.
            print("Warning: GEMINI_API_KEY is not set. Gemini API calls will fail.")
        else:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                print("Gemini API configured successfully.")
            except Exception as e:
                print(f"Error configuring Gemini API: {e}")
                # Potentially raise an error to prevent app startup if Gemini is critical

        # Function to interact with a specific Gemini model (e.g., gemini-1.5-pro-latest or gemini-2.5)
        # Model name should be configurable or passed as an argument
        def generate_gemini_content(prompt: str, model_name: str = "gemini-1.5-flash-latest"): # Use a cost-effective model for general tasks initially
            """
            Generates content using the specified Gemini model.
            """
            if not GEMINI_API_KEY:
                return "Error: GEMINI_API_KEY not configured."

            try:
                model = genai.GenerativeModel(model_name)
                # Example: Simple text generation. For more complex scenarios (chat, vision),
                # the API usage will differ.
                response = model.generate_content(prompt)
                
                # Basic error/safety handling (refer to Gemini API docs for comprehensive handling)
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    return f"Content generation blocked. Reason: {response.prompt_feedback.block_reason_message}"
                if not response.candidates or not response.candidates[0].content.parts:
                     return "Error: No content generated or unexpected response structure."

                return response.text # Accessing .text directly might raise if parts are not text
            except Exception as e:
                # Log the full error for debugging
                print(f"Error generating content with Gemini model {model_name}: {e}")
                return f"Error: Could not generate content using Gemini. Details: {str(e)}"

        # Example of how this might be used in a task:
        # if __name__ == '__main__':
        #     if GEMINI_API_KEY:
        //         test_prompt = "Explain the concept of a Docker container in simple terms."
        //         result = generate_gemini_content(test_prompt)
        //         print(f"Prompt: {test_prompt}\nGemini: {result}")
        //     else:
        //         print("Skipping Gemini test as API key is not set.")

        ```
    *   The `genai.configure(api_key=GEMINI_API_KEY)` line initializes the library globally with the API key.
    *   The `generate_gemini_content` function is a basic example; actual prompts and model interactions will be more complex for the research tasks.

4.  **Model Selection:**
    *   The project plan mentions "Gemini 2.5". Ensure the chosen model name in the code (e.g., `gemini-2.5-pro-preview` or whatever the latest/appropriate version is at implementation time) matches the capabilities required and is available.
    *   Consider making the model name configurable (e.g., via environment variable or passed to functions).

5.  **Error Handling and Safety Settings:**
    *   Implement robust error handling for API calls (network issues, API errors, rate limits, content blocked due to safety settings).
    *   Familiarize with Gemini API's safety settings and how to handle responses that might be blocked. The example includes a very basic check.

## 3. Expected Output / Deliverables
*   `google-generativeai` library added to `backend/requirements.txt`.
*   A backend service module (e.g., `backend/services/gemini_service.py`) that:
    *   Configures the Gemini API client with the API key from environment variables.
    *   Provides functions to interact with Gemini models (e.g., generate text based on a prompt).
*   Confirmation that the `GEMINI_API_KEY` environment variable is documented and required.

## 4. Dependencies
*   Task 0.5: Environment Variable Management (for `GEMINI_API_KEY`).

## 5. Acceptance Criteria
*   The backend application can successfully configure the `google-generativeai` client using the `GEMINI_API_KEY`.
*   A test call to the Gemini API (e.g., using a simple prompt within the `gemini_service.py` or a test Celery task) returns a valid response.
*   If the API key is missing or invalid, the application handles this gracefully (e.g., logs an error, and API calls fail with a clear message) rather than crashing.

## 6. Estimated Effort (Optional)
*   Small to Medium (integrating the library and basic calls are straightforward; robust error/safety handling adds complexity).

## 7. Notes / Questions
*   **API Quotas and Billing:** Ensure the Google Cloud project associated with the Gemini API key has billing enabled and is aware of API usage quotas.
*   **Prompt Engineering:** The quality of Gemini's output will heavily depend on the prompts used. This task focuses on client setup; prompt engineering will be part of specific research tasks (3.3, 3.5, 3.6).
*   **Streaming Responses:** For long-form content generation, consider using streaming responses from Gemini if applicable, to improve perceived performance.
*   **Retry Logic:** Implement retry logic (e.g., with exponential backoff) for transient API errors.
# Task 3.3: Celery Task - Prospect Deep Dive (Gemini - Part 1)

**Phase:** Phase 3: Core Research Logic - Gemini API & Celery Tasks
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create a Celery task that performs the "Prospect Deep Dive". This involves:
1.  Constructing a detailed prompt for the Gemini API to gather comprehensive company information (technologies, industry, cloud apps, news, key personnel/roles, challenges).
2.  Crucially, the prompt must also ask Gemini to return a *prioritized list of relevant source URLs* that it used or deems important for further research.
3.  Calling the Gemini API via the service set up in Task 3.2.
4.  Parsing the Gemini response to extract the overview text and the list of URLs.

The overview text will be saved to Google Drive in a subsequent task/step (Task 3.4), and the URL list will be passed to the Content Extraction Module (Phase 4).

## 2. Detailed Steps / Implementation Notes

1.  **Create Task Module (`backend/tasks/gemini_research.py`):**
    *   If not already created, ensure this module exists.
    *   Import `celery_app` from `backend.celery_app` and the Gemini service function (e.g., `generate_gemini_content` from `backend.services.gemini_service`).

2.  **Define Celery Task (`prospect_deep_dive_task`):**
    *   Decorate a Python function with `@celery_app.task(name="prospect_deep_dive_task")`.
    *   The task should accept parameters like `company_name: str` and `drive_folder_id: str` (though `drive_folder_id` is for saving, the primary output here is data for further tasks). It might also accept `user_id` or `session_id` if user-specific context or API limits need to be managed.
        ```python
        # backend/tasks/gemini_research.py
        from backend.celery_app import celery_app
        from backend.services.gemini_service import generate_gemini_content
        # from backend.services.google_drive_service import upload_text_file # For Task 3.4
        import json # For parsing structured URL output

        # Placeholder for a more sophisticated status update mechanism
        def update_task_status(task_id: str, message: str, current_step: int, total_steps: int):
            # This could update a database, Redis, or use Celery's custom states
            print(f"TASK [{task_id}]: {message} ({current_step}/{total_steps})")
            # celery_app.update_state(state='PROGRESS', meta={'message': message, 'current': current_step, 'total': total_steps})


        @celery_app.task(bind=True, name="prospect_deep_dive_task")
        def prospect_deep_dive_task(self, company_name: str, drive_folder_id: str):
            """
            Performs a deep dive research on a company using Gemini,
            extracts overview and source URLs.
            """
            task_id = self.request.id
            total_steps = 3 # 1. Prompt, 2. Gemini Call, 3. Parse & Return (Saving is next task)
            
            update_task_status(task_id, f"Starting deep dive for {company_name}", 1, total_steps)

            # 1. Construct Prompt
            # This is a critical step and will require iteration.
            # The prompt needs to ask for:
            # - Company Overview (technologies, industry, cloud apps, recent news, key personnel/roles, challenges)
            # - A prioritized list of relevant source URLs (e.g., in a specific format like JSON)
            prompt = f"""
            Perform a comprehensive deep dive research on the company: "{company_name}".
            Provide the following information:
            1.  **Company Overview:**
                *   **Industry and Niche:**
                *   **Key Products/Services:**
                *   **Technologies Used (if known/publicly mentioned, e.g., CRM, ERP, Cloud Provider, specific software):**
                *   **Cloud Applications Used (if known/publicly mentioned):**
                *   **Recent News (last 6-12 months, concise summaries):**
                *   **Key Personnel/Roles (e.g., CIO, CTO, Head of Sales, relevant VPs - focus on decision-makers or influencers for sales):**
                *   **Reported Challenges or Pain Points (if any public information):**
            2.  **Source URLs:**
                *   Provide a prioritized list of 5-10 relevant source URLs that were most influential in generating this overview or are highly recommended for further reading.
                *   Format this list as a JSON array of strings. For example:
                    ["url1", "url2", "url3"]
            
            Structure your entire response so that the "Source URLs" JSON array is clearly distinguishable at the end, perhaps under a specific heading like "### Source URLs JSON:".
            """
            update_task_status(task_id, "Prompt constructed", 1, total_steps)

            # 2. Call Gemini API
            # Consider which Gemini model to use (e.g., "gemini-1.5-pro-latest" for quality)
            # This model name could be a config setting.
            update_task_status(task_id, "Calling Gemini API...", 2, total_steps)
            gemini_response_text = generate_gemini_content(prompt, model_name="gemini-1.5-pro-latest") # Or your chosen model

            if gemini_response_text.startswith("Error:"):
                update_task_status(task_id, f"Gemini API Error: {gemini_response_text}", 2, total_steps)
                # Handle error: raise an exception, or return error status
                # This might trigger a retry or failure state for the Celery task.
                raise Exception(f"Gemini API Error: {gemini_response_text}")

            update_task_status(task_id, "Gemini response received", 2, total_steps)

            # 3. Parse Response
            # This will also require iteration based on Gemini's typical output structure.
            # Aim to separate the main overview text from the JSON list of URLs.
            overview_text = ""
            source_urls = []

            try:
                # A simple strategy: find the JSON part. This needs to be robust.
                # Look for a specific marker if you instructed Gemini to use one.
                json_marker = "### Source URLs JSON:"
                if json_marker in gemini_response_text:
                    parts = gemini_response_text.split(json_marker, 1)
                    overview_text = parts[0].strip()
                    json_part = parts[1].strip()
                    # Try to find the JSON array within this part
                    # This is a naive approach; regex or more structured parsing might be needed
                    # if Gemini doesn't perfectly isolate the JSON.
                    json_start = json_part.find('[')
                    json_end = json_part.rfind(']') + 1
                    if json_start != -1 and json_end != -1:
                        source_urls_json_str = json_part[json_start:json_end]
                        source_urls = json.loads(source_urls_json_str)
                    else:
                        overview_text = gemini_response_text # Fallback if JSON not found as expected
                        print(f"Warning: Could not parse JSON URLs from Gemini response for {company_name}")
                else:
                    overview_text = gemini_response_text # Assume entire response is overview if marker not found
                    print(f"Warning: JSON URL marker not found in Gemini response for {company_name}")
                
                if not isinstance(source_urls, list): # Basic validation
                    print(f"Warning: Parsed source_urls is not a list for {company_name}. Found: {source_urls}")
                    source_urls = []

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON URLs from Gemini response for {company_name}: {e}")
                overview_text = gemini_response_text # Fallback
                source_urls = [] # Ensure it's an empty list on error
            except Exception as e:
                print(f"Generic error parsing Gemini response for {company_name}: {e}")
                overview_text = gemini_response_text # Fallback
                source_urls = []


            update_task_status(task_id, "Response parsed", 3, total_steps)
            
            # The task will return data to be used by subsequent tasks or chained tasks.
            # Task 3.4 will handle saving `overview_text`.
            # Phase 4 tasks will handle `source_urls`.
            return {
                "company_name": company_name,
                "drive_folder_id": drive_folder_id,
                "overview_text": overview_text,
                "source_urls": source_urls,
                "status_message": f"Deep dive for {company_name} complete. Overview and URLs extracted."
            }
        ```

3.  **Prompt Engineering (Iterative Process):**
    *   The quality of the prompt is paramount. It needs to be very specific about the desired information and the format for the source URLs (e.g., JSON list).
    *   This will likely require significant testing and refinement based on Gemini's responses.
    *   Consider instructing Gemini to use clear markers or headings to separate the overview from the URL list for easier parsing.

4.  **Parsing Logic (Iterative Process):**
    *   Develop robust parsing logic to extract the overview text and the list of URLs from Gemini's raw response.
    *   This might involve string manipulation, regular expressions, or trying to guide Gemini to produce a more structured output (like a JSON object containing both overview and URLs, though this can be harder for long text).

5.  **Error Handling:**
    *   Handle potential errors from the Gemini API call (e.g., API errors, rate limits, content blocked).
    *   Handle errors during parsing of the response.
    *   The Celery task should report failures appropriately so they can be tracked.

## 3. Expected Output / Deliverables
*   A Celery task function (`prospect_deep_dive_task`) defined in `backend/tasks/gemini_research.py`.
*   The task takes `company_name` (and `drive_folder_id` for later use) as input.
*   The task constructs a detailed prompt for Gemini.
*   The task calls the Gemini API and parses its response.
*   The task returns a dictionary containing:
    *   `company_name`
    *   `drive_folder_id`
    *   `overview_text` (string)
    *   `source_urls` (list of strings)

## 4. Dependencies
*   Task 3.1: Backend - Celery & Redis Setup (Celery app instance).
*   Task 3.2: Backend - Gemini API Client Setup (Gemini service function).

## 5. Acceptance Criteria
*   The Celery task can be successfully enqueued and executed.
*   Given a company name, the task generates a relevant prompt.
*   The task successfully calls the Gemini API.
*   The task correctly parses the Gemini response to separate the overview text and a list of source URLs.
*   The returned dictionary contains the expected keys and data types.
*   Failures in Gemini API call or parsing are handled gracefully within the task (e.g., logging error, returning an error state or specific error information).

## 6. Estimated Effort (Optional)
*   Medium to Large (Prompt engineering and response parsing can be time-consuming and iterative).

## 7. Notes / Questions
*   **Prompt Iteration:** This is key. The initial prompt is a starting point. Expect to refine it based on actual Gemini outputs.
*   **Structured Output from Gemini:** Explore if Gemini can be prompted to return a more structured overall response (e.g., a single JSON object with keys for "overview" and "source_urls"). This could simplify parsing but might be harder for Gemini with very long overview texts. The current approach of asking for a JSON array for URLs within a larger text body is a common pattern.
*   **URL Validation:** Consider adding a basic validation step for the extracted URLs (e.g., check if they look like valid HTTP/HTTPS URLs).
*   **Task Chaining/Callbacks:** The result of this task (overview text and URLs) will be used by subsequent Celery tasks (saving overview, crawling URLs). This can be handled by Celery's chaining/callback mechanisms or by the orchestrating code that starts these tasks.
*   **Status Updates:** The `update_task_status` is a placeholder. A more robust mechanism for frontend progress updates will be part of Task 5.2 and 5.5. Celery's built-in state updates can be leveraged.
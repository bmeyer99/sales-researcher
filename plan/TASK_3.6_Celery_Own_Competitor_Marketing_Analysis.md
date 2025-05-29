# Task 3.6: Celery Task - Own Competitor Marketing Analysis (Gemini - Part 3)

**Phase:** Phase 3: Core Research Logic - Gemini API & Celery Tasks
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Create a Celery task that analyzes how *our* (Palo Alto Networks, as specified in the project objectives) competitors are targeting the prospect company's market segment. This involves:
1.  Constructing a prompt for the Gemini API. The prompt needs to leverage context about the prospect company (e.g., its industry, size, potential needs identified in Task 3.3) and ask how Palo Alto Networks' key competitors position themselves and market to similar companies.
2.  Calling the Gemini API.
3.  Parsing the response.
4.  Saving the generated analysis report to the user's Google Drive folder.

## 2. Detailed Steps / Implementation Notes

1.  **Define Celery Task (`own_competitor_marketing_analysis_task`):**
    *   In `backend/tasks/gemini_research.py` or a similar module.
    *   The task should accept `prospect_company_name: str`, `prospect_company_industry: str` (or other relevant context from Task 3.3), `drive_folder_id: str`, and `user_id: str` (for GDrive auth).
        ```python
        # backend/tasks/gemini_research.py
        from backend.celery_app import celery_app
        from backend.services.gemini_service import generate_gemini_content
        from backend.services.google_drive_service import upload_text_file # Assuming this handles auth via user_id context
        # from .utils import update_task_status

        OUR_COMPANY_NAME = "Palo Alto Networks" # Define our company for the prompt

        @celery_app.task(bind=True, name="own_competitor_marketing_analysis_task")
        def own_competitor_marketing_analysis_task(self, prospect_company_name: str, prospect_company_industry: str, drive_folder_id: str, user_id: str = None):
            """
            Analyzes how OUR competitors target the prospect's market segment using Gemini
            and saves the report to Google Drive.
            """
            task_id = self.request.id
            # update_task_status(task_id, f"Starting our competitive marketing analysis for {prospect_company_name}'s segment", 1, 4)

            # 1. Construct Prompt
            # This prompt needs to be carefully crafted.
            # It should define "our" key competitors (or ask Gemini to identify them based on OUR_COMPANY_NAME).
            prompt = f"""
            The prospect company is "{prospect_company_name}", which operates in the "{prospect_company_industry}" industry.
            Our company is "{OUR_COMPANY_NAME}".

            Please analyze how key competitors of "{OUR_COMPANY_NAME}" (e.g., Cisco, Fortinet, Check Point, CrowdStrike, Zscaler - or identify others if more relevant)
            typically market their cybersecurity solutions to companies similar to "{prospect_company_name}" in the "{prospect_company_industry}" sector.

            Consider the following aspects in your analysis for each of our competitors:
            *   **Targeting Strategies:** What specific pain points or needs do they emphasize for this type of prospect?
            *   **Messaging and Positioning:** What are their key marketing messages and value propositions?
            *   **Commonly Highlighted Product Categories or Solutions:** Which of their products/services do they typically push for this segment?
            *   **Channels (if known):** Any insights into how they reach these prospects (e.g., specific industry events, types of content marketing)?

            Provide a concise report summarizing this competitive marketing analysis. This will help our sales team understand how to position "{OUR_COMPANY_NAME}" effectively against others when approaching "{prospect_company_name}".
            """
            # update_task_status(task_id, "Own competitive marketing analysis prompt constructed", 2, 4)

            # 2. Call Gemini API
            # update_task_status(task_id, "Calling Gemini API for our competitive marketing analysis...", 3, 4)
            analysis_text = generate_gemini_content(prompt, model_name="gemini-1.5-pro-latest")

            if analysis_text.startswith("Error:"):
                # update_task_status(task_id, f"Gemini API Error: {analysis_text}", 3, 4)
                raise Exception(f"Gemini API Error during own competitive marketing analysis: {analysis_text}")
            
            # update_task_status(task_id, "Gemini response for own competitive marketing analysis received", 3, 4)

            # 3. Parse Response (Gemini response is likely the report itself)
            # Minimal parsing might be needed.

            # 4. Save Report to Google Drive
            file_name = f"{prospect_company_name}_Own_Competitive_Marketing_Analysis.md"
            # update_task_status(task_id, f"Saving own competitive marketing analysis to GDrive: {file_name}", 4, 4)

            try:
                # CRITICAL: `upload_text_file` needs to handle auth using `user_id`
                upload_result = upload_text_file(
                    file_name=file_name,
                    file_content=analysis_text,
                    folder_id=drive_folder_id,
                    mime_type='text/markdown',
                    user_id=user_id # Pass user_id for auth context
                )
                # update_task_status(task_id, "Own competitive marketing analysis saved successfully", 4, 4)
                return {
                    "status": "success",
                    "file_id": upload_result.get('id'),
                    "file_name": file_name,
                    "drive_folder_id": drive_folder_id,
                    "webViewLink": upload_result.get('webViewLink'),
                    "message": f"Own competitive marketing analysis for {prospect_company_name}'s segment complete and saved."
                }
            except Exception as e:
                # update_task_status(task_id, f"Error saving own competitive marketing analysis: {e}", 4, 4)
                print(f"Error saving '{file_name}' to GDrive: {e}")
                raise
        ```

2.  **Contextual Information for Prompt:**
    *   The prompt needs context about the prospect company (e.g., `prospect_company_name`, `prospect_company_industry`). This information should be available from the output of Task 3.3 (Prospect Deep Dive).
    *   The definition of "our company" (Palo Alto Networks) should be clear in the prompt.

3.  **Identifying "Our" Competitors:**
    *   The prompt can either list known key competitors of Palo Alto Networks or ask Gemini to identify them in the context of cybersecurity and the prospect's industry. Listing them might yield more focused results.

4.  **Google Drive Upload:**
    *   Use the `upload_text_file` service (Task 2.3).
    *   Filename example: `"{prospect_company_name}_Own_Competitive_Marketing_Analysis.md"`.
    *   Ensure `user_id` is passed for GDrive authentication context.

## 3. Expected Output / Deliverables
*   A Celery task function (`own_competitor_marketing_analysis_task`) in the backend.
*   The task takes prospect company details (name, industry), `drive_folder_id`, and `user_id` as input.
*   The task generates a report on how Palo Alto Networks' competitors market to the prospect's segment.
*   The report is saved as a file in the specified Google Drive folder.
*   The task returns status information, including the ID/link of the saved file.

## 4. Dependencies
*   Task 2.3: Backend - File Upload Functionality.
*   Task 3.1: Backend - Celery & Redis Setup.
*   Task 3.2: Backend - Gemini API Client Setup.
*   Task 3.3: Celery Task - Prospect Deep Dive (to provide context like `prospect_company_industry`).
*   Mechanism for Celery tasks to use user-specific Google OAuth tokens.

## 5. Acceptance Criteria
*   The Celery task executes successfully.
*   A relevant marketing analysis report is generated by Gemini.
*   The report is saved to the correct Google Drive folder with the expected filename.
*   Failures are handled gracefully.

## 6. Estimated Effort (Optional)
*   Medium (Prompt engineering is key here).

## 7. Notes / Questions
*   **Specificity of "Our Competitors":** Being explicit about which competitors to analyze (e.g., Cisco, Fortinet, Check Point) will likely yield better results than asking Gemini to infer them, though Gemini might also suggest others.
*   **Actionability of Report:** The prompt should guide Gemini to produce insights that are actionable for a sales team.
*   **Data Flow:** This task relies on outputs or context from the initial Prospect Deep Dive (Task 3.3), such as the prospect's industry. The overall Celery workflow needs to manage this data flow (e.g., by passing results from one task to another or having an orchestrator task).
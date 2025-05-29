import logging # Changed to standard logging
from celery_app import celery_app
from services.gemini_service import gemini_service
from tasks.google_drive_tasks import save_text_to_gdrive_task
import json
import re

logger = logging.getLogger(__name__) # Changed to standard logging

@celery_app.task(bind=True, name="gemini_tasks.test_gemini_api")
def test_gemini_api(self, prompt: str):
    """
    Celery task to test the Gemini API integration.
    """
    try:
        response_text = gemini_service.generate_content(prompt)
        if response_text:
            print(f"Gemini API Test Response: {response_text}")
            return {"status": "success", "response": response_text}
        else:
            print("Failed to get response from Gemini API.")
            return {"status": "failed", "message": "No response from Gemini API."}
    except Exception as e:
        logger.error(f"Error in test_gemini_api task: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="prospect_deep_dive_task")
def prospect_deep_dive_task(
    self, company_name: str, drive_folder_id: str, user_id: str
):
    """
    Celery task to perform a "Prospect Deep Dive" using the Gemini API.
    Gathers comprehensive company information and a prioritized list of source URLs.
    """
    try:
        # 1. Construct Prompt
        prompt = f"""
        Perform a comprehensive "Prospect Deep Dive" on the company: {company_name}.

        I need the following information:
        - Company Overview: Include details on their core business, technologies used (e.g., programming languages, frameworks, databases, cloud providers), primary industry, specific cloud applications they might be using (e.g., Salesforce, HubSpot, Workday), recent significant news or press releases (last 12-18 months), key personnel and their roles (e.g., CEO, CTO, Head of Sales, Head of Marketing), and major challenges or pain points they might be facing (e.g., market competition, technological shifts, regulatory hurdles, scaling issues).

        Crucially, after providing the overview, provide a prioritized list of relevant source URLs that you used to gather this information or that you deem important for further research. The URLs should be presented as a JSON array under a key named "source_urls". The overview text should be a single, coherent string.

        Example format for the output:
        {{
          "overview": "Detailed company overview text goes here...",
          "source_urls": [
            "https://example.com/source1",
            "https://example.com/source2",
            "https://example.com/source3"
          ]
        }}

        Ensure the output is a valid JSON object.
        """

        # 2. Call Gemini API
        gemini_response_text = gemini_service.generate_content(prompt)

        if not gemini_response_text:
            return {
                "company_name": company_name,
                "drive_folder_id": drive_folder_id,
                "user_id": user_id,
                "overview_text": "",
                "source_urls": [],
                "status_message": "failed: No response from Gemini API.",
            }

        # 3. Parse Response
        overview_text = ""
        source_urls = []
        status_message = "success"

        try:
            # Attempt to parse as JSON first
            response_json = json.loads(gemini_response_text)
            overview_text = response_json.get("overview", "")
            source_urls = response_json.get("source_urls", [])
            if not isinstance(source_urls, list):
                source_urls = []  # Ensure it's a list
        except json.JSONDecodeError:
            # If not a perfect JSON, try to extract using regex or string manipulation
            status_message = "success_with_parsing_issues: Gemini response was not perfect JSON, extracted best effort."

            # Attempt to extract overview text (everything before "source_urls": [)
            overview_match = re.match(
                r'^(.*?)(?="source_urls": \[|$)', gemini_response_text, re.DOTALL
            )
            if overview_match:
                overview_text = overview_match.group(1).strip()
                # Clean up potential JSON remnants at the end of overview
                if overview_text.endswith('",'):
                    overview_text = overview_text[:-2]
                if overview_text.startswith('{"overview": "'):
                    overview_text = overview_text[len('{"overview": "') :]

            # Attempt to extract URLs using regex
            urls_match = re.search(
                r'"source_urls": \[\s*([^\]]+?)\s*\]', gemini_response_text, re.DOTALL
            )
            if urls_match:
                urls_str = urls_match.group(1)
                # Extract individual URLs, handling various quote types and commas
                found_urls = re.findall(r'"(https?://[^"]+)"', urls_str)
                source_urls = found_urls

            # Fallback if no URLs found in JSON format, try to find any URLs
            if not source_urls:
                source_urls = re.findall(r'https?://[^\s"\']+', gemini_response_text)
                # Filter out common non-URL strings that might match the regex broadly
                source_urls = [
                    url
                    for url in source_urls
                    if not any(
                        ext in url for ext in [".png", ".jpg", ".gif", ".css", ".js"]
                    )
                ]

        # 4. Call save_text_to_gdrive_task
        if overview_text:
            save_text_to_gdrive_task.delay(
                file_content=overview_text,
                company_name=company_name,
                drive_folder_id=drive_folder_id,
                user_id=user_id,
            )

        # 5. Return Value
        return {
            "company_name": company_name,
            "drive_folder_id": drive_folder_id,
            "user_id": user_id,
            "overview_text": overview_text,
            "source_urls": source_urls,
            "status_message": status_message,
        }

    except Exception as e:
        logger.error(f"Error in prospect_deep_dive_task for {company_name}: {e}", exc_info=True)
        self.retry(exc=e, countdown=5, max_retries=3)  # Example retry logic
        return {
            "company_name": company_name,
            "drive_folder_id": drive_folder_id,
            "user_id": user_id,
            "overview_text": "",
            "source_urls": [],
            "status_message": f"error: {str(e)}",
        }


@celery_app.task(bind=True, name="prospect_competitor_analysis_task")
def prospect_competitor_analysis_task(
    self, company_name: str, drive_folder_id: str, user_id: str
):
    """
    Celery task to perform competitor analysis for the target prospect company using Gemini.
    """
    try:
        # 1. Construct Prompt
        prompt = f"""
        Perform a comprehensive competitor analysis for the company: {company_name}.

        Identify its key competitors and analyze their technologies, offerings, strengths, and weaknesses.
        Provide a detailed report that includes:
        - A list of 3-5 key competitors.
        - For each competitor:
            - Their core offerings/products.
            - Key technologies they utilize (e.g., cloud providers, specific software, frameworks).
            - Their main strengths.
            - Their main weaknesses.
            - How they differentiate themselves from {company_name} (if applicable, or from the general market).

        The report should be well-structured and easy to read, suitable for a business audience.
        Present the information clearly, perhaps using bullet points or subheadings for each competitor.
        """

        # 2. Call Gemini API
        gemini_response_text = gemini_service.generate_content(prompt)

        if not gemini_response_text:
            return {
                "company_name": company_name,
                "drive_folder_id": drive_folder_id,
                "user_id": user_id,
                "analysis_report": "",
                "status_message": "failed: No response from Gemini API.",
            }

        # 3. Parse Response (Gemini's response is expected to be free-form text for this task)
        analysis_report = gemini_response_text

        # 4. Call save_text_to_gdrive_task
        if analysis_report:
            file_name = f"{company_name}_Competitor_Analysis.md"
            save_text_to_gdrive_task.delay(
                file_content=analysis_report,
                file_name=file_name,
                drive_folder_id=drive_folder_id,
                user_id=user_id,
            )

        # 5. Return Value
        return {
            "company_name": company_name,
            "drive_folder_id": drive_folder_id,
            "user_id": user_id,
            "analysis_report": analysis_report,
            "status_message": "success",
        }

    except Exception as e:
        logger.error(f"Error in prospect_competitor_analysis_task for {company_name}: {e}", exc_info=True)
        self.retry(exc=e, countdown=5, max_retries=3)  # Example retry logic
        return {
            "company_name": company_name,
            "drive_folder_id": drive_folder_id,
            "user_id": user_id,
            "analysis_report": "",
            "status_message": f"error: {str(e)}",
        }


@celery_app.task(bind=True, name="own_competitor_marketing_analysis_task")
def own_competitor_marketing_analysis_task(
    self,
    prospect_company_name: str,
    prospect_company_industry: str,
    drive_folder_id: str,
    user_id: str,
):
    """
    Celery task to analyze how Palo Alto Networks' competitors are targeting the prospect company's market segment.
    """
    try:
        # Define Palo Alto Networks' key competitors for focused analysis
        palo_alto_competitors = [
            "Cisco (Security Business)",
            "Fortinet",
            "Check Point Software Technologies",
            "CrowdStrike",
            "Zscaler",
            "Microsoft (Azure Security)",
            "Amazon Web Services (AWS Security)",
        ]
        competitors_list_str = ", ".join(palo_alto_competitors)

        # 1. Construct Prompt
        prompt = f"""
        You are an expert in cybersecurity market analysis.
        Palo Alto Networks is a leading cybersecurity company.

        Analyze how Palo Alto Networks' key competitors are targeting the market segment of a prospect company with the following details:
        - Prospect Company Name: {prospect_company_name}
        - Prospect Company Industry: {prospect_company_industry}

        Palo Alto Networks' key competitors include: {competitors_list_str}.

        For each of these competitors, describe their marketing strategies, messaging, and product positioning when targeting companies similar to '{prospect_company_name}' in the '{prospect_company_industry}' industry.
        Focus on:
        - How they articulate their value proposition to this specific market segment.
        - What pain points they address for companies in this industry.
        - What specific products or solutions they emphasize.
        - Their common marketing channels and campaigns relevant to this segment.

        Provide a comprehensive analysis report, suitable for a sales and marketing team, detailing these aspects for each competitor.
        The report should be well-structured, easy to read, and provide actionable insights.
        """

        # 2. Call Gemini API
        gemini_response_text = gemini_service.generate_content(prompt)

        if not gemini_response_text:
            return {
                "prospect_company_name": prospect_company_name,
                "drive_folder_id": drive_folder_id,
                "user_id": user_id,
                "analysis_report": "",
                "status_message": "failed: No response from Gemini API.",
            }

        # 3. Parse Response (Gemini's response is expected to be free-form text for this task)
        analysis_report = gemini_response_text

        # 4. Call save_text_to_gdrive_task
        if analysis_report:
            file_name = f"{prospect_company_name}_Own_Competitive_Marketing_Analysis.md"
            save_text_to_gdrive_task.delay(
                file_content=analysis_report,
                file_name=file_name,
                drive_folder_id=drive_folder_id,
                user_id=user_id,
            )

        # 5. Return Value
        return {
            "prospect_company_name": prospect_company_name,
            "drive_folder_id": drive_folder_id,
            "user_id": user_id,
            "analysis_report": analysis_report,
            "status_message": "success",
        }

    except Exception as e:
        logger.error(f"Error in own_competitor_marketing_analysis_task for {prospect_company_name}: {e}", exc_info=True)
        self.retry(exc=e, countdown=5, max_retries=3)  # Example retry logic
        return {
            "prospect_company_name": prospect_company_name,
            "drive_folder_id": drive_folder_id,
            "user_id": user_id,
            "analysis_report": "",
            "status_message": f"error: {str(e)}",
        }

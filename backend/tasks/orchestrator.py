from celery.utils.log import get_task_logger

from backend.celery_app import celery_app
from backend.tasks.gemini_tasks import (
    prospect_deep_dive_task,
    prospect_competitor_analysis_task,
    own_competitor_marketing_analysis_task,
)
from backend.tasks.content_extraction import extract_url_content_task
from backend.tasks.google_drive_tasks import save_extracted_content_to_gdrive_task

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="research_orchestrator_task")
def research_orchestrator_task(
    self, user_id: str, company_name: str, gdrive_folder_id: str
):
    """
    Orchestrates the entire research workflow, chaining Celery tasks.
    """
    self.update_state(
        state="PROGRESS", meta={"current_phase": "Starting research workflow..."}
    )
    logger.info(
        f"Starting research orchestration for company: {company_name}, user: {user_id}"
    )

    try:
        # Phase 1: Prospect Deep Dive
        self.update_state(
            state="PROGRESS", meta={"current_phase": "Phase 1: Prospect Deep Dive"}
        )
        logger.info("Initiating Prospect Deep Dive task...")
        deep_dive_result = prospect_deep_dive_task.delay(company_name, gdrive_folder_id, user_id).get(
            timeout=600
        )
        logger.info(f"Prospect Deep Dive completed. Result: {deep_dive_result}")

        # Phase 2: Prospect Competitor Analysis
        self.update_state(
            state="PROGRESS",
            meta={"current_phase": "Phase 2: Prospect Competitor Analysis"},
        )
        logger.info("Initiating Prospect Competitor Analysis task...")
        competitor_analysis_result = prospect_competitor_analysis_task.delay(
            company_name, gdrive_folder_id, user_id
        ).get(timeout=600)
        logger.info(
            f"Prospect Competitor Analysis completed. Result: {competitor_analysis_result}"
        )

        # Phase 3: Own Competitor Marketing Analysis
        self.update_state(
            state="PROGRESS",
            meta={"current_phase": "Phase 3: Own Competitor Marketing Analysis"},
        )
        logger.info("Initiating Own Competitor Marketing Analysis task...")
        # TODO: The own_competitor_marketing_analysis_task expects prospect_company_industry.
        # This is not currently available in the orchestrator.
        # For now, passing a placeholder. This needs to be addressed.
        placeholder_industry = "Unknown Industry"
        own_marketing_analysis_result = own_competitor_marketing_analysis_task.delay(
            company_name, placeholder_industry, gdrive_folder_id, user_id
        ).get(timeout=600)
        logger.info(
            f"Own Competitor Marketing Analysis completed. Result: {own_marketing_analysis_result}"
        )

        # Phase 4: Extract URL Content (Example - assuming deep_dive_result contains URLs)
        # In a real scenario, you'd parse URLs from previous results or a dedicated source
        self.update_state(
            state="PROGRESS", meta={"current_phase": "Phase 4: Extracting URL Content"}
        )
        logger.info("Initiating URL Content Extraction task...")
        source_urls_from_deep_dive = []
        if deep_dive_result and isinstance(deep_dive_result, dict):
            source_urls_from_deep_dive = deep_dive_result.get("source_urls", [])

        if not source_urls_from_deep_dive:
            logger.warning("No source URLs found from deep dive to extract content.")
            extracted_content_results = []
        else:
            logger.info(f"Extracting content from {len(source_urls_from_deep_dive)} URLs: {source_urls_from_deep_dive}")
            # The extract_url_content_task expects a list of URLs and processes them internally.
            # We call it once with all URLs.
            extracted_content_results = extract_url_content_task.delay(
                source_urls=source_urls_from_deep_dive,
                # Pass drive_folder_id and user_id if the task is to save directly.
                # Current design: orchestrator saves after this task.
                # drive_folder_id=gdrive_folder_id,
                # user_id=user_id
            ).get(timeout=300 * len(source_urls_from_deep_dive)) # Adjust timeout based on number of URLs

        logger.info(
            f"URL Content Extraction completed. Results: {extracted_content_results}"
        )

        # Phase 5: Save Extracted Content to Google Drive
        self.update_state(
            state="PROGRESS",
            meta={"current_phase": "Phase 5: Saving Content to Google Drive"},
        )
        logger.info("Initiating Save Extracted Content to Google Drive task...")
        # Assuming extracted_content_results is a list of dicts with 'url' and 'content'
        for item in extracted_content_results:
            file_name = f"{company_name}_{item['url'].replace('https://', '').replace('/', '_')}.txt"
            # Ensure item['content'] is not None before saving
            if item.get("content"):
                save_extracted_content_to_gdrive_task.delay(
                    item["content"], file_name, gdrive_folder_id, user_id # Corrected argument order
                ).get(timeout=300)
            else:
                logger.warning(f"Skipping save for {file_name} as content is missing.")
        logger.info("Saving Extracted Content to Google Drive completed.")

        result_link = f"https://drive.google.com/drive/folders/{gdrive_folder_id}"
        self.update_state(
            state="SUCCESS",
            meta={
                "current_phase": "Research workflow completed successfully!",
                "result_link": result_link,
            },
        )
        logger.info(
            f"Research orchestration completed successfully for company: {company_name}. Google Drive link: {result_link}"
        )
        return {
            "status": "SUCCESS",
            "message": "Research workflow completed successfully.",
            "result_link": result_link,
        }

    except Exception as e:
        logger.error(
            f"Research orchestration failed for company: {company_name}, error: {e}",
            exc_info=True,
        )
        self.update_state(
            state="FAILURE",
            meta={"current_phase": "Research workflow failed", "error": str(e)},
        )
        return {"status": "FAILURE", "message": f"Research workflow failed: {str(e)}"}

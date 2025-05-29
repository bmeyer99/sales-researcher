from celery import Celery
from celery.utils.log import get_task_logger

from backend.celery_app import celery_app
from backend.tasks.gemini_tasks import prospect_deep_dive_task, prospect_competitor_analysis_task, own_competitor_marketing_analysis_task
from backend.tasks.content_extraction import extract_url_content_task
from backend.tasks.google_drive_tasks import save_extracted_content_to_gdrive_task

logger = get_task_logger(__name__)

@celery_app.task(bind=True, name="research_orchestrator_task")
def research_orchestrator_task(self, user_id: str, company_name: str, gdrive_folder_id: str):
    """
    Orchestrates the entire research workflow, chaining Celery tasks.
    """
    self.update_state(state='PROGRESS', meta={'current_phase': 'Starting research workflow...'})
    logger.info(f"Starting research orchestration for company: {company_name}, user: {user_id}")

    try:
        # Phase 1: Prospect Deep Dive
        self.update_state(state='PROGRESS', meta={'current_phase': 'Phase 1: Prospect Deep Dive'})
        logger.info("Initiating Prospect Deep Dive task...")
        deep_dive_result = prospect_deep_dive_task.delay(user_id, company_name).get(timeout=600)
        logger.info(f"Prospect Deep Dive completed. Result: {deep_dive_result}")

        # Phase 2: Prospect Competitor Analysis
        self.update_state(state='PROGRESS', meta={'current_phase': 'Phase 2: Prospect Competitor Analysis'})
        logger.info("Initiating Prospect Competitor Analysis task...")
        competitor_analysis_result = prospect_competitor_analysis_task.delay(user_id, company_name).get(timeout=600)
        logger.info(f"Prospect Competitor Analysis completed. Result: {competitor_analysis_result}")

        # Phase 3: Own Competitor Marketing Analysis
        self.update_state(state='PROGRESS', meta={'current_phase': 'Phase 3: Own Competitor Marketing Analysis'})
        logger.info("Initiating Own Competitor Marketing Analysis task...")
        own_marketing_analysis_result = own_competitor_marketing_analysis_task.delay(user_id, company_name).get(timeout=600)
        logger.info(f"Own Competitor Marketing Analysis completed. Result: {own_marketing_analysis_result}")

        # Phase 4: Extract URL Content (Example - assuming deep_dive_result contains URLs)
        # In a real scenario, you'd parse URLs from previous results or a dedicated source
        self.update_state(state='PROGRESS', meta={'current_phase': 'Phase 4: Extracting URL Content'})
        logger.info("Initiating URL Content Extraction task...")
        # For demonstration, let's assume deep_dive_result contains a list of URLs
        # Replace with actual URL extraction logic from previous tasks' outputs
        example_urls = ["https://www.example.com", "https://www.anotherexample.com"]
        extracted_content_results = []
        for url in example_urls:
            content = extract_url_content_task.delay(url).get(timeout=300)
            extracted_content_results.append({"url": url, "content": content})
        logger.info(f"URL Content Extraction completed. Results: {extracted_content_results}")

        # Phase 5: Save Extracted Content to Google Drive
        self.update_state(state='PROGRESS', meta={'current_phase': 'Phase 5: Saving Content to Google Drive'})
        logger.info("Initiating Save Extracted Content to Google Drive task...")
        # Assuming extracted_content_results is a list of dicts with 'url' and 'content'
        for item in extracted_content_results:
            file_name = f"{company_name}_{item['url'].replace('https://', '').replace('/', '_')}.txt"
            save_extracted_content_to_gdrive_task.delay(user_id, gdrive_folder_id, file_name, item['content']).get(timeout=300)
        logger.info("Saving Extracted Content to Google Drive completed.")

        result_link = f"https://drive.google.com/drive/folders/{gdrive_folder_id}"
        self.update_state(state='SUCCESS', meta={'current_phase': 'Research workflow completed successfully!', 'result_link': result_link})
        logger.info(f"Research orchestration completed successfully for company: {company_name}. Google Drive link: {result_link}")
        return {"status": "SUCCESS", "message": "Research workflow completed successfully.", "result_link": result_link}

    except Exception as e:
        logger.error(f"Research orchestration failed for company: {company_name}, error: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'current_phase': 'Research workflow failed', 'error': str(e)})
        return {"status": "FAILURE", "message": f"Research workflow failed: {str(e)}"}
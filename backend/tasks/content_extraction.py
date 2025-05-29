import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Optional

from backend.celery_app import celery_app
from backend.services.content_extraction_service import fetch_and_extract_text
from markdownify import markdownify as md

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text

@celery_app.task(bind=True)
def extract_url_content_task(self, source_urls: list[str], drive_folder_id: Optional[str] = None, user_id: Optional[str] = None):
    from backend.tasks.google_drive_tasks import save_extracted_content_to_gdrive_task
    
    results = []
    total_urls = len(source_urls)

    for index, url in enumerate(source_urls):
        self.update_state(state='PROGRESS', meta={'current': index + 1, 'total': total_urls, 'url': url})
        extracted_content = None
        extracted_title = None
        status = "failed"
        error = None

        try:
            content = fetch_and_extract_text(url)
            if content:
                # Attempt to parse HTML to get title and then convert to Markdown
                if "<html" in content.lower() or "<body" in content.lower():
                    soup = BeautifulSoup(content, 'html.parser')
                    title_tag = soup.find('title')
                    if title_tag:
                        extracted_title = title_tag.get_text(strip=True)
                    
                    markdown_content = md(content)
                else:
                    markdown_content = content
                    # For non-HTML content, use a truncated URL as a fallback title
                    extracted_title = urlparse(url).netloc + urlparse(url).path[:20]

                extracted_content = markdown_content
                status = "success"
            else:
                error = "Failed to fetch or extract content"
        except Exception as e:
            error = f"An error occurred: {str(e)}"

        results.append({
            "url": url,
            "title": extracted_title,
            "content": extracted_content,
            "status": status,
            "error": error
        })
    
    if drive_folder_id and user_id:
        # Chain the task to save extracted content to Google Drive
        save_extracted_content_to_gdrive_task.delay(results, drive_folder_id, user_id)
    
    return results
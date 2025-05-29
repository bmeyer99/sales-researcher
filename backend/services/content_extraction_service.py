import trafilatura
import logging

logger = logging.getLogger(__name__)

def fetch_and_extract_text(url: str) -> str | None:
    """
    Fetches a webpage from the given URL and extracts its main text content using trafilatura.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str | None: The extracted main text content, or None if extraction fails.
    """
    try:
        # Download the webpage
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            logger.warning(f"Failed to download content from URL: {url}")
            return None

        # Extract the main text content
        extracted_text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)

        if extracted_text is None:
            logger.warning(f"Failed to extract significant text from URL: {url}")
            return None

        return extracted_text
    except Exception as e:
        logger.error(f"An error occurred during content extraction for URL {url}: {e}")
        return None
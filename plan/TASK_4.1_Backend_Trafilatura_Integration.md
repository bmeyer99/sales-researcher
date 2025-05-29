# Task 4.1: Backend - `trafilatura` Integration

**Phase:** Phase 4: Content Extraction & Finalization
**Parent Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
**Status:** To Do
**Last Updated:** 2025-05-29

## 1. Description
Integrate the `trafilatura` Python library into the backend. This library will be used to fetch web pages from URLs and extract the main text content, stripping away boilerplate like navigation, ads, and footers.

## 2. Detailed Steps / Implementation Notes

1.  **Add Dependency:**
    *   Add `trafilatura` to the `backend/requirements.txt` file.
        ```txt
        # backend/requirements.txt
        # ... other dependencies
        trafilatura>=1.5.0,<1.9.0 # Check for latest stable version
        ```
    *   Install it in the local venv and ensure it'll be in the Docker image.
    *   `trafilatura` has some optional dependencies for extended functionality (e.g., `brotli` for decompressing Brotli-encoded content, `justext` for an alternative extraction algorithm). Consider if these are needed. For basic usage, the core library is often sufficient.

2.  **Create Content Extraction Service (`backend/services/content_extraction_service.py` or similar):**
    *   Create a Python module to encapsulate web page fetching and text extraction logic using `trafilatura`.
        ```python
        # Example: backend/services/content_extraction_service.py
        import trafilatura
        from trafilatura.settings import use_config # For customizing settings if needed
        import requests # trafilatura can use requests or urllib, ensure one is available

        # Optional: Configure trafilatura if defaults are not sufficient
        # config = use_config()
        # config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "500") # Example: min characters for main content
        # config.set("DEFAULT", "MIN_OUTPUT_SIZE", "250")   # Example: min characters for output text

        def fetch_and_extract_text(url: str, include_comments: bool = False, target_language: str = None) -> str | None:
            """
            Fetches a web page from the given URL and extracts its main text content.

            Args:
                url: The URL of the web page to process.
                include_comments: Whether to include comments in the extracted text.
                target_language: Optional target language for extraction.

            Returns:
                The extracted main text content as a string, or None if extraction fails.
            """
            # 1. Download the webpage
            # trafilatura.fetch_url downloads the content of the URL
            downloaded = trafilatura.fetch_url(url)

            if downloaded is None:
                print(f"Failed to download content from URL: {url}")
                return None

            # 2. Extract main text content
            # trafilatura.extract returns the main text, stripping boilerplate
            # `include_comments=False` is default, set to True if comments are desired
            # `target_language` can help if language is known, e.g., 'en'
            extracted_text = trafilatura.extract(
                downloaded,
                include_comments=include_comments,
                target_language=target_language,
                # Optional: pass the config object if customized
                # config=config,
                # Optional: provide URL for better metadata extraction if `downloaded` is just HTML string
                # url=url
            )

            if extracted_text:
                return extracted_text.strip()
            else:
                print(f"Could not extract main content from URL: {url}")
                return None

        # Example usage:
        # if __name__ == '__main__':
        //     test_url = "https_example_com_some_article" # Replace with a real article URL
        //     text = fetch_and_extract_text(test_url)
        //     if text:
        //         print(f"Extracted text from {test_url}:\n{text[:500]}...") # Print first 500 chars
        //     else:
        //         print(f"No text extracted from {test_url}.")
        ```

3.  **Error Handling:**
    *   `trafilatura.fetch_url` can return `None` if the download fails (e.g., network error, 404).
    *   `trafilatura.extract` can return `None` if it cannot find significant main content.
    *   The service function should handle these cases and propagate errors or return `None` appropriately.
    *   Consider adding try-except blocks for network-related exceptions if using `requests` directly before `trafilatura.extract`.

4.  **Configuration (Optional):**
    *   `trafilatura` is configurable. Default settings usually work well, but for specific needs (e.g., minimum content size, handling of tables/comments), its configuration can be adjusted. The example shows how to use `use_config()`.

## 3. Expected Output / Deliverables
*   `trafilatura` library added to `backend/requirements.txt`.
*   A backend service module (e.g., `backend/services/content_extraction_service.py`) that provides a function (`fetch_and_extract_text`) to:
    *   Download content from a given URL.
    *   Extract the main text content using `trafilatura`.
    *   Return the extracted text or `None` on failure.

## 4. Dependencies
*   None directly from previous project tasks, but it requires network access for the worker.

## 5. Acceptance Criteria
*   The `fetch_and_extract_text` function can successfully download and extract main text from a sample news article URL.
*   The function returns `None` or handles errors gracefully for invalid URLs or pages where content extraction fails.
*   The extracted text is reasonably clean (i.e., boilerplate is mostly removed).

## 6. Estimated Effort (Optional)
*   Small (integrating and using `trafilatura` for basic extraction is straightforward).

## 7. Notes / Questions
*   **Website Compatibility:** `trafilatura` works well for many websites, especially news articles and blog posts. However, its effectiveness can vary for highly dynamic JavaScript-rendered sites or sites with unusual structures.
*   **Respect `robots.txt` / Rate Limiting:** When crawling multiple URLs from a single site, be mindful of `robots.txt` and implement politeness (e.g., delays between requests, identify your bot with a User-Agent) to avoid overloading servers or getting blocked. `trafilatura` itself focuses on extraction from given HTML content; the fetching part is where politeness applies.
*   **User-Agent:** `trafilatura.fetch_url` (which uses `urllib.request` by default) will use a default Python User-Agent. For more control or to set a custom User-Agent, you might fetch the HTML content using `requests` library first and then pass the HTML string to `trafilatura.extract()`.
*   **Character Encoding:** `trafilatura` generally handles encoding well, but be aware of potential issues with exotic sites.
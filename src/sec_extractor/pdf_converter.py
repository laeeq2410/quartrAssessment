"""Convert a filing's HTML document to PDF."""

import re  # Find the opening head tag in the HTML text.
from html import escape  # Make the source URL safe to insert into an HTML attribute.
from pathlib import Path  # Describe the destination PDF path.


def convert_html_to_pdf(html: str, base_url: str, output_path: Path) -> None:
    """Use Chromium to save the filing HTML as a PDF."""
    # Import here so other parts of the application can be tested without loading Playwright.
    try:
        from playwright.sync_api import sync_playwright
    # Explain the missing dependency while retaining the original error as its cause.
    except ImportError as error:
        raise RuntimeError(
            "PDF conversion requires Playwright. Install project requirements and Chromium."
        ) from error

    # The base tag lets relative images and stylesheets resolve from the SEC filing URL.
    base_tag = f'<base href="{escape(base_url, quote=True)}">'
    # Match an opening head tag, allowing attributes and any mix of uppercase/lowercase letters.
    head_match = re.search(r"<head\b[^>]*>", html, flags=re.IGNORECASE)
    if head_match:
        # Insert the base tag just after the opening head tag, keeping the rest of the HTML.
        html = html[:head_match.end()] + base_tag + html[head_match.end():]
    else:
        # If there is no head tag, wrap the content with one that contains our base URL.
        html = f"<html><head>{base_tag}</head><body>{html}</body></html>"

    # Start Playwright's synchronous API; with shuts down its resources when this block exits.
    with sync_playwright() as playwright:
        # Launch the installed Microsoft Edge browser in headless mode (no visible window).
        browser = playwright.chromium.launch(channel="msedge")
        # Ensure the browser is closed even if loading the HTML or saving the PDF fails.
        try:
            # Open a new browser page for this report.
            page = browser.new_page()
            # Load the downloaded HTML and wait for its load event, allowing up to 60 seconds.
            page.set_content(html, wait_until="load", timeout=60_000)
            # Print to a US Letter PDF, including background colors and images.
            page.pdf(path=str(output_path), format="Letter", print_background=True)
        # finally runs on both success and failure.
        finally:
            browser.close()
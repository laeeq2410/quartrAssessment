"""Fetch the latest 10-K PDFs for the target companies."""

from pathlib import Path  # Build file and folder paths in a platform-independent way.

from sec_extractor.companies import COMPANIES  # Load the company list from our configuration.
from sec_extractor.filing_service import download_latest_10k_pdf  # Import the download workflow.


# This function runs the program; -> None means it does not return a result to its caller.
def main() -> None:
    # __file__ is this file; resolve() makes its path absolute and parent gives its folder.
    output_dir = Path(__file__).resolve().parent / "output"

    # Process one company at a time, in the order listed in COMPANIES.
    for company in COMPANIES:
        print(f"Fetching the latest 10-K for {company['name']}...")
        # Handle failures separately so one company's error does not stop the remaining companies.
        try:
            # Run the complete workflow and receive the saved PDF's path.
            pdf_path = download_latest_10k_pdf(
                company_name=company["name"],  # The name is required for lookup and filenames.
                cik=company.get("cik"),  # Unlike [], get() returns None when the key is missing.
                output_dir=output_dir,  # Tell the workflow where to write the PDF.
            )
            print(f"Saved PDF: {pdf_path}")
        # Capture the error message and let the loop continue with the next company.
        except Exception as error:
            print(f"Could not download {company['name']}: {error}")


# Start downloads only when run directly, not when another file imports this module.
if __name__ == "__main__":
    main()
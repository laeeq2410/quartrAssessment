"""Find and save a company's latest 10-K as a PDF."""

import re  # Use a regular expression to remove unsafe characters from filenames.
from pathlib import Path  # Represent the output directory and PDF path.

# The dot means these modules belong to the same sec_extractor package.
from . import pdf_converter, sec_client


def select_latest_10k(submissions: dict) -> dict:
    """Return the newest regular 10-K in a submissions response."""
    # SEC stores recent filings as separate lists, rather than a list of filing dictionaries.
    recent = submissions["filings"]["recent"]
    # zip() groups values at the same index into one row for each filing.
    filings = zip(
        recent["form"],  # Form type, such as 10-K or 10-Q.
        recent["filingDate"],  # The date the filing was submitted, in YYYY-MM-DD format.
        recent["accessionNumber"],  # SEC's identifier for this particular filing.
        recent["primaryDocument"],  # The main report's document filename.
    )
    # Build a dictionary for each regular annual report and collect those dictionaries in a list.
    ten_ks = [
        {
            "form": form,
            "filingDate": filing_date,
            "accessionNumber": accession_number,
            "primaryDocument": primary_document,
        }
        # Unpack each grouped row into four readable variable names.
        for form, filing_date, accession_number, primary_document in filings
        # Match exactly: amended reports (10-K/A) and quarterly reports (10-Q) are excluded.
        if form == "10-K"
    ]

    # An empty list means there are no regular 10-Ks in this response's recent filings.
    if not ten_ks:
        raise ValueError("No 10-K filing was found in the recent submissions.")

    # YYYY-MM-DD strings sort in date order; lambda tells max() which field to compare.
    return max(ten_ks, key=lambda filing: filing["filingDate"])


def download_latest_10k_pdf(
    company_name: str,  # Company name used for lookup and the PDF filename.
    cik: str | None,  # A supplied CIK or None when it needs to be discovered.
    output_dir: Path,  # Folder where the resulting PDF belongs.
) -> Path:
    """Download the latest 10-K and save a PDF in the output directory."""
    # Resolve the company identifier before requesting its filings.
    cik = sec_client.get_company_cik(company_name, cik)
    # Get the company's filing metadata as a Python dictionary.
    submissions = sec_client.get_submissions(cik)
    # Choose the most recently filed regular 10-K from that metadata.
    filing = select_latest_10k(submissions)
    # Download the main report; unpack the returned pair into its URL and HTML text.
    filing_url, filing_html = sec_client.get_filing_document(
        cik,  # Identifies the company in the SEC archive.
        filing["accessionNumber"],  # Identifies the filing folder.
        filing["primaryDocument"],  # Identifies the document inside that folder.
    )

    # Create any missing parent folders; do not fail if the output folder already exists.
    output_dir.mkdir(parents=True, exist_ok=True)
    # Replace groups of nonletters/nondigits with underscores, then remove edge underscores.
    safe_company_name = re.sub(r"[^A-Za-z0-9]+", "_", company_name).strip("_")
    # Path's / operator joins a folder and filename; this date is the filing date, not fiscal year.
    pdf_path = output_dir / f"{safe_company_name}_10-K_{filing['filingDate']}.pdf"
    # Render the downloaded HTML and write the PDF to disk.
    pdf_converter.convert_html_to_pdf(filing_html, filing_url, pdf_path)
    # Give main() the path so it can display where the PDF was saved.
    return pdf_path
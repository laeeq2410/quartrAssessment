import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sec_extractor.filing_service import download_latest_10k_pdf, select_latest_10k


def sample_submissions() -> dict:
    return {
        "filings": {
            "recent": {
                "form": ["10-K", "10-Q", "10-K/A", "10-K"],
                "filingDate": ["2023-02-01", "2024-05-01", "2024-02-10", "2025-02-01"],
                "accessionNumber": ["old", "quarterly", "amended", "latest"],
                "primaryDocument": ["old.htm", "quarterly.htm", "amended.htm", "latest.htm"],
            }
        }
    }


class FilingServiceTests(unittest.TestCase):
    def test_selects_newest_regular_10k(self) -> None:
        filing = select_latest_10k(sample_submissions())

        self.assertEqual(filing["accessionNumber"], "latest")

    def test_raises_when_no_10k_is_available(self) -> None:
        submissions = sample_submissions()
        submissions["filings"]["recent"]["form"] = ["10-Q"] * 4

        with self.assertRaisesRegex(ValueError, "No 10-K"):
            select_latest_10k(submissions)

    def test_downloads_and_converts_the_latest_filing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "output"
            with (
                patch("sec_extractor.filing_service.sec_client.get_submissions", return_value=sample_submissions()),
                patch(
                    "sec_extractor.filing_service.sec_client.get_filing_document",
                    return_value=("https://www.sec.gov/example.htm", "<html></html>"),
                ),
                patch("sec_extractor.filing_service.pdf_converter.convert_html_to_pdf") as convert,
            ):
                pdf_path = download_latest_10k_pdf(
                    "Apple Inc.", "0000320193", output_dir
                )

        self.assertEqual(pdf_path.name, "Apple_Inc_10-K_2025-02-01.pdf")
        convert.assert_called_once()


if __name__ == "__main__":
    unittest.main()
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sec_extractor.sec_client import get_company_cik, get_filing_document, get_submissions


class SecClientTests(unittest.TestCase):
    @patch("sec_extractor.sec_client._read_url", return_value='{"ok": true}')
    def test_submissions_url_uses_ten_digit_cik(self, read_url) -> None:
        result = get_submissions("320193")

        self.assertEqual(result, {"ok": True})
        read_url.assert_called_once_with(
            "https://data.sec.gov/submissions/CIK0000320193.json"
        )

    @patch("sec_extractor.sec_client._read_url", return_value="<html></html>")
    def test_filing_url_uses_archive_path_format(self, read_url) -> None:
        url, document = get_filing_document(
            "0000320193", "0000320193-25-000001", "annual report.htm"
        )

        self.assertEqual(
            url,
            "https://www.sec.gov/Archives/edgar/data/320193/000032019325000001/annual%20report.htm",
        )
        self.assertEqual(document, "<html></html>")

    def test_finds_and_caches_cik_when_missing(self) -> None:
        sec_company_list = json.dumps(
            {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "APPLE INC."}}
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            cache_path = Path(temporary_directory) / "company_ciks.json"
            with patch(
                "sec_extractor.sec_client._read_url", return_value=sec_company_list
            ) as read_url:
                cik = get_company_cik("Apple Inc.", None, cache_path)

            self.assertEqual(cik, "0000320193")
            read_url.assert_called_once()

            with patch("sec_extractor.sec_client._read_url") as read_url:
                cached_cik = get_company_cik("Apple Inc.", None, cache_path)

            self.assertEqual(cached_cik, "0000320193")
            read_url.assert_not_called()


if __name__ == "__main__":
    unittest.main()
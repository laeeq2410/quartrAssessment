"""Small HTTP client for the SEC submissions and filing archive endpoints."""

import json  # Convert between JSON text and Python dictionaries.
import re  # Clean up company names for consistent matching.
from pathlib import Path  # Locate, read, and write the local cache file.
from urllib.parse import quote  # Encode special characters in document URL paths.
from urllib.request import Request, urlopen  # Build and send HTTP requests.


# SEC asks automated clients to identify themselves with a name and monitored contact email.
SEC_USER_AGENT = "Quartr 10-K downloader laeeq2410@hotmail.com"
# The submissions endpoint uses a ten-digit company identifier, including leading zeros.
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
# Filing documents live in the archive, separately from the metadata API.
SEC_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data"
# This SEC file maps listed company names and tickers to their CIKs.
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
# parents[2] reaches the project root from this file under src/sec_extractor/.
DEFAULT_CIK_CACHE_PATH = Path(__file__).resolve().parents[2] / ".cache" / "company_ciks.json"


# The leading underscore indicates an internal helper; str annotations describe text inputs/outputs.
def _read_url(url: str) -> str:
    # Attach our identifying header to SEC metadata and document requests made through this helper.
    request = Request(url, headers={"User-Agent": SEC_USER_AGENT})
    # Open the response with a 30-second timeout; with closes it even if an error occurs.
    with urlopen(request, timeout=30) as response:
        # Use the server's text encoding when provided, otherwise assume UTF-8.
        encoding = response.headers.get_content_charset() or "utf-8"
        # Read bytes and decode to text, replacing any characters that cannot be decoded.
        return response.read().decode(encoding, errors="replace")


def get_submissions(cik: str) -> dict:
    """Return the SEC submissions JSON for a company."""
    # zfill(10) adds leading zeros if needed; format() replaces {cik} in the URL template.
    url = SEC_SUBMISSIONS_URL.format(cik=cik.zfill(10))
    # Fetch the JSON text, then loads() parses it into a Python dictionary.
    return json.loads(_read_url(url))


def _normalize_company_name(company_name: str) -> str:
    # Lowercase the name, replace punctuation with spaces, and split it into words.
    words = re.sub(r"[^a-z0-9]+", " ", company_name.lower()).split()
    # Only inspect the first word if the list is nonempty.
    if words and words[0] == "the":
        # Keep everything after the optional opening word "the".
        words = words[1:]
    # Remove common legal suffixes from the end, checking again after each removal.
    while words and words[-1] in {
        "inc", "incorporated", "corp", "corporation", "company", "co", "limited", "ltd"
    }:
        # With no index, pop() removes the last word in the list.
        words.pop()
    # Join the remaining words with single spaces to form the lookup/cache key.
    return " ".join(words)


def get_company_cik(
    company_name: str,  # The company to match in the SEC company list.
    cik: str | None,  # An optional identifier supplied by the caller.
    cache_path: Path | None = None,  # Tests can provide a temporary cache instead of the real one.
) -> str:
    """Return the supplied CIK or find and cache it by company name."""
    # None, empty strings, and whitespace-only strings mean that lookup is needed.
    if cik is not None and cik.strip():
        # A supplied CIK must contain only digits; strip() above does not change the original value.
        if not cik.isdigit():
            raise ValueError(f"Invalid SEC CIK for {company_name}: {cik}")
        # Return the known identifier immediately without reading the cache or making a lookup request.
        return cik.zfill(10)

    # Use the same cleanup rules for caller-provided names and SEC names.
    normalized_name = _normalize_company_name(company_name)
    # Reject names that become empty after cleanup.
    if not normalized_name:
        raise ValueError("A company name is required to look up its CIK.")

    # Use the caller's cache location, or fall back to the project's .cache folder.
    cache_path = cache_path or DEFAULT_CIK_CACHE_PATH
    # Read a saved JSON dictionary if the file exists; otherwise start with an empty dictionary.
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    # A cached identifier avoids downloading the SEC company list again.
    if normalized_name in cache:
        return cache[normalized_name]

    # Download the SEC company list only when the identifier was not supplied or cached.
    companies = json.loads(_read_url(SEC_COMPANY_TICKERS_URL))
    # A set collects distinct CIKs so multiple share tickers for the same company count once.
    matching_ciks = {
        # SEC's numeric cik_str becomes a ten-digit string for the submissions API.
        str(company["cik_str"]).zfill(10)
        # values() iterates over the company records rather than their JSON record keys.
        for company in companies.values()
        # Require the complete normalized name to match rather than guessing from a partial name.
        if _normalize_company_name(company["title"]) == normalized_name
    }

    # No match requires a more accurate name or an explicitly supplied CIK.
    if not matching_ciks:
        raise ValueError(f"Could not find a CIK for {company_name!r} in the SEC company list.")
    # Never silently choose between different companies with the same cleaned name.
    if len(matching_ciks) > 1:
        raise ValueError(f"More than one SEC CIK matched {company_name!r}; please provide the CIK.")

    # Exactly one identifier remains; remove and retrieve it from the set.
    cik = matching_ciks.pop()
    # Add this successful lookup without removing any other cached companies.
    cache[normalized_name] = cik
    # Create .cache and any missing parents; an existing directory is fine.
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    # Save readable, alphabetically sorted JSON with a final newline for the next run.
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Give the discovered identifier back to the filing service.
    return cik


def get_filing_document(cik: str, accession_number: str, primary_document: str) -> tuple[str, str]:
    """Return the archive URL and HTML for one filing document."""
    # Converting through int removes leading zeros, as required by SEC archive paths.
    archive_cik = str(int(cik))
    # The filing's archive folder uses its accession number without dashes.
    accession = accession_number.replace("-", "")
    # Encode characters such as spaces so the filename works inside a URL.
    document = quote(primary_document)
    # Combine the archive root, company, filing folder, and main document filename.
    url = f"{SEC_ARCHIVE_URL}/{archive_cik}/{accession}/{document}"
    # Return two strings together: the source URL and its downloaded HTML.
    return url, _read_url(url)
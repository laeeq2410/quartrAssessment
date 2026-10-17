# SEC 10-K PDF Downloader

Downloads the latest regular 10-K filing for Apple, Meta, Alphabet, Amazon, Netflix, and Goldman Sachs, then converts each filing to PDF.

## Setup

Use Python 3.10 or newer. From the project directory, create and activate a virtual environment, then install the project dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Before running, update `SEC_USER_AGENT` in `src/sec_extractor/sec_client.py` with your name or organization and a monitored email address, as required by SEC automated-access guidance.

Each company entry in `src/sec_extractor/companies.py` needs a `name`. A CIK can be provided directly, or set to `None` (or omitted) to look it up in the SEC company list. Successful lookups are saved in `.cache/company_ciks.json` and reused on later runs.

## Run

```powershell
python main.py
```

PDFs are written to `output/`. Playwright uses the installed Microsoft Edge browser to render the filing HTML, so no GTK/Pango installation or separate browser download is needed. Microsoft Edge must be installed. The program reports an error for a company and continues with the next one if a filing cannot be downloaded.

## Tests

```powershell
python -m unittest discover -s tests
```

The tests use mocked SEC responses and do not make network requests.
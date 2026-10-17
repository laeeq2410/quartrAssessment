# AI Prompt Log

GitHub Copilot was used to help design, implement, debug, document, and test this project.

This is a curated log of implementation-related requests in conversation order, not a complete chat transcript. Requests and outcomes below are summarized rather than quoted verbatim.

## Implementation Requests

1. **Plan the SEC integration.** Use the assignment and supplied SEC API documentation to plan downloading the latest 10-K filings for Apple, Meta, Alphabet, Amazon, Netflix, and Goldman Sachs and converting them to PDF.

2. **Create an initial implementation.** Start with `sec_10k.py` and `main.py`, keeping the logic simple and adding natural comments. Copilot created the initial SEC lookup, document download, PDF conversion, and company loop.

3. **Adopt the modular structure.** Move the implementation into `src/sec_extractor/` with company configuration, SEC client, filing service, PDF converter, and tests, without `__init__.py`. Copilot also added packaging configuration, run instructions, and Git exclusions.

4. **Set up a virtual environment.** Create `.venv` and install the project dependencies there. Dependency installation was subsequently completed in that environment.

5. **Remove stock tickers.** Use company names rather than tickers for PDF filenames and allow additional companies to be added through the company list. Copilot removed ticker fields and updated the workflow and filename test.

6. **Test one company first.** Provide virtual-environment and Python commands for an Apple-only run before processing the full company list.

7. **Investigate the Windows PDF conversion failure.** Diagnose the reported WeasyPrint `libgobject-2.0-0` error. Copilot identified the native-library dependency and consulted the WeasyPrint installation documentation.

8. **Replace WeasyPrint.** Implement the proposed Playwright alternative. Copilot updated the converter, dependency configuration, and setup instructions. A Chromium download failed certificate validation, so the implementation used the installed Microsoft Edge browser without disabling TLS verification. A temporary PDF smoke test and an Apple end-to-end download succeeded.

9. **Discover and persist missing CIKs.** If a company's CIK is missing or null, look it up automatically and save it for the next run. Copilot added SEC company-list lookup, normalized name matching, ambiguity checks, and a local `.cache/company_ciks.json` file, plus a cache-reuse test.

10. **Check the company configuration error.** Inspect the reported problem in `companies.py`. Copilot fixed a missing comma after the Apple entry and checked the resulting diagnostics.

11. **Add detailed learning comments.** Comment almost every instruction to make the code easier to understand. Copilot added explanatory comments throughout the application files without changing executable logic and reran the six unit tests successfully.

12. **Rerun the test cases.** Run the existing unit tests again. All six passed. These mocked tests cover filing selection, missing-10-K handling, workflow coordination, SEC URL construction, and CIK lookup/cache reuse; they do not perform live downloads or actual PDF conversion.

13. **Update the dependency file.** Update `requirements.txt`. Copilot listed `playwright>=1.50` explicitly while retaining `-e .` for the local package and validated dependency resolution with a pip dry run.

14. **Update this log.** Bring the implementation-related prompt log up to date while excluding basic explanatory questions. Copilot revised this document and retained the distinction between summaries and a full transcript.
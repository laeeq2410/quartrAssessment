"""Companies included in the 10-K download run."""

# Each dictionary describes one company; add another entry to process another company.
# An empty CIK triggers lookup from the cache or, if needed, the SEC company list.
# You can also supply a known CIK as a string, use None, or omit the cik key entirely.
COMPANIES = [
    {"name": "Apple Inc.", "cik": ""},
    {"name": "Meta Platforms, Inc.", "cik": ""},
    {"name": "Alphabet Inc.", "cik": ""},
    {"name": "Amazon.com, Inc.", "cik": ""},
    {"name": "Netflix, Inc.", "cik": ""},
    {"name": "The Goldman Sachs Group, Inc.", "cik": ""},
]
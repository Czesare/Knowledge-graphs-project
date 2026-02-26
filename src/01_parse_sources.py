"""
Step 1: Parse PDFs and scenario CSV into clean text files.

Usage:
    python 01_parse_sources.py

Reads PDFs from papers/ and scenarios from scenarios/scenarios.csv.
Outputs clean text to output/text/ for inspection and LLM consumption.
"""
import re
import csv
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Install pdfplumber: pip install pdfplumber")
    raise

from config import PAPERS_DIR, SCENARIOS_CSV, OUTPUT_DIR, MAX_PAPER_CHARS, STRIP_REFERENCES


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from a PDF using pdfplumber."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def strip_references_section(text: str) -> str:
    """
    Remove the references/bibliography section from paper text.
    This saves tokens and removes noise for the LLM.
    We look for common section headers that start the references.
    """
    # Common patterns for reference sections in academic papers
    patterns = [
        r'\n\s*References\s*\n',
        r'\n\s*REFERENCES\s*\n',
        r'\n\s*Bibliography\s*\n',
        r'\n\s*BIBLIOGRAPHY\s*\n',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return text[:match.start()].strip()
    return text


def clean_text(text: str) -> str:
    """Basic text cleanup: normalize whitespace, remove artifacts."""
    # Collapse multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove page numbers that are just a number on a line
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)
    # Remove excessive spaces
    text = re.sub(r' {3,}', ' ', text)
    return text.strip()


def parse_scenarios(csv_path: Path) -> list[dict]:
    """
    Parse the scenarios CSV. For each row, pick Best or Worst case
    based on the 'Choose' column.
    """
    scenarios = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            choose = row['Choose'].strip()
            scenario_id = int(row['ID'])

            if choose == 'Best':
                team = row['Best Case - Use Case HI Team']
                description = row['Best Case - Scenario']
            else:
                team = row['Worst Case - Use Case HI Team']
                description = row['Worst Case - Scenario']

            scenarios.append({
                'id': f'scenario_{scenario_id:02d}',
                'event': row['Event'].strip(),
                'date': row['Date'].strip(),
                'team_name': team.strip(),
                'outcome': choose.lower(),
                'description': description.strip(),
            })
    return scenarios


def main():
    text_dir = OUTPUT_DIR / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    # ── Parse papers ──────────────────────────────────────────
    print("=== Parsing papers ===")
    pdf_files = sorted(PAPERS_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs")

    for i, pdf_path in enumerate(pdf_files, 1):
        paper_id = f"paper_{i:02d}"
        print(f"  [{paper_id}] {pdf_path.name}")

        text = extract_pdf_text(pdf_path)
        text = clean_text(text)

        if STRIP_REFERENCES:
            text = strip_references_section(text)

        if len(text) > MAX_PAPER_CHARS:
            print(f"    WARNING: Truncating from {len(text)} to {MAX_PAPER_CHARS} chars")
            text = text[:MAX_PAPER_CHARS]

        out_path = text_dir / f"{paper_id}.txt"
        out_path.write_text(text, encoding='utf-8')
        print(f"    -> {out_path.name} ({len(text)} chars)")

    # ── Parse scenarios ───────────────────────────────────────
    print("\n=== Parsing scenarios ===")
    scenarios = parse_scenarios(SCENARIOS_CSV)
    print(f"Found {len(scenarios)} scenarios")

    for s in scenarios:
        print(f"  [{s['id']}] {s['event']} ({s['outcome']} case)")

        # Create a structured text block for the LLM
        text = (
            f"HI Competition Scenario\n"
            f"Event: {s['event']}\n"
            f"Date: {s['date']}\n"
            f"Team: {s['team_name']}\n"
            f"Outcome: {s['outcome']} case\n\n"
            f"Scenario Description:\n{s['description']}"
        )

        out_path = text_dir / f"{s['id']}.txt"
        out_path.write_text(text, encoding='utf-8')
        print(f"    -> {out_path.name} ({len(text)} chars)")

    print(f"\nDone. Text files written to {text_dir}/")


if __name__ == "__main__":
    main()

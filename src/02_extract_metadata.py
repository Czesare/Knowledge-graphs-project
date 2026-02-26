"""
Step 2: Extract structured HI metadata from papers using OpenAI API.

Usage:
    python 02_extract_metadata.py                    # process all
    python 02_extract_metadata.py paper_01            # process one
    python 02_extract_metadata.py --skip-existing     # skip already extracted

Reads text files from output/text/, sends to OpenAI with the extraction
prompt, and writes structured JSON to output/json/.
"""
import json
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Install openai: pip install openai")
    raise

from config import (
    OUTPUT_DIR, PROMPTS_DIR,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE,
    JSON_DIR
)


def load_prompt_template() -> str:
    """Load the extraction prompt template."""
    prompt_path = PROMPTS_DIR / "extraction_prompt.txt"
    return prompt_path.read_text(encoding='utf-8')


def extract_metadata(client: OpenAI, paper_text: str, prompt_template: str) -> dict:
    """
    Send paper text to OpenAI and get structured JSON back.
    Retries once on JSON parse failure.
    """
    prompt = prompt_template.replace("{paper_text}", paper_text)

    for attempt in range(2):
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise ontology engineer. You output only valid JSON, no markdown, no explanation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]  # remove first line
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        try:
            data = json.loads(raw)
            return data
        except json.JSONDecodeError as e:
            print(f"    JSON parse error (attempt {attempt+1}): {e}")
            if attempt == 0:
                print("    Retrying...")
                time.sleep(2)
            else:
                # Save raw output for debugging
                return {"_error": str(e), "_raw": raw}

    return {"_error": "Failed after retries"}


def validate_extraction(data: dict, source_id: str) -> list[str]:
    """
    Basic validation of the extracted JSON.
    Returns a list of warnings (empty = all good).
    """
    warnings = []

    if "_error" in data:
        warnings.append(f"EXTRACTION FAILED: {data['_error']}")
        return warnings

    uc = data.get("use_case", {})

    # Check team composition
    team = uc.get("team", {})
    if not team.get("human_agents"):
        warnings.append("NO HUMAN AGENTS - ontology requires at least 1")
    if not team.get("artificial_agents"):
        warnings.append("NO ARTIFICIAL AGENTS - ontology requires at least 1")

    # Check goals have tasks
    for goal in uc.get("goals", []):
        if not goal.get("tasks"):
            warnings.append(f"Goal '{goal.get('label')}' has no tasks")
        for task in goal.get("tasks", []):
            if not task.get("required_capabilities"):
                warnings.append(f"Task '{task.get('label')}' has no required capabilities")

    # Check agents have capabilities
    for agent_type in ["human_agents", "artificial_agents"]:
        for agent in team.get(agent_type, []):
            if not agent.get("capabilities"):
                warnings.append(f"Agent '{agent.get('label')}' has no capabilities")

    # Check domain
    if not uc.get("domain_concepts"):
        warnings.append("No domain concepts specified")

    return warnings


def main():
    text_dir = OUTPUT_DIR / "text"
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    # Parse arguments
    target = None
    skip_existing = False
    for arg in sys.argv[1:]:
        if arg == "--skip-existing":
            skip_existing = True
        else:
            target = arg

    # Check API key
    if OPENAI_API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Set your OpenAI API key in src/config.py")
        sys.exit(1)

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt_template = load_prompt_template()

    # Find text files to process
    text_files = sorted(text_dir.glob("*.txt"))
    if target:
        text_files = [f for f in text_files if target in f.stem]

    if not text_files:
        print(f"No text files found in {text_dir}/")
        print("Run 01_parse_sources.py first.")
        sys.exit(1)

    print(f"=== Extracting metadata ({len(text_files)} sources) ===")
    print(f"Model: {OPENAI_MODEL}")
    print()

    results_summary = []

    for text_file in text_files:
        source_id = text_file.stem
        json_path = JSON_DIR / f"{source_id}.json"

        if skip_existing and json_path.exists():
            print(f"  [{source_id}] SKIPPED (already exists)")
            continue

        print(f"  [{source_id}] Processing...")

        paper_text = text_file.read_text(encoding='utf-8')

        # For scenarios, adjust the prompt context
        if source_id.startswith("scenario"):
            # Modify the use_case type hint
            paper_text = "[NOTE: This is an HI Competition scenario, not a research paper. Set type to 'competition'. Authors field should be empty.]\n\n" + paper_text

        try:
            data = extract_metadata(client, paper_text, prompt_template)
        except Exception as e:
            print(f"    API ERROR: {e}")
            data = {"_error": str(e)}

        # Validate
        warnings = validate_extraction(data, source_id)
        if warnings:
            for w in warnings:
                print(f"    WARNING: {w}")
        else:
            print(f"    OK - extracted successfully")

        # Save JSON
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"    -> {json_path.name}")

        results_summary.append({
            'source': source_id,
            'status': 'error' if '_error' in data else ('warnings' if warnings else 'ok'),
            'warnings': len(warnings),
        })

        # Rate limiting: small delay between API calls
        time.sleep(1)

    # Print summary
    print("\n=== Summary ===")
    for r in results_summary:
        status_icon = {"ok": "OK", "warnings": "WARN", "error": "FAIL"}[r['status']]
        print(f"  [{r['source']}] {status_icon}" +
              (f" ({r['warnings']} warnings)" if r['warnings'] else ""))

    ok_count = sum(1 for r in results_summary if r['status'] == 'ok')
    print(f"\n{ok_count}/{len(results_summary)} extracted cleanly")
    print(f"JSON files in {JSON_DIR}/")


if __name__ == "__main__":
    main()

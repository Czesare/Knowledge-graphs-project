"""
Pipeline configuration.
Edit the paths and API settings here before running.
"""
from pathlib import Path

# ── Directory layout ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = PROJECT_ROOT / "papers"
SCENARIOS_DIR = PROJECT_ROOT / "scenarios"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output"
JSON_DIR = OUTPUT_DIR / "json"
INSTANCES_DIR = OUTPUT_DIR / "instances"

# ── Source files ──────────────────────────────────────────────
ONTOLOGY_FILE = DATA_DIR / "hi-ontology.ttl"
THESAURUS_FILE = DATA_DIR / "hi-thesaurus.ttl"
EXTENSIONS_FILE = DATA_DIR / "hi-ontology-extensions.ttl"
SCENARIOS_CSV = SCENARIOS_DIR / "scenarios.csv"
PROMPT_TEMPLATE = PROMPTS_DIR / "extraction_prompt.txt"

# ── Output files ──────────────────────────────────────────────
THESAURUS_EXT_FILE = OUTPUT_DIR / "hi-thesaurus-extensions.ttl"
MERGED_KG_FILE = OUTPUT_DIR / "merged_kg.ttl"
EXTERNAL_LINKS_FILE = OUTPUT_DIR / "external_links.ttl"

# ── OpenAI API settings ──────────────────────────────────────
OPENAI_API_KEY = ""  # <-- PUT YOUR KEY HERE
OPENAI_MODEL = "gpt-4o"               # good balance of quality/cost
OPENAI_MAX_TOKENS = 4096
OPENAI_TEMPERATURE = 0.1              # low temp for consistent structured output

# ── Namespaces ────────────────────────────────────────────────
HI_NS = "https://w3id.org/hi-ontology#"
HINT_NS = "https://w3id.org/hi-thesaurus/"
INST_NS = "https://w3id.org/hi-ontology/instances/"  # our instance namespace

# ── Processing settings ───────────────────────────────────────
MAX_PAPER_CHARS = 60000    # truncate papers beyond this (saves tokens)
STRIP_REFERENCES = True     # remove references section before sending to LLM

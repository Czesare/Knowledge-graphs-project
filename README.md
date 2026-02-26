# HI Ontology Expansion Pipeline

Pipeline to populate the Hybrid Intelligence Ontology (V2) from HHAI 2025
papers and HI Competition scenarios using LLM-assisted extraction.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key in src/config.py
#    Edit OPENAI_API_KEY = "sk-..."

# 3. Place your files:
#    data/hi-ontology.ttl          <- HI Ontology V2
#    data/hi-thesaurus.ttl         <- HINT Thesaurus
#    data/hi-ontology-extensions.ttl  <- TBox extensions (from this project)
#    papers/*.pdf                  <- 9 HHAI papers
#    scenarios/scenarios.csv       <- 3 HI Competition scenarios
```

## Running the Pipeline

Run each step in order from the `src/` directory:

```bash
cd src/

# Step 1: Extract text from PDFs and scenarios
python 01_parse_sources.py

# Step 2: Send to LLM for structured extraction
python 02_extract_metadata.py              # all at once
python 02_extract_metadata.py paper_01     # one at a time
python 02_extract_metadata.py --skip-existing  # skip already done

# Step 3: Convert JSON to RDF (no LLM, deterministic)
python 03_generate_instances.py

# Step 4: Add external links (needs internet for Wikidata)
python 04_add_external_links.py

# Step 5: Merge everything and validate
python 05_merge_and_validate.py
```

## Output Structure

```
output/
  text/                    <- Extracted paper text (for inspection)
  json/                    <- Structured JSON per paper (LLM output)
  instances/               <- RDF Turtle per paper
  hi-thesaurus-extensions.ttl  <- New HINT concepts the LLM proposed
  external_links.ttl       <- Wikidata/DBpedia links
  merged_kg.ttl            <- Final merged knowledge graph
```

## Debugging Workflow

1. Check `output/json/paper_XX.json` - is the LLM extraction sensible?
2. Check `output/instances/paper_XX.ttl` - does the RDF look correct?
3. Re-run step 2 for a single paper: `python 02_extract_metadata.py paper_03`
4. Re-run step 3 to regenerate RDF: `python 03_generate_instances.py`
5. Check `output/hi-thesaurus-extensions.ttl` - review new concepts before using

## Architecture

```
Paper (PDF) --> [01_parse] --> Text --> [02_extract (LLM)] --> JSON
                                                                |
                                                    [03_generate (Python)]
                                                                |
HINT Thesaurus  ----+                                    Instance .ttl
HI Ontology V2  ----+-- [05_merge] --> merged_kg.ttl
TBox Extensions ----+                        |
External Links  ----+               [Load into GraphDB]
```

Key design: The LLM outputs structured JSON, not RDF. Python handles
all RDF serialization deterministically. This makes debugging easy
and avoids LLM syntax errors in Turtle output.

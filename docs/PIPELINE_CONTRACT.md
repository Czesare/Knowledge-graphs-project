## Purpose

This file defines the intended role of each numbered script and the canonical artifact flow of the repository.

## Canonical pipeline

`01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 10 -> 07 -> 08 -> 09`

Interpretation:
- `01-05` build the graph
- `06,10` validate or strengthen confidence in the graph
- `07-09` consume or analyze the graph

## Canonical artifact

The canonical merged graph is:

`output/merged_kg.ttl`

This is the main graph artifact that the project should trust and present.

Derived serializations may exist, but they are secondary.

Legacy merged graphs must not be silently used as fallback.

---

## Script contract

### 01_parse_sources.py
**Status:** Core  
**Purpose:** Parse source material into normalized text  
**Inputs:** source PDFs, scenarios CSV, configuration  
**Outputs:** cleaned text files in `output/text/`  
**Notes:** This is the first transformation stage

### 02_extract_metadata.py
**Status:** Core  
**Purpose:** Extract structured metadata from normalized text using an LLM  
**Inputs:** `output/text/`, prompt, configuration  
**Outputs:** JSON files in `output/json/`  
**Notes:** Extraction should not be confused with deterministic KG generation

### 03_generate_instances.py
**Status:** Core  
**Purpose:** Convert extracted JSON into RDF/Turtle instances  
**Inputs:** `output/json/`, ontology/thesaurus resources  
**Outputs:** per-source RDF instance files in `output/instances/`, possibly thesaurus extensions  
**Notes:** This is the key deterministic KG construction stage

### 04_add_external_links.py
**Status:** Core  
**Purpose:** Add external links to concepts/entities  
**Inputs:** generated graph artifacts, mapping resources  
**Outputs:** external links RDF artifact(s)  
**Notes:** Linking contributes directly to grading

### 05_merge_and_validate.py
**Status:** Core  
**Purpose:** Merge schema, instances, links, and extensions into a single KG  
**Inputs:** outputs of prior build stages  
**Outputs:** `output/merged_kg.ttl` and optionally derived serializations  
**Notes:** This stage defines the canonical merged graph

### 06_reasoning.py
**Status:** Quality/support  
**Purpose:** Perform reasoning or inferred-graph checks  
**Inputs:** canonical merged graph or derived serialization  
**Outputs:** inferred or reasoned artifacts  
**Notes:** Useful for ontology quality, but not the primary graph-construction stage

### 10_shacl_validation.py
**Status:** Quality/support  
**Purpose:** Validate graph structure and constraints  
**Inputs:** canonical merged graph  
**Outputs:** SHACL validation outputs  
**Notes:** Supports trust and reproducibility

### 07_sparql_queries.py
**Status:** Consumption/analysis  
**Purpose:** Query and summarize the KG  
**Inputs:** canonical merged graph  
**Outputs:** query results / reports / figures  
**Notes:** Important for the insights section of the report

### 08_kg_metrics.py
**Status:** Consumption/analysis  
**Purpose:** Compute graph-level metrics and summaries  
**Inputs:** canonical merged graph  
**Outputs:** metrics reports / visualizations  
**Notes:** Supports the insights section

### 09_kg_embeddings.py
**Status:** Consumption/analysis / experimental extension  
**Purpose:** Run embedding-based analyses, ablations, or link prediction-style experiments  
**Inputs:** canonical merged graph and optional auxiliary resources  
**Outputs:** embeddings artifacts, evaluation outputs, ablation outputs  
**Notes:** Valuable but not the defining artifact of the project

---

## Canonical rules

1. `output/merged_kg.ttl` is the only canonical merged graph.
2. Legacy merged graphs must not remain as silent fallbacks.
3. If a downstream stage depends on a non-canonical artifact, that dependency must be explicit and documented.
4. Optional analysis outputs are not part of the canonical build state.
5. Changes to numbered scripts must preserve this contract unless the contract is intentionally revised.

## Current maintenance priority

When in doubt, prioritize:

1. correctness of `01-05`
2. clarity of `06` and `10`
3. stability of `07-09`
4. cleanup of legacy outputs only after active dependencies are removed

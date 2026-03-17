# Hybrid Intelligence Knowledge Graph Pipeline

## 1. Project Overview

This repository contains an academic-engineering pipeline for populating a
Hybrid Intelligence (HI) knowledge graph from research papers and competition
scenarios. The project is centered on the Hybrid Intelligence Ontology (V2)
and the HINT thesaurus, and combines large language model extraction with
deterministic RDF generation in Python.

The central design choice is deliberate:

- the LLM is used for structured semantic extraction into JSON
- Python then converts that JSON into RDF/Turtle deterministically

This hybrid design makes the workflow easier to inspect, debug, and validate
than direct LLM-to-RDF generation. It also keeps ontology serialization logic
in code rather than in prompt behavior.

In its current repository state, the project includes:

- 10 paper PDFs in `papers/`
- 3 HI competition scenarios in `scenarios/scenarios.csv`
- generated outputs for all 13 sources in `output/`
- a merged graph in `output/merged_kg.ttl`
- SHACL validation artifacts in `output/shacl/`

## 2. Motivation and Problem Setting

Populating domain ontologies from unstructured documents is time-consuming and
error-prone when done manually. Research papers and scenario descriptions often
contain rich information about agents, tasks, goals, capabilities, contexts,
interactions, and evaluation procedures, but that knowledge is embedded in free
text rather than available in machine-readable form.

This repository addresses that problem by providing a reproducible pipeline
that:

- extracts text from heterogeneous inputs
- maps content to a shared ontology and thesaurus
- generates inspectable RDF artifacts
- supports validation, querying, graph analysis, and embedding-based
  exploration

The project is intended both as a knowledge engineering exercise and as a
practical prototype for semi-automated ontology population in an academic
setting.

## 3. Data Sources

The repository combines curated schema resources with document-level source
material.

### Core schema resources

- `data/hi-ontology.ttl`: Hybrid Intelligence Ontology V2
- `data/hi-thesaurus.ttl`: HINT thesaurus
- `data/hi-ontology-extensions.ttl`: ontology extensions used by this project

### Source documents

- `papers/*.pdf`: 10 paper PDFs currently present in the repository
- `scenarios/scenarios.csv`: 3 HI competition scenarios

### Prompt resource

- `prompts/extraction_prompt.txt`: prompt template used during LLM extraction

## 4. End-to-End Pipeline

The repository has one canonical build pipeline and several downstream analysis
scripts.

### Canonical build pipeline

`01 -> 02 -> 03 -> 04 -> 05`

`parse -> LLM -> inst -> link -> merge`

This sequence is the only true end-to-end graph construction workflow in the
codebase. It produces the canonical merged graph:

- `output/merged_kg.ttl`

### Downstream analysis order used in this README

`06 -> 10 -> 07 -> 08 -> 09`

`reason -> SHACL validation -> SPARQL -> metrics -> embeddings (+ ablation)`

These downstream scripts are useful, but they are not a strict chained
dependency sequence. They operate as optional consumers of
`output/merged_kg.ttl`.

### Core ingestion and graph construction

These stages build the knowledge graph from source material and form the main
pipeline.

1. `01_parse_sources.py`
   Extracts clean text from PDFs and converts scenario CSV rows into normalized
   text files for downstream processing.

2. `02_extract_metadata.py`
   Sends text to the OpenAI API and produces structured JSON describing papers,
   use cases, agents, goals, tasks, interactions, evaluations, and proposed new
   concepts.

3. `03_generate_instances.py`
   Converts the extracted JSON into RDF/Turtle instance graphs. This stage is
   deterministic and does not call the LLM.

4. `04_add_external_links.py`
   Adds links to external resources such as Wikidata and DBpedia, combining
   static concept mappings with query-based matching for authors and
   affiliations.

5. `05_merge_and_validate.py`
   Merges ontology files, thesaurus files, instance graphs, thesaurus
   extensions, and external links into a single merged knowledge graph and runs
   basic structural validation checks.

### Optional downstream analysis and validation

These stages operate on the merged graph and are best understood as downstream
analysis rather than core ingestion.

6. `06_reasoning.py`
   Converts the merged graph to N-Triples and runs OWL reasoning with
   Pellet via Owlready2.

10. `10_shacl_validation.py`
   Generates SHACL shapes and validates the merged graph against structural
   constraints such as team composition, task-capability links, and execution
   cardinality.

7. `07_sparql_queries.py`
   Runs competency-question-oriented SPARQL queries and exports query results
   and visualizations.

8. `08_kg_metrics.py`
   Computes ontology-level and graph-level metrics and produces graph analysis
   visualizations using NetworkX and Matplotlib.

9. `09_kg_embeddings.py`
   Trains knowledge graph embedding models, performs link prediction, visualizes
   embeddings, and optionally compares training on the project graph versus a
   combined graph containing an additional populated ontology file.

### Processing logic at a glance

```text
papers/*.pdf + scenarios/scenarios.csv
    -> 01_parse_sources.py
    -> output/text/*.txt
    -> 02_extract_metadata.py
    -> output/json/*.json
    -> 03_generate_instances.py
    -> output/instances/*.ttl + output/hi-thesaurus-extensions.ttl
    -> 04_add_external_links.py
    -> output/external_links.ttl
    -> 05_merge_and_validate.py
    -> output/merged_kg.ttl
    -> 06 / 10 / 07 / 08 / 09 (optional downstream stages)
```

Legacy note: the older file `merged_kg_a2.ttl` is not part of the active
workflow and has been archived for reference.

## 5. Repository Structure

```text
.
├── data/                   # Ontology, thesaurus, and ontology extension files
├── output/                 # Generated artifacts from ingestion and analysis
│   ├── text/               # Extracted source text
│   ├── json/               # LLM-generated structured extractions
│   ├── instances/          # RDF instance graphs per source
│   ├── queries/            # SPARQL query outputs and charts
│   ├── metrics/            # Graph metrics and visualizations
│   ├── embeddings/         # Embedding outputs, checkpoints, and ablation artifacts
│   └── shacl/              # SHACL shapes and validation reports
├── papers/                 # Source PDFs
├── prompts/                # Prompt templates for extraction
├── scenarios/              # Scenario CSV input
├── src/                    # Pipeline and analysis scripts
├── requirements.txt        # Minimal core dependencies
└── README.md
```

## 6. Setup and Dependencies

### Core dependencies

The checked-in `requirements.txt` covers the minimal dependencies needed for
the core ingestion stages:

```bash
pip install -r requirements.txt
```

Current core requirements:

- `rdflib`
- `openai`
- `pdfplumber`
- `requests`

### Configuration

Before running LLM extraction, configure the API key in:

- `src/config.py`

The same configuration file also controls:

- model selection
- output paths
- maximum paper length for extraction
- whether reference sections are stripped before sending text to the LLM

### Optional dependencies

Several downstream scripts require additional packages that are not currently
listed in `requirements.txt`. In particular:

- `06_reasoning.py`: `owlready2` and a working Pellet setup
- `07_sparql_queries.py`: `matplotlib`
- `08_kg_metrics.py`: `networkx`, `matplotlib`, `numpy`
- `09_kg_embeddings.py`: `pykeen`, `torch`, `pandas`, `scikit-learn`,
  `matplotlib`, `numpy`, `scipy`
- `10_shacl_validation.py`: `pyshacl`

This is an important reproducibility consideration: the repository currently
documents the core stack well, but the full analysis environment is broader
than the base requirements file.

## 7. How to Run the Pipeline

Run commands from the `src/` directory.

### Core ingestion pipeline

```bash
cd src/

# 01. Parse source documents into normalized text
python 01_parse_sources.py

# 02. LLM-based structured extraction
python 02_extract_metadata.py
python 02_extract_metadata.py paper_01
python 02_extract_metadata.py --skip-existing

# 03. Deterministic RDF instance generation
python 03_generate_instances.py

# 04. External linking (requires internet access for Wikidata queries)
python 04_add_external_links.py

# 05. Merge and basic validation
python 05_merge_and_validate.py
```

### Optional downstream stages

```bash
# 06. OWL reasoning
python 06_reasoning.py

# 10. SHACL validation
python 10_shacl_validation.py

# 07. SPARQL competency queries
python 07_sparql_queries.py

# 08. Graph metrics and visualizations
python 08_kg_metrics.py

# 09. KG embeddings and optional ablation
python 09_kg_embeddings.py
```

### Recommended inspection workflow

If you are iterating on the extraction quality, the most useful checkpoints are:

1. `output/text/*.txt`
2. `output/json/*.json`
3. `output/instances/*.ttl`
4. `output/hi-thesaurus-extensions.ttl`
5. `output/merged_kg.ttl`

## 8. Outputs / Artifacts

The repository currently contains generated artifacts for the available 10
papers and 3 scenarios.

### Core outputs

- `output/text/`: extracted and normalized source text
- `output/json/`: LLM-produced structured JSON files
- `output/instances/`: deterministic RDF/Turtle instance files
- `output/hi-thesaurus-extensions.ttl`: new HINT concepts proposed by the LLM
- `output/external_links.ttl`: external entity and concept links
- `output/merged_kg.ttl`: canonical merged knowledge graph
- `output/merged_kg.nt`: N-Triples serialization for reasoning tools

### Validation and analysis outputs

- `output/shacl/`: SHACL shapes, validation report, validation summary
- `output/queries/`: SPARQL query results and associated charts
- `output/metrics/`: ontology-level and graph-level metrics, visualizations
- `output/embeddings/`: model comparison tables, loss curves, predicted links,
  embedding plots, checkpoints, and ablation artifacts

### Current repository state

At the time of this README update, the checked-in outputs include:

- 13 text files in `output/text/`
- 13 JSON files in `output/json/`
- 13 instance graphs in `output/instances/`
- a merged graph in `output/merged_kg.ttl`
- SHACL validation artifacts reporting conformance

The checked-in metrics report for `output/merged_kg.ttl` records:

- 3,886 triples
- 626 individuals
- 13 use cases in total

These numbers describe the current repository snapshot; they should not be read
as benchmark claims.

## 9. Validation and Quality Control

The project includes multiple validation layers, with different strengths.

### Deterministic RDF generation

The most important quality-control decision in the repository is the separation
between extraction and serialization:

- the LLM generates structured JSON
- Python code generates RDF deterministically

This avoids direct LLM generation of Turtle and makes intermediate artifacts
inspectable.

### Merge-time structural checks

`05_merge_and_validate.py` performs basic structural checks, including:

- hybrid teams containing both human and artificial agents
- goals linked to tasks
- tasks linked to capabilities
- executions linked to realized tasks
- keyword values being modeled as IRIs rather than plain literals

### SHACL validation

`10_shacl_validation.py` provides explicit SHACL-based validation of the merged
graph. The checked-in validation summary currently reports conformance for the
generated merged graph in `output/merged_kg.ttl`.

### Manual review points

In practice, the most important manual review points remain:

- extracted JSON quality in `output/json/`
- proposed thesaurus extensions in `output/hi-thesaurus-extensions.ttl`
- external links in `output/external_links.ttl`

## 10. Known Limitations and Risks

This repository is designed to be inspectable and useful, but it is not free of
semantic or reproducibility risk.

### LLM extraction risk

The extraction prompt enforces structural completeness, which is helpful for
ontology population but can encourage the model to infer plausible missing
structure rather than extract only explicitly stated facts. This means that the
resulting graph should be treated as a curated machine-assisted representation,
not as a ground-truth transcription of the source text.

### Fuzzy repair logic in RDF generation

The RDF generation stage includes fallback and fuzzy matching behavior to repair
missing task-capability and task-execution links. This improves structural
validity but can reduce semantic reliability when labels do not align cleanly.

### External linking uncertainty

External links are a mix of static mappings and query-based matches. Query-based
entity linking, especially for authors and affiliations, is inherently fallible
and should be reviewed before being used as authoritative alignment.

### Identifier stability

Paper identifiers are assigned from sorted filenames during parsing. This makes
the pipeline easy to run, but it also means that renaming or adding source
files can shift identifiers and make cached outputs harder to compare across
runs.

### Reproducibility constraints

The full workflow depends on:

- an API-based extraction step
- optional internet access for external linking
- optional dependencies not fully captured in `requirements.txt`

For those reasons, the repository is best understood as a reproducible
engineering workflow with partial environment gaps, rather than as a completely
self-contained one-command experiment.

## 11. Future Improvements

The most valuable next steps for the repository would be:

- improving configuration and secret handling so API credentials are not managed
  through tracked source files
- making source identifiers and rerun behavior more stable across incremental
  updates
- adding provenance and confidence metadata so extracted, inferred, and linked
  facts are easier to distinguish
- strengthening test coverage for the core stages, especially deterministic RDF
  generation and validation
- improving external linking confidence and review workflows
- packaging optional dependencies more completely for full-environment
  reproducibility
- reducing reliance on naming conventions in downstream SPARQL and analytics

## License and Academic Context

This repository is structured as an academic knowledge-engineering project with
engineering-oriented implementation artifacts. It is suitable for demonstrating
skills in:

- ontology population workflows
- RDF and Turtle generation
- LLM-assisted information extraction
- graph validation and analysis
- knowledge graph experimentation

At the same time, it should be evaluated with the usual academic caution:
automated semantic extraction is useful, but careful manual review remains
important for high-confidence ontology population.

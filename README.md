# Hybrid Intelligence Knowledge Graph Pipeline

A knowledge engineering pipeline for building a **Hybrid Intelligence (HI) knowledge graph** from **research papers** and **competition scenarios**, using:

- **LLM-based structured extraction** into JSON
- **deterministic Python-based RDF generation**
- **external linking, validation, querying, metrics, and embeddings**

The project is built on top of the **Hybrid Intelligence Ontology** and the **HINT thesaurus** and was developed as an academic-engineering project for **Knowledge Graphs & Semantic Technologies**.

---

## Final Snapshot

Current checked-in repository state:

- **11 HHAI papers**
- **3 HI competition scenarios**
- **14 source artifacts**
- **3839 triples** in the final merged graph
- **641 individuals**
- **229 external links** (including DOI-based `owl:sameAs` for all 11 papers)
- **SHACL conformance: 0 violations**
- **5 competency-question SPARQL query outputs** (each with CSV and PNG chart)
- **provenance / repair audit outputs** in `output/audit/`

Canonical merged graph:

- `output/merged_kg.ttl`

---

## Why This Project Matters

Populating an ontology from research papers and scenario descriptions is slow and error-prone when done manually. Important knowledge about:

- agents
- goals
- tasks
- capabilities
- contexts
- interactions
- evaluations
- experiments

is usually embedded in natural language rather than available in machine-readable form.

This repository addresses that problem through a **hybrid workflow**:

1. an LLM extracts structured semantic content from text
2. Python turns that structured output into RDF/Turtle **deterministically**

This design keeps the pipeline:

- inspectable
- debuggable
- reproducible downstream
- more academically defensible than direct LLM-to-RDF generation

---

## Main Results

The current project pipeline produces a knowledge graph that:

- integrates **11 research papers** and **3 competition scenarios**
- links to external resources through **229 external links** (including DOI-based `owl:sameAs` for all 11 papers)
- passes **SHACL validation with zero violations**
- supports **five non-trivial competency-question queries** (each with CSV and PNG chart)
- includes **metrics, community analysis, embeddings, and ablation results**
- explicitly reports **repaired** and **unresolved** ABox links instead of hiding them
- models `hi:hasSubTask` decompositions in three papers (paper_01, paper_07, paper_11)
- resolves all previously unresolved `requiresCapability` links in paper_09

This makes the repository suitable both as:

- an academic submission
- a portfolio-ready knowledge graph engineering project

---

## Data Sources

### Core schema resources

- `data/hi-ontology.ttl` — Hybrid Intelligence Ontology
- `data/hi-thesaurus.ttl` — HINT thesaurus
- `data/hi-ontology-extensions.ttl` — project-specific ontology extensions

### Source materials

- `papers/*.pdf` — **11 HHAI paper PDFs**
- `scenarios/scenarios.csv` — **3 HI competition scenarios**

### Prompt resource

- `prompts/extraction_prompt.txt` — prompt template used during structured extraction

---

## Canonical Pipeline

### Core build pipeline

`01 -> 02 -> 03 -> 04 -> 05`

`parse -> LLM extraction -> RDF instances -> external linking -> merge`

This is the canonical graph-construction workflow and produces:

- `output/merged_kg.ttl`

### Downstream analysis / validation

`06 -> 10 -> 07 -> 08 -> 09`

`reasoning -> SHACL -> SPARQL -> metrics -> embeddings`

These stages are **downstream consumers** of the merged graph, not the core build path.

---

## Pipeline Stages

### 01. `01_parse_sources.py`
Parses PDFs and scenario rows into normalized text files.

Output:
- `output/text/*.txt`

### 02. `02_extract_metadata.py`
Uses the OpenAI API to extract structured JSON from normalized text.

Output:
- `output/json/*.json`

### 03. `03_generate_instances.py`
Deterministically converts JSON into RDF/Turtle instance graphs.

Outputs:
- `output/instances/*.ttl`
- `output/hi-thesaurus-extensions.ttl`
- `output/audit/instance_generation/`
- `output/audit/instance_generation_summary.json`
- `output/audit/instance_generation_summary.csv`

### 04. `04_add_external_links.py`
Adds external links to concepts and instances using static mappings and query-based entity linking.

Output:
- `output/external_links.ttl`

### 05. `05_merge_and_validate.py`
Merges schema, thesaurus, extensions, instances, and links into a canonical KG and performs structural validation checks.
It also loads protected manual patch files from `output/manual_patches/` after the generated instances and links.

Outputs:
- `output/merged_kg.ttl`
- `output/merged_kg.nt`
- `output/audit/merge_validation_summary.json`

### 06. `06_reasoning.py`
Runs OWL reasoning with Pellet through Owlready2.

### 10. `10_shacl_validation.py`
Builds SHACL shapes and validates the merged KG.

Outputs:
- `output/shacl/hi_shapes.ttl`
- `output/shacl/validation_report.ttl`
- `output/shacl/validation_summary.txt`

### 07. `07_sparql_queries.py`
Runs five competency-question-oriented SPARQL queries and exports result tables/charts.

Output:
- `output/queries/`

### 08. `08_kg_metrics.py`
Computes ontology-level and graph-level metrics and produces visualizations.

Output:
- `output/metrics/`

### 09. `09_kg_embeddings.py`
Trains KG embedding models, performs link prediction, visualizes embeddings, and runs an ablation experiment using a combined KG.

Output:
- `output/embeddings/`

---

## Repository Structure

```text
.
├── data/                       # Ontology, thesaurus, populated KG, extensions
├── docs/                       # Project contract / course guidance files
├── output/
│   ├── text/                   # Parsed source text
│   ├── json/                   # LLM-generated structured metadata
│   ├── manual_patches/         # Protected manual RDF patches loaded after generated files
│   ├── instances/              # Per-source RDF instance graphs
│   ├── audit/                  # Repair/provenance summaries
│   ├── queries/                # SPARQL outputs
│   ├── metrics/                # Graph metrics and visualisations
│   ├── embeddings/             # KGE outputs and ablation artifacts
│   ├── shacl/                  # SHACL shapes and validation reports
│   ├── external_links.ttl      # External links
│   ├── merged_kg.ttl           # Canonical merged graph
│   └── merged_kg.nt            # N-Triples export for reasoning tools
├── papers/                     # Source paper PDFs
├── prompts/                    # Extraction prompt
├── scenarios/                  # Scenario CSV input
├── src/                        # Numbered pipeline scripts
├── tests/                      # Lightweight canonical-path checks
├── AGENTS.md                   # Repo rules for coding agents
├── requirements.txt
└── README.md
```

---

## Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Current `requirements.txt` covers the main Python dependencies used by the numbered scripts, including:

* `rdflib`
* `openai`
* `pdfplumber`
* `requests`
* `matplotlib`
* `networkx`
* `numpy`
* `owlready2`
* `pandas`
* `pykeen`
* `pyshacl`
* `scikit-learn`
* `scipy`
* `torch`

### OpenAI API key

Stage `02_extract_metadata.py` requires an OpenAI API key.

Set it in the environment before running extraction.

PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key-here"
```

### Additional runtime requirements

Some optional downstream stages require non-Python runtime support:

* `06_reasoning.py` requires **Java** for Pellet / Owlready2 reasoning
* `04_add_external_links.py` requires internet access for Wikidata lookups

---

## How to Run

Run commands from the `src/` directory.

### Core build pipeline

```bash
cd src/

# 01. Parse PDFs and scenarios into normalized text
python 01_parse_sources.py

# 02. Extract structured metadata with the OpenAI API
python 02_extract_metadata.py

# 03. Generate deterministic RDF instance graphs
python 03_generate_instances.py

# 04. Add external links
python 04_add_external_links.py

# 05. Merge and validate
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

# 08. KG metrics
python 08_kg_metrics.py

# 09. Embeddings + ablation
python 09_kg_embeddings.py
```

---

## Reproducibility Modes

This repository supports two practical reproducibility modes.

### 1. Full rebuild

Rebuild the entire pipeline from raw papers and scenarios.

Requires:

* OpenAI API access for stage 02
* internet access for stage 04
* Java for stage 06

### 2. Downstream reproducibility from checked outputs

Reuse the checked intermediate outputs and rerun deterministic stages and analyses.

This allows reproducibility of:

* RDF generation
* merging
* validation
* SPARQL querying
* metrics
* embeddings

without repeating the LLM extraction step.

This distinction is important: the project is **not fully self-contained from zero without API access**, but it is **substantially reproducible downstream from checked artifacts**.

### Note on direct TTL edits

Several post-pipeline improvements were applied as direct edits to checked-in artifacts rather than as pipeline changes:

* **DOI external links** — added to `output/external_links.ttl` directly and to `src/expanded_concept_mappings.py` so they are picked up by stage 05 and persist through future stage 04 reruns.
* **`hi:hasSubTask` decompositions** — originally added directly to `output/instances/paper_01.ttl`, `paper_07.ttl`, and `paper_11.ttl`, but now migrated to `output/manual_patches/instances/` as protected patch files loaded during stage 05. The corresponding `output/json/` files were not updated, so a full stage 03 rebuild alone would not recreate these decompositions.
* **paper_09 capability alignment** — corrected in both `output/json/paper_09.json` and `output/instances/paper_09.ttl`, so a stage 03 re-run from the corrected JSON would reproduce the fix.

---

## Outputs

### Core outputs

* `output/text/` — normalized text extracted from papers and scenarios
* `output/json/` — structured LLM extraction outputs
* `output/instances/` — deterministic RDF instance graphs
* `output/hi-thesaurus-extensions.ttl` — proposed HINT concept extensions
* `output/external_links.ttl` — external links
* `output/merged_kg.ttl` — canonical merged KG
* `output/merged_kg.nt` — N-Triples export

### Audit outputs

* `output/audit/instance_generation/` — per-source repair / unresolved audit files
* `output/audit/instance_generation_summary.json`
* `output/audit/instance_generation_summary.csv`
* `output/audit/merge_validation_summary.json`

### Validation / analysis outputs

* `output/shacl/` — SHACL shapes and reports
* `output/queries/` — SPARQL outputs
* `output/metrics/` — graph metrics and visualizations
* `output/embeddings/` — model comparison, link prediction, embeddings, ablation outputs

---

## Current Repository State

The current checked-in snapshot includes:

* **14** normalized text files in `output/text/`
* **14** JSON extraction files in `output/json/`
* **14** instance graphs in `output/instances/`
* **1** canonical merged graph in `output/merged_kg.ttl`

Key current graph statistics:

* **3839 triples**
* **641 individuals**
* **11 papers**
* **3 competition scenarios**
* **229 external links**

These values describe the current repository snapshot and should not be interpreted as benchmark claims.

---

## Validation and Quality Control

The project uses multiple quality-control layers.

### Deterministic RDF generation

The most important quality-control design choice is the separation between:

* **LLM extraction**
* **deterministic RDF serialization**

This keeps the KG generation process inspectable and reduces prompt-driven RDF variability.

### Structural validation

`05_merge_and_validate.py` performs merge-time validation checks on key graph structures.

Current merged validation summary:

* **3839 triples**
* **0 validation errors**
* **0 validation warnings**
* explicit counts for:

  * extracted links
  * repaired links
  * unresolved matches
  * linked external actions

### SHACL validation

`10_shacl_validation.py` validates the merged KG against SHACL constraints.

Current status:

* **CONFORMS**
* **0 violations**

### Canonical-path checks

Lightweight regression checks exist in:

* `tests/test_canonical_graph_contract.py`

These focus on key canonical relations and the explicit query path used in Query 5.

---

## Provenance and Repair Transparency

A key late-stage improvement in this repository is that repaired and unresolved ABox links are no longer hidden.

Current audited counts from the instance-generation / merge summaries include:

* **46** direct `task -> requiresCapability` links
* **30** direct `execution -> realizesTask` links
* **5** fallback `task -> requiresCapability` repairs
* **1** fallback `execution -> realizesTask` repair
* **5** unresolved capability matches
* **1** unresolved execution-task match

The three previously unresolved `requiresCapability` links in paper_09 were resolved by a direct correction to both `output/json/paper_09.json` and `output/instances/paper_09.ttl`. The correction aligned the capability concepts assigned to agents with the capability concepts referenced in the task `required_capabilities` fields (the two sides of LLM extraction had been misaligned).

This is important academically: the project now exposes structural repairs explicitly instead of silently masking them.

---

## Query and Insight Summary

The repository currently includes five competency-question-oriented SPARQL query outputs, covering:

1. **team composition and roles per use case**
2. **capability distribution across papers**
3. **constraints and phenomena across use cases**
4. **interaction patterns and methods**
5. **evaluation and experiment structure**

Current query stage highlights:

* **15** results for team composition / roles
* **11** capability-distribution results (filter: `> 1` capability per paper)
* **10** constraint / phenomenon results (filter: `>= 2` total per use case)
* **29** interaction / method results
* **11** evaluation / experiment results

Each query produces both a CSV result table and a PNG chart. These outputs are available in:

* `output/queries/`

---

## Graph Metrics Summary

`08_kg_metrics.py` produced ontology-level and graph-level metrics, including:

* **25 OWL classes**
* **48 object properties**
* **11 datatype properties**
* **292 SKOS concepts**
* **921 graph nodes**
* **2560 graph edges**
* **largest weakly connected component: 98.3% of nodes**
* **15 Louvain communities**
* **modularity: 0.5883**

This provides a useful graph-level view of cohesion, connectivity, and community structure.

---

## Embeddings Summary

`09_kg_embeddings.py` was run successfully on the project KG and on a combined KG for ablation.

Main result:

* **DistMult** was the best-performing model

Own KG:

* **MRR = 0.3132**
* **Hits@10 = 0.5564**

Combined KG:

* **MRR = 0.4226**
* **Hits@10 = 0.5855**

This suggests that enriching the training graph with the additional populated KG improved the embedding quality for the best-performing model.

The raw predicted links should be interpreted cautiously because the training graph mixes instance-level, thesaurus-level, and schema-level structure.

---

## Known Limitations

This repository is strong, but not perfect.

### 1. External dependency in extraction

Stage `02_extract_metadata.py` depends on an external LLM API and therefore is not fully self-contained without API access.

### 2. External linking is heuristic

Author and affiliation linking uses conservative query-based matching and does not guarantee perfect entity resolution.

### 3. Some ABox repairs still exist

A small number of fallback-generated and unresolved links remain. These are now explicitly audited. The paper_09 `requiresCapability` misalignments were resolved by direct JSON and TTL correction rather than pipeline re-generation.

### 4. Embedding predictions are exploratory

The embedding experiments are useful enrichment, but raw link prediction outputs include semantically noisy candidates and should not be overclaimed.

### 5. Reasoning requires extra setup

Pellet reasoning through Owlready2 requires Java and is more environment-sensitive than the rest of the pipeline.

### 6. Sub-task decompositions are preserved through a manual patch layer

The `hi:hasSubTask` decompositions for paper_01, paper_07, and paper_11 are stored in `output/manual_patches/instances/` and merged after the generated instance files. The corresponding `output/json/` files were not updated, so a full rebuild from stage 03 alone would not reproduce these decompositions unless the manual patches are also retained.

---

## Submission-Oriented Summary

This repository now contains a complete academic-engineering pipeline that:

* builds a Hybrid Intelligence KG from **11 papers** and **3 scenarios**
* produces a final graph of **3839 triples**
* adds **229 external links**, including DOI-based `owl:sameAs` for all 11 papers
* passes **SHACL validation with zero violations**
* answers **five competency questions**, each with a CSV result table and PNG chart
* provides graph metrics, community analysis, embeddings, and ablation results
* exposes repaired and unresolved ABox cases through explicit audit outputs
* models `hi:hasSubTask` task decompositions in three papers
* resolves all `requiresCapability` misalignments in paper_09

The strongest current deliverables for review are:

* `output/merged_kg.ttl`
* `output/shacl/validation_summary.txt`
* `output/audit/merge_validation_summary.json`
* `output/queries/`
* `output/metrics/`
* `output/embeddings/`

---

## Tech Stack

* Python
* RDF / Turtle / N-Triples
* rdflib
* OpenAI API
* SHACL / pySHACL
* Owlready2 / Pellet
* NetworkX / Matplotlib
* PyKEEN / PyTorch

---

## License / Use

This repository was developed as a course project and research-engineering prototype. Reuse of included ontology resources, papers, or derived outputs should respect the original licenses and academic context.
## Project summary

This repository contains a course project for Knowledge Graphs & Semantic Technologies focused on Hybrid Intelligence (HI).

The goal is to demonstrate the ability to:

1. extend an existing ontology,
2. create instances from literature and scenarios,
3. integrate external knowledge sources,
4. consume the KG through symbolic and subsymbolic methods,
5. formulate a small research proposal grounded in the created data.

The project uses the Hybrid Intelligence ontology and thesaurus as starting points and builds a knowledge graph from HHAI papers and HI competition scenarios.

## Architectural choice

The project follows a hybrid extraction/build architecture:

- LLMs are used for structured information extraction from text sources
- Python scripts convert structured outputs into deterministic RDF/Turtle graphs

This design is intentional:
- it accelerates extraction from papers and scenarios
- it keeps graph serialization reproducible and inspectable
- it separates probabilistic extraction from deterministic KG construction

## Main data sources

The project is built from:

- HI ontology and thesaurus
- HHAI literature papers
- HI competition scenarios
- external linked data sources such as Wikidata / DBpedia / scholarly or domain KGs

## Deliverables supported by the repository

The repository is intended to support the following course deliverables:

- ontology extension / design work
- instance creation in RDF
- integration with external sources
- symbolic KG consumption (SPARQL, summaries, metrics)
- subsymbolic KG consumption (embeddings / link prediction if used)
- reproducible project artifacts
- final academic report

## Intended audience

The repo should be understandable and credible for:

- course instructors and TAs
- group members and future contributors
- technical reviewers
- recruiters or managers viewing the project as portfolio work

## Success criteria

A successful project repository should make it easy to understand:

- what the canonical pipeline is
- which scripts are required to rebuild the main graph
- what the main graph artifact is
- which outputs are core versus optional
- how ontology extension, instance creation, linking, and querying are performed
- what the limitations and risks of the pipeline are

## Out of scope

The following are useful but not the primary definition of success:

- large-scale refactoring for software engineering elegance
- making every optional downstream script part of the canonical build
- presenting experimental outputs as core deliverables
- hiding semantic uncertainty behind structurally “valid” graphs

## Current project interpretation

The project should be understood in three layers:

### Layer 1 — Core KG construction
- ontology extension
- source parsing
- extraction
- RDF generation
- external linking
- merge

### Layer 2 — Quality and validation
- reasoning
- SHACL validation
- structural and consistency checks

### Layer 3 — KG consumption and analysis
- SPARQL queries
- KG metrics
- embeddings / ablation / link prediction

This layered view is the preferred interpretation for repo organization and maintenance.

Before making non-trivial changes, read:

1. `docs/PROJECT_BRIEF.md`
2. `docs/COURSE_CONTRACT.md`
3. `docs/PIPELINE_CONTRACT.md`

## Project goal

This repository implements a Knowledge Graphs & Semantic Technologies course project based on the Hybrid Intelligence ontology and thesaurus.

The project builds a Hybrid Intelligence knowledge graph from:
- HI literature papers
- HI competition scenarios
- ontology/thesaurus extensions
- external knowledge links

The architecture is intentionally hybrid:
- LLMs produce structured extraction outputs
- Python scripts deterministically generate RDF/Turtle

The repo must remain academically credible, reproducible, and understandable to both instructors and technical reviewers.

## Canonical workflow

Treat this as the canonical workflow unless explicitly told otherwise:

`01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 10 -> 07 -> 08 -> 09`

Meaning:
- 01 parse sources
- 02 extract metadata with LLM
- 03 generate RDF instances
- 04 add external links
- 05 merge and validate
- 06 reasoning
- 10 SHACL validation
- 07 SPARQL querying
- 08 KG metrics
- 09 embeddings / ablation

## Status of stages

- Core/canonical build stages: `01, 02, 03, 04, 05`
- Quality/support stages: `06, 10`
- Consumption/analysis stages: `07, 08, 09`

Do not treat stage 09 as defining the canonical graph.

## Canonical artifact rules

- The canonical merged graph is: `output/merged_kg.ttl`
- Derived serializations may exist, but must not replace the canonical graph
- Legacy artifacts must not be silently used as fallback inputs
- If a canonical file is missing, prefer explicit failure with a clear message

## Change policy

- Be conservative with numbered scripts (`01` to `10`)
- Do not make broad refactors unless explicitly asked
- Do not silently change scientific logic
- Preserve semantic correctness over structural convenience
- Do not invent or strengthen claims in documentation
- Prefer minimal, reviewable edits

## Legacy / experimental handling

- Legacy files should be clearly labeled or removed only after code no longer depends on them
- Optional or experimental outputs should not be presented as canonical deliverables
- If uncertain whether something is canonical, check `docs/PIPELINE_CONTRACT.md`

## Documentation policy

When editing documentation:
- keep tone professional and academically honest
- distinguish mandatory project requirements from optional enhancements
- align claims with the actual repository state

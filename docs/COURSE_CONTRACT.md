## Purpose of this file

The teaching materials and project framing contain multiple components and some ambiguity. This file records the practical interpretation used for this repository, so that maintenance decisions stay aligned with the actual grading goals.

## Distilled course requirements

From the project description, the project consists of:

1. Ontology design
2. Instance creation
3. Integration with external sources
4. KG consumption
5. Research proposal

The written report is expected to include:

- Title / authors
- Abstract
- Introduction
- Data section:
  - ontology design
  - instance creation
  - linking
- Insights section:
  - querying / visualizing with SPARQL
  - KG metrics / summary
  - optionally link prediction / node classification / KG embeddings
- Research proposal
- Conclusion

## Practical interpretation

### Clearly mandatory
- Expand or modify the ontology
- Create instances from HI papers and scenarios
- Link the graph to external knowledge
- Document methods and data clearly
- Show meaningful queries and report results
- Produce a final report
- Maintain reproducibility

### Expected target level for a strong project
- Use 10 papers if possible
- Use 3 HI scenarios
- Provide a well-documented reproducible workflow
- Include substantial external linking
- Include multiple non-trivial queries
- Show that ontology/data integration is coherent

### Useful but not strictly core
- Reasoning
- SHACL validation
- KG metrics
- Embeddings / link prediction / ablation

These are best treated as supporting or enrichment components unless explicitly required for grading.

## Rubric interpretation

Based on the implementation rubric:

### Ontology Design
Strong performance requires more than adding a few classes/properties.
Consistency, restrictions, and some meaningful OWL use matter.

### Instance Creation
High performance comes from converting many papers and using the ontology thoroughly.
Completeness and ontology-aware structure matter.

### Schema/Data Integration/Linking
A strong project should connect the graph to external sources with a meaningful number of links.

### Reproducibility
The repository must make data, code, and method understandable and runnable.

### Queries
The project must show multiple useful queries, not just a minimal demonstration.

## Operational conclusion for this repository

The repo should prioritize clarity and correctness in the following order:

1. ontology and instance-building pipeline
2. external linking
3. reproducibility and documentation
4. SPARQL and graph insights
5. optional advanced analysis

## What should not distort repo decisions

The following should not be allowed to dominate maintenance choices:

- optional downstream experiments being treated as the canonical output
- undocumented legacy artifacts confusing the trusted workflow
- structural validity being prioritized over semantic honesty
- experimental convenience overriding reproducibility

## Repository policy derived from the course

Therefore this repository should:

- maintain one clear canonical merged graph
- separate core build steps from optional analysis
- document limitations honestly
- support the report structure
- support reproducibility for the main project path

"""
Step 10: SHACL Validation of the HI Knowledge Graph

Usage:
    python 10_shacl_validation.py

Writes SHACL shapes to a file, then validates the merged KG against them.
Aligned with the SHACL-tutorial.ipynb (Exercise 3) and the ESWC HI
Ontology paper's SHACL validation approach.

Shapes enforce:
  - HITeam: >=2 members, >=1 HumanAgent, >=1 ArtificialAgent, >=1 Goal
  - Goal: >=1 requiresTask
  - Task: >=1 requiresCapability
  - TaskExecution: exactly 1 realizesTask
  - Agent (team member): >=1 hasRoleConcept
  - Paper: >=1 hasAuthor, 1 hasTitle, 1 publishedAt, >=1 hasKeyword (IRI)
  - UseCase: >=1 hasHITeam
  - Interaction: >=2 hasAgentInvolved

Dependencies:
    pip install pyshacl rdflib

Output:
    output/shacl/
      hi_shapes.ttl          <- SHACL shapes file
      validation_report.ttl  <- Full SHACL validation report
      validation_summary.txt <- Human-readable summary
"""
import sys
from pathlib import Path

try:
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise

try:
    import pyshacl
except ImportError:
    print("Install pyshacl: pip install pyshacl")
    raise

try:
    from config import OUTPUT_DIR, HI_NS, HINT_NS, INST_NS
except ImportError:
    OUTPUT_DIR = Path("../output")
    HI_NS = "https://w3id.org/hi-ontology#"
    HINT_NS = "https://w3id.org/hi-thesaurus/"
    INST_NS = "https://w3id.org/hi-ontology/instances/"

SHACL_DIR = OUTPUT_DIR / "shacl"

SHAPES_TTL = """
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix hi:   <https://w3id.org/hi-ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .


###############################################################
# 1. HITeam Shape (tutorial Exercise 3 + ESWC paper)
###############################################################
hi:HITeamShape
    a sh:NodeShape ;
    sh:targetClass hi:HITeam ;
    sh:property [
        sh:path hi:hasMember ;
        sh:minCount 2 ;
        sh:message "A HITeam must have at least two agents." ;
    ] ;
    sh:property [
        sh:path hi:hasMember ;
        sh:qualifiedValueShape [ sh:class hi:HumanAgent ] ;
        sh:qualifiedMinCount 1 ;
        sh:message "A HITeam must include at least one HumanAgent." ;
    ] ;
    sh:property [
        sh:path hi:hasMember ;
        sh:qualifiedValueShape [ sh:class hi:ArtificialAgent ] ;
        sh:qualifiedMinCount 1 ;
        sh:message "A HITeam must include at least one ArtificialAgent." ;
    ] ;
    sh:property [
        sh:path hi:hasGoal ;
        sh:minCount 1 ;
        sh:message "A HITeam must have at least one goal." ;
    ] .

###############################################################
# 2. Team members must have a role (tutorial Exercise 3)
###############################################################
hi:TeamMemberRoleShape
    a sh:NodeShape ;
    sh:targetObjectsOf hi:hasMember ;
    sh:property [
        sh:path hi:hasRoleConcept ;
        sh:minCount 1 ;
        sh:message "Every team member must have at least one role concept." ;
    ] .

###############################################################
# 3. Goal Shape (tutorial Exercise 3)
###############################################################
hi:GoalShape
    a sh:NodeShape ;
    sh:targetClass hi:Goal ;
    sh:property [
        sh:path hi:requiresTask ;
        sh:minCount 1 ;
        sh:message "Each Goal must require at least one Task." ;
    ] .

###############################################################
# 4. Task Shape
###############################################################
hi:TaskShape
    a sh:NodeShape ;
    sh:targetClass hi:Task ;
    sh:property [
        sh:path hi:requiresCapability ;
        sh:minCount 1 ;
        sh:message "Each Task must require at least one Capability." ;
    ] .

###############################################################
# 5. TaskExecution Shape (ESWC paper)
###############################################################
hi:TaskExecutionShape
    a sh:NodeShape ;
    sh:targetClass hi:TaskExecution ;
    sh:property [
        sh:path hi:realizesTask ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Each TaskExecution must realise exactly one Task." ;
    ] .

###############################################################
# 6. UseCase Shapes
###############################################################
hi:ResearchUseCaseShape
    a sh:NodeShape ;
    sh:targetClass hi:ResearchUseCase ;
    sh:property [
        sh:path hi:hasHITeam ;
        sh:minCount 1 ;
        sh:message "Each ResearchUseCase must have at least one HITeam." ;
    ] .

hi:CompetitionUseCaseShape
    a sh:NodeShape ;
    sh:targetClass hi:CompetitionUseCase ;
    sh:property [
        sh:path hi:hasHITeam ;
        sh:minCount 1 ;
        sh:message "Each CompetitionUseCase must have at least one HITeam." ;
    ] .

###############################################################
# 7. Paper Shape (our extension)
###############################################################
hi:PaperShape
    a sh:NodeShape ;
    sh:targetClass hi:Paper ;
    sh:property [
        sh:path hi:hasAuthor ;
        sh:minCount 1 ;
        sh:message "Each Paper must have at least one Author." ;
    ] ;
    sh:property [
        sh:path hi:hasTitle ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Each Paper must have exactly one title (xsd:string)." ;
    ] ;
    sh:property [
        sh:path hi:publishedAt ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Each Paper must be published at exactly one Conference." ;
    ] ;
    sh:property [
        sh:path hi:hasKeyword ;
        sh:minCount 1 ;
        sh:nodeKind sh:IRI ;
        sh:message "Paper keywords must be IRIs (skos:Concept), not literals." ;
    ] .

###############################################################
# 8. Interaction Shape (ESWC paper)
###############################################################
hi:InteractionShape
    a sh:NodeShape ;
    sh:targetClass hi:Interaction ;
    sh:property [
        sh:path hi:hasAgentInvolved ;
        sh:minCount 2 ;
        sh:message "Each Interaction must involve at least two agents." ;
    ] .
"""


def main():
    SHACL_DIR.mkdir(parents=True, exist_ok=True)

    # Write shapes
    shapes_path = SHACL_DIR / "hi_shapes.ttl"
    shapes_path.write_text(SHAPES_TTL, encoding="utf-8")
    print(f"SHACL shapes written to: {shapes_path}")

    # Locate merged KG
    candidates = [OUTPUT_DIR / "merged_kg.ttl"]
    kg_file = None
    for c in candidates:
        if c.exists():
            kg_file = c
            break
    if not kg_file:
        if len(sys.argv) > 1:
            kg_file = Path(sys.argv[1])
        if not kg_file or not kg_file.exists():
            print("ERROR: Cannot find merged KG.")
            sys.exit(1)

    print(f"Loading KG: {kg_file}")
    data_graph = Graph()
    data_graph.parse(str(kg_file), format="turtle")
    print(f"Loaded {len(data_graph)} triples.")

    shapes_graph = Graph()
    shapes_graph.parse(str(shapes_path), format="turtle")
    print(f"Loaded {len(shapes_graph)} shape triples.\n")

    # Validate
    print("=" * 60)
    print("Running SHACL validation...")
    print("=" * 60)

    conforms, results_graph, results_text = pyshacl.validate(
        data_graph, shacl_graph=shapes_graph,
        inference="none", abort_on_first=False,
    )

    status = "CONFORMS" if conforms else "DOES NOT CONFORM"
    print(f"\n  Result: {status}")

    SH = Namespace("http://www.w3.org/ns/shacl#")
    violations = list(results_graph.subjects(RDF.type, SH.ValidationResult))
    print(f"  Violations: {len(violations)}")

    if violations:
        print(f"\n  Violation details:")
        for v in violations:
            focus = list(results_graph.objects(v, SH.focusNode))
            path = list(results_graph.objects(v, SH.resultPath))
            msg = list(results_graph.objects(v, SH.resultMessage))
            sev = list(results_graph.objects(v, SH.resultSeverity))
            focus_s = str(focus[0]).split("/")[-1].split("#")[-1] if focus else "?"
            path_s = str(path[0]).split("/")[-1].split("#")[-1] if path else "?"
            msg_s = str(msg[0]) if msg else "?"
            sev_s = str(sev[0]).split("#")[-1] if sev else "Violation"
            print(f"    [{sev_s}] {focus_s} / {path_s}: {msg_s}")

    # Save outputs
    results_graph.serialize(
        destination=str(SHACL_DIR / "validation_report.ttl"), format="turtle")

    lines = [
        "SHACL Validation Summary", "=" * 40,
        f"Data graph: {kg_file}", f"Triples: {len(data_graph)}",
        f"Shapes: {shapes_path}", "",
        f"Result: {status}", f"Violations: {len(violations)}", "",
    ]
    if violations:
        lines.append("Violation details:")
        for v in violations:
            focus = list(results_graph.objects(v, SH.focusNode))
            msg = list(results_graph.objects(v, SH.resultMessage))
            focus_s = str(focus[0]).split("/")[-1].split("#")[-1] if focus else "?"
            msg_s = str(msg[0]) if msg else "?"
            lines.append(f"  - {focus_s}: {msg_s}")
    else:
        lines.append("All SHACL shapes satisfied.")

    (SHACL_DIR / "validation_summary.txt").write_text(
        "\n".join(lines), encoding="utf-8")

    print(f"\n  -> Saved hi_shapes.ttl")
    print(f"  -> Saved validation_report.ttl")
    print(f"  -> Saved validation_summary.txt")


if __name__ == "__main__":
    main()

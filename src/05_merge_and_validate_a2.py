"""
Step 5: Merge all RDF files into one knowledge graph and validate.

Usage:
    python 05_merge_and_validate.py

Merges: ontology + extensions + thesaurus + thesaurus extensions +
        all instance files + external links -> merged_kg.ttl

Also runs basic validation checks.
"""
import sys
from pathlib import Path

try:
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF, RDFS, OWL, SKOS
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise



from config import (
    ONTOLOGY_FILE, THESAURUS_FILE, EXTENSIONS_FILE,
    INSTANCES_DIR, OUTPUT_DIR,
    HI_NS, HINT_NS, INST_NS
)

MERGED_KG_FILE = OUTPUT_DIR / "merged_kg_a2.ttl"

HI = Namespace(HI_NS)
HINT = Namespace(HINT_NS)
INST = Namespace(INST_NS)


def count_by_type(g: Graph, rdf_type) -> int:
    """Count instances of a given RDF type."""
    return len(list(g.subjects(RDF.type, rdf_type)))


def validate_teams(g: Graph) -> list[str]:
    """Check that every HITeam has at least 1 human and 1 artificial agent."""
    issues = []
    for team in g.subjects(RDF.type, HI.HITeam):
        members = list(g.objects(team, HI.hasMember))
        humans = [m for m in members if (m, RDF.type, HI.HumanAgent) in g]
        artificials = [m for m in members if (m, RDF.type, HI.ArtificialAgent) in g]

        team_label = str(list(g.objects(team, RDFS.label))[0]) if list(g.objects(team, RDFS.label)) else str(team)

        if not humans:
            issues.append(f"Team '{team_label}' has no HumanAgent members")
        if not artificials:
            issues.append(f"Team '{team_label}' has no ArtificialAgent members")

    return issues


def validate_goals(g: Graph) -> list[str]:
    """Check that every Goal has at least one task."""
    issues = []
    for goal in g.subjects(RDF.type, HI.Goal):
        tasks = list(g.objects(goal, HI.requiresTask))
        if not tasks:
            goal_label = str(list(g.objects(goal, RDFS.label))[0]) if list(g.objects(goal, RDFS.label)) else str(goal)
            issues.append(f"Goal '{goal_label}' has no tasks")
    return issues


def validate_use_cases(g: Graph) -> list[str]:
    """Check that every UseCase has an HITeam."""
    issues = []
    for uc_type in [HI.UseCase, HI.ResearchUseCase, HI.CompetitionUseCase]:
        for uc in g.subjects(RDF.type, uc_type):
            teams = list(g.objects(uc, HI.hasHITeam))
            if not teams:
                uc_label = str(list(g.objects(uc, RDFS.label))[0]) if list(g.objects(uc, RDFS.label)) else str(uc)
                issues.append(f"UseCase '{uc_label}' has no HITeam")
    return issues


def main():
    print("=== Merging all RDF sources ===\n")
    merged = Graph()
    merged.bind("hi", HI)
    merged.bind("hint", HINT)
    merged.bind("inst", INST)

    files_to_load = []

    # Core ontology files
    for f in [ONTOLOGY_FILE, THESAURUS_FILE, EXTENSIONS_FILE]:
        if f.exists():
            files_to_load.append(("SCHEMA", f))
        else:
            print(f"  WARNING: {f} not found")

    # Thesaurus extensions (if generated)
    thes_ext = OUTPUT_DIR / "hi-thesaurus-extensions.ttl"
    if thes_ext.exists():
        files_to_load.append(("THESAURUS_EXT", thes_ext))

    # Instance files
    if INSTANCES_DIR.exists():
        for ttl in sorted(INSTANCES_DIR.glob("*.ttl")):
            files_to_load.append(("INSTANCE", ttl))

    # External links
    # ext_links = OUTPUT_DIR / "external_links.ttl"
    # if ext_links.exists():
    #     files_to_load.append(("LINKS", ext_links))

    # Load all
    for category, filepath in files_to_load:
        try:
            before = len(merged)
            merged.parse(str(filepath), format="turtle")
            after = len(merged)
            print(f"  [{category:14s}] {filepath.name}: +{after - before} triples")
        except Exception as e:
            print(f"  [{category:14s}] {filepath.name}: ERROR - {e}")

    total = len(merged)
    print(f"\n  TOTAL: {total} triples")

    # ── Statistics ────────────────────────────────────────────
    print("\n=== Knowledge Graph Statistics ===")
    print(f"  Papers:          {count_by_type(merged, HI.Paper)}")
    print(f"  Authors:         {count_by_type(merged, HI.Author)}")
    print(f"  Conferences:     {count_by_type(merged, HI.Conference)}")
    print(f"  Affiliations:    {count_by_type(merged, HI.Affiliation)}")
    print(f"  ResearchUseCases:{count_by_type(merged, HI.ResearchUseCase)}")
    print(f"  CompetitionUCs:  {count_by_type(merged, HI.CompetitionUseCase)}")
    print(f"  HITeams:         {count_by_type(merged, HI.HITeam)}")
    print(f"  HumanAgents:     {count_by_type(merged, HI.HumanAgent)}")
    print(f"  ArtificialAgents:{count_by_type(merged, HI.ArtificialAgent)}")
    print(f"  Capabilities:    {count_by_type(merged, HI.Capability)}")
    print(f"  Goals:           {count_by_type(merged, HI.Goal)}")
    print(f"  Tasks:           {count_by_type(merged, HI.Task)}")
    print(f"  TaskExecutions:  {count_by_type(merged, HI.TaskExecution)}")
    print(f"  Interactions:    {count_by_type(merged, HI.Interaction)}")
    print(f"  Evaluations:     {count_by_type(merged, HI.Evaluation)}")
    print(f"  Experiments:     {count_by_type(merged, HI.Experiment)}")
    print(f"  Contexts:        {count_by_type(merged, HI.Context)}")

    # Count external links
    same_as = len(list(merged.triples((None, OWL.sameAs, None))))
    close_match = len(list(merged.triples((None, SKOS.closeMatch, None))))
    related_match = len(list(merged.triples((None, SKOS.relatedMatch, None))))
    see_also = len(list(merged.triples((None, RDFS.seeAlso, None))))
    print(f"\n  External links:")
    print(f"    owl:sameAs:       {same_as}")
    print(f"    skos:closeMatch:  {close_match}")
    print(f"    skos:relatedMatch:{related_match}")
    print(f"    rdfs:seeAlso:     {see_also}")
    print(f"    TOTAL:            {same_as + close_match + related_match + see_also}")

    # ── Validation ────────────────────────────────────────────
    print("\n=== Validation ===")
    all_issues = []
    all_issues.extend(validate_teams(merged))
    all_issues.extend(validate_goals(merged))
    all_issues.extend(validate_use_cases(merged))

    if all_issues:
        print(f"  {len(all_issues)} issues found:")
        for issue in all_issues:
            print(f"    - {issue}")
    else:
        print("  All validation checks passed!")

    # ── Save ──────────────────────────────────────────────────
    MERGED_KG_FILE.parent.mkdir(parents=True, exist_ok=True)
    merged.serialize(destination=str(MERGED_KG_FILE), format="turtle")
    print(f"\nMerged KG saved to: {MERGED_KG_FILE}")
    print(f"Total triples: {total}")


if __name__ == "__main__":
    main()

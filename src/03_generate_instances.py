"""
Step 3: Convert extracted JSON metadata into RDF instances (Turtle).

Usage:
    python 03_generate_instances.py                  # process all
    python 03_generate_instances.py paper_01          # process one

Reads JSON from output/json/, produces Turtle files in output/instances/.
Also collects new HINT concepts and writes them to output/hi-thesaurus-extensions.ttl.

This script is DETERMINISTIC - no LLM calls. It converts the structured
JSON into valid RDF using rdflib, following the HI Ontology V2 schema.
"""
import json
import re
import sys
from pathlib import Path

try:
    from rdflib import Graph, Namespace, Literal, URIRef, BNode
    from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, FOAF, DCTERMS, DC
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise

from config import (
    JSON_DIR, INSTANCES_DIR, OUTPUT_DIR,
    HI_NS, HINT_NS, INST_NS
)

# ── Namespace setup ───────────────────────────────────────────
HI = Namespace(HI_NS)
HINT = Namespace(HINT_NS)
INST = Namespace(INST_NS)
SCHEMA = Namespace("http://schema.org/")
BIBO = Namespace("http://purl.org/ontology/bibo/")


def sanitize_uri(label: str) -> str:
    """Convert a human label into a valid URI fragment."""
    # Remove special chars, replace spaces with camelCase
    s = re.sub(r'[^\w\s-]', '', label)
    parts = s.strip().split()
    if not parts:
        return "Unknown"
    return parts[0].capitalize() + ''.join(w.capitalize() for w in parts[1:])


def resolve_hint_concept(concept_str: str) -> URIRef:
    """
    Resolve a concept string like 'hint:TransparencyConstraint'
    to a proper URIRef.
    """
    if concept_str.startswith("hint:"):
        local = concept_str[5:]  # strip 'hint:'
        return HINT[local]
    # If it's already a full URI
    if concept_str.startswith("http"):
        return URIRef(concept_str)
    # Fallback: make it a HINT concept
    return HINT[sanitize_uri(concept_str)]


def build_paper_graph(data: dict, source_id: str) -> tuple[Graph, list[dict]]:
    """
    Build an RDF graph from extracted JSON for one paper/scenario.
    Returns (graph, new_concepts_list).
    """
    g = Graph()
    g.bind("hi", HI)
    g.bind("hint", HINT)
    g.bind("inst", INST)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)
    g.bind("dcterms", DCTERMS)
    g.bind("schema", SCHEMA)
    g.bind("bibo", BIBO)
    g.bind("skos", SKOS)

    uc_data = data.get("use_case", {})
    is_scenario = data.get("use_case", {}).get("type") == "competition"
    prefix = sanitize_uri(source_id)  # e.g. "Paper01" or "Scenario01"

    # ── Paper metadata (only for research papers) ─────────────
    if not is_scenario and data.get("title"):
        paper_uri = INST[f"{prefix}"]
        g.add((paper_uri, RDF.type, HI.Paper))
        g.add((paper_uri, HI.hasTitle, Literal(data["title"], datatype=XSD.string)))
        g.add((paper_uri, HI.hasPublicationYear, Literal("2025", datatype=XSD.gYear)))

        # Authors
        for i, author in enumerate(data.get("authors", []), 1):
            author_uri = INST[f"{prefix}_Author{i}"]
            g.add((author_uri, RDF.type, HI.Author))
            g.add((author_uri, HI.hasAuthorName, Literal(author["name"], datatype=XSD.string)))
            g.add((author_uri, FOAF.name, Literal(author["name"])))
            g.add((paper_uri, HI.hasAuthor, author_uri))

            if author.get("affiliation"):
                aff_id = sanitize_uri(author["affiliation"])
                aff_uri = INST[f"Affiliation_{aff_id}"]
                g.add((aff_uri, RDF.type, HI.Affiliation))
                g.add((aff_uri, RDFS.label, Literal(author["affiliation"])))
                g.add((aff_uri, SCHEMA.name, Literal(author["affiliation"])))
                g.add((author_uri, HI.hasAffiliation, aff_uri))

        # Conference
        conf_uri = INST["HHAI2025"]
        g.add((conf_uri, RDF.type, HI.Conference))
        g.add((conf_uri, HI.hasConferenceName, Literal("HHAI 2025", datatype=XSD.string)))
        g.add((conf_uri, HI.hasConferenceYear, Literal("2025", datatype=XSD.gYear)))
        g.add((conf_uri, RDFS.label, Literal("HHAI 2025")))
        g.add((paper_uri, HI.publishedAt, conf_uri))

        # Keywords
        for kw in data.get("keywords", []):
            g.add((paper_uri, HI.hasKeyword, Literal(kw)))

    # ── Use Case ──────────────────────────────────────────────
    uc_label = uc_data.get("label", source_id)
    uc_uri = INST[f"{prefix}_UseCase"]

    if is_scenario:
        g.add((uc_uri, RDF.type, HI.CompetitionUseCase))
        if data.get("use_case", {}).get("context", {}).get("label"):
            g.add((uc_uri, HI.hasScenarioDescription,
                   Literal(uc_data["context"]["label"], datatype=XSD.string)))
    else:
        g.add((uc_uri, RDF.type, HI.ResearchUseCase))
        # Link paper to use case
        if data.get("title"):
            g.add((INST[prefix], HI.describesUseCase, uc_uri))

    g.add((uc_uri, RDFS.label, Literal(uc_label)))

    # Domain concepts
    for dc in uc_data.get("domain_concepts", []):
        g.add((uc_uri, HI.hasDomainConcept, resolve_hint_concept(dc)))

    # ── Context ───────────────────────────────────────────────
    ctx_data = uc_data.get("context", {})
    if ctx_data:
        ctx_uri = INST[f"{prefix}_Context"]
        g.add((ctx_uri, RDF.type, HI.Context))
        g.add((ctx_uri, RDFS.label, Literal(ctx_data.get("label", "Context"))))

        for cc in ctx_data.get("context_concepts", []):
            g.add((ctx_uri, HI.hasContextConcept, resolve_hint_concept(cc)))
        for con in ctx_data.get("constraint_concepts", []):
            g.add((ctx_uri, HI.hasConstraintConcept, resolve_hint_concept(con)))
        for phen in ctx_data.get("phenomenon_concepts", []):
            g.add((ctx_uri, HI.hasPhenomenonConcept, resolve_hint_concept(phen)))

    # ── HI Team ───────────────────────────────────────────────
    team_data = uc_data.get("team", {})
    team_uri = INST[f"{prefix}_Team"]
    g.add((team_uri, RDF.type, HI.HITeam))
    g.add((team_uri, RDFS.label, Literal(f"{uc_label} Team")))
    g.add((uc_uri, HI.hasHITeam, team_uri))

    # Link team to context
    if ctx_data:
        g.add((team_uri, HI.isInfluencedBy, ctx_uri))
        g.add((ctx_uri, HI.hasInfluenceOn, team_uri))

    # Track agent URIs by label for cross-referencing
    agent_uris = {}

    # Capabilities tracker: label -> URI (for linking tasks)
    capability_uris = {}

    # ── Agents ────────────────────────────────────────────────
    for agent_type, agent_class in [("human_agents", HI.HumanAgent),
                                     ("artificial_agents", HI.ArtificialAgent)]:
        for j, agent in enumerate(team_data.get(agent_type, []), 1):
            agent_label = agent.get("label", f"Agent{j}")
            agent_id = sanitize_uri(agent_label)
            agent_uri = INST[f"{prefix}_{agent_id}"]

            g.add((agent_uri, RDF.type, agent_class))
            g.add((agent_uri, RDFS.label, Literal(agent_label)))
            g.add((team_uri, HI.hasMember, agent_uri))

            if agent.get("role_concept"):
                g.add((agent_uri, HI.hasRoleConcept, resolve_hint_concept(agent["role_concept"])))

            # Agent capabilities
            for k, cap in enumerate(agent.get("capabilities", []), 1):
                cap_label = cap.get("label", f"Capability{k}")
                cap_id = sanitize_uri(cap_label)
                cap_uri = INST[f"{prefix}_{agent_id}_Cap_{cap_id}"]

                g.add((cap_uri, RDF.type, HI.Capability))
                g.add((cap_uri, RDFS.label, Literal(cap_label)))
                g.add((agent_uri, HI.hasCapability, cap_uri))

                if cap.get("concept"):
                    g.add((cap_uri, HI.hasCapabilityConcept, resolve_hint_concept(cap["concept"])))

                capability_uris[cap_label] = cap_uri

            agent_uris[agent_label] = agent_uri

    # ── Goals and Tasks ───────────────────────────────────────
    task_uris = {}  # label -> URI

    for gi, goal in enumerate(uc_data.get("goals", []), 1):
        goal_label = goal.get("label", f"Goal{gi}")
        goal_id = sanitize_uri(goal_label)
        goal_uri = INST[f"{prefix}_Goal_{goal_id}"]

        g.add((goal_uri, RDF.type, HI.Goal))
        g.add((goal_uri, RDFS.label, Literal(goal_label)))
        g.add((team_uri, HI.hasGoal, goal_uri))

        if goal.get("goal_concept"):
            g.add((goal_uri, HI.hasGoalConcept, resolve_hint_concept(goal["goal_concept"])))

        # Tasks
        for ti, task in enumerate(goal.get("tasks", []), 1):
            task_label = task.get("label", f"Task{ti}")
            task_id = sanitize_uri(task_label)
            task_uri = INST[f"{prefix}_Task_{task_id}"]

            g.add((task_uri, RDF.type, HI.Task))
            g.add((task_uri, RDFS.label, Literal(task_label)))
            g.add((goal_uri, HI.requiresTask, task_uri))

            if task.get("task_concept"):
                g.add((task_uri, HI.hasTaskConcept, resolve_hint_concept(task["task_concept"])))

            # Link task to required capabilities
            for rc in task.get("required_capabilities", []):
                rc_concept = resolve_hint_concept(rc)
                # Find or create a capability instance that matches
                # We link through requiresCapability
                for cap_label, cap_uri in capability_uris.items():
                    # Check if this capability has the matching concept
                    # Simple heuristic: match by concept URI
                    if rc in [f"hint:{cap_label}", rc]:
                        g.add((task_uri, HI.requiresCapability, cap_uri))
                        g.add((cap_uri, HI.allowsTask, task_uri))
                        break

            # Sub-tasks
            for st in task.get("sub_tasks", []):
                st_label = st if isinstance(st, str) else st.get("label", "SubTask")
                st_id = sanitize_uri(st_label)
                st_uri = INST[f"{prefix}_Task_{st_id}"]
                g.add((st_uri, RDF.type, HI.Task))
                g.add((st_uri, RDFS.label, Literal(st_label)))
                g.add((task_uri, HI.hasSubTask, st_uri))

            task_uris[task_label] = task_uri

    # ── Task Executions ───────────────────────────────────────
    for ei, exec_data in enumerate(uc_data.get("task_executions", []), 1):
        exec_label = exec_data.get("label", f"Execution{ei}")
        exec_id = sanitize_uri(exec_label)
        exec_uri = INST[f"{prefix}_Exec_{exec_id}"]

        g.add((exec_uri, RDF.type, HI.TaskExecution))
        g.add((exec_uri, RDFS.label, Literal(exec_label)))

        # Link to task
        task_label = exec_data.get("task_label", "")
        if task_label in task_uris:
            g.add((exec_uri, HI.realizesTask, task_uris[task_label]))

        # Link to performing agent
        agent_label = exec_data.get("performed_by", "")
        if agent_label in agent_uris:
            g.add((agent_uris[agent_label], HI.performsExecution, exec_uri))

        # Method concept
        if exec_data.get("method_concept"):
            g.add((exec_uri, HI.hasMethodConcept, resolve_hint_concept(exec_data["method_concept"])))

    # ── Interactions ──────────────────────────────────────────
    for ii, inter in enumerate(uc_data.get("interactions", []), 1):
        inter_label = inter.get("label", f"Interaction{ii}")
        inter_id = sanitize_uri(inter_label)
        inter_uri = INST[f"{prefix}_Interaction_{inter_id}"]

        g.add((inter_uri, RDF.type, HI.Interaction))
        g.add((inter_uri, RDFS.label, Literal(inter_label)))

        if inter.get("modality_concept"):
            g.add((inter_uri, HI.hasInteractionModalityConcept,
                   resolve_hint_concept(inter["modality_concept"])))
        if inter.get("intent_concept"):
            g.add((inter_uri, HI.hasInteractionIntentConcept,
                   resolve_hint_concept(inter["intent_concept"])))

        # Link involved agents
        for agent_label in inter.get("agents_involved", []):
            if agent_label in agent_uris:
                g.add((inter_uri, HI.hasAgentInvolved, agent_uris[agent_label]))

    # ── Evaluation ────────────────────────────────────────────
    eval_data = uc_data.get("evaluation", {})
    if eval_data and (eval_data.get("evaluation_concepts") or eval_data.get("metric_concepts")):
        eval_uri = INST[f"{prefix}_Evaluation"]
        g.add((eval_uri, RDF.type, HI.Evaluation))
        g.add((eval_uri, RDFS.label, Literal(eval_data.get("label", "Evaluation"))))

        for ec in eval_data.get("evaluation_concepts", []):
            g.add((eval_uri, HI.hasEvaluationConcept, resolve_hint_concept(ec)))
        for mc in eval_data.get("metric_concepts", []):
            g.add((eval_uri, HI.hasMetricConcept, resolve_hint_concept(mc)))

        # Experiments
        for xi, exp in enumerate(eval_data.get("experiments", []), 1):
            exp_label = exp.get("label", f"Experiment{xi}")
            exp_id = sanitize_uri(exp_label)
            exp_uri = INST[f"{prefix}_Experiment_{exp_id}"]

            g.add((exp_uri, RDF.type, HI.Experiment))
            g.add((exp_uri, RDFS.label, Literal(exp_label)))
            g.add((eval_uri, HI.hasExperiment, exp_uri))

            if exp.get("experiment_concept"):
                g.add((exp_uri, HI.hasExperimentConcept, resolve_hint_concept(exp["experiment_concept"])))

            for mt in exp.get("metrics_tested", []):
                g.add((exp_uri, HI.hasMetricTested, resolve_hint_concept(mt)))

            if exp.get("null_hypothesis") and exp["null_hypothesis"] != "null":
                g.add((exp_uri, HI.hasNullHypothesis, Literal(exp["null_hypothesis"], datatype=XSD.string)))
            if exp.get("alternative_hypothesis") and exp["alternative_hypothesis"] != "null":
                g.add((exp_uri, HI.hasAlternativeHypothesis, Literal(exp["alternative_hypothesis"], datatype=XSD.string)))

    # Collect new concepts
    new_concepts = data.get("new_concepts", [])
    return g, new_concepts


def generate_thesaurus_extensions(all_new_concepts: list[dict]) -> str:
    """
    Generate Turtle for new HINT thesaurus concepts
    that the LLM identified as missing.
    """
    g = Graph()
    g.bind("hint", HINT)
    g.bind("skos", SKOS)
    g.bind("hi", HI)

    seen = set()
    for concept in all_new_concepts:
        uri_str = concept.get("uri", "")
        if not uri_str or uri_str in seen:
            continue
        seen.add(uri_str)

        concept_uri = resolve_hint_concept(uri_str)
        g.add((concept_uri, RDF.type, SKOS.Concept))
        g.add((concept_uri, SKOS.inScheme, HINT.HIScheme))
        g.add((concept_uri, SKOS.prefLabel, Literal(concept.get("label", uri_str), lang="en")))

        if concept.get("definition"):
            g.add((concept_uri, SKOS.definition, Literal(concept["definition"], lang="en")))
        if concept.get("broader"):
            g.add((concept_uri, SKOS.broader, resolve_hint_concept(concept["broader"])))

    return g.serialize(format="turtle")


def main():
    INSTANCES_DIR.mkdir(parents=True, exist_ok=True)

    # Parse arguments
    target = None
    for arg in sys.argv[1:]:
        target = arg

    json_files = sorted(JSON_DIR.glob("*.json"))
    if target:
        json_files = [f for f in json_files if target in f.stem]

    if not json_files:
        print(f"No JSON files found in {JSON_DIR}/")
        print("Run 02_extract_metadata.py first.")
        sys.exit(1)

    print(f"=== Generating RDF instances ({len(json_files)} sources) ===\n")

    all_new_concepts = []
    total_triples = 0

    for json_file in json_files:
        source_id = json_file.stem

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "_error" in data:
            print(f"  [{source_id}] SKIPPED (extraction error)")
            continue

        print(f"  [{source_id}] Generating RDF...")

        g, new_concepts = build_paper_graph(data, source_id)
        all_new_concepts.extend(new_concepts)

        # Serialize
        ttl_path = INSTANCES_DIR / f"{source_id}.ttl"
        g.serialize(destination=str(ttl_path), format="turtle")

        n_triples = len(g)
        total_triples += n_triples
        print(f"    -> {ttl_path.name} ({n_triples} triples)")

        if new_concepts:
            print(f"    {len(new_concepts)} new HINT concepts proposed")

    # Write thesaurus extensions
    if all_new_concepts:
        ext_ttl = generate_thesaurus_extensions(all_new_concepts)
        ext_path = OUTPUT_DIR / "hi-thesaurus-extensions.ttl"
        ext_path.write_text(ext_ttl, encoding='utf-8')
        print(f"\nNew HINT concepts written to {ext_path}")
        print(f"  ({len(all_new_concepts)} concepts - REVIEW BEFORE USING)")

    print(f"\nTotal triples generated: {total_triples}")
    print(f"Instance files in {INSTANCES_DIR}/")


if __name__ == "__main__":
    main()

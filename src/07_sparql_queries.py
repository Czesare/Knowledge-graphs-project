"""
Step 7: SPARQL Queries and KG Metrics

Usage:
    python 07_sparql_queries.py

Loads merged_kg.ttl, runs SPARQL queries,
computes KG metrics, prints results tables, and saves visualisations.

Queries are designed to address Competency Questions from the HI Ontology
(ESWC paper, Table 1) and satisfy the project rubric:
  - 4+ complex queries
  - 4+ triple patterns per query
  - Multiple SPARQL operators (GROUP BY, COUNT, OPTIONAL, FILTER,
    ORDER BY, HAVING, UNION, BIND, DISTINCT, CONCAT, SUBQUERY)
  - Visualisations of query results

Output:
    output/queries/   <- Query results as CSV + PNG charts
    output/metrics/   <- KG summary statistics + charts
"""
import sys
import csv
from pathlib import Path
from collections import Counter

try:
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("Install matplotlib: pip install matplotlib")
    raise

# ── Configuration ─────────────────────────────────────────────
try:
    from config import OUTPUT_DIR, HI_NS, HINT_NS, INST_NS
except ImportError:
    OUTPUT_DIR = Path("../output")
    HI_NS = "https://w3id.org/hi-ontology#"
    HINT_NS = "https://w3id.org/hi-thesaurus/"
    INST_NS = "https://w3id.org/hi-ontology/instances/"

HI = Namespace(HI_NS)
HINT = Namespace(HINT_NS)
INST = Namespace(INST_NS)

QUERIES_DIR = OUTPUT_DIR / "queries"
METRICS_DIR = OUTPUT_DIR / "metrics"

# ── Shared SPARQL prefixes ────────────────────────────────────
PREFIXES = """
PREFIX hi:   <https://w3id.org/hi-ontology#>
PREFIX hint: <https://w3id.org/hi-thesaurus/>
PREFIX inst: <https://w3id.org/hi-ontology/instances/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""


def short(uri) -> str:
    """Shorten a URI for display."""
    s = str(uri)
    for prefix, ns in [("inst:", INST_NS), ("hint:", HINT_NS),
                        ("hi:", HI_NS), ("skos:", str(SKOS))]:
        if s.startswith(ns):
            return prefix + s[len(ns):]
    return s.split("/")[-1].split("#")[-1]


def print_table(headers: list, rows: list, max_col_width: int = 45):
    """Pretty-print a table to the console."""
    # Truncate long values
    def trunc(v):
        s = str(v)
        return s[:max_col_width] + "…" if len(s) > max_col_width else s

    widths = [len(h) for h in headers]
    for row in rows:
        for i, v in enumerate(row):
            widths[i] = max(widths[i], len(trunc(v)))

    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["─" * w for w in widths]))
    for row in rows:
        print(fmt.format(*[trunc(v) for v in row]))


def save_csv(headers: list, rows: list, path: Path):
    """Save query results as CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


# ══════════════════════════════════════════════════════════════
# QUERY 1 — CQ1: Team Composition & Roles per Use Case
#
# "Given a use-case, how is the hybrid intelligence team composed,
#  and what roles do its agents assume?"
#
# SPARQL features: 5 triple patterns, OPTIONAL, BIND, CONCAT,
#                  GROUP BY, GROUP_CONCAT, COUNT, ORDER BY
# ══════════════════════════════════════════════════════════════
Q1_SPARQL = PREFIXES + """
SELECT ?ucLabel ?domain
       (COUNT(DISTINCT ?human) AS ?nHumans)
       (COUNT(DISTINCT ?ai)    AS ?nAIs)
       (GROUP_CONCAT(DISTINCT ?roleName; separator=", ") AS ?roles)
WHERE {
    ?uc a ?ucType ;
        rdfs:label ?ucLabel ;
        hi:hasDomainConcept ?domainConcept ;
        hi:hasHITeam ?team .
    ?domainConcept skos:prefLabel ?domain .

    VALUES ?ucType { hi:ResearchUseCase hi:CompetitionUseCase }

    ?team hi:hasMember ?agent .
    ?agent hi:hasRoleConcept ?role .
    ?role skos:prefLabel ?roleName .

    OPTIONAL { ?agent a hi:HumanAgent . BIND(?agent AS ?human) }
    OPTIONAL { ?agent a hi:ArtificialAgent . BIND(?agent AS ?ai) }
}
GROUP BY ?ucLabel ?domain
ORDER BY ?ucLabel
"""


def run_q1(g: Graph):
    print("\n" + "=" * 70)
    print("QUERY 1 — CQ1: Team Composition & Roles per Use Case")
    print("=" * 70)

    results = g.query(Q1_SPARQL)
    headers = ["Use Case", "Domain", "Humans", "AIs", "Roles"]
    rows = []
    for r in results:
        rows.append([str(r.ucLabel), str(r.domain),
                     str(r.nHumans), str(r.nAIs), str(r.roles)])

    print_table(headers, rows)
    save_csv(headers, rows, QUERIES_DIR / "q1_team_composition.csv")

    # Visualisation: stacked bar chart of human vs AI agents per use case
    if rows:
        labels = [r[0][:25] for r in rows]
        humans = [int(r[2]) for r in rows]
        ais = [int(r[3]) for r in rows]

        fig, ax = plt.subplots(figsize=(12, 6))
        x = range(len(labels))
        ax.bar(x, humans, label="Human Agents", color="#2196F3")
        ax.bar(x, ais, bottom=humans, label="AI Agents", color="#FF9800")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("Number of Agents")
        ax.set_title("Q1: Team Composition per Use Case (Human vs AI)")
        ax.legend()
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig(QUERIES_DIR / "q1_team_composition.png", dpi=150)
        plt.close()

    print(f"  → {len(rows)} results. Saved to queries/q1_team_composition.*")


# ══════════════════════════════════════════════════════════════
# QUERY 2 — CQ2/CQ3: Capability Distribution Across Papers
#
# "Given an agent's capabilities, which tasks can it perform?"
# Extended: Rank papers by the number of distinct capability
# concepts their agents collectively possess.
#
# SPARQL features: 6 triple patterns, COUNT(DISTINCT),
#                  GROUP BY, HAVING, ORDER BY DESC
# ══════════════════════════════════════════════════════════════
Q2_SPARQL = PREFIXES + """
SELECT ?paperTitle
       (COUNT(DISTINCT ?capConcept) AS ?nDistinctCapabilities)
       (COUNT(DISTINCT ?task) AS ?nTasks)
       (GROUP_CONCAT(DISTINCT ?capName; separator=", ") AS ?capabilities)
WHERE {
    ?paper a hi:Paper ;
           hi:hasTitle ?paperTitle ;
           hi:describesUseCase ?uc .
    ?uc hi:hasHITeam ?team .
    ?team hi:hasMember ?agent .
    ?agent hi:hasCapability ?cap .
    ?cap hi:hasCapabilityConcept ?capConcept .
    ?capConcept skos:prefLabel ?capName .

    OPTIONAL {
        ?cap hi:allowsTask ?task .
    }
}
GROUP BY ?paperTitle
HAVING (COUNT(DISTINCT ?capConcept) > 0)
ORDER BY DESC(?nDistinctCapabilities)
"""


def run_q2(g: Graph):
    print("\n" + "=" * 70)
    print("QUERY 2 — CQ2/CQ3: Capability Distribution Across Papers")
    print("=" * 70)

    results = g.query(Q2_SPARQL)
    headers = ["Paper", "#Capabilities", "#Tasks", "Capability Concepts"]
    rows = []
    for r in results:
        rows.append([str(r.paperTitle)[:50], str(r.nDistinctCapabilities),
                     str(r.nTasks), str(r.capabilities)])

    print_table(headers, rows)
    save_csv(headers, rows, QUERIES_DIR / "q2_capability_distribution.csv")

    # Visualisation: horizontal bar chart
    if rows:
        labels = [r[0][:35] for r in rows]
        caps = [int(r[1]) for r in rows]
        tasks = [int(r[2]) for r in rows]

        fig, ax = plt.subplots(figsize=(12, 6))
        y = range(len(labels))
        ax.barh(y, caps, label="Distinct Capabilities", color="#4CAF50")
        ax.barh(y, tasks, left=caps, label="Tasks Covered", color="#9C27B0", alpha=0.7)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("Count")
        ax.set_title("Q2: Capability Breadth and Task Coverage per Paper")
        ax.legend()
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig(QUERIES_DIR / "q2_capability_distribution.png", dpi=150)
        plt.close()

    print(f"  → {len(rows)} results. Saved to queries/q2_capability_distribution.*")


# ══════════════════════════════════════════════════════════════
# QUERY 3 — CQ9/CQ10: Cross-Use-Case Constraint & Phenomenon Analysis
#
# "Which constraints are shared across different use-cases?"
# Shows which ethical/safety constraints and contextual phenomena
# appear across multiple use cases, revealing common concerns.
#
# SPARQL features: UNION, 5+ triple patterns, COUNT, FILTER,
#                  GROUP BY, HAVING, ORDER BY DESC
# ══════════════════════════════════════════════════════════════
Q3_SPARQL = PREFIXES + """
SELECT ?conceptLabel ?conceptType
       (COUNT(DISTINCT ?uc) AS ?nUseCases)
       (GROUP_CONCAT(DISTINCT ?ucLabel; separator=", ") AS ?useCases)
WHERE {
    {
        ?uc hi:hasHITeam ?team .
        ?team hi:isInfluencedBy ?ctx .
        ?ctx hi:hasConstraintConcept ?concept .
        BIND("Constraint" AS ?conceptType)
    }
    UNION
    {
        ?uc hi:hasHITeam ?team .
        ?team hi:isInfluencedBy ?ctx .
        ?ctx hi:hasPhenomenonConcept ?concept .
        BIND("Phenomenon" AS ?conceptType)
    }

    ?concept skos:prefLabel ?conceptLabel .
    ?uc rdfs:label ?ucLabel .
}
GROUP BY ?conceptLabel ?conceptType
HAVING (COUNT(DISTINCT ?uc) >= 1)
ORDER BY DESC(?nUseCases) ?conceptType ?conceptLabel
"""


def run_q3(g: Graph):
    print("\n" + "=" * 70)
    print("QUERY 3 — CQ9/CQ10: Constraints & Phenomena Across Use Cases")
    print("=" * 70)

    results = g.query(Q3_SPARQL)
    headers = ["Concept", "Type", "#UseCases", "Use Cases"]
    rows = []
    for r in results:
        rows.append([str(r.conceptLabel), str(r.conceptType),
                     str(r.nUseCases), str(r.useCases)])

    print_table(headers, rows)
    save_csv(headers, rows, QUERIES_DIR / "q3_constraints_phenomena.csv")

    # Visualisation: grouped horizontal bar chart
    if rows:
        constraints = [(r[0][:30], int(r[2])) for r in rows if r[1] == "Constraint"]
        phenomena = [(r[0][:30], int(r[2])) for r in rows if r[1] == "Phenomenon"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        if constraints:
            c_labels, c_vals = zip(*sorted(constraints, key=lambda x: x[1]))
            ax1.barh(range(len(c_labels)), c_vals, color="#F44336")
            ax1.set_yticks(range(len(c_labels)))
            ax1.set_yticklabels(c_labels, fontsize=8)
            ax1.set_xlabel("# Use Cases")
            ax1.set_title("Constraints")
            ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        if phenomena:
            p_labels, p_vals = zip(*sorted(phenomena, key=lambda x: x[1]))
            ax2.barh(range(len(p_labels)), p_vals, color="#FF9800")
            ax2.set_yticks(range(len(p_labels)))
            ax2.set_yticklabels(p_labels, fontsize=8)
            ax2.set_xlabel("# Use Cases")
            ax2.set_title("Phenomena")
            ax2.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        fig.suptitle("Q3: Constraints & Phenomena Shared Across Use Cases", fontsize=13)
        plt.tight_layout()
        plt.savefig(QUERIES_DIR / "q3_constraints_phenomena.png", dpi=150)
        plt.close()

    print(f"  → {len(rows)} results. Saved to queries/q3_constraints_phenomena.*")


# ══════════════════════════════════════════════════════════════
# QUERY 4 — CQ5/CQ6: Interaction Patterns & Methods per Paper
#
# "What types of interactions occur between agents during
#  execution of a task, and which methods are used?"
#
# SPARQL features: 7+ triple patterns, OPTIONAL (×2), BIND,
#                  FILTER, GROUP BY, GROUP_CONCAT, ORDER BY
# ══════════════════════════════════════════════════════════════
Q4_SPARQL = PREFIXES + """
SELECT ?paperTitle ?interLabel ?modalityName ?intentName
       (GROUP_CONCAT(DISTINCT ?agentLabel; separator=" ↔ ") AS ?agents)
       ?methodName
WHERE {
    ?paper a hi:Paper ;
           hi:hasTitle ?paperTitle ;
           hi:describesUseCase ?uc .
    ?uc hi:hasHITeam ?team .

    # Interaction details
    ?team hi:hasMember ?memberAgent .
    ?inter a hi:Interaction ;
           rdfs:label ?interLabel ;
           hi:hasAgentInvolved ?memberAgent .
    ?inter hi:hasInteractionModalityConcept ?modality .
    ?modality skos:prefLabel ?modalityName .

    OPTIONAL {
        ?inter hi:hasInteractionIntentConcept ?intent .
        ?intent skos:prefLabel ?intentName .
    }

    # Agent labels
    ?memberAgent rdfs:label ?agentLabel .
    FILTER EXISTS { ?inter hi:hasAgentInvolved ?memberAgent }

    # Method from any execution in this use case
    OPTIONAL {
        ?exec a hi:TaskExecution ;
              hi:hasMethodConcept ?method .
        ?memberAgent hi:performsExecution ?exec .
        ?method skos:prefLabel ?methodName .
    }
}
GROUP BY ?paperTitle ?interLabel ?modalityName ?intentName ?methodName
ORDER BY ?paperTitle
"""


def run_q4(g: Graph):
    print("\n" + "=" * 70)
    print("QUERY 4 — CQ5/CQ6: Interaction Patterns & Methods")
    print("=" * 70)

    results = g.query(Q4_SPARQL)
    headers = ["Paper", "Interaction", "Modality", "Intent", "Agents", "Method"]
    rows = []
    for r in results:
        rows.append([
            str(r.paperTitle)[:40],
            str(r.interLabel)[:30],
            str(r.modalityName) if r.modalityName else "—",
            str(r.intentName) if r.intentName else "—",
            str(r.agents),
            str(r.methodName) if r.methodName else "—",
        ])

    print_table(headers, rows)
    save_csv(headers, rows, QUERIES_DIR / "q4_interactions_methods.csv")

    # Visualisation: modality frequency pie chart
    if rows:
        modalities = Counter(r[2] for r in rows if r[2] != "—")
        intents = Counter(r[3] for r in rows if r[3] != "—")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

        if modalities:
            ax1.pie(modalities.values(), labels=modalities.keys(),
                    autopct="%1.0f%%", startangle=90,
                    colors=plt.cm.Set3.colors)
            ax1.set_title("Interaction Modalities")

        if intents:
            ax2.pie(intents.values(), labels=intents.keys(),
                    autopct="%1.0f%%", startangle=90,
                    colors=plt.cm.Pastel1.colors)
            ax2.set_title("Interaction Intents")

        fig.suptitle("Q4: Interaction Modalities & Intents Across Papers", fontsize=13)
        plt.tight_layout()
        plt.savefig(QUERIES_DIR / "q4_interactions_methods.png", dpi=150)
        plt.close()

    print(f"  → {len(rows)} results. Saved to queries/q4_interactions_methods.*")


# ══════════════════════════════════════════════════════════════
# QUERY 5 — CQ8: Evaluation & Experiment Structure
#
# "Given a goal, which experiments test which metrics, and
#  what hypotheses do these experiments address?"
#
# Evaluations are joined through the explicit hi:evaluatedBy relation
# on task executions, rather than through URI naming conventions.
#
# SPARQL features: 6+ triple patterns, OPTIONAL (×3),
#                  DISTINCT, ORDER BY
# ══════════════════════════════════════════════════════════════
Q5_SPARQL = PREFIXES + """
SELECT DISTINCT ?paperTitle ?evalLabel ?expLabel ?metricName
       ?nullH ?altH
WHERE {
    ?paper a hi:Paper ;
           hi:hasTitle ?paperTitle ;
           hi:describesUseCase ?uc .
    ?uc hi:hasHITeam ?team .
    ?team hi:hasMember ?agent .
    ?agent hi:performsExecution ?exec .
    ?exec hi:evaluatedBy ?eval .

    ?eval a hi:Evaluation ;
           rdfs:label ?evalLabel ;
           hi:hasExperiment ?exp .
    ?exp rdfs:label ?expLabel .

    OPTIONAL {
        ?exp hi:hasMetricTested ?metric .
        ?metric skos:prefLabel ?metricName .
    }
    OPTIONAL { ?exp hi:hasNullHypothesis ?nullH }
    OPTIONAL { ?exp hi:hasAlternativeHypothesis ?altH }
}
ORDER BY ?paperTitle ?expLabel
"""


def run_q5(g: Graph):
    print("\n" + "=" * 70)
    print("QUERY 5 — CQ8: Evaluation & Experiment Structure")
    print("=" * 70)

    results = g.query(Q5_SPARQL)
    headers = ["Paper", "Evaluation", "Experiment", "Metric",
               "H₀ (Null)", "H₁ (Alt.)"]
    rows = []
    for r in results:
        rows.append([
            str(r.paperTitle)[:40],
            str(r.evalLabel)[:30],
            str(r.expLabel)[:30],
            str(r.metricName) if r.metricName else "—",
            str(r.nullH)[:50] if r.nullH else "—",
            str(r.altH)[:50] if r.altH else "—",
        ])

    print_table(headers, rows)

    save_csv(headers, rows, QUERIES_DIR / "q5_evaluations.csv")
    print(f"  → {len(rows)} results. Saved to queries/q5_evaluations.*")


# ══════════════════════════════════════════════════════════════
# KG METRICS — Summary Statistics
# ══════════════════════════════════════════════════════════════
def compute_metrics(g: Graph):
    print("\n" + "=" * 70)
    print("KG METRICS — Summary Statistics")
    print("=" * 70)

    # Basic counts
    classes = {
        "Paper": HI.Paper, "Author": HI.Author, "Conference": HI.Conference,
        "Affiliation": HI.Affiliation, "ResearchUseCase": HI.ResearchUseCase,
        "CompetitionUseCase": HI.CompetitionUseCase, "HITeam": HI.HITeam,
        "HumanAgent": HI.HumanAgent, "ArtificialAgent": HI.ArtificialAgent,
        "Capability": HI.Capability, "Goal": HI.Goal, "Task": HI.Task,
        "TaskExecution": HI.TaskExecution, "Interaction": HI.Interaction,
        "Evaluation": HI.Evaluation, "Experiment": HI.Experiment,
        "Context": HI.Context,
    }

    print("\n  Instance counts:")
    counts = {}
    for name, cls in classes.items():
        n = len(list(g.subjects(RDF.type, cls)))
        counts[name] = n
        print(f"    {name:25s} {n:4d}")
    print(f"    {'TOTAL':25s} {sum(counts.values()):4d}")

    # External links
    link_types = {
        "owl:sameAs": OWL.sameAs,
        "skos:closeMatch": SKOS.closeMatch,
        "skos:relatedMatch": SKOS.relatedMatch,
        "rdfs:seeAlso": RDFS.seeAlso,
    }
    print("\n  External links:")
    link_counts = {}
    for name, pred in link_types.items():
        n = len(list(g.triples((None, pred, None))))
        link_counts[name] = n
        print(f"    {name:25s} {n:4d}")
    print(f"    {'TOTAL':25s} {sum(link_counts.values()):4d}")

    # Total triples
    print(f"\n  Total triples: {len(g)}")

    # Property usage distribution
    print("\n  Top 15 properties by usage:")
    prop_counts = Counter()
    for _, p, _ in g:
        prop_counts[short(p)] += 1
    for prop, cnt in prop_counts.most_common(15):
        print(f"    {prop:45s} {cnt:5d}")

    # Visualisation: class distribution bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Instance counts
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    names = [c[0] for c in sorted_counts if c[1] > 0]
    vals = [c[1] for c in sorted_counts if c[1] > 0]
    ax1.barh(range(len(names)), vals, color="#3F51B5")
    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names, fontsize=9)
    ax1.set_xlabel("Count")
    ax1.set_title("Instance Distribution by Class")
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Top properties
    top_props = prop_counts.most_common(12)
    p_names = [p[0][:30] for p in top_props]
    p_vals = [p[1] for p in top_props]
    ax2.barh(range(len(p_names)), p_vals, color="#009688")
    ax2.set_yticks(range(len(p_names)))
    ax2.set_yticklabels(p_names, fontsize=8)
    ax2.set_xlabel("Usage Count")
    ax2.set_title("Top Properties by Usage")
    ax2.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.tight_layout()
    plt.savefig(METRICS_DIR / "kg_summary.png", dpi=150)
    plt.close()

    # Save metrics as CSV
    save_csv(["Class", "Count"], list(counts.items()),
             METRICS_DIR / "instance_counts.csv")
    save_csv(["Link Type", "Count"], list(link_counts.items()),
             METRICS_DIR / "external_links.csv")

    print(f"\n  → Saved to metrics/kg_summary.png, instance_counts.csv")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    QUERIES_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # Locate merged KG
    candidates = [
        OUTPUT_DIR / "merged_kg.ttl",
        Path("merged_kg.ttl"),
    ]
    kg_file = None
    for c in candidates:
        if c.exists():
            kg_file = c
            break

    if not kg_file:
        if len(sys.argv) > 1:
            kg_file = Path(sys.argv[1])
        if not kg_file or not kg_file.exists():
            print("ERROR: Cannot find merged KG. Provide path as argument.")
            sys.exit(1)

    print(f"Loading {kg_file}...")
    g = Graph()
    g.parse(str(kg_file), format="turtle")
    print(f"Loaded {len(g)} triples.\n")

    # Run queries
    run_q1(g)
    run_q2(g)
    run_q3(g)
    run_q4(g)
    run_q5(g)

    # Compute metrics
    compute_metrics(g)

    print("\n" + "=" * 70)
    print("Done! All query results and charts saved in:")
    print(f"  {QUERIES_DIR}/")
    print(f"  {METRICS_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Step 8: KG Metrics, Graph Analysis, and Visualisation

Usage:
    python 08_kg_metrics.py

Loads merged_kg.ttl, computes ontology-level and graph-level metrics,
performs community detection, and produces visualisations.

Aligned with the KGmeasures-tutorial.ipynb from the course:
  Section 1 — Basic ontology measures (classes, properties, individuals, triples)
  Section 2 — RDF → NetworkX conversion (URI-only, no blank nodes/literals)
  Section 3 — Graph measures (nodes, edges, density, degree distribution,
              centrality, clustering coefficient, connected components)
  Section 4 — Graph visualisation (colour-coded by node type)
  Section 5 — Louvain community detection

Output:
    output/metrics/
      ├── basic_measures.txt          <- Ontology-level counts
      ├── graph_measures.txt          <- NetworkX graph statistics
      ├── degree_distribution.png     <- Degree histogram
      ├── centrality_top20.png        <- Top 20 PageRank bar chart
      ├── centrality_rankplot.png     <- PageRank log-log rank plot
      ├── node_type_distribution.png  <- Pie chart by node type
      ├── graph_visualisation.png     <- Colour-coded graph
      ├── communities.png             <- Louvain community graph
      └── communities.txt             <- Community membership details
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict

try:
    from rdflib import Graph as RDFGraph, Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD
    from rdflib.term import BNode
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise

try:
    import networkx as nx
    import networkx.algorithms.community as nx_comm
except ImportError:
    print("Install networkx: pip install networkx")
    raise

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np
except ImportError:
    print("Install matplotlib numpy: pip install matplotlib numpy")
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

METRICS_DIR = OUTPUT_DIR / "metrics"


def short(uri) -> str:
    """Shorten a URI for display."""
    s = str(uri)
    for prefix, ns in [("inst:", INST_NS), ("hint:", HINT_NS),
                        ("hi:", HI_NS), ("skos:", str(SKOS)),
                        ("owl:", str(OWL)), ("rdfs:", str(RDFS)),
                        ("rdf:", str(RDF))]:
        if s.startswith(ns):
            return prefix + s[len(ns):]
    if "#" in s:
        return s.split("#")[-1]
    return s.rstrip("/").split("/")[-1]


# ══════════════════════════════════════════════════════════════
# SECTION 1: Basic Ontology Measures
# (Tutorial Section 1 — Exercise 1)
# ══════════════════════════════════════════════════════════════
def basic_measures(g: RDFGraph) -> dict:
    """Compute basic ontology-level measures using SPARQL."""
    print("=" * 70)
    print("SECTION 1 — Basic Ontology Measures")
    print("=" * 70)

    measures = {}

    # Number of classes
    q = "SELECT DISTINCT ?s WHERE { ?s rdf:type owl:Class . FILTER(isURI(?s)) }"
    classes = list(g.query(q))
    measures["classes"] = len(classes)

    # Number of object properties
    q = "SELECT DISTINCT ?s WHERE { ?s rdf:type owl:ObjectProperty . FILTER(isURI(?s)) }"
    obj_props = list(g.query(q))
    measures["object_properties"] = len(obj_props)

    # Number of datatype properties
    q = "SELECT DISTINCT ?s WHERE { ?s rdf:type owl:DatatypeProperty . FILTER(isURI(?s)) }"
    data_props = list(g.query(q))
    measures["datatype_properties"] = len(data_props)

    # Number of individuals (NamedIndividual or typed instances)
    q = """SELECT DISTINCT ?s WHERE {
        ?s rdf:type ?t .
        FILTER(isURI(?s) && isURI(?t))
        FILTER(?t != owl:Class && ?t != owl:ObjectProperty &&
               ?t != owl:DatatypeProperty && ?t != owl:Ontology &&
               ?t != owl:AnnotationProperty && ?t != owl:FunctionalProperty &&
               ?t != owl:TransitiveProperty)
        FILTER(!STRSTARTS(STR(?t), "http://www.w3.org/2002/07/owl#"))
        FILTER(!STRSTARTS(STR(?t), "http://www.w3.org/2000/01/rdf-schema#"))
    }"""
    individuals = list(g.query(q))
    measures["individuals"] = len(individuals)

    # Number of triples
    measures["triples"] = len(g)

    # Number of unique entities (anything in subject position)
    q = "SELECT DISTINCT ?s WHERE { ?s ?p ?o . FILTER(isURI(?s)) }"
    entities = list(g.query(q))
    measures["entities"] = len(entities)

    # Number of blank nodes
    bnodes = set()
    for s, p, o in g:
        if isinstance(s, BNode):
            bnodes.add(s)
        if isinstance(o, BNode):
            bnodes.add(o)
    measures["blank_nodes"] = len(bnodes)

    # SKOS concepts
    q = "SELECT DISTINCT ?s WHERE { ?s rdf:type <http://www.w3.org/2004/02/skos/core#Concept> . }"
    concepts = list(g.query(q))
    measures["skos_concepts"] = len(concepts)

    # Print results
    print(f"\n  Classes (owl:Class):             {measures['classes']}")
    print(f"  Object Properties:               {measures['object_properties']}")
    print(f"  Datatype Properties:             {measures['datatype_properties']}")
    print(f"  Individuals:                     {measures['individuals']}")
    print(f"  SKOS Concepts:                   {measures['skos_concepts']}")
    print(f"  Unique Entities (URI subjects):  {measures['entities']}")
    print(f"  Blank Nodes:                     {measures['blank_nodes']}")
    print(f"  Total Triples:                   {measures['triples']}")

    # Instance breakdown per class (top-level HI classes)
    hi_classes = {
        "Paper": HI.Paper, "Author": HI.Author, "Conference": HI.Conference,
        "Affiliation": HI.Affiliation, "ResearchUseCase": HI.ResearchUseCase,
        "CompetitionUseCase": HI.CompetitionUseCase, "HITeam": HI.HITeam,
        "HumanAgent": HI.HumanAgent, "ArtificialAgent": HI.ArtificialAgent,
        "Capability": HI.Capability, "Goal": HI.Goal, "Task": HI.Task,
        "TaskExecution": HI.TaskExecution, "Interaction": HI.Interaction,
        "Evaluation": HI.Evaluation, "Experiment": HI.Experiment,
        "Context": HI.Context,
    }
    print("\n  Instance breakdown (HI classes):")
    class_counts = {}
    for name, cls in hi_classes.items():
        n = len(set(g.subjects(RDF.type, cls)))
        class_counts[name] = n
        print(f"    {name:25s} {n:4d}")
    measures["class_counts"] = class_counts

    # Visualise: node type pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    labels = [k for k, v in class_counts.items() if v > 0]
    sizes = [v for v in class_counts.values() if v > 0]
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.0f%%", startangle=90,
        colors=colors, pctdistance=0.85)
    for t in texts:
        t.set_fontsize(9)
    for t in autotexts:
        t.set_fontsize(7)
    ax.set_title("Instance Distribution by HI Ontology Class", fontsize=13)
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "node_type_distribution.png", dpi=150)
    plt.close()

    # Save to text file
    with open(METRICS_DIR / "basic_measures.txt", "w") as f:
        for k, v in measures.items():
            if k != "class_counts":
                f.write(f"{k}: {v}\n")
        f.write("\nClass breakdown:\n")
        for k, v in class_counts.items():
            f.write(f"  {k}: {v}\n")

    print(f"\n  → Saved to metrics/basic_measures.txt, node_type_distribution.png")
    return measures


# ══════════════════════════════════════════════════════════════
# SECTION 2: Convert RDF to NetworkX
# (Tutorial Section 2 — URI-only, no blank nodes/literals)
# ══════════════════════════════════════════════════════════════
def rdf_to_networkx(g: RDFGraph) -> nx.DiGraph:
    """
    Convert RDF graph to a NetworkX DiGraph.
    Keep only URI → URI edges (drop literals and blank nodes).
    This follows the tutorial's recommendation for graph analysis.
    """
    print("\n" + "=" * 70)
    print("SECTION 2 — RDF to NetworkX Conversion")
    print("=" * 70)

    G = nx.DiGraph()
    skipped_literals = 0
    skipped_bnodes = 0

    for s, p, o in g:
        if isinstance(o, Literal):
            skipped_literals += 1
            continue
        if isinstance(s, BNode) or isinstance(o, BNode):
            skipped_bnodes += 1
            continue
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            G.add_edge(s, o, predicate=p)

    print(f"\n  URI-only DiGraph:")
    print(f"    Nodes:             {G.number_of_nodes()}")
    print(f"    Edges:             {G.number_of_edges()}")
    print(f"    Skipped literals:  {skipped_literals}")
    print(f"    Skipped BNodes:    {skipped_bnodes}")

    return G


# ══════════════════════════════════════════════════════════════
# SECTION 3: Graph Measures
# (Tutorial Section 3 — density, degree, centrality, clustering)
# ══════════════════════════════════════════════════════════════
def graph_measures(G: nx.DiGraph):
    """Compute graph-theoretic measures on the NetworkX graph."""
    print("\n" + "=" * 70)
    print("SECTION 3 — Graph Measures")
    print("=" * 70)

    report = []

    # ── Basic measures ────────────────────────────────────────
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    density = nx.density(G)
    print(f"\n  Nodes:    {n_nodes}")
    print(f"  Edges:    {n_edges}")
    print(f"  Density:  {density:.6f}")
    report.append(f"nodes: {n_nodes}")
    report.append(f"edges: {n_edges}")
    report.append(f"density: {density:.6f}")

    # ── Degree distribution ───────────────────────────────────
    degrees = dict(G.degree())
    degree_values = list(degrees.values())
    mean_degree = np.mean(degree_values)
    median_degree = np.median(degree_values)
    max_degree = max(degree_values)
    min_degree = min(degree_values)

    print(f"\n  Degree statistics:")
    print(f"    Mean:    {mean_degree:.2f}")
    print(f"    Median:  {median_degree:.1f}")
    print(f"    Min:     {min_degree}")
    print(f"    Max:     {max_degree}")
    report.append(f"mean_degree: {mean_degree:.2f}")
    report.append(f"median_degree: {median_degree:.1f}")
    report.append(f"max_degree: {max_degree}")

    # In/out degree for directed graph
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    mean_in = np.mean(list(in_degrees.values()))
    mean_out = np.mean(list(out_degrees.values()))
    print(f"    Mean in-degree:  {mean_in:.2f}")
    print(f"    Mean out-degree: {mean_out:.2f}")
    report.append(f"mean_in_degree: {mean_in:.2f}")
    report.append(f"mean_out_degree: {mean_out:.2f}")

    # Degree histogram
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Total degree
    axes[0].hist(degree_values, bins=30, color="#3F51B5", edgecolor="white")
    axes[0].axvline(mean_degree, color="red", linestyle="--",
                    label=f"Mean: {mean_degree:.1f}")
    axes[0].set_xlabel("Degree")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title("Total Degree Distribution")
    axes[0].legend()

    # In-degree
    axes[1].hist(list(in_degrees.values()), bins=30, color="#4CAF50",
                 edgecolor="white")
    axes[1].axvline(mean_in, color="red", linestyle="--",
                    label=f"Mean: {mean_in:.1f}")
    axes[1].set_xlabel("In-Degree")
    axes[1].set_title("In-Degree Distribution")
    axes[1].legend()

    # Out-degree
    axes[2].hist(list(out_degrees.values()), bins=30, color="#FF9800",
                 edgecolor="white")
    axes[2].axvline(mean_out, color="red", linestyle="--",
                    label=f"Mean: {mean_out:.1f}")
    axes[2].set_xlabel("Out-Degree")
    axes[2].set_title("Out-Degree Distribution")
    axes[2].legend()

    plt.suptitle("Degree Distributions (URI-only graph)", fontsize=13)
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "degree_distribution.png", dpi=150)
    plt.close()

    # ── Degree centrality ─────────────────────────────────────
    deg_centrality = nx.degree_centrality(G)
    mean_deg_cent = np.mean(list(deg_centrality.values()))
    print(f"\n  Mean degree centrality: {mean_deg_cent:.6f}")
    report.append(f"mean_degree_centrality: {mean_deg_cent:.6f}")

    # ── PageRank centrality ───────────────────────────────────
    print("\n  PageRank (top 20):")
    pr = nx.pagerank(G, alpha=0.85, max_iter=200, tol=1e-6)
    top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:20]
    for i, (node, val) in enumerate(top_pr, 1):
        print(f"    {i:2d}. {short(node):45s} {val:.6f}")

    # PageRank bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    labels = [short(n)[:30] for n, _ in top_pr]
    values = [v for _, v in top_pr]
    ax.bar(range(len(labels)), values, color="#009688")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=8)
    ax.set_ylabel("PageRank Score")
    ax.set_title("Top 20 Nodes by PageRank Centrality")
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "centrality_top20.png", dpi=150)
    plt.close()

    # PageRank rank plot (log-log)
    vals_sorted = np.sort(np.array(list(pr.values())))[::-1]
    ranks = np.arange(1, len(vals_sorted) + 1)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ranks, vals_sorted, linewidth=1.5, color="#E91E63")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Rank")
    ax.set_ylabel("PageRank")
    ax.set_title("PageRank Rank Plot (log-log)")
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "centrality_rankplot.png", dpi=150)
    plt.close()

    # ── Clustering coefficient ────────────────────────────────
    # Need undirected graph for clustering coefficient
    G_undir = G.to_undirected()
    avg_clustering = nx.average_clustering(G_undir)
    print(f"\n  Average clustering coefficient: {avg_clustering:.6f}")
    report.append(f"avg_clustering_coefficient: {avg_clustering:.6f}")

    # ── Connected components ──────────────────────────────────
    n_wcc = nx.number_weakly_connected_components(G)
    wcc_list = list(nx.weakly_connected_components(G))
    largest_wcc = max(wcc_list, key=len)
    print(f"\n  Weakly connected components: {n_wcc}")
    print(f"  Largest WCC size: {len(largest_wcc)} "
          f"({len(largest_wcc)/n_nodes:.1%} of nodes)")
    report.append(f"weakly_connected_components: {n_wcc}")
    report.append(f"largest_wcc_size: {len(largest_wcc)}")
    report.append(f"largest_wcc_pct: {len(largest_wcc)/n_nodes:.4f}")

    n_scc = nx.number_strongly_connected_components(G)
    scc_list = list(nx.strongly_connected_components(G))
    largest_scc = max(scc_list, key=len)
    print(f"  Strongly connected components: {n_scc}")
    print(f"  Largest SCC size: {len(largest_scc)} "
          f"({len(largest_scc)/n_nodes:.1%} of nodes)")
    report.append(f"strongly_connected_components: {n_scc}")
    report.append(f"largest_scc_size: {len(largest_scc)}")

    # Save report
    with open(METRICS_DIR / "graph_measures.txt", "w") as f:
        for line in report:
            f.write(line + "\n")

    print(f"\n  → Saved to metrics/graph_measures.txt, degree_distribution.png,")
    print(f"    centrality_top20.png, centrality_rankplot.png")

    return pr, G_undir


# ══════════════════════════════════════════════════════════════
# SECTION 4: Graph Visualisation
# (Tutorial Section 4 — colour-coded by node type)
# ══════════════════════════════════════════════════════════════
def visualise_graph(G: nx.DiGraph, g_rdf: RDFGraph):
    """Visualise a subgraph of the KG, colour-coded by node type."""
    print("\n" + "=" * 70)
    print("SECTION 4 — Graph Visualisation")
    print("=" * 70)

    # Classify nodes by type
    classes_set = set(g_rdf.subjects(RDF.type, OWL.Class))
    properties_set = set(g_rdf.subjects(RDF.type, OWL.ObjectProperty)) | \
                     set(g_rdf.subjects(RDF.type, OWL.DatatypeProperty))
    concepts_set = set(g_rdf.subjects(RDF.type, SKOS.Concept))

    # Instance types from the HI ontology
    instance_types = {}
    for cls_name, cls_uri in [
        ("Paper", HI.Paper), ("Author", HI.Author),
        ("HITeam", HI.HITeam), ("Agent", HI.HumanAgent),
        ("Agent", HI.ArtificialAgent), ("Task", HI.Task),
        ("Capability", HI.Capability), ("Goal", HI.Goal),
        ("UseCase", HI.ResearchUseCase), ("UseCase", HI.CompetitionUseCase),
        ("Evaluation", HI.Evaluation), ("Interaction", HI.Interaction),
        ("Context", HI.Context), ("Affiliation", HI.Affiliation),
    ]:
        for s in g_rdf.subjects(RDF.type, cls_uri):
            instance_types[s] = cls_name

    def node_kind(n):
        if n in classes_set:
            return "class"
        if n in properties_set:
            return "property"
        if n in concepts_set:
            return "concept"
        if n in instance_types:
            return instance_types[n]
        return "other"

    # Build a subgraph of inst: nodes only (manageable size)
    inst_nodes = [n for n in G.nodes() if str(n).startswith(INST_NS)]
    SG = G.subgraph(inst_nodes).copy()

    print(f"  Subgraph (inst: nodes only): {SG.number_of_nodes()} nodes, "
          f"{SG.number_of_edges()} edges")

    if SG.number_of_nodes() == 0:
        print("  No inst: nodes found, skipping visualisation.")
        return

    # Colour mapping
    kind_colors = {
        "Paper": "#1f77b4", "Author": "#aec7e8", "Affiliation": "#c5b0d5",
        "HITeam": "#ff7f0e", "Agent": "#2ca02c", "Task": "#d62728",
        "Capability": "#9467bd", "Goal": "#8c564b",
        "UseCase": "#e377c2", "Evaluation": "#7f7f7f",
        "Interaction": "#bcbd22", "Context": "#17becf",
        "class": "#1f77b4", "property": "#ff7f0e", "concept": "#98df8a",
        "other": "#cccccc",
    }

    node_colors = [kind_colors.get(node_kind(n), "#cccccc") for n in SG.nodes()]
    node_labels = {n: short(n)[:20] for n in SG.nodes()}

    fig, ax = plt.subplots(figsize=(18, 14))
    pos = nx.spring_layout(SG, seed=42, k=1.5, iterations=80)

    nx.draw_networkx_nodes(SG, pos, node_size=60, node_color=node_colors,
                           alpha=0.85, ax=ax)
    nx.draw_networkx_edges(SG, pos, width=0.3, alpha=0.3, edge_color="#888",
                           arrows=True, arrowsize=5, ax=ax)

    # Label only high-degree nodes
    degree_threshold = sorted(dict(SG.degree()).values(), reverse=True)
    cutoff = degree_threshold[min(30, len(degree_threshold) - 1)]
    labels_to_show = {n: l for n, l in node_labels.items()
                      if SG.degree(n) >= cutoff}
    nx.draw_networkx_labels(SG, pos, labels_to_show, font_size=6, ax=ax)

    # Legend
    from matplotlib.patches import Patch
    seen_kinds = set(node_kind(n) for n in SG.nodes())
    legend_elements = [Patch(facecolor=kind_colors.get(k, "#ccc"), label=k)
                       for k in sorted(seen_kinds) if k in kind_colors]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=8)

    ax.set_title("HI Knowledge Graph — Instance Subgraph (colour by type)",
                 fontsize=13)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "graph_visualisation.png", dpi=150,
                bbox_inches="tight")
    plt.close()

    print(f"  → Saved to metrics/graph_visualisation.png")


# ══════════════════════════════════════════════════════════════
# SECTION 5: Louvain Community Detection
# (Tutorial Section 5)
# ══════════════════════════════════════════════════════════════
def community_detection(G: nx.DiGraph, g_rdf: RDFGraph):
    """Run Louvain community detection on the KG."""
    print("\n" + "=" * 70)
    print("SECTION 5 — Louvain Community Detection")
    print("=" * 70)

    # Work on the largest weakly connected component (undirected)
    G_undir = G.to_undirected()

    # Keep only inst: and hint: nodes for meaningful clustering
    # (schema nodes like owl:Class pollute the clustering)
    relevant = [n for n in G_undir.nodes()
                if str(n).startswith(INST_NS) or str(n).startswith(HINT_NS)]
    SG = G_undir.subgraph(relevant).copy()

    # Remove isolates
    isolates = list(nx.isolates(SG))
    SG.remove_nodes_from(isolates)

    print(f"\n  Clustering graph (inst: + hint: nodes, no isolates):")
    print(f"    Nodes: {SG.number_of_nodes()}")
    print(f"    Edges: {SG.number_of_edges()}")
    print(f"    Removed {len(isolates)} isolates")

    if SG.number_of_nodes() == 0:
        print("  No nodes to cluster.")
        return

    # Louvain communities
    communities = nx_comm.louvain_communities(SG, resolution=1.0, seed=42)
    n_communities = len(communities)
    sizes = sorted([len(c) for c in communities], reverse=True)

    # Modularity
    modularity = nx_comm.modularity(SG, communities)

    print(f"\n  Communities found: {n_communities}")
    print(f"  Modularity:       {modularity:.4f}")
    print(f"  Top 10 community sizes: {sizes[:10]}")

    # Show composition of top communities
    # Determine node types
    hi_types = {}
    for cls_name, cls_uri in [
        ("Paper", HI.Paper), ("Author", HI.Author),
        ("HITeam", HI.HITeam), ("HumanAgent", HI.HumanAgent),
        ("ArtificialAgent", HI.ArtificialAgent), ("Task", HI.Task),
        ("Capability", HI.Capability), ("Goal", HI.Goal),
        ("UseCase", HI.ResearchUseCase), ("UseCase", HI.CompetitionUseCase),
        ("Evaluation", HI.Evaluation), ("Experiment", HI.Experiment),
        ("Interaction", HI.Interaction), ("Context", HI.Context),
        ("Affiliation", HI.Affiliation), ("Conference", HI.Conference),
    ]:
        for s in g_rdf.subjects(RDF.type, cls_uri):
            hi_types[s] = cls_name

    lines = []
    sorted_communities = sorted(communities, key=len, reverse=True)

    for i, comm in enumerate(sorted_communities[:8], 1):
        print(f"\n  Community {i} ({len(comm)} nodes):")
        type_counts = Counter()
        sample_labels = []
        for n in comm:
            t = hi_types.get(n, "SKOS Concept" if str(n).startswith(HINT_NS) else "Other")
            type_counts[t] += 1
            label_list = list(g_rdf.objects(n, RDFS.label))
            lbl = str(label_list[0]) if label_list else short(n)
            sample_labels.append(lbl)

        for t, c in type_counts.most_common():
            print(f"    {t}: {c}")
        print(f"    Sample: {', '.join(sample_labels[:5])}")

        lines.append(f"Community {i} ({len(comm)} nodes)")
        for t, c in type_counts.most_common():
            lines.append(f"  {t}: {c}")
        lines.append(f"  Sample: {', '.join(sample_labels[:5])}")
        lines.append("")

    # Save community report
    with open(METRICS_DIR / "communities.txt", "w", encoding="utf-8") as f:
        f.write(f"Communities: {n_communities}\n")
        f.write(f"Modularity: {modularity:.4f}\n")
        f.write(f"Sizes: {sizes}\n\n")
        f.write("\n".join(lines))

    # Visualise communities
    fig, ax = plt.subplots(figsize=(16, 12))

    # Use only the top communities for visibility
    top_communities = sorted_communities[:min(12, len(sorted_communities))]
    top_nodes = set()
    for c in top_communities:
        top_nodes.update(c)
    VSG = SG.subgraph(top_nodes).copy()

    pos = nx.spring_layout(VSG, seed=42, k=1.2, iterations=60)

    # Assign colors per community
    cmap = plt.cm.Set3(np.linspace(0, 1, len(top_communities)))
    node2cid = {}
    for cid, comm in enumerate(top_communities):
        for n in comm:
            node2cid[n] = cid

    node_colors = [cmap[node2cid.get(n, 0)] for n in VSG.nodes()]

    nx.draw_networkx_nodes(VSG, pos, node_size=40, node_color=node_colors,
                           alpha=0.8, ax=ax)
    nx.draw_networkx_edges(VSG, pos, width=0.2, alpha=0.2,
                           edge_color="#888", arrows=False, ax=ax)

    # Label community centres
    for cid, comm in enumerate(top_communities[:6]):
        comm_nodes = [n for n in comm if n in pos]
        if comm_nodes:
            cx = np.mean([pos[n][0] for n in comm_nodes])
            cy = np.mean([pos[n][1] for n in comm_nodes])
            ax.annotate(f"C{cid+1}\n({len(comm)})",
                       xy=(cx, cy), fontsize=9, fontweight="bold",
                       ha="center", va="center",
                       bbox=dict(boxstyle="round,pad=0.3",
                                facecolor="white", alpha=0.8))

    ax.set_title(f"Louvain Communities ({n_communities} communities, "
                 f"modularity={modularity:.3f})", fontsize=13)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "communities.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"\n  → Saved to metrics/communities.txt, communities.png")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # Locate merged KG
    candidates = [
        OUTPUT_DIR / "merged_kg.ttl",
        OUTPUT_DIR / "merged_kg_a2.ttl",
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
    g = RDFGraph()
    g.parse(str(kg_file), format="turtle")
    print(f"Loaded {len(g)} triples.\n")

    # Section 1: Basic measures
    basic_measures(g)

    # Section 2: Convert to NetworkX
    G = rdf_to_networkx(g)

    # Section 3: Graph measures
    pr, G_undir = graph_measures(G)

    # Section 4: Visualisation
    visualise_graph(G, g)

    # Section 5: Community detection
    community_detection(G, g)

    print("\n" + "=" * 70)
    print("Done! All metrics and charts saved in:")
    print(f"  {METRICS_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Step 9: KG Embeddings, Link Prediction & Embedding Visualisation

Usage:
    python 09_kg_embeddings.py

Aligned with the ML4KG-tutorial.ipynb from the course (Exercise 7):
  1. Load the HI KG as triples
  2. Train/test split
  3. Train multiple KG embedding models (ComplEx, TransE, DistMult)
  4. Evaluate: MRR, Hits@1, Hits@3, Hits@10
  5. Link Prediction: predict and score unseen triples
  6. Embedding Visualisation: PCA + t-SNE coloured by entity type
  7. Optional: Cluster embeddings
  8. Ablation: compare training on own KG vs combined KG
     (with hi-ontology-populated.ttl from all student groups)

Dependencies:
    pip install pykeen torch scikit-learn matplotlib numpy pandas

Output:
    output/embeddings/
      ├── triples.tsv                <- Raw triples (own KG)
      ├── model_comparison.csv       <- MRR/Hits@k for each model (own KG)
      ├── model_comparison.png       <- Bar chart comparing models
      ├── loss_curves.png            <- Training loss curves
      ├── link_predictions.csv       <- Top predicted missing links
      ├── link_predictions_scored.csv <- Candidate triples with scores
      ├── embeddings_pca.png         <- PCA projection by entity type
      ├── embeddings_tsne.png        <- t-SNE projection by entity type
      ├── embedding_clusters.png     <- Clustered embeddings
      ├── combined_kg_for_training.ttl <- Combined KG (own + populated)
      ├── ablation_comparison.csv    <- Own vs Combined results
      └── ablation_comparison.png    <- Ablation bar chart
"""
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import torch
    from pykeen.triples import TriplesFactory
    from pykeen.pipeline import pipeline
    from pykeen import predict as pk_predict
except ImportError:
    print("Install pykeen: pip install pykeen")
    print("  (requires torch: pip install torch)")
    raise

try:
    from rdflib import Graph as RDFGraph, Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, OWL, SKOS
    from rdflib.term import BNode
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.cluster import KMeans
except ImportError:
    print("Install: pip install matplotlib scikit-learn")
    raise

from scipy.special import expit

warnings.filterwarnings("ignore", category=FutureWarning)

# ── Configuration ─────────────────────────────────────────────
try:
    from config import OUTPUT_DIR, HI_NS, HINT_NS, INST_NS
except ImportError:
    OUTPUT_DIR = Path("../output")
    HI_NS = "https://w3id.org/hi-ontology#"
    HINT_NS = "https://w3id.org/hi-thesaurus/"
    INST_NS = "https://w3id.org/hi-ontology/instances/"

EMB_DIR = OUTPUT_DIR / "embeddings"

# Models to compare (as in tutorial: try multiple)
MODELS_TO_TRAIN = ["ComplEx", "TransE", "DistMult"]

# Training hyperparameters
NUM_EPOCHS = 200
EMBEDDING_DIM = 150
LEARNING_RATE = 1e-3


def short(uri_str: str) -> str:
    """Shorten a URI for display."""
    s = str(uri_str)
    for prefix, ns in [("inst:", INST_NS), ("hint:", HINT_NS),
                        ("hi:", HI_NS), ("skos:", str(SKOS)),
                        ("owl:", str(OWL))]:
        if s.startswith(ns):
            return prefix + s[len(ns):]
    if "#" in s:
        return s.split("#")[-1]
    return s.rstrip("/").split("/")[-1]


def entity_type(uri_str: str) -> str:
    """Classify an entity URI by type for visualisation colouring."""
    s = str(uri_str)
    if "/instances/" in s:
        local = s.split("/instances/")[-1]
        if local.startswith("Paper") and "_" not in local:
            return "Paper"
        if "_Author" in local:
            return "Author"
        if "Affiliation_" in local:
            return "Affiliation"
        if "_Team" in local:
            return "HITeam"
        if "Agent" in local or "_Ai" in local or "Robot" in local:
            return "Agent"
        if "_Task_" in local:
            return "Task"
        if "_Cap_" in local or "Capability" in local:
            return "Capability"
        if "_Goal_" in local:
            return "Goal"
        if "_UseCase" in local:
            return "UseCase"
        if "_Eval" in local:
            return "Evaluation"
        if "_Exp" in local or "Experiment" in local:
            return "Experiment"
        if "_Interaction" in local:
            return "Interaction"
        if "_Context" in local:
            return "Context"
        if "_Exec_" in local:
            return "TaskExecution"
        if "Keyword_" in local:
            return "Keyword"
        if "HHAI" in local:
            return "Conference"
        return "Instance(other)"
    if "/hi-thesaurus/" in s:
        return "HINT Concept"
    if "/hi-ontology#" in s:
        return "Schema"
    if "w3.org" in s:
        return "Schema"
    return "Other"


# ══════════════════════════════════════════════════════════════
# SECTION 1: Load KG as Triples
# ══════════════════════════════════════════════════════════════
def load_triples(kg_file: Path) -> tuple[np.ndarray, RDFGraph]:
    """
    Load the KG and extract (subject, predicate, object) triples.
    Keep only URI→URI edges (drop literals and blank nodes),
    as KG embedding models work on entity-relation-entity triples.
    """
    print("=" * 70)
    print("SECTION 1 — Loading KG as Triples")
    print("=" * 70)

    g = RDFGraph()
    g.parse(str(kg_file), format="turtle")
    print(f"  RDF triples loaded: {len(g)}")

    triples_list = []
    for s, p, o in g:
        if isinstance(s, URIRef) and isinstance(o, URIRef) and \
           not isinstance(s, BNode) and not isinstance(o, BNode):
            triples_list.append([str(s), str(p), str(o)])

    triples_arr = np.array(triples_list, dtype=str)
    print(f"  URI-only triples: {len(triples_arr)}")
    print(f"  Unique entities:  {len(set(triples_arr[:, 0]) | set(triples_arr[:, 2]))}")
    print(f"  Unique relations: {len(set(triples_arr[:, 1]))}")

    # Save for inspection
    pd.DataFrame(triples_arr, columns=["subject", "predicate", "object"]) \
      .to_csv(EMB_DIR / "triples.tsv", sep="\t", index=False)
    print(f"  → Saved triples.tsv")

    return triples_arr, g


# ══════════════════════════════════════════════════════════════
# SECTION 2: Train/Test Split
# ══════════════════════════════════════════════════════════════
def split_data(triples_arr: np.ndarray) -> tuple:
    """Create TriplesFactory and split into train/test."""
    print("\n" + "=" * 70)
    print("SECTION 2 — Train/Test Split")
    print("=" * 70)

    tf = TriplesFactory.from_labeled_triples(triples_arr)
    print(f"  Total triples: {tf.num_triples}")
    print(f"  Entities: {tf.num_entities} | Relations: {tf.num_relations}")

    # 90/10 split (tutorial uses 95/5, we use 90/10 for more test data)
    train_tf, test_tf = tf.split([0.9, 0.1], random_state=42)
    print(f"  Train: {train_tf.num_triples} | Test: {test_tf.num_triples}")
    print(f"  Test ratio: {test_tf.num_triples / tf.num_triples:.1%}")

    return tf, train_tf, test_tf


# ══════════════════════════════════════════════════════════════
# SECTION 3 & 4: Train Multiple Models and Evaluate
# ══════════════════════════════════════════════════════════════
def train_and_evaluate(train_tf, test_tf) -> dict:
    """
    Train multiple KGE models and evaluate them.
    Returns dict of {model_name: pipeline_result}.
    """
    print("\n" + "=" * 70)
    print("SECTION 3 & 4 — Training & Evaluation")
    print("=" * 70)

    results = {}
    all_metrics = []

    for model_name in MODELS_TO_TRAIN:
        print(f"\n  --- Training {model_name} ---")

        try:
            res = pipeline(
                random_seed=42,
                model=model_name,
                training=train_tf,
                testing=test_tf,
                training_kwargs=dict(
                    num_epochs=NUM_EPOCHS,
                    checkpoint_name=f"hi_{model_name.lower()}_checkpoint.pt",
                    checkpoint_directory=str(EMB_DIR / "checkpoints"),
                    checkpoint_frequency=50,
                ),
                dimensions=EMBEDDING_DIM,
                optimizer="adam",
                optimizer_kwargs={"lr": LEARNING_RATE},
                negative_sampler="basic",
                negative_sampler_kwargs=dict(filtered=True),
            )

            # Extract metrics
            mrr = res.get_metric("mrr")
            h1 = res.get_metric("hits_at_1")
            h3 = res.get_metric("hits_at_3")
            h10 = res.get_metric("hits_at_10")

            print(f"  MRR:      {mrr:.4f}")
            print(f"  Hits@1:   {h1:.4f}")
            print(f"  Hits@3:   {h3:.4f}")
            print(f"  Hits@10:  {h10:.4f}")

            results[model_name] = res
            all_metrics.append({
                "Model": model_name,
                "MRR": round(mrr, 4),
                "Hits@1": round(h1, 4),
                "Hits@3": round(h3, 4),
                "Hits@10": round(h10, 4),
            })

        except Exception as e:
            print(f"  ERROR training {model_name}: {e}")
            continue

    # Save comparison table
    df_metrics = pd.DataFrame(all_metrics)
    df_metrics.to_csv(EMB_DIR / "model_comparison.csv", index=False)
    print(f"\n  Model Comparison:")
    print(df_metrics.to_string(index=False))

    # Visualise: comparison bar chart
    if all_metrics:
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(all_metrics))
        width = 0.2
        metrics_to_plot = ["MRR", "Hits@1", "Hits@3", "Hits@10"]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

        for j, (metric, color) in enumerate(zip(metrics_to_plot, colors)):
            vals = [m[metric] for m in all_metrics]
            ax.bar(x + j * width, vals, width, label=metric, color=color)

        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels([m["Model"] for m in all_metrics])
        ax.set_ylabel("Score")
        ax.set_title("KG Embedding Model Comparison on HI Knowledge Graph")
        ax.legend()
        ax.set_ylim(0, 1)
        plt.tight_layout()
        plt.savefig(EMB_DIR / "model_comparison.png", dpi=150)
        plt.close()

    # Loss curves
    if results:
        fig, ax = plt.subplots(figsize=(10, 5))
        for model_name, res in results.items():
            losses = res.losses
            ax.plot(range(1, len(losses) + 1), losses, label=model_name)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title("Training Loss Curves")
        ax.legend()
        plt.tight_layout()
        plt.savefig(EMB_DIR / "loss_curves.png", dpi=150)
        plt.close()

    print(f"\n  → Saved model_comparison.csv, model_comparison.png, loss_curves.png")
    return results


# ══════════════════════════════════════════════════════════════
# SECTION 5: Link Prediction
# ══════════════════════════════════════════════════════════════
def link_prediction(best_result, tf: TriplesFactory, triples_arr: np.ndarray):
    """
    Predict missing links using the best trained model.
    Generate candidate triples and score them.
    """
    print("\n" + "=" * 70)
    print("SECTION 5 — Link Prediction")
    print("=" * 70)

    model = best_result.model

    # ── A) Score specific candidate triples ───────────────────
    # Create meaningful candidate triples for our HI domain
    # e.g., "Which papers might describe which use cases?"
    #       "Which agents might have which capabilities?"
    papers = [s for s, p, o in triples_arr
              if p.endswith("#hasTitle") or (p.endswith("type") and o.endswith("#Paper"))]
    papers = list(set(papers))[:5]

    usecases = [o for s, p, o in triples_arr if p.endswith("#describesUseCase")]
    usecases = list(set(usecases))

    agents = [s for s, p, o in triples_arr if o.endswith("#HumanAgent") or o.endswith("#ArtificialAgent")]
    agents = list(set(agents))[:10]

    capabilities = [s for s, p, o in triples_arr if o.endswith("#Capability")]
    capabilities = list(set(capabilities))[:10]

    existing = set((s, o) for s, _, o in triples_arr)

    # Generate candidates: agent → hasCapability → capability
    candidates = []
    has_cap_rel = HI_NS + "hasCapability"
    for agent in agents:
        for cap in capabilities:
            if (agent, cap) not in existing:
                candidates.append([agent, has_cap_rel, cap])

    # Also: paper → hasKeyword → keyword
    keywords = [o for s, p, o in triples_arr if p.endswith("#hasKeyword")]
    keywords = list(set(keywords))[:10]
    has_kw_rel = HI_NS + "hasKeyword"
    for paper in papers:
        for kw in keywords:
            if (paper, kw) not in existing:
                candidates.append([paper, has_kw_rel, kw])

    if not candidates:
        print("  No candidate triples generated.")
        return

    # Limit to manageable number
    candidates = candidates[:500]
    X_cand = np.array(candidates, dtype=str)
    print(f"  Candidate triples to score: {len(X_cand)}")

    try:
        pack = pk_predict.predict_triples(
            model=model, triples=X_cand, triples_factory=tf
        )
        processed = pack.process(factory=tf).df
        probs = expit(processed["score"].values)
        processed["probability"] = probs
        processed["subject_short"] = [short(s) for s in X_cand[:len(processed), 0]]
        processed["predicate_short"] = [short(p) for p in X_cand[:len(processed), 1]]
        processed["object_short"] = [short(o) for o in X_cand[:len(processed), 2]]

        # Sort by score descending
        processed = processed.sort_values("score", ascending=False)

        # Save all
        processed.to_csv(EMB_DIR / "link_predictions_scored.csv", index=False)

        # Show top 20
        top20 = processed.head(20)
        print(f"\n  Top 20 predicted links:")
        for _, row in top20.iterrows():
            print(f"    {row['subject_short']:40s} → "
                  f"{row['predicate_short']:20s} → "
                  f"{row['object_short']:40s}  "
                  f"score={row['score']:.4f}  prob={row['probability']:.4f}")

        # Save top predictions
        top_cols = ["subject_short", "predicate_short", "object_short",
                    "score", "probability"]
        processed[top_cols].head(50).to_csv(
            EMB_DIR / "link_predictions.csv", index=False)

        print(f"\n  → Saved link_predictions.csv, link_predictions_scored.csv")

    except Exception as e:
        print(f"  Link prediction error: {e}")
        print("  (This can happen if candidate entities are not in the training set)")


# ══════════════════════════════════════════════════════════════
# SECTION 6: Embedding Visualisation (PCA + t-SNE)
# ══════════════════════════════════════════════════════════════
def visualise_embeddings(best_result, train_tf: TriplesFactory):
    """
    Visualise entity embeddings using PCA and t-SNE,
    coloured by entity type (as in tutorial Section 6 / Exercise 7).
    """
    print("\n" + "=" * 70)
    print("SECTION 6 — Embedding Visualisation")
    print("=" * 70)

    model = best_result.model

    # Extract entity embeddings
    try:
        emb_raw = model.entity_representations[0](
            indices=None
        ).detach().cpu().numpy()
    except Exception:
        print("  Could not extract embeddings from this model type.")
        return

    # For ComplEx: embeddings are complex — stack real and imaginary parts
    if np.iscomplexobj(emb_raw):
        emb = np.hstack([emb_raw.real, emb_raw.imag])
    elif emb_raw.dtype == np.complex64 or emb_raw.dtype == np.complex128:
        emb = np.hstack([emb_raw.real, emb_raw.imag])
    else:
        emb = emb_raw.real if hasattr(emb_raw, 'real') else emb_raw

    # Ensure 2D real array
    if len(emb.shape) == 1:
        emb = emb.reshape(1, -1)
    emb = emb.astype(float)

    print(f"  Embedding matrix shape: {emb.shape}")

    # Map indices back to entity labels and types
    id2ent = {v: k for k, v in train_tf.entity_to_id.items()}
    n_entities = len(id2ent)
    types = np.array([entity_type(id2ent[i]) for i in range(n_entities)])
    unique_types = sorted(set(types))
    print(f"  Entity types found: {unique_types}")
    print(f"  Type distribution:")
    for t in unique_types:
        print(f"    {t:25s} {np.sum(types == t):4d}")

    # Colour map
    cmap = plt.cm.tab20(np.linspace(0, 1, len(unique_types)))
    type_to_color = {t: cmap[i] for i, t in enumerate(unique_types)}

    # ── PCA visualisation ─────────────────────────────────────
    print("\n  Computing PCA projection...")
    pca = PCA(n_components=2, random_state=42)
    xy_pca = pca.fit_transform(emb[:n_entities])

    fig, ax = plt.subplots(figsize=(12, 9))
    for t in unique_types:
        mask = types == t
        if mask.any():
            ax.scatter(xy_pca[mask, 0], xy_pca[mask, 1],
                      s=15, alpha=0.6, label=f"{t} ({mask.sum()})",
                      color=type_to_color[t])
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} var.)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} var.)")
    ax.set_title("Entity Embeddings — PCA Projection (coloured by type)")
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    plt.tight_layout()
    plt.savefig(EMB_DIR / "embeddings_pca.png", dpi=150)
    plt.close()
    print(f"  → Saved embeddings_pca.png")

    # ── t-SNE visualisation ───────────────────────────────────
    print("  Computing t-SNE projection (this may take a moment)...")
    n_sample = min(n_entities, 2000)
    rng = np.random.RandomState(42)
    idx = rng.choice(n_entities, size=n_sample, replace=False)

    tsne = TSNE(n_components=2, random_state=42, perplexity=30, init="pca",
                learning_rate="auto")
    xy_tsne = tsne.fit_transform(emb[idx])
    types_sample = types[idx]

    fig, ax = plt.subplots(figsize=(12, 9))
    for t in unique_types:
        mask = types_sample == t
        if mask.any():
            ax.scatter(xy_tsne[mask, 0], xy_tsne[mask, 1],
                      s=15, alpha=0.6, label=f"{t} ({mask.sum()})",
                      color=type_to_color[t])
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    ax.set_title(f"Entity Embeddings — t-SNE Projection (n={n_sample})")
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    plt.tight_layout()
    plt.savefig(EMB_DIR / "embeddings_tsne.png", dpi=150)
    plt.close()
    print(f"  → Saved embeddings_tsne.png")

    # ── Optional: K-Means clustering on embeddings ────────────
    print("\n  Clustering embeddings (K-Means)...")
    n_clusters = min(10, n_entities // 5)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = km.fit_predict(emb[:n_entities])

    fig, ax = plt.subplots(figsize=(12, 9))
    scatter = ax.scatter(xy_pca[:, 0], xy_pca[:, 1],
                        c=clusters, cmap="tab20", s=15, alpha=0.6)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title(f"Entity Embeddings — K-Means Clusters (k={n_clusters})")
    plt.colorbar(scatter, ax=ax, label="Cluster ID")
    plt.tight_layout()
    plt.savefig(EMB_DIR / "embedding_clusters.png", dpi=150)
    plt.close()

    # Analyse cluster composition
    print(f"\n  K-Means cluster composition (k={n_clusters}):")
    for c in range(n_clusters):
        mask = clusters == c
        type_counts = pd.Series(types[mask]).value_counts()
        dominant = type_counts.index[0]
        print(f"    Cluster {c}: {mask.sum()} entities, "
              f"dominant type: {dominant} ({type_counts.iloc[0]})")

    print(f"  → Saved embedding_clusters.png")


# ══════════════════════════════════════════════════════════════
# HELPER: Load combined KG (own + populated)
# ══════════════════════════════════════════════════════════════
def load_combined_triples(kg_file: Path, populated_file: Path) -> tuple:
    """
    Load own KG + hi-ontology-populated.ttl into a combined graph.
    Saves the combined graph as a new file (never overwrites originals).
    Returns (triples_arr, combined_rdf_graph).
    """
    print("\n" + "=" * 70)
    print("ABLATION — Loading Combined KG (own + populated)")
    print("=" * 70)

    g = RDFGraph()
    g.parse(str(kg_file), format="turtle")
    own_count = len(g)
    print(f"  Own KG triples: {own_count}")

    g.parse(str(populated_file), format="turtle")
    combined_count = len(g)
    print(f"  After adding populated: {combined_count} (+{combined_count - own_count})")

    # Save combined graph as new file (never overwrite originals)
    combined_path = EMB_DIR / "combined_kg_for_training.ttl"
    g.serialize(destination=str(combined_path), format="turtle")
    print(f"  Saved combined KG to: {combined_path}")

    triples_list = []
    for s, p, o in g:
        if isinstance(s, URIRef) and isinstance(o, URIRef) and \
           not isinstance(s, BNode) and not isinstance(o, BNode):
            triples_list.append([str(s), str(p), str(o)])

    triples_arr = np.array(triples_list, dtype=str)
    print(f"  URI-only triples: {len(triples_arr)}")
    print(f"  Unique entities:  {len(set(triples_arr[:, 0]) | set(triples_arr[:, 2]))}")
    print(f"  Unique relations: {len(set(triples_arr[:, 1]))}")

    return triples_arr, g


# ══════════════════════════════════════════════════════════════
# HELPER: Run a single training experiment (for ablation)
# ══════════════════════════════════════════════════════════════
def run_single_model(model_name: str, train_tf, test_tf,
                     label: str = "") -> dict:
    """Train one model and return metrics dict."""
    prefix = f"[{label}] " if label else ""
    print(f"\n  {prefix}--- Training {model_name} ---")
    try:
        res = pipeline(
            random_seed=42,
            model=model_name,
            training=train_tf,
            testing=test_tf,
            training_kwargs=dict(num_epochs=NUM_EPOCHS),
            dimensions=EMBEDDING_DIM,
            optimizer="adam",
            optimizer_kwargs={"lr": LEARNING_RATE},
            negative_sampler="basic",
            negative_sampler_kwargs=dict(filtered=True),
        )
        mrr = res.get_metric("mrr")
        h1 = res.get_metric("hits_at_1")
        h3 = res.get_metric("hits_at_3")
        h10 = res.get_metric("hits_at_10")
        print(f"  {prefix}MRR={mrr:.4f}  H@1={h1:.4f}  H@3={h3:.4f}  H@10={h10:.4f}")
        return {"MRR": mrr, "Hits@1": h1, "Hits@3": h3, "Hits@10": h10,
                "result": res}
    except Exception as e:
        print(f"  {prefix}ERROR: {e}")
        return None


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    EMB_DIR.mkdir(parents=True, exist_ok=True)
    (EMB_DIR / "checkpoints").mkdir(parents=True, exist_ok=True)

    # Locate merged KG
    candidates = [
        OUTPUT_DIR / "merged_kg.ttl",
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
            print("ERROR: Cannot find merged KG.")
            sys.exit(1)

    # Locate populated file (optional — for ablation)
    populated_candidates = [
        OUTPUT_DIR.parent / "data" / "hi-ontology-populated.ttl",
        OUTPUT_DIR / "hi-ontology-populated.ttl",
        Path("../data/hi-ontology-populated.ttl"),
        Path("data/hi-ontology-populated.ttl"),
    ]
    populated_file = None
    for c in populated_candidates:
        if c.exists():
            populated_file = c
            break

    print(f"Using KG: {kg_file}")
    if populated_file:
        print(f"Populated file found: {populated_file} (will use for ablation)")
    else:
        print("Populated file not found (ablation will be skipped)")

    # ══════════════════════════════════════════════════════════
    # EXPERIMENT 1: Own KG only (primary experiment)
    # ══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("EXPERIMENT 1 — Own KG Only")
    print(f"{'='*70}")

    # Section 1: Load triples
    triples_arr, g_rdf = load_triples(kg_file)

    # Section 2: Train/test split
    tf, train_tf, test_tf = split_data(triples_arr)

    # Sections 3 & 4: Train and evaluate models
    results = train_and_evaluate(train_tf, test_tf)

    if not results:
        print("\nNo models trained successfully. Exiting.")
        sys.exit(1)

    # Pick best model by MRR
    best_name = max(results, key=lambda k: results[k].get_metric("mrr"))
    best_result = results[best_name]
    print(f"\n  Best model: {best_name} "
          f"(MRR={best_result.get_metric('mrr'):.4f})")

    # Section 5: Link Prediction
    link_prediction(best_result, tf, triples_arr)

    # Section 6: Embedding Visualisation
    visualise_embeddings(best_result, train_tf)

    # Collect own-KG metrics for ablation comparison
    own_metrics = {}
    for model_name, res in results.items():
        own_metrics[model_name] = {
            "MRR": round(res.get_metric("mrr"), 4),
            "Hits@1": round(res.get_metric("hits_at_1"), 4),
            "Hits@3": round(res.get_metric("hits_at_3"), 4),
            "Hits@10": round(res.get_metric("hits_at_10"), 4),
        }

    # ══════════════════════════════════════════════════════════
    # EXPERIMENT 2: Combined KG (own + populated) — Ablation
    # ══════════════════════════════════════════════════════════
    if populated_file:
        print(f"\n{'='*70}")
        print("EXPERIMENT 2 — Combined KG (own + all-groups populated)")
        print(f"{'='*70}")

        combined_triples, combined_rdf = load_combined_triples(
            kg_file, populated_file)

        # Split combined data
        combined_tf = TriplesFactory.from_labeled_triples(combined_triples)
        comb_train, comb_test = combined_tf.split([0.9, 0.1], random_state=42)
        print(f"  Combined split: train={comb_train.num_triples} "
              f"test={comb_test.num_triples}")

        # Train best model on combined data
        combined_metrics = {}
        for model_name in MODELS_TO_TRAIN:
            m = run_single_model(model_name, comb_train, comb_test,
                                 label="Combined")
            if m:
                combined_metrics[model_name] = {
                    "MRR": round(m["MRR"], 4),
                    "Hits@1": round(m["Hits@1"], 4),
                    "Hits@3": round(m["Hits@3"], 4),
                    "Hits@10": round(m["Hits@10"], 4),
                }

        # ── Ablation comparison table ─────────────────────────
        print(f"\n{'='*70}")
        print("ABLATION COMPARISON — Own KG vs Combined KG")
        print(f"{'='*70}")

        ablation_rows = []
        header = f"  {'Model':<10} {'Dataset':<12} {'MRR':>6} {'H@1':>6} {'H@3':>6} {'H@10':>6}"
        print(header)
        print("  " + "-" * (len(header) - 2))

        for model_name in MODELS_TO_TRAIN:
            if model_name in own_metrics:
                om = own_metrics[model_name]
                print(f"  {model_name:<10} {'Own KG':<12} "
                      f"{om['MRR']:>6.4f} {om['Hits@1']:>6.4f} "
                      f"{om['Hits@3']:>6.4f} {om['Hits@10']:>6.4f}")
                ablation_rows.append({
                    "Model": model_name, "Dataset": "Own KG",
                    **om
                })
            if model_name in combined_metrics:
                cm = combined_metrics[model_name]
                print(f"  {model_name:<10} {'Combined':<12} "
                      f"{cm['MRR']:>6.4f} {cm['Hits@1']:>6.4f} "
                      f"{cm['Hits@3']:>6.4f} {cm['Hits@10']:>6.4f}")
                ablation_rows.append({
                    "Model": model_name, "Dataset": "Combined",
                    **cm
                })

        # Save ablation CSV
        df_ablation = pd.DataFrame(ablation_rows)
        df_ablation.to_csv(EMB_DIR / "ablation_comparison.csv", index=False)

        # Ablation bar chart
        fig, axes = plt.subplots(1, 4, figsize=(16, 5))
        metrics_list = ["MRR", "Hits@1", "Hits@3", "Hits@10"]
        colors = {"Own KG": "#2196F3", "Combined": "#FF9800"}

        for ax, metric in zip(axes, metrics_list):
            models = [m for m in MODELS_TO_TRAIN
                      if m in own_metrics and m in combined_metrics]
            x = np.arange(len(models))
            w = 0.35
            own_vals = [own_metrics[m][metric] for m in models]
            comb_vals = [combined_metrics[m][metric] for m in models]
            ax.bar(x - w/2, own_vals, w, label="Own KG",
                   color=colors["Own KG"])
            ax.bar(x + w/2, comb_vals, w, label="Combined",
                   color=colors["Combined"])
            ax.set_xticks(x)
            ax.set_xticklabels(models, fontsize=9)
            ax.set_title(metric)
            ax.set_ylim(0, max(max(own_vals + comb_vals) * 1.2, 0.1))
            if ax == axes[0]:
                ax.legend(fontsize=8)

        plt.suptitle("Ablation: Own KG vs Combined KG (with all-groups data)",
                     fontsize=12)
        plt.tight_layout()
        plt.savefig(EMB_DIR / "ablation_comparison.png", dpi=150)
        plt.close()

        print(f"\n  -> Saved ablation_comparison.csv, ablation_comparison.png")

    print("\n" + "=" * 70)
    print("Done! All embedding results saved in:")
    print(f"  {EMB_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
